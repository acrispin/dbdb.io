# stdlib imports
# django imports
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django import forms
from django.forms.fields import MultipleChoiceField
from django.forms import widgets
from django.forms.widgets import Textarea
# project imports
from dbdb.core.models import CitationUrl
from dbdb.core.models import Feature
from dbdb.core.models import FeatureOption
from dbdb.core.models import System
from dbdb.core.models import SystemVersion
from dbdb.core.models import SystemVersionMetadata


# fields

class TagFieldM2M(MultipleChoiceField):

    widget = forms.TextInput(attrs={'data-role': 'tagsinput', 'placeholder': ''})

    def prepare_value(self, value):
        try:
            return ','.join([x.url for x in value])
        except (AttributeError, TypeError):
            if value is not None:
                return value.split(',')
            return ''

    def clean(self, value):
        if value:
            urls = value.split(',')
        else:
            urls = []
        url_objs = []
        for url in urls:
            cit_url, _ = CitationUrl.objects.get_or_create(url=url)
            url_objs.append(cit_url)
        return url_objs
    
    pass


# forms

class AdvancedSearchForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(AdvancedSearchForm, self).__init__(*args, **kwargs)
        features = Feature.objects.all()

        for feature in features:
            self.fields[feature.label] = forms.MultipleChoiceField(
                choices=(
                    (x, x) for x in FeatureOption.objects.filter(feature=feature)
                ), required=False
            )
        return
    
    pass

class SystemFeaturesForm(forms.Form):

    def __init__(self, *args, **kwargs):
        try:
            features = kwargs.pop('features')
        except KeyError:
            features = []

        super(SystemFeaturesForm, self).__init__(*args, **kwargs)

        initial = {}

        for feature in features:
            o = feature.options.values_list('value', flat=True)
            if len(o) > 1:
                o = list(o)
            elif len(o) == 1:
                o = o[0]
            else:
                o = None
            initial[feature.feature.label] = {
                'options': o,
                'description': feature.description,
                'citations': ','.join(feature.citations.values_list('url', flat=True))
            }
            pass

        features = Feature.objects.all()

        self.features = []
        for feature in features:
            initial_value = None
            if feature.multivalued:
                if feature.label in initial:
                    initial_value = initial[feature.label]['options']
                self.fields[feature.label+'_choices'] = forms.MultipleChoiceField(
                    choices=(
                        (x, x) for x in FeatureOption.objects.filter(feature=feature)
                    ),
                    initial=initial_value,
                    required=False
                )
                pass
            else:
                if feature.label in initial:
                    initial_value = initial[feature.label]['options']
                self.fields[feature.label+'_choices'] = forms.ChoiceField(
                    choices=(
                        (x, x) for x in FeatureOption.objects.filter(feature=feature)
                    ),
                    initial=initial_value,
                    required=False
                )
                pass

            initial_desc = None
            initial_cit = None
            if feature.label in initial:
                initial_desc = initial[feature.label]['description']
                initial_cit = initial[feature.label]['citations']
                pass

            self.fields[feature.label+'_description'] = forms.CharField(
                label='Description',
                help_text="This field supports Markdown Syntax",
                widget=widgets.Textarea(),
                initial=initial_desc,
                required=False
            )

            self.fields[feature.label+'_citation'] = forms.CharField(
                label='Citations',
                help_text="Separate the urls with commas",
                widget=widgets.TextInput(attrs={'data-role': 'tagsinput', 'placeholder': ''}),
                initial=initial_cit,
                required=False
            )
            
            self.fields[feature.label+'_choices'].feature_id = feature.id
            self.fields[feature.label+'_description'].feature_id = feature.id
            self.fields[feature.label+'_citation'].feature_id = feature.id
            pass
        return
        
    pass


# model forms

class CreateUserForm(forms.ModelForm):

    email = forms.EmailField(max_length=254, required=True)
    password = forms.CharField(max_length=128, label='Password', widget=widgets.PasswordInput)
    password2 = forms.CharField(max_length=128, label='Password Confirmation', widget=widgets.PasswordInput)

    def clean_password2(self):
        if self.cleaned_data['password2'] == self.cleaned_data['password']:
            return self.cleaned_data['password2']
        raise ValidationError("The passwords don't match")

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password', 'password2']

    pass

class SystemForm(forms.ModelForm):

    class Meta:
        model = System
        fields = ['name']
    
    pass

class SystemVersionEditForm(forms.ModelForm):

    description_citations = TagFieldM2M(
        help_text="Separate the urls with commas",
        required=False
    )
    history_citations = TagFieldM2M(
        help_text="Separate the urls with commas",
        required=False
    )
    start_year_citations = TagFieldM2M(
        help_text="Separate the urls with commas",
        required=False
    )
    end_year_citations = TagFieldM2M(
        help_text="Separate the urls with commas",
        required=False
    )

    class Meta:
        model = SystemVersion
        fields = [
            'logo',
            'description',
            'description_citations',
            'history',
            'history_citations',
            'url',
            'tech_docs',
            'developer',
            'start_year',
            'start_year_citations',
            'end_year',
            'end_year_citations',
            'projecttypes',
            'comment'
        ]
    
    pass

class SystemVersionForm(forms.ModelForm):

    description_citations = TagFieldM2M(
        help_text="Separate the urls with commas",
        required=False
    )
    history_citations = TagFieldM2M(
        help_text="Separate the urls with commas",
        required=False
    )
    start_year_citations = TagFieldM2M(
        help_text="Separate the urls with commas",
        required=False
    )
    end_year_citations = TagFieldM2M(
        help_text="Separate the urls with commas",
        required=False
    )

    class Meta:
        model = SystemVersion
        fields = [
            'logo',
            'description',
            'description_citations',
            'history',
            'history_citations',
            'url',
            'tech_docs',
            'developer',
            'start_year',
            'start_year_citations',
            'end_year',
            'end_year_citations',
            'projecttypes',
        ]

    pass

class SystemVersionMetadataForm(forms.ModelForm):

    class Meta:
        model = SystemVersionMetadata
        exclude = ['system']

    pass