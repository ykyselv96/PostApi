from httpx import AsyncClient
from sqlalchemy import text

from app.crud.post_crud import PostCrud
from app.schemas.post_schema import PostCreationForm
from app.schemas.user_schema import User
import pytest
from fastapi import HTTPException


current_user = User(id=1, username='Test', password='qwerty*12346', email='test@gmail.com')
current_user_2 = User(id=2, username='Test2', password='qwerty*12346', email='test4@gmail.com')


# CRUD TESTS(with mocks)
async def test_create_post_if_it_exits(ac: AsyncClient, db_session, monkeypatch):

    post_crud = PostCrud(db_session)

    payload = PostCreationForm(
        title="post1",
        text="string"
    )

    async def mock_if_post_in_db(post_title="post1"):
        return True

    monkeypatch.setattr(post_crud, 'if_post_in_db_by_title', mock_if_post_in_db)

    with pytest.raises(HTTPException) as ex:
        await post_crud.create_post(payload, current_user)

    assert ex.value.status_code == 409
    assert ex.value.detail == "There is already another post with this title"


async def test_create_post_inappropriate(ac: AsyncClient, db_session, monkeypatch):

    post_crud = PostCrud(db_session)

    payload = PostCreationForm(
        title="post1",
        text="string1"
    )

    async def mock_if_post_in_db(post_title):
        return False

    monkeypatch.setattr(post_crud, 'if_post_in_db_by_title', mock_if_post_in_db)

    def policy_check(title, text):
        return True

    monkeypatch.setattr(post_crud, 'policy_check', policy_check)

    with pytest.raises(HTTPException) as ex:
        await post_crud.create_post(payload, current_user)
    assert ex.value.status_code == 403
    assert ex.value.detail == "Your post contains prohibited content and has been blocked."

    db_result = await db_session.execute(
            text("SELECT * FROM posts")
        )
    posts = db_result.fetchall()
    assert len(posts) == 1
    assert posts[0].user_id == 1
    assert posts[0].id == 1
    assert posts[0].is_blocked is True


async def test_create_post_good(ac: AsyncClient, db_session, monkeypatch):
    post_crud = PostCrud(db_session)

    payload = PostCreationForm(
        title="post1",
        text="string1"
    )

    async def mock_if_post_in_db(post_title):
        return False

    monkeypatch.setattr(post_crud, 'if_post_in_db_by_title', mock_if_post_in_db)

    def policy_check(title, text):
        return False

    monkeypatch.setattr(post_crud, 'policy_check', policy_check)

    response = await post_crud.create_post(payload, current_user_2)

    assert response.id == 2
    assert response.title == "post1"
    assert response.text == "string1"
    assert response.is_blocked is False

    db_result = await db_session.execute(
            text("SELECT * FROM posts")
        )

    posts = db_result.fetchall()

    assert len(posts) == 2
    assert posts[1].id == 2
    assert posts[1].user_id == 2
    assert posts[1].is_blocked is False


# API tests
async def test_create_post_unauthorized(ac: AsyncClient):
    payload = {
        "title": "post1",
        "text": "string"
    }
    response = await ac.post("/posts/", json=payload)

    assert response.json().get('detail') == 'Not authenticated'
    assert response.status_code == 403


async def test_bad_create_post__no_title(ac: AsyncClient, users_tokens):
    headers = {
        "Authorization": f"Bearer {users_tokens['test1@gmail.com']}",
    }
    payload = {
        "title": "",
        "text": "description"
    }
    response = await ac.post("/posts/", json=payload, headers=headers)
    assert response.status_code == 422


async def test_create_first_post_with_inappropriate_language(ac: AsyncClient, users_tokens, db_session):

    headers = {
        "Authorization": f"Bearer {users_tokens['test1@gmail.com']}",
    }
    payload = {
        "title": "ХУЙ",  # sorry for inappropriate language, but it's need for test
        "text": "post_description"
    }

    response = await ac.post("/posts/", json=payload, headers=headers)

    db_result = await db_session.execute(
        text("SELECT * FROM posts")
    )
    posts = db_result.fetchall()
    assert len(posts) == 3
    assert posts[0].user_id == 1
    assert posts[0].is_blocked is True
    assert response.status_code == 403
    assert response.json().get("detail") == 'Your post contains prohibited content and has been blocked.'


async def test_create_post_good_api(users_tokens, ac: AsyncClient, db_session):
    headers = {
        "Authorization": f"Bearer {users_tokens['test2@gmail.com']}",
    }

    payload = {
        "title": "good post",
        "text": "good post description",
    }
    response = await ac.post("/posts/", json=payload, headers=headers)

    db_result = await db_session.execute(
        text("SELECT * FROM posts")
    )
    posts = db_result.fetchall()

    assert len(posts) == 4
    assert posts[3].user_id == 2

    assert not posts[3].is_blocked
    assert response.status_code == 201
    assert response.json().get("id") == 4


