# Zappos Scraper

## setup python project
* clone the repository
* run `pip install -r requirements.txt`

## Prerequisites
* Install [Docker Community Edition (CE)](https://docs.docker.com/engine/installation/) on your workstation.
* Install [Docker Compose](https://docs.docker.com/compose/install/) v1.29.1 or newer on your workstation.

## Setup Apache-Airflow in docker
* Get docker-compose.yaml
```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.6.2/docker-compose.yaml'
```
* create support directories in project folder if not exist
```bash
mkdir -p ./dags ./logs ./plugins ./config
echo -e "AIRFLOW_UID=$(id -u)" > .env
```
* initialize Airflow database
```bash
docker compose up airflow-init
```
* Run Airflow
```bash
docker compose up
```
