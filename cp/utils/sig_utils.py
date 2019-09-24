import json

from charm.toolbox.integergroup import IntegerGroupQ
from flask_jwt_extended import current_user
from cp.models.KeyModel import KeyModel
from cp.models.PolicyModel import PolicyModel
from cp.models.SigVarsModel import SigVarsModel
from crypto_utils.signatures import SignerBlindSignature
from crypto_utils.conversions import SigConversion


def setup_key_handler(timestamp, number, policy):
    """
    :param timestamp: (int) Timestamp of when the first knowledge proofs should be available on the ledger
    :param number: (int) Number of requested credentials
    :param policy: (int) The policy that a user is requesting credentials for.
    :return: (dict)
    """
    resp = []
    policy = PolicyModel.query.get(policy)
    if not policy:
        raise Exception("Couldn't find policy")
    for i in range(0, number):
        # Retrieve key for particular timestamp and policy combination
        time = timestamp + (i * policy.publication_interval)

        key_model = policy.get_key(time)
        if key_model is None:
            signer = SignerBlindSignature(IntegerGroupQ())

            new = KeyModel(time, policy, signer)
            policy.keys.append(new)

            new.save_to_db()
            policy.save_to_db()
        else:
            signer = key_model.signer

        # Retrieve pubkey and generate challenge to send in the response
        pubkey = SigConversion.convert_dict_strlist(signer.get_public_key())
        challenge = SigConversion.convert_dict_strlist(signer.get_challenge())

        # Save
        sigvars = SigVarsModel(timestamp=time, policy=policy.policy, u=signer.u, d=signer.d, user_id=current_user.id)
        sigvars.save_to_db()

        data = {
            'timestamp': time,
            'public_key': pubkey,
            'challenge': challenge
        }

        resp.append(data)

    return resp


# TODO add the responses to the ledger
def gen_proofs_handler(policy, es):
    policy = PolicyModel.query.get(policy)
    resp = list()
    for x in es:
        timestamp = x.get('timestamp')
        key = policy.get_key(timestamp)
        sigvars = current_user.get_sigvar(timestamp, policy.policy)
        if key and sigvars:
            signer = key.signer
            signer.d = sigvars.d
            signer.u = sigvars.u

            x['e'] = SigConversion.strlist2modint(x.get('e'))
            proofs = SigConversion.convert_dict_strlist(signer.get_proofs(x))
            hash_proof = hash(json.dumps(proofs))

            resp.append({
                'timestamp': timestamp,
                'hash_proof': hash_proof
            })

    resp = {
        'policy': policy.policy,
        'hash_proofs': resp
    }
    return resp
