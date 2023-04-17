# from django.shortcuts import render
import json
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.http.response import JsonResponse
import dbconfig
import pdb
from django.views.decorators.csrf import csrf_exempt

db = dbconfig.getDB()
mycollection = db.users

# Create your views here.

@csrf_exempt
def Set_test_old_users(req):
    try:
        req_body = json.loads(req.body)
        name_value = req_body['name']
        return JsonResponse({'msg': f'{name_value}'})
    except:
        return HttpResponseBadRequest(JsonResponse(
            {'msg': f'You forget some value in the request'}))

@csrf_exempt
def show(req):
    try:
        users = mycollection.find({})
        users = list(users)
        user_list = []
        for user in users:
            user_doc = {
                'name': user['users_name'],
                # Exception Value:Object of type ObjectId is not JSON serializable
                '_id': str(user['_id']),
                'email': user['users_email'],
                'status': user['users_status'],
                'rgisteration at': user['users_regiterd_at']
                # Add more fields as needed
            }
            user_list.append(user_doc)
        return JsonResponse({'users': user_list})

    except:
        return HttpResponseServerError(JsonResponse({'msg': 'we are having troubles now.'}))
