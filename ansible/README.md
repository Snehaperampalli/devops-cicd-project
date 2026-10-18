# Ansible: provision an Ubuntu host (phase 3)

`site.yml` turns a fresh Ubuntu machine into a Docker + k3s (Kubernetes) host.
It is idempotent, so you can run it again safely.

What it does:

1. Installs Docker (`docker.io`) and lets your user run it without `sudo`
2. Adds a 2 GB swap file if the machine has no swap (helps small VMs)
3. Installs k3s (single-node Kubernetes) and waits for the node to be Ready
4. Copies the kubeconfig to `~/.kube/config` so `kubectl` works without `sudo`

## Run it

```bash
sudo apt install -y ansible-core
cd ansible
ansible-playbook site.yml --ask-become-pass
```

Enter your sudo password at the `BECOME password:` prompt.

## Check the result

```bash
kubectl get nodes          # STATUS should be Ready
kubectl get pods -A        # system pods should be Running
free -h                    # memory and swap
```

## Settings (top of `site.yml`)

| Variable | Default | Meaning |
|---|---|---|
| `swap_size_gb` | `2` | Size of the swap file, skipped if swap already exists |
| `k3s_version` | `""` | Empty = latest stable. Pin a version for reproducible builds |
