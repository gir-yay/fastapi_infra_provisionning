import time
from kubernetes import client, config
import digitalocean
import os
from .config import settings



# === CONFIG ===
DO_TOKEN =  settings.DO_API_KEY
CHECK_INTERVAL = 60  # seconds

# === Kubernetes Setup ===
config.load_kube_config()  # Assumes script runs on the master with access
v1 = client.CoreV1Api()

# === DigitalOcean Setup ===
manager = digitalocean.Manager(token=DO_TOKEN)


def get_pending_pods():
    pods = v1.list_pod_for_all_namespaces().items
    return [p for p in pods if p.status.phase == "Pending" and not p.spec.node_name]


def get_worker_nodes():
    nodes = v1.list_node().items
    return [n for n in nodes if n.metadata.labels.get("node-role.kubernetes.io/master") is None]


def scale_up():
    name = f"{NODE_NAME_PREFIX}-{int(time.time())}"
    print(f"[INFO] Scaling up: creating droplet '{name}'")

    droplet = digitalocean.Droplet(token=manager.token,
                                name = f"node-{int(time.time())}",
                                region='nyc3', # Amster
                                image='187863098', # Ubuntu 20.04 x64
                                size_slug='s-2vcpu-4gb',  # 2GB RAM, 1 vCPU
                                ssh_keys=[46706575], #Automatic conversion
                                vpc_uuid='9263061d-54fb-4123-a46c-6d326318fe80')
    droplet.create()
    print(f"[INFO] Droplet '{name}' creation triggered.")


def scale_down():
    nodes = get_worker_nodes()
    if len(nodes) <= 1:
        print("[INFO] Only one worker node remaining, skipping scale down.")
        return

    for node in nodes:
        node_name = node.metadata.name
        pods = v1.list_pod_for_all_namespaces(field_selector=f"spec.nodeName={node_name}").items
        if not pods:  # No pods running — safe to delete
            print(f"[INFO] Scaling down: deleting node '{node_name}'")
            # You might want to drain the node first
            os.system(f"kubectl drain {node_name} --ignore-daemonsets --delete-local-data")
            os.system(f"kubectl delete node {node_name}")
            # You also need to delete the corresponding droplet
            for droplet in manager.get_all_droplets():
                if droplet.name == node_name:
                    droplet.destroy()
                    print(f"[INFO] Droplet '{node_name}' deleted.")
                    break
            break


def main():
    while True:
        try:
            pending = get_pending_pods()
            print(f"[INFO] Pending pods: {len(pending)}")
            if pending:
                scale_up()
            else:
                scale_down()
        except Exception as e:
            print(f"[ERROR] {e}")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
