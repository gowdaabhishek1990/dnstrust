from dns_query import get_domain_ips
from sets import Set


class Domain(object):
    def __init__(self, name1):
        self.name = name1
        try:
            domain_ips = get_domain_ips(self.name)
            self.ip = domain_ips[0]
            self.all_ips = domain_ips
        except ValueError:
            file("C:\Failed.txt", "w").write(name1 + "\n")
            self.ip = "0.0.0.0"
            self.all_ips = ["0.0.0.0"]

    def __repr__(self):
        return "Domain: %s at %s" % (self.name, self.ip)


class Zone(object):
    def __init__(self, name):
        self.name = name.lower()

    def __repr__(self):
        return "Zone: %s" % (self.name)


class TrustResults(object):
    results = None

    def __init__(self, results={}):
        self.results = results

    def pretty_print(self):
        stream = ""
        for ns in self.results.keys():
            stream += "NS:%s at IP:%s\n" % (ns, self.results[ns])
        return stream


class DiffResults(object):
    # FIXME to handle some ips together in a result.
    ns_changes = []
    ip_changes = []

    def __init__(self, previous, current):
        self.previous = previous
        self.current = current

    def calculate_diff(self):
        for ns in self.current.results.keys():

            if ns not in self.previous.results.keys():
                # New Name server
                self.ns_changes.append((ns, self.current.results[ns]))
            else:
                old_ip_set = Set(self.previous.results[ns])
                new_ip_set = Set(self.current.results[ns])

                if new_ip_set != old_ip_set:
                    new_ips_added = new_ip_set - old_ip_set
                    old_ips_lost = old_ip_set - new_ip_set
                    self.ip_changes.append((ns, new_ips_added, old_ips_lost))

    def pretty_print(self):
        stream = ""
        for ip_change_tuple in self.ip_changes:
            prev_ips = ";".join(list(ip_change_tuple[2]))
            new_ips = " ; ".join(list(ip_change_tuple[1]))
            stream += "New IPs:%s for NS:%s -  instead of:%s\n" % (prev_ips, ip_change_tuple[0], new_ips)
        for ns_change_tuple in self.ns_changes:
            stream += "New NS:%s at IP:%s\n" % ns_change_tuple
        return stream
