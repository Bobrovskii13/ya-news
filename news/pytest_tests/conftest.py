from datetime import timedelta

import pytest
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import News
from yanews import settings


@pytest.fixture
def author(django_user_model):
    """Автор комментария."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Пользователь, не являющийся автором комментария."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Авторизованный клиент."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Авторизованный клиент, не являющийся автором комментария."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Новость."""
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def news_batch(db):
    """Набор новостей."""
    today = timezone.now().date()

    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comment(news, author):
    """Комментарий к новости."""
    return news.comment_set.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def comments_batch(news, author):
    """Набор комментариев к новости."""
    now = timezone.now()
    comments = []
    for index in range(10):
        comment = news.comment_set.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments.append(comment)
    return comments


@pytest.fixture
def comment_id_for_args(comment):
    """ID комментария для передачи в аргументы."""
    return (comment.id,)


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def detail_news_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_comment_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_comment_url(comment):
    return reverse('news:delete', args=(comment.id,))
