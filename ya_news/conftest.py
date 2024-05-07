import pytest
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.test import Client
from django.contrib.auth import get_user_model

from news.models import News, Comment

TEXT_COMMENT = 'Текст комментария'


@pytest.fixture(autouse=True)
def enable_db_access(db):
    """Автоматически предоставляет доступ к базе данных для всех тестов."""
    pass  # No action needed, as db fixture already provides access


@pytest.fixture
def new_text_comment():
    """Новый текст для комментария."""
    return {'text': 'Новый текст'}


@pytest.fixture
def user():
    """Создаём пользователя."""
    return get_user_model().objects.create(username='Автор')


@pytest.fixture
def user_client(user):
    """Создаём клиент для авторизованного пользователя."""
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def another_user():
    """Создаём другого пользователя."""
    return get_user_model().objects.create(username='Другой пользователь')


@pytest.fixture
def another_user_client(another_user):
    """Создаём клиент для другого пользователя."""
    client = Client()
    client.force_login(another_user)
    return client


@pytest.fixture
def news_item():
    """Создаём новость."""
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
        date=datetime.today(),
    )


@pytest.fixture
def comment_item(news_item, user):
    """Создаём комментарий."""
    return Comment.objects.create(
        text=TEXT_COMMENT,
        news=news_item,
        author=user
    )


@pytest.fixture
def news_list():
    """Создаём список новостей."""
    today = datetime.today()
    news_list = [
        News(title=f'Новость {i}', text='Текст новости',
             date=today - timedelta(days=i))
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE)
    ]
    News.objects.bulk_create(news_list)


@pytest.fixture
def comment_list(news_item, user):
    """Создаём список комментариев."""
    now = timezone.now()
    comment_list = [
        Comment(text=f'Текст {i}', news=news_item,
                author=user, created=now + timedelta(minutes=i))
        for i in range(5)  # Увеличено количество комментариев
    ]
    Comment.objects.bulk_create(comment_list)
