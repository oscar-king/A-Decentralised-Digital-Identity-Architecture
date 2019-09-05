from cp.workers import post_key_worker
import testing.redis


# class TestWorker:
#     rd = None
#
#     @classmethod
#     def setup_class(cls):
#         cls.rd = testing.redis.RedisServer()
#         cls.pkw = post_key_worker.PostKeyWorker(1)
#
#     @classmethod
#     def teardown_class(cls):
#         cls.rd.stop()
#
#     def test_add_retrieve_redis(self):
#         keys = ["hello", "this", "is", "test"]
#         self.pkw.__add_to_redis__(1, keys)
#         res = self.pkw.__retrieve_from_redis__(1)
#         assert keys == res
