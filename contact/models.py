from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.template.defaultfilters import slugify

from outil.imagekit.models import ProcessedImageField
from outil.imaging import Imaging


class ContactManager(models.Manager):

    def compte(self, request: int):
        return super(ContactManager,self).get_queryset().select_related("ContactModel").filter(client=request.user.id).values('id', 'pk',  "client",'objet_contact','email_contact','message_contact','nom_contact', 'categorie')[:10]

    def client(self, request):
        return super(ContactManager,self).get_queryset().filter(client=request.user.id,)
        #.values('id','pk',"client_email", 'objet_contact', 'email_contact','message_contact','nom_contact', 'categorie','client_email')[:10]

    def client_email(self, request):
        return super(ContactManager,self).get_queryset().filter(client_envoie=request.user.id)

    def messagerie_client(self, request, pk):
        return super(ContactManager,self).get_queryset().filter(client=request.user.id, pk=pk)

    def messagerie_client_envoie(self, request, pk):
        return super(ContactManager,self).get_queryset().filter(client_envoie=request.user.id,pk=pk )

    def message_client(self, request, pk):
        return super(ContactManager,self).get_queryset().filter(client=request.user.id, pk=pk)

    def message_client_envoie(self, request, pk):
        return super(ContactManager,self).get_queryset().filter(client_envoie=request.user.id,pk=pk )


class ContactModel(models.Model):
    id = models.AutoField(primary_key=True)
    slug = models.SlugField(default='', editable=False, max_length=15, null=False)
    date_add = models.DateTimeField(null=True, auto_now_add=True)
    email = models.EmailField(null=True, blank=True)
    categorie = models.CharField(null=True, blank=True, max_length=50)
    nom_contact = models.CharField(blank=True, max_length=50)
    email_contact = models.EmailField(blank=True, max_length=70)
    objet_contact = models.CharField(blank=True, null=True, max_length=50)
    message_contact = models.TextField(blank=True)
    client_envoie = models.IntegerField(null=False, blank=False, default="0")
    client = models.IntegerField(null=False, blank=False, default="0")
    mes_c = models.IntegerField(null=False, blank=False, default="0")
    mes_b = models.CharField(null=True, blank=True, max_length=10000)
    obj = ContactManager()

    class Meta:
        db_table = 'so_cont'
        ordering = ['-id']

    def __str__(self): return str(self.objet_contact)

    #def save(self, *args, **kwargs):
      #  self.slug = slugify(self.categorie)
       # super(ContactModel, self).save(*args, **kwargs)

    @cached_property
    def url_update_reception(self): return reverse('messagerie_categorie_reception', args=[ self.pk])

    @cached_property
    def url_update_envoie(self): return reverse('messagerie_categorie_envoie', args=[self.pk])


    @cached_property
    def url_signalement_envoie(self):
        return reverse('signalement_contact_envoie', args=[self.client_envoie])

    @cached_property
    def url_signalement_reception(self):
        return reverse('signalement_contact_reception', args=[self.client])


from django.db import models
class ContactAdminModel(models.Model):
    id = models.AutoField(primary_key=True)
    email_coucou = models.CharField(blank=True, max_length=250)
    texte_coucou = models.CharField(blank=True, max_length=250)
    objet_coucou = models.CharField(blank=True, null=True, max_length=50)
    connaissance_coucou = models.CharField(blank=True, null=True, max_length=12)
    langue = models.CharField(blank=True, null=True, max_length=3)
    client = models.IntegerField(null=False, blank=False, default="0")

    class Meta:
        db_table = 'sa_cona'

    def __str__(self): return str(self.objet_coucou) + str(self.pk)


class RachatManager:
    pass


class ContactRachatModel(models.Model):
    id = models.AutoField(primary_key=True)
    marque = models.CharField(blank=True, max_length=250)
    modele = models.CharField(blank=True, max_length=250)
    carnet = models.CharField(blank=True, max_length=250)
    facture = models.CharField(blank=True, max_length=250)
    cylindre = models.CharField(blank=True, max_length=250)
    annee = models.CharField(blank=True, max_length=250)
    km = models.CharField(blank=True, max_length=250)
    cle_rouge = models.CharField(blank=True, max_length=250)
    etat = models.CharField(blank=True, max_length=250)
    nom = models.CharField(blank=True, max_length=250)
    ville = models.CharField(blank=True, max_length=250)
    email = models.CharField(blank=True, max_length=250)
    estimation = models.CharField(blank=True, max_length=250)
    commentaire = models.CharField(blank=True, max_length=2000)
    phone = models.CharField(blank=True, max_length=2000)
    image1 = ProcessedImageField(blank=True, null=True, upload_to='rachat/',
                                 processors=[Imaging(300, 300, upscale=True), ],
                                 options={'quality': 70}, format='JPEG')

    image2 = ProcessedImageField(blank=True, null=True, upload_to='rachat/',
                                 processors=[Imaging(300, 300)],
                                 options={'quality': 70}, format='JPEG', )


    client = models.IntegerField(null=False, blank=False, default="0")

    obj = RachatManager()

    class Meta:
        db_table = 'sa_conr'

    def __str__(self): return str(self.modele)
