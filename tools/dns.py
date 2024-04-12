
#!/usr/bin/python3.8

import os
import getopt, sys
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

gandi_api = {'domain': "api.gandi.net/v5/livedns/domains"}
headers   = {'authorization': 'Bearer 78690ba30c3222e1c5c706deac0e63b005b275c4', 'Accept': 'application/json'}


def get_domains():
    entries = []
    response = requests.request("GET", "https://"+gandi_api['domain'], headers=headers)
    domains = { 'fqdn' : [ x['fqdn'] for x in response.json() ], 'url' : [ y['domain_records_href'] for y in response.json() ] }
    return domains

def set_ip_host_record(domain, nameserver, ipaddr):
    """ add an ipv4 type entry """
    if ipaddr is None:
       return None
    hosts_entries = Hosts()
    hosts_entry = HostsEntry(entry_type='ipv4', address=ipaddr,
                             names=[nameserver,(".").join([nameserver,domain])],
                             comment='this is a comment')
    assert hosts_entry.entry_type == 'ipv4'
    assert hosts_entry.address == ipaddr
    assert hosts_entry.names == [nameserver,(".").join([nameserver,domain])]
    assert hosts_entry.comment == 'this is a comment'
    hosts_entries.add(entries=[hosts_entry], force=True)
    hosts_entries.write()

def get_ip_host_record(domain,nameserver) -> str:
    response = requests.request("GET", "https://"+gandi_api['domain']+"/"+domain+"/records", headers=headers)
    if response.json() is not None and 'code' not in  response.json():
       for entry in response.json():
         if nameserver == entry['rrset_name']:
           for namesrvrecord in entry['rrset_values']:
               return namesrvrecord
    return None

def set_ip_host_record(domain, nameserver, ipaddr) -> str:
    payload = "{\"items\":[{\"rrset_type\":\"A\",\"rrset_values\":[\""+ipaddr+"\"]}]}"
    response = requests.request("PUT", "https://"+gandi_api['domain']+"/"+domain+"/records/"+nameserver, data=payload, headers=headers)
    print (response.json())
    return None

def set_alias_host_record(domain,nameserver, alias) -> str:
    payload = "{\"items\":[{\"rrset_type\":\"CNAME\",\"rrset_values\":[\""+alias+"\"]}]}"
    response = requests.request("PUT", "https://"+gandi_api['domain']+"/"+domain+"/records/"+nameserver, data=payload, headers=headers)
    print (response.json())
    return None

def main() -> int:
    """Echo the input arguments to standard output"""
    try:
       ipaddr     = ""
       nameserver = ""
       opts, args = getopt.getopt(sys.argv[1:], "d:n:a:i:", ["help", "output="])
    except getopt.GetoptError as err:
       print(err)
       usage()
       sys.exit(2)
    
    for opt,arg  in opts:
       if opt == "-n":
          nameserver = arg
       if opt == "-d":
          domain = arg
       if opt == "-a":
          alias = arg
          for fqdn in get_domains()['fqdn']:
              set_alias_host_record(fqdn, nameserver, alias)
              ip = get_ip_host_record(fqdn,nameserver)
              print (ip)
       if opt == "-i":
          ipaddr = arg
          for fqdn in get_domains()['fqdn']:
              set_ip_host_record(fqdn, nameserver, ipaddr)
              ip = get_ip_host_record(fqdn,nameserver)
              print (ip)

    return 0

if __name__ == '__main__':
    sys.exit(main()) 
