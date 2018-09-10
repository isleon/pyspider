from pyspider.scheduler.token_bucket import Bucket

bucket = Bucket(rate=3.0, burst=3.0)

b = bucket.get()
print(b)
