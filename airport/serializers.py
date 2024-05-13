from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.db import transaction

from airport.models import (
    Airport,
    AirplaneType,
    Airplane,
    Crew,
    Route,
    Flight,
    Ticket,
    Order
)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "airplane_image")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id", "name", "airplane_type", "rows", "seats_in_row", "capacity"
        )


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.CharField(source="airplane_type.name")

    class Meta:
        model = Airplane
        fields = ("id", "airplane_image", "name", "airplane_type")


class AirplaneDetailSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer(read_only=True)

    class Meta:
        model = Airplane
        fields = (
            "id",
            "airplane_image",
            "name",
            "airplane_type",
            "rows",
            "seats_in_row",
            "capacity"
        )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.CharField(source="source.name", read_only=True)
    destination = serializers.CharField(
        source="destination.name", read_only=True
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination")


class RouteDetailSerializer(RouteSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "crew",
            "airplane",
            "crew",
            "departure_time",
            "arrival_time"
        )


class FlightListSerializer(FlightSerializer):
    route_source = serializers.CharField(
        source="route.source.name", read_only=True
    )
    route_dest = serializers.CharField(
        source="route.destination.name", read_only=True
    )
    airplane_name = serializers.CharField(
        source="airplane.name", read_only=True
    )
    airplane_type = serializers.CharField(
        source="airplane.airplane_type.name", read_only=True
    )
    airplane_capacity = serializers.IntegerField(
        source="airplane.capacity", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route_source",
            "route_dest",
            "airplane_name",
            "airplane_type",
            "airplane_capacity",
            "tickets_available",
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        flight = attrs.get("flight")
        row = attrs.get("row")
        seat = attrs.get("seat")

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

        return attrs

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class RowAndSeatSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class OrderSerializer(serializers.ModelSerializer):
    tickets = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Ticket.objects.all()
    )

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at", "user")

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        order = Order.objects.create(**validated_data)
        for ticket in tickets_data:
            ticket.order = order
            ticket.save()
        return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
    user = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at", "user")


class FlightDetailSerializer(FlightSerializer):
    route = RouteDetailSerializer(many=False, read_only=True)
    airplane = AirplaneSerializer(many=False, read_only=True)
    crew = CrewSerializer(many=True, read_only=True)
    taken_places = RowAndSeatSerializer(
        source="tickets", many=True, read_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "departure_time",
            "arrival_time",
            "airplane",
            "crew",
            "taken_places"
        )


class TicketDetailSerializer(TicketSerializer):
    flight = FlightDetailSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")
