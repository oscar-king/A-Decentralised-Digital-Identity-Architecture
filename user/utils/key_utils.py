from charm.toolbox.conversion import Conversion
from crypto_utils.conversions import SigConversion
from crypto_utils.signatures import UserBlindSignature
from user.models.keys import KeyModel


def handle_challenge(resp, policy):
    es = list()
    for x in resp:
        # Parse resp parameter
        pubk = SigConversion.convert_dict_modint(x.get('public_key'))
        challenge = SigConversion.convert_dict_modint(x.get('challenge'))
        timestamp = x.get('timestamp')

        # Generate signer and keymodel
        signer = UserBlindSignature(pubk)
        key_model = KeyModel(interval=timestamp, signer=signer, policy=policy)
        message = Conversion.OS2IP(key_model.public_key)

        e = SigConversion.convert_dict_strlist(signer.challenge_response(challenge, message))
        e['timestamp'] = timestamp
        es.append(e)
        key_model.save_to_db()

    ret = {
        'policy': policy,
        'es': es
    }
    return ret


def blind_number(number):
    return number