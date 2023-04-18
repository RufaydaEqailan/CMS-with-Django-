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
from ..auth .auth import logged_in


db = dbconfig.getDB()  
mycollection_users = db.users

@csrf_exempt
def set_old_users(req):
    """Set an status 'terminated' for all users accounts where Online < some value"""
    try:
        req_body = json.loads(req.body)
        online_value=req_body['date']
        if len(online_value)!=10:
            raise ValueError
        if online_value=="":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'The date you enter is (Less\More) 10 Digit - YYY MM-DD..  '}))  
    
    if len(online_value)==10:
        try:
            year=online_value[:4]
            month=online_value[5:7]
            day=online_value[8:]
            online_value=datetime.datetime(int(year),int(month),int(day))
        except:
            return HttpResponseBadRequest(JsonResponse({'msg':"Wrong format (YYYY-MM-DD)"}))
    else:
        return HttpResponseBadRequest(JsonResponse({'msg': 'The date you enter is (Less\More) 10 Digit - .  '}))      
     
    try:
        myquery = { "users_online":{ "$lt":online_value  } }
        newvalues = { "$set": { "users_status": "terminated" } }
        result=mycollection_users.update_many(myquery, newvalues)
        if result.matched_count>0:
            return JsonResponse({'msg':f'The new status :terminated for all users who has online date less than  : {result.matched_count}  are updated successfully'})    
        else:
            return JsonResponse({'msg':f'{result.matched_count}  are updated not  successfully'})    
    except:
            return HttpResponseServerError(JsonResponse({'msg': 'we are having troubles now.'}))
    
@csrf_exempt 
def search_by_value(req):
    """search parameter value user """
    try:
        req_body=json.loads(req.body)
        cat_name=req_body['Category']
        cat_value=req_body['value']  
        if cat_name=="":
            raise ValueError
        if cat_value=="":
            raise ValueError    
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'The Category or the value you typing is not correct..  '}))  
    try:
        if cat_name.lower()=="carts":
            users=mycollection_users.find({'users_carts':{"$in": [ObjectId(cat_value)]}}).limit(10)
            users=list(users)
            if users:
                cart_list=[]
                user_list=[]
                for user in users:
                    for cart in user['users_carts']:
                        cart=str(cart)
                        cart_list.append(cart) 
                    else:
                        user['users_carts']=cart_list
                        cart_list=[]
                        user_dic={
                            'user ID':str(user['_id']),
                            'email': user['users_email'],
                            'carts': user['users_carts']
                        }
                        user_list.append(user_dic)    
                return JsonResponse({'msg':user_list})
            else:
                return HttpResponseBadRequest(JsonResponse({'msg':'There re no users have this cart'} ))  
  
        elif cat_name.lower()=="users_online" or cat_name.lower()=="users_regiterd_at":
            if len(cat_value)==10:
                try:
                    year=cat_value[:4]
                    month=cat_value[5:7]
                    day=cat_value[8:]
                    cat_value=datetime.datetime(int(year),int(month),int(day))
                except:
                    return HttpResponseBadRequest(JsonResponse({'msg':"Wrong format (YYYY-MM-DD)"}))
            else:
                return HttpResponseBadRequest(JsonResponse({'msg': 'The date you enter is (Less\More) 10 Digit - .  '}))                             
            users=mycollection_users.find({f'{cat_name}':cat_value}) 
            if users:
                users=list(users)
                if users:
                        users_list=[]
                        for user in users:
                            user_dic={
                            "id":str(user['_id']),
                            "name":user['users_name'],
                            cat_name:cat_value
                            }
                            users_list.append(user_dic)
                        return JsonResponse({'msg':users_list})
                else:
                    return HttpResponseBadRequest(JsonResponse({'msg':'There re no users'} ))  

        elif cat_name.lower()=="email":
            try:
                email_pattern="([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
                if re.search(email_pattern, cat_value)==None:
                    raise ValueError
            except:
                return HttpResponseBadRequest(JsonResponse({'msg':"Not valid email formate , must be like this formate: name.surname@gmail.com"}))
       
            users=mycollection_users.find({'users_email':cat_value}) 
            users=list(users)
            if users:
                    users_list=[]
                    for user in users:
                        user_dic={
                        "id":str(user['_id']),
                        "name":user['users_name'],
                        cat_name:cat_value
                        }
                        users_list.append(user_dic)
                    return JsonResponse({'msg':users_list})
            else:
                return HttpResponseBadRequest(JsonResponse({'msg':'There re no users have this email'} ))  

        elif cat_name.lower()=="payment":
            available_methods=["VISA","PayPal","Master"]
            if cat_value in available_methods:
                query = {"users_payment_methods": {"$in": [cat_value]}}
                users=mycollection_users.find(query)
                users=list(users)
                if users:
                    payment_list=[]
                    user_list=[]
                    for user in users:
                        for payment in user['users_payment_methods']:
                            payment_list.append(payment) 
                        else:
                            user['users_payment_methods']=payment_list
                            payment_list=[]
                            user_dic={
                                'user ID':str(user['_id']),
                                'email': user['users_email'],
                                'payment methods': user['users_payment_methods']
                            }
                            user_list.append(user_dic)    
                    return JsonResponse({'msg':user_list})
                else:   
                    return HttpResponseBadRequest(JsonResponse({'msg':'There re no users have this paymentmethod'} ))  
    
        else:
            users=mycollection_users.find({f'{cat_name}':cat_value}) 
            if users:
                users=list(users)
                if users:
                        users_list=[]
                        for user in users:
                            user_dic={
                            "id":str(user['_id']),
                            "name":user['users_name'],
                            cat_name:cat_value
                            }
                            users_list.append(user_dic)
                        return JsonResponse({'msg':users_list})
                else:
                    return HttpResponseBadRequest(JsonResponse({'msg':'There re no users'} ))  
    except:
        return HttpResponseServerError({'msg':'We are having troubles now.'})

