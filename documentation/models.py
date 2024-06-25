from django.db import models
# traduction en lazy car les traductions
# doivent être résolues au moment où les champs sont affichés,
# et non au moment où le modèle est chargé.
from django.utils.translation import gettext_lazy as _


class Document(models.Model):
    # introduction du ugettext_lazy as _ pour (i18n)
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    content = models.TextField(verbose_name=_("Content"))
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name=_("Updated At"))

    def __str__(self):
        return self.title
