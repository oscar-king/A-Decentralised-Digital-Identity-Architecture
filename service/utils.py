import json
import requests
from flask import current_app
from crypto_utils.conversions import SigConversion
from service.models import APKeyModel


# TODO: Ideally the keys should have been distributed by some other means
def get_ap_key(timestamp: int, policy: int):
    key = APKeyModel.find(timestamp, policy)
    if key is not None:
        return key.public_key
    else:
        params = {
            'policy': policy,
            'timestamp': timestamp
        }
        res = requests.get('http://{}/pubkey'.format(current_app.config['ap_host']), params=params)
        if res.status_code == 200:
            key = res.json()
            APKeyModel(timestamp, policy, json.dumps(key)).save_to_db()
            return SigConversion.convert_dict_modint(key)
