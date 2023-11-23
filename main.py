import json
import datetime
import os
import re
import time
import requests
import math
import threading
import zulu
import websocket
from APModule import *
from playsound import playsound

_db, _autorem, _background_q, _background_q2, _background_q3, noti_on, auto_rem_pass = True, False, True, True, True, False, False

ab_thres_val = 1440  # 24 Hours
noti_thres = 30  # 30 seconds
ip_array, _aq = [], []
epoch_time = int(time.time())

usr_name, usr_prompt, _cook, _ipdbKey, cookie_session = '', '', '', '', ''

auth_json, blkadd_json, blkdel_json, blkquery_json, qquery_json, ccon_json, msearch_json, dsearch_json, usr_json, act_json, assgn_json, alres_json, alrem_json, alroot_json, sc_ips, org_id, watchlist, ip_feed = {
}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}
intro_graphic = """
           _____             _   _          _  __     _______ _______             _____ _____ _____  _____ _______ 
     /\   |  __ \      /\   | \ | |   /\   | | \ \   / / ____|__   __|     /\    / ____/ ____|_   _|/ ____|__   __|
    /  \  | |__) |    /  \  |  \| |  /  \  | |  \ \_/ / (___    | |       /  \  | (___| (___   | | | (___    | |   
   / /\ \ |  ___/    / /\ \ | . ` | / /\ \ | |   \   / \___ \   | |      / /\ \  \___  \\___ \  | |  \___ \   | |   
  / ____ \| |       / ____ \| |\  |/ ____ \| |____| |  ____) |  | |     / ____ \ ____) |___) |_| |_ ____) |  | |   
 /_/    \_\_|      /_/    \_\_| \_/_/    \_\______|_| |_____/   |_|    /_/    \_\_____/_____/|_____|_____/   |_|   
                                                                                                                                                                                                               
"""
queue_graphic = """
    ____                          __  __                                   
   / __ \                        |  \/  |                                  
  | |  | |_   _  ___ _   _  ___  | \  / | __ _ _ __   __ _  __ _  ___ _ __ 
  | |  | | | | |/ _ \ | | |/ _ \ | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|
  | |__| | |_| |  __/ |_| |  __/ | |  | | (_| | | | | (_| | (_| |  __/ |   
  \___\_\ \__,_|\___|\__,_|\___| |_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|   
                                                           __/ /          
                                                          |___/           
"""
watchlist_graphic = """
 __          __   _       _     _ _     _   
 \ \        / /  | |     | |   | (_)   | |  
  \ \  /\  / /_ _| |_ ___| |__ | |_ ___| |_ 
   \ \/  \/ / _` | __/ __| '_ \| | / __| __|
    \  /\  / (_| | || (__| | | | | \__ \ |_ 
     \/  \/ \__,_|\__\___|_| |_|_|_|___/\__|
                                            
"""
threat_graphic = """
  _______ _                    _     ______            _ 
 |__   __| |                  | |   |  ____|          | |
    | |  | |__  _ __ ___  __ _| |_  | |__ ___  ___  __| |
    | |  | '_ \| '__/ _ \/ _` | __| |  __/ _ \/ _ \/ _` |
    | |  | | | | | |  __/ (_| | |_  | | |  __/  __/ (_| |
    |_|  |_| |_|_|  \___|\__,_|\__| |_|  \___|\___|\__,_|
                                                         
"""
org_graphic = """

   ____                        _          _   _                 
  / __ \                      (_)        | | (_)                
 | |  | |_ __ __ _  __ _ _ __  _ ______ _| |_ _  ___  _ __  ___ 
 | |  | | '__/ _` |/ _` | '_ \| |_  / _` | __| |/ _ \| '_ \/ __|
 | |__| | | | (_| | (_| | | | | |/ / (_| | |_| | (_) | | | \__ \\
  \____/|_|  \__, |\__,_|_| |_|_/___\__,_|\__|_|\___/|_| |_|___/
              __/ |                                             
             |___/    
                                                       
"""
block_graphic = """
  ____  _            _    _ _     _   
 |  _ \| |          | |  | (_)   | |  
 | |_) | | ___   ___| | _| |_ ___| |_ 
 |  _ <| |/ _ \ / __| |/ / | / __| __|
 | |_) | | (_) | (__|   <| | \__ \ |_ 
 |____/|_|\___/ \___|_|\_\_|_|___/\__|
                                                                    
"""
qauto_graphic = """
   ____                                        _                        _   _             
  / __ \                            /\        | |                      | | (_)            
 | |  | |_   _  ___ _   _  ___     /  \  _   _| |_ ___  _ __ ___   __ _| |_ _  ___  _ __  
 | |  | | | | |/ _ \ | | |/ _ \   / /\ \| | | | __/ _ \| '_ ` _ \ / _` | __| |/ _ \| '_ \ 
 | |__| | |_| |  __/ |_| |  __/  / ____ \ |_| | || (_) | | | | | | (_| | |_| | (_) | | | |
  \___\_ \\__,_|\___|\__,_|\___| /_/    \_\__,_|\__\___/|_| |_| |_|\__,_|\__|_|\___/|_| |_|
                                                                                          
"""
cookies = {
    'session_token': 'YOUR_SESSION_TOKEN_HERE',  # Replace with a placeholder or remove
}
headers = {
    'authority': 'API_AUTHORITY_PLACEHOLDER',  # Replace with a placeholder
    'origin': 'ORIGIN_PLACEHOLDER',            # Replace with a placeholder
}
grey_headers = {
    "accept": "application/json",
    "key": "YOUR_API_KEY_HERE",                # Replace with a placeholder or remove
}

alertcountervar = 0

def alrt_ctr(_tv):
    global alertcountervar
    _t1 = {}
    if _tv == "Reset":
        with open("tempday.json", "w") as f:
            _t1["Alerts"] = 0
            json.dump(_t1, f)
            f.close()
    elif _tv == "Update":
        with open("tempday.json", "w") as f:
            _t1["Alerts"] = alertcountervar
            json.dump(_t1, f)
            f.close()
    elif _tv == "Restore":
        with open("tempday.json", "r") as f:
            _t1 = json.load(f)
            alertcountervar = _t1["Alerts"]
            f.close()

def grey_n(_ip):
   url = "https://API_ENDPOINT_PLACEHOLDER/community/" + _ip
    response = requests.get(url, headers=grey_headers)
    resp_g = response.json()
    
def unqueue_pass():
    while True:
        _gen = []
        if auto_rem_pass:
            response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                                    cookies=cookies, headers=headers, json=qquery_json)
            resp_data = response.json()
            for i in resp_data["data"]["workQueue"]["work_queueitems"]:
                try:
                    if (i["queue_status"] == "unAssigned") and (i["assigned_to"] == None):
                        if i["regarding"]["name"] == "User Password Change - Log":
                            _gen.append(i)
                except TypeError:
                    None
            for i in _gen:
                same_pass((i["regarding"]["id"])[7:])
            time.sleep(30)
        if (not t1.is_alive()):
            break

def pass_man():
    global auto_rem_pass
    clear()
    print(intro_graphic)
    print("1 - Enable Password Change Auto-Resolve\n2 - Disable Password Change Auto-Resolve")
    _tx = sani(int, "Please make a selection: ", [1, 2])
    if _tx == 1:
        auto_rem_pass = True
    elif _tx == 2:
        auto_rem_pass = False

def same_pass(_a):
    global auto_rem_pass
    source_l, ip_l = [], []
    subject_l = ''
    fm_ = False
    alroot_json["variables"]["id"] = _a
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=alroot_json)
    
    if response.status_code != 200:
        input("error with request", response.status_code)
        return None
    resp_data = response.json()
    _org = org_id[str(resp_data["data"]["alert"]["int_account_id"])][0]
    _orgid = resp_data["data"]["alert"]["int_account_id"]
    if resp_data["data"]["alert"]["name"] == "User Password Change - Log" :
        for i in resp_data["data"]["alert"]["sources"]:
            source_l.append(i["external_id"])
        subject_l = resp_data["data"]["alert"]["primary_subject"]["key"]
        ep = resp_data["data"]["alert"]["created"]
        ep2 = resp_data["data"]["alert"]["modified"]
        timestamp_start = datetime.datetime.strptime(ep, "%Y-%m-%dT%H:%M:%S.%fZ")
        timestamp_start = timestamp_start - datetime.timedelta(hours=6)
        timestamp_start2 = datetime.datetime.strptime(ep2, "%Y-%m-%dT%H:%M:%S.%fZ")
        timestamp_start2 = timestamp_start2 - datetime.timedelta(hours=4)
        ep_s = timestamp_start.strftime('%s')
        ep_n = timestamp_start2.strftime('%s')
        while len(ep_s) != 13:
            ep_s = ep_s + '0'
        while len(ep_n) != 13:
            ep_n = ep_n + '0'
        
        msearch_json["variables"]["sources"] = source_l
        msearch_json["variables"]["subject"] = subject_l
        
        msearch_json["variables"]["id"] = resp_data["data"]["alert"]["triggering_rule"]["id"]
        response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                                cookies=cookies, headers=headers, json=msearch_json)
        resp_data = (response.json())["data"]["ruleMonitor"]["createQuery"]
        _index = resp_data["index"][0]
        _index = '{"index":"'+_index+'","ignore_unavailable":true}'
        del resp_data["index"]
        resp_data["size"] = 500
        resp_data["query"]["bool"]["filter"][0]["range"]["@timestamp"]["gte"] = int(ep_s)
        resp_data["query"]["bool"]["filter"][0]["range"]["@timestamp"]["lte"] = int(ep_n)
        resp_data["sort"] ={"@timestamp": {"order": "asc"}}
        del resp_data["alias"]
        _body =  json.dumps(resp_data)
        _tres = _index+'\n'+_body +'\n'
        x_headers = {
            'authority': 'R3D4CT3D.REDACTED.com',
            'origin': 'https://R3D4CT3D.REDACTED.com',
        }
        if auto_rem_pass:
            response = requests.post('https://R3D4CT3D.REDACTED.com/esquery/_msearch',
                                    cookies=cookies, headers=x_headers, data=_tres)
            if response.status_code != 200:
                None
            else:
                resp_data = response.json()
                for i in resp_data["responses"][0]['hits']['hits']:
                    if i["_source"]["EventData"]["TargetUserName"] != i["_source"]["EventData"]["SubjectUserName"]:
                        fm_ = False
                        break
                    else:
                        fm_ = True
                    
                if fm_ and auto_rem_pass:
                    assign_alert(_a)
                    close_alert(_a)
                    print(f'ALERT: https://R3D4CT3D.REDACTED.com/app/alerts/{_a} AUTO RESOLVED')
          
