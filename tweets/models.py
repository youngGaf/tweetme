import random
from django.db import models

# Create your models here.
class Tweet(models.Model):
    content = models.TextField(blank=True, null=True)
    image = models.FileField(upload_to='./image', blank=True, null=True)
    class Meta:
        ordering = ['-id']
        verbose_name = 'Tweet'
        verbose_name_plural = 'Tweets'

    def serialize(self):
        return {
            "id": self.id,
            "content": self.content,
            "likes": random.randint(0,10)
        }
