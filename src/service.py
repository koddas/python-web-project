from bottle import route, template, static_file, run, request, response
from random import randint
from datetime import date
import json
import requests

@route('/')
def index():
    return template("index", title = "Swedish namesday insult service");

@route('/static/<part>/<filename>')
def server_static(part, filename):
    ''' This endpoint serves static files '''
    return static_file(filename, 'static/' + part + '/')

@route('/insult')
def server_todays_insult():
    ''' The /insult endpoint. '''
    today = date.today()
    year = str(today.year).zfill(4)
    month = str(today.month).zfill(2)
    day = str(today.day).zfill(2)
    insult = get_insult(get_name(year, month, day))
    
    if request.headers.get('Accept') == "application/json":
        response.set_header("Content-Type", "application/json")
        return json.dumps(insult)
    else:
        return template("insult", title = "Today's insult", insult = insult)
            

@route('/insult/<year>/<month>/<day>')
def server_insult(year, month, day):
    ''' The /insult/year/month/day endpoint. '''
    insult = get_insult(get_name(year, month, day))
    
    if request.headers.get('Accept') == "application/json":
        response.set_header("Content-Type", "application/json")
        return json.dumps(insult)
    else:
        date = year + "-" + month + "-" + day
        return template("insult", title = "Insult at " + date, insult = insult)

def get_name(year, month, day):
    '''
    Fetches today's name from the Svenska Dagar web service. The year variable
    needs to be four digits long, while the month and day variables need to be
    two digits long each. All three are expected to be strings.
    '''
    url = "http://api.dryg.net/dagar/v2/" + year + "/" + month + "/" + day
    r = requests.get(url)
    data = r.json()
    dag = data['dagar'].itervalues().next()
    
    return dag['namnsdag'].pop(0)

def get_insult(name):
    ''' Fetches an insult from the FOAAS web service '''
    url = "http://foaas.herokuapp.com/" + pick_insult() + "/" + name
    headers = { 'Accept': 'application/json' }
    r = requests.get(url, headers = headers)
    data = r.json()
    insult = { 'signed' : name, 'message' : data['message'] }
    
    return insult

def pick_insult():
    ''' Draws an insult at random from the pool of available FOAAS endpoints '''
    endpoints = ["thanks", "fascinating", "because", "bye", "diabetes"]
    
    return endpoints[randint(0, 4)]

run(host='localhost', port=8081)