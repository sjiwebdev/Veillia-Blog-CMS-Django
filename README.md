# PRESENTATION DE L'APPLICATION WEB DJANGO "VEILLIA"

Veille intelligente **Data Science & Intelligence Artificielle** : un magazine
technique éditorial (articles, taxonomie, workflow, commentaires, newsletter),
un fil d'agrégation RSS multi-sources et une API REST documentée par Swagger, le tout en
**quatre applications Django** au sein d'un dépôt unique.

| Application | Rôle | Statut | Documentation |
| --- | --- | --- | --- |
| `core` | socle : comptes, audit, middlewares transverses, santé du service | en cours | [`docs/core.md`](docs/core.md) |
| `veilliablog` | CMS éditorial : billets, workflow, rendu Markdown, communauté, API blog | en cours (phase 1) | [`docs/veilliablog.md`](docs/veilliablog.md) |
| `veillia_aggregator` | veille : sources, flux RSS, collecte, déduplication, fil `/veille/`, API dédiée | non debutée (phase 2) | [`docs/veillia-aggregator.md`](docs/veillia-aggregator.md) |
| `veillia_agent` | agentique : synthèses, scores, recommandations | **en conception** (phase 3) | [`docs/veillia-agent.md`](docs/veillia-agent.md) |

## Table des matières

