import functools
import requests
from charm.toolbox.conversion import Conversion
from flask import Blueprint, render_template, redirect, url_for, request, json, flash
import os
from time import localtime
import dotenv
from user import dev_host
from crypto_utils.conversions import SigConversion
from user.models.keys import KeyModel
from user.models.sessions import SessionModel
from user.utils.utils import handle_challenge, handle_response_hashes, prove_owner, validate_block, \
    handle_challenge_ap, validate_proof
import dateutil.parser

main = Blueprint('main', __name__, template_folder='templates')

dotenv.load_dotenv('../.env')

def token_required(func):
    @functools.wraps(func)
    def decorator_token_required(*args, **kwargs):
        # Get access_token
        first = SessionModel.query.first()
        headers = {}
        if first:
            access_token = SessionModel.query.first().access_token
            headers = {
                'Authorization': "Bearer " + access_token
            }
        return func(headers)
    return decorator_token_required


@main.route('/')
def index():
    # Use os.getenv("key") to get environment variables
    app_name = os.getenv("APP_NAME")
    if not app_name:
        app_name = "User Interface"

    return render_template('index.html', name=app_name)


# TODO add expiry checking
@main.route('/generate_keys')
@token_required
def gen_keys(headers):
    access_token = SessionModel.query.first()
    if access_token is None:
        return redirect(url_for('auth.login'))
    return render_template('generate_keys.html', now=localtime())


# TODO Save keys on the user side
@main.route("/generate_keys", methods=['POST'])
@token_required
def challenge_response_post(headers):

    # Get the number of requested keys from the form, then generate the required number
    params = {
        'number': int(request.form.get('number')),
        'time': int(dateutil.parser.parse(request.form.get('time')).timestamp()),
        'policy': int(request.form.get('policy'))
    }

    res = requests.get("http://%s:5002/setup_keys" % dev_host, params=params, headers=headers)
    if res.status_code == 401:
        return redirect(url_for('auth.login'))
    try:
        # Blind the keys
        es = handle_challenge(res.json(), params.get('policy'))

        # Post keys to CP
        try:
            res = requests.post("http://%s:5002/generate_proofs" % dev_host, json=json.dumps(es), headers=headers)
            if res.status_code == 201:
                # TODO remove hardcoded CP
                data = res.json()
                handle_response_hashes(data, int(os.environ.get('cp_dlt_id')), data.get('policy'))
                flash("Keys have been generated", 'keygen_success')
                return render_template('generate_keys.html')
            else:
                return render_template('generate_keys.html')
        except Exception as e:
            flash(str(e), "post_keys")
            return render_template('generate_keys.html')
    except Exception as e:
        flash(str(e), "post_keys")
        return render_template('generate_keys.html')


@main.route("/access_service", methods=['GET'])
def access_service():
    return render_template('service_authenticate.html')


@main.route("/access_service", methods=['POST'])
def access_service_post():
    # Get nonce from service
    res = requests.get('http://%s:5003/request' % dev_host).json()
    service_y = res.get('y')

    # Request-certs CP_i
    params = {
        'cp': int(request.form.get('cp')),
        'timestamp': int(dateutil.parser.parse(request.form.get('timestamp')).timestamp()),
        'policy': int(request.form.get('policy'))
    }

    res = requests.get('http://%s:5001/request_certs' % dev_host, params=params)
    if res.status_code == 500:
        flash(res.json().get('message'), "access_service_error")
        return render_template('service_authenticate.html')

    # Get data
    data = res.json()
    key_model = KeyModel.query.filter_by(provider_type_=1, p_id_=params.get('cp'), policy_=params.get('policy'),
                                         interval_timestamp_=params.get('timestamp')).first()

    # Validate that block has not been altered
    try:
        validate_block(data)
    except Exception as e:
        flash(str(e), "access_service_error")
        return render_template('service_authenticate.html')

    pubk = {
        'pubk': Conversion.OS2IP(key_model.public_key)
    }

    res = requests.get('http://%s:5001/prove_owner' % dev_host, params=pubk)
    y = res.json().get('y')

    # Prove the user owns the private key corresponding to a set of proofs in the block
    try:
        (proof, proof_owner) = prove_owner(y, data, key_model.proof_hash)
        blind_signature = key_model.generate_blind_signature(proof.get('proofs'))

        proof_resp = json.dumps({
            'y': y,
            'signature': proof_owner[1],
            'blind_signature': json.dumps(SigConversion.convert_dict_strlist(blind_signature))
        })
        res = requests.post('http://%s:5001/prove_owner' % dev_host, json=proof_resp, params=params)

        access_info = res.json()
        headers = {
            'Authorization': "Bearer " + access_info.get('access')
        }

        # Request challenge
        challenge = requests.get('http://%s:5001/init_sig' % dev_host, headers=headers).json()

        # Handle challenge
        try:
            challenge['timestamp'] = params.get('timestamp')
            e = json.dumps(handle_challenge_ap(challenge, params.get('policy'), service_y))

            # Send Response
            proof_response = requests.post('http://%s:5001/generate_proof' % dev_host, json=e, headers=headers)
            proofs = proof_response.json()

            # Validate Response
            try:
                validate_proof(proofs)
            except Exception as e:
                flash(str(e), "access_service_error")
                return render_template('service_authenticate.html')

            # Get AP Keymodel
            ap_key_model = KeyModel.query.filter_by(p_id_=int(os.environ.get('ap_dlt_id')), provider_type_ = 2).first()

            # Build signature
            blind_signature = ap_key_model.generate_blind_signature(proofs.get('proof'))

            # Send signature on service_y to service
            resp_service = {
                'y': service_y,
                'sig': json.dumps(SigConversion.convert_dict_strlist(blind_signature)),
                'policy': params.get('policy'),
                'timestamp': params.get('timestamp')
            }

            # Get access to service
            res = requests.post('http://%s:5003/response' % dev_host, json=json.dumps(resp_service))
            if res.status_code == 200:
                return render_template('thanks.html')
            else:
                message = res.json().get('message')
                flash(message, "access_service_error")
                return render_template('service_authenticate.html')
        except Exception as e:
            flash(str(e), "access_service_error")
            return render_template('service_authenticate.html')
    except Exception as e:
        flash(str(e), "access_service_error")
        return render_template('service_authenticate.html')




@main.route('/thanks')
def thanks():
    return render_template('thanks.html')