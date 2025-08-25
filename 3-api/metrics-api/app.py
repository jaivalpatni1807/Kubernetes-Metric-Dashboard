import psycopg2
from flask import Flask, jsonify
import datetime
import requests

app = Flask(__name__)

NODE_EXPORTER_URL = "http://node-exporter.metrics-dashboard.svc.cluster.local:9100/metrics"

def get_connection():
    return psycopg2.connect(
        host="timescaledb-0.timescaledb.metrics-dashboard.svc.cluster.local",
        database="metrics",
        user="admin",
        password="admin123"
    )

def scrape_metrics():
    response = requests.get(NODE_EXPORTER_URL)
    metrics = {}
    
    for line in response.text.splitlines():
        if line.startswith("node_cpu_seconds_total{cpu=\"0\",mode=\"user\"}"):
            metrics["cpu_user"] = float(line.split(" ")[1])
        if line.startswith("node_memory_MemAvailable_bytes"):
            metrics["mem_available"] = float(line.split(" ")[1])
        if line.startswith("node_memory_MemTotal_bytes"):
            metrics["mem_total"] = float(line.split(" ")[1])
    
    if "mem_available" in metrics and "mem_total" in metrics:
        metrics["mem_used_percent"] = round(
            (1 - (metrics["mem_available"] / metrics["mem_total"])) * 100, 2
        )
    
    return metrics

@app.route("/metrics", methods=["POST"])
def insert_metrics():
    metrics = scrape_metrics()
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO metrics_table (cpu_usage, memory_usage, timestamp) VALUES (%s, %s, %s)",
        (
            metrics.get("cpu_user", 0),
            metrics.get("mem_used_percent", 0),
            datetime.datetime.utcnow()
        )
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "inserted", "metrics": metrics})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)