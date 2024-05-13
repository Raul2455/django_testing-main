import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

BAD_WORDS_COMMENT = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client,
                                            new_text_comment, news_detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    client.post(news_detail_url, data=new_text_comment)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(author_client, author,
                                 new_text_comment,
                                 news_detail_url, news_instance):
    """Авторизованный пользователь может отправить комментарий."""
    author_client.post(news_detail_url, data=new_text_comment)
    assert Comment.objects.count() == 1
    comment_instance = Comment.objects.get()
    assert comment_instance.text == new_text_comment['text']
    assert comment_instance.news == news_instance
    assert comment_instance.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news_detail_url):
    """
    Если комментарий содержит запрещённые слова, он не будет
    опубликован, а форма вернёт ошибку.
    """
    response = author_client.post(news_detail_url, data=BAD_WORDS_COMMENT)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, news_detail_url, comment):
    """Авторизованный пользователь может удалять свои комментарии."""
    url_to_comments = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(url_to_comments)
    assertRedirects(response, news_detail_url + '#comments')
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
                                 news_detail_url, comment):
    """Авторизованный пользователь может редактировать свои комментарии."""
    comment_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(comment_url, data=new_text_comment)
    assertRedirects(response, news_detail_url + '#comments')
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
