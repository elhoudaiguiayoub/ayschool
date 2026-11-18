from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from .forms import DemoLoginForm, DemoRegistrationForm


def _is_logged(request):
    return bool(request.session.get('demo_user')) if settings.DEMO_MODE else request.user.is_authenticated


def accueil(request):
    return render(request, 'authentification/accueil.html')


def connexion(request):
    if _is_logged(request):
        return redirect('liste_activites')

    if not settings.DEMO_MODE:
        form = AuthenticationForm(request, data=request.POST if request.method == 'POST' else None)
        if request.method == 'POST' and form.is_valid():
            login(request, form.get_user())
            return redirect('liste_activites')
        return render(request, 'authentification/connexion.html', {'form': form})

    if request.method == 'POST':
        form = DemoLoginForm(request.POST)
        if form.is_valid():
            request.session['demo_user'] = {
                'username': form.cleaned_data['username'] or 'demo_user',
                'role': form.cleaned_data['role'],
            }
            request.session.setdefault('demo_inscriptions', [])
            messages.success(request, 'Connexion démo réussie. Aucune base de données n’est nécessaire sur Vercel.')
            return redirect('liste_activites')
    else:
        form = DemoLoginForm(initial={'username': 'eleve_demo', 'role': 'eleve'})
    return render(request, 'authentification/connexion.html', {'form': form})


def inscription(request):
    if not settings.DEMO_MODE:
        messages.info(request, 'Votre établissement crée votre compte.')
        return redirect('connexion')
    if _is_logged(request):
        return redirect('liste_activites')

    if request.method == 'POST':
        form = DemoRegistrationForm(request.POST)
        if form.is_valid():
            request.session['demo_user'] = {
                'username': form.cleaned_data['username'],
                'role': form.cleaned_data['role'],
            }
            request.session['demo_inscriptions'] = []
            messages.success(request, 'Compte démo créé pour cette session.')
            return redirect('liste_activites')
    else:
        form = DemoRegistrationForm()
    return render(request, 'authentification/inscription.html', {'form': form})


def profil(request):
    if not settings.DEMO_MODE:
        if not request.user.is_authenticated:
            return redirect('connexion')
        return render(request, 'authentification/profil.html', {
            'username': request.user.get_username(), 'role': request.user.role,
        })
    user = request.session.get('demo_user')
    if not user:
        return redirect('connexion')
    return render(request, 'authentification/profil.html', {
        'username': user['username'],
        'role': user['role'],
    })


@require_http_methods(['GET', 'POST'])
def deconnexion(request):
    if settings.DEMO_MODE:
        request.session.flush()
    elif request.method == 'POST':
        logout(request)
    else:
        return redirect('profil')
    messages.info(request, 'Déconnexion réussie.')
    return redirect('accueil')
