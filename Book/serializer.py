# books/serializer.py
from django.db import connection
from rest_framework import serializers
from Book.models import Books

class BooksSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = Books
        fields = '__all__'

from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    Books = serializers.PrimaryKeyRelatedField(many=True, queryset=Books.objects.all())
    print(connection.queries)
    class Meta:
        model = User
        fields = ['id', 'username', 'Books']