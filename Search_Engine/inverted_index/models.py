from django.db import models

class Token(models.Model):
    """Basic data struct of token and postings"""
    word = models.CharField(max_length=200, primary_key=True)
    path = models.CharField(max_length=2000)
    
    def __str__(self):
        """Return a string representation of the model"""
        return self.word

class Mapping(models.Model):
    """A mapping that from file name to URL"""
    file_name = models.CharField(max_length=20, primary_key=True)
    URL = models.CharField(max_length=2000)
    
    def __str__(self):
        """Return the URL"""
        return self.URL
