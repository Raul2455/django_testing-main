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
def test_comment_form_availability(parametrized_client,
                                   status, news_detail_url):
    """
    Проверка доступности формы для отправки комментария:
    - анонимному пользователю форма недоступна;
    - авторизованному пользователю форма доступна.
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
    news_from_db = list(object_list)
    # Используем поле 'date' из модели News
    sorted_news = sorted(
        news_from_db,
        key=lambda x: x.date,
        reverse=True
    )
    assert sorted_news == news_from_db


def test_comments_order(client, news_detail_url):
    """
    Комментарии на странице отдельной новости отсортированы в
    хронологическом порядке: старые в начале списка, новые — в конце.
    """
    response = client.get(news_detail_url)
    assert 'news' in response.context
    news_item = response.context['news']
    comments_from_db = list(news_item.comment_set.all())
    sorted_comments = sorted(
        comments_from_db,
        key=lambda x: x.created
    )
    assert comments_from_db == sorted_comments
