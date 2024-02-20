from django.db import models


class MotardManager(models.Manager):

    def compte(self, request):
        return super(MotardManager, self).get_queryset().filter(client=request.user.id)


class MotardModel(models.Model):
    id = models.AutoField(primary_key=True)


    client = models.IntegerField(null=True, blank=True, default="0")

    surnom = models.CharField(null=True, blank=True, max_length=150)
    nom = models.CharField(null=True, blank=True, max_length=150)
    prenom = models.CharField(null=True, blank=True, max_length=150)
    societe = models.CharField(null=True, blank=True, max_length=150)
    adresse = models.CharField(null=True, blank=True, max_length=150)
    code_postale = models.CharField(null=True, blank=True, max_length=6)
    ville = models.CharField(blank=True, max_length=50, null=True)

    role = models.CharField(blank=True, null=True, max_length=20)
    obj = MotardManager()

    def __str__(self):
        return self.client

    class Meta:
        db_table = 'so_mota'
        ordering = ['id']
        verbose_name = 'motard'
        verbose_name_plural = 'motards'


    def save(self, *args, **kwargs):
        super(MotardModel, self).save(*args, **kwargs)