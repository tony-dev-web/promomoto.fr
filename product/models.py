from django.contrib.postgres.search import SearchVector
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.urls import reverse
from functools import cached_property

from outil.imagekit.models import ProcessedImageField
from outil.imaging import Imaging
from vehicule.models import VehiculeModel


class ProductManager(models.Manager):

    def search(self, s,t):
        return super(ProductManager, self).get_queryset().annotate(
            search=(SearchVector('title', weight='A') + SearchVector('description', weight='B'))).filter(
            (Q(title__search=s) | Q(description__search=s) | Q(title__icontains=s) | Q(description__icontains=s)| Q(categorie__icontains=s) | Q(categorie__search=s)) & Q(type__icontains=t))

    def autocomplete(self, qs):
        return super(ProductManager, self).get_queryset().annotate(search=SearchVector('title')).filter(title__startswith=qs)


class ProductModel(models.Model):
    id = models.AutoField(primary_key=True)
    vehicule = models.ForeignKey(VehiculeModel, null=True, blank=True, on_delete=models.CASCADE)
    vp_id = models.IntegerField(null=True, blank=True, default="0")

    client = models.IntegerField(null=True, blank=True, default="0")
    title = models.CharField(max_length=150)
    description = models.TextField(max_length=255)
    prix = models.DecimalField(max_digits=12, decimal_places=2,default=0, null=True, blank=True)
    euros = models.CharField(blank=True, max_length=20)
    stock = models.IntegerField(null=True, blank=True, default="1")
    slug = models.SlugField(null=False, unique=True)
    reference = models.CharField(max_length=150)
    etat = models.CharField(max_length=150, default="Bon etat")
    rangement = models.CharField(max_length=150)
    vendu = models.CharField(max_length=150)
    date_add = models.DateField(null=True, auto_now_add=True)
    date_update = models.DateField(null=True)
    signalement = models.IntegerField(null=True, blank=True, default="1")
    marque = models.CharField(blank=True, max_length=50, null=True)
    modele = models.CharField(blank=True, max_length=150, null=True)

    categorie = models.CharField(blank=True, max_length=150, null=True)
    type = models.CharField(blank=True, max_length=50, null=True)
    vues = models.IntegerField(null=True, blank=True, default="0")


    image1 = ProcessedImageField(blank=True, null=True, upload_to='piece/',
                                 processors=[Imaging(300, 300, upscale=True), ],
                                 options={'quality': 70}, format='JPEG')

    image2 = ProcessedImageField(blank=True, null=True, upload_to='piece/',
                                 processors=[Imaging(300, 300)],
                                 options={'quality': 70}, format='JPEG', )

    image3 = ProcessedImageField(blank=True, null=True, upload_to='piece/',
                                 processors=[Imaging(300, 300)],
                                 options={'quality': 70}, format='JPEG', )

    image4 = ProcessedImageField(blank=True, null=True, upload_to='piece/',
                                 processors=[Imaging(300, 300)],
                                 options={'quality': 70}, format='JPEG', )

    ia1 = models.CharField(null=True, blank=True,max_length=2000)
    ia2 = models.CharField(null=True, blank=True,max_length=2000)
    ia3 = models.CharField(null=True, blank=True,max_length=2000)
    ia4 = models.CharField(null=True, blank=True,max_length=2000)

    obj = ProductManager()



    def __str__(self):
        return self.title

    class Meta:
        db_table = 'so_prod'
        # default_related_name = 'AnnonceModel'
        indexes = [models.Index(fields=["title", "description"], )]
        ordering = ['-id']
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'

    @cached_property
    def url_frontend(self):
        return reverse('product_url', args=[ self.slug, self.pk])

    @cached_property
    def url_supression(self):
        return reverse('supression_product', args=[self.client, self.pk])

    @cached_property
    def url_order_add(self):
        return reverse('order_add', args=[self.pk])

    def get_absolute_url(self):
        return reverse('product_url', args=[self.slug,self.pk ])


    @cached_property
    def def_stock(self):
        if self.stock in [0, None]:
                return f'<span class="c3">Vendu</span>'
        elif self.stock in list(range(1,1000)):
                return f'<span class="c4">En stock</span>'


    @cached_property
    def ville(self):
            return f'Par Promomoto'


    def save(self, *args, **kwargs):
        #self.slug = self.slug = slugify(f'{self.title} {self.marque} ')
        self.slug = slugify(self.title)
        super(ProductModel, self).save(*args, **kwargs)



