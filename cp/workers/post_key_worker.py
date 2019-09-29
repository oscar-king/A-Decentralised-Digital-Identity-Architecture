import json
from datetime import datetime

from redis import Redis
from rq_scheduler import Scheduler

from cp.utils import ledger_utils
from crypto_utils import signatures


class PostKeyWorker:
    rd = Redis()
    scheduler = Scheduler(connection=rd)
    interval = None

    def __init__(self, interval):
        PostKeyWorker.interval = interval

    def __add_to_redis__(self, obj_id, obj):
        # We need the json string because redis doesnt accept random objects
        json_obj = json.dumps(obj)

        # Adds the keys that need to be published to the redis database
        self.rd.set(str(obj_id), str(json_obj))

    def __retrieve_from_redis__(self, obj_id):
        data = self.rd.get(str(obj_id))
        return json.loads(data, encoding='utf-8')

    # def publish_certificate(self, key_id):
    #     # Get keys from redis, pop the first from the list, then save the remainder
    #     keys = self.__retrieve_from_redis__(key_id)
    #     if keys:
    #         key = keys.pop(0)
    #
    #         signer = signatures.Signature()  # Going to have to add s_k and p_k later
    #         sig = signer.sign_message(key)  # Need to add s_k
    #
    #         # This publishes it on the utils (still needs to be implemented)
    #         ledger_utils.publish_pool(sig)
    #         if keys:
    #             self.__add_to_redis__(key_id, keys)
    #         else:
    #             self.rd.delete(key_id)

    # def schedule_key_publishing(self, keyset_id, keys, start_time=None):
    #     self.__add_to_redis__(keyset_id, keys)
    #     time = datetime.utcnow()
    #
    #     if start_time is not None:
    #         time = start_time
    #
    #     self.scheduler.schedule(
    #         id=keyset_id,
    #         scheduled_time=time,
    #         func=self.publish_certificate,
    #         args=[keyset_id],
    #         interval=self.interval,
    #         repeat=len(keys)
    #     )
