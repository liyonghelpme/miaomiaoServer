#coding:utf8
import time
from flaskext import *
def doGain(uid, gain):
    for k in gain:
        sql = 'update User set %s = %s+%d where uid = %d' % (k, k, gain[k], uid)
        update(sql)

def checkCost(uid, cost):
    user = queryOne('select * from User where uid = %s', (uid))
    for k in cost:
        if user[k] < cost[k]:
            return False
    return True

def doCost(uid, cost):
    for k in cost:
        sql = 'update User set %s = %s - %d where uid = %d' % (k, k, cost[k], uid)
        update(sql)

def getTime():
    return int(time.time())
