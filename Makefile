# Define variables
APP_NAME = my-kubernetes-project
NAMESPACE = my-kubernetes-project

# Kubernetes commands
deploy:
	helm upgrade --install $(APP_NAME) charts/$(APP_NAME) --namespace $(NAMESPACE) --create-namespace

delete:
	helm uninstall $(APP_NAME) --namespace $(NAMESPACE)

status:
	kubectl get all -n $(NAMESPACE)
