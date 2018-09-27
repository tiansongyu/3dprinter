#!/usr/bin/env python
# coding: utf-8
#打印文件命令
import requests
import json
import time
import urllib
import os
import glob
import pathlib
# def create_folder():
#     headers={'X-Api-Key': '2F4E7E03FDAA48428B2337853E7E5427'}
#     files = {"foldername": (None,"d23"),"path": (None,"/")}
#     r = requests.post('http://10.10.63.78/api/files/local',headers = headers,files = files)
#     print r.request.body
#     print r.request.headers
#     if r.status_code == 200:
#         json_file = r.json()
#         print json_file
#     else :
#         print "create_folder_fail"
def upload_file(file_name,mach_ip,api):
    # ip_add = "/api/printer?exclude=sd"
    # ip_header = "http://"
    # final_ip  = '%s%s%s' % (ip_header,mach_data["mach_ip"],ip_add)
    headers={'X-Api-Key': api}
    files = {"file": ("108108.gcode",open(file_name, 'rb'))}

    ip_add = "/api/files/local"
    ip_header = "http://"
    final_ip  = '%s%s%s' % (ip_header,mach_ip,ip_add)
    r = requests.post(final_ip,
                        headers = headers,
                        files = files)
    # print r.request.body
    # print r.request.headers
    if r.status_code == 201:
        json_file = r.json()
        print "upload_file success"
    else :
        print "upload_file fail"
def start_print(path,mach_ip,api):
    headers={'X-Api-Key': api,'Content-Type':'application/json'}
    post_json = {"command": "select","print": "true"}
    post_js   = json.dumps(post_json)

    ip_add = "/api/files/local/108108.gcode"
    ip_header = "http://"
    final_ip  = '%s%s%s' % (ip_header,mach_ip,ip_add)

    r = requests.post(final_ip,headers = headers,data = post_js)
    if r.status_code == 204:
        print "start success"
    else :
        print "start_print fail"
def down_load_printfile(printfile_name,printfile_path,mach_ip,api):
        # path  = ".\printfile\\%s.gcode" % printfile_name
        # print path
        # if os.path.exists(path) == False:
        #     try:
        #         #如果不存在，删除上一个gcode文件，并下载新的文件
        #         folder_path ='.\printfile'
        #         for infile in glob.glob(os.path.join(folder_path, '*.gcode')):
        #             os.remove(infile)
        #         print "prepare to download a file "
        #         url = str(printfile_path)
        #         urllib.urlretrieve(url, path)  
        #     except Exception, e:
        #         print "fail to download a file "
        #         print e
        #     print "down_load file"
        pwd = os.getcwd()
        #path  = ".\printfile\\%s.gcode" % printfile_name
        final_file = "%s/printfile/%s.gcode" % (pwd,printfile_name)
        if os.path.exists(final_file) == False:
            try:
                #如果不存在，删除上一个gcode文件，并下载新的文件
                folder_path = "%s/printfile" % pwd
                for infile in glob.glob(os.path.join(folder_path, '*.gcode')):
                    os.remove(infile)
                print "prepare to download a file "
                url = str(printfile_path)
                urllib.urlretrieve(url, final_file)  
            except Exception, e:
                print "fail to download a file "
                print e
        time.sleep(1)        
        upload_file(final_file,mach_ip,api)
        start_print(final_file,mach_ip,api)
        print printfile_path

if __name__ == '__main__':
    #create_folder()
    #upload_file("d:\\test.gco")
    #start_print()
    pass