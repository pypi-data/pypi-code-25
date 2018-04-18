from django.db import models
from django.contrib.postgres.fields import JSONField


# Create your models here.
class Personas(models.Model):
    name = models.CharField(max_length=455, default='')
    active = models.BooleanField()
    inclusion_terms = JSONField(blank=True, null=True)
    exclusion_terms = JSONField(blank=True, null=True)

    class Meta:
        db_table = "personas"
        verbose_name_plural = 'Personas'

    def __str__(self):
        return self.name


class CpacRssFeeds(models.Model):
    url = models.CharField(max_length=255, default='')
    publication = models.CharField(max_length=255, default='')
    active = models.BooleanField()

    class Meta:
        db_table = '"cpac_rss_feeds"'
        verbose_name_plural = 'CpacRssFeeds'

    def __str__(self):
        return self.url


class PersonaPublicationJunction(models.Model):
    publication = models.CharField(max_length=100, default='')
    persona = models.ForeignKey('Personas', on_delete=models.CASCADE, null=True)
    rss_feed = models.ForeignKey('CpacRssFeeds', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "persona_publication_junction"
        verbose_name_plural = 'PersonaPublicationJunction'
        unique_together = (("publication", "persona", "rss_feed"),)

    def __str__(self):
        return self.publication


class FeederJobs(models.Model):
    cpac_num_articles = models.IntegerField()
    cpac_num_feed_articles = models.IntegerField()
    cpac_num_feeds = models.IntegerField()
    persona_num_articles_total = models.IntegerField()
    persona_num_feeds_articles = models.IntegerField()
    persona_num_feeds = models.IntegerField()
    job_types = models.CharField(max_length=30, default='')

    class Meta:
        db_table = "feeder_jobs"
        verbose_name_plural = 'FeederJobs'


class FeederProcessedArticlesUrls(models.Model):
    url = models.CharField(max_length=255, default='')
    job = models.ForeignKey('FeederJobs', on_delete=models.CASCADE, null=True)
    personas = models.ForeignKey('Personas', on_delete=models.CASCADE, null=True)
    rss_feed = models.ForeignKey('CpacRssFeeds', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "feeder_processed_articles_urls"
        verbose_name_plural = 'FeederProcessedArticlesUrls'
