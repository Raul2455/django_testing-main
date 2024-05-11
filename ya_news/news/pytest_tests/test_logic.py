from http import HTTPStatus
from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client,
                                            new_text_comment, news_instance):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=(news_instance.id,))
    client.post(url, data=new_text_comment)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(author_client, author,
                                 new_text_comment, news_instance):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=(news_instance.id,))
    author_client.post(url, data=new_text_comment)
    assert Comment.objects.count() == 1
    comment_instance = Comment.objects.get()
    assert comment_instance.text == new_text_comment['text']
    assert comment_instance.news == news_instance
    assert comment_instance.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client,
                                 news_detail_url, bad_words_data):
    """
    Проверяем, что пользователь не может
    использовать запрещённые слова в комментариях.
    """
    response = author_client.post(news_detail_url, data=bad_words_data)
    # Проверяем, что сервер возвращает статус-код 302,
    # указывающий на перенаправление.
    assert response.status_code == 302


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, news_instance, comment):
    """Авторизованный пользователь может удалять свои комментарии."""
    news_url = reverse('news:detail', args=(news_instance.id,))
    url_to_comments = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(url_to_comments)
    assertRedirects(response, news_url + '#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    comment_url = reverse('news:delete', args=(comment.id,))
    response = admin_client.delete(comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, new_text_comment,
                                 news_instance, comment):
    """Авторизованный пользователь может редактировать свои комментарии."""
    news_url = reverse('news:detail', args=(news_instance.id,))
    comment_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(comment_url, data=new_text_comment)
    assertRedirects(response, news_url + '#comments')
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == new_text_comment['text']
    assert updated_comment.news == comment.news
    assert updated_comment.author == comment.author


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(admin_client,
                                                new_text_comment, comment):
    """
    Авторизованный пользователь не может редактировать чужие
    комментарии.
    """
    comment_url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(comment_url, data=new_text_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == comment.text
    assert updated_comment.news == comment.news
    assert updated_comment.author == comment.author
