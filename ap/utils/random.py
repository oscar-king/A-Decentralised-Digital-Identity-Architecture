from Crypto import Random as rd
from sqlalchemy.exc import InvalidRequestError

from ap.models import UserNonce


class Nonce:
    def __init__(self, pubk, n=None):
        self.y = self.__generate_nonce__()
        self.pubk = pubk

        if n is None:
            self.n = 256
        else:
            self.n = n

    def __generate_nonce__(self):
        # Generate cryptographically secure random number
        y = str(rd.get_random_bytes(self.n).hex())

        # Check if y already exists, should be very unlikely
        check = UserNonce.query.get(y)
        while check:
            y = str(rd.get_random_bytes(self.n).hex())
            check = UserNonce.query.get(y)
        return y

    def save(self):
        # Add the generated uuid to the db
        new_user = UserNonce(self.y, self.pubk)

        # Database interaction can throw exceptions
        try:
            new_user.save()
            return True
        except InvalidRequestError:
            return False

def response_handler(response):
    pass