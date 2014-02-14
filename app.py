#coding:utf8
from flask import Flask, g, abort, session, redirect, url_for, \
     request, render_template, _app_ctx_stack, jsonify
from flaskext import *
import json
import time
from util import *
import random
import util

app = Flask(__name__)
app.config.from_object("config")

@app.route('/login', methods=['POST', 'GET'])
def login():
    #uid = request.form.get("uid", None, type=int)
    res = queryAll('select * from buildings')
    pep = queryAll('select * from people')
    equip = queryAll('select * from equip')
    skill = queryAll('select * from skill')
    goods = queryAll('select * from goods')
    return jsonify(dict(build=res, people=pep, equip=equip, skill=skill, goods=goods))



if __name__ == '__main__':
    app.run(port=9900, host='0.0.0.0')
