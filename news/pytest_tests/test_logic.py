import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, detail_news_url):
    """Анонимный пользователь не может отправить комментарий."""
    client.post(detail_news_url, data={'text': 'Текст'})
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author_client,
        author,
        news,
        detail_news_url
):
    """Авторизованный пользователь может отправить комментарий."""
    form_data = {'text': 'Текст комментария'}
    response = author_client.post(detail_news_url, data=form_data)
    assertRedirects(response, f'{detail_news_url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_user_cant_use_bad_words(author_client, detail_news_url):
    """Если в комментарии есть стоп-слова, он не будет создан."""
    bad_words_data = {'text': f'Текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_news_url, data=bad_words_data)
    assertFormError(response.context['form'], 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
        author_client,
        delete_comment_url,
        detail_news_url
):
    """Автор может удалить свой комментарий."""
    response = author_client.delete(delete_comment_url)
    assertRedirects(response, f'{detail_news_url}#comments')
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client,
        delete_comment_url
):
    """Пользователь не может удалить чужой комментарий."""
    comment_before = Comment.objects.get()
    response = not_author_client.delete(delete_comment_url)
    comment_after = Comment.objects.get()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    assert comment_after.text == comment_before.text
    assert comment_after.author_id == comment_before.author_id
    assert comment_after.news_id == comment_before.news_id


@pytest.mark.parametrize(
    'client_fixture, expected_status, new_text, check_text',
    (
        ('author_client', HTTPStatus.FOUND, 'Обновлённый текст', True),
        ('not_author_client', HTTPStatus.NOT_FOUND, 'Новый текст', False),
    )
)
def test_edit_comment(
        request,
        client_fixture,
        expected_status,
        new_text,
        check_text,
        comment,
        edit_comment_url,
        detail_news_url
):
    """Проверка возможности редактирования комментария автором / не автором."""
    client = request.getfixturevalue(client_fixture)
    comments_count_before = Comment.objects.count()
    response = client.post(edit_comment_url, data={'text': new_text})
    if expected_status == HTTPStatus.OK:
        assertRedirects(response, f'{detail_news_url}#comments')
    assert response.status_code == expected_status
    comment_from_db = Comment.objects.get(pk=comment.pk)
    assert Comment.objects.count() == comments_count_before
    if check_text:
        assert comment_from_db.text == new_text
    else:
        assert comment_from_db.text != new_text
