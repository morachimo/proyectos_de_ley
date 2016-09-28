from functools import partial

from django import forms

from pdl.models import Proyecto
from pdl.models import Slug


DateInput1 = partial(forms.DateInput, {'class': 'datepicker form-control',
                                       'placeholder': 'Fecha inicio'})
DateInput2 = partial(forms.DateInput, {'class': 'datepicker form-control',
                                       'placeholder': 'Fecha fin'})


class SearchAdvancedForm(forms.Form):
    query = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Palabra de búsqueda',
        }),
        required=False,
    )
    date_from = forms.DateField(
        widget=DateInput1(),
        label="Fecha inicio",
        required=False,
        error_messages={'invalid': 'Ingrese fecha válida'},
    )
    date_to = forms.DateField(
        widget=DateInput2(),
        label="Fecha fin",
        required=False,
        error_messages={'invalid': 'Ingrese fecha válida'},
    )
    comision = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Comisión',
        required=False,
        choices=[
            ('---', '---'),
            ('Agraria', 'Agraria'),
            ('Ciencia', 'Ciencia'),
            ('Comercio Exterior', 'Comercio Exterior'),
            ('Constitución', 'Constitución'),
            ('Cultura', 'Cultura'),
            ('Defensa del Consumidor', 'Defensa del Consumidor'),
            ('Defensa Nacional', 'Defensa Nacional'),
            ('Descentralización', 'Descentralización'),
            ('Economía', 'Economía'),
            ('Educación', 'Educación'),
            ('Energía', 'Energía'),
            ('Fiscalización', 'Fiscalización'),
            ('Inclusión Social', 'Inclusión Social'),
            ('Inteligencia', 'Inteligencia'),
            ('Justicia', 'Justicia'),
            ('Mujer', 'Mujer'),
            ('Presupuesto', 'Presupuesto'),
            ('Producción Micro', 'Producción Micro'),
            ('Pueblos Andinos', 'Pueblos Andinos'),
            ('Relaciones Exteriores', 'Relaciones Exteriores'),
            ('Salud', 'Salud'),
            ('Trabajo', 'Trabajo'),
            ('Transportes', 'Transportes'),
            ('Vivienda', 'Vivienda'),
        ]
    )
    congresista = forms.ModelChoiceField(
        Slug.objects.all().order_by('nombre'),
        label='Búsqueda por author de proyecto de ley.',
        required=False,
        empty_label='--Escoger nombre--',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    tmp = Proyecto.objects.filter(
        grupo_parlamentario__isnull=False).exclude(
        grupo_parlamentario='').values_list(
        'grupo_parlamentario', flat=True).order_by('grupo_parlamentario').distinct()
    choices = [('--Escoger bancada--', '--Escoger bancada--',)]
    for i in tmp:
        choices.append((i, i,))
    grupo_parlamentario = forms.ChoiceField(
        choices=choices,
        label='Búsqueda por grupo parlamentario.',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    dispensados_2da_votacion = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Dispensados 2da votación',
        required=False,
        choices=[
            ('---', '---'),
            ('TOTAL dispensados', 'TOTAL dispensados'),
            ('NÚMERO TOTAL DE LEYES', 'NÙMERO TOTAL DE LEYES'),
            ('TOTAL aprobados', 'TOTAL aprobados'),
            ('Dispensados por acuerdo del pleno', 'Dispensados por acuerdo del pleno'),
            ('Dispensados por junta portavoces', 'Dispensados por junta portavoces'),
            ('Otros proyectos dispensados', 'Otros proyectos dispensados'),
        ]
    )
    dictamen = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Dictamen',
        required=False,
        choices=[
            ('---', '---'),
            ('NÚMERO TOTAL DE LEYES', 'NÙMERO TOTAL DE LEYES'),
            ('Exonerados de dictamen', 'Exonerados de dictamen'),
        ]
    )
