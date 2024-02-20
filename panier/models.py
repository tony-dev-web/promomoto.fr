from functools import cached_property
from django.db import models
from django.urls import reverse

class PanierManager(models.Manager):

    def search(self):
        return super(PanierManager, self).get_queryset().filter()


class PanierModel(models.Model):
    client = models.IntegerField(null=True, blank=True, default="0")
    #product = models.ForeignKey(ProductModel, on_delete=models.SET_NULL, null=True)
    pr_id = models.IntegerField(null=True, blank=True, default="0")
    session = models.CharField(blank=True, max_length=100, null=True)
    payment = models.CharField(null=True, blank=True, max_length=150)
    obj = PanierManager()

    class Meta:
        db_table = 'so_pani'
        ordering = ['-id']
        verbose_name = 'Panier'
        verbose_name_plural = 'Paniers'

    @cached_property
    def url_supression_panier(self):
        return reverse('supression_panier', args=[self.session])
