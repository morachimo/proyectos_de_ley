from django.utils.text import slugify
from haystack import indexes

from .models import Proyecto


class ProyectoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    codigo = indexes.CharField(model_attr='codigo', null=True)
    legislatura = indexes.CharField(model_attr='legislatura', null=True)
    numero_proyecto = indexes.CharField(model_attr='numero_proyecto', null=True)
    short_url = indexes.CharField(model_attr='short_url', null=True)
    congresistas = indexes.EdgeNgramField(model_attr='congresistas', null=True)
    titulo = indexes.EdgeNgramField(model_attr='titulo', null=True)
    titulo_de_ley = indexes.EdgeNgramField(model_attr='titulo_de_ley', null=True)
    numero_de_ley = indexes.CharField(model_attr='titulo_de_ley', null=True)

    def get_model(self):
        return Proyecto

    def prepare_text(self, obj):
        fields = [
            obj.codigo,
            str(obj.legislatura),
            obj.numero_proyecto,
            obj.short_url,
            obj.congresistas,
            obj.titulo,
            obj.titulo_de_ley,
            obj.numero_de_ley,
        ]
        data = [i for i in fields if i is not None]
        original = ' '.join(data)
        slugified = slugify(original)
        return ' '.join([original, slugified])
