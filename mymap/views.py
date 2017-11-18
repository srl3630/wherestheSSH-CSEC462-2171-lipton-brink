import datetime
import decimal
import json

from django.db import connection
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render
from django.views import View

from .forms import DateForm


# Create your views here.

#render main page
class mymapjson(View):
    def get(self, request):
        return render(request, 'index.html', context={'form': DateForm})


#encode logs in json format, mostly to remove sql formatting
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, datetime.time):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)


def myquery(request):
    if request.method == "POST":
        try:
            #grab start and end date
            startdate = request.POST.get('startdate')
            enddate = request.POST.get('enddate')
            #To avoid sql attacks, attempt to parse dates, to make sure they are valid
            datetime.datetime.strptime(startdate, '%Y-%m-%d')
            datetime.datetime.strptime(enddate, '%Y-%m-%d')
            with connection.cursor() as cursor:
                #grab logs between specified dates
                cursor.execute("SELECT * FROM logs WHERE date >= %s AND date <= %s", [startdate, enddate])
                #grab results
                data = dictfetchall(cursor)
                #parse to json string from sql
                data = json.dumps(data, cls=MyEncoder)
                #load json string to json
                data = json.loads(data)
                #parse json to amcharts readable images
                data = makejson(data)
            return JsonResponse(data)
        except:
            return HttpResponseNotFound('error message')
    else:
        print('nothing is happening')


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def makejson(myjson):
    #set dictionary format
    finaljson = {'Authvno': [], 'Heat': {}, 'IPAuth': [], 'NOIPAuth': []}
    tempcount = 0
    states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS',
              'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV',
              'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
    #make heatmap from log data
    while tempcount < 50:
        #add state and grab state heat
        finaljson['Heat'][states[tempcount]] = 0
        tempcount += 1
    for i in myjson:
        #check if city exists in data yet
        cityexists = False
        for pos in finaljson['Authvno']:
            if i['city'] == pos["title"]:
                cityexists = True
        #if city doesn't exist creat image object for city
        if cityexists == False:
            tempdict = {'title': i['city'],
                        'latitude': i['lat'],
                        'longitude': i['long'],
                        "width": 90,
                        "height": 90,
                        "pie": {
                            "type": "pie",
                            "pullOutRadius": 0,
                            "labelRadius": 0,
                            "dataProvider": [{
                                "category": "Auth",
                                "value": 0
                            }, {
                                "category": "No Auth",
                                "value": 0
                            }],
                            "labelText": "",
                            "valueField": "value",
                            "titleField": "category"
                        }
                        }
            finaljson['Authvno'].append(tempdict)
        #go to city and add value to auth or no auht based on value
        for pos in finaljson['Authvno']:
            if i['city'] == pos["title"]:
                if i['auth']:
                    pos['pie']['dataProvider'][0]['value'] += 1
                else:
                    pos['pie']['dataProvider'][1]['value'] += 1
        #add to heat based on city
        for key in finaljson['Heat']:
            if i['state'] == key:
                finaljson['Heat'][key] += 1
        cityexists = False
        #add to ipauth
        if i['auth']:
            for pos in finaljson['IPAuth']:
                #check if city exists
                if i["city"] == pos["title"]:
                    cityexists = True
                    ipexists = False
                    for nexpos in pos['pie']['dataProvider']:
                        if i['ip'] == nexpos['category']:
                            #if ipexists increment it
                            nexpos['value'] += 1
                            ipexists = True
                            break
                    #if ip doesn't exist, make an object for it
                    if ipexists == False:
                        newip = {"category": i['ip'], "value": 1}
                        pos['pie']['dataProvider'].append(newip)
                    break
            #add city object if it doesn't exist
            if cityexists == False:
                tempdict = {'title': i['city'],
                            'latitude': i['lat'],
                            'longitude': i['long'],
                            "width": 90,
                            "height": 90,
                            "pie": {
                                "type": "pie",
                                "pullOutRadius": 0,
                                "labelRadius": 0,
                                "dataProvider": [],
                                "labelText": "",
                                "valueField": "value",
                                "titleField": "category"
                            }
                            }
                finaljson['IPAuth'].append(tempdict)
                ipexists = False
                #add ip if doesn't exist then increment value if does
                for pos in finaljson['IPAuth'][-1]['pie']['dataProvider']:
                    if i['ip'] == pos['category']:
                        ipexists = True
                if ipexists == False:
                    newip = {"category": i['ip'], "value": 1}
                    finaljson['IPAuth'][-1]['pie']['dataProvider'].append(newip)
                else:
                    finaljson['IPAuth'][-1]['pie']['dataProvider']['value'] += 1
        else:
            #else it is not authorized so add to NOIPAUTH
            #performs actions similar to IPAUTH
            for pos in finaljson['NOIPAuth']:
                if i["city"] == pos["title"]:
                    cityexists = True
                    ipexists = False
                    for nexpos in pos['pie']['dataProvider']:
                        if i['ip'] == nexpos['category']:
                            nexpos['value'] += 1
                            ipexists = True
                            break
                    if ipexists == False:
                        newip = {"category": i['ip'], "value": 1}
                        pos['pie']['dataProvider'].append(newip)
                    break

            if cityexists == False:
                tempdict = {'title': i['city'],
                            'latitude': i['lat'],
                            'longitude': i['long'],
                            "width": 90,
                            "height": 90,
                            "pie": {
                                "type": "pie",
                                "pullOutRadius": 0,
                                "labelRadius": 0,
                                "dataProvider": [],
                                "labelText": "",
                                "valueField": "value",
                                "titleField": "category"
                            }
                            }
                finaljson['NOIPAuth'].append(tempdict)
                ipexists = False
                for pos in finaljson['NOIPAuth'][-1]['pie']['dataProvider']:
                    if i['ip'] == pos['category']:
                        ipexists = True
                if ipexists == False:
                    newip = {"category": i['ip'], "value": 1}
                    finaljson['NOIPAuth'][-1]['pie']['dataProvider'].append(newip)
                else:
                    finaljson['NOIPAuth'][-1]['pie']['dataProvider']['value'] += 1
    return finaljson



