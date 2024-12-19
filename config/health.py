from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return JsonResponse({"status": "healthy", "database": "connected"})
    except Exception as e:
        return JsonResponse(
            {"status": "unhealthy", "database": "disconnected", "error": str(e)},
            status=503
        ) 