from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.auth_user = User.objects.create(username='auth_user')
        cls.auth_user_client = Client()
        cls.auth_user_client.force_login(cls.auth_user)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )

    def test_pages_availability(self):
        """Проверка доступности страниц для разных типов пользователей."""
        tests = [
            ('notes:home', None, self.client, HTTPStatus.OK),
            ('users:login', None, self.client, HTTPStatus.OK),
            ('users:logout', None, self.client, HTTPStatus.OK),
            ('users:signup', None, self.client, HTTPStatus.OK),
            ('notes:list', None, self.author_client, HTTPStatus.OK),
            ('notes:success', None, self.author_client, HTTPStatus.OK),
            ('notes:add', None, self.author_client, HTTPStatus.OK),
            ('notes:detail', (self.note.slug,),
             self.author_client, HTTPStatus.OK),
            ('notes:edit', (self.note.slug,),
             self.author_client, HTTPStatus.OK),
            ('notes:delete', (self.note.slug,),
             self.author_client, HTTPStatus.OK),
            ('notes:detail', (self.note.slug,),
             self.auth_user_client, HTTPStatus.NOT_FOUND),
            ('notes:edit', (self.note.slug,),
             self.auth_user_client, HTTPStatus.NOT_FOUND),
            ('notes:delete', (self.note.slug,),
             self.auth_user_client, HTTPStatus.NOT_FOUND),
        ]

        for name, args, client, expected_status in tests:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirects_for_anonymous_user(self):
        """Проверка перенаправлений для анонимных пользователей."""
        login_url = reverse('users:login')
        urls = [
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        ]

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
