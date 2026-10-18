# GitOps with Argo CD (phase 5)

Git is the single source of truth. Nobody runs `kubectl` or `helm` to deploy.

```
git push (app code)
  -> GitHub Actions: lint, test, build, scan, push image tagged with the commit SHA
  -> Actions commits the new tag into helm/devops-demo/values.yaml
  -> Argo CD sees the change in Git and syncs the cluster
```

## Install Argo CD (pinned to v3.5.2)

```bash
kubectl create namespace argocd
kubectl apply -n argocd --server-side --force-conflicts \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/v3.5.2/manifests/install.yaml
kubectl -n argocd get pods
```

Low-memory tuning: this setup uses local admin login, so the SSO server,
notifications and ApplicationSet controllers are not needed.

```bash
kubectl -n argocd scale deployment \
  argocd-dex-server argocd-notifications-controller argocd-applicationset-controller \
  --replicas=0
```

## Hand the app over to Argo CD

```bash
helm uninstall devops-demo -n demo        # remove the manual Helm install first
kubectl apply -f argocd/application.yaml
kubectl -n argocd get applications
```

The status should reach `Synced` and `Healthy`.

## Open the Argo CD web UI

```bash
kubectl -n argocd port-forward svc/argocd-server 8443:443
```

Open https://localhost:8443 (accept the self-signed certificate warning) and
sign in as `admin`. Get the first password with:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d; echo
```

## Demo: a code change reaches the cluster on its own

1. Edit the message in `app/app.py` (the `/` endpoint) and `git push`.
2. Watch the Actions tab: tests, build, scan, push, then "Update image tag in Git".
3. Within about 3 minutes Argo CD syncs the new tag (press Refresh in the UI to speed it up).
4. `curl http://devops-demo.local/` now shows the new message and the commit SHA as `version`.

## Notes

- Argo CD checks Git every 3 minutes by default (no webhook, since the cluster is a local VM).
- The repo is public, so Argo CD needs no credentials. For a private repo, add a deploy key as a Kubernetes Secret, never in Git.
- Chart, Ansible and docs changes do not trigger CI (`paths-ignore`), so they do not build a new image.
- In larger teams the Helm config usually lives in a separate repo from the app code. One repo keeps this project simple.
- If you enable branch protection that requires pull requests on `main`, the CI bot's direct push will be blocked; allow `github-actions` to bypass it, or move the chart to a separate repo.
