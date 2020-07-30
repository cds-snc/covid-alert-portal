from django import forms


class HealthcareBaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # Remove the colon after field labels
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)

        # override field attributes: https://stackoverflow.com/a/56870308
        for field in self.fields:
            self.fields[field].widget.attrs.pop("autofocus", None)
            # remove autocomplete attributes
            self.fields[field].widget.attrs.update({"autocomplete": "off"})
