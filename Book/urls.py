from django.urls import path, include
from rest_framework.routers import DefaultRouter
from Book import views
# books/urls.py

router = DefaultRouter()
router.register('Book', views.BooksViewSet)

urlpatterns = [
    path('all', include(router.urls)),
    path('index',views.index),
    path('sync/<str:name>/', views.BooksDetail.as_view()),
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    path('async/<int:id>',views.deal),
    path('orm',views.orm_test),
]