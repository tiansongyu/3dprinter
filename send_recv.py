# coding: utf-8
import json
import sys
import threading
import time
from collections import deque
from threading import Event
import paho.mqtt.client as mqtt
import getinfo
import pause_start
import upload
import random
import os
import RPi.GPIO as GPIO

event_post_info = Event()
#event_post_info.set()
semaphore_printfile = threading.Semaphore(0)
semaphore_isprint = threading.Semaphore(0)
reload(sys)
sys.setdefaultencoding('utf8')
#建立任务队列
q = deque()
printing_file_name = {"tempfilename":"","tempjobid":""}
global printfile_index
printfile_index={}
global mach_data 
global MQTTHOST
global MQTTPORT
global mqttClient
global mach_ip
global factoryID
#GPIO初始化
GPIO_PIN = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN)
mach_data = {"factoryId":"","mach_ip":"","machineCode":"","api":"","mqttip":"","mqttport":""}
def init_data():
    #初始化树莓派及打印机信息
    global MQTTHOST
    global MQTTPORT
    global mqttClient
	#当前文件的路径
    pwd = os.getcwd()
	#当前文件的父路径
    #father_path=os.path.abspath(os.path.dirname(pwd)+os.path.sep+".")
    final_file = "%s/machine_data/mach_info.json" % pwd
    with open(final_file, 'r') as f:
        temp = json.loads(f.read())
        print(temp)
    mach_data["factoryId"] = int(temp['factoryId'])
    mach_data["machineCode"] = temp['machineCode']
    mach_data["mach_ip"] = temp['mach_ip']
    mach_data["api"] = temp['api']
    MQTTHOST = temp['mqttip']
    MQTTPORT = temp['mqttport']
    #mqtt 服务器连接
    while True:
        try:
            client_id_random = random.randint(100, 999999)
            mqttClient = mqtt.Client(client_id=str(client_id_random), clean_session=True)
            mqttClient.username_pw_set("machine", "machine_12.34")# 必须设置，否则会返回「Connected with result code 4」
            mqttClient.connect(str(MQTTHOST), str(MQTTPORT), 60)
            mqttClient.loop_start()
            print "successfully connecting the mqtt"
            break
        except Exception, e:
            time.sleep(3)
            print "fail to connect the mqtt .try to connect again"
########################################## publish 消息
def on_publish(topic, payload, qos):        #发送服务器信息函数
    mqttClient.publish(topic, payload, qos)
