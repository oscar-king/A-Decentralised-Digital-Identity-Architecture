import json

from Crypto.Hash.SHA256 import SHA256Hash
from charm.toolbox.conversion import Conversion
from flask_jwt_extended import current_user

from ap.models.KeyModel import KeyModel
from ap.models.PolicyModel import PolicyModel
from ap.models.Session import Session
from crypto_utils.conversions import SigConversion


def setup_key_handler(y: str):
    session = Session.find(y)
    policy = PolicyModel.query.get(session.policy)

    if policy is None:
        raise Exception("Couldn't find policy matching session information. Consider adding a policy")
    else:
        key_model = policy.get_key(session.timestamp)
        signer = key_model.signer

        # Retrieve pubkey and generate challenge to send in the response
        pubkey = SigConversion.convert_dict_strlist(signer.get_public_key())
        challenge = SigConversion.convert_dict_strlist(signer.get_challenge())

        # Update and Save
        session.u = signer.u
        session.d = signer.d
        session.s1 = signer.s1
        session.s2 = signer.s2
        session.save_to_db()

        data = {
            'public_key': pubkey,
            'challenge': challenge
        }
        return data


def gen_proof_handler(e: dict):
    key = KeyModel.query.get((current_user.timestamp, current_user.policy))
    signer = key.signer
    signer.d = current_user.d
    signer.u = current_user.u
    signer.s1 = current_user.s1
    signer.s2 = current_user.s2

    # Do the appropriate conversions so that we can serialize
    e = SigConversion.convert_dict_modint(e)
    proofs = SigConversion.convert_dict_strlist(signer.get_proofs(e))
    hash_tmp = SHA256Hash().new(json.dumps(proofs).encode())
    hash_proof = Conversion.OS2IP(hash_tmp.digest())

    resp = {
        'proof': proofs,
        'hash': hash_proof
    }

    return resp
