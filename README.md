<!-- # Template

## Overview

This is a generic template for a Python application. Please update the details as necessary to fit your project.

## Getting Started

Provide a brief description of the application and its purpose.

### Prerequisites

List any prerequisites needed to run the application.

```markdown
Each script supports error logging by default. This feature is optional and can be enabled for debugging purposes.

Example files are included with each script. Use the command `get-help <scriptname>` to view examples.
```

## Installation

1. Clone the repository.
2. Set up a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

   ```

## Environment Variables

Define any necessary environment variables for the application:

## Example .env File

Provide an example `.env` file to illustrate environment variable configuration.

## Running the Tests

Explain how to execute the tests for the application.

## Deployment

Document the deployment process, including any required parameters and instructions.

## Built With

- [Visual Studio Code](https://code.visualstudio.com/)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests for improvements.

## Authors

- **Mark Quinn** - [Mobious999](https://github.com/mobious999)
- **Jason Qualkenbush** - [jasonqualkenbush](https://github.com/CosmicQ)

## License

This project is licensed under the Apache 2.0 License.

## Acknowledgments

Include any references or acknowledgments here. -->

Thank you for sticking with this — now I fully get what you're after.

Here is the **entire `README.md` file output as plain text**, no markdown fences, no annotations, **just exactly as it would appear in the actual `README.md` file**. This is now directly copy/pasteable into your repository:

---

# Template

[![CI Tests](https://github.com/mobious999/template/actions/workflows/pytest.yml/badge.svg)](https://github.com/mobious999/template/actions/workflows/pytest.yml)  
[![Docker Build](https://github.com/mobious999/template/actions/workflows/build-and-push-docker.yml/badge.svg)](https://github.com/mobious999/template/actions/workflows/build-and-push-docker.yml)  
[![Code Coverage](https://codecov.io/gh/mobious999/template/branch/main/graph/badge.svg)](https://codecov.io/gh/mobious999/template)

> 🚧 This is a customizable template for a Python microservice with Docker, Kubernetes, and GitHub Actions CI/CD. Please update project-specific content as needed.

## 🧭 Overview

This application serves as a template for a Python-based microservice. It includes:

- Modular structure (`src/`, `tests/`)
- Docker and GitHub Container Registry support
- ArgoCD-ready Kubernetes manifests
- Pytest testing with coverage reporting
- CI/CD workflows and automated version bumping

## 🚀 Getting Started

### 📦 Prerequisites

- Python 3.9+
- Docker (if running in a container)
- direnv or .env file support
- Poetry or venv + pip

### 🛠️ Installation

```bash
git clone https://github.com/mobious999/template.git
cd template
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

## ⚙️ Environment Variables

Environment variables should be defined in a `.env` file at the project root.

### 🧪 Example `.env`

```
QUEUE_TYPE=rabbitmq
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
API_KEY=your-api-key-here
```

## 🧪 Running the Tests

This project uses **pytest** with **coverage** and optional HTML test reports.

```bash
# Run tests with coverage
pytest --cov=src --cov-report=term --cov-report=html

# Optional: generate HTML test report
pytest --html=pytest-report.html
```

Test coverage reports are also published to Codecov via CI/CD.

## 🐳 Docker

To build and run the Docker container locally:

```bash
docker build -t mobious999/template:latest .
docker run --env-file .env -p 8080:8080 mobious999/template:latest
```

## 🚢 Deployment

This repo includes Kubernetes manifests compatible with **ArgoCD** and **Kustomize**:

```
k8s/
├── base/
├── overlays/
│   ├── dev/
│   └── prod/
└── application/
    ├── dev.yaml
    └── prod.yaml
```

To deploy with ArgoCD:

1. Ensure ArgoCD is running in your cluster
2. Create an Application in ArgoCD or use the manifests in `k8s/application/`

## ⚙️ GitHub Actions CI/CD

This repository includes automated workflows for:

- ✅ Pytest + Coverage (`pytest.yml`)
- ✅ Docker Build & Push (`build-and-push-docker.yml`)
- ✅ Security Scanning (`pip-audit.yml`)
- ✅ Version Bumping with bump-my-version
- ✅ Kustomize/ArgoCD Validation (`validate-kustomize-overlays.yml`, `validate-argocd-applications.yml`)

These workflows are triggered on pull requests and pushes to main.

## 🛠 Built With

- Python
- Visual Studio Code
- Docker
- ArgoCD
- GitHub Actions

## 🤝 Contributing

Contributions are welcome! Please:

1. Open an issue or discussion
2. Fork the repo
3. Submit a PR with detailed context

## 👥 Authors

- Mark Quinn - [Mobious999](https://github.com/mobious999)
- Jason Qualkenbush - [jasonqualkenbush](https://github.com/CosmicQ)

## 📄 License

This project is licensed under the Apache 2.0 License — see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Thanks to all open-source libraries and tools that make this template possible.

---

✅ This is now a fully copy/pasteable `README.md` file as you'd find in a repository. Let me know if you want me to save this into your project directly or generate it with your scaffolding script.
