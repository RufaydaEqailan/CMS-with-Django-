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

@csrf_exempt
def validateToken(token):
    return True

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
    