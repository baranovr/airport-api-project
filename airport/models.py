import os
import uuid

from django.db import models
from django.utils.text import slugify

from rest_framework.exceptions import ValidationError

from airport_api_project import settings


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


class AirplaneType(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


def airplane_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/airplanes/", filename)


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)
    airplane_image = models.ImageField(
        null=True,
        blank=True,
        upload_to=airplane_image_file_path
    )

    class Meta:
        ordering = ["id"]

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"{self.name} (Type: {self.airplane_type})"


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="source_routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="destination_routes"
    )
    distance = models.IntegerField()

    class Meta:
        ordering = ["source", "destination"]


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        ordering = ["id"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew)

    class Meta:
        ordering = ["id", "departure_time", "arrival_time"]
        unique_together = (("departure_time", "arrival_time"),)

    def __str__(self):
        return f"{self.route} ({self.departure_time} -> {self.arrival_time})"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.created_at} ({self.user})"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets",
        null=True,
        blank=True
    )

    def clean(self):
        if self.row < 1 or self.row > self.flight.airplane.rows:
            raise ValidationError(
                f"The row number must be in the range from 1 to "
                f"{self.flight.airplane.rows}"
            )

        if self.seat < 1 or self.seat > self.flight.airplane.seats_in_row:
            raise ValidationError(
                f"The seat number must be in the range from 1 to "
                f"{self.flight.airplane.seats_in_row}"
            )

        if Ticket.objects.filter(
                row=self.row,
                seat=self.seat,
                flight=self.flight
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                "This seat is already occupied on this flight."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @staticmethod
    def validate_ticket(row, seat, flight):
        if row < 1 or row > flight.airplane.rows:
            raise ValidationError(
                f"The row number must be in the range from 1 to "
                f"{flight.airplane.rows}"
            )

        if seat < 1 or seat > flight.airplane.seats_in_row:
            raise ValidationError(
                f"The seat number must be in the range from 1 to "
                f"{flight.airplane.seats_in_row}"
            )

        if Ticket.objects.filter(row=row, seat=seat, flight=flight).exists():
            raise ValidationError(
                "This seat is already occupied on this flight."
            )

    class Meta:
        ordering = ["id",]
        unique_together = (("row", "seat", "flight"),)

    def __str__(self):
        return f"{self.flight} (r: {self.row}, s: {self.seat})"