def m_search(_a): # Function for alert to blocklist query
    source_l = []
    subject_l = []
    qip_l, intp_l = [], []
    alroot_json["variables"]["id"] = _a
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=alroot_json)
    
    if response.status_code != 200:
        input("error with request", response.status_code)
        return None
    resp_data = response.json()
    _org = org_id[str(resp_data["data"]["alert"]["int_account_id"])][0]
    _orgid = resp_data["data"]["alert"]["int_account_id"]
    if resp_data["data"]["alert"]["name"] != "Inbound System Exploit Detected by Network IDS - IDS" and resp_data["data"]["alert"]["name"] != "Outbound System Exploit Detected by Network IDS - IDS" and resp_data["data"]["alert"]["name"] != "Critical Risk Application Usage - Alert":
        dsearch_json["variables"]["id"] = resp_data["data"]["alert"]["triggering_rule"]["id"]
        dsearch_json["variables"]["parent"]["id"] = _a
        response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                                cookies=cookies, headers=headers, json=dsearch_json)
        resp_data = response.json()
        for i in resp_data["data"]["detections"]["edges"]:
            try:
                qip_l.append(i["node"]["data"]["destination"]["ip"])
                qip_l.append(i["node"]["data"]["source"]["ip"])
            except KeyError:
                try:
                    qip_l.append(i["node"]["data"]["client"]["ip"])
                except KeyError:
                    qip_l.append(i["node"]["data"]["source"]["ip"][0])
    else:
        for i in resp_data["data"]["alert"]["sources"]:
            source_l.append(i["external_id"])
        for i in resp_data["data"]["alert"]["subjects"]:
            subject_l.append(i["key"])
        ep = resp_data["data"]["alert"]["created"]
        ep2 = resp_data["data"]["alert"]["modified"]
        timestamp_start = datetime.datetime.strptime(ep, "%Y-%m-%dT%H:%M:%S.%fZ")
        timestamp_start = timestamp_start - datetime.timedelta(hours=6)
        timestamp_start2 = datetime.datetime.strptime(ep2, "%Y-%m-%dT%H:%M:%S.%fZ")
        timestamp_start2 = timestamp_start2 - datetime.timedelta(hours=4)
        ep_s = timestamp_start.strftime('%s')
        ep_n = timestamp_start2.strftime('%s')
        while len(ep_s) != 13:
            ep_s = ep_s + '0'
        while len(ep_n) != 13:
            ep_n = ep_n + '0'
        
        msearch_json["variables"]["sources"] = source_l
        msearch_json["variables"]["subjects"] = subject_l
        
        msearch_json["variables"]["id"] = resp_data["data"]["alert"]["triggering_rule"]["id"]
        response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                                cookies=cookies, headers=headers, json=msearch_json)
        resp_data = (response.json())["data"]["ruleMonitor"]["createQuery"]
        _index = resp_data["index"][0]
        _index = '{"index":"'+_index+'","ignore_unavailable":true}'
        del resp_data["index"]
        resp_data["size"] = 500
        resp_data["query"]["bool"]["filter"][0]["range"]["@timestamp"]["gte"] = int(ep_s)
        resp_data["query"]["bool"]["filter"][0]["range"]["@timestamp"]["lte"] = int(ep_n)
        resp_data["sort"] ={"@timestamp": {"order": "asc"}}
        del resp_data["alias"]
        _body =  json.dumps(resp_data)
        _tres = _index+'\n'+_body +'\n'
        x_headers = {
            #REDACTED
        }
        response = requests.post('https://R3D4CT3D.REDACTED.com/esquery/_msearch',
                                cookies=cookies, headers=x_headers, data=_tres)
        resp_data = response.json()
        for i in resp_data["responses"][0]['hits']['hits']:
            qip_l.append(i['_source']['srcip'])
            qip_l.append(i['_source']['dstip'])
    qip_l = list(set(qip_l))
    _ac_ch = check_activity(_org)
    if _ac_ch == '*':
        print("Blocklist ACTIVE!")
    else:
        print("Blocklist INACTIVE!")
    for i in qip_l:
        if (not ip_in_prefix(i, '10.0.0.0/8')) and (not ip_in_prefix(i, '172.16.0.0/11')) and (not ip_in_prefix(i, '192.168.0.0/16')):
            _gtx = grey_n(i)
            _ipcoa = ipdb_query(i)
            if _gtx:
                print(f'{i} - {_ipcoa[0]}% Confidence of Abuse IPDB - Domain: {_ipcoa[1]} - Classification: {_gtx["classification"]}  Name: {_gtx["name"]}   RIOT: {_gtx["riot"]}')
            else:
                print(f'{i} - {_ipcoa[0]}% Confidence of Abuse IPDB  - Domain: {_ipcoa[1]}')
            if not list_pull(str(_orgid), i):
                if _ipcoa[0] != 0:
                    _bx = sani(str, "\nAdd to blocklist manual (m), add to blocklist automatic(a) or skip (enter)?: ", ['y','a','m',''])
                else:
                    _bx = ''
                if _bx == 'm':
                    _tbx = input("Please enter description: ")
                    print('\n')
                    block_ip(_org, [i], _tbx, True )
                elif _bx == 'a':
                    try:
                        _ipcoa = int(_ipcoa)
                        if _gtx and _gtx["message"] == "Success":
                           _tdx = str(_ipcoa) + "% Confidence of abuse" + "Classification: " +_gtx["classification"] + " Name: " + _gtx["name"]
                        else:
                            _tdx = str(_ipcoa) + "% Confidence of abuse"
                    except TypeError:
                        if _gtx and _gtx["message"] == "Success":
                            _tdx = "Classification: " +_gtx["classification"] + " Name: " + _gtx["name"]
                        else:
                            _tdx = "Abusive IP"
                    block_ip(_org, [i], _tdx, True )
                else:
                    print("SKIPPED")
        else:
            intp_l.append(i)
    if intp_l == qip_l:
        print("No Public IPs Found")
    else:
        print("Internal IPs Skipped: ", intp_l)
    print("Press enter to continue: ")
        

def data_sync(_s=False):  # Function to import data and normalize from JSON
    # True - Write to File
    # False - Read from file
    global auth_json, blkadd_json, blkdel_json, blkquery_json, qquery_json, ccon_json, msearch_json, dsearch_json, usr_json, act_json, assgn_json, alres_json, alrem_json, alroot_json, sc_ips, org_id, ip_feed, _ipdbKey, cookie_session
    _t = {}
    if not _s:
        with open("appdata.json", "r") as f:
            _t = json.load(f)
            cookie_session = _t["APCookie"]
            _ipdbKey = _t["IPDBKey"]
            ip_feed = _t["TF"]
            auth_json = _t["auth"]
            ccon_json = _t["clientconnections"]
            blkadd_json = _t["blkadd"]
            blkdel_json = _t["blkdel"]
            blkquery_json = _t["blkquery"]
            qquery_json = _t["Qquery"]
            sc_ips = _t["ScannerIPs"]
            org_id = _t["orgid"]
            usr_json = _t["userquery"]
            act_json = _t["alertactivity"]
            assgn_json = _t["alertassign"]
            alres_json = _t["alertresolve"]
            alrem_json = _t["alertqueueremove"]
            alroot_json = _t["alertrootquery"]
            msearch_json = _t["alertmsearch"]
            dsearch_json = _t["alertnormalsearch"]
        cookie_sync()
        with open("appdata.json", "r") as f:
            assgn_json["variables"]["UserID"] = get_sysid()
            f.close()
    if _s:
        cookie_sync()
        with open("appdata.json", "w") as f:
            _t["TF"] = ip_feed
            _t["auth"] = auth_json
            _t["clientconnections"] = ccon_json
            _t["blkadd"] = blkadd_json
            _t["blkdel"] = blkdel_json
            _t["blkquery"] = blkquery_json
            _t["Qquery"] = qquery_json
            _t["ScannerIPs"] = sc_ips
            _t["orgid"] = org_id
            _t["userquery"] = usr_json
            _t["alertactivity"] = act_json
            _t["alertassign"] = assgn_json
            _t["alertresolve"] = alres_json
            _t["alertqueueremove"] = alrem_json
            _t["alertrootquery"] = alroot_json
            _t["IPDBKey"] = _ipdbKey
            _t["APCookie"] = cookie_session
            _t["alertmsearch"] = msearch_json
            _t["alertnormalsearch"] = dsearch_json
            json.dump(_t, f)
            f.close()


