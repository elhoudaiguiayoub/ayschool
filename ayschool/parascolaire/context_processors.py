from django.conf import settings


def demo_user(request):
    user = request.session.get('demo_user') if settings.DEMO_MODE else (
        {'username': request.user.get_username(), 'role': request.user.role}
        if request.user.is_authenticated else None
    )
    return {
        'demo_mode': settings.DEMO_MODE,
        'demo_user': user,
        'is_demo_authenticated': bool(user),
        'demo_role': user.get('role') if user else None,
        'demo_username': user.get('username') if user else None,
    }
