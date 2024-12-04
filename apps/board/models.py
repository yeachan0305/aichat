from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name

class postdb(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField()
    body = models.TextField()
    imgUrl = models.TextField(null=True)
    date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    counting = models.IntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts' , default=1)

class Postlike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 추천한 사용자
    post = models.ForeignKey(postdb, on_delete=models.CASCADE)  # 추천한 게시글
    created_at = models.DateTimeField(auto_now_add=True)  # 추천 시간
    
    class Meta:
        unique_together = ('user', 'post')

class Comment(models.Model):
    post = models.ForeignKey(postdb, on_delete=models.CASCADE, related_name='comments', null=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    comment_body = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_datetime = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.comment_body