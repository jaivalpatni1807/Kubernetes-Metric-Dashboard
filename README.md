# Kubernetes Metrics Dashboard

This project demonstrates a comprehensive metrics collection and visualization solution using Kubernetes. It scrapes node metrics, stores them in a time-series database, and visualizes them with Grafana. The entire application is deployed on a Minikube cluster.


## 🚀 Project Overview

This project showcases several key Kubernetes concepts by building a pipeline to:
- **Collect** metrics from each node in the cluster using **node-exporter**.
- **Store** the collected metrics in a **TimescaleDB** database, a time-series database built on PostgreSQL.
- **Process** and expose the metrics via a custom Python **Flask API**.
- **Visualize** the data in a **Grafana** dashboard.
- **Automate** metric scraping and database backups using **CronJobs**.

## ✨ Features

- **Real-time Monitoring**: Visualize CPU and memory usage of your Kubernetes nodes.
- **Scalable**: The API is configured with a **HorizontalPodAutoscaler** to handle varying loads.
- **Persistent Storage**: **StatefulSets** and **PersistentVolumeClaims** ensure that your data is safe.
- **Automated Backups**: A **CronJob** regularly backs up the database.
- **Declarative Deployments**: All components are deployed using Kubernetes YAML manifests.

## 🏛️ Architecture

The project is composed of the following components:

- **TimescaleDB**: A **StatefulSet** to ensure stable storage for our time-series data. It uses a **PersistentVolumeClaim** to store data.
- **Node Exporter**: A **DaemonSet** that runs on every node to collect and expose hardware and OS metrics.
- **Metrics API**: A Python Flask application (**Deployment**) that scrapes metrics from the Node Exporter, processes them, and stores them in TimescaleDB. It's exposed via a **Service** and includes a **HorizontalPodAutoscaler**.
- **Grafana**: A **Deployment** for visualizing the metrics stored in TimescaleDB.
- **CronJobs**:
    - **Metrics Caller**: A **CronJob** that periodically calls the Metrics API to scrape and store new metrics.
    - **Database Backup**: A **CronJob** that performs daily backups of the TimescaleDB database.

## Prerequisites

- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Docker](https://www.docker.com/products/docker-desktop/) (or another container runtime)

## 🛠️ Installation and Deployment

1.  **Start Minikube**:
    ```bash
    minikube start
    ```

2.  **Clone the repository**:
    ```bash
    git clone [https://github.com/jaivalpatni1807/Kubernetes-Metric-Dashboard.git](https://github.com/jaivalpatni1807/Kubernetes-Metric-Dashboard.git)
    cd k8s-metrics-dashboard
    ```

3.  **Create the namespace**:
    ```bash
    kubectl create namespace metrics-dashboard
    ```

4.  **Build the Metrics API Docker image**:
    Navigate to the `3-api/metrics-api` directory and build the image.
    ```bash
    cd 3-api/metrics-api
    eval $(minikube docker-env)
    docker build -t metrics-api:v2 .
    cd ../..
    ```
    *Note: `eval $(minikube -p minikube docker-env)` is used to point your local Docker daemon to the Minikube's Docker daemon. This makes the image available to the Minikube cluster without pushing it to a registry.*

5.  **Apply the Kubernetes manifests in order**:
    ```bash
    # 1. Database
    kubectl apply -f 1-database/
    
    # 2. Node Exporter
    kubectl apply -f 2-node-exporter/

    # 3. API
    kubectl apply -f 3-api/

    # 4. Grafana
    kubectl apply -f 4-grafana/

    # 5. Jobs
    kubectl apply -f 5-jobs/
    ```

## 💻 Usage

1.  **Access Grafana**:
    ```bash
    kubectl port-forward -n metrics-dashboard svc/grafana 3000:3000
    ```
    Open your browser and go to `http://localhost:3000`. The default credentials are `admin`/`admin`.

2.  **Configure Grafana Data Source**:
    - Add a new **PostgreSQL** data source.
    - **Host**: `timescaledb-0.timescaledb.metrics-dashboard.svc.cluster.local:5432`
    - [cite_start]**Database**: `metrics` [cite: 29]
    - [cite_start]**User**: `admin` [cite: 29]
    - [cite_start]**Password**: `admin123` [cite: 33]
    - **SSL Mode**: `disable`
    - Enable **TimescaleDB**.

3.  **Create a Dashboard**:
    - Create a new dashboard and add a panel.
    - Use a query like the following to visualize CPU usage:
      ```sql
      SELECT "timestamp", cpu_usage FROM metrics_table ORDER BY "timestamp";
      ```

## Kubernetes Concepts Showcased

This project utilizes the following Kubernetes concepts:

- [cite_start]**StatefulSet**: For deploying the stateful TimescaleDB database.
- [cite_start]**DaemonSet**: To ensure the `node-exporter` runs on every node.
- [cite_start]**Deployment**: For the stateless `metrics-api` and `grafana` applications.
- [cite_start]**Service**[cite: 21, 48, 106, 125]: To expose the applications within the cluster.
- [cite_start]**HorizontalPodAutoscaler**: To automatically scale the `metrics-api` based on CPU usage.
- [cite_start]**CronJob**: For scheduling periodic tasks like metric scraping and database backups.
- [cite_start]**PersistentVolumeClaim**[cite: 13, 32]: To provide persistent storage for the database and backups.
- [cite_start]**ConfigMap** and **Secret**[cite: 32]: To manage configuration data and secrets.
- [cite_start]**Readiness & Liveness Probes**: To ensure the database is ready to accept connections.
