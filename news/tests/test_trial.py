import unittest

from django.test import TestCase

from news.models import News


class TestNews(TestCase):

    TITLE = 'Заголовок новости'
    TEXT = 'Тестовый текст'

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
        )

    @unittest.skip('Пропущен тренировочный тест.')
    def test_successful_creation(self):
        news_count = News.objects.count()
        self.assertEqual(news_count, 1)

    @unittest.skip('Пропущен тренировочный тест.')
    def test_title(self):
        self.assertEqual(self.news.title, self.TITLE)

    @unittest.skip('Пропущен тренировочный тест.')
    def test_text(self):
        self.assertEqual(self.news.text, self.TEXT)
