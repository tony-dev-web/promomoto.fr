from publication.models import PublicationModel
from signalement.views import SignalementView, DeleteView

class publication_delete(DeleteView):
    model = PublicationModel
    title = 'publication'

class publication_signalement(SignalementView):
    model = PublicationModel