@csrf_exempt        
def delete_user(req):
    """Clear users list"""
    try:
        mycollection_users.drop()
        return JsonResponse({'msg':'collection users is deleted...'})
    except:
        return HttpResponseServerError({'msg':'We are having troubles now.'})
    
@csrf_exempt 
@logged_in
def show_users(req):
    """MY Users LIST"""
    try:   
        users = mycollection_users.find({},{'users_name':1, 'users_email':1, 'users_status':1,'_id':1}).limit(10)
        users=list(users)
        user_list=[]
        for user in users:
            user_dic={
                'user ID':str(user['_id']),
                'name': user['users_name'],
                'email': user['users_email'],
                'status': user['users_status'],
            }
            user_list.append(user_dic)
        return JsonResponse({'msg':user_list})
    except:
        return HttpResponseServerError({'msg':'We are having troubles now.'})
    
@csrf_exempt 
def show_payment_methods(req):
    """show payment methods for users"""
    try:
        users=mycollection_users.find({})
        users=list(users)
        user_list=[]
        for user in users:
            user_dic={
                'user name':user['users_name'],
                'payment methods': user['users_payment_methods']
            }
            user_list.append(user_dic)
        return JsonResponse({'msg':user_list})
    except:
        HttpResponseServerError({'msg':'We are having troubles now.'})

@csrf_exempt 
def add_user(req):
    """Add new user"""
    if req.method=='POST':
        try:
            req_body=json.loads(req.body)
            users_name=req_body['name']
            users_email=req_body['email'] 
            users_password=req_body['password']
            users_status=req_body['status'] 
            users_online=""
            users_carts=[]
            users_payment_methods=req_body['payment']
            users_regiterd_at=""
            users_credit_card=req_body['cridtcard']
        except:
            return HttpResponseBadRequest(JsonResponse({'msg': f'There is parameter missing  '})) 

        newuser={
            'users_name':users_name,
            'users_email':users_email,
            'users_password':users_password,
            'users_status':users_status,
            # 'online':users_online,
            'users_carts':users_carts,
            'users_payment_methods':users_payment_methods,
            'users_regiterd_at':datetime.datetime.now(),
            'users_credit_card':users_credit_card
        }
        uservalidation=user_validator.validate(newuser)
        emailvalidation=email_validator.validate({'users_email':users_email})
        if uservalidation==True:
            if emailvalidation==True:
                try:
                    add_new_user=mycollection_users.insert_one(newuser)
                    if add_new_user.inserted_id:
                        return JsonResponse({'msg':f'user with this {users_name} is added successfully.'})
                except:
                    return HttpResponseServerError({'msg':'We are having troubles now.'})
            else:
                return HttpResponseBadRequest(JsonResponse({'msg':email_validator.errors}))
        else:
            return HttpResponseBadRequest(JsonResponse({'msg':user_validator.errors}))
    else:
        return 
    
