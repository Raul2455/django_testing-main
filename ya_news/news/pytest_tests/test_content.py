from django.conf import settings
from django.urls import reverse
import pytest
from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, list_news):
    """Количество новостей на главной странице — не более 10."""
    url = reverse('news:home')
    response = client.get(url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, list_news):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    url = reverse('news:home')
    response = client.get(url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    db_news_ids = [news_item.id for news_item in object_list]
    fixture_news_ids = [news_item.id for news_item in list_news]
    assert db_news_ids == fixture_news_ids


def test_comments_order(client, news_instance, list_comments):
    """
    Комментарии на странице отдельной новости отсортированы в
    хронологическом порядке: старые в начале списка, новые — в конце.
    """
    url = reverse('news:detail', args=(news_instance.id,))
    response = client.get(url)
    assert 'news' in response.context
    news_item = response.context['news']
    comments_from_db = list(news_item.comment_set.all())
    comments_from_fixture = list(list_comments)
    assert comments_from_db == comments_from_fixture


@pytest.mark.parametrize(
    'parametrized_client, status',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    ),
)
def test_anonymous_client_has_no_form(parametrized_client, status, comment):
    """
    Анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости.
    Авторизованному пользователю доступна форма для отправки
    комментария на странице отдельной новости.
    """
    url = reverse('news:detail', args=(comment.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is status
    if status:
        assert isinstance(response.context['form'], CommentForm)
