import json
from typing import Tuple

from charm.toolbox.conversion import Conversion
from crypto_utils.conversions import SigConversion
from crypto_utils.signatures import UserBlindSignature
from user.models.keys import KeyModel
from Crypto.Hash.SHA256 import SHA256Hash
import os
import dotenv

dotenv.load_dotenv('.env')


def handle_challenge_util(signer_type: str, signer_id: int, resp: dict, policy: int, message: int = None):
    pubk = SigConversion.convert_dict_modint(resp.get('public_key'))
    challenge = SigConversion.convert_dict_modint(resp.get('challenge'))
    timestamp = resp.get('timestamp')

    # Generate signer and keymodel
    signer = UserBlindSignature(pubk)
    key_model = KeyModel(provider_type=signer_type, p_id=signer_id, policy=policy, signer=signer, interval=timestamp)

    if message is None:
        message = Conversion.OS2IP(key_model.public_key)

    e = SigConversion.convert_dict_strlist(signer.challenge_response(challenge, message))
    e['timestamp'] = timestamp
    key_model.signer = signer
    key_model.save_to_db()

    return e


def handle_challenge(resp: dict or list, policy: int):
    """
    Handles the challenge received from a Certification Provider
    :param resp:
    :param policy:
    :return:
    """
    es = list()
    for x in resp:
        e = handle_challenge_util('CP', int(os.environ.get('cp_dlt_id')), x, policy)
        es.append(e)

    ret = {
        'policy': policy,
        'es': es
    }
    return ret


def handle_response_hashes(resp: dict, cp: int, policy: int):
    for x in resp.get('hash_proofs'):
        timestamp = int(x.get('timestamp'))
        proof_hash = x.get('hash_proof')
        key_model = KeyModel.query.filter_by(provider_type_=1,
                                             p_id_=cp, policy_=policy, interval_timestamp_=timestamp).first()
        key_model.proof_hash = proof_hash
        key_model.save_to_db()


# TODO generate signature on x
def prove_owner(y: str, proofs: dict, proof_hash_idx: int) -> Tuple[dict, Tuple[int, int]]:
        for x in json.loads(proofs.get('proofs')):
            if x.get('hash') == proof_hash_idx:
                key_model = KeyModel.query.filter_by(proof_hash_= str(proof_hash_idx)).first()
                return x, key_model.sign(y)
        raise Exception("Couldn't find hash matching input parameters in block.")


def hash_util(d: dict or list) -> int:
    hash_tmp = SHA256Hash().new(json.dumps(d).encode())
    return Conversion.OS2IP(hash_tmp.digest())


def validate_block(data: dict) -> None:
    """
    Checks if the hash of the proofs sent in the Response is the same as the one that is generated user side. If they do
    not match an exception is raised.
    :param data:
    :return: (None)
    """
    proofs = json.loads(data.get('proofs'))
    p_hash = int(data.get('proofs_hash'))

    tmp_hash = hash_util(proofs)

    if p_hash != tmp_hash:
        raise Exception("SHA256 hash of received proof block doesn't match the one calculated")


def validate_proof(data: dict) -> None:
    """
    Checks if the hash of the single proof sent by the AP matches the one that is calculated on the user side. If they
    do not match an exception is raised.
    :param data:
    :return:
    """
    hash_proof = data.get('hash')
    tmp_hash = hash_util(data.get('proof'))

    if hash_proof != tmp_hash:
        raise Exception("SHA256 hash of received proof doesn't match the one calculated")


def handle_challenge_ap(challenge: dict, policy: int, service_y):
    return handle_challenge_util('AP', int(os.environ.get('ap_dlt_id')), challenge, policy, int(service_y, 16))