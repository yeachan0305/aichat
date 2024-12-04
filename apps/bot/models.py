from django.contrib.auth.models import User
from django.db import models
from PIL import Image

class Botcategory(models.Model):
    name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name

# Create your models here.
class bots(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    descript = models.TextField()
    firstMessage = models.TextField()
    comment = models.TextField()
    botImg = models.ImageField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Botcategory, on_delete=models.CASCADE, related_name='bots' , default=3)

    def crop_image(self):
        """이미지를 1:1 비율로 중앙에서 크롭하는 메서드"""
        if self.botImg:
            img_path = self.botImg.path
            img = Image.open(img_path)
            width, height = img.size
            new_size = min(width, height)

            # 중앙 크롭 영역 계산
            left = (width - new_size) / 2
            top = (height - new_size) / 2
            right = (width + new_size) / 2
            bottom = (height + new_size) / 2

            # 이미지 크롭
            img_cropped = img.crop((left, top, right, bottom))

            # 크롭된 이미지 저장
            img_cropped.save(img_path)