def publish_certificate(certificate):
    """
    This method will be the method that a Certification Provider can call to publish a certificate to the ledger.
    :param certificate:
    :return:
    """
    print(certificate)


def revoke_key(key):
    """
    This will be the method by which a Certification Provider can revoke a
    specific key with which they will have signed a set of certificates.
    :param key:
    :return:
    """
    pass