from django.urls import path
from .views import get_cinemas,get_halls,get_shows,get_seats,create_reservation

urlpatterns = [
    path('get_cinemas/',get_cinemas,name='get_cinemas'),
    path('get_halls/',get_halls,name="get_halls"),
    path('get_shows/',get_shows,name='get_shows'),
    path('get_seats/',get_seats,name='get_seats'),
    path('create_reservation/',create_reservation,name='create_reservation')

]