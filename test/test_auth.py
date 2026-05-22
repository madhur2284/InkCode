from httpx import AsyncClient

class TestRegister:
    async def test_register(self, client: AsyncClient):
        response = await client.post(url='/auth/register', data={
            "username": "test",
            "email": "test@example.com",
            "password": "password@123",
            "bio": "test"
        })
        assert response.status_code == 201

        data = response.json()
        assert "password" not in data
        assert "hashedpassword" not in data
        assert data["username"] == "test"
        assert data["email"] == "test@example.com"
        assert data["bio"] == "test"
        assert "id" in data
        assert "avatar_url" in data


    async def test_register_duplicate(self, client: AsyncClient):
        await client.post(url='/auth/register', data={
            "username": "test",
            "email": "test@example.com",
            "password": "password@123",
            "bio": "test"
        })

        response = await client.post(url='/auth/register', data={
            "username": "test",
            "email": "test@example.com",
            "password": "password@123",
            "bio": "test"
        })

        assert response.status_code == 400


class TestLogin:
    async def test_login(self, client: AsyncClient):
        await client.post(url='/auth/register', data={
            "username": "test",
            "email": "test@example.com",
            "password": "password@123",
            "bio": "test"
        })
        response = await client.post(url='/auth/login', data={
            "username": "test",
            "password": "password@123"
        })

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data


    async def test_wrong_usersname(self, client: AsyncClient):
        await client.post(url='/auth/register', data={
            "username": "test",
            "email": "test@example.com",
            "password": "password@123",
            "bio": "test"
        })
        response = await client.post(url='/auth/login', data={
            "username": "tets",
            "password": "password@123"
        })

        assert response.status_code == 400

    async def test_wrong_password(self, client: AsyncClient):
        await client.post(url='/auth/register', data={
            "username": "test",
            "email": "test@example.com",
            "password": "password@123",
            "bio": "test"
        })
        response = await client.post(url='/auth/login', data={
            "username": "tets",
            "password": "password@13"
        })

        assert response.status_code == 400


class TestLogout:
    async def test_logout(self, authenticated_client: AsyncClient):
        response = await authenticated_client.post(url='/auth/logout')
        assert response.status_code == 200

    async def test_logout_without_login(self, client: AsyncClient):
        response = await client.post(url='/auth/logout')
        assert response.status_code == 401


class TestChangePassword:
    async def test_change_password(self, authenticated_client: AsyncClient):
        response = await authenticated_client.post(url='/auth/change_password', json={
            "new_password": "test@password",
            "old_password": "testpassword123"
        })

        assert response.status_code == 200


    async def test_change_password_with_wrong_old_password(self, authenticated_client: AsyncClient):
        response = await authenticated_client.post(url='/auth/change_password', json={
            "new_password": "test@password",
            "old_password": "test"
        })

        assert response.status_code == 400


class TestGetMe:
    async def test_get_me(self, authenticated_client: AsyncClient):
        response = await authenticated_client.get(url='/auth/me')
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert "password" not in data
        assert "hashed_password" not in data


    async def test_get_me_without_login(self, client: AsyncClient):
        response = await client.get(url='/auth/me')
        assert response.status_code == 401


class TestUpdate:
    async def test_update_me(self, authenticated_client: AsyncClient):
        response = await authenticated_client.patch(url='/auth/me', data={
            "bio": "hi"
        })

        assert response.status_code == 200

        data = response.json()
        assert data["username"] == "testuser"
        assert data["bio"] == "hi"


class TestDelete:
    async def test_delete_me(self, authenticated_client: AsyncClient):
        response = await authenticated_client.delete(url="/auth/me")
        assert response.status_code == 200