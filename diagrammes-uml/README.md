# Diagrammes UML du projet VEILLIA

Cette arborescence contient les diagrammes UML **modernes** du projet,
concus en **images** : un fichier **SVG** (vectoriel, net à tout zoom) et un
fichier **PNG** (fond blanc, prêt à insérer) par diagramme soit 42 diagrammes au
total, organisés **par application** puis complétés par une série de vues
**globales**.

Les diagrammes sont produits à partir de la notation **Mermaid**
(`classDiagram`, `sequenceDiagram`, `stateDiagram-v2`, `flowchart`) puis
rendus hors ligne en images

## Organisation

| Répertoire | Contenu |
| --- | --- |
| [`global/`](global/) | Architecture, paquetages, modèle relationnel complet, séquences transverses, machines à états |
| [`core/`](core/) | Socle : `User`, `AuditLog`, middlewares, santé du service |
| [`veilliablog/`](veilliablog/) | CMS : classes, entités, séquences des vues HTML et de l'API, états du workflow |
| [`veillia-aggregator/`](veillia-aggregator/) | Veille : classes, entités, séquences de collecte et d'affichage, états d'un flux |
| [`veillia-agent/`](veillia-agent/) | Phase 3 (conception cible, non encore implémentée) |

## Catalogue

### Vues globales — `global/`

