'''
This is a module containing some help methods for basic queries on the TT graph.
'''
from py2neo import neo4j
from sets import Set
import datetime
import graph_database


def get_all_name_servers_of_domain(website_name, db, timestamp=str(datetime.date.today())):
    node = db.get_node(website_name.lower(), timestamp)
    print website_name
    if node is None:
        return {}
    nodes = find_all_related_nodes(node, Set([]))
    nodes = [node for node in nodes if "ip" in node.get_properties()]
    
    ns_dict = {}
    
    for node in nodes:
        name = node["name"]
        if  name is not None:
            ns_dict[name] = node["all_ips"]
        
    return ns_dict

def find_all_related_nodes(node, node_list):
    relation_nodes = node.match_outgoing()
    
    for relation in relation_nodes:
        if relation.end_node not in node_list:
            node_list = node_list.union(Set([relation.end_node]))
            node_list = node_list.union(find_all_related_nodes(relation.end_node, node_list))
            
    return node_list
    