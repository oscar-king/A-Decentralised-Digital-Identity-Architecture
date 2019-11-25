import random

import pytest

from cp.models.PolicyPoolModel import PolicyPoolModel


class TestPolicyPoolModel:

    def test_hash_util(self):
        d1 = {k: random.getrandbits(20) for k in range(1,101)}
        d2 = {k: random.getrandbits(20) for k in range(1, 51)}
        h1 = PolicyPoolModel.hash_util(d1)
        h2 = PolicyPoolModel.hash_util(d2)

        try:
            assert h1 != h2
        except AssertionError:
            return pytest.fail("Hash of d1 should not equal hash of d2")

        try:
            h3 = PolicyPoolModel.hash_util(d1)
            assert h1 == h3
        except AssertionError:
            return pytest.fail("Hash of d1 should equal hash of d1")
