from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', lf('news_id_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
@pytest.mark.django_db
def test_pages_available_for_anonymous_users(client, name, args):
    """Тест доступности страниц для всех."""
    url = reverse(name, args=args)
    if 'logout' in name:
        response = client.post(url)
    else:
        response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'client, status',
    (
        (lf('author_client'), HTTPStatus.OK),
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_availability_for_comment_edit_and_delete(
    client,
    status,
    name,
    comment_id_for_args
):
    """Тест доступности редактирования и удаления комментариев."""
    url = reverse(name, args=comment_id_for_args)
    response = client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lf('comment_id_for_args')),
        ('news:delete', lf('comment_id_for_args')),
    )
)
@pytest.mark.django_db
def test_redirect_for_anonymous_client(name, args, client):
    """Тест перенаправления анонимного пользователя на страницу входа."""
    url = reverse(name, args=args)
    login_url = reverse('users:login')
    response = client.get(url)
    redirect_url = f'{login_url}?next={url}'
    assertRedirects(response, redirect_url)
