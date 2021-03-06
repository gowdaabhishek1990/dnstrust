'''
'''
from py2neo import neo4j, rel
from py2neo.packages.httpstream.http import SocketError
import datetime

class Graph(object):
    
    ZONE_LABEL = "Zone"
    DOMAIN_LABEL = "Domain"
    ZONE_CONNECTION = "PARENT"
    NAME_SERVER_CONNECTION = "NS"
    CNAME_CONNECTION = "CNAME"
    A_CONNECTION = "A"
    

    def __init__(self, db_path = None):
        """
        Creates the Database we will be using.
        default is neo4j.GraphDatabase service in the computer, but can be changed using any URI in
        the neo4j format.
        """
        try:
            self.handler = neo4j.GraphDatabaseService(db_path)
        except SocketError:
            self.handler = neo4j.GraphDatabaseService(db_path)
            
    def clear(self):
        """
        Clears all the data from the database
        """
        self.handler.clear()
    
    def get_last_timestamp(self, domain = None):
        timestamps = self.get_all_query_timestamps(domain)
        
        if len(timestamps) >= 1:
            return timestamps[-1]
        return str(datetime.date.today())
    
    def link(self, first_node, second_node, connection_type):
        """
        This method links two object of neo4j Node type, with an edge labeled under the given connection_type.
        All types are defined in this class.
        """
        if not self._are_nodes_related(first_node, second_node, connection_type):
            relation = rel(first_node, connection_type, second_node)
            self.handler.create(relation) 
    
    def get_all_query_timestamps(self, domain):
        """
        @return: All the timestamps in which the given domain was queried.
        """
        dates_queried = self.get_indexes(neo4j.Node).keys()
        if domain is None:
            return dates_queried
        return [day for day in dates_queried if self.get_node(domain, day) is not None]
    
    
    def get_node(self, name, timestamp = None):
        """
        @return: A py2neo object, allowing navigation and graph checks on it, or None if no node found.
        """
        if timestamp is None:
            timestamp = self.get_last_timestamp(name)
            
        node = self.get_indexed_node(timestamp, "name", name)
        return node

    #def get_indexed_node(self, timestamp, "name", name):
#
 #       index = self.get_index(neo4j.Node, timestamp)
   #     if index:
    #        nodes = index.get("name",name)

    def get_all_nodes(self, timestamp, query):
        """
        @return: A generator of all nodes in the database at a given timestamp
        """
        index = self.get_indexes(neo4j.Node)[timestamp]
        data = index.query(query)
        return data
        

    def create_node(self, obj, label, timestamp = None):
        """
        @return: The created node.
        """
        if timestamp is None:
            timestamp = self.get_last_timestamp(obj.name)
        
        if label is self.DOMAIN_LABEL:
            node = self.handler.get_or_create_indexed_node(timestamp, "name", obj.name, 
                                                          {"name" : obj.name, "ip": obj.ip,
                                                           "all_ips" : obj.all_ips})
            
            for ip in obj.all_ips:
                ip_node = self.handler.get_or_create_indexed_node(timestamp, "ip", ip, 
                                                          {"ip": ip})
                self.link(node, ip_node, self.A_CONNECTION)
        else:
            node = self.handler.get_or_create_indexed_node(timestamp ,"name", obj.name, 
                                                        {"name" : obj.name})
        node["label"] = label
        return node
    
    def _are_nodes_related(self, nodeA, nodeB, relation_type):
        related_nodes = nodeA.match(rel_type=relation_type)
        for relation in related_nodes:
            if nodeB._id == relation.end_node._id:
                return True
        return False

    def __getattr__(self, attr):
        return getattr(self.handler, attr)