def cookie_sync():  # Function to sync cookie
    global cookies, cookie_session
    cookies["REDACTED_session"] = cookie_session
    response = requests.post(
        'https://R3D4CT3D.REDACTED.com/g/graphql', cookies=cookies, headers=headers, json=auth_json)
    if response.status_code != 200:
        while True:
            cookie_session = sani(str, "Please enter cookie: ", False)
            cookies["REDACTED_session"] = cookie_session
            response = requests.post(
                'https://R3D4CT3D.REDACTED.com/g/graphql', cookies=cookies, headers=headers, json=auth_json)
            if response.status_code == 200:
                break
            else:
                print("Invalid cookie!")


def active_alert_query(alertid): # Function to check activity of alerts (Communications)
    _tmp = []
    act_json["variables"]["id"] = alertid
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=act_json)
    resp_data = response.json()
    for i in resp_data["data"]["activitiesRegarding"]:
        if i["activity_type"] == "email":
            _tmp.append(i)
            break
    if (len(_tmp) > 0) and _tmp[0]["to"] != None:
        if _tmp[0]["from"] != None and _tmp[0]["from"]["address"] != None:
            return [True, _tmp[0]['created']]
        return [False, _tmp[0]['created']]
    else:
        return [False, None]


def org_add():  # Function to add organizations
    global org_id
    clear()
    print(intro_graphic)
    _a = sani(int, "Please enter Organization ID number: ", False)
    _b = sani(str, "Please enter Organization Blocklist ID: ", False)
    _c = sani(str, "Please enter Organization Name: ", False)
    org_id[_a] = [_b, _c]
    data_sync(True)
    print("Organization Added! Press Enter to Continue: ")


def threat_manager():  # Function to add and remove threat feed entries
    global ip_feed
    clear()
    while True:
        counter = 0
        for i in ip_feed:
            counter = counter + 1
            print(f'{counter} - URL: {ip_feed[i]} DESCRIPTION: {i}')
        _tmpint = sani(
            str, "Would you like to Add(a) or Remove(r)?: ", ['a', 'r'])
        if _tmpint == 'a':
            _tmpurl = sani(str, "Please enter threat feed URL: ", False)
            _tmpdesc = sani(
                str, "Please enter threat feed description: ", False)
            ip_feed[_tmpdesc] = _tmpurl
            data_sync(True)
            break
        elif _tmpint == 'r':
            _tmpsel = sani(int, "Please enter number to delete: ",
                           list(range(0, counter + 1)))
            for i in ip_feed:
                if _tmpsel == counter:
                    del ip_feed[i]
                    data_sync(True)
                    break
        else:
            break


def gb_update():  # Function to update global threat list
    print(intro_graphic)
    org = "REDACTED"
    ip_tmp = []
    for i in progressBar(ip_feed, prefix='Progress:', suffix='Complete', fill='|', length=100):
        response = requests.get(ip_feed[i])
        _tmp = response.text.split()
        for j in _tmp:
            ip_tmp.append(j)
        ip_tmp = list_pull('global', ip_tmp)
        block_ip(org, ip_tmp, i, True)
    rem_dup_auto(org, True)


def list_pull(org, ip):
    if org_id[org][0] == '':
        return
    blkquery_json["variables"]["id"] = org_id[org][0]
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=blkquery_json)
    resp_data = response.json()
    ip_list = []
    if len(ip[0]) > 1:
        _s1 = set(ip)
        for i in resp_data["data"]["systemConfig"]["resources"]["edges"]:
            ip_list.append(i["node"]["value"].strip())
        _s2 = set(ip_list)
        ip_list = list(_s1.difference(_s2))
        return ip_list
    for i in resp_data["data"]["systemConfig"]["resources"]["edges"]:
        if i["node"]["value"].strip() == ip:
            return True
    return False


def rem_dup_auto(org, auto_):  # Function to remove duplicate entries in block list
    if org_id[org][0] == '':
        return
    blkquery_json["variables"]["id"] = org_id[org][0]
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=blkquery_json)
    resp_data = response.json()
    ip_list, ip_list2, ip_list3 = [], [], []
    for i in resp_data["data"]["systemConfig"]["resources"]["edges"]:
        ip_list.append({"IP": i["node"]["value"].strip(), "Date": i["node"]["created"],
                        "Description": i["node"]["description"], "ID": i["node"]["id"]})
    ip_list = sorted(ip_list, key=lambda d: d['Date'], reverse=True)
    print(f'\n{org_id[org][-1]}')
    for i in progressBar(ip_list, prefix='Searching:', suffix='Complete', fill='|', length=100):
        if i["IP"] not in ip_list2:
            ip_list2.append(i["IP"].strip())
        else:
            ip_list3.append(i)
        time.sleep(0.01)

    if ip_list3:
        print("This will delete: ")
        for i in ip_list3:
            print("IP:", i["IP"].strip(), "Date:", i["Date"],
                  "Description:", i["Description"])
        if auto_:
            print("Removing ", len(ip_list3), " IPs")
            for i in progressBar(ip_list3, prefix='Progress:', suffix='Complete', fill='|', length=100):
                del_ip(org[0], i["ID"])
        else:
            run_conf = sani(
                str, "Please enter 'y' to confirm, or 'n' to skip: ", ['y', 'n'])
            if run_conf == 'y':
                print("Removing ", len(ip_list3), " IPs")
                for i in progressBar(ip_list3, prefix='Progress:', suffix='Complete', fill='|', length=100):
                    del_ip(org[0], i["ID"])
            elif run_conf == 'n':
                print("No IPs Removed")
                time.sleep(1)


def IPDB_bulk():  # Bulk IPDB Replacement function
    if _db:
        for i in org_id:
            pull_list(i)
            rem_dup_auto(i, True)


def IPDB_R_bulk():  # Bulk IPDB Null description replacement
    for i in org_id:
        scanner_check(i)
        rem_dup_auto(i, True)


def blocklist_clean_bulk():  # Function to bulk remove duplicate entries to all blocklists
    clear()
    print(block_graphic)
    for i in progressBar(org_id, prefix='Total:', suffix='Complete', fill='|', length=100):
        rem_dup_auto(i, True)
        clear()
        print(block_graphic)


def check_activity(org):  # This function pulls the information from the blocklist client connections, returning a "*", if there has been a connection in the past 24 hours
    if org == '' or len(org) < 24:
        return 'x'
    ccon_json["variables"]["id"] = org
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=ccon_json)
    _tmp = response.json()
    try:
        if _tmp["data"]["systemConfig"]["client_ip_logs"] != None:
            epoch_time = int(time.time())
            for i in _tmp["data"]["systemConfig"]["client_ip_logs"]:
                if (epoch_time - ab_thres_val*60) <= _tmp["data"]["systemConfig"]["client_ip_logs"][i]["last_seen"]:
                    return '*'
    except TypeError or KeyError:
        print("!!ORGANIZATION BLOCKLIST NOT FOUND!!")
    return ''


def ab_thres():  # This function allows setting threshold for blocklist "ACTIVE" classification (Default 24 hours)
    global ab_thres_val
    r = age_convert(ab_thres_val)
    print(f'Current threshold - Days: {r["day"]}, Hours: {r["hour"]}')
    _dy = sani(int, "Enter Days: ", list(range(0, 31)))
    _dy = _dy * 24
    _hr = sani(int, "Enter Hours: ", list(range(0, 25)))
    ab_thres_val = int(_hr + _dy) * 60
    r = age_convert(ab_thres_val)
    print(f'New threshold set!\nDays: {r["day"]}, Hours: {r["hour"]}')
    input("Press enter to continue: ")


def noti_thresh():  # This function allows setting threshold for blocklist "ACTIVE" classification (Default 24 hours)
    global noti_thres
    print(f'Current frequency - {noti_thres} seconds')
    noti_thres = sani(int, "Enter new frequency in seconds: ",
                      list(range(0, 3601)))
    print(f'New frequency set!\n{noti_thres}')
    input("Press enter to continue:")


def del_ip(org, i):  # This function removes an IP from an organization's block list
    blkdel_json["variables"]["systemConfigId"] = str(org[0])
    blkdel_json["variables"]["id"] = i
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=blkdel_json)
    if response.status_code == 200:
        None
    else:
        print(i, " - REMOVAL FAILED!")


