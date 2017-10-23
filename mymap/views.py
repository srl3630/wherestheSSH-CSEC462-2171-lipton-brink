from django.shortcuts import render
from django.views import View
from .forms import login_form
# Create your views here.


class mymapjson(View):
    def get(self, request):
        return render(request,'index.html',context={'form' : login_form })
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')