from django.test import TestCase

# Create your tests here.

import requests

headers = {'content-type': 'application/json, text/javascript, */*; q=0.01',
           'Accept-Encoding': 'gzip, deflate, sdch',
           # 'Cookie': 'Hm_lvt_a23e9746ef9e5704a5a2e6e758c55e21=1465864877,1466490276,1467355183,1468200509; sessionid=llieyme2ytogugmp5uifhofccx00vu24; csrftoken=BfHm8ilFrleMH6F8ZAXOssnprnGgHqSt',
           }
response = requests.delete("http://192.168.30.139:8000/api/jobs/f1547e8a0ba04ca5bc1363dbe2708bdf/", headers=headers)
print response.text
