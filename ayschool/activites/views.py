from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from .demo_data import ACTIVITES, get_activity
from .forms import ActiviteForm, EtablissementActiviteForm
from .models import Activite, Inscription


def _is_logged(request):
    return bool(request.session.get('demo_user'))


def liste_activites(request):
    if not settings.DEMO_MODE and not request.user.is_authenticated:
        return redirect('connexion')
    activites = (
        sorted(ACTIVITES, key=lambda item: item['date']) if settings.DEMO_MODE
        else Activite.objects.filter(date__gt=timezone.now()).select_related('professeur').order_by('date')
    )
    return render(request, 'activites/liste_activites.html', {'activites': activites})


def inscription_activite(request, activite_id):
    if not settings.DEMO_MODE:
        return inscription_etablissement(request, activite_id)
    if not _is_logged(request):
        return redirect('connexion')

    activite = get_activity(activite_id)
    if not activite:
        messages.error(request, 'Activité introuvable.')
        return redirect('liste_activites')

    inscriptions = request.session.get('demo_inscriptions', [])
    deja_inscrit = int(activite_id) in inscriptions

    if request.method == 'POST':
        if deja_inscrit:
            messages.info(request, 'Tu es déjà inscrit à cette activité.')
        else:
            inscriptions.append(int(activite_id))
            request.session['demo_inscriptions'] = inscriptions
            request.session.modified = True
            messages.success(request, 'Inscription confirmée pour cette session démo.')
        return redirect('suivi')

    return render(request, 'activites/inscription_activite.html', {'activite': activite, 'deja_inscrit': deja_inscrit})


def ajouter_activite(request):
    if not settings.DEMO_MODE:
        if not request.user.is_authenticated:
            return redirect('connexion')
        if request.user.role not in ('professeur', 'admin'):
            messages.error(request, 'Cette page est réservée à l’équipe.')
            return redirect('liste_activites')
        form = EtablissementActiviteForm(request.POST if request.method == 'POST' else None)
        if request.method == 'POST' and form.is_valid():
            Activite.objects.create(professeur=request.user, **form.cleaned_data)
            messages.success(request, 'Activité publiée.')
            return redirect('liste_activites')
        return render(request, 'activites/ajouter_activite.html', {'form': form})

    user = request.session.get('demo_user')
    if not user:
        return redirect('connexion')
    if user.get('role') != 'professeur':
        messages.error(request, 'Connecte-toi en mode professeur pour tester cette page.')
        return redirect('liste_activites')

    if request.method == 'POST':
        form = ActiviteForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Activité simulée. Sur Vercel, cette version garde les données en mode démo.')
            return redirect('liste_activites')
    else:
        form = ActiviteForm()
    return render(request, 'activites/ajouter_activite.html', {'form': form})


def suivi(request):
    if not settings.DEMO_MODE:
        if not request.user.is_authenticated:
            return redirect('connexion')
        inscriptions = Inscription.objects.filter(eleve=request.user).select_related('activite').order_by('activite__date')
        return render(request, 'activites/suivi.html', {'inscriptions': inscriptions})

    if not _is_logged(request):
        return redirect('connexion')

    ids = request.session.get('demo_inscriptions', [])
    inscriptions = [
        {'activite': activity, 'date_inscription': activity['date']}
        for activity in ACTIVITES
        if activity['id'] in ids
    ]
    return render(request, 'activites/suivi.html', {'inscriptions': inscriptions})


def inscription_etablissement(request, activite_id):
    if not request.user.is_authenticated:
        return redirect('connexion')
    if request.user.role != 'eleve':
        messages.error(request, 'Les inscriptions sont réservées aux élèves.')
        return redirect('liste_activites')

    if request.method == 'POST':
        with transaction.atomic():
            activite = get_object_or_404(Activite.objects.select_for_update(), pk=activite_id)
            inscriptions = Inscription.objects.filter(activite=activite)
            if inscriptions.filter(eleve=request.user).exists():
                messages.info(request, 'Tu es déjà inscrit à cette activité.')
            elif activite.date <= timezone.now():
                messages.error(request, 'Les inscriptions à cette activité sont closes.')
            elif inscriptions.count() >= activite.nombre_max_participants:
                messages.error(request, 'Cette activité est complète.')
            else:
                inscriptions.create(eleve=request.user, activite=activite)
                messages.success(request, 'Inscription confirmée.')
        return redirect('suivi')

    activite = get_object_or_404(Activite, pk=activite_id)
    deja_inscrit = Inscription.objects.filter(activite=activite, eleve=request.user).exists()
    return render(request, 'activites/inscription_activite.html', {
        'activite': activite,
        'deja_inscrit': deja_inscrit,
        'inscriptions_closes': activite.date <= timezone.now(),
    })
