# from Crypto.Hash import SHA256
# from Crypto.PublicKey import ECC
# from Crypto.Signature import DSS
# from charm.toolbox.conversion import Conversion
#
# from user.models.keys import KeyModel
#
#
# class TestKeyModel():
#     def test_sign(self):
#         keyModel = KeyModel(provider_type=1, p_id=2000)
#         y = hex(1231231)
#         (h, sig) = keyModel.sign(y)
#         sig = Conversion.IP2OS(sig)
#         h = Conversion.IP2OS(h)
#
#         pubk = keyModel.public_key
#         msg_hash = SHA256.new(pubk)
#         ecc = ECC.import_key(pubk)
#         verif = DSS.new(ecc, 'fips-186-3')
#         assert h == msg_hash.digest()
#         try:
#             verif.verify(msg_hash, sig)
#             assert True
#         except:
#             assert False