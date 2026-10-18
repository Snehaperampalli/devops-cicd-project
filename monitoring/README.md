# Monitoring: Prometheus + Grafana (phase 6)

A deliberately small monitoring stack for a 4 GB single-node cluster. Plain
Kubernetes files, bundled with Kustomize and deployed by Argo CD.

| Part | What it does | Memory limit |
|---|---|---|
| Prometheus v3.13.4 (LTS) | Scrapes the app's `/metrics` every 30 s, reads pod CPU and memory from the kubelet, evaluates alert rules | 512 Mi |
| Grafana 12.4.3 | Shows the "DevOps Demo App" dashboard (provisioned from Git, nothing to click together) | 300 Mi |

Not included on purpose: Alertmanager, node-exporter and kube-state-metrics,
to save memory. Alerts are visible in the Prometheus UI and on the dashboard;
sending notifications (Slack, email) would need Alertmanager.

## Files

```
monitoring/
  kustomization.yaml            bundles everything, generates the ConfigMaps
  rbac.yaml                     read-only permissions for Prometheus
  prometheus.yaml               Deployment + Service
  grafana.yaml                  Deployment + Service + Ingress (grafana.local)
  config/prometheus.yml         scrape targets
  config/alerts.yml             alert rules
  config/grafana-*.yaml         data source and dashboard loading
  config/devops-demo-dashboard.json   the dashboard
```

## Alert rules

| Alert | Fires when |
|---|---|
| `HighErrorRate` | more than 5% of requests return 5xx for 1 minute |
| `AppPodDown` | a pod stops answering Prometheus for 1 minute |
| `AppDown` | no healthy app pod exists for 1 minute |

## Deploy

```bash
kubectl kustomize monitoring | head -40     # preview what will be created
kubectl apply -f argocd/monitoring-application.yaml
kubectl -n argocd get applications
kubectl -n monitoring get pods
```

## Open it

```bash
echo "127.0.0.1 grafana.local" | sudo tee -a /etc/hosts
```

Then open http://grafana.local. Sign in with `admin` / `admin` and choose a new
password when asked. The dashboard is under Dashboards > DevOps Demo App.

Prometheus has no public address. Use a port-forward:

```bash
kubectl -n monitoring port-forward svc/prometheus 9090:9090
```

Open http://localhost:9090 and check Status > Targets (all should be UP) and
the Alerts page.

## Demo: trigger the alert

```bash
for i in $(seq 1 200); do curl -s -o /dev/null http://devops-demo.local/api/error; done
for i in $(seq 1 100); do curl -s -o /dev/null http://devops-demo.local/health; done
```

Keep sending a mix of requests for a few minutes. The error-rate stat turns red
and `HighErrorRate` moves from Pending to Firing on the Prometheus Alerts page.

## Notes

- Prometheus and Grafana store data in `emptyDir`, so history is lost when a pod restarts. That is fine for a lab. A real setup would use persistent volumes.
- The default Grafana login is `admin` / `admin`. For anything beyond a lab, load the password from a Kubernetes Secret, never from Git.
- Checking memory use: `kubectl top pods -A`
