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
    
    async def get(self, request, name, format=None):
        print('------------------------------')
        #Books =await sync_to_async(self.get_object, thread_sensitive=True)(name=name)
        Books=await sync_to_async(self.get_object,thread_sensitive=True)(name=name)
        #serializer =await sync_to_async(BooksSerializer,thread_sensitive=True)(Books,many=True)
        serializer=await sync_to_async(BooksSerializer)(Books,many=True)
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



