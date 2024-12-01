# models.py
from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown
import os

class Product(models.Model):  
    name = models.CharField(max_length=30) 
    image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)
    like = models.IntegerField()
    dislike = models.IntegerField()
    keyword = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)      
    updated_at = models.DateTimeField(auto_now=True)         
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'[{self.pk}]{self.name} :: {self.author}'

    def get_absolute_url(self):
        return f'/project/{self.pk}/'
    
    def get_file_name(self):
        return os.path.basename(self.file_upload.name)
    
    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]
    
    def get_content_markdown(self):
        return markdown(self.content)

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return f"https://doitdjango.com/avatar/id/131/83a0315115dc3c15/svg/{self.author.email}"