def disp_org():  # Function to display organizations
    while True:
        clear()
        l, o = [], []
        print("1 - Display all\n2 - Display Only Active\n3 - Display No Orgs\n")
        disp = sani(int, "Please make a selection: ", [1, 2, 3])
        if disp == 1:
            clear()
            print(org_graphic)
            for i in progressBar(org_id, prefix='Searching:', suffix='Complete', fill='|', length=100):
                _t = check_activity(org_id[i][0])
                if _t == '':
                    o.append(org_id[i][-1])
                elif _t == '*':
                    l.append(org_id[i][-1])
                else:
                    print("ORG NOT FOUND", i)
            for j in o:
                print(j, ' - NO RECENT BLOCKLIST ACTIVITY')
            for k in l:
                print(k, ' - ACTIVE!')
            break
        elif disp == 2:
            clear()
            print(org_graphic)
            for m in progressBar(org_id, prefix='Searching:', suffix='Complete', fill='|', length=100):
                _t = check_activity(org_id[m][0])
                if _t != '':
                    l.append(org_id[m][-1])
            print('\n')
            for n in l:
                print(n, ' - ACTIVE!')
            break
        elif disp == 3:
            break
    input("Press enter to continue: ")


def org_check():  # Function to select organization
    l, o = [], []
    disp_org()
    while True:
        org_choice = sani(
            str, "\nPlease type the full organization name: ", False)
        if org_choice == "back":
            break
        for p in org_id:
            if org_choice == org_id[p][-1]:
                g_org = True
                break
            else:
                g_org = False
        if g_org == True:
            break
        else:
            print("No Organization Found - Try again!")

    for r in org_id:
        if org_id[r][-1] == org_choice:
            return r


def block_ip(org, ip_array, desc, show):  # This function adds IPs to a organization's blocklist

    blkadd_json["variables"]["systemConfigId"] = org
    if show:
        print("Adding ", len(ip_array), " IPs\n")
        for i in progressBar(ip_array, prefix='Progress:', suffix='Complete', fill='|', length=100):
            if valid_ip(i):
                blkadd_json["variables"]["input"]["value"] = i
                blkadd_json["variables"]["input"]["description"] = desc
                response = requests.post(
                    'https://R3D4CT3D.REDACTED.com/g/graphql', cookies=cookies, headers=headers, json=blkadd_json)
                if response.status_code != 200:
                    print(i.strip() + " - ERR: ", response.status_code)
    else:
        for i in ip_array:
            if valid_ip(i):
                blkadd_json["variables"]["input"]["value"] = i
                blkadd_json["variables"]["input"]["description"] = desc
                response = requests.post(
                    'https://R3D4CT3D.REDACTED.com/g/graphql', cookies=cookies, headers=headers, json=blkadd_json)
                if response.status_code != 200:
                    print(i.strip() + " - ERR: ", response.status_code)


def get_name():  # Gets user name needed for sorting queue
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=usr_json)
    _tmp = response.json()
    if response.status_code != 200:
        input("error with request", response.status_code)
    else:
        return _tmp["data"]["me"]["name"]


def get_sysid():  # Gets system ID needed for assigning alerts
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=usr_json)
    _tmp = response.json()
    if response.status_code != 200:
        input("error with request", response.status_code)
    else:
        return _tmp["data"]["me"]["system_id"]


def assign_alert(_a):  # Function to assign alert
    assgn_json["variables"]["id"] = str(_a)
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=assgn_json)
    if response.status_code != 200:
        input("error with request", response.status_code)


def rem_alert(_x):  # Function to REMOVE ALERT FROM QUEUE
    global alertcountervar
    alrt_ctr("Restore")
    if _background_q:
        alertcountervar = alertcountervar + 1
        alrt_ctr("Update")
        print("REM", _x)
        print("Alerts Closed: ", alertcountervar, "  Averaging: ", (math.floor(alertcountervar/12)), " Alerts per hour (12 Hours)")
    alrem_json["variables"]["id"] = _x
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=alrem_json)
    resp_data = response.json()
    if response.status_code != 200:
        input("error with request", response.status_code)


def single_alert_query(_a):  # Function to get alert creation time in Z
    alroot_json["variables"]["id"] = _a
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=alroot_json)
    resp_data = response.json()
    if response.status_code != 200:
        input("error with request", response.status_code)
    else:
        return resp_data["data"]["alert"]["created"]


def _usrwatchlist():  # User watchlist function
    _ic, _ih, _im, _il, _gen, _l = [], [], [], [], [], []
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=qquery_json)
    resp_data = response.json()
    clear()
    print(watchlist_graphic)
    _ks = sani(str, "View All(a) or Personal(p): ", ['a', 'p'])
    for i in resp_data["data"]["workQueue"]["work_queueitems"]:
        try:
            if i["assigned_to"]["name"] != None and _ks == 'a':
                if (i["assigned_to"]["name"]) and (i["queue_status"] == "watching"):
                    _gen.append(i)
            if i["assigned_to"]["name"] != None and _ks == 'p':
                if (i["assigned_to"]["name"] == usr_name) and (i["queue_status"] == "watching"):
                    _gen.append(i)
        except TypeError:
            None
    _ex = '0'
    if len(_gen) == 0:
        _ex = input("Watchlist Empty. Press Enter to Finish:")

    while True and _ex == '0':
        _tmp, _tmp2, _tmp3 = [], [], []
        for i in progressBar(_gen, prefix='Compiling:', suffix='Complete', fill='|', length=100):
            if i["regarding"]["id"][7:]:
                _l = active_alert_query(i["regarding"]["id"][7:])
                if _l != None and (_l[0] == True and _l[1] != None):
                    try:
                        if org_id[str(i["int_account_id"])][-1] != None:
                            _tmp.append(i)
                    except KeyError:
                        _t = "ORGANIZATION NOT FOUND, ORG ID:", i["int_account_id"]
                elif _l != None and (_l[0] == False and _l[1] != None):
                    try:
                        if org_id[str(i["int_account_id"])][-1] != None:
                            _tmp2.append(i)
                    except KeyError:
                        _t = "ORGANIZATION NOT FOUND, ORG ID:", i["int_account_id"]
                elif _l != None and (_l[0] == False and _l[1] == None):
                    try:
                        if org_id[str(i["int_account_id"])][-1] != None:
                            _tmp3.append(i)
                    except KeyError:
                        _t = "ORGANIZATION NOT FOUND, ORG ID:", i["int_account_id"]
        _tmp = sorted(_tmp, key=lambda d: d['timestamp'], reverse=False)
        _tmp2 = sorted(_tmp2, key=lambda d: d['timestamp'], reverse=False)
        _tmp3 = sorted(_tmp3, key=lambda d: d['timestamp'], reverse=False)
        print("Customer has responded: ")
        for i in _tmp:
            print('\n')
            _agetemp = age_convert(
                round(alert_age(epoch_time, i["timestamp"])))
            if _agetemp["min"] > 0:
                print(f'Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {_agetemp["day"]} Days {_agetemp["hour"]} Hours {_agetemp["min"]} Minutes\n  Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}')
            elif _agetemp["min"] <= 0:
                print(f'Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {_agetemp["day"]} Days {_agetemp["hour"]} Hours    Last Change to Alert: {i["last_notification"]["created"]}  \n  Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}')
            else:
                print("\n\nORGANIZATION NOT FOUND, ORG ID:",
                      i["int_account_id\n\n"])
        input("\n\nPress Enter to Continue:")
        print("Customer has NOT responded: ")
        for i in _tmp2:
            print('\n')
            _agetemp = age_convert(
                round(alert_age(epoch_time, i["timestamp"])))
            if _agetemp["min"] > 0:
                print(f'Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {_agetemp["day"]} Days {_agetemp["hour"]} Hours {_agetemp["min"]} Minutes\n  Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}')
            elif _agetemp["min"] <= 0:
                print(f'Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {_agetemp["day"]} Days {_agetemp["hour"]} Hours    Last Change to Alert: {i["last_notification"]["created"]}  \n  Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}')
            else:
                print("\n\nORGANIZATION NOT FOUND, ORG ID:",
                      i["int_account_id\n\n"])
        input("\n\nPress Enter to Continue:")
        print("NO COMMS: ")   
        for i in _tmp3:
            print('\n')
            _agetemp = age_convert(
                round(alert_age(epoch_time, i["timestamp"])))
            if _agetemp["min"] > 0:
                print(f'Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {_agetemp["day"]} Days {_agetemp["hour"]} Hours {_agetemp["min"]} Minutes\n  Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}')
            elif _agetemp["min"] <= 0:
                print(f'Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {_agetemp["day"]} Days {_agetemp["hour"]} Hours    Last Change to Alert: {i["last_notification"]["created"]}  \n  Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}')
            else:
                print("\n\nORGANIZATION NOT FOUND, ORG ID:",
                      i["int_account_id\n\n"])
        input("\n\nPress Enter to Continue:")
        break


