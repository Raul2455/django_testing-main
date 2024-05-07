from notes.models import Note
from django.contrib.auth import get_user_model

User = get_user_model()


def create_user(username):
    return User.objects.create(username=username)


def create_note(title, text, author):
    return Note.objects.create(title=title, text=text, author=author)
