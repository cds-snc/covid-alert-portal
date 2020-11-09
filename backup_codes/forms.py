from django import forms


class BackupCodesBaseForm(forms.Form):
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

class RequestBackupCodesForm(BackupCodesBaseForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def is_valid(self):
        if self.user is None or self.user.is_authenticated is False:
            return False
        
        # Create email to admin here
        # generate_2fa_code(self.user)
        return True
