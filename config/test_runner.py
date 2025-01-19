from django.test.runner import DiscoverRunner
from django.db import connections

class CustomTestRunner(DiscoverRunner):
    def teardown_databases(self, old_config, **kwargs):
        # Close all database connections before teardown
        for conn in connections.all():
            conn.close()
        super().teardown_databases(old_config, **kwargs) 