from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class Routes:
    NOTE_SLUG = 'test-slug'
    HOME = reverse('notes:home')
    LOGIN = reverse('users:login')
    LOGOUT = reverse('users:logout')
    SIGNUP = reverse('users:signup')
    LIST = reverse('notes:list')
    SUCCESS = reverse('notes:success')
    ADD = reverse('notes:add')
    DETAIL = reverse('notes:detail', args=[NOTE_SLUG])
    EDIT = reverse('notes:edit', args=[NOTE_SLUG])
    DELETE = reverse('notes:delete', args=[NOTE_SLUG])


class BaseTestCase(TestCase):
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
            slug=Routes.NOTE_SLUG,
        )
