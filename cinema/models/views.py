from django.shortcuts import render
from .models import Country,City,Cinema,Hall,Seat,Movie,Show,Booking
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

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



@csrf_exempt
def create_reservation(request):
    if request.method == "POST":
        try:
            request_data = json.loads(request.body)
            show_id = request_data.get('show_id')
            seat_id = request_data.get('seat_id')
            name = request_data.get("name")
            email = request_data.get("email")
            phone = request_data.get("phone")

            show_instance = Show.objects.get(id=show_id)
            seat_instance = Seat.objects.get(id=seat_id)

            if not Booking.objects.filter(show_id=show_instance, seat_id=seat_id).exists():
                new_reservation = Booking.objects.create(
                    show_id=show_instance, 
                    seat_id=seat_instance,
                    customer_name=name,
                    customer_email=email,
                    customer_phone=phone,
                    status='confirmed'
                )
                new_reservation.save()
                return JsonResponse({"status": 200, "message": "Reservation created successfully"})
            else:
                return JsonResponse({"status": 400, "message": "Seat is not available"})
        except Show.DoesNotExist:
            return JsonResponse({"status": 400, "message": "Show not found"})
        except Seat.DoesNotExist:
            return JsonResponse({"status": 400, "message": "Seat not found"})
        except json.JSONDecodeError:
            return JsonResponse({"status": 400, "message": "Invalid JSON data"})
        except Exception as e:
            return JsonResponse({"status": 400, "message": str(e)})
    else:
        return JsonResponse({"status": 400, "message": "Method not allowed"})