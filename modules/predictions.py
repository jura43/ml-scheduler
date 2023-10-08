from .data_normaliztion import data_normalization
from .kubernetes_telemetry import get_nodes_usage
import itertools
import tensorflow as tf

model = tf.keras.models.load_model('ml_scheduler_model.keras')
    

def make_prediction(nodes_list, nodes_info, nodes_metrics, pods, ssd):
    """
    Requires:
        - list of nodes for scheduling
        - v1core.list_node(label_selector="node=worker")
        - api_custom.list_cluster_custom_object(group="metrics.k8s.io",version="v1beta1", plural="nodes")
        - list of namespaced pods (v1core.list_namespaced_pod("default", watch=False))
        - json filename with ssd configuraiton

    Returns set of nodes as a list
    [{set: [], res_time: 50}]
    Example:
    `[minikube01, minikube02, minikube01]`
    """
    nodes_variations = list(itertools.product(nodes_list, repeat=3))
    nodes_usage = get_nodes_usage(nodes_list, nodes_info, nodes_metrics, pods, ssd)

    predictions = []

    for n in nodes_variations:
        data = {
            'frontend': [n[0]],
            'backend': [n[1]],
            'database': [n[2]],
            'frontend_cpu_usage': [nodes_usage[n[0]]['cpu_usage']],
            'frontend_memory_usage': [nodes_usage[n[0]]['memory_usage']],
            'frontend_pods': [nodes_usage[n[0]]['pods']],
            'frontend_ssd': [nodes_usage[n[0]]['ssd']],
            'backend_cpu_usage': [nodes_usage[n[1]]['cpu_usage']],
            'backend_memory_usage': [nodes_usage[n[1]]['memory_usage']],
            'backend_pods': [nodes_usage[n[1]]['pods']],
            'backend_ssd': [nodes_usage[n[1]]['ssd']],
            'database_cpu_usage': [nodes_usage[n[2]]['cpu_usage']],
            'database_memory_usage': [nodes_usage[n[2]]['memory_usage']],
            'database_pods': [nodes_usage[n[2]]['pods']],
            'database_ssd': [nodes_usage[n[2]]['ssd']],
            }
        
        data_normal = data_normalization(data)
        prediction = model.predict(data_normal, verbose=0)
        predictions.append({'set': n, 'pred_time': prediction, 'frontend_cpu': nodes_usage[n[0]]['cpu_usage'], 'frontend_ram': nodes_usage[n[0]]['memory_usage'], 'frontend_pods': nodes_usage[n[0]]['pods'], 'frontend_ssd': nodes_usage[n[0]]['ssd'], 'backend_cpu': nodes_usage[n[1]]['cpu_usage'], 'backend_ram': nodes_usage[n[1]]['memory_usage'], 'backend_pods': nodes_usage[n[1]]['pods'], 'backend_ssd': nodes_usage[n[1]]['ssd'], 'database_cpu': nodes_usage[n[2]]['cpu_usage'], 'database_ram': nodes_usage[n[2]]['memory_usage'], 'database_pods': nodes_usage[n[2]]['pods'], 'database_ssd': nodes_usage[n[2]]['ssd']})

    # 1. Sorting by response time
    predictions_sorted = sorted(predictions, key=lambda t: t['pred_time'])

    # 2. Creating new list with sets that are within 10% of best set
    best_time = predictions_sorted[0]['pred_time']
    ten_precent = best_time + best_time*0.1
    sets_for_grade = []

    for n in predictions_sorted:
        if n['pred_time'] <= ten_precent:
            sets_for_grade.append(n)


    # 3. Adding metric to the objects
    for n in range(0, len(sets_for_grade)):
        sets_for_grade[n]['metric'] = 100

    # 4. Calculating set efficiency
    for n in range(0, len(sets_for_grade)):
        # Checking SSD
        if sets_for_grade[n]['frontend_ssd'] == True:
            sets_for_grade[n]['metric'] -= 20

        if sets_for_grade[n]['backend_ssd'] == True:
            sets_for_grade[n]['metric'] -= 20

        if sets_for_grade[n]['database_ssd'] == True:
            sets_for_grade[n]['metric'] -= 0

        # Checking node resource usage
        sets_for_grade[n]['metric'] -= sets_for_grade[n]['frontend_cpu']*8
        sets_for_grade[n]['metric'] -= sets_for_grade[n]['backend_cpu']*8
        sets_for_grade[n]['metric'] -= sets_for_grade[n]['database_cpu']*8
        sets_for_grade[n]['metric'] -= sets_for_grade[n]['frontend_ram']*5
        sets_for_grade[n]['metric'] -= sets_for_grade[n]['backend_ram']*5
        sets_for_grade[n]['metric'] -= sets_for_grade[n]['database_ram']*5

    # 5. Finding most efficient set
    best_prediction = sorted(predictions, key=lambda t: t['metric'], reverse=True)

    return best_prediction[0]['set'], best_prediction[0]['pred_time'][0][0]