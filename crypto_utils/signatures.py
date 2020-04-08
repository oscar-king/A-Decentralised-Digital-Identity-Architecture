"""
:Blind Signature Scheme

| From: "M. Abe A Secure Three-move Blind Signature Scheme for Polynomially
| 	Many Signatures"
| Published in: EUROCRYPT 2001
| Available from: http://www.iacr.org/archive/eurocrypt2001/20450135.pdf

* type:           signature
* setting:        integer groups

Code adapted from: https://jhuisi.github.io/charm/_modules/protocol_a01.html#Asig
"""
import hashlib
import json

from Crypto.Hash.SHA256 import SHA256Hash
from charm.toolbox.conversion import Conversion
from charm.toolbox.integergroup import IntegerGroupQ
from charm.toolbox.integergroup import integer, randomBits

from crypto_utils.conversions import SigConversion


def SHA1(bytes1):
    s1 = hashlib.new('sha256')
    s1.update(bytes1)
    return s1.digest()


def hash_int(args):
    hash = SHA256Hash()
    for arg in args:
        hash.update(Conversion.IP2OS(arg))
    return Conversion.OS2IP(hash.digest())


def xgcd(a, b):
    """return (g, x, y) such that a*x + b*y = g = gcd(a, b)"""
    x0, x1, y0, y1 = 0, 1, 1, 0
    while a != 0:
        q, b, a = b // a, a, b % a
        y0, y1 = y1, y0 - q * y1
        x0, x1 = x1, x0 - q * x1
    return b, x0, y0


def mulinv(a, b):
    a = int(a)
    b = int(b)
    """return x such that (x * a) % b == 1"""
    g, x, _ = xgcd(a, b)
    if g == 1:
        return x % b
    return x % b


class BlindSigner:
    """
    Should not be subclassed. Decode only works on the two currently defined subclasses.
    """
    def __eq__(self, other):
        s_dict = {**self.__dict__}
        o_dict = {**other.__dict__}
        s_group = str(s_dict.pop("group"))
        o_group = str(o_dict.pop("group"))
        return (s_dict == o_dict) and (s_group == o_group)

    def __encode_dict__(self, dict_):
        tmp = {**dict_}
        for key in tmp:
            if tmp.get(key) is not None:
                tmp[key] = SigConversion.modint2strlist(tmp.get(key))
            else:
                tmp[key] = 'null'
        return tmp

    def encode(self):
        tmp = {**self.__dict__}
        tmp.pop("group")
        db = tmp.get('db')
        db = self.__encode_dict__(db) if db is not None else None
        tmp = self.__encode_dict__(tmp)
        if db is not None:
            tmp['db'] = db
        return json.dumps(tmp)

    def decode(self, jsn):
        obj = json.loads(jsn)
        db = obj.pop('db') if obj.get('db') is not None else None

        if isinstance(self, SignerBlindSignature):
            new = SignerBlindSignature(IntegerGroupQ())
        elif isinstance(self, UserBlindSignature):
            new = UserBlindSignature()
        else:
            raise Exception("Unexpected argument")

        for key in obj:
            if obj[key] == 'null':
                attr_val = None
            else:
                attr_val = SigConversion.strlist2modint(obj[key])
            setattr(new, key, attr_val)
        if db:
            for key in db:
                db[key] = SigConversion.strlist2modint(db[key])
            setattr(new, 'db', db)
        new.group = IntegerGroupQ()
        new.group.setparam(p=new.p, q=new.q)
        return new


class UserBlindSignature(BlindSigner):
    """
    This class represents the entity who wishes to have a certain message blindly signed.
    """
    def __init__(self, input_=None):
        if input_ is not None:
            self.p = input_.get('p')
            self.q = input_.get('q')
            self.g = input_.get('g')
            self.y = input_.get('y')
            self.h = input_.get('h')
            self.z = input_.get('z')
            self.group = IntegerGroupQ()
            self.group.setparam(p=self.p, q=self.q)
            self.db = input_.get('db')
            if self.db is None:
                self.db = {}

    def __store__(self, *args):
        for i in args:
            if isinstance(i, tuple):
                self.db[i[0]] = i[1]
        return None

    def __get__(self, keys, _type=tuple):
        if not type(keys) == list:
            return
        if _type == tuple:
            ret = []
        else:
            ret = {}
        # get the data
        for i in keys:
            if _type == tuple:
                ret.append(self.db[i])
            else:  # dict
                ret[i] = self.db[i]
        # return data
        if _type == tuple:
            return tuple(ret)
        return ret

    def challenge_response(self, input, message):
        rnd = input.get('rnd')
        a = input.get('a')
        b1 = input.get('b1')
        b2 = input.get('b2')

        msg = integer(Conversion.OS2IP(SHA1(Conversion.IP2OS(rnd))))
        z1 = (msg ** ((self.p - 1) / self.q)) % self.p

        gamma = self.group.random()

        tau = self.group.random()

        t1 = self.group.random()
        t2 = self.group.random()
        t3 = self.group.random()
        t4 = self.group.random()
        t5 = self.group.random()

        zeta = self.z ** gamma
        zeta1 = z1 ** gamma
        zeta2 = zeta / zeta1

        alpha = a * (self.g ** t1) * (self.y ** t2) % self.p
        beta1 = (b1 ** gamma) * (self.g ** t3) * (zeta1 ** t4) % self.p
        beta2 = (b2 ** gamma) * (self.h ** t5) * (zeta2 ** t4) % self.p
        eta = self.z ** tau

        epsilon = integer(hash_int([zeta, zeta1, alpha, beta1, beta2, eta, message])) % self.q
        e = (epsilon - t2 - t4) % self.q

        self.__store__(self, ('z1', z1), ('zeta', zeta), ('zeta1', zeta1))
        self.__store__(self, ('zeta2', zeta2), ('alpha', alpha), ('beta1', beta1), ('beta2', beta2))
        self.__store__(self, ('t1', t1), ('t2', t2), ('t3', t3), ('t4', t4), ('t5', t5))
        self.__store__(self, ('gamma', gamma), ('tau', tau), ('eta', eta))

        return {'e': e}

    def gen_signature(self, proofs: dict) -> dict:
        r = proofs.get('r')
        c = proofs.get('c')
        d = proofs.get('d')
        s1 = proofs.get('s1')
        s2 = proofs.get('s2')

        (zeta, zeta1, z, z1) = self.__get__(['zeta', 'zeta1', 'zeta2', 'z1'])
        (t1, t2, t3, t4, t5) = self.__get__(['t1', 't2', 't3', 't4', 't5'])
        (gamma, tau, eta) = self.__get__(['gamma', 'tau', 'eta'])

        rho = (r + t1) % self.q
        omega = (c + t2) % self.q

        sigma1 = ((gamma * s1) + t3) % self.q
        sigma2 = ((gamma * s2) + t5) % self.q

        delta = (d + t4) % self.q

        mu = (tau - (delta * gamma)) % self.q

        return {'zeta': zeta, 'zeta1': zeta1, 'rho': rho, 'omega': omega,
                'sigma1': sigma1, 'sigma2': sigma2, 'delta': delta, 'mu': mu}


