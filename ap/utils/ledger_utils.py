import json

import requests
from flask import jsonify

from crypto_utils.conversions import SigConversion


def get_block(cp: int, timestamp: int, policy: int):
    """
    Gets a specific block from the ledger.
    :param cp: The ID of the CP on the ledger.
    :param timestamp: The timestamp at which the proofs are valid.
    :param policy: The CP policy the proofs are associated with.
    :return:
    """
    params = {
        'ownerParam': "resource:digid.CertificationProvider#" + str(cp),
        'timestampParam': timestamp,
        'policyParam': policy
    }
    res = requests.get('http://rest_api:3000/api/queries/ProofBlockQuery', params=params)
    data = res.json()[0] if len(res.json()) != 0 else None
    return data


def get_cp_pubkey(cp: int, timestamp: int, policy: int):
    """
    Gets the public key from the ledger for a given timestamp and policy.
    :param cp: The ID of the CP on the ledger.
    :param timestamp: The timestamp at which the proofs are valid.
    :param policy: The CP policy the proofs are associated with.
    :return:
    """
    block = get_block(cp, timestamp, policy)
    key_json = block.get('key')
    key_str = json.loads(key_json.get('key'))
    key = SigConversion.convert_dict_modint(key_str)
    return key


def get_certs(cp: int, timestamp: int, policy: int):
    """
    Gets the proofs as well as the hash of the proof block.
    :param cp: The ID of the CP on the ledger.
    :param timestamp: The timestamp at which the proofs are valid.
    :param policy: The CP policy the proofs are associated with.
    :return:
    """
    data = get_block(cp, timestamp, policy)
    if data:
        resp = jsonify({
            'proofs_hash': data.get('proofHash'),
            'proofs': data.get('proofs')
        })
        return resp, 200
    else:
        raise Exception("No block matching those parameters exists.")
