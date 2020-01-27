import sys

from Crypto import Random as rd

from ap.models.Session import Session


class Nonce:
    def __init__(self, pubk: int, n=None):
        if n is None:
            self.n = 256
        else:
            self.n = n

        self.y = self.__generate_nonce__()
        self.pubk = pubk

    def __generate_nonce__(self) -> str:
        # Generate cryptographically secure random number
        y = rd.get_random_bytes(self.n).hex()

        # Check if y already exists, should be very unlikely
        check = Session.find(y)
        while check:
            y = rd.get_random_bytes(self.n).hex()
            check = Session.find(y)
        return y

    def save(self) -> bool:
        # Add the generated uuid to the db
        new_user = Session(self.y, self.pubk)

        # Database interaction can throw exceptions
        try:
            new_user.save_to_db()
            return True
        except Exception:
            print("Something went wrong saving the Session information", file=sys.stderr)
            return False
