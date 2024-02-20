from django.contrib.postgres.search import SearchVector
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import translation
from datetime import datetime, date, timedelta
from functools import cached_property

from outil.imagekit.models import ProcessedImageField
from outil.imaging import Imaging


class AnnonceManager(models.Manager):

    def search(self, s,t):
        return super(AnnonceManager, self).get_queryset().annotate(search=( SearchVector('title', weight='A') + SearchVector('description', weight='B'))).filter(
        (Q(title__search=s) | Q(description__search=s) | Q(title__icontains=s) | Q(description__icontains=s) | Q(ville__search=s) | Q(ville__icontains=s) ) & Q(type__icontains=t),date_end__gte=date.today())

    def compte(self, request: int):
        return super(AnnonceManager, self).get_queryset().filter(client=request.user.id)

    def autocomplete(self, qs):
        return super(AnnonceManager, self).get_queryset().annotate(search=SearchVector('title')).filter(title__startswith=qs)




class AnnonceModel(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.IntegerField(null=True, blank=True, default="0")
    title = models.CharField(null=True, max_length=150)
    etat = models.CharField(null=True,max_length=150)
    description = models.TextField(null=True,max_length=2000)
    prix = models.DecimalField(max_digits=12, decimal_places=2,default=0, null=True, blank=True)
    slug = models.SlugField(null=False, unique=True)
    date_add = models.DateField(null=True, auto_now_add=True)
    date_update = models.DateField(null=True)
    date_end = models.DateField(null=True)
    marque = models.CharField(blank=True, max_length=50, null=True)
    type = models.CharField(blank=True, max_length=50, null=True)
    phone = models.CharField(blank=True, max_length=12, null=True)
    ville = models.CharField(blank=True, max_length=50, null=True)
    signalement = models.IntegerField(null=True, blank=True, default="0")
    vues = models.IntegerField(null=True, blank=True, default="0")

    image1 = ProcessedImageField(blank=True, null=True, upload_to='annonce/',
                                 processors=[Imaging(300, 300, upscale=True), ],
                                 options={'quality': 70}, format='JPEG')

    image2 = ProcessedImageField(blank=True, null=True, upload_to='annonce/',
                                 processors=[Imaging(300, 300)],
                                 options={'quality': 70}, format='JPEG', )

    image3 = ProcessedImageField(blank=True, null=True, upload_to='annonce/',
                                 processors=[Imaging(300, 300)],
                                 options={'quality': 70}, format='JPEG', )

    image4 = ProcessedImageField(blank=True, null=True, upload_to='annonce/',
                                 processors=[Imaging(300, 300)],
                                 options={'quality': 70}, format='JPEG', )


    ia1 = models.CharField(null=True, blank=True,max_length=2000)
    ia2 = models.CharField(null=True, blank=True,max_length=2000)
    ia3 = models.CharField(null=True, blank=True,max_length=2000)
    ia4 = models.CharField(null=True, blank=True,max_length=2000)

    ia5 = models.CharField(null=True, blank=True,max_length=2000)
    ia6 = models.CharField(null=True, blank=True,max_length=2000)
    ia7 = models.CharField(null=True, blank=True,max_length=2000)
    ia8 = models.CharField(null=True, blank=True,max_length=2000)
    ia9 = models.CharField(null=True, blank=True, max_length=2000)


    obj = AnnonceManager()

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'so_anno'
        indexes = [models.Index(fields=["title", "description"], )]
        ordering = ['-id']
        verbose_name = 'Annonce'
        verbose_name_plural = 'Annonces'

    @cached_property
    def url_frontend(self):
        return reverse('annonce_url', args=[self.client, self.slug, self.pk])

    @cached_property
    def url_supression(self):
        return reverse('supression_annonce',args=[self.pk])


    @cached_property
    def url_signalement(self):
        return reverse('signalement_annonce',args=[self.pk])

    @cached_property
    def url_update(self): return reverse('update_annonce', args=[self.pk])

    @cached_property
    def robots_url(self):
        return f'rel="nofollow"'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        self.date_end = (date.today() + timedelta(90))
        super(AnnonceModel, self).save(*args, **kwargs)
