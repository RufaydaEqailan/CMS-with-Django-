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
from ..models import product_validator
from cerberus import Validator


db = dbconfig.getDB()  
mycollection_products = db.product

@csrf_exempt 
def delete_one_product(req):
    """Delete product"""
    try:
        req_body=json.loads(req.body)
        cat_value=req_body['id'] 
        if cat_value=="":
            raise ValueError   
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'The id is missing..  '})) 
    try:
        cat_value=ObjectId(cat_value)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string.  '})) 
    try:
        product=mycollection_products.find_one({'_id':cat_value},{'_id':0})
        if product:
            products=mycollection_products.find_one_and_delete({"_id":cat_value},{"_id":0})
            if products:
                return JsonResponse({'msg':f'The product with this ID {cat_value} is delete successfully.'})
            else:
                return HttpResponseBadRequest(JsonResponse({'msg':f'The product with this ID {cat_value} is not delete successfully.'}))
        else:
            return HttpResponse(JsonResponse({'msg':'this product is not exist'}))
    except:    
        return HttpResponse(JsonResponse({'msg':'we have troubles now'}))
    
@csrf_exempt 
def modify_master_category(req):
    """modify_master_category"""
    try:
        req_body=json.loads(req.body)
        product_id=req_body['id'] 
        cat_name=req_body['Category']
        cat_value=req_body['Value']
        if product_id=="" or cat_name=="" or cat_value=="":
            raise ValueError   
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'There is parameter is  missing..  '})) 
    try:
        product_id=ObjectId(product_id)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string.  '})) 
    
    if cat_name=="price" or cat_name=="year":
        try:  
            cat_value=int(cat_value)
        except:
            return HttpResponseBadRequest(JsonResponse({'msg': f'The {cat_name} must be integer.  '}))  
    elif cat_value=="old_products":
        try:
            cat_value=bool(cat_value)
        except:
            return HttpResponseBadRequest(JsonResponse({'msg': f'The {cat_name} must be boolean.  '}))  
    else:
        try:
            cat_value=str(cat_value)
        except:
            return HttpResponseBadRequest(JsonResponse({'msg': f'The {cat_name} must be string.  '}))  

    try:
        product=mycollection_products.find_one({'_id':product_id},{'_id':0})
        if  product:
            query={"_id":product_id}    
            newvalues={ "$set": { cat_name: cat_value } }                        
            products=mycollection_products.update_one(query,newvalues) 
            if products.matched_count>0:     
                return JsonResponse({'msg':f' The new value : {cat_value } for a filed : {cat_name} is updated successfully")'})
            else:
                return HttpResponseBadRequest(JsonResponse({'msg':"\nThere is something wrong  happend... Try again later"}))   
        else:
            return  HttpResponseBadRequest(JsonResponse({'msg':f'The product with this ID {product_id} is not exiest.'}))
    except:
           return HttpResponse(JsonResponse({'msg':'we have troubles now'}))
