import json
from urllib.parse import quote

import requests
from flask import jsonify
from crypto_utils.conversions import SigConversion
from ap.models.CPKeyModel import CPKeyModel

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
    res = requests.get('http://ap_rest_api:3000/api/queries/ProofBlockQuery', params=params)
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
    key = CPKeyModel.find(timestamp, policy)
    if key is not None:
        return key.public_key
    else:
        block = get_block(cp, timestamp, policy)
        if block is not None:
            key_json = block.get('key')
            key_str = json.loads(key_json.get('key'))
            key = SigConversion.convert_dict_modint(key_str)
            return key
        else:
            return None


def cache_cp_pubkey(app):
    # query_filter = quote('{"owner": "resource:digid.CertificationProvider#2000"}')
    # params = {"filter":query_filter}
    # res = requests.get('http://ap_rest_api:3000/api/queries/ProofBlockQuery', params=params)
    with app.app_context():
        try:
            res = requests.get("http://ap_rest_api:3000/api/ProofBlock?filter=%7B%22owner%22%3A%20%22resource%3Adigid.CertificationProvider%232000%22%7D")
            data = res.json()
            if len(res.json()) == 0:
                return
            for block in data:
                timestamp = block.get('timestamp')
                policy = block.get('key').get('policy')
                pubkey = block.get('key').get('key')
                if CPKeyModel.find(timestamp, policy) is None:
                    new_cp_key = CPKeyModel(timestamp, policy, pubkey)
                    new_cp_key.save_to_db()
        except Exception:
            return


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
