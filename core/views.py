from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
import time, datetime
import pytz


# Create your views here.

def index(request):
    return render(request, 'index.html')
