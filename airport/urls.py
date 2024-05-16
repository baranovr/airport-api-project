from rest_framework import routers

from airport.views import (
    AirplaneViewSet,
    AirplaneTypeViewSet,
    CrewViewSet,
    RouteViewSet,
    FlightViewSet,
    OrderViewSet,
    AirportViewSet,
    TicketViewSet
)

router = routers.DefaultRouter()

router.register("airplanes", AirplaneViewSet, basename="airplanes")
router.register("airports", AirportViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("crews", CrewViewSet)
router.register("routes", RouteViewSet)
router.register("flights-list", FlightViewSet, basename="flights")
router.register("orders", OrderViewSet)
router.register("tickets", TicketViewSet)

urlpatterns = router.urls

app_name = "airport"
