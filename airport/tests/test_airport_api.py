from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

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

User = get_user_model()


class AirportViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.airport = Airport.objects.create(name="Test Airport")

    def test_airport_list(self):
        url = reverse("airport-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_airport_create(self):
        url = reverse("airport-list")
        data = {"name": "New Airport"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AirplaneTypeViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.airplane_type = AirplaneType.objects.create(
            name="Test Airplane Type"
        )

    def test_airplane_type_list(self):
        url = reverse("airplanetype-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_airplane_type_create(self):
        url = reverse("airplanetype-list")
        data = {"name": "New Airplane Type"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AirplaneViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.airplane_type = AirplaneType.objects.create(
            name="Test Airplane Type"
        )
        self.airplane = Airplane.objects.create(
            name="Test Airplane",
            rows=10,
            seats_in_row=6,
            airplane_type=self.airplane_type
        )

    def test_airplane_list(self):
        url = reverse("airplane-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_airplane_retrieve(self):
        url = reverse(
            "airplane-detail",
            kwargs={"pk": self.airplane.pk}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Airplane")


class CrewViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.crew = Crew.objects.create(name="Test Crew")

    def test_crew_list(self):
        url = reverse("crew-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_crew_create(self):
        url = reverse("crew-list")
        data = {"name": "New Crew"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class RouteViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.airport1 = Airport.objects.create(name="Test Airport 1")
        self.airport2 = Airport.objects.create(name="Test Airport 2")
        self.route = Route.objects.create(
            source=self.airport1,
            destination=self.airport2,
            distance=1000
        )

    def test_route_list(self):
        url = reverse("route-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_route_retrieve(self):
        url = reverse("route-detail", kwargs={"pk": self.route.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["source"]["airport"]["name"],
            "Test Airport 1"
        )
        self.assertEqual(
            response.data["destination"]["airport"]["name"],
            "Test Airport 2"
        )


class FlightViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.airplane_type = AirplaneType.objects.create(
            name="Test Airplane Type"
        )
        self.airplane = Airplane.objects.create(
            name="Test Airplane",
            rows=10,
            seats_in_row=6,
            airplane_type=self.airplane_type
        )
        self.airport1 = Airport.objects.create(name="Test Airport 1")
        self.airport2 = Airport.objects.create(name="Test Airport 2")
        self.route = Route.objects.create(
            source=self.airport1,
            destination=self.airport2,
            distance=1000
        )
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time="2023-05-01T10:00:00Z",
            arrival_time="2023-05-01T12:00:00Z"
        )

    def test_flight_list(self):
        url = reverse("flight-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_flight_retrieve(self):
        url = reverse("flight-detail", kwargs={"pk": self.flight.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["route"]["source"]["airport"]["name"],
            "Test Airport 1"
        )
        self.assertEqual(
            response.data["route"]["destination"]["airport"]["name"],
            "Test Airport 2"
        )
        self.assertEqual(
            response.data["airplane"]["name"],
            "Test Airplane"
        )


class TicketViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword"
        )
        self.client.force_authenticate(user=self.user)
        self.airplane_type = AirplaneType.objects.create(
            name="Test Airplane Type"
        )
        self.airplane = Airplane.objects.create(
            name="Test Airplane",
            rows=10,
            seats_in_row=6,
            airplane_type=self.airplane_type
        )
        self.airport1 = Airport.objects.create(name="Test Airport 1")
        self.airport2 = Airport.objects.create(name="Test Airport 2")
        self.route = Route.objects.create(
            source=self.airport1,
            destination=self.airport2,
            distance=1000
        )
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time="2023-05-01T10:00:00Z",
            arrival_time="2023-05-01T12:00:00Z"
        )
        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            order=self.order,
            flight=self.flight,
            price=500
        )

    def test_ticket_list(self):
        url = reverse("ticket-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_ticket_retrieve(self):
        url = reverse("ticket-detail", kwargs={"pk": self.ticket.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["flight"]["id"], self.flight.pk)
        self.assertEqual(response.data["price"], 500)


class OrderViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword"
        )

        self.client.force_authenticate(user=self.user)
        self.airplane_type = AirplaneType.objects.create(
            name="Test Airplane Type"
        )
        self.airplane = Airplane.objects.create(
            name="Test Airplane",
            rows=10,
            seats_in_row=6,
            airplane_type=self.airplane_type
        )
        self.airport1 = Airport.objects.create(name="Test Airport 1")
        self.airport2 = Airport.objects.create(name="Test Airport 2")
        self.route = Route.objects.create(
            source=self.airport1,
            destination=self.airport2,
            distance=1000
        )
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time="2023-05-01T10:00:00Z",
            arrival_time="2023-05-01T12:00:00Z"
        )
        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            order=self.order,
            flight=self.flight,
            price=500
        )
    
    def test_order_list(self):
        url = reverse("order-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["user"], self.user.pk)
    
    def test_order_create(self):
        url = reverse("order-list")
        data = {"tickets": [{"flight": self.flight.pk, "price": 600}]}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(Ticket.objects.count(), 2)
