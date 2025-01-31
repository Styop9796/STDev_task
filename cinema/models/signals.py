from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Hall, Seat

@receiver(post_save, sender=Hall)
def create_seats_for_hall(sender, instance, created, **kwargs):
    if created:  
        seats = []
        seat_order_number = 1  

        for row in range(1, instance.seat_rows + 1):  
            for seat in range(1, instance.seats_per_row + 1):  
                
                seat_type = Seat.VIP if row == 1 else Seat.STANDARD
                
                seats.append(Seat(
                    hall=instance,
                    row_number=row,
                    seat_number=seat,
                    seat_order=seat_order_number,  
                    seat_type=seat_type  
                ))
                seat_order_number += 1 
        
        Seat.objects.bulk_create(seats)