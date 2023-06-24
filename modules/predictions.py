from .data_normaliztion import data_normalization
from .kubernetes_telemetry import get_nodes_usage
import itertools
import tensorflow as tf

model = tf.keras.models.load_model('test.h5')
    

def make_prediction(nodes_list, nodes_info, nodes_metrics):
    """
    Requires:
        - list of nodes for scheduling
        - v1core.list_node(label_selector="node=worker")
        - api_custom.list_cluster_custom_object(group="metrics.k8s.io",version="v1beta1", plural="nodes")

    Returns set of nodes as a list
    [{set: [], res_time: 50}]
    Example:
    `[minikube01, minikube02, minikube01]`
    """
    nodes_variations = list(itertools.product(nodes_list, repeat=3))
    nodes_usage = get_nodes_usage(nodes_list, nodes_info, nodes_metrics)

    predictions = []

    for n in nodes_variations:
        data = {
            'frontend': [n[0]],
            'backend': [n[1]],
            'database': [n[2]],
            'frontend_cpu_usage': [nodes_usage[n[0]]['cpu_usage']],
            'frontend_memory_usage': [nodes_usage[n[0]]['memory_usage']],
            'frontend_memory_pressure': [nodes_usage[n[0]]['memory_pressure']],
            'frontend_disk_pressure': [nodes_usage[n[0]]['disk_pressure']],
            'backend_cpu_usage': [nodes_usage[n[1]]['cpu_usage']],
            'backend_memory_usage': [nodes_usage[n[1]]['memory_usage']],
            'backend_memory_pressure': [nodes_usage[n[1]]['memory_pressure']],
            'backend_disk_pressure': [nodes_usage[n[1]]['disk_pressure']],
            'database_cpu_usage': [nodes_usage[n[2]]['cpu_usage']],
            'database_memory_usage': [nodes_usage[n[2]]['memory_usage']],
            'database_memory_pressure': [nodes_usage[n[2]]['memory_pressure']],
            'database_disk_pressure': [nodes_usage[n[2]]['disk_pressure']]
            }
        
        data_normal = data_normalization(data)
        with tf.device('/cpu:0'):
            prediction = model.predict(data_normal, verbose=0)
        predictions.append({'set': n, 'pred_time': prediction})

    best_prediction = sorted(predictions, key=lambda t: t['pred_time'])

    return best_prediction[0]['set']