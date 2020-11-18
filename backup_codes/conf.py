import django.conf


class Settings:
    """
    This is a simple class to take the place of the global settings object. An
    instance will contain all of our settings as attributes, with default values
    if they are not specified by the configuration.
    """

    defaults = {
        "BACKUP_CODES_LOCKOUT_LIMIT": 100,
    }

    def __getattr__(self, name):
        if name in self.defaults:
            return getattr(django.conf.settings, name, self.defaults[name])
        else:
            return getattr(django.conf.settings, name)


settings = Settings()
