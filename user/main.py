import functools
import os
import random
from time import localtime
from traceback import format_exc

import dateutil.parser
import dotenv
import requests
from Crypto import Random as rd
from charm.toolbox.conversion import Conversion
from flask import Blueprint, render_template, redirect, url_for, request, json, flash, jsonify
from flask import current_app

from crypto_utils.conversions import SigConversion
from user.models.keys import KeyModel
from user.models.sessions import SessionModel
from user.utils.utils import handle_challenge, handle_response_hashes, prove_owner, validate_block, \
    handle_challenge_ap, validate_proof, verify_block_hash

main = Blueprint('main', __name__, template_folder='templates')

dotenv.load_dotenv('../.env')


def token_required(func):
    """
    Helper wrapper that injects the access token that is needed for authentication into the protected methods.
    :param func: JWT protected function.
    :return:
    """
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
    """
    Renders the user main page.
    :return:
    """
    # Use os.getenv("key") to get environment variables
    app_name = os.getenv("APP_NAME")
    if not app_name:
        app_name = "User Interface"

    return render_template('index.html', name=app_name)


# TODO add expiry checking
@main.route('/generate_keys')
@token_required
def gen_keys(headers):
    """
    Renders the generate_keys.html page.
    :param headers:
    :return:
    """
    access_token = SessionModel.query.first()
    if access_token is None:
        return redirect(url_for('auth.login'))
    return render_template('generate_keys.html', now=localtime())


# TODO Save keys on the user side
@main.route("/generate_keys", methods=['POST'])
@token_required
def challenge_response_post(headers):
    """
    This method is called by the user frontend when the generate keys form has been filled out. It then initiates the
    blinding process with the CP. It receives the the proof hashes from the CP and saves them in the database.

    This is the first step the user must take to create credentials.
    """
    # Get the number of requested keys from the form, then generate the required number
    params = {
        'number': int(request.form.get('number')),
        'time': int(dateutil.parser.parse(request.form.get('time')).timestamp()),
        'policy': int(request.form.get('policy'))
    }

    """
    The user must initiate the interaction with the CP in order to blind the signatures. It sends a GET request
    to the following endpoint in order to receive (rnd, a, b1, b2) and the CP public key for the corresponding policy
    and time interval.
    """
    res = requests.get("http://{}/setup_keys".format(current_app.config['cp_host']), params=params, headers=headers)
    if res.status_code == 401:
        return redirect(url_for('auth.login'))
    if res.status_code == 500:
        current_app.logger.error("Could not setup keys. Check CP Logs")
        flash(res.json().get('message'), "post_keys")
        return render_template("generate_keys.html")
    try:
        # Generates the challenge response
        es = handle_challenge(res.json(), params.get('policy'))

        # Post keys to CP
        try:
            res = requests.post("http://{}/generate_proofs".format(current_app.config['cp_host']), json=json.dumps(es), headers=headers)
            if res.status_code == 201:
                # TODO remove hardcoded CP
                data = res.json()

                # The response hashes need to be saved with the corresponding policy at a given timestamp
                handle_response_hashes(data, current_app.config['cp_dlt_id'], data.get('policy'))
                flash("Keys have been generated", 'keygen_success')
                return render_template('generate_keys.html')
            else:
                current_app.logger.error("Could not generate proofs, check CP logs.")
                return render_template('generate_keys.html')
        except Exception as e:
            flash(str(e), "post_keys")
            current_app.logger.error(format_exc())
            return render_template('generate_keys.html')
    except Exception as e:
        flash(str(e), "post_keys")
        current_app.logger.error(format_exc())
        return render_template('generate_keys.html')


@main.route("/verify", methods=['GET'])
def verify():
    """
        Renders the verify.html page.
        :return:
        """
    return render_template('verify.html')


@main.route("/verify", methods=['POST'])
def verify_post():
    params = {
        'cp': int(request.form.get('cp')),
        'timestamp': int(dateutil.parser.parse(request.form.get('timestamp')).timestamp()),
        'policy': int(request.form.get('policy'))
    }

    key_model = KeyModel.query.filter_by(provider_type_=1, p_id_=params.get('cp'), policy_=params.get('policy'),
                                         interval_timestamp_=params.get('timestamp')).first()

    res = requests.get('http://{}/request_certs'.format(current_app.config['ap_host']), params=params)
    if res.status_code == 500:
        flash("Error when requesting certs: " + res.json().get('message'), "verify_error")
        return render_template('verify.html')

    # Get data from response and find corresponding keymodel
    data = res.json()

    try:
        validate_block(data, key_model.proof_hash)
    except Exception as e:
        flash("Error when validating block: " + str(e), "verify_error")
        return render_template('verify.html')

    flash("Verified", "verify_success")
    return render_template('verify.html')


