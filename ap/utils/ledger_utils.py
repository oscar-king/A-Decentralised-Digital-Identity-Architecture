from flask import json


def get_certs(cp, timestamp):
    data = {
        "cp":cp,
        "timestamp":timestamp
    }
    return json.dumps(data)