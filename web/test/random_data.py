import responses
import random
import time

# temp, light, pir
last_vals = [23.4, 0.8, 0]

def random_val():
    global last_vals
    last_vals = [
        max(5, min(40, last_vals[0] + random.gauss(0,2))),
        max(0, min(1,  last_vals[1] + random.gauss(0,.03))),
        int(round(max(0,min(1,random.gauss(last_vals[2],.4)))))]
        
    fmt = '%0.2f %0.2f %d' % tuple(last_vals)
    print fmt
    return fmt

while 1:
    responses.readings_data(random_val())
    time.sleep(2)
