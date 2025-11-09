# Use the official Apache Airflow image (Python 3.12 recommended)
FROM apache/airflow:2.9.0-python3.12

USER root
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies for XGBoost and Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgomp1 \
        openjdk-17-jdk-headless \
        procps \
        bash && \
    rm -rf /var/lib/apt/lists/* && \
    ln -sf /bin/bash /bin/sh && \
    mkdir -p /usr/lib/jvm/java-17-openjdk-amd64/bin && \
    ln -s "$(which java)" /usr/lib/jvm/java-17-openjdk-amd64/bin/java

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

WORKDIR /opt/airflow

# Copy requirements
COPY requirements.txt .

USER airflow
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything needed for your project
COPY dags/ dags/
COPY utils/ utils/
COPY datamart/ datamart/
COPY model_store/ model_store/
COPY main.py .

ENV PYTHONPATH="${PYTHONPATH}:/opt/airflow"
