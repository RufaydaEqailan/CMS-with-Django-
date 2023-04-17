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
def show_products(req):
    """MY products LIST"""
    try:   
        products = mycollection_products.find({},{'productDisplayName':1, 'masterCategory':1, 'articleType':1,'price':1,'_id':1}).limit(10)
        products=list(products)
        product_list=[]
        for product in products:
            product_dic={
                'product ID':str(product['_id']),
                'product name': product['productDisplayName'],
                'product catrgory': product['masterCategory'],
                'product price': product['price'],
                'product type': product['articleType'],
            }
            product_list.append(product_dic)
        return JsonResponse({'msg':product_list})
    except:
        return HttpResponseServerError({'msg':'We are having troubles now.'})
    
@csrf_exempt        
def delete_products(req):
    """Clear products list"""
    try:
        mycollection_products.drop()
        return JsonResponse({'msg':'collection products is deleted...'})
    except:
        return HttpResponseServerError({'msg':'We are having troubles now.'})
    
@csrf_exempt
def set_old_products(req):
    """Set an status 'terminated' for all products accounts where Online < some value"""
    try:
        req_body = json.loads(req.body)
        year=req_body['year']
        if year=="":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'Missing parameter .  '}))  
    try:
        year=int(year)
    except:
            return HttpResponseBadRequest(JsonResponse({'msg':"Wrong format (YYYY)"}))
    try:
        myquery = { "year":{ "$lt":year  } }
        newvalues = { "$set": { "old_products": "True"} }
        result=mycollection_products.update_many(myquery, newvalues)
        if result.matched_count>0:
            return JsonResponse({'msg':f'The new status :number of edited products : {result.matched_count}, True for all products who has year less than  : {year}  are updated successfully'})    
        else:
            return JsonResponse({'msg':f'{result.matched_count}  are updated not  successfully'})    
    except:
            return HttpResponseServerError(JsonResponse({'msg': 'we are having troubles now.'}))

@csrf_exempt    
def show_categories_product(req):
    """Show the different products catergories"""
    try:  
        products=mycollection_products.find({})
        master__catergories=[]
        sub_categories=[]
        # master_cate=my_collection.distinct('masterCategory')
        for entry in products:
            if not entry["masterCategory"] in master__catergories:
                master__catergories.append(entry["masterCategory"])
            if not entry["subCategory"] in sub_categories:
                sub_categories.append(entry["subCategory"])
        return JsonResponse({"master categoeries ": master__catergories , "sub categories" : sub_categories})
    except:  
        return HttpResponseServerError({'msg':'We are having troubles now.'})

@csrf_exempt      
def search_by_value(req):
    """search parameter value product """
    try:
        req_body=json.loads(req.body)
        cat_name=req_body['Category']
        cat_value=req_body['value']  
        if cat_name=="" :
            raise ValueError
        if cat_value=="":
            raise ValueError    
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'Missing paramerter..  '}))  
    
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
        products=mycollection_products.find({cat_name:cat_value}) 
        if products:
            products=list(products)
            if products:
                products_list=[]
                for product in products:
                    product_dic={
                    "id":str(product['_id']),
                    "name":product['productDisplayName'],
                    cat_name:cat_value
                    }
                    products_list.append(product_dic)
                return JsonResponse({'msg':products_list})
            else:
                return HttpResponseBadRequest(JsonResponse({'msg':'There re no products'} ))  
    except:
        return HttpResponseServerError({'msg':'We are having troubles now.'})


@csrf_exempt 
def add_product(req):
    """Add new product"""
    if req.method=='POST':
        try:
            req_body=json.loads(req.body)
            gender=req_body['gender']
            masterCategory=req_body['masterCategory'] 
            subCategory=req_body['subCategory']
            articleType=req_body['articleType'] 
            baseColour=req_body['baseColour']
            season=req_body['season']
            year=req_body['year']
            usage=req_body['usage']
            productDisplayName=req_body['productDisplayName']
            price=req_body['price']
            filename=req_body['filename']
            Link=req_body['Link']
           

        except:
            return HttpResponseBadRequest(JsonResponse({'msg': f'There is parameter missing  '})) 

        newproduct={
            'gender':gender,
            'masterCategory':masterCategory,
            'subCategory':subCategory,
            'articleType':articleType,
            'baseColour':baseColour,
            'season':season,
            'year':year,
            'usage':usage,
            'productDisplayName':productDisplayName,
            'price':price,
            'filename':filename,
            'Link':Link,
            'usage':usage,
            'old_products':False  
        }
        productvalidation=product_validator.validate(newproduct)
        if productvalidation==True:
            try:
                add_new_product=mycollection_products.insert_one(newproduct)
                if add_new_product.inserted_id:
                    return JsonResponse({'msg':f'product with this {productDisplayName} is added successfully.'})
            except:
                return HttpResponseServerError({'msg':'We are having troubles now.'})
        else:
            return HttpResponseBadRequest(JsonResponse({'msg':product_validator.errors}))
    else:
        return HttpResponseServerError({'msg':'Method should be POST.'})     