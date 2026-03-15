import pytest


def test_user_login(client):
    response = client.post("/user/login",data={"username": "admin", "password": "password"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_user_login_invalid(client):
    response = client.post("/user/login", data={"username": "admin", "password": "wrong_password"})
    assert response.status_code == 401


def test_user_current_no_auth(client):
    response = client.get("/user/currentUser/")
    assert response.status_code == 401

def test_user_create(client):
    response = client.post("/user/", json={"username": "username", "email": "username@example.com", "password": "pass123"})
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "username"
    assert data["email"] == "username@example.com"
    assert data["is_active"] is True
    assert data["is_admin"] is False
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_user_current_auth(client, auth_headers):
    response = client.get("/user/currentUser/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "admin"


def test_user_get_by_id_admin(client, auth_headers):
    response = client.get("/user/1", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_user_get_by_id_not_admin(client, auth_headers):
    client.post("/user/", json={"username": "username", "email": "username@example.com", "password": "pass123"})
    response = client.post("/user/login", data={"username": "username", "password": "pass123"})
    assert response.status_code == 200
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    response = client.get("/user/1", headers=headers)
    assert response.status_code == 403


def test_user_list_admin(client, auth_headers):
    response = client.get("/user/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "users" in data
    assert len(data["users"]) > 0


def test_user_get_by_id_not_found(client, auth_headers):
    response = client.get("/user/99999", headers=auth_headers)
    assert response.status_code == 404

def test_user_list_not_admin(client, auth_headers):
    client.post("/user/", json={"username": "username", "email": "username@example.com", "password": "pass123"})
    response = client.post("/user/login", data={"username": "username", "password": "pass123"})
    assert response.status_code == 200
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    response = client.get("/user/", headers=headers)
    assert response.status_code == 403

def test_user_get_by_username_admin(client, auth_headers):
    response = client.get("/user/username/admin", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "admin"


def test_user_get_by_username_not_found(client, auth_headers):
    response = client.get("/user/username/nonexistent_use", headers=auth_headers)
    assert response.status_code == 404


def test_user_get_by_username_not_admin(client, auth_headers):
    client.post("/user/", json={"username": "username", "email": "username@example.com", "password": "pass123"})
    response = client.post("/user/login", data={"username": "username", "password": "pass123"})
    assert response.status_code == 200
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    response = client.get("/user/username/username", headers=headers)
    assert response.status_code == 403

@pytest.mark.skip(reason="search_users не реализован")
def test_user_search_admin(client, auth_headers):
    response = client.get("/user/search/?q=username", headers=auth_headers)
    assert response.status_code == 200


def test_user_search_not_admin(client, auth_headers):
    client.post("/user/", json={"username": "username", "email": "username@example.com", "password": "pass123"})
    response = client.post("/user/login", data={"username": "username", "password": "pass123"})
    assert response.status_code == 200
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    response = client.get("/user/search/?q=username", headers=headers)
    assert response.status_code == 403

def test_user_delete(client):
    response = client.post("/user/", json={"username": "todelete", "email": "del@example.com", "password": "pass123",})
    assert response.status_code == 201
    uid = response.json()["id"]
    response = client.post("/user/login", data={"username": "todelete", "password": "pass123"})
    assert response.status_code == 200
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    response = client.delete(f"/user/{uid}", headers=headers)
    assert response.status_code == 204

def test_user_patch(client):
    response = client.post("/user/", json={"username": "patch", "email": "patch@example.com", "password": "pass123"})
    assert response.status_code == 201
    uid = response.json()["id"]
    response = client.post("/user/login", data={"username": "patch", "password": "pass123"})
    assert response.status_code == 200
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    response = client.patch(f"/user/{uid}", headers=headers, json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False