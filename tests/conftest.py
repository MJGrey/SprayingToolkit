import asyncio
import pytest
import faker
import os
import logging
import random
from faker.providers import internet, misc

fake = faker.Faker()
fake.add_provider(internet)
fake.add_provider(misc)

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(name)s] %(levelname)s - %(message)s"))
log = logging.getLogger("atomizer")
log.setLevel(logging.DEBUG)
log.addHandler(handler)


@pytest.fixture(scope="session", autouse=True)
def fake_usernames_file(tmp_path_factory):
    emails = [
        fake.email(domain=os.environ.get("TEST_EMAIL_DOMAIN")) for _ in range(100)
    ]
    email_file = tmp_path_factory.mktemp("atomizer") / "emails.txt"
    with email_file.open("w") as tmp_email_file:
        for email in emails:
            tmp_email_file.write(email + "\n")
    return email_file


@pytest.fixture(scope="session", autouse=True)
def fake_passwords_file(tmp_path_factory):
    passwords = [fake.password(length=random.randint(8, 15)) for _ in range(2)]
    pass_file = tmp_path_factory.mktemp("atomizer") / "passwords.txt"
    with pass_file.open("w") as tmp_pass_file:
        for passw in passwords:
            tmp_pass_file.write(passw + "\n")
    return pass_file


@pytest.fixture
def fake_username():
    return fake.email(domain=os.environ.get("TEST_EMAIL_DOMAIN"))


@pytest.fixture
def fake_password():
    return fake.password(length=random.randint(8, 15))
