from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.urls import reverse

from .base import BaseTestCase, Routes  # Импортируем Routes

User = get_user_model()


class TestRoutes(BaseTestCase):
    def test_pages_availability(self):
        """Проверка доступности страниц для разных типов пользователей."""
        tests = [
            (Routes.LOGIN, self.client, HTTPStatus.OK),
            (Routes.LOGOUT, self.client, HTTPStatus.OK),
            (Routes.SIGNUP, self.client, HTTPStatus.OK),
            (Routes.LIST, self.author_client, HTTPStatus.OK),
            (Routes.SUCCESS, self.author_client, HTTPStatus.OK),
            (Routes.ADD, self.author_client, HTTPStatus.OK),
            (Routes.DETAIL, self.author_client, HTTPStatus.OK),
            (Routes.EDIT, self.author_client, HTTPStatus.OK),
            (Routes.DELETE, self.author_client, HTTPStatus.OK),
            (Routes.DETAIL, self.auth_user_client, HTTPStatus.NOT_FOUND),
            (Routes.EDIT, self.auth_user_client, HTTPStatus.NOT_FOUND),
            (Routes.DELETE, self.auth_user_client, HTTPStatus.NOT_FOUND),
        ]
        for url, client, expected_status in tests:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirects_for_anonymous_user(self):
        """Проверка перенаправлений для анонимных пользователей."""
        login_url = reverse('users:login')
        urls = [
            Routes.LIST,
            Routes.SUCCESS,
            Routes.ADD,
            Routes.DETAIL,
            Routes.EDIT,
            Routes.DELETE,
        ]
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
