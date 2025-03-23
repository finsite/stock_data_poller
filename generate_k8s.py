import os
import sys

def create_directory(path):
    os.makedirs(path, exist_ok=True)

def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)

def generate_kustomize_base(app_name, repo_path):
    base_path = os.path.join(repo_path, "k8s", "base")
    create_directory(base_path)

    deployment_yaml = f"""\
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
  labels:
    app: {app_name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
    spec:
      containers:
      - name: {app_name}
        image: {app_name}:latest
        ports:
        - containerPort: 8080
"""

    service_yaml = f"""\
apiVersion: v1
kind: Service
metadata:
  name: {app_name}
spec:
  selector:
    app: {app_name}
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
"""

    kustomization_yaml = f"""\
resources:
  - deployment.yaml
  - service.yaml
"""

    write_file(os.path.join(base_path, "deployment.yaml"), deployment_yaml)
    write_file(os.path.join(base_path, "service.yaml"), service_yaml)
    write_file(os.path.join(base_path, "kustomization.yaml"), kustomization_yaml)

def generate_kustomize_overlays(app_name, repo_path):
    for env in ["dev", "prod"]:
        overlay_path = os.path.join(repo_path, "k8s", "overlays", env)
        create_directory(overlay_path)
        kustomization_yaml = f"""\
resources:
  - ../../base
"""
        write_file(os.path.join(overlay_path, "kustomization.yaml"), kustomization_yaml)

def generate_argocd_application(app_name, repo_path):
    app_path = os.path.join(repo_path, "k8s", "application")
    create_directory(app_path)

    for env in ["dev", "prod"]:
        app_yaml = f"""\
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: {app_name}-{env}
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/my-org/{app_name}.git
    targetRevision: main
    path: k8s/overlays/{env}
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
"""
        write_file(os.path.join(app_path, f"{env}.yaml"), app_yaml)

def generate_helm_chart(app_name, repo_path):
    helm_path = os.path.join(repo_path, "charts", app_name)
    create_directory(helm_path)
    create_directory(os.path.join(helm_path, "templates"))

    chart_yaml = f"""\
apiVersion: v2
name: {app_name}
description: A Helm chart for {app_name}
type: application
version: 0.1.0
appVersion: "1.0"
"""
    values_yaml = f"""\
replicaCount: 1

image:
  repository: {app_name}
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8080
"""
    deployment_yaml = f"""\
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
  labels:
    app: {app_name}
spec:
  replicas: {{ {{ .Values.replicaCount }} }}
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
    spec:
      containers:
      - name: {app_name}
        image: "{{ {{ .Values.image.repository }} }}:{{ {{ .Values.image.tag }} }}"
        ports:
        - containerPort: 8080
"""

    write_file(os.path.join(helm_path, "Chart.yaml"), chart_yaml)
    write_file(os.path.join(helm_path, "values.yaml"), values_yaml)
    write_file(os.path.join(helm_path, "templates", "deployment.yaml"), deployment_yaml)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_k8s.py <app-name>")
        sys.exit(1)

    app_name = sys.argv[1]
    repo_path = os.getcwd()

    generate_kustomize_base(app_name, repo_path)
    generate_kustomize_overlays(app_name, repo_path)
    generate_argocd_application(app_name, repo_path)
    generate_helm_chart(app_name, repo_path)

    print(f"✅ Folder structure and manifests generated for {app_name}.")
    print("Modify before committing to Git.")
