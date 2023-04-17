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
from geopy.geocoders import Nominatim
from time import sleep
from pymongo import DESCENDING
from pymongo.operations import IndexModel

db = dbconfig.getDB()
mycollection_carts = db.carts


@csrf_exempt
def show_carts(req):
    """MY carts LIST"""
    try:
        carts = mycollection_carts.find({}, {'cart_status': 1, 'cart_total_price': 1,
                                        'cart_discount': 1, 'cart_payment_methods': 1, '_id': 1}).limit(10)
        carts = list(carts)
        cart_list = []
        for cart in carts:
            cart_dic = {
                'cart ID': str(cart['_id']),
                'cart status': cart['cart_status'],
                'cart total price ': cart['cart_total_price'],
                'cart discount': cart['cart_discount'],
                'cart payment methods': cart['cart_payment_methods']                          
            }
            cart_list.append(cart_dic)
        return JsonResponse({'msg': cart_list})
    except:
        return HttpResponseServerError({'msg': 'We are having troubles now.'})


@csrf_exempt
def delete_carts(req):
    """Clear carts list"""
    try:
        mycollection_carts.drop()
        return JsonResponse({'msg': 'collection carts is deleted...'})
    except:
        return HttpResponseServerError({'msg': 'We are having troubles now.'})


@csrf_exempt
def set_old_carts(req):
    """Set an status 'pending to abandon ' for all carts  where date < some value"""
    try:
        req_body = json.loads(req.body)
        online_value=req_body['date']
        if len(online_value)!=10:
            raise ValueError
        if online_value=="":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'Missing parameter or the date you enter is (Less\More) 10 Digit - YYY MM-DD..  '}))  
    
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
        myquery = { "cart_created_at":{ "$lt":online_value  }, "cart_status": "pending" }
        newvalues = { "$set": { "cart_status": "abandon", "cart_abandoned_date":datetime.datetime.now(),"cart_paid_date":"" } }
        cart=mycollection_carts.update_many(myquery, newvalues)
        if cart.matched_count>0:
            return JsonResponse({'msg':f'The new status :abandon for all carts who has created date less than  : {cart.matched_count} carts  are updated successfully'})    
        else:
            return JsonResponse({'msg':f'{cart.matched_count} carts  are updated   successfully'})    
    except:
            return HttpResponseServerError(JsonResponse({'msg': 'we are having troubles now.'}))
    

@csrf_exempt
def show_by_status(req):
    """search status for carts"""
    try:
        req_body = json.loads(req.body)
        cat_value = req_body['Status']
        if cat_value == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'Missing parameter or The Status or the value you typing is not correct..  '}))

    try:
        available_status = ["paid", "abandon", "pending"]
        if cat_value in available_status:
            query = {"cart_status":cat_value}
            carts = mycollection_carts.find(query)
            if carts:
                carts = list(carts)
                carts_list = []
                for cart in carts:
                    products_list = []
                    for products in cart['cart_products']:
                        prod_dic={
                            "product ID": str(products["pro_id"]),
                            "product quantity": products["pro_qua"],
                            "products price": products["prodcts_price"]
                        }
                        products_list.append(prod_dic)
                    else:
                        cart['cart_products'] = products_list
                        products_list = []
                        cart_dic = {
                            "id": str(cart['_id']),
                            "cart total price": cart['cart_total_price'],
                            "cart status": cat_value,
                            "cart products": cart['cart_products']
                        }
                        carts_list.append(cart_dic)
                return JsonResponse({'msg': carts_list})
            else:
                return HttpResponseBadRequest(JsonResponse({'msg': f'There re no carts have this status {cat_value}'}))
        else:
            return HttpResponseBadRequest(JsonResponse({'msg':'This status is wrong [ paid , abandon , pending]'} ))  
    except:
        return HttpResponseServerError({'msg': 'We are having troubles now.'})


