from datetime import timedelta

import pytest
from django.test.client import Client
from django.utils import timezone

from news.models import News
from yanews import settings


@pytest.fixture
def autor(django_user_model):
    """Автор комментария."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Пользователь, не являющийся автором комментария."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(autor):
    """Авторизованный клиент."""
    client = Client()
    client.force_login(autor)
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

    News.objects.bulk_create([
        News(
            title=f'Новость {index}',
            text='Текст',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ])


@pytest.fixture
def news_id_for_args(news):
    """ID новости для передачи в аргументы."""
    return (news.id,)


@pytest.fixture
def comment(news, autor):
    """Комментарий к новости."""
    return news.comment_set.create(
        news=news,
        author=autor,
        text='Текст комментария'
    )


@pytest.fixture
def comments_batch(news, autor):
    """Набор комментариев к новости."""
    now = timezone.now()
    comments = []
    for index in range(10):
        comment = news.comment_set.create(
            news=news,
            author=autor,
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
