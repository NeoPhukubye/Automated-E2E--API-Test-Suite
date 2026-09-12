"""Randomized test data generation using Faker."""

from typing import Any, Dict
from faker import Faker


class DataGenerator:
    """Generates randomized test data using Faker for test isolation."""

    def __init__(self, locale: str = "en_US"):
        self._fake = Faker(locale)
        # Seed for reproducibility in CI
        Faker.seed(self._fake, 42)

    def first_name(self) -> str:
        return self._fake.first_name()

    def last_name(self) -> str:
        return self._fake.last_name()

    def full_name(self) -> str:
        return self._fake.name()

    def email(self) -> str:
        return self._fake.email()

    def username(self) -> str:
        return self._fake.user_name()

    def password(self, length: int = 12) -> str:
        return self._fake.password(length=length)

    def postal_code(self) -> str:
        return self._fake.postcode()

    def address(self) -> str:
        return self._fake.address()

    def phone_number(self) -> str:
        return self._fake.phone_number()

    def city(self) -> str:
        return self._fake.city()

    def state(self) -> str:
        return self._fake.state()

    def country(self) -> str:
        return self._fake.country()

    def street_number(self) -> str:
        return self._fake.building_number()

    def street_name(self) -> str:
        return self._fake.street_name()

    def url(self) -> str:
        return self._fake.url()

    def random_int(self, min: int = 0, max: int = 100) -> int:
        return self._fake.random_int(min=min, max=max)

    def random_choice(self, choices: list) -> Any:
        return self._fake.choice(choices)

    def random_sample(self, population: list, k: int = 1) -> list:
        return self._fake.sample(population, k=k)

    def generate_user_payload(self) -> Dict[str, Any]:
        """Generate a complete user payload matching the API schema."""
        return {
            "email": self.email(),
            "username": self.username(),
            "password": self.password(),
            "name": {
                "firstname": self.first_name(),
                "lastname": self.last_name(),
            },
            "address": {
                "city": self.city(),
                "street": f"{self.street_number()} {self.street_name()}",
                "number": self.random_int(1, 999),
                "zipcode": self.postal_code(),
                "geolocation": {
                    "lat": str(self._fake.latitude()),
                    "long": str(self._fake.longitude()),
                },
            },
            "phone": self.phone_number(),
        }

    def generate_product_payload(self) -> Dict[str, Any]:
        """Generate a product payload for API tests."""
        return {
            "title": self._fake.sentence(nb_words=3),
            "price": round(self._fake.random_int(1, 1000) + self._fake.random.random(), 2),
            "description": self._fake.sentence(nb_words=10),
            "image": "https://i.pravatar.cc/150?img=" + str(self.random_int(1, 70)),
            "category": self.random_choice(
                ["electronics", "jewelery", "men's clothing", "women's clothing"]
            ),
        }

    def generate_cart_payload(
        self, user_id: int = 1, product_ids: list = None, quantities: list = None
    ) -> Dict[str, Any]:
        """Generate a cart payload for API tests."""
        if product_ids is None:
            product_ids = [self.random_int(1, 20) for _ in range(self.random_int(1, 3))]
        if quantities is None:
            quantities = [self.random_int(1, 5) for _ in product_ids]

        return {
            "userId": user_id,
            "date": self._fake.date_between(start_date="-30d", end_date="today").isoformat(),
            "products": [
                {"productId": pid, "quantity": qty}
                for pid, qty in zip(product_ids, quantities)
            ],
        }