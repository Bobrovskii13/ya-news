import pytest
from django.conf import settings
from django.urls import reverse
from pytest_lazyfixture import lazy_fixture as lf

from news.forms import CommentForm


@pytest.mark.django_db
def test_home_page(client, news_batch):
    """Тест отображения главной страницы с новостями (порядок и количество)."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE
    dates = [news.date for news in object_list]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(client, news, comments_batch):
    """Тест порядка комментариев: от старых к новым."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news_obj = response.context['news']
    all_comments = news_obj.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    assert all_timestamps == sorted(all_timestamps)


@pytest.mark.parametrize(
    'parametrized_client, has_form',
    (
        (lf('client'), False),
        (lf('author_client'), True),
    ),
)
@pytest.mark.django_db
def test_client_has_form(parametrized_client, has_form, news_id_for_args):
    """Анонимный клиент не видит форму, авторизованный — видит."""
    url = reverse('news:detail', args=news_id_for_args)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is has_form
    if has_form:
        assert isinstance(response.context['form'], CommentForm)
