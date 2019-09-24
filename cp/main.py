from flask import Blueprint, render_template, redirect, url_for, request, flash, session, json, Response, jsonify
from flask_jwt_extended import jwt_required
import os

from cp.models.PolicyModel import PolicyModel
from cp.models.UserModel import UserModel
from cp.utils.sig_utils import setup_key_handler, gen_proofs_handler
from cp.workers import post_key_worker


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
    flash("Policy has been added", 'gen_policies')
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



# @main.route('/generate_proofs')
# @jwt_required
# def post_keys():
#     return render_template('post_keys.html')


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
    # worker = post_key_worker.PostKeyWorker(1)
    # worker.schedule_key_publishing("Key", ["This", "is", "a", "client_test"])
    # return redirect(url_for('main.thanks'))
        return resp, 201


@main.route('/thanks')
@jwt_required
def thanks():
    return render_template('thanks.html')