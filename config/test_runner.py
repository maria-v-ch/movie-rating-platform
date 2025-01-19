from django.test.runner import DiscoverRunner
from django.db import connections
import psycopg2
from django.conf import settings
import time

class CustomTestRunner(DiscoverRunner):
    def teardown_databases(self, old_config, **kwargs):
        # First close all Django connections
        for conn in connections.all():
            conn.close()
        
        # Then forcefully terminate all database connections
        try:
            # Connect to default postgres database to run admin commands
            conn = psycopg2.connect(
                dbname='postgres',
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT']
            )
            conn.autocommit = True
            cur = conn.cursor()
            
            # Try multiple times to terminate connections and drop database
            for attempt in range(5):
                try:
                    # Terminate all connections to the test database
                    cur.execute("""
                        SELECT pg_terminate_backend(pid)
                        FROM pg_stat_activity
                        WHERE datname = 'test_postgres'
                        AND pid <> pg_backend_pid()
                    """)
                    time.sleep(1)  # Give connections time to close
                    break
                except Exception as e:
                    if attempt == 4:  # Last attempt
                        print(f"Warning: Could not terminate connections: {e}")
                    time.sleep(1)
            
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Warning: Error during connection cleanup: {e}")
        
        # Finally proceed with normal teardown
        super().teardown_databases(old_config, **kwargs) 