# from django.shortcuts import render
import json
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.http.response import JsonResponse
import dbconfig
import pdb
import datetime
import re
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId


db = dbconfig.getDB()  
mycollection_carts = db.carts

@csrf_exempt 
def delete_one_cart(req):
    """Delete cart"""
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
        total_price=0
        total_sum=0
        carts=mycollection_carts.find_one_and_delete({"_id":cat_value},{"_id":0})
        if carts:
            query = {"_id": cat_value}
            products = carts["cart_products"]
            for product in products:
                total_price += int(product['prodcts_price'])
            query_update = {"$set": {"cart_total_price": total_price}}
            update_cart = mycollection_carts.update_one(query, query_update)
            if update_cart.matched_count > 0:
                return JsonResponse({'msg':f'The cart with this ID {cat_value} is delete successfully.'})
        else:
                return HttpResponseBadRequest(JsonResponse({'msg':f'The cart with this ID {cat_value} is not delete successfully.'}))
    except:    
        return HttpResponse(JsonResponse({'msg':'we have troubles now'}))
    
@csrf_exempt 
def modify_master_category(req):
    """modify_master_category"""
    try:
        req_body=json.loads(req.body)
        cart_id=req_body['id'] 
        cat_name=req_body['Category']
        cat_value=req_body['Value']
        if cart_id=="" or cat_name=="" or cat_value=="":
            raise ValueError   
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'There is parameter is  missing..  '})) 
    try:
        cart_id=ObjectId(cart_id)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string.  '})) 
    
    if cat_name == "cart_total_price" or cat_name == "cart_discount":
        try:  
            cat_value=int(cat_value)
        except:
            return HttpResponseBadRequest(JsonResponse({'msg': f'The {cat_name} must be integer.  '}))  
    elif cat_name.lower() == "cart_payment_methods":
        # "payment method code goes here"
        payment_list = []
        available_methods = ["VISA", "PayPal", "Master"]
        if cat_value in available_methods:
            payment_list = [cat_value]
            cat_value = payment_list
        else:
            return HttpResponseBadRequest(JsonResponse({'msg': f"The paymentmethod {cat_value} is not in the available payment method list [VISA,PayPal,Master] ."}))
    else:
        try:
            cat_value=str(cat_value)
        except:
            return HttpResponseBadRequest(JsonResponse({'msg': f'The {cat_name} must be string.  '}))  

    try:
        cart=mycollection_carts.find_one({'_id':cart_id},{'_id':0})
        if  cart:
            query={"_id":cart_id}    
            newvalues={ "$set": { cat_name: cat_value } }                        
            carts=mycollection_carts.update_one(query,newvalues) 
            if carts.matched_count>0:     
                return JsonResponse({'msg':f' The new value : {cat_value } for a filed : {cat_name} is updated successfully")'})
            else:
                return HttpResponseBadRequest(JsonResponse({'msg':"\nThere is something wrong  happend... Try again later"}))   
        else:
            return  HttpResponseBadRequest(JsonResponse({'msg':f'The cart with this ID {cart_id} is not exiest.'}))
    except:
           return HttpResponse(JsonResponse({'msg':'we have troubles now'}))


@csrf_exempt
def calculate_cart_total_price(req):
    """Get Total price for the cart"""
    total_price = 0
    try:
        req_body = json.loads(req.body)
        cart_id = req_body['id']
        if cart_id == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'There is parameter is  missing..  '}))
    try:
        cart_id = ObjectId(cart_id)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string.  '}))

    try:
        cart=mycollection_carts.find_one({'_id':cart_id},{'_id':0})
        if  cart:
            query={"_id":cart_id}    
            products = cart["cart_products"]
            for product in products:
                total_price += int(product['prodcts_price'])
                    
            query_update = {"$set": {"cart_total_price": total_price}}
            update_cart = mycollection_carts.update_one(query, query_update)
            if update_cart.matched_count > 0:
                return JsonResponse({'msg': f' The new value : {total_price } for a filed : cart_total_price is updated successfully")'})
            # return JsonResponse({'msg':products})
        else:
            return HttpResponseBadRequest(JsonResponse({'msg': f'The cart with this ID {cart_id} is not exiest.'}))
    except:
        return HttpResponse(JsonResponse({'msg': 'we have troubles now!'}))

        
