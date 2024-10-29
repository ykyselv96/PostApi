from httpx import AsyncClient


async def test_bad_create_user__not_password(ac: AsyncClient):
    payload = {
        "password": "",
        "password_repeat": "",
        "email": "test@gmail.com",
        "username": "test"
    }
    response = await ac.post("/users/", json=payload)
    assert response.status_code == 422


async def test_bad_create_user_low_password(ac: AsyncClient):
    payload = {
      "password": "tet",
      "password_repeat": "tet",
      "email": "test@test.test",
      "username": "test"
    }
    response = await ac.post("/users/", json=payload)
    assert response.status_code == 422


async def test_bad_create_user_dont_match(ac: AsyncClient):
    payload = {
      "password": "test",
      "password_repeat": "tess",
      "email": "test@test.test",
      "username": "test"
    }
    response = await ac.post("/users/", json=payload)
    assert response.status_code == 422


async def test_bad_create_user_no_valid_email(ac: AsyncClient):
    payload = {
      "password": "test",
      "password_repeat": "tess",
      "email": "test",
      "username": "test"
    }
    response = await ac.post("/users/", json=payload)
    assert response.status_code == 422


async def test_create_user_one(ac: AsyncClient):
    payload = {
      "password": "qwerty*1testtT*",
      "password_repeat": "qwerty*1testtT*",
      "email": "test1@gmail.com",
      "username": "test1",
      "comments_reply": True,
      "auto_reply_delay": 1
    }
    response = await ac.post("/users/", json=payload)
    assert response.status_code == 201
    assert response.json().get("id") == 1


async def test_bad_create_user__email_exist(ac: AsyncClient):
    payload = {
        "password": "qwerty*1testtT*",
        "password_repeat": "qwerty*1testtT*",
        "email": "test1@gmail.com",
        "username": "test1",
    }

    response = await ac.post("/users/", json=payload)
    assert response.status_code == 409


async def test_create_user_two(ac: AsyncClient):
    payload = {
        "password": "qwerty*2testtT+",
        "password_repeat": "qwerty*2testtT+",
        "email": "test2@gmail.com",
        "username": "test2",
    }

    response = await ac.post("/users/", json=payload)
    assert response.status_code == 201
    assert response.json().get("id") == 2


async def test_create_user_three(ac: AsyncClient):
    payload = {
      "password": "qwerty*3testtT+",
      "password_repeat": "qwerty*3testtT+",
      "email": "test3@gmail.com",
      "username": "test3",
    }

    response = await ac.post("/users/", json=payload)
    assert response.status_code == 201
    assert response.json().get("id") == 3


async def test_create_user_four(ac: AsyncClient):
    payload = {
        "password": "qwerty*4testtT+",
        "password_repeat": "qwerty*4testtT+",
        "email": "test4@gmail.com",
        "username": "test4",
    }
    response = await ac.post("/users/", json=payload)
    assert response.status_code == 201
    assert response.json().get("id") == 4


async def test_create_user_five(ac: AsyncClient):

    payload = {
        "password": "qwerty*5testtT+",
        "password_repeat": "qwerty*5testtT+",
        "email": "test5@gmail.com",
        "username": "test5",
    }
    response = await ac.post("/users/", json=payload)
    assert response.status_code == 201
    assert response.json().get("id") == 5


async def test_bad_try_login(ac: AsyncClient, login_user):
    response = await login_user("test2@gmail.com", "test_bad")
    assert response.status_code == 401
    assert response.json().get('detail') == 'Incorrect password'


async def test_try_login_one(ac: AsyncClient, login_user):
    response = await login_user("test1@gmail.com", "qwerty*1testtT*")
    assert response.status_code == 200
    assert response.json().get('token_type') == 'Bearer'


async def test_try_login_two(ac: AsyncClient, login_user):
    response = await login_user("test2@gmail.com", "qwerty*2testtT+")
    assert response.status_code == 200
    assert response.json().get('token_type') == 'Bearer'


async def test_try_login_three(ac: AsyncClient, login_user):
    response = await login_user("test3@gmail.com", "qwerty*3testtT+")
    assert response.status_code == 200
    assert response.json().get('token_type') == 'Bearer'


async def test_try_login_four(ac: AsyncClient, login_user):
    response = await login_user("test4@gmail.com", "qwerty*4testtT+")
    assert response.status_code == 200
    assert response.json().get('token_type') == 'Bearer'


async def test_try_login_five(ac: AsyncClient, login_user):
    response = await login_user("test5@gmail.com", "qwerty*5testtT+")
    assert response.status_code == 200
    assert response.json().get('token_type') == 'Bearer'


async def test_get_users_list(ac: AsyncClient):

    response = await ac.get("/users/")
    assert response.status_code == 200
    assert len(response.json().get('items')) == 5


async def test_get_user_by_id(ac: AsyncClient):

    response = await ac.get("/users/2")
    assert response.status_code == 200
    assert response.json().get('username') == "test2"
    assert response.json().get('email') == "test2@gmail.com"
    assert response.json().get('id') == 2
    assert response.json().get('password') is None


async def test_bad_get_user_by_id__not_found(ac: AsyncClient):

    response = await ac.get("/users/6")

    assert response.status_code == 404
    assert response.json().get('detail') == "User_not_found"


async def test_bad_update_user_one__not_your_acc(ac: AsyncClient, users_tokens):
    payload = {
        "username": "test1NEW",
    }
    headers = {
        "Authorization": f"Bearer {users_tokens['test1@gmail.com']}",
    }
    response = await ac.put("/users/2", json=payload, headers=headers)
    assert response.status_code == 403
    assert response.json().get("detail") == "You can't update other users"


async def test_update_user_one(ac: AsyncClient, users_tokens):
    payload = {
        "username": "test1NEW",
    }
    headers = {
        "Authorization": f"Bearer {users_tokens['test1@gmail.com']}",
    }
    response = await ac.put("/users/1", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json().get("id") == 1


async def test_get_user_by_id_updated(ac: AsyncClient, users_tokens):
    headers = {
        "Authorization": f"Bearer {users_tokens['test1@gmail.com']}",
    }
    response = await ac.get("/users/1", headers=headers)
    assert response.status_code == 200
    assert response.json().get("id") == 1
    assert response.json().get("email") == 'test1@gmail.com'
    assert response.json().get("username") == 'test1NEW'
    assert response.json().get('password') is None


async def test_bad_delete_user_five__not_your_acc(ac: AsyncClient, users_tokens):
    headers = {
        "Authorization": f"Bearer {users_tokens['test1@gmail.com']}",
    }
    response = await ac.delete("/users/5", headers=headers)
    assert response.status_code == 403
    assert response.json().get("detail") == "You can't delete another users"


async def test_delete_user_five(ac: AsyncClient, users_tokens):
    headers = {
        "Authorization": f"Bearer {users_tokens['test5@gmail.com']}",
    }
    response = await ac.delete("/users/5", headers=headers)
    assert response.status_code == 200


async def test_get_users_list_after_delete(ac: AsyncClient, users_tokens):
    headers = {
        "Authorization": f"Bearer {users_tokens['test1@gmail.com']}",
    }
    response = await ac.get("/users/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 4
