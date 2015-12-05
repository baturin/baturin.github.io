from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'wvpoi/index.html')

def tool(request):
    return render(request, 'wvpoi/tool.html')