@csrf_exempt
def search_by_value(req):
    """search parameter value cart """
    try:
        req_body = json.loads(req.body)
        cat_name = req_body['Category']
        cat_value = req_body['value']
        if cat_name == "":
            raise ValueError
        if cat_value == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'Missing parameter or The Status or the value you typing is not correct..  '}))

    try:
        """sreach by cart_products"""
        if cat_name.lower() == "product":
            carts = mycollection_carts.find(
                {'cart_products.pro_id': {"$in": [ObjectId(cat_value)]}}).limit(10)
            carts = list(carts)
            if carts:
                prod_list = []
                cart_list = []
                for cart in carts:
                    for product in cart['cart_products']:
                        prod_dic={
                            'product ID': str(product['pro_id']),
                            'product quantity': product['pro_qua'],
                            'product price': product['prodcts_price']
                                  }
                        prod_list.append(prod_dic)       
                    else:
                        cart['cart_products'] = prod_list
                        prod_list = []
                        cart_dic = {
                            'cart ID': str(cart['_id']),
                            'status': cart['cart_status'],
                            'total price': cart['cart_total_price'],
                            'discount': cart['cart_discount'],
                        }
                        cart_list.append(cart_dic)
                return JsonResponse({'msg': cart_list})
            else:
                return HttpResponseBadRequest(JsonResponse({'msg': 'There re no carts have this product'}))
        elif cat_name.lower() == "discount":
            try:
                cat_value=int(cat_value)
            except:
                return HttpResponseBadRequest(JsonResponse({'msg': 'Discount must be integer'}))
            carts = mycollection_carts.find({'cart_discount': cat_value}).limit(10)
            carts = list(carts)
            if carts:
                cart_list = []
                for cart in carts:
                    cart_dic = {
                        'cart ID': str(cart['_id']),
                        'status': cart['cart_status'],
                        'total price': cart['cart_total_price'],
                        'discount': cart['cart_discount'],
                    }
                    cart_list.append(cart_dic)
                return JsonResponse({'msg': cart_list})
            else:
                return HttpResponseBadRequest(JsonResponse({'msg': 'There is no carts have this discount'}))
        elif cat_name.lower()=="payment":
            available_methods=["VISA","PayPal","Master"]
            if cat_value in available_methods:
                query = {"cart_payment_methods": {"$in": [cat_value]}}
                carts=mycollection_carts.find(query)
                carts=list(carts)
                if carts:
                    payment_list=[]
                    cart_list=[]
                    for cart in carts:
                        for payment in cart['cart_payment_methods']:
                            payment_list.append(payment) 
                        else:
                            cart['cart_payment_methods'] = payment_list
                            payment_list=[]
                            cart_dic={
                                'cart ID': str(cart['_id']),
                                'status': cart['cart_status'],
                                'total price': cart['cart_total_price'],
                                'discount': cart['cart_discount'],
                                'payment methods': cart['cart_payment_methods']
                            }
                            cart_list.append(cart_dic)    
                    return JsonResponse({'msg':cart_list})
                else:   
                    return HttpResponseBadRequest(JsonResponse({'msg':'There re no carts have this paymentmethod'} ))        
            else:
                return HttpResponseBadRequest(JsonResponse({'msg':'There re no carts have this paymentmethod'} ))        
    except:
        return HttpResponseServerError({'msg': 'We are having troubles now.'})


@csrf_exempt
def add_cart(req):
    """Add new cart"""
    # if req.method == 'POST':
    #     try:
    #         req_body = json.loads(req.body)
    #         gender = req_body['gender']
    #         masterCategory = req_body['masterCategory']
    #         subCategory = req_body['subCategory']
    #         articleType = req_body['articleType']
    #         baseColour = req_body['baseColour']
    #         season = req_body['season']
    #         year = req_body['year']
    #         usage = req_body['usage']
    #         cartDisplayName = req_body['cartDisplayName']
    #         price = req_body['price']
    #         filename = req_body['filename']
    #         Link = req_body['Link']

    #     except:
    #         return HttpResponseBadRequest(JsonResponse({'msg': f'There is parameter missing  '}))

    #     newcart = {
    #         'gender': gender,
    #         'masterCategory': masterCategory,
    #         'subCategory': subCategory,
    #         'articleType': articleType,
    #         'baseColour': baseColour,
    #         'season': season,
    #         'year': year,
    #         'usage': usage,
    #         'cartDisplayName': cartDisplayName,
    #         'price': price,
    #         'filename': filename,
    #         'Link': Link,
    #         'usage': usage,
    #         'old_carts': False
    #     }
    #     cartvalidation = cart_validator.validate(newcart)
    #     if cartvalidation == True:
    #         try:
    #             add_new_cart = mycollection_carts.insert_one(newcart)
    #             if add_new_cart.inserted_id:
    #                 return JsonResponse({'msg': f'cart with this {cartDisplayName} is added successfully.'})
    #         except:
    #             return HttpResponseServerError({'msg': 'We are having troubles now.'})
    #     else:
    #         return HttpResponseBadRequest(JsonResponse({'msg': cart_validator.errors}))
    # else:
    #     return HttpResponseServerError({'msg': 'Method should be POST.'})  
 
 
@csrf_exempt
def search_by_location(req):
    """Find carts based on Location"""
    try:
        req_body = json.loads(req.body)
        cat_name = req_body['city']
        cat_value = req_body['distance']
        if cat_name == "":
            raise ValueError
        if cat_value == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'Missing paramter..  '}))
    try:
        cat_value=int(cat_value)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'The distance must be intger..  '}))
    mycollection_carts.create_index([("cart_location", "2dsphere")])
    geoLoc = Nominatim(user_agent="GetLoc")
    location = geoLoc.geocode(cat_name)
    coordinates = [int(location.latitude), int(location.longitude)]
    sleep(1)
    carts = mycollection_carts.aggregate([
        {
            '$geoNear': {
                'near': {'type': "Point", 'coordinates': coordinates},
                'distanceField': "dist.calculated",
                'maxDistance': int(cat_value)*1000,
                'includeLocs': "dist.location",
                'spherical': True   
            }
        }
    ])
    carts = list(carts)
    if carts:
        cart_list=[]
        for cart in carts:
            if cart["_id"] not in carts:
                cart_dic = {'cartID':str(cart["_id"]),
                            'status': cart['cart_status'],
                            'total price': cart['cart_total_price'],
                            'discount': cart['cart_discount'], }
                
                cart_list.append(cart_dic)
                
        location = f'{cart["cart_location"][0]},{cart["cart_location"][1]}'
        geoLoc = Nominatim(user_agent="GetLoc")
        sleep(1)
        locname = geoLoc.reverse(location)
        return JsonResponse({f'carts near {locname.address } Location are ': cart_list})
    else:
        return HttpResponseBadRequest(JsonResponse({'msg': f'There re no cart near {cat_name }'}))
