"""Movies app configuration."""

from django.apps import AppConfig


class MoviesConfig(AppConfig):
    """Movies app configuration class."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "movies"

    def ready(self):
        """Import signals when the app is ready."""
        # pylint: disable=import-outside-toplevel,unused-import
        import movies.signals  # noqa: F401  # This import is needed to register signals
