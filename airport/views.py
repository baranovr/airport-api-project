from datetime import datetime

from django.db.models import F, Count

from drf_spectacular.types import OpenApiTypes

from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from drf_spectacular.utils import extend_schema, OpenApiParameter

from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.models import AirplaneType, Crew, Airplane, Flight, Order, \
    Airport

from airport.serializers import (
    AirplaneTypeSerializer,
    CrewSerializer,
    AirplaneSerializer,
    FlightSerializer,
    FlightDetailSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    RouteSerializer,
    FlightListSerializer,
    OrderSerializer,
    OrderListSerializer, AirportSerializer
)


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Flight.objects.prefetch_related(
        "route__source, route__destination"
    )
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def change_params_str_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        source = self.request.query_params.get("source", None)
        destination = self.request.query_params.get("destination", None)

        queryset = self.queryset

        if source:
            queryset = queryset.filter(
                source__airport__name__icontains=source
            )

        if destination:
            queryset = queryset.filter(
                destination__airport__name__icontains=destination
            )

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type=OpenApiTypes.STR,
                description="Filter by source airport",
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.STR,
                description="Filter by destination airport",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.all().select_related("route", "airplane")
        .annotate(
            tickets_avaliable=(
                    F('airplane__rows')
                    * F("airplane__seats_in_row")
                    - Count("flight_tickets")
            )
        )
    )
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        route = self.request.query_params.get("route", None)
        airplane = self.request.query_params.get("airplane", None)
        arrival_time = self.request.query_params.get("arrival_time", None)
        departure_time = self.request.query_params.get("departure_time", None)

        queryset = self.queryset

        if route:
            queryset = queryset.filter(route__source__name__icontains=route)

        if airplane:
            queryset = queryset.filter(
                airplane__name__icontains=airplane
            )

        if arrival_time:
            arr_time = datetime.strptime(
                arrival_time, "%Y-%m-%d"
            ).date()
            queryset = queryset.filter(arrival_time__date=arr_time)

        if departure_time:
            dep_time = datetime.strptime(
                departure_time, "%Y-%m-%d"
            ).date()
            queryset = queryset.filter(departure_time__date=dep_time)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        return FlightSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "route",
                type=OpenApiTypes.STR,
                description="Filter by route",
            ),
            OpenApiParameter(
                "departure_time",
                type=OpenApiTypes.DATE,
                description=(
                        "Filter by departure time (ex. ?date=20024-04-05)"
                ),
            ),
            OpenApiParameter(
                "arrival_time",
                type=OpenApiTypes.DATE,
                description=(
                        "Filter by arrival time (ex. ?date=20024-04-05)"
                ),
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__route", "tickets__flight__airplane"
    )
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