class SignerBlindSignature(BlindSigner):
    """
    This class represents the entity which blindly signs a given value.
    """
    def __init__(self, group=None, p=0, q=0, secparam=512):
        self.group = group if group is not None else IntegerGroupQ()
        self.group.p, self.group.q, self.group.r = p, q, 2

        if self.group.p == 0 or self.group.q == 0:
            self.group.paramgen(secparam)

        self.p = self.group.p
        self.q = self.group.q

        self.x, self.g, = self.group.random(), self.group.randomGen()
        self.z, self.h, = self.group.randomGen(), self.group.randomGen()

        self.y = (self.g ** self.x) % self.p

        hs1 = hashlib.new('sha256')
        hs1.update(Conversion.IP2OS(integer(self.p)))
        hs1.update(Conversion.IP2OS(integer(self.q)))
        hs1.update(Conversion.IP2OS(integer(self.g)))
        hs1.update(Conversion.IP2OS(integer(self.h)))
        hs1.update(Conversion.IP2OS(integer(self.y)))

        msg = integer(Conversion.OS2IP(hs1.digest()))
        self.z = ((msg ** ((self.p - 1) / self.q)) % self.p)

        self.u = None
        self.d = None
        self.s1 = None
        self.s2 = None

    # Signer state 1
    def get_public_key(self):
        return {'p': self.p, 'q': self.q, 'g': self.g, 'y': self.y, 'h': self.h, 'z': self.z}

    def get_private_key(self):
        return self.x

    def get_challenge(self):
        rnd = randomBits(80)

        msg = integer(Conversion.OS2IP(SHA1(Conversion.IP2OS(rnd))))

        z1 = ((msg ** ((self.p - 1) / self.q)) % self.p)
        inv_z1 = (mulinv(z1, self.p)) % self.p

        z2 = (int(self.z) * int(inv_z1)) % self.p

        self.u = self.group.random()
        self.s1 = self.group.random()
        self.s2 = self.group.random()
        self.d = self.group.random()

        a = self.g ** self.u

        b1 = (self.g ** self.s1) * (z1 ** self.d)
        b2 = (self.h ** self.s2) * (z2 ** self.d)

        return {'rnd': rnd, 'a': a, 'b1': b1, 'b2': b2}

    def get_proofs(self, input):
        e = input.get('e')

        c = (e - self.d) % self.q
        r = (self.u - c * self.x) % self.q

        return {'r': r, 'c': c, 'd': self.d, 's1': self.s1, 's2': self.s2}


class BlindSignatureVerifier:
    def __init__(self, pubk: dict):
        self.p = pubk.get('p')
        self.q = pubk.get('q')
        self.g = pubk.get('g')
        self.y = pubk.get('y')
        self.h = pubk.get('h')
        self.z = pubk.get('z')
        self.group = IntegerGroupQ()
        self.group.setparam(p=self.p, q=self.q)

    def verify(self, signature, message):
        zeta = signature.get('zeta')
        zeta1 = signature.get('zeta1')
        rho = signature.get('rho')
        omega = signature.get('omega')
        sigma1 = signature.get('sigma1')
        sigma2 = signature.get('sigma2')
        delta = signature.get('delta')
        mu = signature.get('mu')

        tmp1 = (self.g ** rho) * (self.y ** omega) % self.p
        tmp2 = (self.g ** sigma1) * (zeta1 ** delta) % self.p
        tmp3 = (self.h ** sigma2) * ((zeta / zeta1) ** delta) % self.p
        tmp4 = (self.z ** mu) * (zeta ** delta) % self.p

        p1 = (omega + delta) % self.q
        p2 = integer(hash_int([zeta, zeta1, tmp1, tmp2, tmp3, tmp4, message])) % self.q

        return p1 == p2
