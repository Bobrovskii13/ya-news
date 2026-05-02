import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news_id_for_args):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=news_id_for_args)
    client.post(url, data={'text': 'Текст'})
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, autor, news, news_id_for_args):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=news_id_for_args)
    form_data = {'text': 'Текст комментария'}
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == autor
    assert comment.news == news


def test_user_cant_use_bad_words(author_client, news_id_for_args):
    """Если в комментарии есть стоп-слова, он не будет создан."""
    url = reverse('news:detail', args=news_id_for_args)
    bad_words_data = {'text': f'Текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response.context['form'], 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
        author_client,
        comment_id_for_args,
        news_id_for_args
):
    """Автор может удалить свой комментарий."""
    url = reverse('news:delete', args=comment_id_for_args)
    news_url = reverse('news:detail', args=news_id_for_args)
    response = author_client.delete(url)
    assertRedirects(response, f'{news_url}#comments')
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client,
        comment_id_for_args
):
    """Пользователь не может удалить чужой комментарий."""
    url = reverse('news:delete', args=comment_id_for_args)
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
        author_client,
        comment,
        comment_id_for_args,
        news_id_for_args
):
    """Автор может редактировать свой комментарий."""
    url = reverse('news:edit', args=comment_id_for_args)
    news_url = reverse('news:detail', args=news_id_for_args)
    new_text = 'Обновлённый текст'
    response = author_client.post(url, data={'text': new_text})
    assertRedirects(response, f'{news_url}#comments')
    comment.refresh_from_db()
    assert comment.text == new_text


def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        comment,
        comment_id_for_args
):
    """Пользователь не может редактировать чужой комментарий."""
    url = reverse('news:edit', args=comment_id_for_args)
    response = not_author_client.post(url, data={'text': 'Новый текст'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != 'Новый текст'
