#coding:utf8
from flask import Flask, g, abort, session, redirect, url_for, \
     request, render_template, _app_ctx_stack, jsonify
from flaskext import *
import json
import time
from util import *
import random
import util
from util import getServer
import config
import MySQLdb

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
#test 
print json.dumps([1, 2, 3])

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
        uid = insertAndGetId('insert into user (silver, username, gold, inSell, ownTech, ownBuild) values(%s,  %s, %s, %s, %s, %s)', (600, username, 1000000, json.dumps({'food':True, 'wood':True, 'stone':True}), json.dumps({'sword':0,'spear':0,'magic':0,'bow':0, 'armour':0,'ninja':0}), json.dumps([1,2,15,4]))) 
        batchUpdate('insert into userTableData(uid) values(%s)', uid)
        batchUpdate('insert into userBattleData (uid, catData) values(%s, %s)', (uid, json.dumps(None)))

        user = queryOne('select * from user where uid = %s', uid)
        newUser = True
        print "uid is", uid, len(util.allBuild), len(util.allRoad), len(util.allPeople)
        for v in util.allBuild:
            batchUpdate("insert into userBuilding(uid, bid, kind, ax, ay, static, goodsKind) values(%s, %s, %s, %s, %s, %s, %s)", (uid, v['bid'], v['id'], v['px'], v['py'], v['static'], v.get('goodsKind', 0)))
        for v in util.allRoad:
            batchUpdate("insert into userBuilding(uid, bid, kind, ax, ay, static) values(%s, %s, %s, %s, %s, %s)", (uid, v['bid'], v['id'], v['px'], v['py'], v['static']))
        for k in xrange(0, len(util.allPeople)):
            v = util.allPeople[k]
            batchUpdate("insert into userPeople(uid, pid, kind, px, py) values(%s, %s, %s, %s, %s)", (uid, k+1, v['id'], v['px'], v['py']))

        #batchUpdate('insert userResearch(uid, researchGoods, ownGoods) values(%s, %s, %s)', (uid, json.dumps([[0, 11]]), json.dumps([[0, 2], [0, 3]])))
        rserver = getServer()
        rserver.set('researchGoods.'+str(uid), json.dumps([[0, 11]]))
        rserver.set('ownGoods.'+str(uid), json.dumps([[0,2],[0,3]]))

        batchFinish()

    else:
        uid = user['uid']


    allB = queryAll('select * from userBuilding where uid = %s', uid)
    allP = queryAll('select * from userPeople where uid = %s', uid)
    #researchData = queryOne('select * from userResearch where uid = %s', uid)
    rserver = getServer()
    rg = rserver.get('researchGoods.'+str(uid))
    og = rserver.get('ownGoods.'+str(uid))
    researchData = {'researchGoods':rg, 'ownGoods':og}

    tableData = queryOne('select * from userTableData where uid = %s', uid)
    tableData.pop('uid')
    catData = queryOne('select catData from userBattleData where uid = %s', uid)
    user['catData'] = catData['catData']
    holdNum = queryAll('select eid, num from userHoldEquip where uid = %s', params=uid, cursorKind=MySQLdb.cursors.Cursor)
    tableData['holdNum'] = holdNum
    return jsonify(dict(uid=uid, newUser=newUser, allB=allB, allP=allP, researchData=researchData, user=user, tableData=tableData))

