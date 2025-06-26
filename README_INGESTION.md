# Guide d'Ingestion : `python -m ingestion.ingest --clean`

Ce guide explique en détail ce que fait la commande d'ingestion avec l'option `--clean` dans le système Agentic RAG avec Graphe de Connaissances.

## Vue d'ensemble

La commande `python -m ingestion.ingest --clean` effectue un processus complet d'ingestion de documents avec nettoyage préalable des bases de données. Cette commande est essentielle pour préparer le système avant d'utiliser l'agent IA.

## Processus détaillé étape par étape

### Étape 1 : Nettoyage des bases de données (--clean)
```
🧹 NETTOYAGE DES DONNÉES EXISTANTES
├── PostgreSQL
│   ├── DELETE FROM messages          # Suppression des conversations
│   ├── DELETE FROM sessions          # Suppression des sessions utilisateur
│   ├── DELETE FROM chunks            # Suppression des fragments de documents
│   └── DELETE FROM documents         # Suppression des documents
└── Neo4j (Graphe de connaissances)
    └── CLEAR GRAPH                   # Suppression complète du graphe Graphiti
```

**⚠️ ATTENTION** : Cette étape supprime **toutes** les données existantes des deux bases de données !

### Étape 2 : Initialisation du pipeline
```
🔧 INITIALISATION DU SYSTÈME
├── 🔌 Connexion à PostgreSQL (DATABASE_URL)
├── 🔌 Connexion à Neo4j (NEO4J_URI)
├── 🤖 Initialisation du modèle LLM pour l'ingestion
├── 📊 Initialisation du client d'embeddings
├── ✂️  Initialisation du chunker sémantique
└── 🕸️  Initialisation du constructeur de graphe Graphiti
```

### Étape 3 : Découverte des documents
```
📁 SCAN DU DOSSIER DOCUMENTS
├── 📂 Parcours du dossier 'documents/' (par défaut)
├── 🔍 Recherche des fichiers *.md et *.markdown
├── 📋 Création de la liste des fichiers à traiter
└── 📊 Affichage : "Found X markdown files to process"
```

### Étape 4 : Traitement de chaque document

Pour chaque fichier markdown trouvé, le système effectue :

#### 4.1 Lecture et analyse initiale
```
📖 LECTURE DU DOCUMENT
├── 📄 Lecture du contenu (UTF-8, fallback latin-1)
├── 🏷️  Extraction du titre
│   ├── Recherche du premier # dans les 10 premières lignes
│   └── Fallback : nom du fichier sans extension
├── 📊 Extraction des métadonnées
│   ├── Parsing du YAML frontmatter (si présent)
│   ├── Calcul de la taille du fichier
│   ├── Comptage des lignes et mots
│   └── Date d'ingestion
└── 📝 Préparation pour le chunking
```

#### 4.2 Découpage sémantique intelligent
```
✂️  CHUNKING SÉMANTIQUE
├── 🏗️  Division structurelle
│   ├── Headers markdown (# ## ###)
│   ├── Paragraphes (lignes vides multiples)
│   ├── Listes (- * + 1. 2. 3.)
│   ├── Blocs de code (```)
│   └── Tableaux (|)
├── 🧠 Regroupement sémantique
│   ├── Analyse de cohérence par le LLM
│   ├── Respect de la taille max (1000 chars par défaut)
│   ├── Chevauchement entre chunks (200 chars)
│   └── Préservation du contexte
└── 📊 Création des objets DocumentChunk
    ├── Index du chunk
    ├── Position dans le document
    ├── Métadonnées enrichies
    └── Estimation du nombre de tokens
