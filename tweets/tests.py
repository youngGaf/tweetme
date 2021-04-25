from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.test import TestCase
from .models import Tweet

# Create your tests here.

User = get_user_model()


class TweetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='gaf', password='gafar')
        self.user1 = User.objects.create(username='gaf1', password='gafar')
        Tweet.objects.create(content='my first tweet', user=self.user)
        Tweet.objects.create(content='my second tweet', user=self.user)
        Tweet.objects.create(content='my third tweet', user=self.user1)
        self.count = Tweet.objects.all().count()

    def get_client(self):
        client = APIClient()
        client.force_authenticate(self.user)
        return client

    def test_tweet_created(self):
        tweet_obj = Tweet.objects.create(content='my fourth tweet', user=self.user)
        self.assertEqual(tweet_obj.id, 4)
        self.assertEqual(tweet_obj.user, self.user)

    def test_tweet_list(self):
        client = self.get_client()
        response = client.get('/api/tweets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

    def test_action_like(self):
        client = self.get_client()
        response = client.post('/api/tweets/action/', {'id': 1, 'action': 'like'})
        self.assertEqual(response.status_code, 200)
        like_count = response.json().get('likes')
        self.assertEqual(like_count, 1)

    def test_action_unlike(self):
        client = self.get_client()
        response =  client.post('/api/tweets/action/', {'id': 1, 'action': 'like'})
        self.assertEqual(response.status_code, 200)
        response =  client.post('/api/tweets/action/', {'id': 1, 'action': 'unlike'})
        self.assertEqual(response.status_code, 200)
        like_count = response.json().get('likes')
        self.assertEqual(like_count, 0)

    def test_action_retweet(self):
        client = self.get_client()
        response = client.post('/api/tweets/action/', {'id': 1, 'action': 'retweet'})
        self.assertEqual(response.status_code, 200)
        tweet_id = response.json().get('id')
        self.assertEqual(self.count + 1, tweet_id)

    def test_tweet_create_view(self):
        data = {'content': 'This is my test tweet'}
        client = self.get_client()
        response = client.post('/api/tweets/create/', data)
        self.assertEqual(response.status_code, 201)
        tweet_id = response.json().get('id')
        self.assertEqual(self.count + 1, tweet_id)

    def test_tweet_detail_view(self):
        client = self.get_client()
        response = client.get('/api/tweets/1/')
        self.assertEqual(response.status_code, 200)
        tweet_id = response.json().get('id')
        self.assertEqual(tweet_id, 1)

    def test_tweet_delete_view(self):
        client = self.get_client()
        response = client.delete('/api/tweets/1/delete/')
        self.assertEqual(response.status_code, 200)
        client = self.get_client()
        response = client.delete('/api/tweets/1/delete/')
        self.assertEqual(response.status_code, 404)
        response = client.delete('/api/tweets/3/delete/')
        self.assertEqual(response.status_code, 401)