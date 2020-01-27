import os

import dateutil.parser
from flask import Blueprint, render_template, redirect, url_for, request, flash, json, jsonify
from flask_jwt_extended import jwt_required

from cp.models.PolicyModel import PolicyModel
from cp.models.UserModel import UserModel
from cp.utils.ledger_utils import publish_pool
from cp.utils.sig_utils import setup_key_handler, gen_proofs_handler

main = Blueprint('main', __name__, template_folder='templates')


@main.route('/')
def index():
    app_name = os.getenv("APP_NAME")
    if not app_name:
        app_name = "Certification Provider Interface"

    return render_template('index.html', name=app_name)


# TODO Return all active signatures
@main.route('/active_keys')
def get_keys():
    return json.dumps("This will be a list of active signatures")


@main.route('/users')
def get_users():
    user = []
    for x in UserModel.query.all():
        user.append(x)
    return str(user)


#TODO seems not to work
@main.route('/reset_users')
def reset_users():
    map(lambda x: x.delete(), UserModel.query.all())
    print()
    return redirect(url_for('main.get_users'))


@main.route('/gen_policies')
def gen_policies():
    return render_template('generate_policies.html')


@main.route('/gen_policies', methods=['POST'])
def gen_policies_post():
    i = request.form.get('interval')
    life = request.form.get('lifetime')
    ds = request.form.get('description')

    PolicyModel(publication_interval=i, lifetime=life, description=ds).save_to_db()
    flash("Policy has been added", 'gen_policies_success')
    return redirect(url_for('main.gen_policies'))


@main.route('/pols')
def get_policies():
    pols = list()
    for x in PolicyModel.query.all():
        pols.append(str(x))
    return json.dumps(pols, indent=2)


@main.route('/setup_keys')
@jwt_required
def setup_keys():
    time = request.args.get('time')
    n = request.args.get('number')
    policy = request.args.get('policy')

    if (time is None) or (n is None) or (policy is None):
        resp = jsonify({
            'message': "Bad Request: Required parameters are not set. Please check that you have set "
                       "'time', 'number', and 'policy'"
        })

        return resp, 400
    else:
        try:
            resp = json.dumps(setup_key_handler(timestamp=int(time), number=int(n), policy=int(policy)))
            return resp, 201
        except Exception:
            resp = jsonify({
                'message': "Couldn't find policy"
            })

            return resp, 500

@main.route('/publish_policies')
def publish():
    return render_template('publish.html')


@main.route('/publish_policies', methods=['POST'])
def publish_policies():
    policy = int(request.form.get('policy'))
    timestamp = int(dateutil.parser.parse(request.form.get('timestamp')).timestamp())

    if publish_pool(policy, timestamp):
        flash("Proofs published", 'pub_policies_success')
        return redirect(url_for('main.publish_policies'))
    else:
        flash("Proofs not published. Possibly because the policy does not exist, incorrect timestamp, or API error",
              'pub_policies_fail')
        return redirect(url_for('main.publish_policies'))


# TODO Link up worker so that these keys are posted onto the blockchain. Return needs to be the (CP_1, and the interval)
@main.route('/generate_proofs', methods=['POST'])
@jwt_required
def generate_proofs():
    data = json.loads(request.json)
    es = data.get('es')
    policy = data.get('policy')

    if not data: # If no file is submitted flash message
        flash('Please submit file', 'post_keys')
        resp = jsonify({
            'message': "Bad Request"
        })
        return resp, 400
    else:
        resp = json.dumps(gen_proofs_handler(policy, es))
        return resp, 201


@main.route('/thanks')
@jwt_required
def thanks():
    return render_template('thanks.html')