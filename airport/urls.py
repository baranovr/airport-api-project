from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirplaneViewSet,
    AirplaneTypeViewSet,
    CrewViewSet,
    RouteViewSet,
    FlightViewSet,
    OrderViewSet,
    AirportViewSet
)

router = routers.DefaultRouter()

router.register("airplanes", AirplaneViewSet)
router.register("airports", AirportViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("crews", CrewViewSet)
router.register("routes", RouteViewSet)
router.register("flights-list", FlightViewSet, basename='flights')
router.register("orders", OrderViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "airport"