```

#### 4.3 Génération des embeddings
```
🧮 GÉNÉRATION DES EMBEDDINGS VECTORIELS
├── 🔤 Tokenisation du contenu de chaque chunk
├── 🌐 Appel à l'API d'embeddings (OpenAI/Ollama/etc.)
├── 📊 Génération du vecteur (1536 dimensions pour OpenAI)
└── 🔢 Conversion au format PostgreSQL vector
```

#### 4.4 Sauvegarde en PostgreSQL
```
💾 SAUVEGARDE EN BASE VECTORIELLE
├── 📄 INSERT INTO documents
│   ├── title, source, content
│   ├── metadata (JSON)
│   └── timestamps
└── 🧩 INSERT INTO chunks (pour chaque chunk)
    ├── document_id (référence)
    ├── content (texte)
    ├── embedding (vecteur)
    ├── chunk_index
    ├── metadata (JSON)
    └── token_count
```

#### 4.5 Construction du graphe de connaissances
```
🕸️  CONSTRUCTION DU GRAPHE GRAPHITI
├── 📝 Préparation des épisodes
│   ├── Création d'un episode_id unique
│   ├── Limitation du contenu (6000 chars max)
│   ├── Troncature intelligente aux limites de phrases
│   └── Ajout du contexte minimal
├── 🤖 Traitement par Graphiti
│   ├── Extraction automatique d'entités
│   │   ├── Entreprises (Google, Microsoft, OpenAI...)
│   │   ├── Personnes (Sam Altman, Satya Nadella...)
│   │   ├── Technologies (GPT, Claude, LLaMA...)
│   │   └── Lieux et organisations
│   ├── Identification des relations
│   │   ├── Partenariats (Microsoft ↔ OpenAI)
│   │   ├── Acquisitions (Google → DeepMind)
│   │   ├── Concurrence (OpenAI vs Anthropic)
│   │   └── Collaborations
│   └── Création des nœuds et arêtes temporels
├── ⏱️  Délai entre épisodes (0.5s pour éviter la surcharge)
└── 📊 Comptage des épisodes créés
```

### Étape 5 : Résumé et statistiques finales
```
📊 RAPPORT D'INGESTION FINAL
├── 📈 Statistiques globales
│   ├── Nombre de documents traités
│   ├── Nombre total de chunks créés
│   ├── Nombre d'entités extraites
│   ├── Nombre d'épisodes de graphe créés
│   ├── Nombre d'erreurs rencontrées
│   └── Temps de traitement total
├── 📋 Détail par document
│   ├── ✓ Succès : titre, chunks, entités
│   └── ✗ Échecs : titre, erreurs détaillées
└── 🏁 Fermeture des connexions
    ├── Fermeture du pool PostgreSQL
    ├── Fermeture du client Neo4j
    └── Nettoyage des ressources
```

## Options de la commande

| Option | Description | Valeur par défaut |
|--------|-------------|-------------------|
| `--clean` | Nettoie les données existantes avant ingestion | `False` |
| `--documents` | Dossier contenant les documents markdown | `"documents"` |
| `--chunk-size` | Taille maximale des chunks en caractères | `1000` |
| `--chunk-overlap` | Chevauchement entre chunks en caractères | `200` |
| `--no-semantic` | Désactive le découpage sémantique (utilise le découpage simple) | `False` |
| `--no-entities` | Désactive l'extraction d'entités | `False` |
| `--fast` | Mode rapide : ignore la construction du graphe | `False` |
| `--verbose` | Active les logs détaillés | `False` |

## Exemples d'utilisation

### Ingestion complète avec nettoyage (recommandé)
```bash
python -m ingestion.ingest --clean --verbose
```

### Ingestion rapide sans graphe de connaissances
```bash
python -m ingestion.ingest --clean --fast
```

### Ingestion avec paramètres personnalisés
```bash
python -m ingestion.ingest --clean --chunk-size 800 --chunk-overlap 150
```

### Ajout de nouveaux documents sans nettoyage
```bash
python -m ingestion.ingest --documents new_docs/
```

## Exemple de sortie complète

```
2024-01-15 10:30:15,123 - ingestion.ingest - INFO - Initializing ingestion pipeline...
2024-01-15 10:30:16,456 - ingestion.ingest - WARNING - Cleaning existing data from databases...
2024-01-15 10:30:17,789 - ingestion.ingest - INFO - Cleaned PostgreSQL database
2024-01-15 10:30:18,012 - ingestion.ingest - INFO - Cleaned knowledge graph
2024-01-15 10:30:19,345 - ingestion.ingest - INFO - Ingestion pipeline initialized
2024-01-15 10:30:20,678 - ingestion.ingest - INFO - Found 5 markdown files to process
2024-01-15 10:30:21,901 - ingestion.ingest - INFO - Processing file 1/5: documents/openai_funding.md
2024-01-15 10:30:22,234 - ingestion.ingest - INFO - Processing document: OpenAI Funding Analysis
2024-01-15 10:30:35,567 - ingestion.graph_builder - INFO - Adding 8 chunks to knowledge graph for document: OpenAI Funding Analysis
2024-01-15 10:30:45,890 - ingestion.graph_builder - INFO - ✓ Added episode openai_funding.md_0_1705312845.123 to knowledge graph (1/8)
2024-01-15 10:30:46,890 - ingestion.graph_builder - INFO - ✓ Added episode openai_funding.md_1_1705312846.456 to knowledge graph (2/8)
...
Progress: 1/5 documents processed
2024-01-15 10:32:15,234 - ingestion.ingest - INFO - Processing file 2/5: documents/microsoft_openai.md
...
Progress: 5/5 documents processed

