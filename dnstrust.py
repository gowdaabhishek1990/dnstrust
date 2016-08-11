
"""
dnstrust module.

This is the basic API to work with our code.
Example:
>>> g = get_graph()
>>> g.crawl_domain(domain, index)
>>> get_transitive_trust(domain, index)
"""

from crawler import Crawler
from objects import DiffResults, TrustResults
from graph_query import get_all_name_servers_of_domain
import graph_database
import datetime
import random


def get_transitive_trust(domain, timestamp = None, graph = None):
    """
    Gets the transitive trust attribute of a domain as in The list of name servers  
    """
    if graph is None:
        graph = get_graph()
        
    if timestamp is None:
        timestamp = graph.get_last_timestamp(domain)
    
    result = get_all_name_servers_of_domain(domain, graph, timestamp)
    return TrustResults(result)


def get_graph(uri = None):
    """
    @param: URI, indicating the neo4j graph database link. If None is given, the default db in the system
    is retrieved.
    @return: A Graph object, storing the information from dns crawling.
    """
    return graph_database.Graph(uri)
 
# TODO: can easily add changes from any time
def calculate_changes_from_last_check(domain):
    """
    The function queries the transitive trust attribute of a given domain, 
    while differentiating it from previous results.
    
    @return: a DiffResults object from objects module.
    """
    ns_list = get_transitive_trust(domain)
    crawl_domain(domain)
    new_ns_list = get_transitive_trust(domain, _calculate_index())
    diff = DiffResults(ns_list, new_ns_list)
    diff.calculate_diff()
    return diff


def _calculate_index():
    timestamp = str(datetime.date.today())
    return timestamp


def crawl_domain(domain, index = None, days_ttl = 0, graph = None):
    """
    Crawls recursively on a domain, and all of its servers.
    Updates the database with the new data.
    Information can be retrieved using the get methods.
    
    @param days_ttl: Information retrieved in the time window defined by this parameter (was retrieved
    in the last days_ttl days, will not be checked again.
    """
    if graph is None:
        graph = get_graph()
        
    if index is None:
        index = _calculate_index()
        
    crawler_handler = Crawler(domain, index, days_ttl, graph, domain=True)
    crawler_handler.run()
