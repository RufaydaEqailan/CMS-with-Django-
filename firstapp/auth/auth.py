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
    try:
        SECRET_KEY = os.getenv('SECRET_KEY')
        decoded_token = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256'])
        expire_token = decoded_token['expireAt']
        current_date = datetime.datetime.utcnow().timestamp()
        if current_date > expire_token:
            return  False,HttpResponseForbidden[{'msg':'Your token is expire'}]
        else:
            exists_token=mycollection_token.find_one({'token':token},{'_id':0})
            try:
                if exists_token:
                    return True
                else:
                    return False,HttpResponseForbidden[{'msg':'Your token is expire'}]
            except:
                return False,HttpResponseForbidden[{'msg':'Your token is expire'}]
    except:
        return False,HttpResponseForbidden[{'msg':'Your token is expire'}]

@csrf_exempt
def validateTokenAdmin(token):
    try:
        SECRET_KEY = os.getenv('SECRET_KEY')
        decoded_token = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256'])
        admin_token = decoded_token['role']
        if admin_token =="admin":
            return  True
        else:
            return False,HttpResponseForbidden[{'msg':'You are not admin'}]
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
            else:
                return HttpResponseForbidden({'msg':'You are not login'})
        except:
            return HttpResponseForbidden({'msg':'You are currently not login'})
    return decorated_fun
    

@csrf_exempt 
def is_admin(f):
    def decorated_fun(req):
        try:
            token=""
            token=req.headers["Authorization"]
            token=token.replace("Bearer ","")
            userAuthenticated=validateTokenAdmin(token)
            if userAuthenticated:
                 return f(req)
            else:
                return HttpResponseForbidden({'msg':'You are not admin'})
        except:
            return HttpResponseForbidden({'msg':'You are currently not login as admin'})
    return decorated_fun
    