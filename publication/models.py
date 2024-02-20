from functools import cached_property

from django.db import models
from datetime import datetime, date, timedelta

from django.urls import reverse

from outil.imagekit.models import ProcessedImageField
from outil.imaging import Imaging


class PublicationManager(models.Manager):

    def compte(self, request: int):
        return super(PublicationManager, self).get_queryset().filter(client=request.user.id)


class PublicationModel(models.Model):
    id = models.AutoField(primary_key=True)
    publication = models.TextField(max_length=255)
    date_add = models.DateField(null=True, auto_now_add=True)
    signalement = models.IntegerField(null=True, blank=True, default="1")
    client = models.IntegerField(null=True, blank=True, default="0")
    vues = models.IntegerField(null=True, blank=True, default="0")

    image1 = ProcessedImageField(blank=True, null=True, upload_to='publication/',
                                 processors=[Imaging(300, 300, upscale=True), ],
                                 options={'quality': 70}, format='JPEG')

    ia1 = models.CharField(null=True, blank=True,max_length=2000)
    ia2 = models.CharField(null=True, blank=True,max_length=2000)
    ia3 = models.CharField(null=True, blank=True,max_length=2000)
    ia4 = models.CharField(null=True, blank=True,max_length=2000)

    obj = PublicationManager()

    def __str__(self):
        return self.publication

    class Meta:
        db_table = 'so_publ'
        # default_related_name = 'AnnonceModel'
        indexes = [models.Index(fields=["publication"], )]
        ordering = ['-id']
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'

    @cached_property
    def url_supression(self):
        return reverse('supression_publication', args=[self.pk])

    @cached_property
    def url_signalement(self):
        return reverse('signalement_publication',args=[self.pk])
