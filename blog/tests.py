from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from .models import Post


class TestPost(APITestCase):

    def setUpTestData(cls):
        cls.client = cls.client()
        self.url = reverse("config:test")  # temporary. would be changed to postviewset related url, later
        data = {
            'author': 3,
            'title': 'test',
            'content': 'random content',
            'post_tags': 'test django debugging'
        }

    def test_create_post(self):
        response = self.client.post(path=url, data=data, format='json')