def user_auto_assign():  # User auto assign function
    global epoch_time
    _ic, _ih, _im, _il, _gen = [], [], [], [], []
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=qquery_json)
    resp_data = response.json()
    clear()
    print(watchlist_graphic)
    print("Queue Pull")
    _t = sani(int, "Please enter monitoring time in minutes: ",
              list(range(0, 1441)))
    _p = sani(int, "Please enter refresh rate in seconds: ",
              list(range(10, 36001)))
    _d = sani(int, "Please enter threshold time in minutes: ",
              list(range(0, 120)))
    print("\n1 - Critical\n2 - Critical & High\n3 - Critical, High, & Medium\n4 - All")
    _alt = sani(
        int, "Please choose alert severity: ", list(range(1, 5)))
    _t = (_t * 60) + epoch_time
    while epoch_time <= _t:
        clear()
        print(intro_graphic)
        for i in resp_data["data"]["workQueue"]["work_queueitems"]:
            try:
                if (round(alert_age(epoch_time, i["timestamp"]))) > _d:
                    if i["queue_status"] == "unAssigned" and i["auto_close_time"] == None:
                        if _alt == 1 and i["severity_level"] == "_6critical":
                            _gen.append(i)
                            assign_alert(i["regarding"]["id"][7:])
                        elif _alt == 2 and (i["severity_level"] == "_5high" or i["severity_level"] == "_6critical"):
                            _gen.append(i)
                            assign_alert(i["regarding"]["id"][7:])
                        elif _alt == 3 and i["severity_level"] != "_1low":
                            _gen.append(i)
                            assign_alert(i["regarding"]["id"][7:])
                        elif _alt == 4:
                            _gen.append(i)
                            assign_alert(i["regarding"]["id"][7:])
            except TypeError:
                None
        for i in _gen:
            try:
                print(f'\rAlert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {round(alert_age(epoch_time,i["timestamp"]))} minutes     Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}', end='\n\r')
            except KeyError:
                None

        for i in range(_p):
            if not epoch_time <= _t:
                break
            _sele = (_t - epoch_time) % 60
            _minle = ((_t - epoch_time) - _sele) / 60
            _hrle = math.floor((((_t - epoch_time) - _sele) - (_minle * 60)) / 360)
            _serf = _p - i
            print(
                f'\rAutoassigned {len(_gen)} alerts from queue, refreshing in... {_serf} seconds     Time Remaining: {_hrle} : {_minle} : {_sele} ', end='\r')
            time.sleep(1)
        response = requests.post(
            'https://R3D4CT3D.REDACTED.com/g/graphql', cookies=cookies, headers=headers, json=qquery_json)
        resp_data = response.json()


def org_auto_assign():  # Organization auto assign for new alerts function
    _ic, _ih, _im, _il, _gen = [], [], [], [], []
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=qquery_json)
    resp_data = response.json()
    clear()
    print(org_graphic)
    _o = int(org_check())
    _t = sani(int, "Please enter monitoring time in minutes: ",
              list(range(0, 1441)))
    _p = sani(int, "Please enter refresh rate in seconds: ",
              list(range(10, 36001)))
    _t = (_t * 60) + epoch_time
    while epoch_time <= _t:
        clear()
        print(queue_graphic)
        for i in resp_data["data"]["workQueue"]["work_queueitems"]:
            try:
                if (i["queue_status"] == "unAssigned") and (i["timestamp"] < _t) and (i["int_account_id"] == _o):
                    if len(_gen) > 0:
                        for j in _gen:
                            if i["regarding"]["id"] == _gen[j]["regarding"]["id"][7:]:
                                break
                            else:
                                _gen.append(i)
                                assign_alert(i["regarding"]["id"][7:])
                    else:
                        _gen.append(i)
            except TypeError:
                None
        for i in _gen:
            assign_alert(i["regarding"]["id"][7:])
            print(f'\rAlert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {round(alert_age(epoch_time,i["timestamp"]))} minutes     Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}', end='\n\r')
        for i in range(_p):
            if not epoch_time <= _t:
                break
            _sele = (_t - epoch_time) % 60
            _minle = ((_t - epoch_time) - _sele) / 60
            _hrle = math.floor((((_t - epoch_time) - _sele) - (_minle * 60)) / 360)
            _serf = _p - i
            print(
                f'\rAdded {len(_gen)} alerts to queue, refreshing in... {_serf} seconds     Time Remaining: {_hrle} : {_minle} : {_sele} ', end='\r')
            time.sleep(1)
        response = requests.post(
            'https://R3D4CT3D.REDACTED.com/g/graphql', cookies=cookies, headers=headers, json=qquery_json)
        resp_data = response.json()


def org_auto_assign_all():  # Organization auto assign all function
    _ic, _ih, _im, _il, _gen = [], [], [], [], []
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=qquery_json)
    resp_data = response.json()
    clear()
    print(org_graphic)
    _o = int(org_check())
    clear()
    print("1 - Pull all active alerts from organization (Will re-assign all active alerts to you)")
    print("2 - Pull all unassigned active alerts from organization")
    _ua = sani(int, "Please make a selection: ", [1, 2])
    clear()
    print(qauto_graphic)
    for i in resp_data["data"]["workQueue"]["work_queueitems"]:
        if (i["status"] != None) and (i["status"] == 'resolved'):
            None
        else:
            try:
                if (i["queue_status"] == "unAssigned") and (i["int_account_id"] == _o):
                    print(f'\rAlert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {round(alert_age(epoch_time,i["timestamp"]))} minutes     Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}', end='\n\r')
                    assign_alert(i["regarding"]["id"][7:])
                    _gen.append(i)
            except TypeError:
                None
            try:
                if (i["queue_status"] == "assigned") and (i["int_account_id"] == _o) and (_ua == 1):
                    print(f'Currently Assigned to: {i["assigned_to"]["name"]}')
                    print(f'\rAlert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {round(alert_age(epoch_time,i["timestamp"]))} minutes     Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}', end='\n\r')
                    _tx = sani(
                        str, "Enter 'y' to confirm re-assignment, or 'n' to skip: ", ['y', 'n'])
                    if _tx == 'y':
                        assign_alert(i["regarding"]["id"][7:])
                        _gen.append(i)
                    if _tx == 'n':
                        print("--ALERT SKIPPED--")
            except TypeError:
                None
    if len(_gen) <= 0:
        print("No alerts found!")
    input("Press enter to Continue:")


def alert_notification():  # Function to notify of aging alerts in queue
    global _background_q3
    # If alert is critical or high, play alert and print url
    while True and (not t1._is_stopped):
        usr_qc, usr_qh, usr_qm, usr_ql = False, False , False, False
        if (not _background_q3):
            clear()
            print(intro_graphic)
        _ic, _ih, _im, _il = [], [], [], []
        response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                                 cookies=cookies, headers=headers, json=qquery_json)
        resp_data = response.json()
        try:
            if not ('errors') in resp_data.items() and resp_data['data'] != None:
                for i in resp_data["data"]["workQueue"]["work_queueitems"]:
                    try:
                        if ((i["queue_status"] == "unAssigned") and (i["assigned_to"] == None)) or i["assigned_to"]["name"] == usr_name and i["auto_close_time"] == None:
                            if (round(alert_age(epoch_time, i["timestamp"])) > 2880 ) and i["auto_close_time"] == None:
                                None
                            elif (round(alert_age(epoch_time, i["timestamp"])) > 30) and i["auto_close_time"] == None:
                                if i["severity_level"] == "_6critical":
                                    _ic.append(i)
                                    if i["assigned_to"]["name"] == usr_name:
                                        usr_qc = True
                                elif i["severity_level"] == "_5high":
                                    _ih.append(i)
                                    if i["assigned_to"]["name"] == usr_name:
                                        usr_qh = True
                            elif (round(alert_age(epoch_time, i["timestamp"])) > 120) and i["auto_close_time"] == None:
                                if i["severity_level"] == "_3medium":
                                    _im.append(i)
                                if i["assigned_to"]["name"] == usr_name:
                                    usr_qm = True
                            elif (round(alert_age(epoch_time, i["timestamp"])) > 240) and i["auto_close_time"] == None:
                                if i["severity_level"] == "_1low":
                                    _il.append(i)
                                if i["assigned_to"]["name"] == usr_name:
                                    usr_ql = True
                    except TypeError:
                        None
        except KeyError:
            None
        _ic = sorted(_ic, key=lambda d: d['timestamp'], reverse=False)
        _ih = sorted(_ih, key=lambda d: d['timestamp'], reverse=False)
        _im = sorted(_im, key=lambda d: d['timestamp'], reverse=False)
        _il = sorted(_il, key=lambda d: d['timestamp'], reverse=False)
        if len(_ic) > 0 and noti_on:
            playsound('ALRT.mp3')
            if usr_qc == True:
                playsound('Criticaluser.mp3')
            else:
                playsound('Criticalall.mp3')
        elif len(_ih) > 0 and noti_on:
            playsound('ALRT.mp3')
            if usr_qh == True:
                playsound('Highuser.mp3')
            else:
                playsound('Highall.mp3')
        elif len(_im) > 0 and noti_on:
            playsound('ALRT.mp3')
            if usr_qm == True:
                playsound('Mediumuser.mp3')
            else:
                playsound('Mediumall.mp3')
        elif len(_il) > 0 and noti_on:
            playsound('ALRT.mp3')
            if usr_ql == True:
                playsound('Lowuser.mp3')
            else:
                playsound('Lowall.mp3')
        if (not _background_q3):
            clear()
            print(queue_graphic)
            for i in _ic:
                print(f'CRITICAL Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {round(alert_age(epoch_time,i["timestamp"]))} minutes     Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}')
            print('\n\n')
            for i in _ih:
                print(f'HIGH Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {round(alert_age(epoch_time,i["timestamp"]))} minutes     Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}')
            print('\n\n')
            for i in _im:
                print(f'MEDIUM Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {round(alert_age(epoch_time,i["timestamp"]))} minutes     Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}')
            print('\n\n')
            for i in _il:
                print(f'LOW Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {round(alert_age(epoch_time,i["timestamp"]))} minutes     Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}')
            print("\nPress enter to exit: ")
        for i in range(0, noti_thres):
            if (not _background_q3): print(f'Refreshing in {(noti_thres - i)} seconds', end='\r')
            time.sleep(1)
            if t1._is_stopped:
                break


