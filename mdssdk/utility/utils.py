import logging
import re
import threading

from ..constants import PAT_WWN
from ..fcns import Fcns
from ..parsers.switch.show_topology import ShowTopology

log = logging.getLogger()


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def is_pwwn_valid(pwwn):
    newpwwn = pwwn.lower()
    match = re.match(PAT_WWN, newpwwn)
    if match:
        return True
    return False


def get_key(nxapikey, version=None):
    if version in nxapikey.keys():
        return nxapikey[version]
    else:
        return nxapikey["DEFAULT"]


def background(f):
    '''
    a threading decorator
    use @background above the function you want to run in the background
    '''

    def backgrnd_func(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()

    return backgrnd_func


def convert_to_list(items):
    if type(items) is list:
        return items
    else:
        return [items]


def _run_show_topo_for_npiv(sw):
    peer_ip_list = []
    # Show topo
    log.debug("topo")
    out = sw.show("show topology")
    if sw.is_connection_type_ssh():
        shtopo = ShowTopology(out)
        # print(out)
        peer_ip_list = shtopo.get_all_peer_ip_addrs()
    else:
        # alltopo = out['TABLE_topology_vsan']['ROW_topology_vsan']
        alltopo = out.get('TABLE_topology_vsan', [])
        if alltopo:
            for eachvsan in convert_to_list(alltopo['ROW_topology_vsan']):
                # topolines = eachvsan['TABLE_topology']['ROW_topology']
                topolines = eachvsan.get('TABLE_topology', [])
                if topolines:
                    for eachline in convert_to_list(topolines['ROW_topology']):
                        peer_ip_list.append(eachline['peer_ip_address'])

    return list(set(peer_ip_list))


def _run_show_fcns_for_npv(sw):
    peer_ip_list = []
    # Show fcns
    log.debug("Fcns")
    if sw.is_connection_type_ssh():
        out = sw.show("show fcns database detail  | i node-ip | ex 0.0.0.0", raw_text=True).split("\n")
        if out:
            for eachline in out:
                if ":" in eachline:
                    # print(eachline)
                    peer_ip_list.append(eachline.split(':')[1])
    # else:
    #     fcns = Fcns(sw)
    #     out = fcns.database(detail=True)
    #     for eachrow in out:
    #         z = eachrow['TABLE_fcns_database']['ROW_fcns_database']['node_ip_addr']
    #         if z == '0.0.0.0':
    #             continue
    #         peer_ip_list.append(z)
    else:
        fcns = Fcns(sw)
        out = fcns.database(detail=True)
        for eachrow in out:
            # z = eachrow['TABLE_fcns_database']['ROW_fcns_database']['node_ip_addr']
            z = eachrow.get('TABLE_fcns_database', [])
            if z:
                det = convert_to_list(z.get('ROW_fcns_database', []))
                if det:
                    for eachline in det:
                        nodeipdr = eachline['node_ip_addr']
                        if nodeipdr == '0.0.0.0':
                            continue
                        peer_ip_list.append(nodeipdr)

    return list(set(peer_ip_list))
