from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture as lf


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, method',
    (
        (lf('home_url'), 'get'),
        (lf('detail_news_url'), 'get'),
        (lf('login_url'), 'get'),
        (lf('logout_url'), 'post'),
        (lf('signup_url'), 'get'),
    )
)
def test_pages_available_for_anonymous_users(
        client,
        url,
        method,
):
    """Тест доступности страниц для всех."""
    response = getattr(client, method)(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, status',
    (
        (lf('author_client'), HTTPStatus.OK),
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('client'), HTTPStatus.FOUND),
    )
)
@pytest.mark.parametrize(
    'url',
    (
        lf('edit_comment_url'),
        lf('delete_comment_url'),
    ),
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client,
    status,
    url,
    login_url
):
    """Тест доступности редактирования, удаления комментариев."""
    response = parametrized_client.get(url)
    assert response.status_code == status
    if status == HTTPStatus.FOUND:
        expected_redirect = f'{login_url}?next={url}'
        assert response.url == expected_redirect