########################################       
def on_message_come(lient, userdata, msg):  #接受消息处理函数，根据主题的不同处理不同消息
    get_json_data = json.loads(msg.payload)
    #print get_json_data
    global printing_file_name
    if get_json_data["type"] =="addQueue":       # ok
        print get_json_data
        for i in get_json_data["factory"]:       #判断添加任务命令是否是当前工厂
            if int(mach_data["factoryId"]) == i :
                if  q.count(get_json_data["jobId"]) == 0 :
                    #print get_json_data["jobId"]
                    printfile_index[get_json_data["jobId"]] = {"fileName":get_json_data["fileName"],"fileUrl":get_json_data["fileUrl"]}
                    print "add a new task to queue success "
                    q.append(get_json_data["jobId"])
                    semaphore_printfile.release()
                    print "success produce a new task" 
        #print printfile_index
    elif get_json_data["type"] =="removeQueue":    # ok 
        for i in get_json_data["factory"]:       #判断删除的命令是否指的是当前工厂
            if int(mach_data["factoryId"]) == i :
                if q.count(get_json_data["jobId"]) > 0 :
                    q.remove(get_json_data["jobId"])
                    del printfile_index[get_json_data["jobId"]]
                    print "removeQueue"
                    #print get_json_data["fileUrl"]
                break
                
    elif get_json_data["type"] =="resExecute":
            print "type   ==     resExecute:"
            #print get_json_data
        #for i in get_json_data["machineCode"]:       #判断收到的打印指是否是当前机器
            if mach_data["machineCode"] == get_json_data["machineCode"]:    
                print get_json_data
                print "machineCode"
                if int(get_json_data["ack"]) == 1:
                    #开始打印文件  唯一一个直接控制打印机命令
                    file_jobId_ = q.popleft()
                    q.appendleft(file_jobId_)
                    printfile_path = printfile_index[file_jobId_]["fileUrl"]
                    printfile_name = printfile_index[file_jobId_]["fileName"]
                    upload.down_load_printfile(printfile_name,printfile_path,mach_data["mach_ip"],mach_data["api"])
                    #存储当前打印的文件名
                    printing_file_name["tempfilename"] = printfile_name
                    #print "print file name is %s" % printing_file_name
                    print "start to print get_json_data[file]"
                    semaphore_isprint.release()
                elif int(get_json_data["ack"]) == 0:
                    q.remove(get_json_data["jobId"])
                    del printfile_index[get_json_data["jobId"]]
                    semaphore_printfile.release()
                    #从队列中删除当前任务，并发送一个打印请求
                
    elif get_json_data["type"] =="reqMonitor":
            #接收到发送状态信息信号
            #print "req_monitor accept . start to post machine information"
            #for i in get_json_data["factoryId"]:       #判断发送信息指令是否是当前工厂的机器
            if int(mach_data["factoryId"]) == int(get_json_data["factoryId"]):    
                #semaphore_post_info.release() #发送一个持续发送状态信息的信号
                event_post_info.set()
                print "req_monitor accept . start to post machine information"
               
    elif get_json_data["type"] =="reqStopMonitor":
        #接收到停止发送状态信息信号
        #for i in get_json_data["factoryId"]:       #判断取消发送信息指令是否是当前工厂的机器
            #print "reqStopMonitor accept . stop to post machine information"      
            if int(mach_data["factoryId"]) == int(get_json_data["factoryId"]):    
                event_post_info.clear() #接收到停止发送信息的信号
                print "reqStopMonitor accept . stop to post machine information"      
               
    elif get_json_data["type"] =="control":
        #for i in get_json_data["machineCode"]:       #判断收到的打印指是否是当前机器
            print "type  == control"
            if mach_data["machineCode"] == get_json_data["machineCode"]:     
                if get_json_data["typeControl"] == "pause" :
                    pause_start.pause(mach_data["mach_ip"],mach_data["api"])
                elif get_json_data["typeControl"] == "resume" :
                    pause_start.resume(mach_data["mach_ip"],mach_data["api"])
                elif get_json_data["typeControl"] == "cancel" :
                    pause_start.cancel(mach_data["mach_ip"],mach_data["api"])
    # elif get_json_data["type"] =="orderStart":
    #         print get_json_data 
    #         print "orderStart"
    #         if mach_data["machineCode"] == get_json_data["machineCode"]:     
    #             if get_json_data["ack"] == 1 :
    #                 semaphore_printfile.release() #发送一个打印请求
def print_process():
    temp_json =  {"jobId":"","machineCode":"","type":"reqExecute"}
    while True:
        #只要是队列数量大于0并且打印机是空闲状态，就开始请求。
        print("printer is waiting for the task.........")
        semaphore_printfile.acquire() #消费一个打印请求信号量
        flag = getinfo.get_isrunning(mach_data["mach_ip"],mach_data["api"])
        #flag表示是否满足空闲状态
        if len(q)>0 and flag == 2 :      #打印队列中至少有一个并且打印机是空闲状态时，发送一个打印请求。否则丢弃这个信号量
            file_jobId = q.popleft()
            q.appendleft(file_jobId)
            temp_json["jobId"] = file_jobId
            temp_json["machineCode"] = mach_data["machineCode"]
            on_publish("reqPrintFile", json.dumps(temp_json), 2)
            print "post a printing request"
        #time.sleep(1)
