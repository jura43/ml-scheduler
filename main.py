from kubernetes import client, watch, config
from modules.predictions import make_prediction
from modules.kubernetes_telemetry import get_nodes

config.load_kube_config()

ApiClient = client.ApiClient()

v1core = client.CoreV1Api(ApiClient)
api_custom = client.CustomObjectsApi(ApiClient)


# Get list of all worker nodes
nodes = get_nodes(v1core.list_node(label_selector="node=worker"))


def check(set):
    """
        Function for checking if frontend, backend and database pods have been created, if yes schedule them
    """

    if set['frontend'] and set['backend'] and set['database']:
        print('Scheduling pods...')
        nodes_set = make_prediction(nodes, v1core.list_node(label_selector="node=worker"), api_custom.list_cluster_custom_object(group="metrics.k8s.io",version="v1beta1", plural="nodes"), v1core.list_namespaced_pod("default", watch=False), 'ssd.json')
        schedule(set['frontend'], nodes_set[0][0])
        schedule(set['backend'], nodes_set[0][1])
        schedule(set['database'], nodes_set[0][2])
        print('Prediction time:' + nodes_set[1])
        return True
    
    return False


def schedule(name, node, namespace="default"):
    """
        Function for binding a pod to a node
        Requrires:
            - name of the pod
            - name of the node
    """
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
    app_pods = {} # variable for storing array of pods of single app instance
    print("Waiting for pods...")
    for event in w.stream(v1core.list_namespaced_pod, 'default'):
        if event['type'] == "ADDED" and event['object'].status.phase == "Pending" and event['object'].spec.scheduler_name == 'ml-scheduler':
            try:
                if event['object'].metadata.labels['side'] == 'frontend':
                    app_pods['frontend'] = event['object'].metadata.name
                    if check: app_pods = {}
                if event['object'].metadata.labels['side'] == 'backend':
                    app_pods['backend'] = event['object'].metadata.name
                    if check: app_pods = {}
                if event['object'].metadata.labels['side'] == 'database':
                    app_pods['database'] = event['object'].metadata.name
                    if check: app_pods = {}
            except client.rest.ApiException as e:
                print (e)
    return[0]

if __name__ == '__main__':
    main()