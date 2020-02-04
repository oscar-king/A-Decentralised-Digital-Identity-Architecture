import json
import os
from datetime import timedelta

from flask import request, Response, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, current_user

from ap.models.KeyModel import KeyModel
from ap.models.PolicyModel import PolicyModel
from ap.models.Session import Session
from ap.utils.ledger_utils import get_certs
from ap import create_app
from ap.utils.random import Nonce
from ap.utils.sig_utils import setup_key_handler, gen_proof_handler
from crypto_utils.conversions import SigConversion

app = create_app()


@app.route("/")
def index():
    app_name = os.getenv("APP_NAME")
    if not app_name:
        app_name = "Authentication Provider Interface Local"

    return render_template('index.html', name=app_name)


@app.route('/gen_policies')
def gen_policies():
    return render_template('generate_policies.html')


@app.route('/gen_policies', methods=['POST'])
def gen_policies_post():
    life = request.form.get('max_age')
    ds = request.form.get('description')

    PolicyModel(max_age=life, description=ds).save_to_db()
    flash("Policy has been added", 'gen_policies_success')
    return redirect(url_for('gen_policies'))


# TODO implement get_certs
@app.route("/request_certs", methods=['GET'])
def request_certs():
    """
    Takes the CP ID, timestamp, and policy number and retrieves the block on the blockchain with that transaction.
    The proofs are then returned.
    :return:
    """
    cp = request.args.get('cp')
    timestamp = int(request.args.get('timestamp'))
    policy = int(request.args.get('policy'))

    if (cp is None) or (timestamp is None) or (policy is None):
        resp = jsonify({'message': "Bad Request: Required parameters are not set"})
        return resp, 400
    else:
        try:
            return get_certs(cp, timestamp, policy)
        except Exception as e:
            return jsonify({'message': str(e)}), 500


@app.route("/prove_owner", methods=['GET', 'POST'])
def prove_owner():

    # Create challenge
    if request.method == 'GET':
        pubk = request.args.get('pubk')
        if pubk is None:
            return Response("Bad Request: Required parameters are not set.", status=400, mimetype='application/json')
        else:
            nonce = Nonce(pubk)
            saved = nonce.save()
            if saved:
                return jsonify({'y': nonce.y}), 201
            else:
                return Response("{'content': 'Something went wrong saving session info.'}",
                                status=501, mimetype='application/json')

    # Response
    elif request.method == 'POST':
        timestamp = int(request.args.get('timestamp'))
        policy = int(request.args.get('policy'))
        cp = int(request.args.get('cp'))

        if (timestamp is None) or (policy is None) or (cp is None):
            resp = jsonify({
                'message': "Bad Request: Required parameters are not set. Please check that you have set "
                           "'timestamp', 'policy', and 'cp'"
            })
            return resp, 400

        if not request.is_json:
            return Response("Bad Request: No data.", status=400, mimetype='application/json')
        else:
            data = json.loads(request.get_json())
            y = data.get('y')

            # Get data from db
            userNonce = Session.find(y)

            if userNonce:
                signature = data.get('signature')

                # Check signature
                if userNonce.check(signature):
                    userNonce.timestamp = timestamp
                    userNonce.policy = policy

                    # Check blind signature
                    blind_signature = data.get('blind_signature')
                    if userNonce.verify_blind(cp, blind_signature):
                        access_token = create_access_token(identity=userNonce.y, expires_delta=timedelta(minutes=30))
                        refresh_token = create_refresh_token(identity=userNonce.y, expires_delta=timedelta(minutes=30))

                        resp = jsonify({
                            'access': access_token,
                            'refresh': refresh_token
                        })

                        userNonce.save_to_db()
                        return resp, 200
                else:
                    return jsonify({'message': 'Invalid Signature'}), 400

            else:
                return jsonify({'message': 'No such nonce'}), 500


@app.route('/pubkey')
def get_key():
    """
    Allows services to retrieve the public key associated with a specific timestamp and policy.
    :return:
    """
    timestamp = int(request.args.get('timestamp'))
    policy = int(request.args.get('policy'))

    key = KeyModel.query.get((timestamp, policy))
    if key is None:
        return jsonify({'message': 'No key matching those parameters'}), 400
    else:
        pubkey = key.get_public_key()
        pubkey = SigConversion.convert_dict_strlist(pubkey)
        resp = json.dumps(pubkey)
        return resp, 200


@app.route('/init_sig')
@jwt_required
def init_sig():
    try:
        y = current_user.y
        resp = jsonify(setup_key_handler(y=y))
        return resp, 201
    except Exception as e:
        resp = jsonify({
            'message': str(e)
        })
        return resp, 500


@app.route('/generate_proof', methods=['POST'])
@jwt_required
def gen_proof():
    e = json.loads(request.json)
    e.pop('timestamp')

    if not e:  # If no file is submitted flash message
        resp = jsonify({
            'message': "Bad Request"
        })
        return resp, 400
    else:
        proof = json.dumps(gen_proof_handler(e))
        return proof, 201


if __name__ == '__main__':
    app.run()
