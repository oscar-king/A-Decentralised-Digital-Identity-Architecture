from Crypto import Random as rd
from service.models import User
from service import db


def request_handler():
    # Generate cryptographically secure random number
    y = str(rd.get_random_bytes(256).hex())

    # Check if y already exists, should be very unlikely. If true generate new number until unique
    check = User.query.get(y)
    while check:
        y = str(rd.get_random_bytes(256).hex())
        check = User.query.get(y)

    # Add the generated uuid to the db
    new_user = User(y=y)
    new_user.save_to_db()

    return y


def response_handler(response):
    pass