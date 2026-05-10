#!/usr/bin/env python3
import os, json, http.client
os.environ.setdefault('DJANGO_SETTINGS_MODULE','user_service.settings')
import django
django.setup()
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

username='apitest'
user, created = User.objects.get_or_create(username=username, defaults={'email':'apitest@example.com'})
if created:
    user.set_password('password')
    user.save()
    print('Created user')
else:
    print('User exists')

refresh = RefreshToken.for_user(user)
access = str(refresh.access_token)
print('access token:', access)

conn = http.client.HTTPConnection('127.0.0.1',8000, timeout=10)
headers = {'Content-Type':'application/json','Authorization':'Bearer '+access}
# Use Cyrillic names to test unicode handling
payload = json.dumps({'first_name':'Тест','last_name':'Юзер'})
conn.request('PATCH','/api/user/profile/settings/', payload, headers)
resp = conn.getresponse()
print('status', resp.status)
body = resp.read().decode()
print('body:', body)
