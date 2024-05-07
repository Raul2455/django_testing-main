import pytest
from http import HTTPStatus
from urllib import request
from django.urls import reverse
from pytest_django.asserts import assertRedirects

# Константы с URL-ами для использования в тестах
HOME_URL = pytest.lazy_fixture('home_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')


@pytest.mark.django_db
def test_pages_availability(client, name):
    """
    Главная страница, страницы регистрации пользователей,
    входа в учётную запись и выхода из неё доступны анонимным пользователям.
    """
    response = client.get(name)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, client_fixture, expected_status',
    (
        (DETAIL_URL, 'client', HTTPStatus.OK),
        (EDIT_URL, 'admin_client', HTTPStatus.NOT_FOUND),
        (EDIT_URL, 'author_client', HTTPStatus.OK),
        (DELETE_URL, 'admin_client', HTTPStatus.NOT_FOUND),
        (DELETE_URL, 'author_client', HTTPStatus.OK),
    )
)
def test_url_access_with_different_clients(url,
                                           client_fixture,
                                           expected_status, comment):
    """
    Проверяет доступность URL-адресов с
    разными клиентами и ожидаемыми статусами.
    """
    client = request.getfixturevalue(client_fixture)
    url = reverse(url, args=(comment.id,))
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (EDIT_URL, DELETE_URL),
)
def test_redirect_for_anonymous_client(client, url, comment):
    """
    При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(url, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
