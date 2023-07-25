from kubernetes import client, watch
from modules.predictions import make_prediction
from modules.kubernetes_telemetry import get_nodes

token = "eyJhbGciOiJSUzI1NiIsImtpZCI6Ikw4Zl8zS3hzdmN5aVpXVi1lNkRzUVppUzZYLUxSMHI0RDNxdnhRRUgtcGsifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4iLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjRlN2I1YmExLTdhMjgtNGVhMC1iODVhLWI3ZWY5ODE3YTY5OSIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.j980WjWTiosCv-4pjZDSnHwzCadDCpYn5FCRTIO90yJrRqBha5RMpST9NX2N08yjaIYARZwbd7WrvRD0hFfijFtBINTIwXyEXLg4pizVtBmWSvNz44saeZ62_Zql7L6Y1S6OzEqhqMj7YIfs5pGnEDbjrS5vw1qyKIdbB7XFF2YEpe2pFGQe9wWvsg1FxJUG-F6vK4NmXlrdatjhY1d3E_qpUn1YahUgPL8swTMqYwU-ETK1DL7wKUQcJjOoB30G9FSeNFML4JQ3ty4C5t7pxrzq8FJL37xD-mwy6v79Rr1XDVTHgHPMEB7ZeGmjRSI5zGBhO8VN_VXgoa3ebgT2ZQ"

configuration = client.Configuration()
configuration.host = "http://192.168.21.130"
configuration.verify_ssl = False
# configuration.api_key = {"Authorization": "Bearer " + token}

ApiClient = client.ApiClient(configuration)

v1core = client.CoreV1Api(ApiClient)
api_custom = client.CustomObjectsApi(ApiClient)


# Get list of all worker nodes
nodes = get_nodes(v1core.list_node(label_selector="node=worker"))

nodes_set = make_prediction(nodes, v1core.list_node(label_selector="node=worker"), api_custom.list_cluster_custom_object(group="metrics.k8s.io",version="v1beta1", plural="nodes"), 'ssd.json')
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