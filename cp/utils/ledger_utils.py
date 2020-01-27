import json
import os, dotenv
import requests
from cp.models.PolicyModel import PolicyModel
from crypto_utils.conversions import SigConversion

dotenv.load_dotenv('../.env')


# TODO delete pool after
def publish_pool(policy: int, timestamp: int) -> bool:
    """

    :param policy:
    :param timestamp:
    :return:
    """
    pol = PolicyModel.query.get(policy)
    pool = pol.get_pool(timestamp) if pol is not None else None
    key = pol.get_key(timestamp) if pol is not None else None
    res = requests.get("http://localhost:3002/api/ProofBlock")
    cpid = os.environ.get('cp_dlt_id')
    if (res.status_code == 200) and (key is not None) and (pol is not None):
        data = {
            "$class": "digid.ProofBlock",
            "assetId": len(res.json()),
            "owner": "resource:digid.CertificationProvider#" + cpid,
            "timestamp": timestamp,
            "lifetime": pol.lifetime,
            "key": {
                "$class": "digid.PublicKey",
                "key": str(json.dumps(SigConversion.convert_dict_strlist(key.get_public_key()))),
                "policy": policy
            },
            "proofHash": str(pool.get_pool_hash()),
            "proofs": str(json.dumps(pool.pool))
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

