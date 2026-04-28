FROM quay.io/astronomer/astro-runtime:11.3.0
# Installer dbt
RUN pip install dbt-postgres==1.10.0

# Copier le projet dans le conteneur
COPY --chown=astro:astro . /usr/local/airflow/
