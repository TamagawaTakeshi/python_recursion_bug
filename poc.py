import json
import sys
from graph import *

global log_file
global model_graph
global model_nodes
global unique_graphs

    
def chunk_encoder(obj):
    if isinstance(obj, Chunk):
        return obj.__json__()
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def read_graph(path):
    graph = Graph()

    with open(path) as f:
        data = json.load(f)

    for node_id, node_data in data['nodes'].items():
        input = path
        if "input" in node_data:
            input = node_data["input"]
        node = Node(node_data["id"], node_data["category"], node_data["addr"], node_data["correction"], input, node_data["start"], node_data["end"], node_data["values"])
        graph.add_node(node)

    for node_id, node_data in data['nodes'].items():
        for edge in node_data["edges"]:
            if str(edge["to_node"]) in data['nodes'].keys():
                edge = Edge(edge["from_node"], edge["to_node"], edge["category"], edge["weight"])
                graph.add_edge(edge)
    return graph


def graph_to_isi_json(graph: Graph) -> dict:
    data = {}
    for node_idx in graph.nodes:
        node = graph.get_node(node_idx)
        if node == None:
            continue

        if node.id not in data:
            data[node.id] = Chunk(node.start, node.end)
        for child_idx in node.get_childs():
            child = graph.get_node(child_idx)
            if child != None:
                if child.id not in data:
                    data[child.id] = Chunk(child.start, child.end)
                data[node.id].childs.add(data[child.id])
    if 0 in data:
        return data[0]
    else :
        return {}


if __name__ == "__main__":
    sys.setrecursionlimit(17185)
    graph = read_graph("./something.graph")
    isi_json = graph_to_isi_json(graph)
    isi_string = json.dumps(isi_json, default=chunk_encoder)
    with open("test.json", "w") as f:
        f.truncate()
        f.write(isi_string)
