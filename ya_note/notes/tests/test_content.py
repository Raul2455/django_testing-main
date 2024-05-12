from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from .base import BaseTestCase, Routes

User = get_user_model()


class TestRoutes(BaseTestCase):
    def test_notes_list_for_different_users(self):
        """
        Отдельная заметка передаётся на страницу со списком заметок
        в списке object_list в словаре context.
        В список заметок одного пользователя не попадают заметки
        другого пользователя.
        """
        users_statuses = (
            (self.author_client, True),
            (self.auth_user_client, False),
        )
        for user, note_in_list in users_statuses:
            with self.subTest(user=user, note_in_list=note_in_list):
                response = user.get(Routes.LIST)
                self.assertIn('object_list', response.context)
                object_list = response.context['object_list']
                self.assertIs((self.note in object_list), note_in_list)

    def test_pages_contains_form(self):
        """На страницы создания и редактирования заметки передаются формы."""
        urls = (
            (Routes.ADD, None),
            (Routes.EDIT, (Routes.NOTE_SLUG,)),
        )
        for url, args in urls:
            with self.subTest(url=url, args=args):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
