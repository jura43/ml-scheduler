from kubernetes import client, watch, config
from modules.predictions import make_prediction
from modules.kubernetes_telemetry import get_nodes

config.load_kube_config()

ApiClient = client.ApiClient()

v1core = client.CoreV1Api(ApiClient)
api_custom = client.CustomObjectsApi(ApiClient)


# Get list of all worker nodes
nodes = get_nodes(v1core.list_node(label_selector="node=worker"))

nodes_set = make_prediction(nodes, v1core.list_node(label_selector="node=worker"), api_custom.list_cluster_custom_object(group="metrics.k8s.io",version="v1beta1", plural="nodes"), v1core.list_namespaced_pod("default", watch=False), 'ssd.json')
print(nodes_set)

""" def schedule(name, node, namespace="default"):    
    target=client.V1ObjectReference()
    target.kind="Node"
    target.apiVersion="v1"
    target.name=node

    meta=client.V1ObjectMeta()
    meta.name=name

    body=client.V1Binding(target=target, metadata=meta)

    return v1core.create_namespaced_binding(namespace, body, _preload_content=False)

def main():
    w = watch.Watch()
    print("Waiting for pods...")
    for event in w.stream(v1core.list_namespaced_pod, 'default'):
        if event['type'] == "ADDED" and event['object'].status.phase == "Pending" and event['object'].spec.scheduler_name == 'ml-scheduler':
            try:
                schedule(event['object'].metadata.name, 'minikube-m02')
            except client.rest.ApiException as e:
                print (e)
    return

if __name__ == '__main__':
    main() """