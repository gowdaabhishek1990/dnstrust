'''
@author: Abhishek
'''
import logging
from objects import Domain, Zone
import graph_database
from dns_query import get_parent_zones, get_name_servers,\
    get_cname_domains

class Crawler(object):
    
    def __init__(self, root, timestamp, days_ttl, graph, domain = True):
        """
        @param domain: Whether the root we are querying is a domain, or a zone (when False).
        """
        if domain:
            self.root = Domain(root)
        else:
            self.root = Zone(root)
        self.timestamp = timestamp
        self.days_ttl = days_ttl
        self.graph = graph

    def run(self):
        """
        Starts the crawler engine.
        After crawling finished, results can be queried using the query modules.
        """
        # Start by building a graph for the current domain
        node = self.get_queried_node(self.root)
        
        if node is not None:
            raise RuntimeError("Domain has already been queried today, not supported yet.")
        
        #if type(self.root) == type(Domain):
        if True:
            domain_node = self.query_domain(self.root)
            
            cnames = get_cname_domains(self.root)
            
            for cname in cnames:
                cname_node = self.query_domain(cname)
                self.graph.link(domain_node, cname_node, self.graph.CNAME_CONNECTION)
            
        else:
            self.query_zone(self.root)
                
            
    def get_queried_node(self, domain):
        return self.graph.get_node(domain.name, self.timestamp)
        
        
    def query_domain(self, domain, with_cnames = False):
        """
        Recursively queries the given domain and its name-servers
        @return: The domain node.
        """
        domain_node = self.get_queried_node(domain)
        if domain_node is not None:
            return domain_node
        
        domain_node = self.graph.create_node(domain, self.graph.DOMAIN_LABEL, self.timestamp)
        
        zone_list = get_parent_zones(domain.name)
        for zone_name in zone_list:
            zone_node = self.query_zone(zone_name)
            self.graph.link(domain_node, zone_node, self.graph.ZONE_CONNECTION)
        
        return domain_node

    def query_zone(self, zone):
        zone_node = self.get_queried_node(zone)
        if zone_node is not None:
            return zone_node
        
        zone_node = self.graph.create_node(zone, self.graph.ZONE_LABEL, self.timestamp)
        
        print "Finding Servers in... %s" % zone
        
        ns_list = get_name_servers(zone)
        
        for ns in ns_list:
            ns_node = self.query_domain(ns)
            self.graph.link(zone_node, ns_node, self.graph.NAME_SERVER_CONNECTION)
        
        return zone_node     
