"""Generate Kubernetes manifests and folder structure for a given app name.

This script generates the following:

* Kustomize base manifests (deployment and service)
* Kustomize overlays (dev and prod)
* Argo CD application manifests
* Helm chart

The generated files are written to the current working directory.

Example:
$ python generate_k8s.py my-app

"""

import os
import sys


def create_directory(directory_path: str) -> None:
    """Create a directory if it does not already exist.

    :param directory_path: The path to the directory to create.
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory {directory_path}: {e}")
        sys.exit(1)


def write_file(file_path: str, file_content: str) -> None:
    """Write content to a file.

    :param file_path: The path to the file to write.
    :param file_content: The content to write to the file.
    """
    try:
        with open(file_path, "w") as file:
            file.write(file_content)
    except OSError as e:
        print(f"Error writing to file {file_path}: {e}")
        sys.exit(1)


def generate_kustomize_base(app_name: str, repo_path: str) -> None:
    """Generate the Kustomize base manifests.

    The base manifests define the deployment and service for the application.
    The deployment manifest specifies the container image to use and the
    service manifest defines the service port.

    :param app_name: The name of the app.
    :param repo_path: The path to the repository.
    """
    base_path = os.path.join(repo_path, "k8s", "base")
    create_directory(base_path)

    deployment_manifest = f"""\
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

    service_manifest = f"""\
apiVersion: v1
kind: Service
metadata:
  name: {app_name}
spec:
  selector:
    app: {app_name}
  ports:
  - name: http
    port: 80
    targetPort: 8080
"""

    kustomization_manifest = """\
resources:
  - deployment.yaml
  - service.yaml
"""

    write_file(os.path.join(base_path, "deployment.yaml"), deployment_manifest)
    write_file(os.path.join(base_path, "service.yaml"), service_manifest)
    write_file(os.path.join(base_path, "kustomization.yaml"), kustomization_manifest)


def generate_kustomize_overlays(app_name: str, repo_root: str) -> None:
    """Generate the Kustomize overlays for different environments.

    This function creates a Kustomize overlay for each specified environment,
    placing them in the appropriate directory structure under the given repository root.

    :param app_name: The name of the app.
    :param repo_root: The path to the repository root.
    """
    environments = ["dev", "prod"]

    for environment in environments:
        overlay_dir = os.path.join(repo_root, "k8s", "overlays", environment)
        create_directory(overlay_dir)

        kustomization_yaml = """\
resources:
  - ../../base
"""
        write_file(os.path.join(overlay_dir, "kustomization.yaml"), kustomization_yaml)


def generate_argocd_application(app_name: str, repo_path: str) -> None:
    """Generate the Argo CD application manifests.

    Creates Argo CD application manifests for specified environments, defining
    the Git repository, target revision, and Kustomize overlay path for each.

    :param app_name: The name of the app.
    :param repo_path: The path to the repository.
    """
    application_path = os.path.join(repo_path, "k8s", "application")
    create_directory(application_path)

    environments = ["dev", "prod"]
    for environment in environments:
        application_manifest = f"""\
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: {app_name}-{environment}
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/my-org/{app_name}.git
    targetRevision: main
    path: k8s/overlays/{environment}
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
"""
        write_file(os.path.join(application_path, f"{environment}.yaml"), application_manifest)


def generate_helm_chart(app_name: str, repo_root: str) -> None:
    """Generate the Helm chart.

    This function creates a Helm chart directory with necessary files
    and templates for deploying an application.

    :param app_name: The name of the app.
    :param repo_root: The path to the repository root.
    """
    chart_path = os.path.join(repo_root, "charts", app_name)
    create_directory(chart_path)
    create_directory(os.path.join(chart_path, "templates"))

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
  replicas: {{ .Values.replicaCount }}
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
        image: {{ .Values.image.repository }}:{{ .Values.image.tag }}
        ports:
        - containerPort: 8080
"""

    write_file(os.path.join(chart_path, "Chart.yaml"), chart_yaml)
    write_file(os.path.join(chart_path, "values.yaml"), values_yaml)
    write_file(os.path.join(chart_path, "templates", "deployment.yaml"), deployment_yaml)


if __name__ == "__main__":
    """
    Script entry point.

    This script generates the necessary files for a Kubernetes application,
    including a Helm chart, Kustomize overlays, and Argo CD application manifests.

    :param sys.argv[1]: The name of the app.
    """
    if len(sys.argv) != 2:
        print("Usage: python generate_k8s.py <app_name>")
        sys.exit(1)

    app_name: str = sys.argv[1]
    repo_root: str = os.getcwd()

    try:
        # Generate the base Kustomize manifest
        generate_kustomize_base(app_name, repo_root)

        # Generate Kustomize overlays for different environments
        generate_kustomize_overlays(app_name, repo_root)

        # Generate Argo CD application manifests
        generate_argocd_application(app_name, repo_root)

        # Generate a Helm chart
        generate_helm_chart(app_name, repo_root)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
