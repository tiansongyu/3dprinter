# coding: utf-8
#获取打印机状态信息
import re
import time
import json
import requests
def getnow():
    post_data = {"factoryID":"","factoryName":"","adminID":"","type":""}
def get_factoryMessage(mach_ip,api):

    factoryMessage =  { "status":"",            #？？？？
                        "connection":"",        #连接状态？？？
                        "controlStatus":"",     #打印状态？？？
                        "process":"",           #Ok
                        "bedTemperature":"",    #ok
                        "toolTemperature":"",   #ok
                        "printTime":"",         #ok
                        "printTimeLeft":"",     #ok
                        "createTime":""}        #ok
    headers={'X-Api-Key': api}

    ip_add = "/api/printer?exclude=sd"
    ip_header = "http://"
    final_ip  = '%s%s%s' % (ip_header,mach_ip,ip_add)
    r = requests.get(final_ip,headers = headers)

    ip_add2 = "/api/job"
    ip_header = "http://"
    final_ip2  = '%s%s%s' % (ip_header,mach_ip,ip_add2)
    r_connection = requests.get(final_ip2,headers = headers)
    if r.status_code == 200:
        json_file = r.json()
        json_file_connection = r_connection.json()
        factoryMessage["toolTemperature"] =json_file["temperature"]["tool0"]["actual"]
        factoryMessage["bedTemperature"] =json_file["temperature"]["bed"]["actual"]
        #factoryMessage["status"] =   json_file["state"]["text"]
        if get_isrunning(mach_ip,api) == 2 : #空闲状态
            factoryMessage["controlStatus"] = 1 
        elif get_isrunning(mach_ip,api) ==3 :  #暂停状态
            factoryMessage["controlStatus"] = 0
            factoryMessage["process"] =json_file_connection["progress"]["completion"]
            factoryMessage["printTime"] =json_file_connection["progress"]["printTime"]
            factoryMessage["printTimeLeft"] =json_file_connection["progress"]["printTimeLeft"]
            factoryMessage["createTime"] =json_file_connection["job"]["file"]["date"]
        else :
            #print json_file_connection #打印状态
            factoryMessage["controlStatus"] = 1  
            factoryMessage["process"] =json_file_connection["progress"]["completion"]
            factoryMessage["printTime"] =json_file_connection["progress"]["printTime"]
            factoryMessage["printTimeLeft"] =json_file_connection["progress"]["printTimeLeft"]
            factoryMessage["createTime"] =json_file_connection["job"]["file"]["date"]
        return factoryMessage
    else :
        print "get moniter information fail"
        return 0
def get_isrunning(mach_ip,api):
    headers={'X-Api-Key': api}
    ip_add = "/api/printer?exclude=temperature,sd"
    ip_header = "http://"
    final_ip  = '%s%s%s' % (ip_header,mach_ip,ip_add)
    r = requests.get(final_ip,headers = headers)     
    #  "flags": {
    #   "operational": true,
    #   "paused": false,
    #   "printing": false,
    #   "cancelling": false,
    #   "pausing": false,
    #   "sdReady": true,
    #   "error": false,
    #   "ready": true,
    #   "closedOrError": false
    # }
    #isprinting  返回1 表示打印 返回2 表示不在打印 返回3 表示暂停状态
    if r.status_code == 200:
            json_file = r.json()
            if json_file["state"]["text"] =="Printing" :
                return 1   #打印状态
            elif (json_file["state"]["text"] == "Paused") or ( json_file["state"]["text"] == "Pausing"):
                return 3   #暂停状态
            elif json_file["state"]["text"] =="Operational" :
                return 2   #空闲状态
            else :
                return 4
    else:
        print "get_isrunning is fail. can not print somethin now"
if __name__ == '__main__':
    #get_factoryMessage()
    pass