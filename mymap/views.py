from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.db import connection
from .forms import DateForm
import datetime
import decimal
import json



# Create your views here.


class mymapjson(View):
    def get(self, request):
        return render(request, 'index.html', context={'form': DateForm})

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
        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM logs WHERE date >= %s AND date <= %s",[startdate,enddate])
            data = dictfetchall(cursor)
            data = json.dumps(data, cls=MyEncoder)
            data = json.loads(data)
            enumlist = []
            enumerator = 1
            for i in data:
                enumlist.append(enumerator)
                enumerator += 1
            data = dict(zip(enumlist, data))
        return JsonResponse(data)
    else:
        print('nothing is happening')

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