def close_alert(_a): # Function to close alert
    alres_json["variables"]["id"] = str(_a)
    alres_json["variables"]["input"]["resolution_synopsis"] = "No Threat or IOC Observed"
    alres_json["variables"]["input"]["resolution_type"] = "falsePositive"
    alres_json["variables"]["input"]["resolution_actions"] = {0: "No Action Needed"}
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=alres_json)
    if response.status_code != 200:
        print("error with request", response.status_code)
        input()


def _usrunqueue():  # Unassigned alert queue function
    _ic, _ih, _im, _il, _gen = [], [], [], [], []
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=qquery_json)
    resp_data = response.json()
    clear()
    print(watchlist_graphic)
    print("Active Queue")
    _tx = sani(str, "Sort by severity (s), or organization (o)?: ", ['s','o'])
    for i in resp_data["data"]["workQueue"]["work_queueitems"]:
        try:
            if (i["queue_status"] == "unAssigned") and (i["assigned_to"] == None):
                if _tx == 'o':
                    _gen.append(i)
                elif _tx == 's':
                    if i["severity_level"] == "_6critical":
                        _ic.append(i)
                    elif i["severity_level"] == "_5high":
                        _ih.append(i)
                    elif i["severity_level"] == "_3medium":
                        _im.append(i)
                    elif i["severity_level"] == "_1low":
                        _il.append(i)
        except TypeError:
            None

    _gen = sorted(_gen, key=lambda d: (d['int_account_id'],d['severity_level'],d['timestamp']) , reverse=True)
    _ic = sorted(_ic, key=lambda d: d['timestamp'], reverse=False)
    _ih = sorted(_ih, key=lambda d: d['timestamp'], reverse=False)
    _im = sorted(_im, key=lambda d: d['timestamp'], reverse=False)
    _il = sorted(_il, key=lambda d: d['timestamp'], reverse=False)
    if _tx == 'o':
        for i in _gen:
            print(f'Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}\nSeverity: {(i["severity_level"])[2:]}\nAge: {round(alert_age(epoch_time,i["timestamp"]))} minutes\nAlert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}\n')
        input("Press Enter to Finish:")
        
    elif _tx == 's':
        print("\nTotal: ", (len(_ic)+len(_ih)+len(_im)+len(_il)))
        print("\nCritical:")
        for i in _ic:
            print(f'Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {round(alert_age(epoch_time,i["timestamp"]))} minutes     Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}')
        input("Press Enter to Continue:")
        print("\nHigh:")
        for i in _ih:
            print(f'Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {round(alert_age(epoch_time,i["timestamp"]))} minutes     Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}')
        input("Press Enter to Continue:")
        print("\nMedium:")
        for i in _im:
            print(f'Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {round(alert_age(epoch_time,i["timestamp"]))} minutes     Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}')
        input("Press Enter to Continue:")
        print("\nLow:")
        for i in _il:
            print(f'Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {round(alert_age(epoch_time,i["timestamp"]))} minutes     Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}')
        input("Press Enter to Finish:")


def _usraqueue():  # User active queue function
    _ic, _ih, _im, _il, _gen, _gen2 = [], [], [], [], [], []
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=qquery_json)
    resp_data = response.json()
    clear()
    print(watchlist_graphic)
    print("My Queue")
    _tx = sani(str, "Sort by severity (s), or organization (o)?: ", ['s','o'])
    for i in resp_data["data"]["workQueue"]["work_queueitems"]:
        try:
            if i["assigned_to"]["name"] != None:
                if i['assigned_to']['name'] == usr_name:
                    if _tx == 'o':
                        _gen.append(i)
                    elif _tx == 's':
                        if i["severity_level"] == "_6critical":
                            _ic.append(i)
                        elif i["severity_level"] == "_5high":
                            _ih.append(i)
                        elif i["severity_level"] == "_3medium":
                            _im.append(i)
                        elif i["severity_level"] == "_1low":
                            _il.append(i)
        except TypeError:
            None

    _gen = sorted(_gen, key=lambda d: (d['int_account_id'],d['severity_level'],d['timestamp']) , reverse=True)
    _ic = sorted(_ic, key=lambda d: d['timestamp'], reverse=False)
    _ih = sorted(_ih, key=lambda d: d['timestamp'], reverse=False)
    _im = sorted(_im, key=lambda d: d['timestamp'], reverse=False)
    _il = sorted(_il, key=lambda d: d['timestamp'], reverse=False)
    if _tx == 'o':
        for i in _gen:
            print(f'Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}\nSeverity: {(i["severity_level"])[2:]}\nAge: {round(alert_age(epoch_time,i["timestamp"]))} minutes\nAlert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}\n')
        input("Press Enter to Finish:")
        
    elif _tx == 's':
        print("\nTotal: ", (len(_ic)+len(_ih)+len(_im)+len(_il)))
        print("\nCritical:")
        for i in _ic:
            print(f'Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {round(alert_age(epoch_time,i["timestamp"]))} minutes     Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}')
        input("Press Enter to Continue:")
        print("\nHigh:")
        for i in _ih:
            print(f'Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {round(alert_age(epoch_time,i["timestamp"]))} minutes     Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}')
        input("Press Enter to Continue:")
        print("\nMedium:")
        for i in _im:
            print(f'Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {round(alert_age(epoch_time,i["timestamp"]))} minutes     Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}')
        input("Press Enter to Continue:")
        print("\nLow:")
        for i in _il:
            print(f'Alert: {i["regarding"]["name"]}     Organization: {org_id[str(i["int_account_id"])][-1]}     Age: {round(alert_age(epoch_time,i["timestamp"]))} minutes     Alert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{i["regarding"]["id"][7:]}')
        input("Press Enter to Finish:")


def b_useraqueue():  # Background function to accumulate user queue and append to _aq array (active queue variable)
    _gen = []
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=qquery_json)
    resp_data = response.json()
    for i in resp_data["data"]["workQueue"]["work_queueitems"]:
        try:
            if i["assigned_to"]["name"] != None:
                if i['assigned_to']['name'] == usr_name:
                    _t = i['regarding']['id']
                    _t = _t[7:]
                    _aq.append(_t)
        except TypeError:
            None


def blocklist_bulk():  # Function to bulk add to blocklist
    org = org_id[org_check()][0]
    while True:
        try:
            filename = sani(
                str, "\nPlease input file name (Must be in same directory): ", False)
            with open(filename) as f:
                for line in f:
                    ip_array.append(line.strip())
                desc = sani(str, "Please input blocklist description: ", False)
                block_ip(org, ip_array, desc, True)
                input("Press enter to continue: ")
                break
        except FileNotFoundError:
            if filename == "back":
                break
            else:
                print("File not found, try again")


def blocklist_bulk_desc():  # Function to bulk add to blocklist with description in file (',' delimiter)
    org = org_id[org_check()][0]
    desc_array = []
    while True:
        try:
            filename = sani(
                str, "\nPlease input file name (Must be in same directory): ", False)
            with open(filename) as f:
                for line in f:
                    tmp = line.strip()
                    tmp = tmp.split(',')
                    desc_array.append(tmp[1])
                    ip_array.append(tmp[0])
                for x, y in zip(ip_array, desc_array):
                    print(f'Adding: {x}, {y}')
                    block_ip(org, [x], y, False)
                input("Press enter to continue: ")
                break
        except FileNotFoundError:
            if filename == "back":
                break
            else:
                print("File not found, try again")


def blocklist_bulk_check():  # Function to bulk add to blocklist with IPDB features
    if not _db:
        return None
    org = org_id[org_check()][0]

    while True:
        try:
            filename = sani(
                str, "\nPlease input file name (Must be in same directory): ", False)
            max = sani(
                int, "Enter confidence threshold to add to block list (0 - 100): ", list(range(0-101)))
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    desc = ipdb_query(str(line))
                    if int(desc) > max:
                        desc = "Confidence of Abuse " + str(desc) + "%"
                        line_t = [line]
                        block_ip(org, line_t, desc, True)
                break
        except FileNotFoundError:
            print("File not found, try again")


