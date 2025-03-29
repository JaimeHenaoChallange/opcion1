import subprocess
import time
import requests
import os

# Configura tus variables
ARGOCD_SERVER = "http://argocd-server.argocd.svc.cluster.local"  # Cambia esto si es necesario
ARTIFACT_NAME = "hello-world-kubeops"  # Cambia esto por el nombre de tu aplicación
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")  # Obtén la URL de Slack desde las variables de entorno

def check_health():
    result = subprocess.run(
        ["argocd", "app", "get", ARTIFACT_NAME, "--output", "json"],
        capture_output=True,
        text=True
    )
    return result.stdout

def deploy():
    for attempt in range(5):
        print(f"Intentando desplegar {ARTIFACT_NAME}, intento {attempt + 1}")
        subprocess.run(["argocd", "app", "sync", ARTIFACT_NAME])
        time.sleep(10)  # Espera un poco antes de verificar el estado
        health = check_health()
        if "Healthy" in health:
            print(f"{ARTIFACT_NAME} está healthy.")
            return True
    return False

def notify_slack(message):
    requests.post(SLACK_WEBHOOK_URL, json={"text": message})

if __name__ == "__main__":
    if not deploy():
        print(f"{ARTIFACT_NAME} sigue en estado degraded. Pausando...")
        subprocess.run(["argocd", "app", "pause", ARTIFACT_NAME])
        notify_slack(f"{ARTIFACT_NAME} está en estado degraded y ha sido pausado.")