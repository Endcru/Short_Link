import pytest


def test_link_shorten_unauthorized(client):
    response = client.post("/link/shorten", json={"original_url": "https://www.youtube.com/"})
    assert response.status_code == 201
    data = response.json()
    assert data["original_url"] == "https://www.youtube.com/"
    assert "short_code" in data
    short_code = data["short_code"]
    response = client.get(f"/link/{short_code}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://www.youtube.com/"


def test_link_shorten_with_alias_unauthorized(client):
    response = client.post("/link/shorten", json={"original_url": "https://example.com/", "custom_alias": "alias"})
    assert response.status_code == 400


def test_link_not_found(client):
    response = client.get("/link/wrong_code")
    assert response.status_code == 404

def test_link_shorten_authorized(client, auth_headers):
    response = client.post(
        "/link/shorten",
        json={"original_url": "https://example.com/", "custom_alias": "myalias"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["short_code"] == "myalias"

def test_link_shorten_authorized_wrong_expires_at(client, auth_headers):
    response = client.post("/link/shorten", json={"original_url": "https://noalias.com/", "expires_at": "2020-01-01"}, headers=auth_headers)
    assert response.status_code == 400

def test_link_shorten_authorized_no_alias(client, auth_headers):
    response = client.post("/link/shorten", json={"original_url": "https://noalias.com/"}, headers=auth_headers)
    assert response.status_code == 201
    assert "short_code" in response.json()


def test_link_shorten_alias_exists(client, auth_headers):
    client.post("/link/shorten", json={"original_url": "https://a.com/", "custom_alias": "x"}, headers=auth_headers)
    response = client.post("/link/shorten", json={"original_url": "https://b.com/", "custom_alias": "x"}, headers=auth_headers)
    assert response.status_code == 400


def test_link_shorten_alias_blocked(client, auth_headers):
    response = client.post(
        "/link/shorten",
        json={"original_url": "https://x.com/", "custom_alias": "all"},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_link_all(client):
    response = client.get("/link/all")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "links" in data


def test_link_stats(client, auth_headers):
    client.post("/link/shorten", json={"original_url": "https://stats.com/", "custom_alias": "stats"}, headers=auth_headers)
    response = client.get("/link/stats/stats", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["short_code"] == "stats"


def test_link_stats_not_found(client):
    response = client.get("/link/stats/nonexistent_code")
    assert response.status_code == 404


def test_link_project(client, auth_headers):
    client.post("/link/shorten", json={"original_url": "https://p.com/", "project": "proj"}, headers=auth_headers)
    response = client.get("/link/project/proj", headers=auth_headers)
    assert response.status_code == 200
    assert "links" in response.json()

def test_link_project_not_found(client, auth_headers):
    response = client.get("/link/project/nonexistent", headers=auth_headers)
    assert response.status_code == 200
    assert "links" in response.json()
    assert len(response.json()["links"]) == 0

def test_link_unauthorized_project(client):
    response = client.get("/link/project/proj")
    assert response.status_code == 401


def test_link_search(client, auth_headers):
    response = client.get("/link/search?original_url=https://example.com/", headers=auth_headers)
    assert response.status_code == 200
    assert "links" in response.json()


def test_link_search_unauthorized(client):
    response = client.get("/link/search?original_url=https://example.com/")
    assert response.status_code == 200
    assert "links" in response.json()


def test_link_update(client, auth_headers):
    client.post("/link/shorten", json={"original_url": "https://u.com/", "custom_alias": "upd"}, headers=auth_headers)
    response = client.patch("/link/upd", json={"project": "newproj"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["project"] == "newproj"

def test_link_update_not_found(client, auth_headers):
    response = client.patch("/link/nonexistent", headers=auth_headers, json={"project": "project"})
    assert response.status_code == 404


def test_link_update_used_alias(client, auth_headers):
    client.post("/link/shorten", json={"original_url": "https://u.com/", "custom_alias": "upd"}, headers=auth_headers)
    response = client.patch("/link/upd", json={"custom_alias": "upd"}, headers=auth_headers)
    assert response.status_code == 400

def test_link_update_wrong_user(client):
    client.post("/user/", json={"username": "link_test", "email": "link_test@example.com", "password": "pass123"})
    response = client.post("/user/login", data={"username": "link_test", "password": "pass123"})
    assert response.status_code == 200
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    response = client.patch("/link/upd", json={"project": "newproj"}, headers=headers)
    assert response.status_code == 403

def test_link_update_wrong_expires_at(client, auth_headers):
    response = client.patch("/link/upd", json={"expires_at": "2020-01-01"}, headers=auth_headers)
    assert response.status_code == 400

def test_link_delete(client, auth_headers):
    client.post("/link/shorten", json={"original_url": "https://d.com/", "custom_alias": "del"}, headers=auth_headers)
    response = client.delete("/link/del", headers=auth_headers)
    assert response.status_code == 204
    assert client.get("/link/del", follow_redirects=False).status_code == 404


def test_link_delete_not_found(client, auth_headers):
    response = client.delete("/link/nonexistent", headers=auth_headers)
    assert response.status_code == 404

def test_link_delete_wrong_user(client, auth_headers):
    client.post("/link/shorten", json={"original_url": "https://d.com/", "custom_alias": "del"}, headers=auth_headers)
    response = client.post("/user/login", data={"username": "link_test", "password": "pass123"})
    assert response.status_code == 200
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    client.post("/link/shorten", json={"original_url": "https://d.com/", "custom_alias": "del"}, headers=headers)
    response = client.delete("/link/del", headers=headers)
    assert response.status_code == 403