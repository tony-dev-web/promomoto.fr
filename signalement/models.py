from django.db import models

class SignalementModel(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.IntegerField(blank=True, null=True, default=0)
    client_signalement = models.IntegerField(blank=True, null=True, default=0)
    objet = models.CharField(blank=True, max_length=50)
    description = models.TextField(blank=True, max_length=250)
    date_add = models.DateTimeField(null=True, auto_now_add=True)

    class Meta:
        db_table = 'so_sign'

    def __str__(self): return str(self.pk)