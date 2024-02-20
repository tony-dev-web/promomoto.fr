from functools import cached_property

from django.contrib.postgres.search import SearchVector
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.template.defaultfilters import slugify, date
from outil.imagekit.models import ProcessedImageField
from outil.imaging import Imaging


class VehiculeManager(models.Manager):

    def search(self, s, t):
        return super(VehiculeManager, self).get_queryset().annotate(
            search=(SearchVector('title', weight='A') + SearchVector('description', weight='B'))).filter(
            (Q(title__search=s) | Q(title__search=s) | Q(description__icontains=s) | Q(description__icontains=s)) & Q(
                type__icontains=t))

    def autocomplete(self, qs):
        return super(VehiculeManager, self).get_queryset().annotate(search=SearchVector('title')).filter(title__startswith=qs)

class VehiculeModel(models.Model):
    id = models.AutoField(primary_key=True)
    modele = models.CharField(max_length=150)
    marque = models.CharField(max_length=150)
    km = models.CharField(max_length=150)
    cylindre = models.CharField(max_length=150)
    etat = models.CharField(max_length=150)
    description = models.TextField(max_length=255)
    type = models.CharField(max_length=150)
    couleur = models.CharField(max_length=150)
    annee = models.CharField(max_length=150)
    slug = models.SlugField(null=False, unique=True)
    date_add = models.DateField(null=True, auto_now_add=True)
    date_update = models.DateField(null=True)
    signalement = models.IntegerField(null=True, blank=True, default="1")
    client = models.IntegerField(null=True, blank=True, default="0")
    vues = models.IntegerField(null=True, blank=True, default="0")
    title = models.CharField(max_length=3000)


    image1 = ProcessedImageField(blank=True, null=True, upload_to='vehicule/',
                                 processors=[Imaging(300, 300, upscale=True), ],
                                 options={'quality': 70}, format='JPEG')


    ia1 = models.CharField(null=True, blank=True,max_length=2000)
    ia2 = models.CharField(null=True, blank=True,max_length=2000)
    ia3 = models.CharField(null=True, blank=True,max_length=2000)
    ia4 = models.CharField(null=True, blank=True,max_length=2000)

    obj = VehiculeManager()

    def __str__(self):
        return self.marque

    class Meta:
        db_table = 'so_vehi'
        indexes = [models.Index(fields=["modele","marque","description"], )]
        ordering = ['-id']
        verbose_name = 'Vehicule'
        verbose_name_plural = 'Vehicules'

    @cached_property
    def url_frontend(self):
        return reverse('vehicule_url', args=[self.slug, self.pk])

    @cached_property
    def url_supression(self):
        return reverse('supression_vehicule', args=[ self.pk])

    def get_absolute_url(self):
        return reverse('vehicule_url', args=[self.slug,self.pk ])

    @cached_property
    def ville(self):
        return f'{ self.modele} {self.marque}'

    @cached_property
    def ville(self):
        return f'Par Promomoto'


    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(VehiculeModel, self).save(*args, **kwargs)