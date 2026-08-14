import pytest

from app import create_app
from app.extensions import db

TEST_EMAIL = "jane.doe" + "@" + "filmtest.local"


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_register_success(client):
    resp = client.post("/api/auth/register", json={
        "name": "Jane Doe",
        "email": TEST_EMAIL,
        "password": "password123",
    })
    assert resp.status_code == 201
    body = resp.get_json()
    assert "token" in body
    assert body["user"]["email"] == TEST_EMAIL
    assert body["user"]["auth_provider"] == "local"


def test_register_duplicate_email_blocked(client):
    client.post("/api/auth/register", json={
        "name": "Jane Doe", "email": TEST_EMAIL, "password": "password123",
    })
    resp = client.post("/api/auth/register", json={
        "name": "Jane Doe", "email": TEST_EMAIL, "password": "password123",
    })
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "account_exists"


def test_login_success(client):
    client.post("/api/auth/register", json={
        "name": "Jane Doe", "email": TEST_EMAIL, "password": "password123",
    })
    resp = client.post("/api/auth/login", json={
        "email": TEST_EMAIL, "password": "password123",
    })
    assert resp.status_code == 200
    assert "token" in resp.get_json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "name": "Jane Doe", "email": TEST_EMAIL, "password": "password123",
    })
    resp = client.post("/api/auth/login", json={
        "email": TEST_EMAIL, "password": "wrongpassword",
    })
    assert resp.status_code == 401


def test_me_requires_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_with_token(client):
    reg = client.post("/api/auth/register", json={
        "name": "Jane Doe", "email": TEST_EMAIL, "password": "password123",
    })
    token = reg.get_json()["token"]
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.get_json()["user"]["email"] == TEST_EMAIL
    assert resp.get_json()["user"]["profile_completed"] is False


def test_profile_setup_updates_user(client):
    reg = client.post("/api/auth/register", json={
        "name": "Jane Doe", "email": TEST_EMAIL, "password": "password123",
    })
    token = reg.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.put("/api/auth/profile", json={
        "name": "Jane D.",
        "company": "Indie Unit",
        "production_role": "wardrobe",
        "additional_roles": ["props", "wardrobe", "sound"],
        "experience_level": "professional",
    }, headers=headers)

    assert resp.status_code == 200
    user = resp.get_json()["user"]
    assert user["name"] == "Jane D."
    assert user["production_role"] == "wardrobe"
    assert user["production_role_label"] == "Wardrobe"
    assert user["additional_roles"] == ["props", "sound"]
    assert user["company"] == "Indie Unit"
    assert user["experience_level"] == "professional"
    assert user["profile_completed"] is True


def test_profile_setup_rejects_unknown_role(client):
    reg = client.post("/api/auth/register", json={
        "name": "Jane Doe", "email": TEST_EMAIL, "password": "password123",
    })
    token = reg.get_json()["token"]

    resp = client.put("/api/auth/profile", json={
        "production_role": "dragon_department",
    }, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "invalid_input"


def test_google_login_creates_user(client, app, monkeypatch):
    app.config["GOOGLE_CLIENT_ID"] = "test-client-id.apps.googleusercontent.com"

    def fake_verify(token, request, audience):
        assert token == "valid-google-token"
        assert audience == app.config["GOOGLE_CLIENT_ID"]
        return {
            "sub": "google-user-123",
            "email": "google.user@filmtest.local",
            "name": "Google User",
            "email_verified": True,
        }

    monkeypatch.setattr(
        "app.routes.auth_routes.google_id_token.verify_oauth2_token",
        fake_verify,
    )

    resp = client.post("/api/auth/google", json={"id_token": "valid-google-token"})

    assert resp.status_code == 201
    body = resp.get_json()
    assert "token" in body
    assert body["user"]["email"] == "google.user@filmtest.local"
    assert body["user"]["auth_provider"] == "google"
    assert body["user"]["profile_completed"] is False


def test_google_login_blocks_existing_local_email(client, app, monkeypatch):
    app.config["GOOGLE_CLIENT_ID"] = "test-client-id.apps.googleusercontent.com"
    client.post("/api/auth/register", json={
        "name": "Jane Doe", "email": TEST_EMAIL, "password": "password123",
    })

    def fake_verify(token, request, audience):
        return {
            "sub": "google-user-456",
            "email": TEST_EMAIL,
            "name": "Jane Doe",
            "email_verified": True,
        }

    monkeypatch.setattr(
        "app.routes.auth_routes.google_id_token.verify_oauth2_token",
        fake_verify,
    )

    resp = client.post("/api/auth/google", json={"id_token": "valid-google-token"})

    assert resp.status_code == 409
    assert resp.get_json()["error"] == "account_exists"
