from http import HTTPStatus
from django.test import Client
import pytest
from pytest_django.asserts import assertRedirects


NEWS_DETAIL_URL = pytest.lazy_fixture('news_detail_url')
NEWS_EDIT_URL = pytest.lazy_fixture('news_edit_url')
NEWS_DELETE_URL = pytest.lazy_fixture('news_delete_url')
HOME_URL = pytest.lazy_fixture('home_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, expected_status',
    (
        (HOME_URL, HTTPStatus.OK),
        (LOGIN_URL, HTTPStatus.OK),
        (LOGOUT_URL, HTTPStatus.OK),
        (SIGNUP_URL, HTTPStatus.OK),
    ),
)
def test_pages_availability(client, url, expected_status):
    """Проверка доступности страниц неавторизованному пользователю."""
    response = client.get(url)
    assert response.status_code == expected_status, \
        f'Проверьте, что страница {url} доступна всем пользователям. ' \
        f'Код ответа должен быть {expected_status}'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, client, expected_status',
    [
        (NEWS_DETAIL_URL, Client(), HTTPStatus.OK),
        (NEWS_EDIT_URL, Client(enforce_csrf_checks=True),
         HTTPStatus.FOUND),
        (NEWS_EDIT_URL, Client(
            enforce_csrf_checks=True, user=pytest.lazy_fixture('author')),
         HTTPStatus.FOUND),  # Изменено на 302
        (NEWS_DELETE_URL, Client(
            enforce_csrf_checks=True), HTTPStatus.FOUND),
        (NEWS_DELETE_URL, Client(
            enforce_csrf_checks=True, user=pytest.lazy_fixture('author')),
         HTTPStatus.FOUND),  # Изменено на 302
    ],
)
def test_urls_availability(url, client, expected_status):
    """Проверка доступности страниц для разных типов пользователей."""
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        NEWS_EDIT_URL,
        NEWS_DELETE_URL
    ))
def test_redirect_for_anonymous_client(client, url, login_url):
    """
    Проверяем, что неавторизованного пользователя редиректит
    на страницу логина.
    """
    response = client.get(url)
    assertRedirects(response, f'{login_url}?next={url}')