@main.route("/access_service", methods=['GET'])
def access_service():
    """
    Renders the service_authenticate.html page.
    :return:
    """
    return render_template('service_authenticate.html')


@main.route("/access_service", methods=['POST'])
def access_service_post():
    # Get nonce from service
    res = requests.get('http://{}/request'.format(current_app.config['service_host'])).json()
    service_y = res.get('y')

    VERIFY = True if request.form.get('verify') else False
    DELETE = True if request.form.get('delete') else False

    # Setup parameters that are sent to the AP
    params = {
        'cp': int(request.form.get('cp')),
        'timestamp': int(dateutil.parser.parse(request.form.get('timestamp')).timestamp()),
        'policy': int(request.form.get('policy'))
    }

    key_model = KeyModel.query.filter_by(provider_type_=1, p_id_=params.get('cp'), policy_=params.get('policy'),
                                         interval_timestamp_=params.get('timestamp')).first()

    data = None
    if VERIFY:
        # Request-certs CP_i
        res = requests.get('http://{}/request_certs'.format(current_app.config['ap_host']), params=params)
        if res.status_code == 500:
            flash("Error when requesting certs: " + res.json().get('message'), "access_service_error")
            return render_template('service_authenticate.html')

        # Get data from response and find corresponding keymodel
        data = res.json()

        # Validate that block has not been altered
        try:
            verify_block_hash(data)
        except Exception as e:
            current_app.logger.error(format_exc())
            flash("Error when validating block: " + str(e), "access_service_error")
            return render_template('service_authenticate.html')

    pubk = {
        'pubk': Conversion.OS2IP(key_model.public_key)
    }

    # Get the challenge from the AP in order to prove that the user owns a specific keypair
    res = requests.get('http://{}/prove_owner'.format(current_app.config['ap_host']), params=pubk)
    y = res.json().get('y')

    # Prove the user owns the private key corresponding to a set of proofs in the block
    # Proof consists of the signature of the private key on the nonce y and the blind signature on the public key
    try:
        if VERIFY:
            (proof, proof_owner) = prove_owner(y, data, key_model.proof_hash)
            blind_signature = key_model.generate_blind_signature(proof.get('proofs'))
        else:
            proof_owner = key_model.sign(y)
            blind_signature = key_model.generate_blind_signature()

        proof_resp = json.dumps({
            'y': y,
            'signature': proof_owner[1],
            'blind_signature': json.dumps(SigConversion.convert_dict_strlist(blind_signature))
        })

        # Post the proofs
        res = requests.post('http://{}/prove_owner'.format(current_app.config['ap_host']), json=proof_resp, params=params)

        # Receive access token for AP
        access_info = res.json()
        err = access_info
        headers = {
            'Authorization': "Bearer " + access_info.get('access')
        }

        # Request challenge from AP to issue blind signature
        challenge = requests.get('http://{}/init_sig'.format(current_app.config['ap_host']), headers=headers).json()

        # Handle challenge
        try:
            challenge['timestamp'] = params.get('timestamp')
            e = json.dumps(handle_challenge_ap(challenge, params.get('policy'), service_y))

            # Send Response
            proof_response = requests.post('http://{}/generate_proof'.format(current_app.config['ap_host']), json=e, headers=headers)
            proofs = proof_response.json()

            # Validate Response
            try:
                validate_proof(proofs)
            except Exception as e:
                current_app.logger.error(format_exc())
                flash("Error when validating proofs: " + str(e), "access_service_error")
                return render_template('service_authenticate.html')

            # Get AP Keymodel
            ap_key_model = KeyModel.query.filter_by(p_id_=current_app.config['ap_dlt_id'],
                                                    provider_type_=2, index=service_y).first()

            # Build signature
            blind_signature = ap_key_model.generate_blind_signature(proofs.get('proof'))

            # Send signature on service_y to service
            resp_service = {
                'y': service_y,
                'sig': json.dumps(SigConversion.convert_dict_strlist(blind_signature)),
                'policy': params.get('policy'),
                'timestamp': params.get('timestamp')
            }

            # Delete after use
            ap_key_model.delete()

            # Delete if user indicated
            if DELETE:
                key_model.delete()

            # Get access to service
            res = requests.post('http://{}/response'.format(current_app.config['service_host']), json=json.dumps(resp_service))
            if res.status_code == 200:
                return render_template('thanks.html')
            else:
                message = res.json().get('message')
                flash("Response code was not 200: " + message, "access_service_error")
                return render_template('service_authenticate.html')
        except Exception as e:
            flash("There was an error when handling the challenge: " + str(e), "access_service_error")
            current_app.logger.error(format_exc())
            return render_template('service_authenticate.html')
    except Exception as e:
        current_app.logger.error(format_exc())
        flash("There was an error in the ownership proving stage. The blind signature likely failed to verify: "
              + str(e), "access_service_error")
        return render_template('service_authenticate.html')


