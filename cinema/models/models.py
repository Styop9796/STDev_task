from django.db import models
from django.core.exceptions import ValidationError


class Country(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'



class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    def __str__(self):
        return f'{self.name}'


class Hall(models.Model):
    cinema_id = models.ForeignKey(Cinema,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    seat_rows = models.IntegerField(default=8)
    seats_per_row = models.IntegerField(default=10)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return f"{self.name} - {self.cinema_id.name}"


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

    class Meta:
        unique_together = ('hall', 'row_number', 'seat_number')

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
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Hall: {self.hall.name}, Row: {self.row_number}, Seat: {self.seat_number}"
    

class Movie(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.IntegerField()
    genre = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class Show(models.Model):
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE)
    hall_id = models.ForeignKey(Hall , on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()


    def clean(self):
        cinema_start_time = self.hall_id.cinema_id.start_time
        cinema_end_time = self.hall_id.cinema_id.end_time

        if not cinema_start_time < self.time < cinema_end_time:
            raise ValidationError(
                f"Can't add a show outside the cinema's working hours ({cinema_start_time} - {cinema_end_time}).",
                code='invalid_time'
            )
        
    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)


    def __str__(self):
        formatted_time = self.time.strftime("%H:%M")
        return f"{self.movie_id.name}, {self.hall_id.name}, {self.date} {formatted_time} "
    