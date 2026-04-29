# 🛒 Olist Data Quality Pipeline

Pipeline complet de qualité des données marketing construit sur le dataset [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

> **Contexte** : L'objectif est de démontrer des compétences en Data Engineering, qualité des données et analytics en environnement d'entreprise.

---

## 🏗️ Architecture

```
CSV Olist (11 fichiers)
        ↓
  Python (ingestion)
        ↓
 PostgreSQL raw.*
        ↓
   dbt (staging → marts → quality)
        ↓
PostgreSQL staging.* / marts.* / quality.*
        ↓
 Python (anomaly detection + business rules)
        ↓
  quality.audit_log
        ↓
 Alerting (email + Excel)
        ↓
    Power BI Dashboard
```

---

## 🛠️ Stack technique

| Couche            | Outil                          |
|-------------------|-------------------------------|
| Ingestion         | Python + pandas                |
| Base de données   | PostgreSQL 15 (Docker)         |
| Visualisation DB  | pgAdmin 4 (Docker)             |
| Transformation    | dbt-postgres 1.10.0            |
| Orchestration     | Apache Airflow (Astro CLI)     |
| Qualité           | dbt tests + Python             |
| Anomaly Detection | Z-score + WoW (pandas/numpy)   |
| Alerting          | Email SMTP + Excel (openpyxl)  |
| CI/CD             | GitHub Actions                 |
| Visualisation     | Power BI                       |

---

## 📁 Structure du projet

```
olist-data-quality/
├── .github/
│   └── workflows/
│       ├── ci.yml                  # Lint + tests à chaque push
│       ├── dbt_run.yml             # dbt build sur chaque PR
│       └── deploy.yml              # Validation DAGs sur main
├── airflow/
│   ├── dags/
│   │   ├── dag_daily_pipeline.py   # Pipeline complet (06h00)
│   │   └── dag_quality_check.py    # Checks horaires
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env                        # Variables Airflow Docker
├── alerting/
│   └── email_alert.py              # Email + Excel en pièce jointe
├── dbt_project/
│   ├── macros/
│   │   └── generate_schema_name.sql
│   ├── models/
│   │   ├── staging/                # 11 vues nettoyées
│   │   ├── marts/
│   │   │   ├── dimensions/         # dim_customers, dim_products, dim_sellers, dim_date
│   │   │   └── facts/              # fct_orders, fct_order_items, mart_sales, mart_customers_rfm, mart_marketing
│   │   └── quality/                # 7 checks d'anomalies
│   ├── tests/
│   ├── dbt_project.yml
│   └── profiles.yml
├── ingestion/
│   ├── db_connector.py             # Connexion PostgreSQL
│   └── load_olist.py               # Chargement CSV → raw.*
├── monitoring/
│   ├── anomaly_detection.py        # Z-score + WoW drop
│   ├── business_rules.py           # Règles métier Python
│   └── audit_logger.py             # Persistance audit_log
├── tests/
│   ├── test_ingestion.py
│   ├── test_anomaly_detection.py
│   └── test_business_rules.py
├── docs/
│   ├── architecture.md
│   └── setup.md
├── data/olist/                     # CSV Olist (non versionné)
├── docker-compose.yml              # PostgreSQL + pgAdmin
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Démarrage rapide

### Prérequis

- Docker Desktop
- Python 3.10+
- Astro CLI
- dbt-postgres
- Compte Kaggle (pour les données)

### Installation

```bash
# 1. Cloner le repo
git clone https://github.com/ton-username/olist-data-quality.git
cd olist-data-quality

# 2. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec tes valeurs

# 3. Lancer PostgreSQL + pgAdmin
docker-compose up -d

# 4. Télécharger les données Olist
# https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
# Placer les CSV dans ./data/olist/

# 5. Ingérer les données
python ingestion/load_olist.py --data-dir ./data/olist

# 6. Lancer dbt
cd dbt_project
dbt build --profiles-dir .
cd ..

# 7. Lancer le monitoring
python monitoring/anomaly_detection.py
python monitoring/business_rules.py

# 8. Tester l'alerting
python alerting/email_alert.py
```

---

## 🐳 Docker

| Service    | URL                    | Credentials                          |
|------------|------------------------|--------------------------------------|
| PostgreSQL | `localhost:5433`       | `<your_username>` / `<your_password>`         |
| pgAdmin    | `http://localhost:5051`| `<your_email>` / `<your_password>`   |

### Connexion pgAdmin → PostgreSQL

```
Host     : postgres      ← nom du service Docker
Port     : 5432          ← port interne Docker
Database : olist
Username : <your_username>
Password : <your_password>
```

---

## 🗄️ Schémas PostgreSQL

| Schéma    | Contenu                                      | Outil     |
|-----------|----------------------------------------------|-----------|
| `raw`     | 11 tables brutes (TEXT, 1:1 avec CSV)        | Python    |
| `staging` | 11 vues nettoyées et typées                  | dbt       |
| `marts`   | 9 tables agrégées (dims + facts)             | dbt       |
| `quality` | 7 tables de checks + audit_log               | dbt + Python |

### Tables raw (11)

```
raw.orders              raw.order_items         raw.customers
raw.products            raw.sellers             raw.order_payments
raw.order_reviews       raw.geolocation         raw.closed_deals
raw.marketing_leads     raw.category_translation
```

### Tables marts (9)

```
Dimensions :            Facts :
dim_customers           fct_orders
dim_products            fct_order_items
dim_sellers             mart_sales
dim_date                mart_customers_rfm
                        mart_marketing
```

---

## ✅ Règles de qualité implémentées

### Tests dbt (natifs)

| Règle                         | Modèle          | Type        |
|-------------------------------|-----------------|-------------|
| order_id non null et unique   | stg_orders      | Structurel  |
| order_status valeurs valides  | stg_orders      | Domaine     |
| customer_id non null unique   | stg_customers   | Structurel  |
| product_id non null unique    | stg_products    | Structurel  |
| Prix non null                 | stg_order_items | Structurel  |

### Modèles quality (dbt)

| Modèle                        | Règle                                    | Sévérité  |
|-------------------------------|------------------------------------------|-----------|
| check_order_consistency       | Livraison avant achat                    | Critical  |
| check_zero_revenue            | Commande livrée sans revenu              | Critical  |
| check_duplicate_items         | Doublons dans order_items                | Warning   |
| check_orphan_orders           | Commandes sans client                    | Critical  |
| check_negative_prices         | Prix négatifs ou nuls                    | Critical  |
| check_stale_orders            | Expédié > 30j sans livraison             | Warning   |
| check_payment_reconciliation  | Commande livrée sans paiement            | Critical  |
| quality_summary               | Résumé consolidé de toutes les anomalies | —         |

### Monitoring Python

| Fonction                    | Description                              |
|-----------------------------|------------------------------------------|
| detect_zscore_anomalies()   | Z-score glissant 30 jours (warn=2, crit=3)|
| detect_wow_drop()           | Chute WoW > 30%                          |
| check_payment_mismatch()    | Écart paiements vs items                 |
| check_stale_shipped_orders()| Commandes bloquées                       |
| check_low_review_categories()| Catégories score < 3.0                  |
| check_repeat_purchase_rate()| Taux de réachat (référence: 3.36%)       |

---

## 📊 Résultats du monitoring

```
Anomalies détectées (z-score + WoW) : 75
  → Critical : 3  (dont Black Friday 2017-11-24 : z=5.11)
  → Warning  : 72

Business rules :
  → Payment mismatches     : 12,500 commandes
  → Stale shipped orders   : 1,107 commandes
  → Repeat purchase rate   : 3.36% (problème de rétention)
```

---

## 📧 Alerting

- **Email HTML** avec tableau des anomalies
- **Pièce jointe Excel** colorée (rouge = critical, jaune = warning)
- **DRY_RUN=true** → simulation sans envoi
- **DRY_RUN=false** → envoi réel via Gmail App Password

---

## ⚡ Airflow (Astro CLI)

```bash
cd airflow
astro dev start
```

Interface : **http://localhost:8081** — `admin` / `admin`

### DAGs

| DAG                     | Schedule     | Description                        |
|-------------------------|--------------|------------------------------------|
| olist_daily_pipeline    | `0 6 * * *`  | Ingestion + dbt + monitoring + alert|
| olist_quality_check     | `0 * * * *`  | Checks qualité horaires             |

---

## 🔄 CI/CD (GitHub Actions)

| Workflow       | Déclencheur              | Action                          |
|----------------|--------------------------|---------------------------------|
| `ci.yml`       | Push sur toutes branches | Lint flake8 + pytest            |
| `dbt_run.yml`  | PR touchant dbt_project/ | dbt build + tests               |
| `deploy.yml`   | Merge sur main           | Validation syntaxe DAGs         |

---

## 🧪 Tests

```bash
pytest tests/ -v --cov=monitoring --cov=ingestion
```

| Fichier                      | Tests                              |
|------------------------------|------------------------------------|
| test_ingestion.py            | Normalisation colonnes, NULL handling|
| test_anomaly_detection.py    | Z-score, WoW drop, faux positifs   |
| test_business_rules.py       | Règles métier (logique pure)       |

---

## 📈 Insights business (issus du notebook EDA)

- **Pic de ventes** : novembre 2017 (Black Friday) — revenue x5
- **Taux de réachat** : 3.36% → problème de rétention client
- **12,500 commandes** avec écart entre paiements et items
- **1,107 commandes** expédiées sans livraison confirmée
- **Top états par AOV** : PB (234R$) vs SP (volume élevé, AOV modéré)
- **91.88%** des livraisons arrivent avant la date estimée

---

## 🔒 Sécurité

```
✅ .env dans .gitignore (jamais pushé)
✅ .env.example avec placeholders uniquement
✅ Pas de credentials hardcodés dans le code
✅ Gmail App Password (pas le vrai mot de passe)
⚠️ All credentials are managed via environment variables and are never stored in this repository.
```

---

## 📝 Variables d'environnement

Copie `.env.example` → `.env` et remplis les valeurs :

```bash
# PostgreSQL
DB_HOST=localhost          # host.docker.internal pour Airflow
DB_PORT=5433
DB_NAME=olist
DB_USER=<your_username>
DB_PASSWORD=<your_password>

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<your_email>
SMTP_PASSWORD=<your_app_password> # Gmail App Password (16 chars) with no space
SMTP_SENDER=<your_email>
SMTP_RECEIVER=<your_email>


# Mode
DRY_RUN=true   # false pour envoi réel
```

---

## 👤 Auteur

**Khalifa Seck**

