#coding:utf8
from flask import Flask, g, abort, session, redirect, url_for, \
     request, render_template, _app_ctx_stack, jsonify
from flaskext import *
import json
import time
from util import *
import random
import util

import logging
from logging.handlers import TimedRotatingFileHandler

errorLogHandler = TimedRotatingFileHandler('errorLog.log', 'd', 1)
errorlogger = logging.getLogger("errorLogger")
errorlogger.addHandler(errorLogHandler)
errorlogger.setLevel(logging.INFO)

app = Flask(__name__)
app.config.from_object("config")
if __debug__:
    print "Warning running in debug mode!!!!!"
else:
    print 'product mode!!!'

@app.route('/login', methods=['POST', 'GET'])
def login():
    #uid = request.form.get("uid", None, type=int)
    res = queryAll('select * from buildings')
    pep = queryAll('select * from people')
    equip = queryAll('select * from equip')
    skill = queryAll('select * from skill')
    goods = queryAll('select * from goods')
    cityData = queryAll('select * from cityData')
    villageReward = queryAll('select * from villageReward')
    return jsonify(dict(build=res, people=pep, equip=equip, skill=skill, goods=goods, cityData=cityData, villageReward=villageReward))
import time
@app.route('/synError', methods=['POST'])
def synError():
    error = request.form.get('error', None, type=str)
    now = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
    if error == None:
        error = ''
    errorlogger.info(str(now)+'\n'+str(error)+'\n'+str(request.form))
    return jsonify(dict(code=1))

@app.route('/getParam', methods=['POST'])
def getParam():
    res = queryAll('select * from param')
    return jsonify(dict(param=res))

@app.route("/signin", methods=['POST'])
def signin():
    username = request.form.get("username", None, type=str)
    user = queryOne("select * from user where username = %s", (username))
    newUser = False
    if user == None:
        uid = insertAndGetId('insert into user (silver, username) values(%s, %s)', (0, username)) 
        newUser = True
        print "uid is", uid, len(util.allBuild), len(util.allRoad), len(util.allPeople)
        for v in util.allBuild:
            batchUpdate("insert into userBuilding(uid, bid, kind, ax, ay, static) values(%s, %s, %s, %s, %s, %s)", (uid, v['bid'], v['id'], v['px'], v['py'], v['static']))
        for v in util.allRoad:
            batchUpdate("insert into userBuilding(uid, bid, kind, ax, ay, static) values(%s, %s, %s, %s, %s, %s)", (uid, v['bid'], v['id'], v['px'], v['py'], v['static']))
        for k in xrange(0, len(util.allPeople)):
            v = util.allPeople[k]
            batchUpdate("insert into userPeople(uid, pid, kind, px, py) values(%s, %s, %s, %s, %s)", (uid, k+1, v['id'], v['px'], v['py']))
        batchFinish()
    else:
        uid = user['uid']

    allB = queryAll('select * from userBuilding where uid = %s', uid)
    allP = queryAll('select * from userPeople where uid = %s', uid)
    return jsonify(dict(uid=uid, newUser=newUser, allB=allB, allP=allP))


if __name__ == '__main__':
    app.run(port=9100, host='0.0.0.0')
