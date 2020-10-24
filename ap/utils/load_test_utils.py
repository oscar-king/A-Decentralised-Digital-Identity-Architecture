import json

from Crypto import Random as rd
from Crypto.Hash.SHA256 import SHA256Hash
from charm.toolbox.conversion import Conversion

from ap.models.KeyModel import KeyModel
from ap.models.PolicyModel import PolicyModel
from ap.models.Session import Session
from crypto_utils.conversions import SigConversion


def load_test_handler(pubk: int, timestamp: int, policy_id: int):
    session = Session(rd.get_random_bytes(128).hex(), pubk)
    policy = PolicyModel.find(policy_id)

    if policy is None:
        raise Exception("Couldn't find policy matching session information. Consider adding a policy")
    else:
        key_model = policy.get_key(timestamp)
        signer = key_model.signer

        # Retrieve pubkey and generate challenge to send in the response
        pubkey = SigConversion.convert_dict_strlist(signer.get_public_key())
        challenge = SigConversion.convert_dict_strlist(signer.get_challenge())

        # Update and Save
        session.timestamp = timestamp
        session.policy = policy_id
        session.u = signer.u
        session.d = signer.d
        session.s1 = signer.s1
        session.s2 = signer.s2
        session.save_to_db()

        data = {
            'public_key': pubkey,
            'challenge': challenge,
            'y': session.y
        }
        return data


def load_test_proof_handler(e: dict, y: str):
    session = Session.find(y)
    key = KeyModel.query.get((session.timestamp, session.policy))

    signer = key.signer
    signer.d = session.d
    signer.u = session.u
    signer.s1 = session.s1
    signer.s2 = session.s2

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