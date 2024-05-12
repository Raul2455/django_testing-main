import pytest
from django.conf import settings
from news.forms import CommentForm


@pytest.mark.parametrize(
    'parametrized_client, status',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    ),
)
def test_anonymous_client_has_no_form(parametrized_client, status,
                                      news_detail_url):
    """
    Анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости.
    Авторизованному пользователю доступна форма для отправки
    комментария на странице отдельной новости.
    """
    response = parametrized_client.get(news_detail_url)
    assert ('form' in response.context) is status
    if status:
        assert isinstance(response.context['form'], CommentForm)


def test_news_count(client, list_news, home_url):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(home_url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count <= settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, list_news, home_url):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    response = client.get(home_url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    if object_list is not None:
        news_from_db = list(object_list)
        # Check if list_news is not None before sorting
        if list_news is not None:
            sorted_news = sorted(list_news,
                                 key=lambda x: x.pub_date
                                 if hasattr(x, 'pub_date')
                                 else x['pub_date'], reverse=True)
            assert sorted_news == news_from_db


def test_comments_order(client, list_comments, news_detail_url):
    """
    Комментарии на странице отдельной новости отсортированы в
    хронологическом порядке: старые в начале списка, новые — в конце.
    """
    response = client.get(news_detail_url)
    assert 'news' in response.context
    news_item = response.context['news']
    if hasattr(news_item, 'comment_set') and news_item.comment_set.exists():
        comments_from_db = list
        (news_item.comment_set.order_by('created').all())
        if list_comments is not None:
            comments_from_fixture = list(list_comments)
            assert comments_from_db == comments_from_fixture
