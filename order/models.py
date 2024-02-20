from django.db import models
from django.shortcuts import redirect
#from order.views import PaymentOk, PaymentCancelled
#from order.views import PaymentOk, PaymentCancelled


#from payplug_dj.models import Payment
from payplug_dj.signals import payment_return
from payplug_dj.signals import payment_cancel

class OrderManager(models.Manager):

    def search(self):
        return super(OrderManager, self).get_queryset().filter()

class OrderModel(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.IntegerField(null=True, blank=True, default="0")
    nom = models.CharField(null=True, blank=True,max_length=150)
    prenom = models.CharField(null=True, blank=True,max_length=150)
    societe = models.CharField(null=True, blank=True,max_length=150)
    adresse = models.CharField(null=True, blank=True,max_length=150)
    code_postale = models.CharField(null=True, blank=True,max_length=6)
    ville = models.CharField(blank=True, max_length=50, null=True)
    #product_id = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    #total_ht = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)

    date_add = models.DateField(null=True, auto_now_add=True)
    email = models.CharField(max_length=150)
    phone = models.CharField(null=True,blank=True, max_length=12)
    commentaire = models.TextField(null=True, blank=True,max_length=2000)
    moto = models.CharField(null=True, blank=True,max_length=150)

    products = models.CharField(null=True, blank=True, max_length=150)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    stock = models.CharField(null=True, blank=True, max_length=150)
    session = models.CharField(blank=True, max_length=100, null=True)
    payment = models.CharField(null=True, blank=True, max_length=150)

    expedition = models.CharField(null=True, blank=True,max_length=150)

    obj = OrderManager()


    def __str__(self):
        return self.nom

    class Meta:
        db_table = 'so_orde'
        ordering = ['-id']
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'



    #def save(self, *args, **kwargs):
        #post_save.connect(self.paiement_promomoto, sender=Payment)
       # super(OrderModel, self).save(*args, **kwargs)




