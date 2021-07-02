from django import forms
from django.forms.models import ModelFormOptions


"""
Monkey-patch ModelFormOptions so that we can specify the fieldsets ourselves.
Idea taken from: https://schinckel.net/2013/06/14/django-fieldsets/
"""
_old_init = ModelFormOptions.__init__


def _new_init(self, options=None):
    _old_init(self, options)
    self.fieldsets = getattr(options, "fieldsets", None)


ModelFormOptions.__init__ = _new_init


class Fieldset(object):
    """
    Define a fieldset for the datetime forms
    """

    def __init__(self, form, title, fields, classes, error):
        self.form = form
        self.title = title
        self.fields = fields
        self.classes = classes
        self.error = error

    def __iter__(self):
        for field in self.fields:
            yield field


class HealthcareBaseForm(forms.Form):
    use_required_attribute = False

    def __init__(self, *args, **kwargs):
        # Remove the colon after field labels
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)

        # override field attributes: https://stackoverflow.com/a/56870308
        for field in self.fields:
            self.fields[field].widget.attrs.pop("autofocus", None)
            # remove autocomplete attributes
            self.fields[field].widget.attrs.update({"autocomplete": "off"})
            if 'required' in self.fields[field].error_messages:
                self.fields[field].error_messages['required'] = 'Enter the information.'

    def fieldsets(self):
        meta = getattr(self, "Meta", None)
        if not meta or not meta.fieldsets:
            return

        for name, data in meta.fieldsets:
            yield Fieldset(
                form=self,
                title=name,
                fields=(self[f] for f in data.get("fields", ())),
                classes=data.get("classes", ""),
                error=data.get("error", None),
            )
