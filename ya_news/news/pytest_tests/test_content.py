import pytest
from django.conf import settings
from django.urls import reverse


from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client):  # Удалено 'list_news' из аргументов
    """Количество новостей на главной странице — не более 10."""
    url = reverse('news:home')
    response = client.get(url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count <= settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, list_news):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    url = reverse('news:home')
    response = client.get(url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    all_news = list(object_list)
    sorted_news = sorted(all_news, key=lambda x: x.date, reverse=True)
    assert sorted_news == list_news


def test_comments_order(client, news, list_comments):
    """
    Комментарии на странице отдельной новости отсортированы
    по дате создания (от старых к новым).
    """
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news_obj = response.context['news']
    comments = list(news_obj.comment_set.order_by('created'))
    assert comments == list_comments


@pytest.mark.parametrize(
    'parametrized_client, status, expected_form_class',
    (
        (pytest.lazy_fixture('client'), False, None),
        (pytest.lazy_fixture('author_client'), True, CommentForm)
    ),
)
def test_anonymous_client_has_no_form(parametrized_client, status,
                                      expected_form_class, comment):
    """
    Анонимному пользователю недоступна форма для отправки
    комментария. Авторизованному пользователю доступна форма.
    """
    url = reverse('news:detail', args=(comment.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is status
    if status:
        assert isinstance(response.context['form'], expected_form_class)
