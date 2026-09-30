import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "5-Project-Development-Phase"))
os.environ.pop("GEMINI_API_KEY", None)  # force fallback path

from app import create_app  # noqa: E402


@pytest.fixture()
def client(tmp_path):
    app = create_app(str(tmp_path / "test.db"))
    c = app.test_client()
    c.post("/register", data={"username": "sai", "password": "secret1"})
    c.post("/login", data={"username": "sai", "password": "secret1"})
    return c


def test_generate_requires_login(tmp_path):
    c = create_app(str(tmp_path / "x.db")).test_client()
    assert c.post("/generate-home", data={"budget": "5000"}).status_code == 401


def test_home_within_budget(client):
    r = client.post("/generate-home", data={"budget": "50000", "lights": "5", "fans": "4",
                                            "furniture": "2", "dining_tables": "1"})
    d = r.get_json()
    assert r.status_code == 200 and d["source"] == "fallback" and d["items"]


def test_party_fallback(client):
    r = client.post("/generate-party", data={"budget": "60000", "guests": "50", "event_type": "birthday"})
    assert {i["category"] for i in r.get_json()["items"]} >= {"catering", "decoration", "entertainment"}


def test_jewelry_fallback(client):
    r = client.post("/generate-jewelry", data={"budget": "5000", "occasion": "Wedding"})
    assert r.status_code == 200 and r.get_json()["items"]


@pytest.mark.parametrize("path,data", [
    ("/generate-home", {"budget": "abc"}),
    ("/generate-home", {"budget": "-5", "lights": "1"}),
    ("/generate-home", {"budget": "1000"}),
    ("/generate-party", {"budget": "1000", "guests": "0"}),
    ("/generate-jewelry", {"budget": "1000"}),
])
def test_invalid_input_rejected(client, path, data):
    assert client.post(path, data=data).status_code == 400


def test_history_saved(client):
    client.post("/generate-jewelry", data={"budget": "5000", "occasion": "Festival"})
    assert b"Jewelry Budget Planner" in client.get("/history").data
