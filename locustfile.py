import random
import string
from locust import HttpUser, task, between
from typing import Optional

WORKING_CODES: list[str] = []


def random_string(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def add_working_code(code: str):
    global WORKING_CODES
    WORKING_CODES.append(code)


def get_code_for_request() -> Optional[str]:
    if not WORKING_CODES:
        return None
    return random.choice(WORKING_CODES)


class ShortLinkUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        response = self.client.post(
            "/user/login",
            data={"username": "admin", "password": "password"},
            name="/user/login",
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.auth_headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.auth_headers = {}

    @task(1)
    def root(self):
        self.client.get("/", name="/")

    @task(10)
    def shorten_unauthorized(self):
        url = f"https://example.com/{random_string(6)}"
        r = self.client.post("/link/shorten", json={"original_url": url}, name="/link/shorten [unauth]")
        if r.status_code == 201 and r.json().get("short_code"):
            add_working_code(r.json()["short_code"])

    @task(5)
    def shorten_authorized(self):
        if not self.auth_headers:
            return
        url = f"https://example.com/{random_string(10)}"
        alias = random_string(6)
        r = self.client.post(
            "/link/shorten",
            json={"original_url": url, "custom_alias": alias},
            headers=self.auth_headers,
            name="/link/shorten [auth]",
        )
        if r.status_code == 201 and r.json().get("short_code"):
            add_working_code(r.json()["short_code"])

    @task(3)
    def stats(self):
        code = get_code_for_request()
        if not code:
            return
        self.client.get(f"/link/{code}/stats", allow_redirects=False, name="/link/[short_code] stats")

    @task(1)
    def link_all(self):
        if not self.auth_headers:
            return
        self.client.get("/link/all", headers=self.auth_headers, name="/link/all")

#Для тестирования пользователей переходящих по ссылкам
class RandomUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def redirect(self):
        code = get_code_for_request()
        if not code:
            return
        self.client.get(f"/link/{code}", allow_redirects=False, name="/link/[short_code]")
