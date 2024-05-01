from django.db import models

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


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        ordering = ['last_name']

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE)
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE)
    distance = models.IntegerField()

    class Meta:
        ordering = ['source', 'destination']


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ['departure_time', 'arrival_time']
        unique_together = (('departure_time', 'arrival_time'),)

    def __str__(self):
        return f"{self.route} ({self.departure_time} -> {self.arrival_time})"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['created_at']
        unique_together = (('created_at', 'user'),)

    def __str__(self):
        return f"{self.created_at} ({self.user})"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name='tickets'
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='tickets'
    )

    def validate_ticket(self):
        existing_ticket = Ticket.objects.filter(
            row=self.row, seat=self.seat, flight=self.flight
        ).first()

        if existing_ticket:
            if existing_ticket.order == self.order:
                return False
            else:
                return False

        return True

    def clean(self):
        if not self.validate_ticket():
            raise ValidationError(
                "This ticket is already occupied by another order.")

        if self.row < 1 or self.seat < 1:
            raise ValidationError(
                "Row and seat numbers must be positive integers.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['row', 'seat', 'flight']
        unique_together = (('row', 'seat', 'flight'),)

    def __str__(self):
        return f"{self.flight} (r: {self.row}, s: {self.seat})"
