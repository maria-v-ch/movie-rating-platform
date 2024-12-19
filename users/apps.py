"""Users app configuration."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Users app configuration class."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        """Import signals when the app is ready."""
        # pylint: disable=import-outside-toplevel,unused-import
        import users.signals  # noqa: F401  # This import is needed to register signals
