# Airflow + Python environment
FROM apache/airflow:2.9.0-python3.12

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

USER airflow

WORKDIR /opt/airflow

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY dags/ dags/
COPY utils/ utils/
COPY datamart/ datamart/
COPY data/ data/
COPY model_store/ model_store/
COPY main.py .

ENV PYTHONPATH="${PYTHONPATH}:/opt/airflow"

CMD ["bash", "-c", "airflow db init && airflow webserver & airflow scheduler"]