@main.route('/thanks')
def thanks():
    return render_template('thanks.html')


@main.route('/query')
def query():
    return render_template('query.html')


@main.route('/query', methods=['POST'])
def query_post():
    params = {
        'id': int(request.form.get('id')),
        'timestamp': int(dateutil.parser.parse(request.form.get('timestamp')).timestamp()),
        'policy': int(request.form.get('policy'))
    }
    key_model = KeyModel.find(params.get('id'), params.get('policy'), params.get('timestamp'))
    if key_model is not None:
        return json.dumps(str(key_model)), 200
    else:
        return "None", 200

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------- API CALLS FOR LOAD AND PERFORMANCE TESTING ------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


@main.route("/prove", methods=['POST'])
def prove_owner():
    # Setup parameters that are sent to the AP
    params = {
        'cp': int(request.form.get('cp')),
        'timestamp': int(dateutil.parser.parse(request.form.get('timestamp')).timestamp()),
        'policy': int(request.form.get('policy'))
    }

    key_model = KeyModel.find(params.get('cp'), params.get('policy'), params.get('timestamp'))

    pubk = {
        'pubk': Conversion.OS2IP(key_model.public_key)
    }

    # Get the challenge from the AP in order to prove that the user owns a specific keypair
    res = requests.get('http://{}/prove_owner'.format(current_app.config['ap_host']), params=pubk)
    y = res.json().get('y')

    # Prove the user owns the private key corresponding to a set of proofs in the block
    # Proof consists of the signature of the private key on the nonce y and the blind signature on the public key
    try:
        proof_owner = key_model.sign(y)
        blind_signature = key_model.generate_blind_signature()

        proof_resp = json.dumps({
            'y': y,
            'signature': proof_owner[1],
            'blind_signature': json.dumps(SigConversion.convert_dict_strlist(blind_signature))
        })

        # Post the proofs
        res = requests.post('http://{}/prove_owner'.format(current_app.config['ap_host']), json=proof_resp, params=params)
        if res.status_code == 200:
            # Receive access token for AP
            access_info = res.json()
            headers = {
                'Authorization': "Bearer " + access_info.get('access')
            }
            return json.dumps(headers), 200
        else:
            return "Fail", 500
    except Exception:
        return "Fail", 500


