from django.utils import timezone


def year(request):
    """Добавляет переменную с текущим годом."""
    return {
        'year_now': timezone.now().year
    }
