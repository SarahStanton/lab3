from django.db import models
from django.utils import timezone

class URL(models.Model):
	finalDestination = models.URLField(null=True)
	originalURL = models.URLField(null=True)
	statusCode = models.CharField(max_length=3)
	title = models.CharField(default="", max_length=100)
	
	def __str__(self):
		return self.originalURL 

