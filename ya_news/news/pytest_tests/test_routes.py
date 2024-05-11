from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
def test_pages_availability(client, home_url, login_url,
                            logout_url, signup_url):
    """Проверка доступности страниц неавторизованному пользователю."""
    urls = (
        (home_url, HTTPStatus.OK),
        (login_url, HTTPStatus.OK),
        (logout_url, HTTPStatus.OK),
        (signup_url, HTTPStatus.OK),
    )
    for url, expected_status in urls:
        response = client.get(url)
        assert response.status_code == expected_status, \
            f'Проверьте, что страница {url} доступна всем пользователям. ' \
            f'Код ответа должен быть {expected_status}'


@pytest.mark.django_db
def test_urls_availability(client, admin_client, author_client,
                           news_detail_url, news_edit_url, news_delete_url):
    """Проверка доступности страниц для разных типов пользователей."""
    test_cases = [
        (news_detail_url, client, HTTPStatus.OK),
        (news_edit_url, admin_client, HTTPStatus.NOT_FOUND),
        (news_edit_url, author_client, HTTPStatus.OK),
        (news_delete_url, admin_client, HTTPStatus.NOT_FOUND),
        (news_delete_url, author_client, HTTPStatus.OK)
    ]

    for url, client, expected_status in test_cases:
        response = client.get(url)
        assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('news_edit_url'),
        pytest.lazy_fixture('news_delete_url')
    )
)
def test_redirect_for_anonymous_client(client, url, login_url):
    """
    Проверяем, что неавторизованного пользователя редиректит
    на страницу логина.
    """
    response = client.get(url)
    assertRedirects(response, f'{login_url}?next={url}')
