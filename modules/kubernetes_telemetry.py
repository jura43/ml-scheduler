import json

def get_nodes(data):
    """
    Accepts: v1core.list_node()
    Returns: List of nodes that are schedulable and ready
    """
    nodes = []
    for n in data.items:
        if n.spec.unschedulable == None:
            for status in n.status.conditions:
                if status.status == "True" and status.type == "Ready":
                    nodes.append(n.metadata.name)
    return nodes

def get_nodes_usage(nodes_list, nodes_info, nodes_metrics, pods, ssd_json):
    """
    Requires:
      - list of nodes
      - v1core.list_node(label_selector="node=worker")
      - api_custom.list_cluster_custom_object(group="metrics.k8s.io",version="v1beta1", plural="nodes")
      - json filename with ssd configuration

    Returns list of object that contain CPU usage, RAM usage, Memory pressure and Disk pressure

    Example format:
    `[
        node_name: {
        'cpu_usage': 0.1,
        'memory_usage': 0.3,
        'memory_pressure': False,
        'disk_pressure': False,
        'ssd': True,
        'pods': 4
        },
        node_name: {
        'cpu_usage': 0.1,
        'memory_usage': 0.9,
        'memory_pressure': True,
        'disk_pressure': False,
        'ssd': False,
        'pods': 7
        }
    ]`
    """

    with open(ssd_json) as s:
        ssd_nodes = json.load(s)
        
    nodes_usage = {}
    
    for n in nodes_list:
        for i in nodes_info.items:
            if i.spec.unschedulable == None and i.metadata.name == n:
                cpu_alloc = i.status.allocatable['cpu']
                mem_alloc = i.status.allocatable['memory'][:-1][:-1]
                ssd = ssd_nodes[n]
                for status in i.status.conditions:
                    if status.type == "MemoryPressure":
                        mem_press = status.status
                    if status.type == "DiskPressure":
                        disk_press = status.status

        for i in nodes_metrics['items']:
          if i['metadata']['name'] == n:
              cpu_usage = round((int(i['usage']['cpu'][:-1])/1000000)/(int(cpu_alloc)*1000), 2)
              mem_usage = round(int(i['usage']['memory'][:-1][:-1])/int(mem_alloc), 2)

        # Counting pods on a node
        for p in pods.items:
            pods_count = 0
            if p.spec.node_name == n:
                pods_count+=1


        nodes_usage[n] = {'cpu_usage': cpu_usage,
                                'memory_usage': mem_usage,
                                'memory_pressure': mem_press,
                                'disk_pressure': disk_press,
                                'pods': pods_count,
                                'ssd': ssd
                                }

    return nodes_usage