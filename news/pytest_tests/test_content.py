import pytest
from django.conf import settings
from pytest_lazyfixture import lazy_fixture as lf

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_home_page(client, news_batch, home_url):
    """Тест отображения главной страницы с новостями (порядок и количество)."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() <= settings.NEWS_COUNT_ON_HOME_PAGE
    dates = [news.date for news in object_list]
    assert dates == sorted(dates, reverse=True)


def test_comments_order(client, news, comments_batch, detail_news_url):
    """Тест порядка комментариев: от старых к новым."""
    response = client.get(detail_news_url)
    all_comments = response.context['news'].comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    assert all_timestamps == sorted(all_timestamps)


@pytest.mark.parametrize(
    'parametrized_client, has_form',
    (
        (lf('client'), False),
        (lf('author_client'), True),
    ),
)
def test_client_has_form(parametrized_client, has_form, news, detail_news_url):
    """Анонимный клиент не видит форму, авторизованный — видит."""
    response = parametrized_client.get(detail_news_url)
    assert ('form' in response.context) is has_form
    if has_form:
        assert isinstance(response.context['form'], CommentForm)
