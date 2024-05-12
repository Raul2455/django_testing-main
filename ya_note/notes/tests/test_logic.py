from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from ..forms import WARNING
from .base import BaseTestCase, Routes

User = get_user_model()


class TestRoutes(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        Note.objects.all().delete()
        response = self.author_client.post(Routes.ADD, data=self.data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.data['title'])
        self.assertEqual(new_note.text, self.data['text'])
        self.assertEqual(new_note.slug, self.data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count = Note.objects.count()
        response = self.client.post(Routes.ADD, self.data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={Routes.ADD}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        response = self.author_client.post(Routes.ADD, data={
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': self.note.slug
        })
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """
        Если при создании заметки не заполнен slug, то он формируется
        автоматически, с помощью функции pytils.translit.slugify
        """
        Note.objects.all().delete()
        self.data.pop('slug')
        response = self.author_client.post(Routes.ADD, self.data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_delete_note(self):
        """Пользователь может удалять свои заметки."""
        notes_count = Note.objects.count()
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), notes_count - 1)

    def test_other_user_cant_delete_note(self):
        """Пользователь не может удалять чужие заметки."""
        notes_count = Note.objects.count()
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.auth_user_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.post(url, self.data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.data['title'])
        self.assertEqual(self.note.text, self.data['text'])
        self.assertEqual(self.note.slug, self.data['slug'])
        self.assertEqual(self.note.author, self.author)

    def test_other_user_cant_edit_note(self):
        """Пользователь не может редактировать чужие заметки."""
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.auth_user_client.post(url, self.data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Заголовок')
        self.assertEqual(self.note.text, 'Текст')
        self.assertEqual(self.note.slug, Routes.NOTE_SLUG)
        self.assertEqual(self.note.author, self.author)
