from datetime import timedelta

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from authentification.models import Utilisateur

from .models import Activite, Inscription


class DemoWorkflowTest(TestCase):
    def test_existing_demo(self):
        self.client.post(reverse('connexion'), {
            'username': 'eleve_demo', 'role': 'eleve', 'password': 'fictif',
        })
        response = self.client.post(reverse('inscription_activite', args=[1]), follow=True)
        self.assertContains(response, 'Club de développement web')
        self.assertFalse(Inscription.objects.exists())


@override_settings(DEMO_MODE=False, SESSION_ENGINE='django.contrib.sessions.backends.db')
class EstablishmentWorkflowTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = Utilisateur.objects.create_user('prof', password='test-enseignant-2026', role='professeur')
        cls.student = Utilisateur.objects.create_user('eleve', password='test-inscription-2026', role='eleve')
        cls.second = Utilisateur.objects.create_user('autre', password='test-inscription-2026', role='eleve')
        cls.activity = Activite.objects.create(
            professeur=cls.teacher, nom='Robotique', description='Atelier',
            date=timezone.now() + timedelta(days=1), nombre_max_participants=1,
        )
        cls.booking = reverse('inscription_activite', args=[cls.activity.pk])

    def test_real_login_and_private_catalog(self):
        self.assertRedirects(self.client.get(reverse('liste_activites')), reverse('connexion'))
        self.assertEqual(self.client.post(reverse('connexion'), {
            'username': 'eleve', 'password': 'incorrect',
        }).status_code, 200)
        self.assertRedirects(self.client.post(reverse('connexion'), {
            'username': 'eleve', 'password': 'test-inscription-2026',
        }), reverse('liste_activites'))
        self.assertContains(self.client.get(reverse('liste_activites')), 'Robotique')

    def test_only_staff_can_publish(self):
        payload = {'nom':'Théâtre','description':'Répétition','date':'2040-05-12T09:30','nombre_max_participants':15}
        self.client.force_login(self.student)
        self.assertRedirects(self.client.post(reverse('ajouter_activite'), payload), reverse('liste_activites'))
        self.assertFalse(Activite.objects.filter(nom='Théâtre').exists())
        self.client.force_login(self.teacher)
        self.assertRedirects(self.client.post(reverse('ajouter_activite'), payload), reverse('liste_activites'))
        self.assertEqual(Activite.objects.get(nom='Théâtre').professeur, self.teacher)

    def test_capacity_duplicate_and_private_follow_up(self):
        self.client.force_login(self.student)
        self.client.post(self.booking)
        self.client.post(self.booking)
        self.assertEqual(Inscription.objects.filter(activite=self.activity).count(), 1)
        self.assertContains(self.client.get(reverse('suivi')), 'Robotique')
        self.client.force_login(self.second)
        result = self.client.post(self.booking, follow=True)
        self.assertContains(result, 'Cette activité est complète.')
        self.assertFalse(Inscription.objects.filter(eleve=self.second).exists())
        self.assertContains(self.client.get(reverse('suivi')), 'Aucune inscription')

    def test_no_public_role_escalation_or_get_logout(self):
        self.assertRedirects(self.client.post(reverse('inscription'), {'role':'admin'}), reverse('connexion'))
        self.client.force_login(self.student)
        self.assertRedirects(self.client.get(reverse('deconnexion')), reverse('profil'))
        self.assertRedirects(self.client.post(reverse('deconnexion')), reverse('accueil'))
        self.assertRedirects(self.client.get(reverse('suivi')), reverse('connexion'))

    def test_staff_roster_scope_and_enrollment(self):
        roster = reverse('participants', args=[self.activity.pk])
        catalog = reverse('liste_activites')
        self.assertRedirects(self.client.get(roster), reverse('connexion'))
        self.client.force_login(self.teacher)
        self.assertContains(self.client.get(catalog), roster)
        self.assertContains(self.client.get(roster), 'Aucun élève inscrit')
        self.client.force_login(self.student)
        self.client.post(self.booking)
        self.assertEqual(self.client.get(roster).status_code, 404)
        other_teacher = Utilisateur.objects.create_user('collegue', role='professeur')
        self.client.force_login(other_teacher)
        self.assertNotContains(self.client.get(catalog), roster)
        self.assertEqual(self.client.get(roster).status_code, 404)
        admin = Utilisateur.objects.create_user('direction', role='admin')
        for viewer in (self.teacher, admin):
            self.client.force_login(viewer)
            response = self.client.get(roster)
            self.assertContains(response, '<li class="list-group-item">eleve</li>', html=True)
            self.assertContains(response, '1 inscription sur 1 place')
            self.assertIn('no-store', response['Cache-Control'])
        with self.settings(DEMO_MODE=True):
            self.assertEqual(self.client.get(roster).status_code, 404)
