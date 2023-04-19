# from django.shortcuts import render
import json
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.http.response import JsonResponse
import dbconfig
import pdb
import datetime
import re
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId, _encode_datetime
from ..models import user_validator, email_validator
from cerberus import Validator
import jwt
import time
import hashlib
import os
from dotenv import load_dotenv, dotenv_values
config = dotenv_values(".env")
load_dotenv()

db = dbconfig.getDB()  
mycollection_users = db.users
mycollection_token = db.tokens

@csrf_exempt
def validateToken(token):
    # decode_token=jwt.decode(jwt=token)
    # return decode_token
    try:
        SECRET_KEY = os.getenv('SECRET_KEY')
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256'])
        expiration_time = payload['exp']
        current_time = datetime.datetime.utcnow().timestamp()
        if current_time > expiration_time:
            return False
        if (expiration_time - current_time) <= 300: # 300 seconds = 5 minutes
            # expiration time is within 5 minutes
            # you can perform some action here, like sending a warning email
            return True
    except jwt.ExpiredSignatureError:
        return False
    except:
        return False

@csrf_exempt 
def logged_in(f):
    def decorated_fun(req):
        try:
            token=""
            token=req.headers["Authorization"]
            token=token.replace("Bearer ","")
            userAuthenticated=validateToken(token)
            if userAuthenticated:
                 return f(req)
                # return JsonResponse({'msg':userAuthenticated})
            else:
                return HttpResponseForbidden({'msg':'You are not login'})
        except:
            return HttpResponseForbidden({'msg':'You are currently not login'})
    return decorated_fun
    