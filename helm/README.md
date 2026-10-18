# Helm chart: devops-demo (phase 4)

Deploys the Flask app to Kubernetes.

What the chart contains:

| File | Purpose |
|---|---|
| `Deployment` | 2 replicas, rolling updates with no downtime, liveness and readiness probes on `/health`, CPU and memory requests and limits |
| `Service` | Internal cluster address (port 80) in front of the pods |
| `Ingress` | Routes `devops-demo.local` to the Service through Traefik (built into k3s) |
| `ConfigMap` | Non-secret settings; pods restart automatically when it changes |

Security settings on the container: runs as a non-root user, read-only root
filesystem, all Linux capabilities dropped, no privilege escalation.

Secrets are never stored in this repo. If the app needs one, create it with
`kubectl create secret generic ...` and set `existingSecret` in the values.

## Deploy

```bash
helm lint helm/devops-demo
helm upgrade --install devops-demo helm/devops-demo --namespace demo --create-namespace
kubectl -n demo get pods
```

## Test

```bash
echo "127.0.0.1 devops-demo.local" | sudo tee -a /etc/hosts
curl http://devops-demo.local/health
curl http://devops-demo.local/metrics | head
```

## Deploy a specific image version

```bash
helm upgrade devops-demo helm/devops-demo -n demo --set image.tag=<commit-sha>
```

## Roll back

```bash
helm history devops-demo -n demo
helm rollback devops-demo 1 -n demo
```

## Remove

```bash
helm uninstall devops-demo -n demo
```
