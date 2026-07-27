from faker import Faker


class TestDataGenerator:
    """Generates randomized test data using Faker."""

    def __init__(self, locale: str = "en_US"):
        self._fake = Faker(locale)

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
