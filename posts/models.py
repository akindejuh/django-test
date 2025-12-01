from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Post(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
