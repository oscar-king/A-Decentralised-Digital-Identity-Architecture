from crypto import signatures
import uuid
import _sha256


def test_sign_verify():
    """
        Tests that the verify_signature method returns true when given the string which was signed.
        It also tests if the method returns false when given a different string.
    """
    signer = signatures.Signature()

    test_string = uuid.uuid4().hex

    sig = signer.sign_message(test_string)
    result_true = signer.verify_signature(signer.pub_key, sig, test_string)
    result_false = signer.verify_signature(signer.pub_key, sig, "This should be false")

    assert result_true is True
    assert result_false is False


def test_hashing():
    """
        Tests that the output of the Signatures class hashing method produces the expected hex-digest.
        The test compares against inbuilt sha256
    """
    signer = signatures.Signature()

    test_string = uuid.uuid4().hex

    hash_ = signer.hash_str(test_string)
    hash2_ = _sha256.sha256(test_string.encode()).hexdigest()

    assert hash_ == hash2_
