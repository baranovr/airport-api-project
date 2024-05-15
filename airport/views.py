from datetime import datetime

from django.db.models import F, Count

from drf_spectacular.types import OpenApiTypes

from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly
)

from rest_framework.viewsets import GenericViewSet

from drf_spectacular.utils import extend_schema, OpenApiParameter

from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.models import (
    AirplaneType,
    Crew,
    Airplane,
    Flight,
    Order,
    Airport,
    Route,
    Ticket
)

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
    OrderListSerializer,
    AirportSerializer,
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    TicketSerializer,
    TicketDetailSerializer,
    AirplaneImageSerializer
)


class AirportPagination(PageNumberPagination):
    page_size = 15
    max_page_size = 100


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = AirportPagination


class AirplaneTypePagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = AirplaneTypePagination


class AirplanePagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = AirplanePagination

    @staticmethod
    def change_params_str_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        name = self.request.query_params.get("name")
        airplane_type = self.request.query_params.get("airplane_type")

        queryset = self.queryset

        if name:
            queryset.filter(name__icontains=name)

        if airplane_type:
            queryset.filter(airplane_type__icontains=airplane_type)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer

        if self.action == "retrieve":
            return AirplaneDetailSerializer

        if self.action == "upload_image":
            return AirplaneImageSerializer

        return AirplaneSerializer

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAdminUser],
        url_path="upload-image"
    )
    def upload_image(self, request, pk=None):
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by name",
            ),
            OpenApiParameter(
                "airplane_type",
                type=OpenApiTypes.STR,
                description=(
                        "Filter by airplane type"
                ),
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CrewPagination(PageNumberPagination):
    page_size = 15
    max_page_size = 100


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    pagination_class = CrewPagination


class RoutePagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Route.objects.all()
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def change_params_str_to_ints(qs):
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


class FlightPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.all().select_related("route", "airplane")
        .annotate(
            tickets_available=(
                    F("airplane__rows")
                    * F("airplane__seats_in_row")
                    - Count("tickets")
            )
        )
    )
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    pagination_class = FlightPagination

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


class TicketPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class TicketViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TicketDetailSerializer
        return super().get_serializer_class()


class OrderPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100


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
    pagination_class = OrderPagination

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
