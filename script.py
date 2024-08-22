import psutil
import time
import os
import socket
import threading
import queue
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import logging
import smtplib
from email.mime.text import MIMEText

# InfluxDB connection details
influx_token = "NRFxGRmXv4IUlSqliB__wYF87_1cZhOCMfw1pPzr57_F03Hir-QCwsh8jb3zj8r9qyNy4DUSBB0OlxuxG2jQsw=="
influx_org = "Khushi"
influx_bucket = "e7c65661e55a853b"
influx_url = "https://us-east-1-1.aws.cloud2.influxdata.com/orgs/8eb88cf1b1cd899d"

# Email alert settings
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "khushitulsiyan495@gmail.com"
smtp_password = "khushi@nyu23"
alert_recipient = "somebodyantisocial@gmail.com"

# Initialize InfluxDB client
client = influxdb_client.InfluxDBClient(
    url=influx_url, token=influx_token, org=influx_org
)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Define the metric collection function
def collect_metrics():
    cpu_usage = psutil.cpu_percent(interval=1)
    mem_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    net_io = psutil.net_io_counters()

    data_point = {
        "measurement": "system_metrics",
        "tags": {
            "host": socket.gethostname()
        },
        "fields": {
            "cpu_usage": cpu_usage,
            "mem_usage": mem_usage,
            "disk_usage": disk_usage,
            "net_in": net_io.bytes_recv,
            "net_out": net_io.bytes_sent
        }
    }

    return data_point

# Implement a queue-based approach for data collection and alerting
data_queue = queue.Queue()
alert_queue = queue.Queue()
stop_flag = False

def data_collector():
    while not stop_flag:
        data_point = collect_metrics()
        data_queue.put(data_point)
        time.sleep(5)  # Collect data every 5 seconds

def data_writer():
    while not stop_flag:
        if not data_queue.empty():
            data_point = data_queue.get()
            write_api.write(bucket=influx_bucket, org=influx_org, record=data_point)

def alert_monitor():
    while not stop_flag:
        if not data_queue.empty():
            data_point = data_queue.get()
            if data_point["fields"]["cpu_usage"] > 80 or data_point["fields"]["mem_usage"] > 80 or data_point["fields"]["disk_usage"] > 80:
                alert_queue.put(data_point)
                send_alert(data_point)

def send_alert(data_point):
    host = data_point["tags"]["host"]
    cpu_usage = data_point["fields"]["cpu_usage"]
    mem_usage = data_point["fields"]["mem_usage"]
    disk_usage = data_point["fields"]["disk_usage"]

    message = f"System Anomaly Alert:\nHost: {host}\nCPU Usage: {cpu_usage}%\nMemory Usage: {mem_usage}%\nDisk Usage: {disk_usage}%"

    msg = MIMEText(message)
    msg['Subject'] = 'System Anomaly Alert'
    msg['From'] = smtp_username
    msg['To'] = alert_recipient

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.send_message(msg)

    logging.info(f"Alert sent: {message}")

# Optimize resource utilization in containerized deployments
def optimize_resource_utilization():
    while not stop_flag:
        # Fetch container metrics using Linux system internals
        container_metrics = get_container_metrics()

        # Analyze the metrics and optimize resource allocation
        optimize_container_resources(container_metrics)

        time.sleep(60)  # Check for optimization every minute

def get_container_metrics():
    # Implement logic to fetch container-level metrics using Linux system internals
    # e.g., using cgroups, namespaces, or tools like 'docker stats'
    pass

def optimize_container_resources(container_metrics):
    # Implement logic to optimize resource utilization based on the collected metrics
    # e.g., adjusting CPU shares, memory limits, or triggering auto-scaling mechanisms
    pass

# Start the data collection, writing, and alerting threads
collector_thread = threading.Thread(target=data_collector)
writer_thread = threading.Thread(target=data_writer)
alert_thread = threading.Thread(target=alert_monitor)
optimization_thread = threading.Thread(target=optimize_resource_utilization)

collector_thread.start()
writer_thread.start()
alert_thread.start()
optimization_thread.start()

# Run the monitoring tool
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    stop_flag = True
    collector_thread.join()
    writer_thread.join()
    alert_thread.join()
    optimization_thread.join()
    print("Monitoring tool stopped.")