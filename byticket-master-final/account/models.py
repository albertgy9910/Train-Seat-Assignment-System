from django.db import models
from django.contrib.auth.models import AbstractUser


# account information
# database model
class myUser(AbstractUser):
    prefered = models.CharField(max_length=100)
    number_luggage = models.IntegerField(blank=True, null=True)
    order_key = models.CharField(max_length=50,blank=True, null=True)


# ticket information
class order(models.Model):
    user_name = models.ForeignKey(to='myUser', blank=True, null=True, on_delete=models.SET_NULL,)
    order_number = models.CharField('ticket number', max_length=100)
    order_type = models.CharField('ticket_type', max_length=10)
    order_price = models.CharField('ticket_price', max_length=5)
    seat_number = models.CharField('seat_number', max_length=5)
    Departure_station = models.CharField('Departure_station', max_length=50)
    destination_station = models.CharField('destination_station', max_length=50)
    order_key = models.CharField('order key', max_length=50, blank=True, null=True)


# User is associated with seat selection
class seat(models.Model):
    order_id = models.ForeignKey(to='order', blank=True, null=True, on_delete=models.SET_NULL)
    name_id = models.ForeignKey(to='myUser', blank=True, null=True, on_delete=models.SET_NULL)
    seat_type = models.CharField('seat type', max_length=10, blank=True, null=True)
    seat_number = models.CharField('seat number', max_length=10, blank=True, null=True)
    seat_status = models.CharField('seat status', max_length=2, blank=True, null=True)
    seat_complete_time = models.CharField('Seat selection completion time',max_length=20, blank=True, null=True)


class user_seat_selection(models.Model):
    order_id = models.ForeignKey(to='order', blank=True, null=True, on_delete=models.SET_NULL,)
    user_name = models.ForeignKey(to='myUser', blank=True, null=True, on_delete=models.SET_NULL,)
    seat_name = models.ForeignKey(to='seat', blank=True, null=True, on_delete=models.SET_NULL,)