1. [Fonctionnalités](#fonctionnalités)
2. [Stack technique](#stack-technique)
3. [Démarrage rapide](#démarrage-rapide)
4. [Commandes de gestion](#commandes-de-gestion)
5. [Routes clés](#routes-clés)
6. [API REST](#api-rest)
7. [Structure du dépôt](#structure-du-dépôt)
8. [Configuration](#configuration)
9. [Collecte RSS](#collecte-rss)
10. [Sécurité et qualité](#sécurité-et-qualité)
11. [Tests](#tests)
12. [Documentation et diagrammes](#documentation-et-diagrammes)
13. [Roadmap](#roadmap)
14. [Limites connues](#limites-connues)

## Fonctionnalités

### `core`: le socle ou base de l'application

- `User` UUID, e-mail unique, avatar/initials, `Role` + permissions ;
  `UserManager.editors()`.
- `AuditLog.record()` : chaque transition de publication et chaque modération
  laisse une trace (acteur, objet, avant/après, empreinte d'IP).
- `TimeStampedModel` (`created_at` / `updated_at`) hérité par tous les contenus.
- Middlewares : sécurité et cookies, `PermanentRedirectMiddleware`
  (légués `/articles/` → `/blog/`, **302**), `RequestTimingMiddleware`
  (`X-Request-Time-Ms`, alerte > 400 ms).
- Context processor de navigation (cache 60 s, 6 catégories racines + 6 pages).
- `GET /health/` : `{status, service, app, database, python, latency_ms}`,
  **503** si la base est indisponible (sonde de load-balancer).

### `veilliablog`: le magazine / Application principale de CMS Blog

- **Workflow éditorial** : `draft → in_review → published`, planification
  (`scheduled`), archivage, relecture avec demandes de changement, révisions
  restaurables, brouillon toujours reconstruit à partir de la dernière version
  publiée (`services.save_revision`, `PostRevision.restore`).
- **Studio** (`/studio/`) : file de rédaction par statut, prévisualisation,
  actions de transition, compteur de commentaires en attente.
- **Rendu Markdown** : `markdown` (extra, sane_lists, codehilite, toc,
  admonition) → HTML assaini par `bleach` → liens en `noopener noreferrer nofollow`
  → temps de lecture (200 mots/min) → extrait automatique (260 caractères) →
  table des matières ancrée (`toc`, id normalisés, slug à 50 caractères).
- **Taxonomie** : catégories hiérarchisées (`depth`/`root_path`, filtres par
  ancêtre), mots-clés typés (`kind` : method/tool/concept/…), séries ordonnées
  (`PostInSeries.position`), archives par année/mois, auteur (`/auteur/<u>/`).
- **Découverte** : recherche plein texte (browse, `search_text` indexé),
  filtres catégorie/mot-clé/auteur/mois, articles similaires (tags + catégorie
  + ancêtre, cache 5 min), plus consultés sur 7 jours (cache 5 min), pages de
  tags enrichies (top billets, tags connexes), fil RSS (`/blog/flux/`, 30 billets),
  sitemap (posts, pages, catégories), `robots.txt`.
- **Communauté** : commentaires en fil avec réponse, modérés (`pending` par
  défaut — immédiatement publiés pour un éditeur), signalement, réactions
  `like` / `insightful` / `bookmark` (bascule par session, CSRF), compteur de
  vues anti-doublon (session, TTL 1 h), bookmarks personnels, newsletter
  (abonnement/désabonnement, aucun e-mail envoyé en phase 1).
- **Comptes** : inscription auto-connectée, connexion par **e-mail**
  (`USERNAME_FIELD`), réinitialisation de mot de passe (jeton, expiration,
  réutilisable), 4 rôles (`reader`, `editor`, `curator`, `admin`) ×
  permissions (`review_post`, `publish_post`, `manage_blog`).
- **Administration enrichie** : filtres hiérarchiques, recherche, colonnes
  utiles, actions groupées de publication, `list_select_related`.

### `veillia_aggregator`: la veille sur la science de données et l'IA

- **Catalogue** : `Source` (éditeur, `authority_score`, `robots_policy`) →
  `Feed` (URL unique, priorité, intervalle, `is_active`).
- **Collecte** : `fetch_feeds` (`--all`, `--feed URL`) via `urllib` +
  `feedparser`, User-Agent identifiable, `ETag` / `If-Modified-Since` (un 304
  ne re-télécharge rien), timeout configurable, backoff `intervalle × 2^min(n,5)`,
  désactivation après **5 échecs** (`invalid`), journal `FetchLog` (succès /
  304 / échec, durée, volumes).
- **Déduplication** : URL canonique (fragment, paramètres de suivi, casse,
  barre finale) → `sha256` → `url_hash` unique ; repli sur `guid:` ; entrée
  sans lien stockée sans lien sortant.
- **Exploitation** : admin (forcer la collecte, marquer valide/invalide,
  publier/rejeter en masse), fil `/veille/` (recherche, filtre par source,
  tri), `/veille/source/<slug>/`, RSS `/veille/flux/`, dernière collecte
  affichée (diagnostic de fil figé).
- **Politique** : extrait RSS uniquement (`content_license=rss_only`), jamais
  l'article complet, URL source toujours conservée.

## Stack technique

| Couche | Choix |
| --- | --- |
| Framework | Django 5.2.17 |
| API | djangorestframework 3.18.1, django-filter 26.2, drf-spectacular 0.30.0 (OpenAPI + Swagger) |
| Contenu | Markdown 3.11, bleach 6.4.0, Pillow 11.0.0 |
| Collecte | feedparser 6.0.14 (`urllib` pour le transport, aucune dépendance HTTP) |
| Config | python-dotenv 1.2.4 (`.env`, tout est optionnel en dev) |
| Statique | whitenoise 6.12.0 (manifeste compressé en prod) |
| Bases | SQLite en dev ; PostgreSQL via `DB_ENGINE=postgres` (`psycopg[binary]` à activer) |
| Front | templates Django, CSS maison (design system), **JavaScript vanilla**
  (`static/veilliablog/js/app.js` : thème clair/sombre, menu, TOC, barre de
  lecture, réactions/commentaires/vues en `fetch`, amélioration progressive, sans framework ni HTMX) |

## Démarrage rapide

```bash
python -m venv .venv
source .venv/bin/activate            # Windows : .venv\Scripts\activate
python -m pip install -r requirements.txt

cp .env.example .env                 # Windows : Copy-Item .env.example .env
#   tout est optionnel en dev ; SECRET_KEY, DEBUG, ALLOWED_HOSTS en prod

python manage.py migrate
python manage.py seed_blog           # CMS de démonstration (idempotent)
python manage.py seed_feeds          # catalogue RSS P0 (idempotent)
python manage.py fetch_feeds --all   # première collecte (bonne connexion internet requise)
python manage.py runserver
```

# Ou avec Commandes uv
```bash
uv run python -m venv .venv
uv run source .venv/bin/activate            
uv run python -m pip install -r requirements.txt
uv run cp .env.example .env
uv run python manage.py migrate
uv run python manage.py seed_blog           
uv run python manage.py seed_feeds          
uv run python manage.py fetch_feeds --all   
uv run python manage.py runserver
```


| URL | Rôle |
| --- | --- |
| <http://127.0.0.1:8000/> | site |
| <http://127.0.0.1:8000/admin/> | administration |
| <http://127.0.0.1:8000/api/docs/> | Swagger |
| <http://127.0.0.1:8000/health/> | sonde de santé |

### Comptes de démonstration

| Rôle | Identifiant | Mot de passe |
| --- | --- | --- |
| Éditeur (`admin`, staff, superuser) | `editor@veillia.local` | `veillia-demo-2026` |
| Lecteur | `reader@veillia.local` | `veillia-demo-2026` |

Connexion par **adresse e-mail**. À supprimer ou re-mot-de-passer avant toute
mise en ligne.

---

## Commandes de gestion

```bash
python manage.py test               # 139 tests (voir « Tests »)
python manage.py check              # validation de la configuration
python manage.py seed_blog          # idempotent : comptes, taxonomie, pages, 10 billets
python manage.py seed_feeds         # idempotent : 3 sources P0 (TDS, HF, OpenAI)
python manage.py fetch_feeds        # flux dus (intervalle + backoff)
python manage.py fetch_feeds --all  # ignore l'intervalle
python manage.py fetch_feeds --feed URL   # force un flux
python manage.py makemigrations     # après modification d'un modèle
python manage.py migrate
python manage.py collectstatic      # requis si DEBUG=False
python manage.py createsuperuser    # identifiant = e-mail (REQUIRED_FIELDS=["username"])
```

## Routes clés

### HTML

| URL | Rôle |
| --- | --- |
| `/` | accueil : une, vedette, tendances, catégories, derniers billets |
| `/blog/`, `/blog/recherche/` | fil paginé, recherche, filtres `?category=`, `?tag=`, `?author=`, `?month=`, `?ordering=` |
| `/blog/<slug>/` | détail : TOC, réactions, commentaires, similarités, voisins, vue comptée |
| `/blog/categorie/<slug>/`, `/blog/mot-cle/<slug>/`, `/blog/serie/<slug>/` | taxonomie |
| `/blog/archive/<annee>[/mois]/` | archives |
| `/blog/flux/` | RSS des 30 derniers billets |
| `/blog/<slug>/commentaire/` | dépôt de commentaire (POST) |
| `/auteur/<username>/`, `/enregistres/` | auteur, favoris |
| `/studio/`, `/studio/billet/<pk>/<action>/`, `/revisions/<pk>/` | studio et révisions |
| `/reactions/`, `/newsletter/abonnement/` | réactions, newsletter |
| `/compte/{connexion,deconnexion,inscription,oublie}/…` | comptes et parcours mot de passe oublié |
| `/page/<slug>/` + catch-all `/<slug>/` | pages CMS (À propos, Mentions légales, Confidentialité) |
| `/veille/`, `/veille/source/<slug>/`, `/veille/flux/` | fil de veille, fil par source, RSS de la veille |
| `/sitemap.xml`, `/robots.txt`, `/health/` | SEO et supervision |
| `/admin/` | Django admin enrichi (blog, veille, socle) |
| Pages léguées `/articles/`, `/article/`, `/news/`, `/feed/` | redirections 302 vers le blog |

### API (extrait — détail dans [`docs/api.md`](docs/api.md))

| URL | Rôle |
| --- | --- |
| `/api/v1/posts/` | liste paginée (12/page) : `search`, `ordering`, `category`, `tag`, `author`, `featured`, `status` (éditeurs) |
| `/api/v1/posts/<slug>/` | billet complet : `body_html`, `toc`, `canonical_url`, SEO, séries, voisins |
| `/api/v1/posts/<slug>/{similar,search,trending}/` | découvertes (`search`/`trending` aussi au niveau collection) |
| `/api/v1/posts/<slug>/{view,comments,reactions}/` | **écritures** : vue, commentaire, réaction |
| `/api/v1/{categories,tags,series,pages,comments}/` | ressources annexes (+ `…/<slug>/`) |
| `/api/v1/stats/`, `/api/v1/stats/admin/` | chiffres clés (publie / staff) |
| `/api/v1/veille/items/`, `/api/v1/veille/sources/` | agrégats : `source`, `search`, `fresh`, `ordering` |
| `/api/schema/`, `/api/docs/` | schéma OpenAPI, Swagger UI |

## Structure du dépôt

```text
config/               settings (env-driven), urls racine, wsgi/asgi, DRF/spectacular
core/                 User, AuditLog, middlewares, health, context processor
veilliablog/          CMS : modèles, services, vues, formes, tags, rendu, feeds,
                      sitemaps, admin, api/, management/ (seed_blog), tests/ (97)
veillia_aggregator/   veille : modèles, services, vues, feeds, admin, api/,
                      management/ (seed_feeds, fetch_feeds), tests/ (42)
templates/            base.html, 404/500, veilliablog/, veillia_aggregator/
static/veilliablog/   css/base.css, js/app.js, img/favicon.svg
docs/                 documentation exhaustive (8 documents, index : docs/README.md)
diagrammes-uml/       42 diagrammes UML en images SVG + PNG (index : diagrammes-uml/README.md)
```

## Configuration

Copier [`.env.example`](.env.example) vers `.env` : tout est optionnel en
développement. Variables principales :

| Bloc | Variables |
| --- | --- |
| Sécurité / hôte | `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` |
| Base | `DB_ENGINE` (`sqlite`/`postgres`), `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_CONN_MAX_AGE` |
| Identité | `VEILLIA_NAME`, `VEILLIA_TAGLINE`, `VEILLIA_CONTACT_EMAIL`, `DEFAULT_FROM_EMAIL` |
| Blog | `BLOG_POSTS_PER_PAGE`, `BLOG_NEWSLETTER_ENABLED` |
| Veille | `AGGREGATOR_ITEMS_PER_PAGE`, `AGGREGATOR_USER_AGENT`, `AGGREGATOR_TIMEOUT_SECONDS` |
| API | `API_THROTTLE_ANON` (60/min), `API_THROTTLE_USER` (240/min) |
| Prod | `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS` |
| Journal | `LOG_LEVEL` |

Table complète, cron, checklist de déploiement et dépannage :
[`docs/operations.md`](docs/operations.md).

## Collecte RSS

- `seed_feeds` installe les trois sources prioritaires du cahier des charges
  (Towards Data Science 0.800, Hugging Face 0.850, OpenAI 0.850), `priority=0`.
- `fetch_feeds` n'explore que les flux **dûs** ; chaque tentative crée un
  `FetchLog` ; `mark_success` remet `failure_count` à 0 et passe `pending → valid`.
- Après **5 échecs** consécutifs : `validation_status=invalid`,
  `is_active=False`:le flux sort du circuit jusqu'à revue dans l'admin
  (action « Marquer comme valide »).
- Validation sur les 5 premières entrées (lien/GUID + date) ; une entrée sans
  URL canonique ni GUID est comptée `skipped`.
- Aucun scheduler applicatif : cron machine (`*/15` conseillé) appelant
  `fetch_feeds`.
- Volumes observés : **874 articles** ingérés depuis Hugging Face au premier
  passage ; TDS/OpenAI peuvent expirer (timeout) d'ou backoff appliqué.

## Sécurité et qualité

- `SecurityMiddleware`, cookies `HttpOnly`/`SameSite=Lax`/`Secure` en prod,
  HSTS, `X_FRAME_OPTIONS=DENY`, redirection SSL, dépôt `check --deploy` propre.
- CSRF sur tous les POST de session ; API : `SessionAuthentication` +
  `BasicAuthentication`, throttle DRF (désactivé automatiquement en tests).
- Markdown assaini par `bleach` (liste blanche de balises/attributs, protocoles
  http/https/mailto/tel), liens sortants `nofollow noopener`.
- Journal d'audit sur les transitions éditoriales et modérations.
- WhiteNoise en prod (statiques manifeste), collecte RSS identifiée et
  respectueuse (`robots_policy`, ETag/304).
- `manage.py check` : **Resultat attendu: 0 problème**.

## Tests

```bash
python -X utf8 manage.py test         
python -X utf8 manage.py test veilliablog          
python -X utf8 manage.py test veillia_aggregator   
```

## Documentation et diagrammes

**Documentation** ([`docs/README.md`](docs/README.md)) :

| Document | Contenu |
| --- | --- |
| [`docs/architecture.md`](docs/architecture.md) | les 4 applications, arborescence, couche de responsabilités, routage, settings, cycle de requête, flux de données |
| [`docs/core.md`](docs/core.md) | socle : modèles, middlewares, context processor, `/health/`, tests |
| [`docs/veilliablog.md`](docs/veilliablog.md) | CMS : modèles, rendu, 27 services, workflow, ~25 vues, formulaires, admin, seed, API, tests |
| [`docs/veillia-aggregator.md`](docs/veillia-aggregator.md) | veille : modèles, chaîne de collecte, exploitation, restitution, politiques, tests |
| [`docs/veillia-agent.md`](docs/veillia-agent.md) | phase 3 : périmètre, décisions structurantes, contraintes, définition de terminé |
| [`docs/api.md`](docs/api.md) | surface REST complète : routes, paramètres, permissions, exemples |
| [`docs/operations.md`](docs/operations.md) | installation, variables, commandes, tests, déploiement, surveillance, limites connues, dépannage |

**Diagrammes UML** ([`diagrammes-uml/README.md`](diagrammes-uml/README.md)) :
42 diagrammes UML concu en images **SVG + PNG** (fond blanc), par application et
en vues globales: `global/` (architecture, paquetages, entités-relations,
séquences publication/collecte, états) · `core/` · `veilliablog/` (user cases,
classes, entités, séquences, états) · `veillia-aggregator/` ·
`veillia-agent/` (conception).

## Roadmap ou démarche de developpement

1. **Phase 1: Blog CMS** : En cours de conception (`veilliablog` + `core` : workflow, communauté.
2. **Phase 2: Agrégation** : En cours de conception (`veillia_aggregator` : collecte,
   déduplication, journal, fil, API).
3. **Phase 3: Agentique** : En cours de conception `veillia_agent` (synthèses
   traçables, scores de source/mot-clé, recommandations, file de validation
   humaine) ; voir [`docs/veillia-agent.md`](docs/veillia-agent.md).

---

## Limites connues

En résumé (détail et remèdes dans [`docs/operations.md`](docs/operations.md) §9) :

- `publish_scheduled_posts()` n'est appelé que par les tests → cron à brancher
  pour les publications planifiées.
- `request_changes()` existe côté services mais sans bouton d'interface.
- Aucun `EMAIL_BACKEND` configuré → e-mails (mot de passe oublié, newsletter)
  à brancher en production ; la newsletter ne diffuse pas encore.
- Aucun scheduler applicatif : la collecte dépend d'un cron externe.
- La description OpenAPI annonce encore « phase 1 » (la surface veille est
  documentée par `docs/api.md`).
- `veillia_agent` n'existe pas encore (phase 3).

# Contributeurs du projets (membres du groupe)

Ce projet est mene de bout en bout par une equipe de 3 etudiants en Master 2 Data Science de Saint Jean Ingenieur. Les pseudo de commits de chacun sont mentionnes entre parenthese

- NGOUMTSOP TEUZEM Yeiayel Chavaquiah (@teuzem pour commit sur main et @yeiayel branche de travail)
- KAMGUENG YOLONG Ariane Sonita (@Ariane-git)
- TONFACK MATENGUE Elvira Brenda (MatengueElvira)