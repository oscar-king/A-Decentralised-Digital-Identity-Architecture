import json
from typing import Tuple
from charm.toolbox.conversion import Conversion
from flask import current_app

from crypto_utils.conversions import SigConversion
from crypto_utils.signatures import UserBlindSignature
from user.models.keys import KeyModel
from Crypto.Hash.SHA256 import SHA256Hash
import dotenv

dotenv.load_dotenv('.env')


def handle_challenge_util(signer_type: str, signer_id: int, resp: dict, policy: int, message: int = None):
    """
    Utility function that takes care of type conversions and ultimately calls the signing function
    :param signer_type: Whether a blind signature is being requested from a CP or an AP.
    :param signer_id: The CP\\AP's participant ID
    :param resp: The CP\\AP response to the challenge request.
    :param policy: The policy for which the signature needs to be generated.
    :param message: The message that the blind signature needs to be generated on.
    :return: e: The challenge response that is used by the CP/AP's to generate the proofs.
    """
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
    Convenience function that deals with list or dicts of challenge responses. Delegates the processing of individual
    challenges to the handle_challenge_util utility function.
    :param resp: The list of initial challenges sent by a CP.
    :param policy: The policy for which the signatures need to be generated.
    :return: (dict) A dictionary containing the policy and a list of challenge responses.
    """
    es = list()
    for x in resp:
        e = handle_challenge_util('CP', current_app.config['cp_dlt_id'], x, policy)
        es.append(e)

    ret = {
        'policy': policy,
        'es': es
    }
    return ret


def handle_response_hashes(resp: dict, cp: int, policy: int):
    """
    This helper function processes the hashes sent by a CP to a user. These hashes each correspond to a proof that will
    be published on the ledger. This function extracts the proof hash from the response and saves it with the
    corresponding model the user maintains for that signature.
    :param resp: The hashes of the proofs.
    :param cp: The participant ID of the CP on the network
    :param policy: The policy ID for which the signatures were requested.
    :return: None
    """
    for x in resp.get('data'):
        timestamp = int(x.get('timestamp'))
        key_model = KeyModel.query.filter_by(provider_type_=1,
                                             p_id_=cp, policy_=policy, interval_timestamp_=timestamp).first()
        key_model.proof_hash = x.get('hash_proof')
        key_model.proof = x.get('proof')
        key_model.save_to_db()


def prove_owner(y: str, proofs: dict, proof_hash_idx: int) -> Tuple[dict, Tuple[int, int]]:
    """
    Iterates through a block of proofs on public keys sent by an AP to a user for which a user needs to prove that they
    own the a corresponding private key for a corresponding public key proof in the block. The user proves ownership
    by signing a nonce with the appropriate private key.
    :param y: The nonce that needs signing.
    :param proofs: The block of proofs sent by the AP.
    :param proof_hash_idx: The hash of the proof that corresponds to the user-owned keypair.
    :return: (int, int): The hash of the proof and the signature on y.
    """
    for x in json.loads(proofs.get('proofs')):
        if x.get('hash') == proof_hash_idx:
            key_model = KeyModel.query.filter_by(proof_hash_=str(proof_hash_idx)).first()
            return x, key_model.sign(y)
    raise Exception("Couldn't find hash matching input parameters in block.")


def hash_util(d: dict or list) -> int:
    """
    Creates a SHA256 hash of dict or list. Merely a helper function.
    :param d: Input on which a hash needs to be generated.
    :return: (int) Hash of the input d.
    """
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

# def verify_block_hash(data: dict) -> bool:
#     proofs = json.loads(data.get('proofs'))
#     p_hash = int(data.get('proofs_hash'))
#
#     tmp_hash = hash_util(proofs)
#
#     if p_hash != tmp_hash:
#         raise Exception("SHA256 hash of received proof block doesn't match the one calculated")
#     else:
#         return True

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
    """
    Wrapper function to interface with the handle_challenge_util function when creating blind signatures with an AP.
    :param challenge: Challenge sent by an AP.
    :param policy: Policy on which the blind signature is requested.
    :param service_y: The nonce sent by the service that a user has requested access to.
    :return: Challenge response 'e' which needs to be sent back to the AP.
    """
    return handle_challenge_util('AP', current_app.config['cp_dlt_id'], challenge, policy, int(service_y, 16))
