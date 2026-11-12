"""Randomized test data generation using Faker."""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from faker import Faker


@dataclass
class UserData:
    """Structured user test data."""
    email: str
    username: str
    password: str
    firstname: str
    lastname: str
    city: str
    street: str
    number: int
    zipcode: str
    lat: str
    long: str
    phone: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API payload format."""
        return {
            "email": self.email,
            "username": self.username,
            "password": self.password,
            "name": {
                "firstname": self.firstname,
                "lastname": self.lastname,
            },
            "address": {
                "city": self.city,
                "street": self.street,
                "number": self.number,
                "zipcode": self.zipcode,
                "geolocation": {
                    "lat": self.lat,
                    "long": self.long,
                },
            },
            "phone": self.phone,
        }


@dataclass
class ProductData:
    """Structured product test data."""
    title: str
    price: float
    description: str
    image: str
    category: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API payload format."""
        return {
            "title": self.title,
            "price": self.price,
            "description": self.description,
            "image": self.image,
            "category": self.category,
        }


@dataclass
class CartData:
    """Structured cart test data."""
    user_id: int
    date: str
    products: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API payload format."""
        return {
            "userId": self.user_id,
            "date": self.date,
            "products": self.products,
        }


class DataGenerator:
    """Generates randomized test data using Faker for test isolation."""

    VALID_CATEGORIES = [
        "electronics",
        "jewelery",
        "men's clothing",
        "women's clothing",
    ]

    def __init__(self, locale: str = "en_US", seed: Optional[int] = 42):
        self._fake = Faker(locale)
        # Seed for reproducibility in CI
        if seed is not None:
            self._fake.seed_instance(seed)

    def reset_seed(self, seed: int) -> None:
        """Reset the Faker seed for reproducible data."""
        self._fake.seed_instance(seed)

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

    def random_float(self, min: float = 0.0, max: float = 1000.0, precision: int = 2) -> float:
        return round(self._fake.random.uniform(min, max), precision)

    def random_choice(self, choices: list) -> Any:
        return self._fake.random.choice(choices)

    def random_sample(self, population: list, k: int = 1) -> list:
        return self._fake.random.sample(population, k=k)

    def random_bool(self) -> bool:
        return self._fake.random.random() > 0.5

    def sentence(self, nb_words: int = 10) -> str:
        return self._fake.sentence(nb_words=nb_words)

    def paragraph(self, nb_sentences: int = 3) -> str:
        return self._fake.paragraph(nb_sentences=nb_sentences)

    def date_between(self, start_date: str = "-30d", end_date: str = "today") -> str:
        """Generate a date string between start and end."""
        return self._fake.date_between(start_date=start_date, end_date=end_date).isoformat()

    def date_time_between(self, start_date: str = "-30d", end_date: str = "now") -> str:
        """Generate a datetime string between start and end."""
        return self._fake.date_time_between(start_date=start_date, end_date=end_date).isoformat()

    def generate_user_data(self) -> UserData:
        """Generate structured user test data."""
        return UserData(
            email=self.email(),
            username=self.username(),
            password=self.password(),
            firstname=self.first_name(),
            lastname=self.last_name(),
            city=self.city(),
            street=f"{self.street_number()} {self.street_name()}",
            number=self.random_int(1, 999),
            zipcode=self.postal_code(),
            lat=str(self._fake.latitude()),
            long=str(self._fake.longitude()),
            phone=self.phone_number(),
        )

    def generate_product_data(self) -> ProductData:
        """Generate structured product test data."""
        return ProductData(
            title=self._fake.sentence(nb_words=3),
            price=self.random_float(1.0, 1000.0),
            description=self._fake.sentence(nb_words=10),
            image=f"https://i.pravatar.cc/150?img={self.random_int(1, 70)}",
            category=self.random_choice(self.VALID_CATEGORIES),
        )

    def generate_cart_data(
        self,
        user_id: int = 1,
        product_ids: Optional[list] = None,
        quantities: Optional[list] = None,
    ) -> CartData:
        """Generate structured cart test data."""
        if product_ids is None:
            product_ids = [self.random_int(1, 20) for _ in range(self.random_int(1, 3))]
        if quantities is None:
            quantities = [self.random_int(1, 5) for _ in product_ids]

        return CartData(
            user_id=user_id,
            date=self.date_between(),
            products=[
                {"productId": pid, "quantity": qty}
                for pid, qty in zip(product_ids, quantities)
            ],
        )

    def generate_user_payload(self) -> Dict[str, Any]:
        """Generate a complete user payload matching the API schema."""
        return self.generate_user_data().to_dict()

    def generate_product_payload(self) -> Dict[str, Any]:
        """Generate a product payload for API tests."""
        return self.generate_product_data().to_dict()

    def generate_cart_payload(
        self,
        user_id: int = 1,
        product_ids: Optional[list] = None,
        quantities: Optional[list] = None,
    ) -> Dict[str, Any]:
        """Generate a cart payload for API tests."""
        return self.generate_cart_data(user_id, product_ids, quantities).to_dict()

    def generate_login_credentials(self) -> Dict[str, str]:
        """Generate valid login credentials for the FakeStore API."""
        return {
            "username": "mor_2314",
            "password": "83r5^_",
        }

    def generate_invalid_login_credentials(self) -> Dict[str, str]:
        """Generate invalid login credentials for negative testing."""
        return {
            "username": self.username(),
            "password": self.password(),
        }

    def generate_boundary_test_data(self) -> Dict[str, Dict[str, Any]]:
        """Generate boundary value test data for edge case testing."""
        return {
            "min_price_product": {
                "title": "Min Price Product",
                "price": 0.01,
                "description": "Product with minimum price",
                "image": "https://example.com/min.jpg",
                "category": "electronics",
            },
            "max_price_product": {
                "title": "Max Price Product",
                "price": 999999.99,
                "description": "Product with maximum price",
                "image": "https://example.com/max.jpg",
                "category": "electronics",
            },
            "empty_title_product": {
                "title": "",
                "price": 10.0,
                "description": "Product with empty title",
                "image": "https://example.com/empty.jpg",
                "category": "electronics",
            },
            "long_title_product": {
                "title": "x" * 1000,
                "price": 10.0,
                "description": "Product with very long title",
                "image": "https://example.com/long.jpg",
                "category": "electronics",
            },
            "special_chars_product": {
                "title": "Product with <script>alert('xss')</script> & \"quotes\"",
                "price": 10.0,
                "description": "Product with special characters",
                "image": "https://example.com/special.jpg",
                "category": "electronics",
            },
        }

    def generate_pagination_params(
        self,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate pagination query parameters."""
        params = {}
        if limit is not None:
            params["limit"] = limit
        if sort is not None:
            params["sort"] = sort
        return params