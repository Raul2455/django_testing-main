from datetime import datetime, timedelta
import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.test.client import Client
from ..models import Comment, News

TEXT_COMMENT = 'Текст комментария'


@pytest.fixture(autouse=True)
def enable_db_access(db):
    """Фикстура для автоматического предоставления доступа к БД."""
    pass


@pytest.fixture
def new_text_comment():
    """Новый текст для комментария."""
    return {'text': 'Новый текст'}


@pytest.fixture
def author(django_user_model):
    """Создаём пользователя."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    """Создаём клиента, авторизованного как автор."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def another_user(django_user_model):
    """Создаём еще одного пользователя."""
    return django_user_model.objects.create(username='Еще один автор')


@pytest.fixture
def another_author_client(another_user):
    """Создаём клиента, авторизованного как еще один автор."""
    client = Client()
    client.force_login(another_user)
    return client


@pytest.fixture
def news_instance():
    """Создаём новость."""
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
        date=datetime.today(),
    )


@pytest.fixture
def comment(news_instance, author):
    """Создаём комментарий."""
    return Comment.objects.create(
        text=TEXT_COMMENT,
        news=news_instance,
        author=author
    )


@pytest.fixture
def list_news():
    """Создаём список новостей."""
    today = datetime.today()
    news_list = [
        News(
            title=f'Новость {index}',
            text='Текст новости',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE)
    ]
    News.objects.bulk_create(news_list)


@pytest.fixture
def list_comments(news_instance, author):
    """Создаём список комментариев."""
    now = timezone.now()
    for index in range(5):
        Comment.objects.create(
            text=f'Текст {index}',
            news=news_instance,
            author=author,
            created=now + timedelta(days=index)
        )


@pytest.fixture
def home_url():
    """Возвращает URL главной страницы."""
    return reverse('news:home')


@pytest.fixture
def login_url():
    """Возвращает URL страницы входа."""
    return reverse('users:login')


@pytest.fixture
def logout_url():
    """Возвращает URL страницы выхода."""
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    """Возвращает URL страницы регистрации."""
    return reverse('users:signup')


@pytest.fixture
def news_detail_url(news_instance):
    """Возвращает URL страницы новости."""
    return reverse('news:detail', args=(news_instance.id,))


@pytest.fixture
def news_edit_url(comment):
    """Возвращает URL страницы редактирования комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def news_delete_url(comment):
    """Возвращает URL страницы удаления комментария."""
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def bad_words_data():
    """Словарь с запрещенными словами."""
    return {'text': f'Какой-то текст, {settings.BAD_WORDS[0]}, еще текст'}
