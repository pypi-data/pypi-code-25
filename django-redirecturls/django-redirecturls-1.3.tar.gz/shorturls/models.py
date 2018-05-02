from django.db import models


class Shorturls(models.Model):
    shortname = models.SlugField(max_length=100, unique=True)
    url = models.CharField(max_length=400, help_text="The URI to redirect to.")

    class Meta:
        ordering = ('shortname',)
        verbose_name = "Short URI"

    def __str__(self):
        return self.shortname


class Hit(models.Model):
    date = models.DateTimeField(auto_now_add=True, blank=True)
    url = models.ForeignKey(Shorturls, on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.date, self.url)

    class Meta:
        ordering = ('date', 'url', )
