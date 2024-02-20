from django.db import models


class MessageManager(models.Manager):

    def message_client(self, request):
        return super(MessageManager,self).get_queryset().filter(client=request.user.id)

    def message_client_envoie(self, request):
        return super(MessageManager,self).get_queryset().filter(client_envoie=request.user.id)


class MessageModel(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.IntegerField(null=False, blank=False, default="0")
    categorie = models.CharField(null=True, blank=True, max_length=50)

    langue = models.CharField(blank=True, null=True, default="0", max_length=3)
    date_add = models.DateTimeField(null=True, auto_now_add=True)
    client_envoie = models.IntegerField(null=False, blank=False, default="0")
    client = models.IntegerField(null=False, blank=False, default="0")
    message = models.CharField(null=True, blank=True, max_length=50)

    mes_c = models.IntegerField(null=False, blank=False, default="0")
    mes_b = models.CharField(null=True, blank=True, max_length=10000)

    obj = MessageManager()

    class Meta:
        db_table = 'so_mess'
        default_related_name = 'MessageManager'
        ordering = ['id']
        verbose_name = 'messagerie'
        verbose_name_plural = 'messagerie'



    def __str__(self): return str(self.message)







