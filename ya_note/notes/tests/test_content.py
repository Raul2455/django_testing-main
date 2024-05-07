from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from . import test_constants

User = get_user_model()


class TestRoutesBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.auth_user = User.objects.create(username='auth_user')
        cls.auth_user_client = Client()
        cls.auth_user_client.force_login(cls.auth_user)
        cls.note = NoteForm()


class TestNotesList(TestRoutesBase):
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
            with self.subTest():
                response = user.get(reverse(test_constants.NOTES_LIST_URL))
                self.assertIn('object_list', response.context)
                object_list = response.context['object_list']
                self.assertIs((TestRoutesBase.note in object_list),
                              note_in_list)


class TestNoteForms(TestRoutesBase):
    def test_pages_contains_form(self):
        """На страницы создания и редактирования заметки передаются формы."""
        urls = (
            (reverse(test_constants.NOTE_ADD_URL), None),
            (reverse(test_constants.NOTE_EDIT_URL,
                     args=(TestRoutesBase.note.slug,))),
        )
        for url, args in urls:
            with self.subTest():
                response = self.author_client.get(url, args)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)


# Добавленная строка
TestRoutesBase.note.author = TestRoutesBase.author
