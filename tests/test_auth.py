# file: tests/test_auth.py
def test_login_page(client):
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_login_success(client, app):
    response = client.post(
        "/auth/login",
        data={"email": "admin@test.com", "password": "admin123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Welcome back" in response.data


def test_login_failure(client):
    response = client.post(
        "/auth/login", data={"email": "wrong@test.com", "password": "wrong"}
    )

    assert b"Invalid email or password" in response.data


def test_protected_route_redirect(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/auth/login" in response.location


def test_logout(logged_in_client):
    response = logged_in_client.post("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"logged out" in response.data.lower()