@app.route('/saveGame', methods=['POST'])
def saveGame():
    if config.DEBUG:
        print 'saveSize', len(json.dumps(request.form))
        print json.dumps(request.form)
    uid = request.form.get('uid', None, type=int)
    allBuild = json.loads(request.form.get('allBuild', None, type=str))
    allRoad = json.loads(request.form.get('allRoad', None, type=str))
    allSellBuild = json.loads(request.form.get('allSellBuild', None, type=str))
    allPeople = json.loads(request.form.get('allPeople', None, type=str))
    dirParams = json.loads(request.form.get('dirParams', None, type=str))
    indirParams = json.loads(request.form.get('indirParams', None, type=str))
    holdNum = json.loads(request.form.get('holdNum', None, type=str))
    
    #table updateEquipNum
    for k in holdNum:
        batchUpdate('insert into userHoldEquip(uid, eid, num) values(%s, %s, %s) on duplicate key set num = values(num) ', (uid, holdNum[k][0], holdNum[k][1]))
    

    for k in allBuild:
        batchUpdate("insert into userBuilding(uid, bid, ax, ay, goodsKind, workNum, lifeStage, dir, kind)values(%s, %s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update ax=values(ax), ay=values(ay), goodsKind=values(goodsKind), workNum=values(workNum), lifeStage=values(lifeStage), dir=values(dir), kind=values(kind) ", (uid, k[0], k[1], k[2], k[3], k[4], k[5], k[6], k[7]))
    for k in allRoad:
        batchUpdate('insert into userBuilding(uid, bid, ax, ay, kind) values(%s, %s, %s, %s, 15) on duplicate key update ax=values(ax), ay=values(ay) ', (uid, k[0], k[1], k[2]))
    
    for k in allSellBuild:
        batchUpdate('delete from userBuilding where uid = %s and bid = %s', (uid, k))

    for k in allPeople:
        batchUpdate('insert into userPeople(uid, pid, kind, px, py, hid, health, level, weapon, head, body, spe) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update kind=values(kind), px=values(px), py=values(py), hid=values(hid), health=values(health), level=values(level), weapon=values(weapon), head=values(head), body=values(body), spe=values(spe)', (uid, k[0], k[1], k[2], k[3], k[4], k[5], k[6], k[7], k[8], k[9], k[10]))
    
    setcat = False
    for k in dirParams:
        if k == 'resource':
            batchUpdate('update user set silver = %s , gold = %s where uid = %s', (dirParams[k]['silver'], dirParams[k]['gold'], uid))
        elif k == 'researchData':
            rserver = getServer()
            rd = dirParams[k]
            if rd.get('researchGoods'):
                rserver.set('researchGoods.'+str(uid), json.dumps(rd['researchGoods']))
            if rd.get('ownGoods'):
                rserver.set('ownGoods.'+str(uid), json.dumps(rd['ownGoods']))

            #batchUpdate('update userResearch set researchGoods = %s, ownGoods = %s where uid = %s', (json.dumps(dirParams[k]['researchGoods']), json.dumps(dirParams[k]['ownGoods']), uid))
            inR = dirParams[k].get('inResearch', None)
            if inR == None:
                batchUpdate('update user set inResearch = 0 where uid = %s', (uid))
            else:
                batchUpdate('update user set inResearch = %s where uid = %s', (inR[0]*1000+inR[1], uid))
        elif k == 'soldiers':
            batchUpdate('update user set soldiers = %s where uid = %s', (json.dumps(dirParams[k]), uid))
        elif k == 'inSell':
            batchUpdate('update user set inSell = %s where uid = %s', (json.dumps(dirParams[k]), uid))
        elif k == 'catData':
            batchUpdate('update userBattleData set catData = %s where uid = %s', (json.dumps(dirParams[k]), uid))
            setcat = True
        elif k == 'date':
            batchUpdate('update user set date = %s where uid = %s', (json.dumps(dirParams[k]), uid))
        else:
            if type(dirParams[k]) == int or type(dirParams[k]) == bool:
                batchUpdate('update user set key = %s where uid = %s'.replace('key', k), (dirParams[k], uid))
            else:
                batchUpdate('update user set key = %s where uid = %s'.replace('key', k), (json.dumps(dirParams[k]), uid))
    #if not setcat:
    #    batchUpdate('update user set catData = %s where uid = %s', (json.dumps(None), uid))
    
    for k in indirParams:
        batchUpdate('update userTableData set key = %s where uid = %s'.replace('key', k), (json.dumps(indirParams[k]), uid))

    batchFinish()
    return jsonify(dict(code=1))



if __name__ == '__main__':
    app.run(port=9100, host='0.0.0.0')
