from kubernetes import client, config
from kubernetes.client.exceptions import ApiException


def deploy_odoo(instance_name):
    odoo_name = f"odoo-{instance_name}"
    postgres_name = f"postgres-{instance_name}"
    
    # Load kubeconfig from ~/.kube/config
    config.load_kube_config()

    apps_v1 = client.AppsV1Api()
    core_v1 = client.CoreV1Api()
    networking_v1 = client.NetworkingV1Api()

    labels_odoo = {"app": odoo_name}
    labels_postgres = {"app": postgres_name}

    # --- PostgreSQL Deployment ---
    postgres_deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name=postgres_name),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector={"matchLabels": labels_postgres},
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=labels_postgres),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name=f"{postgres_name}",
                            image="postgres:15",
                            env=[
                                client.V1EnvVar(name="POSTGRES_DB", value="postgres"),
                                client.V1EnvVar(name="POSTGRES_USER", value="odoo"),
                                client.V1EnvVar(name="POSTGRES_PASSWORD", value="odoo"),
                            ],
                            ports=[client.V1ContainerPort(container_port=5432)],
                            readiness_probe=client.V1Probe(
                                tcp_socket=client.V1TCPSocketAction(port=5432),
                                initial_delay_seconds=5,
                                period_seconds=5,
                            )
                        )
                    ]
                )
            )
        )
    )

    # --- PostgreSQL Service ---
    postgres_service = client.V1Service(
        metadata=client.V1ObjectMeta(name=postgres_name),
        spec=client.V1ServiceSpec(
            selector=labels_postgres,
            ports=[client.V1ServicePort(port=5432)]
        )
    )

    # --- Odoo Deployment ---
    odoo_deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name=odoo_name),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector={"matchLabels": labels_odoo},
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=labels_odoo),
                spec=client.V1PodSpec(
                    init_containers=[
                        client.V1Container(
                            name="wait-for-postgres",
                            image="busybox",
                            command=["sh", "-c", f"until nc -z {postgres_name} 5432; do echo Waiting...; sleep 3; done"]
                        )
                    ],
                    containers=[
                        client.V1Container(
                            name=f"{odoo_name}",
                            image="odoo:17",
                            env=[
                                client.V1EnvVar(name="HOST", value=postgres_name),
                                client.V1EnvVar(name="USER", value="odoo"),
                                client.V1EnvVar(name="PASSWORD", value="odoo"),
                            ],
                            ports=[client.V1ContainerPort(container_port=8069)]
                        )
                    ]
                )
            )
        )
    )

    # --- Odoo Service ---
    odoo_service = client.V1Service(
        metadata=client.V1ObjectMeta(name=odoo_name),
        spec=client.V1ServiceSpec(
            selector=labels_odoo,
            ports=[client.V1ServicePort(port=8069, target_port=8069)]
        )
    )

    # --- Ingress ---
    ingress = client.V1Ingress(
        metadata=client.V1ObjectMeta(
            name=f"{odoo_name}-ingress",
            annotations={
                "nginx.ingress.kubernetes.io/rewrite-target": "/",
                "kubernetes.io/ingress.class": "nginx"
            }
        ),
        spec=client.V1IngressSpec(
            rules=[
                client.V1IngressRule(
                    host=f"{instance_name}.giryay.me",
                    http=client.V1HTTPIngressRuleValue(
                        paths=[
                            client.V1HTTPIngressPath(
                                path="/",
                                path_type="Prefix",
                                backend=client.V1IngressBackend(
                                    service=client.V1IngressServiceBackend(
                                        name=odoo_name,
                                        port=client.V1ServiceBackendPort(number=8069)
                                    )
                                )
                            )
                        ]
                    )
                )
            ]
        )
    )

    # Create all resources
    apps_v1.create_namespaced_deployment(namespace="default", body=postgres_deployment)
    core_v1.create_namespaced_service(namespace="default", body=postgres_service)
    apps_v1.create_namespaced_deployment(namespace="default", body=odoo_deployment)
    core_v1.create_namespaced_service(namespace="default", body=odoo_service)
    networking_v1.create_namespaced_ingress(namespace="default", body=ingress)

    print(f"Deployed Odoo instance '{odoo_name}' and Postgres '{postgres_name}'")




def delete_odoo(instance_name):
    odoo_name = f"odoo-{instance_name}"
    postgres_name = f"postgres-{instance_name}"
    ingress_name = f"{odoo_name}-ingress"

    # Load kubeconfig
    config.load_kube_config()

    apps_v1 = client.AppsV1Api()
    core_v1 = client.CoreV1Api()
    networking_v1 = client.NetworkingV1Api()

    # Define a helper to delete and handle not found errors gracefully
    def safe_delete(func, kind, name):
        try:
            func(name=name, namespace="default")
            print(f"Deleted {kind}: {name}")
        except ApiException as e:
            if e.status == 404:
                print(f"{kind} '{name}' not found.")
            else:
                raise

    # Delete resources
    safe_delete(apps_v1.delete_namespaced_deployment, "Deployment", odoo_name)
    safe_delete(core_v1.delete_namespaced_service, "Service", odoo_name)

    safe_delete(apps_v1.delete_namespaced_deployment, "Deployment", postgres_name)
    safe_delete(core_v1.delete_namespaced_service, "Service", postgres_name)

    safe_delete(networking_v1.delete_namespaced_ingress, "Ingress", ingress_name)

    print(f"All resources for instance '{instance_name}' have been deleted.")