async def test_get_all_posts_unauth(users_tokens, ac: AsyncClient):

    response = await ac.get("/posts/")

    assert response.status_code == 403
    assert response.json().get('detail') == 'Not authenticated'


async def test_get_all_posts_auth(users_tokens, ac: AsyncClient):
    headers = {
        "Authorization": f"Bearer {users_tokens['test1@gmail.com']}",
    }
    response = await ac.get("/posts/", headers=headers)
    assert response.status_code == 200
    assert len(response.json().get('items')) == 4


async def test_get_post_by_id_not_found(users_tokens, ac: AsyncClient):
    headers = {
        "Authorization": f"Bearer {users_tokens['test1@gmail.com']}",
    }
    response = await ac.get("/posts/7", headers=headers)
    assert response.status_code == 404


async def test_get_post_by_id_first(users_tokens, ac: AsyncClient):
    headers = {
        "Authorization": f"Bearer {users_tokens['test3@gmail.com']}",
    }
    response = await ac.get("/posts/1", headers=headers)
    assert response.status_code == 200

    assert response.json().get("id") == 1
    assert response.json().get("is_blocked") is True
    assert response.json().get("author").get('id') == 1
    assert response.json().get("author").get("comments_reply") is True


async def test_get_post_by_id_sec(users_tokens, ac: AsyncClient):
    headers = {
        "Authorization": f"Bearer {users_tokens['test1@gmail.com']}",
    }
    response = await ac.get("/posts/2", headers=headers)
    assert response.status_code == 200
    assert response.json().get("id") == 2
    assert not response.json().get("is_blocked")
    assert response.json().get("author").get("id") == 2
    assert not response.json().get("author").get("comments_reply")


async def test_bad_update_post__unauthorized(ac: AsyncClient):
    payload = {
        "title": "post_name_1_NEW",
        "text": "post_description_1_NEW"
    }
    response = await ac.put("/posts/1", json=payload)
    assert response.status_code == 403
    assert response.json().get('detail') == 'Not authenticated'


async def test_bad_update_post__not_found(users_tokens, ac: AsyncClient):
    headers = {
        "Authorization": f"Bearer {users_tokens['test1@gmail.com']}",
    }
    payload = {
        "title": "post_name_1_NEW",
        "text": "post_description_1_NEW"
    }
    response = await ac.put("/posts/100", json=payload, headers=headers)
    assert response.status_code == 404
    assert response.json().get('detail') == 'Post_not_found'


async def test_bad_update_not_your_post(users_tokens, ac: AsyncClient):
    headers = {
        "Authorization": f"Bearer {users_tokens['test1@gmail.com']}",
    }
    payload = {
        "title": "post_name_1_NEW",
        "text": "post_description_1_NEW"
    }

    response = await ac.put("/posts/2", json=payload, headers=headers)
    assert response.status_code == 403
    assert response.json().get('detail') == 'You can update only your own posts'


async def test_update_blocked_post(users_tokens, ac: AsyncClient, db_session):
    headers = {
        "Authorization": f"Bearer {users_tokens['test1@gmail.com']}",
    }
    payload = {
        "title": "post_name_1_NEW",
    }
    response = await ac.put("/posts/1", json=payload, headers=headers)
    db_result = await db_session.execute(
        text("SELECT * FROM posts WHERE id = 1")
    )
    posts = db_result.fetchone()
    assert not posts.is_blocked

    assert posts.title == "post_name_1_NEW"
    assert response.status_code == 200


async def test_bad_delete_post_not_auth(users_tokens, ac: AsyncClient):
    response = await ac.delete("/posts/1")
    assert response.status_code == 403
    assert response.json().get('detail') == 'Not authenticated'


async def test_bad_delete_post_not_owner(users_tokens, ac: AsyncClient):
    headers = {
        "Authorization": f"Bearer {users_tokens['test2@gmail.com']}",
    }
    response = await ac.delete("/posts/1", headers=headers)
    assert response.status_code == 403
    assert response.json().get('detail') == 'You can delete only your own posts'


async def test_delete_post_sec(users_tokens, ac: AsyncClient, db_session):

    headers = {
        "Authorization": f"Bearer {users_tokens['test2@gmail.com']}",
    }
    response = await ac.delete("/posts/2", headers=headers)

    db_result = await db_session.execute(
        text("SELECT * FROM posts")
    )
    posts = db_result.fetchall()

    assert len(posts) == 3

    assert response.status_code == 200
    assert response.json().get("id") == 2
    assert response.json().get("author").get('id') == 2
