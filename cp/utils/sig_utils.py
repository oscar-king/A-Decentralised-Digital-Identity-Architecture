import json

from charm.toolbox.conversion import Conversion
from charm.toolbox.integergroup import IntegerGroupQ
from flask_jwt_extended import current_user
from cp.models.KeyModel import KeyModel
from cp.models.PolicyModel import PolicyModel
from cp.models.SigVarsModel import SigVarsModel
from cp.utils.ledger_utils import publish_pool
from crypto_utils.signatures import SignerBlindSignature
from crypto_utils.conversions import SigConversion
from _md5 import md5


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

        # If no KeyModel exists for a given policy at a set time we create one
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
        sigvars = SigVarsModel(timestamp=time, policy=policy.policy, u=signer.u, d=signer.d, s1=signer.s1,
                               s2=signer.s2, user_id=current_user.id)
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
    # Get policy from database and setup list
    policy = PolicyModel.query.get(policy)
    resp = list()

    # Iterate through the challenge responses received
    for x in es:
        # Retrieve KeyModel object
        timestamp = x.get('timestamp')
        key = policy.get_key(timestamp)

        # Retrieve SigVarsModel object so we can populate the signer with u and d
        sigvars = current_user.get_sigvar(timestamp, policy.policy)

        # Get policy pool
        pool = policy.get_pool(timestamp)
        if key and sigvars:
            signer = key.signer
            signer.d = sigvars.d
            signer.u = sigvars.u
            signer.s1 = sigvars.s1
            signer.s2 = sigvars.s2

            # Do the appropriate conversions so that we can serialize
            x['e'] = SigConversion.strlist2modint(x.get('e'))
            proofs = SigConversion.convert_dict_strlist(signer.get_proofs(x))
            hash_proof = Conversion.OS2IP(md5(json.dumps(proofs).encode()).digest())

            # Add proofs to the pool
            pool.append(proofs)

            resp.append({
                'timestamp': timestamp,
                'hash_proof': hash_proof
            })

    resp = {
        'policy': policy.policy,
        'hash_proofs': resp
    }

    return resp
