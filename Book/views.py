from django.shortcuts import render
from Book.models import Books
from Book.serializer import BooksSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import permissions
from django.db import connection
from Book.models import Books
from Book.permissions import IsOwnerOrReadOnly

from django_redis import get_redis_connection
from django.core.cache import cache

from django.http import HttpResponse,JsonResponse
from asgiref.sync import sync_to_async,async_to_sync
import asyncio
import json
from django.core import serializers

import time#更改一下注释git推送的看看效果

async def index(request):
    return await sync_to_async(HttpResponse)("Hello, async Django!")

async def orm_test(request):
    results=cache.get('all')
    if results==None:
        #start = time.clock()
        results =await sync_to_async(Books.objects.all, thread_sensitive=True)()
        query_list=await sync_to_async(serializers.serialize)('json',results)
        #print('+++++++++++++++++++++++++++++++++')
        #print(type(query_list))
        cache.set("all", query_list, nx=True,timeout=3600)
        #end = time.clock()
        #print('Running time: %s Seconds' % (end - start))
    #response = HttpResponse()
    #response.content = results
        return JsonResponse(query_list,safe=False)
    #print('----------------------------------')
    #print(type(results))
    return JsonResponse(results,safe=False)
    


class BooksViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]
    #start = time.clock()
    all_cache=cache.get('all_cache')
    if all_cache==None:
        all_cache=Books.objects.all()
        #all_cache=sync_to_async(get_all, thread_sensitive=True)
        cache.set("all_cache", all_cache, nx=True,timeout=3600)
    #queryset = Books.objects.all()
    queryset=all_cache
    serializer_class = BooksSerializer
    #end = time.clock()
    #print('Running time: %s Seconds' % (end - start))

class BooksDetail(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]
    
    def get_object(self, name):
        print('2222222222222222222222222222222222')
        try:
            result=Books.objects.filter(name=name)
            print(connection.queries)
            return result
        except Books.DoesNotExist:
            raise Http404
 
    def get(self, request, name, format=None):
        print('------------------------------')
        Books =self.get_object(name=name)
        serializer =BooksSerializer(Books,many=True)
        return Response(serializer.data)
    

    def put(self, request, name, format=None):
        print(request)
        Books = self.get_object(name)
        serializer = BooksSerializer(Books, data=request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, name, format=None):
        Books = self.get_object(name)
        Books.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

from django.contrib.auth.models import User
from rest_framework import generics
from Book.serializer import UserSerializer

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


from django.views.generic import View


class BookDetaialView(View):

    @sync_to_async
    def get_object(self, id):
        try:
            result=Books.objects.filter(id=id)
            print(connection.queries)
            return result
        except Books.DoesNotExist:
            raise Http404
    
    def get(self, request, id, format=None):
        print('----------await-------------------')
        results = async_to_sync(self.get_object)(id)
        serializer = serializers.serialize('json',results)
        return JsonResponse(serializer,safe=False)
    
    def post(self,request,id):
        return HttpResponse('上传图书id是：{}'.format(id))
    def http_method_not_allowed(self, request, *args, **kwargs):
        return HttpResponse('你使用的是%s请求，但是不支持POST以外的其他请求！'%request.method)


async def get(id):
    try:
        results=cache.get(str(id))
        if results==None:
            query=await sync_to_async(Books.objects.filter)(id=id)
            results=await sync_to_async(serializers.serialize)('json',query)
            cache.set(str(id), results, nx=True,timeout=3600)
        return results
    except Books.DoesNotExist:
        raise Http404

async def post(id):
    return HttpResponse('上传图书id是：{}'.format(id))

async def deal(request, id, format=None):
    if request.method == 'GET':
        serializer=await get(id)
    elif request.method == 'POST':
        serializer=await post(id)
    else:
        return HttpResponse('你使用的是%s请求，但是不支持GET/POST以外的其他请求！'%request.method)
    return JsonResponse(serializer,safe=False)