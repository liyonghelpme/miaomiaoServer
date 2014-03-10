#coding:utf8
import time
from flaskext import *
import json
import redis
def getServer():
    rsever = redis.Redis()
    return rsever

oldDump = json.dumps

def dumpNew(obj):
    return oldDump(obj, separators=(',', ':'))
json.dumps = dumpNew 

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



mapObj = {}
allBuild = []
allRoad = []
allPeople = []

''''
#tid 计算出 对应的图片编号 生成建筑物返回给客户端
#build2 建筑物 道路 建筑物 斜坡建筑物 树木等建筑物 初始化
#生成图片名称 tid 对应的建筑物类型是什么呢？
def tidToTile(tid, normal, water, gidToTileName):
    #大网格
    for i in xrange(1, len(normal)):
        if tid < normal[i]:
            return 'tile'..tid-normal[i-1]..'.png'
    #最后一个 normal 网格
    if tid < normal[len(normal)-1]+64:
        return 'tile'..tid-normal[len(normal)-1]..'.png'
    
    for i in xrange(1, len(water)):
        if tid < water[i]:
            return 'tile'..(tid-water[i-1]+39)..'.png'


def readMap():
    f = open('big512.json', 'r')
    con = f.read()
    f.close()
    mapObj = json.loads(con)
    layerName = mapObj['layName'] = {}
    layers = mapObj['layers']
    for v in layers:
        layerName[v['name']] = v
    
    width = mapObj['width']
    height = mapObj['height']
    road = layerName['road']
    staticRow = 4
    bid = 1
    for k in xrange(0, len(road['data'])):
        if road['data'][k] != 0:
            tid = road['data'][k]
            w = (k)%width
            h = (k)/width
            static = False
            if w >= width-staticRow:
                static = True
            allBuild.append(dict(id=15, ax=w, ay=h, bid=bid, static=static, tid=tid))
            bid = bid+1
    
    ladder = layerName['ladder']
    for k in xrange(0, len(ladder['data'])):
        if ladder['data'][k] != 0:
            tid = ladder['data'][k]
            w = (k)%width
            h = (k)/width
            static = False
            if w >= width-staticRow:
                static = True
            allBuild.append(dict(id=15, ax=w, ay=h, bid=bid, static=static, ladder=True, tid=tid))

            bid = bid+1
    
    gidToBname = {}
    for k in xrange(0, len(mapObj['tilesets'])):
        

    build2 = layerName['build2']
    for k in xrange(0, len(build2['data'])):
        tid = build2['data'][k]
        if tid != 0:
'''
            
from xml.dom import minidom
def readMap():
    con = minidom.parse('UserDefault.xml')
    build = con.getElementsByTagName('build')[0].firstChild.nodeValue
    bdata = json.loads(build)
    global allBuild
    global allRoad
    global allPeople

    allBuild = bdata
    print "init build num", len(allBuild)
    road = con.getElementsByTagName('road')[0].firstChild.nodeValue
    bdata = json.loads(road)
    allRoad = bdata
    print "init road num", len(allRoad)
    
    people = con.getElementsByTagName('people')[0].firstChild.nodeValue
    bdata = json.loads(people)
    allPeople = bdata
    print "init people num", len(allPeople)

readMap()



        

        


