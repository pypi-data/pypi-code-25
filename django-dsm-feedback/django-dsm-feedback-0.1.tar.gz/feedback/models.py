from django.db import models

# Create your models here.
class Feedback(models.Model):
    rating = models.IntegerField(default=0)
    feedback = models.TextField(default="", blank=True)
    email = models.EmailField(default="", blank=True)
    page = models.CharField(default="/", max_length=500)
    def __str__(self):
        return "[{rating}]: {page}\t{text}".format(rating=self.rating, text=self.feedback[0:50], page=self.page)