==================================================
INGESTION SUMMARY
==================================================
Documents processed: 5
Total chunks created: 42
Total entities extracted: 156
Total graph episodes: 42
Total errors: 0
Total processing time: 180.45 seconds

✓ OpenAI Funding Analysis: 8 chunks, 31 entities
✓ Microsoft-OpenAI Partnership: 12 chunks, 45 entities
✓ Google AI Strategy: 7 chunks, 28 entities
✓ Meta AI Developments: 9 chunks, 34 entities
✓ Amazon AI Initiatives: 6 chunks, 18 entities
```

## Considérations importantes

### ⚠️ Temps de traitement
- **Petits documents** (1-5 docs) : 2-5 minutes
- **Corpus moyen** (10-20 docs) : 10-30 minutes  
- **Gros corpus** (50+ docs) : 1+ heure
- Le graphe de connaissances est le plus coûteux en temps

### 💾 Utilisation des ressources
- **RAM** : ~200-500 MB pendant l'ingestion
- **CPU** : Intensif pendant l'extraction d'entités
- **Réseau** : Appels API pour LLM et embeddings
- **Stockage** : ~10-50 MB par document selon la taille

### 🔑 APIs requises
- **LLM API** : Pour le chunking sémantique et l'extraction d'entités
- **Embeddings API** : Pour la génération des vecteurs
- **Bases de données** : PostgreSQL et Neo4j doivent être accessibles

### 🚨 Gestion des erreurs
- **Timeout API** : Retry automatique avec backoff
- **Chunks trop grands** : Troncature automatique
- **Erreurs de parsing** : Document ignoré, traitement continue
- **Échec de connexion** : Arrêt propre avec nettoyage

## Dépannage

### Problèmes courants

**"No markdown files found"**
```bash
# Vérifiez le dossier documents
ls -la documents/
# Ou spécifiez un autre dossier
python -m ingestion.ingest --documents mon_dossier/
```

**"Database connection failed"**
```bash
# Testez votre connexion PostgreSQL
psql "$DATABASE_URL" -c "SELECT 1;"
```

**"Neo4j connection failed"**
```bash
# Vérifiez que Neo4j est démarré
curl -u neo4j:password http://localhost:7474/
```

**"API rate limit exceeded"**
```bash
# Utilisez des modèles locaux ou attendez
# Ou configurez un autre provider dans .env
```

**Chunks trop volumineux pour Graphiti**
```bash
# Réduisez la taille des chunks
python -m ingestion.ingest --clean --chunk-size 600
```

---

**📝 Note** : Ce processus d'ingestion est la base de tout le système. Une fois terminé, votre agent IA pourra utiliser à la fois la recherche vectorielle et le graphe de connaissances pour répondre aux questions de manière intelligente. 