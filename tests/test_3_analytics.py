from httpx import AsyncClient


# API tests
async def test_get_analytics(ac: AsyncClient, setup_fake_data):

    response = await ac.get("/api/comments-daily-breakdown", params={"date_from": "2024-10-28",
                                                                     "date_to": "2024-10-28"})
    assert len(response.json().get('comments_statistic_per_day')) == 1
    assert response.json().get('comments_statistic_per_day')[0].get('total_comments_amount') == 4
    assert response.json().get('comments_statistic_per_day')[0].get('created_comments_amount') == 2
    assert response.json().get('comments_statistic_per_day')[0].get('blocked_comments_amount') == 2
    assert response.json().get('comments_total_amount') == 4
    assert response.status_code == 200


async def test_2_get_analytics(ac: AsyncClient, setup_fake_data):

    response = await ac.get("/api/comments-daily-breakdown", params={"date_from": "2024-10-20",
                                                                     "date_to": "2024-10-28"})

    assert len(response.json().get('comments_statistic_per_day')) == 3
    assert response.json().get('comments_statistic_per_day')[0].get('total_comments_amount') == 1
    assert response.json().get('comments_statistic_per_day')[0].get('created_comments_amount') == 1
    assert response.json().get('comments_statistic_per_day')[0].get('blocked_comments_amount') == 0
    assert response.json().get('comments_statistic_per_day')[0].get('date') == '2024-10-22'

    assert response.json().get('comments_statistic_per_day')[1].get('total_comments_amount') == 1
    assert response.json().get('comments_statistic_per_day')[1].get('created_comments_amount') == 1
    assert response.json().get('comments_statistic_per_day')[1].get('blocked_comments_amount') == 0
    assert response.json().get('comments_statistic_per_day')[1].get('date') == '2024-10-23'

    assert response.json().get('comments_statistic_per_day')[2].get('total_comments_amount') == 4
    assert response.json().get('comments_statistic_per_day')[2].get('created_comments_amount') == 2
    assert response.json().get('comments_statistic_per_day')[2].get('blocked_comments_amount') == 2
    assert response.json().get('comments_statistic_per_day')[2].get('date') == '2024-10-28'

    assert response.json().get('comments_total_amount') == 6
    assert response.status_code == 200


async def test_3_get_analytics(ac: AsyncClient, setup_fake_data):

    response = await ac.get("/api/comments-daily-breakdown", params={"date_from": "2024-10-18",
                                                                     "date_to": "2024-10-20"})
    assert len(response.json().get('comments_statistic_per_day')) == 0
    assert response.status_code == 200
