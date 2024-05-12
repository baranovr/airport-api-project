from django.db import models

from rest_framework.exceptions import ValidationError

from airport_api_project import settings


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class AirplaneType(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)

    class Meta:
        ordering = ['name']
        unique_together = (('name', 'airplane_type'),)

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"{self.name} (Type: {self.airplane_type})"


class Route(models.Model):
    source = models.ForeignKey(
        Airport,on_delete=models.CASCADE, related_name='source_routes'
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name='destination_routes'
    )
    distance = models.IntegerField()

    class Meta:
        ordering = ['source', 'destination']


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ['departure_time', 'arrival_time']
        unique_together = (('departure_time', 'arrival_time'),)

    def __str__(self):
        return f"{self.route} ({self.departure_time} -> {self.arrival_time})"


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    flights = models.ManyToManyField(Flight)

    class Meta:
        ordering = ['last_name']

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.created_at} ({self.user})"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name='flight_tickets'
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='order_tickets'
    )

    @staticmethod
    def validate_ticket(row, seat, airplane, error):
        for attr, attr_name in [(row, "row"), (seat, "seat")]:
            max_value = getattr(airplane, f"{attr_name}s_in_{attr_name}")
            if not (1 <= attr <= max_value):
                raise error({
                    f"Attribute {attr_name} is out of range. \n"
                    f"\tAvailable range: (1, {max_value}): 1, {max_value}."
                })

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError,
        )

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    class Meta:
        ordering = ['row', 'seat', 'flight']
        unique_together = (('row', 'seat', 'flight'),)

    def __str__(self):
        return f"{self.flight} (r: {self.row}, s: {self.seat})"