def ipdb_query(ip):  # Function to check IPAbuseDB for IP, and return abuse COA
    global _db, _ipdbKey
    headersip = {
        'Accept': 'application/json'
    }

    headersip['Key'] = _ipdbKey
    urlstr = 'https://api.abuseipdb.com/api/v2/check?ipAddress=' + \
        str(ip) + '&maxAgeInDays=90&verbose'
    response = requests.get(urlstr, headers=headersip)
    if response:
        j_res = response.json()
        desc = j_res["data"]["abuseConfidenceScore"]
        descdomain = j_res["data"]["domain"]
        return desc, descdomain
    else:
        _db = False
        return False


def scanner_check(org):  # Function to check block lists for scanner IPs and re-label
    blkquery_json['variables']['id'] = org_id[org][0]
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=blkquery_json)
    resp_data = response.json()
    ip_list, ip_list2, ip_list3 = [], [], []
    for i in resp_data["data"]["systemConfig"]["resources"]["edges"]:
        dup_ips = {"IP": i["node"]["value"].strip(), "Date": i["node"]["created"],
                   "Description": i["node"]["description"], "ID": i["node"]["id"]}
        if i["node"]["value"] != '':
            ip_list.append(dup_ips)
    ip_list = sorted(ip_list, key=lambda d: d['Date'], reverse=True)
    if len(ip_list) == 0:
        None
    else:
        clear()
        print(f'\n{intro_graphic}\nChecking: {org_id[org][-1]}')
        for i in progressBar(ip_list, prefix='Progress:', suffix='Complete', fill='|', length=100):
            for j in sc_ips["Single"]:
                for k in sc_ips["Single"][j]:
                    if k == i["IP"] and i["Description"] != j:
                        desc = j
                        _tmp = [i["IP"]]
                        block_ip(org_id[org][0], _tmp, desc, False)
            for j2 in sc_ips["Subnet"]:
                for k2 in sc_ips["Subnet"][j2]:
                    if ip_in_prefix(i["IP"], k2) and i["Description"] != j2:
                        desc = j2
                        _tmp = [i["IP"]]
                        block_ip(org_id[org][0], _tmp, desc, False)


def pull_list(org):  # Function to check blocklist (IPDB Related)
    blkquery_json['variables']['id'] = org_id[org][0]
    response = requests.post('https://R3D4CT3D.REDACTED.com/g/graphql',
                             cookies=cookies, headers=headers, json=blkquery_json)
    resp_data = response.json()
    ip_list, ip_list2, ip_list3 = [], [], []
    for i in resp_data["data"]["systemConfig"]["resources"]["edges"]:
        dup_ips = {"IP": i["node"]["value"].strip(), "Date": i["node"]["created"],
                   "Description": i["node"]["description"], "ID": i["node"]["id"]}
        if i["node"]["value"] != '':
            ip_list.append(dup_ips)
    ip_list = sorted(ip_list, key=lambda d: d['Date'], reverse=True)
    if len(ip_list) == 0:
        None
    else:
        clear()
        print(f'\n{intro_graphic}\nChecking: {org_id[org][-1]}')
        for i in progressBar(ip_list, prefix='Progress:', suffix='Complete', fill='|', length=100):
            if i["Description"] == None or i["Description"] == 'Abuse Confidence %None':
                desc = ipdb_query(i["IP"])
                if desc == None:
                    _db = False
                elif desc != 0:
                    _tmp = [i["IP"]]
                    desc = "Abuse Confidence %" + desc
                    block_ip(org, _tmp, desc, False)


# WEBSOCKET FUNCTIONS

def on_error(ws, error):  # Function to handle Websocket errors
    print(error)


def on_close(ws):  # Function to handle Websocket closing
    print("### closed ###")


def on_open(ws):  # Function to handle Websocket opening
    def run(*args):
        ws.send()
        ws.send()
    WSST1 = threading.Thread(target=run, args=())
    WSST1.start()


def on_open_b(wss):  # Function to handle Websocket opening (Background thread)
    def run(*args):
        wss.send()
        wss.send()
    WSST4 = threading.Thread(target=run, args=())
    WSST4.start()


def on_message_all(ws, message):  # Function to handle Websocket messages
    global _aq, _x
    if t1._is_stopped:
        ws.close()
        wss.close()
        return
    if _background_q:
        return None
    ws_ml = json.loads(message)
    if not ("type", "ka") in ws_ml.items() and not ("type", "connection_ack") in ws_ml.items():
        print("---------------------------------------------------------------------------------------------------------")
        ws_ms = ws_ml["payload"]["data"]["workQueueEvents"]
    else:
        return None

    _x = ws_ms["regarding"]["regarding"]["id"]
    _x = _x[7:]
    try:
        print(f'{ws_ms["regarding"]["assigned_to"]["name"]} - {ws_ms["regarding"]["regarding"]["name"]}\nAlert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{_x}')
    except TypeError:
        print(
            f'SYSTEM - {ws_ms["regarding"]["regarding"]["name"]}\nAlert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{_x}')

    if ws_ms["regarding"]["queue_status"] == 'watching':
        print('WATCHLIST')
    if ws_ms["regarding"]["status"] == 'reOpened':
        print('REOPENED')
    if ws_ms["event_info"]["message"] == 'created':
        print('NEW')
    if ws_ms["event_info"]["message"] == 'updated':
        print('UPDATE')
        try:
            if ws_ms["regarding"]["status"] == 'resolved' and ws_ms["regarding"]["queue_status"] == 'expiring':
                print(f'RESOLVED')
        except TypeError:
            None
        try:
            if ws_ms["regarding"]["assigned_to"] != None and ws_ms["regarding"]["queue_status"] == 'assigned':
                _tmp1 = ws_ms["regarding"]["assigned"]
                _tmp1 = _tmp1[:19]
                _tmp2 = ws_ms["event_info"]["created"]
                _tmp2 = _tmp2[:19]
                if _tmp1 == _tmp2:
                    print(f'ASSIGNED')
                    if ws_ms["regarding"]["assigned_to"]["name"] == usr_name:
                        _aq.append(_x)
        except TypeError:
            None
    if ws_ms["event_info"]["message"] == 'deleted':
        print('Removed from Queue')


def on_message_rq(wss, message):  # Function to handle Websocket messages
    global _aq, _x
    if t1._is_stopped:
        ws.close()
        wss.close()
        return
    ws_ml = json.loads(message)
    if not ("type", "ka") in ws_ml.items() and not ("type", "connection_ack") in ws_ml.items():
        ws_ms = ws_ml["payload"]["data"]["workQueueEvents"]
    else:
        return None
    _x = ws_ms["regarding"]["regarding"]["id"]
    _x = _x[7:]
    try:
        if ws_ms["regarding"]["status"] == 'resolved' and ws_ms["regarding"]["queue_status"] == 'expiring':
            if ws_ms["regarding"]["assigned_to"]["name"] == usr_name and _autorem:
                if _autorem and ws_ms["event_info"]["message"] != 'deleted':
                    rem_alert(_x)
    except TypeError:
        None


def on_message_personal(ws, message):  # Function to handle Websocket messages
    global _aq, _x
    if t1._is_stopped:
        ws.close()
        wss.close()
        return
    if _background_q2:
        return None
    ws_ml = json.loads(message)
    if not ("type", "ka") in ws_ml.items() and not ("type", "connection_ack") in ws_ml.items():
        ws_ms = ws_ml["payload"]["data"]["workQueueEvents"]
    else:
        return None
    _x = ws_ms["regarding"]["regarding"]["id"]
    _x = _x[7:]

    if ws_ms["regarding"]["assigned_to"] == None:
        return None
    elif ws_ms["regarding"]["assigned_to"]["name"] != usr_name:
        return None
    print(f'{ws_ms["regarding"]["regarding"]["name"]}\nAlert URL: https://R3D4CT3D.REDACTED.com/app/alerts/{_x}')
    if ws_ms["event_info"]["message"] == 'deleted':
        print('Removed from Queue')
    elif ws_ms["regarding"]["status"] == 'resolved' and ws_ms["regarding"]["queue_status"] == 'expiring':
        print(f'RESOLVED')
        queue_chk(_x)
    elif ws_ms["regarding"]["queue_status"] == 'assigned':
        _tmp1 = ws_ms["regarding"]["assigned"]
        _tmp1 = _tmp1[:19]
        _tmp2 = ws_ms["event_info"]["created"]
        _tmp2 = _tmp2[:19]
        if _tmp1 == _tmp2:
            print(f'ASSIGNED')
            _aq.append(_x)
    else:
        if ws_ms["event_info"]["message"] == 'updated':
            print('UPDATE')


def queue_chk(_x):  # Function that uses user assigned alerts combined with websocket data to show efficiency in closing of alerts ( Gives time elapsed before clearing alert )
    global _aq
    _s = []
    for x in _aq:
        if x not in _s:
            _s.append(x)

    _aq = _s
    for i in _aq:
        if i == _x:
            dt = zulu.now()
            dt.format('%Y-%m-%d%H:%M:%ss.%SSS', tz='')
            dt2 = zulu.parse(single_alert_query(_x))
            print(f'Closed in: {str(dt-dt2)[:-7]}')
            _formatdate = str(dt)[:-9]
            _formatdate = _formatdate + 'Z'
            _aq.remove(i)
            return True
    else:
        return False


