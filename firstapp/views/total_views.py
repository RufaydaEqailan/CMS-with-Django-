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
mycollection_users=db.users


@csrf_exempt
def show_user_carts_price(req):
    """user carts price"""
    total_price = 0
    total_sum=0
    try:
        req_body = json.loads(req.body)
        user_id = req_body['id']
        if user_id == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'Missing parameter or The Status or the value you typing is not correct..  '}))
    try:
        user_id = ObjectId(user_id)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'{user_id} is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string'}))
    try:
        user = mycollection_users.find_one({"_id": user_id})
        if user:
            carts = user["users_carts"]
            for cart_id in carts:
                cart_id=ObjectId(cart_id)
                try:
                    cart = mycollection_carts.find_one({'_id': cart_id})
                    if cart:
                        query = {"_id": cart_id}
                        products = cart["cart_products"]
                        for product in products:
                            total_price += int(product['prodcts_price'])
                        query_update = {"$set": {"cart_total_price": total_price}}
                        update_cart = mycollection_carts.update_one(query, query_update)
                        if update_cart.matched_count > 0:
                            x=1
                            total_sum+=total_price
                    else:
                        return HttpResponseBadRequest(JsonResponse({'msg': f'The cart with this ID {cart_id} is not exiest.'}))
                except:
                    return HttpResponse(JsonResponse({'msg': 'we have troubles now!'}))
            else:
                return JsonResponse({'msg': f' The total price for all user carts is  : {total_sum }' })
        else:
            return HttpResponseBadRequest(JsonResponse({'msg': f'The user with this ID {user_id} is not exiest.'}))
    except:
        return HttpResponseServerError({'msg': 'We are having troubles now.'})

@csrf_exempt
def get_total_revenu_by_year(req):
    """Get total year sales from carts"""
    try:
        req_body = json.loads(req.body)
        year = req_body['year']
        if year == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'Missing parameter or The Status or the value you typing is not correct..  '}))
    try:
        year = int(year)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'{year}  This year is not in the right format 0000 four digits.. try again'}))
    start_date = datetime.datetime(year, 1, 1)
    end_date = datetime.datetime(year, 12, 31)
    query = {
        "cart_status": "paid",
        "cart_paid_date": {"$gte": start_date, "$lte": end_date}
    }
    total_revenu = 0
    paid_carts = mycollection_carts.find(query)
    paid_carts = list(paid_carts)
    if paid_carts:
        for cart in paid_carts:
            total_revenu += cart["cart_total_price"]
        return JsonResponse({'msg': f"Total revenue for {year} is {total_revenu} "})
    else:
        return HttpResponseBadRequest(JsonResponse({'msg': f'There is no paid carts in this year...try with another year.'}))


@csrf_exempt
def search_by_location(req):
    """Find carts based on Location"""
    try:
        req_body = json.loads(req.body)
        cat_name = req_body['city']
        cat_value = req_body['distance']
        cat_total=req_body['total']
        if cat_name == "":
            raise ValueError
        if cat_value == "":
            raise ValueError
        if cat_total == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'Missing paramter..  '}))
    try:
        cat_value = int(cat_value)
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
        cart_list = []
        users = []
        users_info = []
        total_near_price = 0
        for cart in carts:
            if cart["_id"] not in carts:
                cart_dic = {'cartID': str(cart["_id"]),
                            'status': cart['cart_status'],
                            'total price': cart['cart_total_price'],
                            'discount': cart['cart_discount'], }

                cart_list.append(cart_dic)
                total_near_price += cart["cart_total_price"]
                location = f'{cart["cart_location"][0]},{cart["cart_location"][1]}'
                geoLoc = Nominatim(user_agent="GetLoc")
                sleep(1)
                locname = geoLoc.reverse(location)
            
                query_user = {"users_carts": {"$in": [cart["_id"]]}}
                all_user_id = mycollection_users.find(query_user)
                for user_id in all_user_id:
                    if user_id["_id"] not in users:
                        user_dic = {
                            'user ID': str(user_id['_id']),
                            'user name': str(user_id['users_name']),
                            'user email': str(user_id['users_email']),
                        }
                        users.append(user_dic)
        if cat_total=="users":
            return JsonResponse({f'Total amount of users buying in these  carts near {locname.address } Location are ': len(users) })
        elif cat_total == "users_info":
            return JsonResponse({f'Information of users buying in these  carts near {locname.address } Location are ': users})
        elif cat_total=="total_price":
            return JsonResponse({f'Total carts value for the  carts near {locname.address } Location are ':f'{total_near_price} sek'})
        elif cat_total=="carts_status":
           return JsonResponse({f'carts near {locname.address } Location are ': cart_list})
        else:
            return JsonResponse({f'Total amount of users buying in these  carts near {locname.address } Location are ': len(cart_list)})