def post_info():
    mach_info_json =  {"factoryId":"","machineCode":"","type":"","status":"","fileName":"","connection":"","controlStatus":"","process":"0","bedTemperature":"","toolTemperature":"","alarmType":"","printTime":"","printTimeLeft":"","createTime":""}
    mach_info_json["factoryId"] = int(mach_data["factoryId"])
    mach_info_json["machineCode"] = mach_data["machineCode"]
    global printing_file_name
    while True:
        time.sleep(3)
        try :
            _data = getinfo.get_factoryMessage(mach_data["mach_ip"],mach_data["api"])
        except Exception, e:
            pass
        if _data != 0:
            print _data
            print "okokoko"
            break
        else :
            print _data
            print "fail to post"
    while True:
        event_post_info.wait()
        #持续发送温度信息4
        mach_mon_data = getinfo.get_factoryMessage(mach_data["mach_ip"],mach_data["api"])
        mach_info_json["process"] = mach_mon_data["process"]
        if ((getinfo.get_isrunning(mach_data["mach_ip"],mach_data["api"]) == 1) or (getinfo.get_isrunning(mach_data["mach_ip"],mach_data["api"]) == 3)) :
            mach_info_json["status"] = 1
            # file_jobId = q.popleft()
            # q.appendleft(file_jobId)
            mach_info_json["fileName"] = printing_file_name["tempfilename"]
            mach_info_json["process"] = mach_mon_data["process"]
            mach_info_json["printTime"] = mach_mon_data["printTime"]
            mach_info_json["printTimeLeft"] = mach_mon_data["printTimeLeft"]
            mach_info_json["createTime"] = mach_mon_data["createTime"]
        else :
            mach_info_json["status"] = 0 
            mach_info_json["fileName"] == ""
            mach_info_json["process"] = 0   
            mach_info_json["printTime"] = 0
            mach_info_json["printTimeLeft"] = 0
            mach_info_json["createTime"] = int(time.time())
        mach_info_json["connection"] = mach_mon_data["connection"]
        mach_info_json["controlStatus"] = mach_mon_data["controlStatus"]
        mach_info_json["bedTemperature"] = mach_mon_data["bedTemperature"]
        mach_info_json["toolTemperature"] = mach_mon_data["toolTemperature"]
        if (float(mach_info_json["bedTemperature"]) > 260 ) and (float(mach_info_json["toolTemperature"]) > 70):
            mach_info_json["type"] = "alarm"
            if (float(mach_info_json["bedTemperature"]) > 260 ) and (float(mach_info_json["toolTemperature"]) > 70):
                mach_info_json["alarmType"] = {"bedTemperature","toolTemperature"}
            elif  (float(mach_info_json["bedTemperature"]) <= 260 ) and (float(mach_info_json["toolTemperature"]) > 70):
                mach_info_json["alarmType"] = {"toolTemperature"}
            else :
                mach_info_json["alarmType"] = {"bedTemperature"}
            pause_start.pause(mach_data["mach_ip"],mach_data["api"])
        else :
            mach_info_json["type"] = "normal"

        alarm_info = {"factoryId":"","machineCode":"","jobId":"","alarmType":"1","createTime":""}
        # mach_info_json["factoryId"] = int(mach_data["factoryId"])
        # mach_info_json["machineCode"] = mach_data["machineCode"]   
        alarm_info["factoryId"] =  mach_info_json["factoryId"]
        alarm_info["machineCode"] = mach_info_json["machineCode"]
        if getinfo.get_isrunning(mach_data["mach_ip"],mach_data["api"]) == 2 :
            alarm_info["jobId"] = 0
        else :
            alarm_info["jobId"] = printing_file_name["tempjobid"] 
        alarm_info["alarmType"]  = "1"
        alarm_info["createTime"] = int(time.time())
        
        on_publish("monitor", json.dumps(mach_info_json), 0)
        on_publish("alarm", json.dumps(alarm_info), 2)
        time.sleep(1)
def recvMsg():
        mqttClient.subscribe("operateFile", 1)
        mqttClient.subscribe("reqMonitor", 2)
        mqttClient.subscribe("resPrintFile", 2)
        mqttClient.subscribe("control", 2)       
        mqttClient.subscribe("orderStart", 2)       
        mqttClient.on_message = on_message_come # 消息到来处理函数
def last_mon():
    global GPIO
    while True:
        semaphore_isprint.acquire()
            #每隔一段时间就检测打印机状态是否在打印，如果在打印则循环检测
            #如果不在打印，则发送一个请求打印命令
        while True:
            time.sleep(20)
            #检测打印
            flag = getinfo.get_isrunning(mach_data["mach_ip"],mach_data["api"])
            if flag == 2 :  #2代表绝对空闲
                # overjob = {"machineCode":"","type":"overJob","createTime":""}
                # overjob["machineCode"] = mach_data["machineCode"]
                # overjob["createTime"] = int(time.time())
                # on_publish("overJob", json.dumps(overjob), 0)

                #print("waiting 5 times...")
                count = 10 
                print "start to wait the start order"
                while count > 0:
                    if(GPIO.input(GPIO_PIN) == 1):
                        count = count - 1
                        print("input high")
                    else :
                        count = 10
                        continue
                    time.sleep(0.1)

                semaphore_printfile.release() #发送一个打印请求
                break
def start_thread():
        init_data()
        tr = threading.Thread(target=recvMsg) 
        ts = threading.Thread(target=print_process)
        always_tr = threading.Thread(target=last_mon)
        t_post_mach_info = threading.Thread(target=post_info) 
        always_tr.start()
        t_post_mach_info.start()
        tr.start()
        ts.start()
if __name__ == '__main__':
    start_thread()
    while True:
        time.sleep(1000)
