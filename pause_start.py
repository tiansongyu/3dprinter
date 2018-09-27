# -*- coding: utf-8 -*-  
#打印过程暂停 恢复
import requests
import json
def pause(mach_ip,api):
    headers={'X-Api-Key': api,'Content-Type':'application/json'}
    ip_add = "/api/job"
    ip_header = "http://"
    final_ip  = '%s%s%s' % (ip_header,mach_ip,ip_add)
    post_json = {"command": "pause","action": "pause"}
    post_js   = json.dumps(post_json)
    r = requests.post(final_ip,headers = headers,data = post_js)
    # print r.request.body
    # print r.request.headers
    if r.status_code == 204:
        print "pause success"
    else :
        print "machine_connection_state_fail"
def restart():
    headers={'X-Api-Key': 'B9183AC73BE2479A846BDB2F32A9C4B1','Content-Type':'application/json'}
    post_json = {'command': 'restart'}
    post_js   = json.dumps(post_json)
    r = requests.post('http://192.168.1.108/api/job',headers = headers,data = post_js)
    print r.request.body
    print r.request.headers
    if r.status_code == 204:
        print "success"
    else :
        print "machine_connection_state_fail"
def resume(mach_ip,api):
    headers={'X-Api-Key': api,'Content-Type':'application/json'}
    ip_add = "/api/job"
    ip_header = "http://"
    final_ip  = '%s%s%s' % (ip_header,mach_ip,ip_add)
    post_json = {'command': 'restart','action': 'pause'}
    post_js   = json.dumps(post_json)
    r = requests.post(final_ip,headers = headers,data = post_js)
    print r.request.body
    print r.request.headers
    if r.status_code == 204:
        print "resume success"
        
    else :
        print "machine_connection_state_fail"
def cancal(mach_ip,api):
    headers={'X-Api-Key':api,'Content-Type':'application/json'}
    ip_add = "/api/job"
    ip_header = "http://"
    final_ip  = '%s%s%s' % (ip_header,mach_ip,ip_add)
    post_json = {'command': 'cancal'}
    post_js   = json.dumps(post_json)
    r = requests.post(final_ip,headers = headers,data = post_js)
    # print r.request.body
    # print r.request.headers
    if r.status_code == 204:
        print "cancal success"
        
    else :
        print "machine_connection_state_fail"
if __name__ == '__main__':
    #pause()
    #restart()
    #resume()
    #cancal()
    pass