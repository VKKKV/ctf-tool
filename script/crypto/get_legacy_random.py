import random
import sys

target_time = int(sys.argv[1])
secret = random.Random()
secret.seed(target_time)
print str(secret.random())
