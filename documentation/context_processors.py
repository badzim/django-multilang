from django.utils.translation import get_language


def language_context(request):
    return {
        'LANGUAGE_CODE': get_language(),
        'redirect_to': request.get_full_path(),
    }