@main.route("/generate", methods=['POST'])
def generate_ap_signature():
    service_y = str(rd.get_random_bytes(256).hex())
    timestamp = int(dateutil.parser.parse(request.args.get('timestamp')).timestamp())
    policy = int(request.args.get('policy'))

    pubk = random.getrandbits(512)

    params = {
        'timestamp': timestamp,
        'policy': policy,
        'pubk': pubk
    }

    try:
        # Request challenge from AP to issue blind signature
        challenge = requests.post('http://{}/load_sig'.format(current_app.config['ap_host']), params=params).json()

        # Handle challenge
        try:
            challenge['timestamp'] = timestamp
            ap_y = challenge.pop('y')
            params = {
                'y': ap_y
            }

            e = json.dumps(handle_challenge_ap(challenge, policy, service_y))

            # Send Response
            proof_response = requests.post('http://{}/load_proof'.format(current_app.config['ap_host']), json=e, params=params)
            proofs = proof_response.json()

            # Validate Response
            try:
                validate_proof(proofs)
            except Exception as e:
                current_app.logger.error(format_exc())
                flash("Error when validating proofs: " + str(e), "access_service_error")
                return "Error when validating proofs: " + str(e), 500

            # Get AP Keymodel
            ap_key_model = KeyModel.query.filter_by(p_id_=current_app.config['ap_dlt_id'], provider_type_=2, index=service_y).first()
            if not ap_key_model:
                ap_key_model = KeyModel.query.filter_by(p_id_=current_app.config['ap_dlt_id'], provider_type_=2,
                                                        index=service_y).first()

            # Build signature
            blind_signature = ap_key_model.generate_blind_signature(proofs.get('proof'))
            ap_key_model.delete()

            return proof_response.json(), 200
        except Exception as e:
            current_app.logger.error(format_exc())
            return "Error when handling challenge: " + str(e), 500
    except Exception:
        current_app.logger.error(format_exc())
        return "Did not get a response for the challenge", 500


@main.route("/service_response", methods=['POST'])
def get_service_response():
    # Get nonce from service
    res = requests.get('http://{}/request'.format(current_app.config['service_host'])).json()
    service_y = res.get('y')

    # Setup parameters that are sent to the AP
    params = {
        'cp': int(request.form.get('cp')),
        'timestamp': int(dateutil.parser.parse(request.form.get('timestamp')).timestamp()),
        'policy': int(request.form.get('policy'))
    }

    key_model = KeyModel.query.filter_by(provider_type_=1, p_id_=params.get('cp'), policy_=params.get('policy'),
                                         interval_timestamp_=params.get('timestamp')).first()

    pubk = {
        'pubk': Conversion.OS2IP(key_model.public_key)
    }

    # Get the challenge from the AP in order to prove that the user owns a specific keypair
    res = requests.get('http://{}/prove_owner'.format(current_app.config['ap_host']), params=pubk)
    y = res.json().get('y')

    # Prove the user owns the private key corresponding to a set of proofs in the block
    # Proof consists of the signature of the private key on the nonce y and the blind signature on the public key
    try:
        proof_owner = key_model.sign(y)
        blind_signature = key_model.generate_blind_signature()

        proof_resp = json.dumps({
            'y': y,
            'signature': proof_owner[1],
            'blind_signature': json.dumps(SigConversion.convert_dict_strlist(blind_signature))
        })

        # Post the proofs
        res = requests.post('http://{}/prove_owner'.format(current_app.config['ap_host']), json=proof_resp, params=params)

        # Receive access token for AP
        access_info = res.json()
        current_app.logger.error(access_info)

        headers = {
            'Authorization': "Bearer " + access_info.get('access')
        }

        # Request challenge from AP to issue blind signature
        challenge = requests.get('http://{}/init_sig'.format(current_app.config['ap_host']), headers=headers).json()

        # Handle challenge
        try:
            challenge['timestamp'] = params.get('timestamp')
            e = json.dumps(handle_challenge_ap(challenge, params.get('policy'), service_y))

            # Send Response
            proof_response = requests.post('http://{}/generate_proof'.format(current_app.config['ap_host']), json=e, headers=headers)
            proofs = proof_response.json()

            # Validate Response
            try:
                validate_proof(proofs)
            except Exception as e:
                current_app.logger.error(format_exc())
                flash("Error when validating proofs: " + str(e), "access_service_error")
                return render_template('service_authenticate.html')

            # Get AP Keymodel
            ap_key_model = KeyModel.query.filter_by(p_id_=current_app.config['ap_dlt_id'],
                                                    provider_type_=2, index=service_y).first()

            # Build signature
            blind_signature = ap_key_model.generate_blind_signature(proofs.get('proof'))

            # Send signature on service_y to service
            resp_service = {
                'y': service_y,
                'sig': json.dumps(SigConversion.convert_dict_strlist(blind_signature)),
                'policy': params.get('policy'),
                'timestamp': params.get('timestamp')
            }

            # Delete after use
            ap_key_model.delete()

            return jsonify(resp_service), 200
        except Exception as e:
            current_app.logger.error(format_exc())
            return str(e), 500
    except Exception as e:
        current_app.logger.error(format_exc())
        return str(e), 500



