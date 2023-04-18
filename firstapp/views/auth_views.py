# from django.shortcuts import render
import json
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseServerError
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
def login(req):
    """"""
    if req.method=='POST':
        try:
            req_body = json.loads(req.body)
            userEmail=req_body['email']
            userPass=req_body['password']
            if userEmail=="":
                raise ValueError
            if userPass=="":
                raise ValueError
        except:
            return HttpResponseBadRequest(JsonResponse({'msg': f'Missing data, useremail or password...'}))
        userEmail = hashlib.sha256(userEmail.encode()).hexdigest().lower()
        userPass = hashlib.sha256(userPass.encode()).hexdigest().lower()
        query={'users_email':userEmail}
        user=mycollection_users.find_one(query)
        try:
            if user:
                if user['Role']=='admin':
                    if user['users_password']==userPass:
                        SECRET_KEY = os.getenv('SECRET_KEY')
                        try:
                            payload={}
                            payload['email']=userEmail
                            payload['exp']=time.time_ns()+300000
                            payload['iss']=os.getenv('ISSUD_BY')
                            payload['role']=user['Role']
                            token=jwt.encode(payload,SECRET_KEY)
                            return JsonResponse({'Token is ':token})
                        except:
                            return HttpResponseBadRequest(JsonResponse({'msg':'something  is error'}))
                    else:
                       return HttpResponseBadRequest(JsonResponse({'msg':"The password is not correct"})) 
                else:
                    return HttpResponseBadRequest(JsonResponse({'msg':"This user dose not has admin account"}))
            else:
                return HttpResponseBadRequest(JsonResponse({'msg':'There is no users have this email'}))
        except:
            return HttpResponseServerError({'msg':'We are having troubles now.'})
    else:
        return 
 


def logout():
    """"""


@csrf_exempt
def register(req):
    """rigister new user"""
    if req.method == 'POST':
        try:
            req_body = json.loads(req.body)
            users_name = req_body['name']
            users_email = req_body['email']
            users_password = req_body['password']
            users_status = ""
            users_online = ""
            users_carts = []
            users_payment_methods = []
            users_regiterd_at = ""
            users_credit_card = 0
        except:
            return HttpResponseBadRequest(JsonResponse({'msg': f'There is parameter missing  '}))
        newuser = {
            'users_name': users_name,
            'users_email': users_email,
            'users_password': users_password,
            'users_status': users_status,
            'online':users_online,
            'users_carts': users_carts,
            'users_payment_methods': users_payment_methods,
            'users_regiterd_at': datetime.datetime.now(),
            'users_credit_card': users_credit_card
        }
        uservalidation = user_validator.validate(newuser)
        emailvalidation = email_validator.validate({'users_email': users_email})
        if uservalidation == True:
            if emailvalidation == True:
                email = hashlib.sha256(users_email.encode()).hexdigest()
                password = hashlib.sha256(users_password.encode()).hexdigest() 
                try:
                    exist_user=mycollection_users.find_one({'users_email':email})
                    try:
                        if exist_user:
                            return HttpResponseBadRequest(JsonResponse({'msg': f'This email {users_email} is already exist.'}))
                        else:
                            newuser['users_email']= email
                            newuser['users_password']= password
                            add_new_user = mycollection_users.insert_one(newuser)
                            if add_new_user.inserted_id:
                                return JsonResponse({'msg': f'user with this {users_email} is added successfully.'})
                    except:
                         return JsonResponse({'msg': f'user with this {exist_user} is not found.'})
                except:
                    return HttpResponseServerError({'msg': 'We are having troubles now.'})
                return  JsonResponse({'msg':users_email})
            else:
                 return HttpResponseBadRequest(JsonResponse({'msg': email_validator.errors}))
        else:
            return HttpResponseBadRequest(JsonResponse({'msg': user_validator.errors})) 
    else:
        return HttpResponseServerError(JsonResponse({'msg': 'We are having troubles now.'}))