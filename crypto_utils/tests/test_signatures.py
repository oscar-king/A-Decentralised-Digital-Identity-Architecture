import pytest
from Crypto.PublicKey import ECC
from Crypto.Random.random import sample
from charm.toolbox.conversion import Conversion
from charm.toolbox.integergroup import IntegerGroupQ

from crypto_utils.signatures import SignerBlindSignature, UserBlindSignature, BlindSignatureVerifier, hash_int


@pytest.fixture(name="protocol", scope="function")
def sig_manager():
    class Protocol:
        def __init__(self):
            self.groupObj = IntegerGroupQ()
            self.groupObj.paramgen(256)
            self.signer = SignerBlindSignature(self.groupObj, 0, 0, 512)
            self.user = UserBlindSignature(self.signer.get_public_key())
            self.verify = BlindSignatureVerifier(self.signer.get_public_key())
            self.user = UserBlindSignature(self.signer.get_public_key())
            self.sig, self.e, self.message = None, None, None
            self.zeta, self.zeta1, self.rho = None, None, None
            self.omega, self.sigma1, self.sigma2 = None, None, None
            self.delta, self.mu, self.tmp1 = None, None, None
            self.tmp2, self.tmp3, self.tmp4 = None, None, None

        def setup_method(self, message=None):
            key = ECC.generate(curve='P-256')
            self.message = Conversion.OS2IP(key.public_key().export_key(format='DER')) if message is None else message
            challenge = self.signer.get_challenge()
            self.e = self.user.challenge_response(challenge, self.message)
            proofs = self.signer.get_proofs(self.e)
            self.sig = self.user.gen_signature(proofs)

        def values(self):
            self.zeta = self.sig.get('zeta')
            self.zeta1 = self.sig.get('zeta1')
            self.rho = self.sig.get('rho')
            self.omega = self.sig.get('omega')
            self.sigma1 = self.sig.get('sigma1')
            self.sigma2 = self.sig.get('sigma2')
            self.delta = self.sig.get('delta')
            self.mu = self.sig.get('mu')
            self.tmp1 = (self.verify.g ** self.rho) * (self.verify.y ** self.omega) % self.verify.p
            self.tmp2 = (self.verify.g ** self.sigma1) * (self.zeta1 ** self.delta) % self.verify.p
            self.tmp3 = (self.verify.h ** self.sigma2) * ((self.zeta / self.zeta1) ** self.delta) % self.verify.p
            self.tmp4 = (self.verify.z ** self.mu) * (self.zeta ** self.delta) % self.verify.p

    return Protocol()


class TestBlindSignatures:
    def test_blind_sign_correctness(self, protocol):
        for i in range(0, 100):
            protocol.setup_method()
            protocol.values()

            (alpha, beta1, beta2, eta) = protocol.user.__get__(['alpha', 'beta1', 'beta2', 'eta'])
            (t2, t4) = protocol.user.__get__(['t2', 't4'])

            # This should pass
            assert protocol.omega + protocol.delta == protocol.e.get('e') + t2 + t4
            assert protocol.tmp1 == alpha
            assert protocol.tmp2 == beta1
            assert protocol.tmp3 == beta2
            assert protocol.tmp4 == eta

    def test_blind_sign_correct_verify(self, protocol):
        for i in range(0, 100):
            protocol.setup_method()
            protocol.values()

            # This should be equal
            p1 = (protocol.omega + protocol.delta) % protocol.verify.q
            p2 = hash_int([protocol.zeta, protocol.zeta1, protocol.tmp1, protocol.tmp2,
                           protocol.tmp3, protocol.tmp4, protocol.message]) % protocol.verify.q

            assert p1 == p2

    def test_blind_sign_correct_not_verify(self, protocol):
        for i in range(0, 100):
            protocol.setup_method()
            protocol.values()

            # This should be equal
            p1 = (protocol.omega + protocol.delta) % protocol.verify.q
            p2 = hash_int([protocol.zeta, protocol.zeta1, protocol.tmp1, protocol.tmp2,
                           protocol.tmp3, protocol.tmp4, protocol.message+1]) % protocol.verify.q

            assert p1 != p2

    def test_blind_sign_encode_decode(self, protocol):
        protocol.setup_method()
        protocol.values()

        encoding = protocol.user.encode()
        user_sig = UserBlindSignature().decode(encoding)

        assert protocol.user == user_sig

    def test_hash_int_list(self):
        for i in range(1000):
            ls1 = sample(population=range(100, 999999999999), k=6)
            ls2 = sample(population=range(100, 999999999999), k=6)
            while ls1 == ls2:
                ls2 = sample(population=range(100, 999999999999), k=6)

            ds3 = hash_int(ls1)
            ds4 = hash_int(ls2)
            ds3c = hash_int(ls1)
            ds4c = hash_int(ls2)

            assert ds3 == ds3c
            assert ds4 == ds4c
            assert ds3 != ds4

    def test_encode_decode(self, protocol):

        signer = protocol.signer
        encoded = signer.encode()
        decoded = SignerBlindSignature().decode(encoded)

        assert signer == decoded

    def test_gen_then_verify(self, protocol):
        protocol.setup_method()
        protocol.values()

        signature = protocol.sig
        message = protocol.message

        assert protocol.verify.verify(signature, message)