| Image | Diagrammes |
| --- | --- |
| [`01-architecture-1`](global/01-architecture-1.svg), [`01-architecture-2`](global/01-architecture-2.svg) | Composants : navigateur, middlewares, routeur, 4 applications, persistance, réseau ; cycle d'une requête |
| [`02-paquetages`](global/02-paquetages.svg) | Dépendances entre applications et bibliothèques tierces |
| [`03-entites-relations`](global/03-entites-relations.svg) | Modèle relationnel complet des 3 applications implémentées (UML, multiplicités) |
| [`04-sequence-publication`](global/04-sequence-publication.svg) | Chaîne complète d'une publication, du brouillon au fil public |
| [`05-sequence-collecte`](global/05-sequence-collecte.svg) | Chaîne complète d'une collecte RSS jusqu'au fil `/veille/` |
| [`06-etats-globaux-1`](global/06-etats-globaux-1.svg) · [`06-etats-globaux-2`](global/06-etats-globaux-2.svg) · [`06-etats-globaux-3`](global/06-etats-globaux-3.svg) | Machines à états transverses (statuts, rôles, cycle de vie d'une requête) |

### `core/`

| Image | Diagrammes |
| --- | --- |
| [`01-classes`](core/01-classes.svg) | `TimeStampedModel`, `User`, `UserManager`, `AuditLog` |
| [`02-entites-relations`](core/02-entites-relations.svg) | Tables `core_user`, `core_audit_log` (UML, multiplicités) |
| [`03-sequence-authentification`](core/03-sequence-authentification.svg) | Connexion par e-mail, garde de vues, déconnexion |
| [`04-sequence-audit`](core/04-sequence-audit.svg) | Écriture d'une entrée d'audit (`AuditLog.record`) |
| [`05-sequence-transverse`](core/05-sequence-transverse.svg) | Cycle de vie d'une requête : middlewares, timing, redirections, `/health/` |

### `veilliablog/`

| Image | Diagrammes |
| --- | --- |
| [`01-classes`](veilliablog/01-classes.svg) | 11 modèles + querysets, helpers de rendu |
| [`02-entites-relations`](veilliablog/02-entites-relations.svg) | Modèle relationnel complet du CMS (UML, multiplicités) |
| [`03-sequence-accueil-fil`](veilliablog/03-sequence-accueil-fil.svg) | Accueil, fils filtrés, pagination, cache de navigation |
| [`04-sequence-detail-article`](veilliablog/04-sequence-detail-article.svg) | Détail : TOC, temps de lecture, vue comptée, similaires, voisins |
| [`05-sequence-commentaire`](veilliablog/05-sequence-commentaire.svg) | Commentaire invité/rédacteur, arborescence, modération |
| [`06-sequence-reaction`](veilliablog/06-sequence-reaction.svg) | Réactions et enregistrements (`like`, `insightful`, `bookmark`) |
| [`07-sequence-studio`](veilliablog/07-sequence-studio.svg) | Studio : transitions du workflow, révisions, restauration |
| [`08-sequence-recherche`](veilliablog/08-sequence-recherche.svg) | Recherche plein texte et filtres croisés |
| [`09-sequence-newsletter`](veilliablog/09-sequence-newsletter.svg) | Abonnement, jeton de désabonnement |
| [`10-sequence-mdp-oublie`](veilliablog/10-sequence-mdp-oublie.svg) | Réinitialisation de mot de passe en 4 étapes |
| [`11-sequence-api-posts`](veilliablog/11-sequence-api-posts.svg) | API REST `/api/v1/posts/` : liste, détail, actions |
| [`12-etats-1`](veilliablog/12-etats-1.svg) · [`12-etats-2`](veilliablog/12-etats-2.svg) · [`12-etats-3`](veilliablog/12-etats-3.svg) · [`12-etats-4`](veilliablog/12-etats-4.svg) | Machines à états : `Post`, `Comment`, `Page`, `NewsletterSubscriber` |

### `veillia-aggregator/`

| Image | Diagrammes |
| --- | --- |
| [`01-classes`](veillia-aggregator/01-classes.svg) | `Source`, `Feed`, `FetchLog`, `AggregatedItem`, fonctions de service |
| [`02-entites-relations`](veillia-aggregator/02-entites-relations.svg) | Modèle relationnel de la veille (UML, multiplicités) |
| [`03-sequence-collecte`](veillia-aggregator/03-sequence-collecte.svg) | `fetch_feeds` → téléchargement conditionnel → validation → ingestion |
| [`04-sequence-commandes`](veillia-aggregator/04-sequence-commandes.svg) | Commandes `seed_feeds` et `fetch_feeds`, action admin « forcer la collecte » |
| [`05-sequence-fil-veille`](veillia-aggregator/05-sequence-fil-veille.svg) | Fil `/veille/`, filtre source, recherche, RSS, API dédiée |
| [`06-etats-flux-1`](veillia-aggregator/06-etats-flux-1.svg) · [`-2`](veillia-aggregator/06-etats-flux-2.svg) · [`-3`](veillia-aggregator/06-etats-flux-3.svg) · [`-4`](veillia-aggregator/06-etats-flux-4.svg) · [`-5`](veillia-aggregator/06-etats-flux-5.svg) | Cycle de vie d'un flux : validation, backoff, désactivation |

### `veillia-agent/` (phase 3, conception)

| Image | Diagrammes |
| --- | --- |
| [`01-classes`](veillia-agent/01-classes.svg) | Classes cibles : résumés, scores, recommandations |
| [`02-entites-relations`](veillia-agent/02-entites-relations.svg) | Tables prévues, liées aux entités existantes |
| [`03-sequence-synthese`](veillia-agent/03-sequence-synthese.svg) | Chaîne prévue d'une synthèse d'article |

## Conventions de notation

- **Diagrammes de classes UML** pour les objets et le modèle de données :
  compartiment attributs, marqueurs `[PK]`, `[FK]`, `[UK]`, multiplicités aux
  extrémités (`1`, `0..1`, `0..*`, `1..*`), losange plein = **composition**
  (suppression en cascade), flèche = association navigable dans le sens du code.
- **Séquences** (`sequenceDiagram`) : acteurs, `alt`/`opt`/`loop`, notes,
  numérotation automatique.
- **Machines à états** (`stateDiagram-v2`) : transitions étiquetées
  `événement / action`.
- **Architecture et paquetages** (`flowchart`) : composants et dépendances.
- Les stéréotypes `<<enumeration>>` marquent les `TextChoices` Django ;
  `<<service>>` les fonctions de `services.py` ; `<<cible>>` les classes
  **à créer** (phase 3).
- Fichiers multiples : un même sujet en plusieurs images reçoit les suffixes
  `-1`, `-2`, … (ex. `06-etats-flux-3.svg`).
- Formats : **SVG** (vectoriel) et **PNG** (raster, fond blanc opaque).

## Rendu

Les images sont fournies telles quelles. Pour visualiser le SVG : ouverture
directe dans le navigateur, VS Code (aperçu d'image), ou n'importe quel
visionneuse. Pour un besoin ponctuel de régénération, coller la source Mermaid
sur <https://mermaid.live> ou appeler l'API <https://kroki.io>.
