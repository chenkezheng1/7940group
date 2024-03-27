import configparser
config = configparser.ConfigParser()
config.read('config.ini')
import redis 
redis1 = redis.Redis(host=(config['REDIS']['HOST']), 
                         password=(config['REDIS']['PASSWORD']), 
                         port=(config['REDIS']['REDISPORT']))
# Get the value of a specific key
redis1.select(0)
data = redis1.keys()
data_list=redis1.lrange('hiking',0,-1)
redis1.flushdb()
print(data_list)
# for key in data:
#     value = redis1.get(key)
#     print(key, value)
