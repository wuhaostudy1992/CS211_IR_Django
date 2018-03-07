from django.db import models

class Token(models.Model):
    """A topic the user is learning about"""
    word = models.CharField(max_length=200, primary_key=True)
    path = models.CharField(max_length=2000)
    
    def __str__(self):
        """Return a string representation of the model"""
        return self.word
