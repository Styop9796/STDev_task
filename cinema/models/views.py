from django.shortcuts import render
from .models import Country,City,Cinema,Hall,Seat,Movie,Show,Booking
from django.http import JsonResponse


def get_cinemas(request):
    cinemas = Cinema.get_all_cinemas()
    return JsonResponse({"status": 200, "data": cinemas})



def get_halls(request):
    cinema_id = request.GET.get("cinema_id")
    if cinema_id:
        halls = Hall.get_hall_by_cinema_id(cinema_id)
    else:
        return JsonResponse({"status":400,"message":"No cinema_id"})
    return JsonResponse({"status":200,"data":halls})



def get_shows(request):
    hall_id = request.GET.get("hall_id")
    if hall_id:
        shows = Show.get_upcoming_shows(hall_id)
    else: 
        return JsonResponse({"status":400,"message":"No hall_id"})
    return JsonResponse({"status":200,"data":shows})




def get_seats(request):
    show_id = request.GET.get("show_id")
    if show_id:
        show_obj = Show.objects.get(id = show_id)
        seats = show_obj.get_all_seats()
        is_started = show_obj.is_started()

    else:
        return JsonResponse({"status":400,"message":"No hall_id"})
    return JsonResponse({"status":200,
                         "is_show_started":is_started,
                         "data":seats})
