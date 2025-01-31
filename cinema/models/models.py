from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta,datetime

class Country(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.name}'



class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}, {self.country.name}'



class Cinema(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    address = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE)  
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f'{self.name}'
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone_number": self.phone_number,
            "email": self.email,
            "address": self.address,
            "city": self.city.name,
            "country" : self.city.country.name,  
            "work_start_time": self.start_time.strftime("%H:%M"),  
            "work_end_time": self.end_time.strftime("%H:%M"), 
        }
    
    @classmethod
    def get_all_cinemas(cls):
        cinemas = [cinema.to_dict() for cinema in Cinema.objects.all()]
        return cinemas




class Hall(models.Model):
    cinema = models.ForeignKey(Cinema,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    seat_rows = models.IntegerField(default=8)
    seats_per_row = models.IntegerField(default=10)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.cinema.name}"

    def to_dict(self):
        return {
            "hall_id" : self.id,
            "cinema_id": self.cinema.id,
            "name" : self.name
        }
    
    @classmethod
    def get_hall_by_cinema_id(cls,cinema_id):
        halls = [hall.to_dict() for hall in cls.objects.filter(cinema_id=cinema_id)]
        return halls

class Seat(models.Model):

    STANDARD = 'standard'
    VIP = 'vip'

    SEAT_TYPE_CHOICES = [
        (STANDARD, 'Standard'),
        (VIP, 'VIP'),
    ]


    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    row_number = models.IntegerField()
    seat_number = models.IntegerField()
    seat_type =  models.CharField(max_length=10,choices=SEAT_TYPE_CHOICES,default=STANDARD)
    seat_order = models.IntegerField(help_text="The order of seats within the hall, min 1st row 1st seat , max last row last seat")

    

    def clean(self):

        if self.row_number < 1 or self.row_number > self.hall.seat_rows:
            raise ValidationError(
                f"Row number must be between 1 and {self.hall.seat_rows}.", 
                code='invalid_row_number'
            )

        if self.seat_number < 1 or self.seat_number > self.hall.seats_per_row:
            raise ValidationError(
                f"Seat number must be between 1 and {self.hall.seats_per_row}.", 
                code='invalid_seat_number'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        self.updated_at = timezone.now()  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.hall.name}, Row: {self.row_number}, Seat: {self.seat_number}"
    
    def to_dict(self):
        return {
            "seat_id": self.id,
            "hall_id" : self.hall.id,
            "hall_name" : self.hall.name,
            "row_number" : self.row_number,
            "seat_number" : self.seat_number,
            "seat_order_number" :  self.seat_order,
            "seat_type" : self.seat_type
        }

class Movie(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.IntegerField()
    genre = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

class Show(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    hall = models.ForeignKey(Hall , on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    standard_price = models.FloatField()
    vip_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        cinema_start_time = self.hall.cinema.start_time
        cinema_end_time = self.hall.cinema.end_time

        if not cinema_start_time <= self.time < cinema_end_time:
            raise ValidationError(
                f"Can't add a show outside the cinema's working hours ({cinema_start_time} - {cinema_end_time}).",
                code='invalid_time'
            )
        
        # Calculate the end time of the show by adding the movie's duration
        movie_duration = timedelta(minutes=self.movie.duration)
        show_end_time = (datetime.combine(self.date, self.time) + movie_duration).time()

        # Check if the new show overlaps with any existing shows
        conflicting_shows = Show.objects.filter(
            hall_id=self.hall_id,  
            date=self.date 
        )

        for show in conflicting_shows:
            # Get the end time of the existing show
            existing_show_end_time = (datetime.combine(self.date, show.time) + timedelta(minutes=show.movie.duration)).time()

            # Check if the new show overlaps with any existing show
            if (self.time < existing_show_end_time and show.time < show_end_time):
                raise ValidationError(
                    f"Showtime conflicts with an existing show in the same hall. "
                    f"The requested show time is from {self.time} to {show_end_time}, "
                    f"but there is already a show from {show.time} to {existing_show_end_time}.",
                    code='overlap_error'
                )
    

    def to_dict(self):

        start_datetime = datetime.combine(self.date, self.time)

        end_datetime = start_datetime + timedelta(minutes=self.movie.duration)

        return {
            "show_id" : self.id,
            "hall_id" : self.hall.id,
            "hall_name" : self.hall.name,
            "movie_name" : self.movie.name,
            "movie_description" : self.movie.description,
            "duration" : self.movie.duration,
            "genre" : self.movie.genre,
            "date" : self.date.strftime('%Y/%m/%d'),
            "start_time" : self.time.strftime('%H:%M'),
            "end_time" :  end_datetime.strftime('%H:%M'), 
            "standard_price" : self.standard_price,
            "vip_price" : self.vip_price,
        }




    @classmethod
    def get_upcoming_shows(cls,hall_id):
        now = timezone.now()  
        current_datetime = now.replace(second=0, microsecond=0)

        # Filter upcoming shows (date in the future or if today, time should be after the current time)
        upcoming_show_objects = cls.objects.filter(
            hall_id=hall_id,
            date__gt=now.date()  ) | cls.objects.filter(hall_id=hall_id,date=now.date(),  time__gt=current_datetime.time()  )

        upcoming_shows = [show.to_dict() for show in upcoming_show_objects]

        return upcoming_shows


    def get_all_seats(self):
        # Get all seats for the hall where the show is happening
        all_seats = Seat.objects.filter(hall=self.hall).order_by('seat_order')

        available_seats = []
        for seat in all_seats:
            seat_dictionary = seat.to_dict()

            # If no booking exists for the seat and show, it's available
            if not Booking.objects.filter(show=self, seat=seat).exists():
                seat_dictionary["is_available"] = True
                
            else:
                seat_dictionary["is_available"] = False
            seat_dictionary["show_id"] = self.id
            if seat_dictionary.get("seat_type") == "vip":
                seat_dictionary["price"] = self.vip_price
            else:
                seat_dictionary["price"] = self.standard_price

            available_seats.append(seat_dictionary)

                            
        return available_seats

    def is_started(self):
        start_datetime = datetime.combine(self.date, self.time)
        now = timezone.now()

        if now >= start_datetime:
            return True
        else:
            return False
 
    def get_halls_dimensions(self):
        rows = self.hall.seat_rows
        columns = self.hall.seats_per_row
        return rows,columns

    def save(self, *args, **kwargs):
        self.full_clean()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


    def __str__(self):
        formatted_time = self.time.strftime("%H:%M")
        return f"{self.movie.name}, {self.hall.name}, {self.date} {formatted_time} "
    


class Booking(models.Model):
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (CONFIRMED, 'Confirmed'),
        (CANCELLED, 'Cancelled'),
    ]
    
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name="bookings")
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name="seats")
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    total_price = models.FloatField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('show', 'seat')

    def __str__(self):
        return f"Booking by {self.customer_name} for {self.show.movie.name} on {self.show.date} at {self.show.time}"

    def save(self, *args, **kwargs):
        if self.seat.seat_type == "vip":
            price = self.show.vip_price
        else:
            price = self.show.standard_price

        self.total_price = price
        super().save(*args, **kwargs)
