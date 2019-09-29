import json
import requests
from cp.models.PolicyModel import PolicyModel


# TODO Certification Provider ID currently hardcoded in the value of the owner key needs to be changed.
from crypto_utils.conversions import SigConversion


def publish_pool(policy: int, timestamp: int) -> bool:
    """

    :param policy:
    :param timestamp:
    :return:
    """
    pol = PolicyModel.query.get(policy)
    pool = pol.get_pool(timestamp)
    key = pol.get_key(timestamp)
    res = requests.get("http://localhost:3002/api/ProofBlock")
    if res.status_code == 200 and key is not None:
        data = {
            "$class": "digid.ProofBlock",
            "assetId": len(res.json()),
            "owner": "resource:digid.CertificationProvider#5488",
            "timestamp": timestamp,
            "key": {
                "$class": "digid.PublicKey",
                "key": json.dumps(SigConversion.convert_dict_strlist(key.get_public_key())),
                "policy": policy
            },
            "proofHash": hash(pool),
            "proofs": pool.pool
        }

        res = requests.post("http://localhost:3002/api/ProofBlock", json=data)
        if res.status_code == 200:
            return True
        else:
            return False
    else:
        return False


def revoke_key(policy: int, timestamp: int) -> bool:
    """

    :param policy:
    :param timestamp:
    :return:
    """
    args = {
        'participantIDParam': '5488',
        'timestampParam': timestamp,
        'policyParam': policy
    }
    res = requests.delete('http://localhost:3001/api/queries/ProofBlockQuery', params=args)
    if res.status_code == 200:
        return True
    else:
        return False

