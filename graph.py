from enum import Enum

class NodeType(Enum):
    Func = "Function"
    Loop = "Loop"
    Iter = "Iteration"
    Load = "Load"
    Type = "Type"
    Cmp = "Cmp"
    Switch = "Switch"
    Case = "Case"
    Branch = "Branch"
    BranchCase = "BranchCase"

class Node:
    def __init__(self, id, type, addr, correction, input, start, end, values):
        self.id = id
        self.type = type
        self.addr = addr
        self.correction = correction
        self.input = input
        self.start = start
        self.end = end
        self.edges = []
        self.values = values

    def add_edge(self, edge):
        self.edges.append(edge)

    def get_edges(self):
        return self.edges

    def get_parent(self):
        if self.id == 0:
            return self.id
        parent = -1
        for edge in self.edges:
            if edge.category == "Belong":
                if parent == -1:
                    parent = edge.to_node
                else:
                    exit(self.__str__() + " has multiple parent")
        if parent != -1:
            return parent
        else:
            exit(self.__str__() + "has no parent")

    def get_childs(self):
        childs = []
        for edge in self.edges:
            if edge.category == "Contain":
                childs.append(edge.to_node)
        return childs
    
    def get_siblings(self, graph):
        if self.id == 0:
            return []
        parent_id = self.get_parent()
        siblings = graph.get_node(parent_id).get_childs()
        siblings.remove(self.id)
        return siblings

    def __str__(self):
        return f"Hash is {self.id}; Type is {self.type}; Start is {self.start}; End is {self.end} Addr is {self.addr}; Correction is {self.correction}; Input is {self.input}"
    
    def print(self):
        print("#Node")
        print(self)
        print("#Edges")
        for edge in self.edges:
            print(edge)
    
    def __json__(self):
        edge_json = [edge.__json__() for edge in self.edges]
        return {
            "id": self.id,
            "category": self.type,
            "addr": self.addr,
            "correction": self.correction,
            "input": self.input,
            "start": self.start,
            "end": self.end,
            "edges": edge_json,
            "values": self.values
        }

class EdgeType(Enum):
    Contain = "Contain"
    Belong = "Belong"

class Edge:
    def __init__(self, from_node, to_node, category, weight=0):
        self.from_node = from_node
        self.to_node = to_node
        self.weight = weight
        self.category = category
    
    def __str__(self):
        return f"{self.from_node}->{self.category}->{self.to_node}"
    
    def get_to_node(self):
        return self.to_node

    def __json__(self):
        return {
            "from_node": self.from_node,
            "to_node": self.to_node,
            "weight": self.weight,
            "category": self.category
        }

class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_node(self, node):
        self.nodes[node.id] = node

    def add_edge(self, edge):
        from_node = self.nodes.get(edge.from_node)
        if not from_node:
            return
        from_node.add_edge(edge)

    def get_node(self, node_id):
        return self.nodes.get(node_id)

    def remove_node(self, node_id):
        node = self.nodes.get(node_id)

        if not node:
            return

        child_node_ids = node.get_childs()
        for child_node_id in child_node_ids:
            self.remove_node(child_node_id)

        parent_id =  node.get_parent()
        parent_node = self.get_node(parent_id)
        if parent_node:
            edges = parent_node.get_edges()
            edges_to_remove = []

            for edge in edges:
                if edge.get_to_node() == node_id:
                    edges_to_remove.append(edge)

            for edge in edges_to_remove:
                edges.remove(edge)

        self.nodes.pop(node_id)

    def remove_edge(self, from_node_id, to_node_id):
        edge = self.edges.get((from_node_id, to_node_id))

        if not edge:
            return

        from_node = self.nodes.get(from_node_id)
        if from_node:
            from_node.edges.pop(self.nodes.get(to_node_id), None)

        self.edges.pop((from_node_id, to_node_id))

    def has_node(self, node_id):
        return node_id in self.nodes

    def has_edge(self, from_node_id, to_node_id):
        return (from_node_id, to_node_id) in self.edges

    def __json__(self):
        nodes_json = {str(node.id) : node.__json__() for node in self.nodes.values()}
        return {
            "nodes": nodes_json
        }
    
class Chunk:
    def __init__(self, start: int, end: int, childs=set()):
        self.start = start
        self.end = end
        self.childs = childs
    
    def __str__(self):
        return f"{self.start}->{self.end}->{self.childs}"

    def __json__(self):
        child_json = [child.__json__() for child in self.childs]
        return {
            "start": self.start,
            "end": self.end,
            "childs": child_json,
        }