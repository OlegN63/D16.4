import os
import redis

red = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=11346,
    password=os.getenv('REDIS_PASSWORD')
)