def NET_main():  # Function to handle Websocket opening
    ws.on_open = on_open
    ws.run_forever(host="R3D4CT3D.REDACTED.com",
                   origin="https://R3D4CT3D.REDACTED.com")


def NET_main_b():  # Function to handle Websocket opening
    wss.on_open = on_open_b
    wss.run_forever(host="R3D4CT3D.REDACTED.com",
                    origin="https://R3D4CT3D.REDACTED.com")


def rs_b():  # Function to manage auto remove and configuration selection
    global _autorem
    if not t4.is_alive():
        t4.start()

    if _autorem:
        _tx = sani(str, "Disable auto-remove (y or n)?: ", ['y', 'n'])
        if _tx == 'y':
            _autorem = False
    else:
        _tx = sani(str, "Enable auto-remove (y or n)?: ", ['y', 'n'])
        if _tx == 'y':
            _autorem = True


def rs(_p):  # Function to manage background vs foreground websocket configuration
    global ws, _background_q, _background_q2
    if _p:
        ws = websocket.WebSocketApp("wss://R3D4CT3D.REDACTED.com/g/graphql", header={"Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
                                                                                     "Sec-WebSocket-Protocol": "graphql-ws"}, cookie=_cook,  on_message=on_message_personal, on_error=on_error, on_close=on_close)
        _background_q2 = False
    else:
        ws = websocket.WebSocketApp("wss://R3D4CT3D.REDACTED.com/g/graphql", header={"Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
                                                                                     "Sec-WebSocket-Protocol": "graphql-ws"}, cookie=_cook,  on_message=on_message_all, on_error=on_error, on_close=on_close)
        _background_q = False
    if not t3.is_alive():
        b_useraqueue()
        t3.start()
    input()
    _background_q = True


def noti_mon():  # Function to mangage notifications of critical alerts
    global _background_q3, noti_on
    clear()
    print(intro_graphic)
    print("1 - View alerts\n2 - Enable Background Chime\n3 - Disable Background Chime")
    _tx = sani(int, "Please make a selection: ", [1, 2, 3])
    if _tx == 1:
        clear()
        print(intro_graphic)
        _background_q3 = False
        noti_on = True
        input()
        _background_q3 = True
        _tx2 = sani(str, "Disable Chime? y or n: ", ['y', 'n'])
        if _tx2 == 'y':
            noti_on = False
    elif _tx == 2:
        _background_q3 = True
        noti_on = True
    elif _tx == 3:
        _background_q3 = True
        noti_on = False

def ipkey_change():  # Function to change IPAbuseDB API Key
    global _ipdbKey
    clear()
    print(f'Current Key: {_ipdbKey}')
    tmp = _ipdbKey
    while True:
        _ipdbKey = sani(str, "Please enter new Key: ", False)
        if _ipdbKey == 'back':
            _ipdbKey = tmp
            break
        if (ipdb_query('8.8.8.8') == False):
            _ipdbKey = tmp
            print("ERR: Key invalid!")
            time.sleep(1)
        else:
            print("New Key Saved! : ", _ipdbKey)
            time.sleep(2)
            break
    data_sync(True)

def time_keeper(): # Function to keep time
    global epoch_time
    while True:
        epoch_time = int(time.time())
        if (not t1.is_alive()):
            break

def m_search_man(): # Function to manage quick search / block
    _tx = sani(str, "Please enter Alert URL: ", False)
    _tx = _tx.split('/')
    _tx = _tx[-1]
    _tx = _tx[-24:]
    if len(_tx) == 24:
        m_search(_tx)
        input()
    else:
        input("Invalid URL, Press enter to continue: ")

def main():
    global ws, wss, _cook, usr_name, usr_prompt
    data_sync(True)
    _cook = "REDACTED_session=" + cookies["REDACTED_session"]
    ws = websocket.WebSocketApp("wss://R3D4CT3D.REDACTED.com/g/graphql", header={"Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits", "Sec-WebSocket-Protocol": "graphql-ws"}, cookie=_cook,  on_message=on_message_personal, on_error=on_error, on_close=on_close)
    wss = websocket.WebSocketApp("wss://R3D4CT3D.REDACTED.com/g/graphql", header={"Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits", "Sec-WebSocket-Protocol": "graphql-ws"}, cookie=_cook,  on_message=on_message_rq, on_error=on_error, on_close=on_close)
    usr_name = get_name()
    _tusr = usr_name.split(" ")
    usr_prompt = "USER-" + _tusr[0] + ": "
    _tHM_F, _tOM_F, _tTFM_F, _tQM_F, _tQAM_F, _tBM_F, _tSM_F = [], [], [], [], [], [], []

    HM = ["Organization Management", "Threat Feed Management",
          "Blocklist Management", "Queue Management", "Quick IP Block", "Settings"]
    OM = ["View Organizations",
          "Add Organization"]
    TFM = ["Threat Feed Manager",
           "Push Threat Feed to Global Blocklist"]
    QM = ["My Watchlist",
          "My Active Queue",
          "Unassigned Queue",
          "Automations",
          "Direct Alert Update Stream (All Activity)",
          "Direct Alert Update Stream (User Activity)",
          "Alert SLT Notifications"]
    QAM = ["Pull from Organization (Timed)",
           "Pull All Alerts from Organization",
           "Configure Alert Auto-Assign",
           "Configure Alert Auto-Remove From Queue",
           "Configure Same User Password Change Auto-Remove"]
    BM = ["Add to Blocklist from File",
          "Add to Blocklist from File with Unique Descriptions",
          "Add to Blocklist from File (with IPAbuseDB)",
          "Replace Null Descriptions on all Blocklists",
          "Update Internet Scanner IP Descriptions",
          "Scrub All Organization Blocklists",
          "Scrub Organization Blocklist",
          ]
    SM = [
        "Sync All Application Data to File",
        "Sync File to Application Data",
        "Edit Active Blocklist Threshold (Default 24 Hours)",
        "Edit Notification Frequency",
        "Change IPDB Key",
        "Reset Alert Counter"
    ]

    _tHM_F.append(lambda: menu_disp(OM, _tOM_F, org_graphic, usr_prompt))
    _tHM_F.append(lambda: menu_disp(TFM, _tTFM_F, threat_graphic, usr_prompt))
    _tHM_F.append(lambda: menu_disp(BM, _tBM_F, block_graphic, usr_prompt))
    _tHM_F.append(lambda: menu_disp(QM, _tQM_F, queue_graphic, usr_prompt))
    _tHM_F.append(lambda: m_search_man())
    _tHM_F.append(lambda: menu_disp(SM, _tSM_F, intro_graphic, usr_prompt))

    _tOM_F.append(lambda: disp_org())
    _tOM_F.append(lambda: org_add())

    _tTFM_F.append(lambda: threat_manager())
    _tTFM_F.append(lambda: gb_update())

    _tQM_F.append(lambda: _usrwatchlist())
    _tQM_F.append(lambda: _usraqueue())
    _tQM_F.append(lambda: _usrunqueue())
    _tQM_F.append(lambda: menu_disp(QAM, _tQAM_F, qauto_graphic, usr_prompt))
    _tQM_F.append(lambda: rs(False))
    _tQM_F.append(lambda: rs(True))
    _tQM_F.append(lambda: noti_mon())

    _tQAM_F.append(lambda: org_auto_assign())
    _tQAM_F.append(lambda: org_auto_assign_all())
    _tQAM_F.append(lambda: user_auto_assign())
    _tQAM_F.append(lambda: rs_b())
    _tQAM_F.append(lambda: pass_man())

    
    _tBM_F.append(lambda: blocklist_bulk())
    _tBM_F.append(lambda: blocklist_bulk_desc())
    _tBM_F.append(lambda: blocklist_bulk_check())
    _tBM_F.append(lambda: IPDB_bulk())
    _tBM_F.append(lambda: IPDB_R_bulk())
    _tBM_F.append(lambda: blocklist_clean_bulk())
    _tBM_F.append(lambda: rem_dup_auto(org_check(), False))

    _tSM_F.append(lambda: data_sync(True))
    _tSM_F.append(lambda: data_sync(False))
    _tSM_F.append(lambda: ab_thres())
    _tSM_F.append(lambda: noti_thresh())
    _tSM_F.append(lambda: ipkey_change())
    _tSM_F.append(lambda: alrt_ctr("Reset"))

    while True:
        menu_disp(HM, _tHM_F, intro_graphic, usr_prompt)


t1 = threading.Thread(target=main, args=())
t2 = threading.Thread(target=data_sync, args=())
t3 = threading.Thread(target=NET_main, args=())
t4 = threading.Thread(target=NET_main_b, args=())
t5 = threading.Thread(target=alert_notification, args=())
t6 = threading.Thread(target=time_keeper, args=())
t7 = threading.Thread(target=unqueue_pass, args=())

t2.start()
t2.join()
t1.start()
t6.start()
t7.start()
time.sleep(2)
t3.start()
t4.start()
t5.start()
t1.join()
t5.join()
t6.join()
t7.join()
t3.join()
t4.join()
