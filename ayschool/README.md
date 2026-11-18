# AySchool — Vercel Demo

AySchool est une plateforme parascolaire Django créée comme projet portfolio.

Cette version est optimisée pour **Vercel** : elle évite SQLite en production et utilise des données de démonstration + sessions signées.

## Fonctionnalités

- Catalogue d'activités
- Connexion démo élève/professeur
- Inscription aux activités pendant la session
- Suivi des inscriptions
- Page profil
- Design responsive avec Bootstrap + CSS custom
- Déploiement compatible Vercel

## Lancer en local

```bash
python -m pip install -r requirements.txt
python manage.py runserver
```

## Déployer sur Vercel

1. Push le projet sur GitHub
2. Import dans Vercel
3. Framework Preset: Other
4. Laisse Vercel utiliser `vercel.json`

## Note technique

Vercel n'est pas idéal pour un vrai backend Django avec base SQLite persistante. Cette version est donc une **démo portfolio propre**, sans erreur database.

Pour une vraie app production avec base de données, utiliser Render, Railway, Fly.io, PythonAnywhere ou PostgreSQL externe.

## Pilote pour un établissement

Le même projet Django peut fonctionner avec de vrais comptes, activités et inscriptions. Chaque déploiement est destiné à un établissement. Son équipe crée les comptes depuis l’administration Django. Le catalogue et le suivi sont accessibles après connexion. Le mode démo reste le mode par défaut.

### Démarrage local avec une base persistante

Avec Python 3.12 ou version supérieure, installe `requirements.txt`. Configure les variables suivantes dans l’environnement du processus :

| Variable | Valeur |
| --- | --- |
| `AYSCHOOL_MODE` | `establishment` |
| `DEBUG` | `True` en développement local seulement |
| `SECRET_KEY` | Clé aléatoire unique de 50 caractères ou plus |
| `AYSCHOOL_ALLOWED_HOSTS` | Noms d’hôtes supplémentaires séparés par des virgules |

Exécute `python manage.py migrate`, puis `python manage.py createsuperuser` et `python manage.py runserver`. Dans /admin/, crée un compte professeur et un compte élève pour tester le parcours. SQLite conserve les données locales dans `ayschool.sqlite3`.

### Installation pour un client

Utilise un service HTTPS avec un serveur WSGI et PostgreSQL, en plus de `requirements-production.txt`. Configure `AYSCHOOL_DB_HOST`, `AYSCHOOL_DB_PORT`, `AYSCHOOL_DB_NAME`, `AYSCHOOL_DB_USER`, `AYSCHOOL_DB_PASSWORD` et, si nécessaire, `AYSCHOOL_DB_SSLMODE`. Configure explicitement `AYSCHOOL_ALLOWED_HOSTS` et `AYSCHOOL_TRUSTED_ORIGINS`. Exécute les migrations et `collectstatic` avant ouverture. Avec un proxy, configure sa réécriture de l’en-tête HTTPS côté serveur.

Pour une ancienne base, vérifie les doublons d’inscription pour un même couple activité/élève avant la migration. La contrainte d’unicité refuse un doublon existant. Prends une sauvegarde avant de migrer les données réelles.

Le premier contrat peut être un pilote payant comprenant la configuration, la formation et un mois de support. Fixe le devis après estimation du temps, de l’hébergement et du support. Avant d’ouvrir à de vrais élèves, convenez avec l’établissement du périmètre des données, des accès et de la durée de conservation.

`python manage.py test` vérifie la démo, l’authentification établissement, les droits de publication, le suivi individuel et la capacité.

### Démonstration à un responsable du parascolaire

Avec deux comptes fictifs, publie une activité depuis le compte professeur. Depuis le compte élève, réserve une place. Reconnecte-toi comme professeur, ouvre le catalogue et clique sur **Voir les inscrits**. La liste montre les identifiants inscrits et la capacité. Chaque professeur consulte ses propres activités. Un compte de rôle administrateur peut consulter toutes les listes. Pour le premier essai, utilise uniquement des identifiants fictifs.
