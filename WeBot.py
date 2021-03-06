# -*- coding: UTF-8 -*-
import itchat #微信核心库
import os
import platform
import time
import win32api,win32con #提示框库
import requests
import json
from threading import Thread #多线程
from apscheduler.schedulers.blocking import BlockingScheduler #计划任务
from apscheduler.triggers.cron import CronTrigger
import io #发送图片使用

#配表摸块
import xdrlib ,sys
import xlrd
import xlwt
from collections import defaultdict
#from xlutils.copy import copy  #修改字典dataDict后再写入新建的一个excel表覆盖保存，与此库功能没有本质区别

# 打开excel文件
def open_excel(file):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception as e:
        print(str(e))

# 根据名称获取Excel表格中的数据   参数:file：Excel文件路径     colnameindex：表头列名所在行的索引   by_name：Sheet1名称
def get_dataDict(file, colnameindex, by_name):
    if not os.path.isfile(file):
        file = input("未找到配表,请手动将表格拖进来:") 
    data = open_excel(file) #打开excel文件
    table = data.sheet_by_name(by_name) #根据sheet名字来获取excel中的sheet
    nrows = table.nrows #行数 
    colnames = table.row_values(colnameindex) #某一行数据 
    dataDict = defaultdict(list) #装读取结果的序列
    for rownum in range(0, nrows): #遍历每一行的内容
        row = table.row_values(rownum) #根据行号获取行
        varName = row[0]
        if row: #如果行存在
            for i in range(len(colnames)-1): #一列列地读取行的内容
                if row[i+1]:
                    dataDict[varName].append(row[i+1])
    return dataDict

# 更新表格
def update_dataDict(file, dataDict):
    if not os.path.isfile(file):
        file = input("未找到配表,请手动将表格拖进来:")
    workbook = xlwt.Workbook(encoding = 'utf-8')
    worksheet = workbook.add_sheet("setting")
    row = 0
    for key, values in dataDict.items():
        worksheet.write(row, 0, key)
        col = 1
        for value in values:
            worksheet.write(row, col, value)
            print(col)
            col += 1
        row += 1
    try:
        os.remove(file)
        workbook.save(file)
        itchat.send("改表成功", toUserName="filehelper")
        print("改表成功")
    except Exception as e:
        print(str(e))


# 将多条文字信息(list)合并为一条
def merge_txtMsg(msgList):
    txtMsg = ""
    for msg in msgList:
        txtMsg = txtMsg + str(msg) + "\n"
    return txtMsg


# 根据昵称等取UserName
def get_UserName(get_name):
    try:
        UserName = itchat.search_friends(remarkName=get_name)[0]["UserName"] #备注名匹配
    except:
        try:
            UserName = itchat.search_friends(nickName=get_name)[0]["UserName"]#昵称匹配
        except:
            try:
                UserName = itchat.search_friends(Alias=get_name)[0]["UserName"] #微信号匹配
            except:
                print("没找到"+str(get_name)+"这号人物")
    #print(UserName)
    return UserName

def get_permissionUser(names,permissionUser):
    for get_name in names:
        try:
            permissionUser.append(get_UserName(get_name)) #备注名匹配
        except:
            print("没找到"+str(get_name)+"这号人物")
    return permissionUser

# 截屏模块
def get_ImagePath():
    if not os.path.exists("./ScreenShoot/"):
        os.mkdir("./ScreenShoot/")
    return "./ScreenShoot/"


def get_SceenShot(userid):
    im_path = get_ImagePath()
    im_name = "{}{}.{}".format(im_path, int(time.time()), "png")
    im = None

    if platform.system() == "Windows" or platform.system() == "Darwin":
        try:
            from PIL import ImageGrab
            im = ImageGrab.grab()
        except OSError as e:
            itchat.send("截图失败，请重试。", toUserName=userid)
            return

    elif platform.system() == "Linux":
        try:
            import pyscreenshot as ImageGrab
            im = ImageGrab.grab()
        except OSError as e:
            itchat.send("截图失败，请重试。", toUserName=userid)
            return
    im.save(im_name)

    if os.path.exists(im_name):
        try:
            itchat.send_image(im_name, toUserName=userid)
        except BaseException as e:
            import traceback
            traceback.print_exc()
            itchat.send("发送截图失败，请重试。", toUserName=userid)
    else:
        itchat.send("截图失败，请重试。", toUserName=userid)

# 设置计划任务模块
def add_Plan(timing,noticeMsg):
    global initData
    myplan = Thread(target=set_Scheduler, args=(timing,noticeMsg))
    myplan.start()
    itchat.send(" >>将会在 "+timing+"提醒你:\n"+noticeMsg, toUserName="filehelper")
    try:
        initData['plansNum'][0] += 1
        initData['timeSet'].append(timing)
        initData['noticeMsg'].append(noticeMsg)
        update_dataDict(excel,initData)
    except:
        print("改表失败,如果想加入默认提醒,记得手动改一下哦")

#清空提醒计划，但未加入停止子线程的功能
def del_Plan():
    global initData
    try:
        initData['plansNum'][0] = 0
        initData['timeSet'] = ["无"]
        initData['noticeMsg'] = ["无"]
        update_dataDict(excel,initData)
        itchat.send("已清空默认提醒", toUserName="filehelper")
    except:
        itchat.send("删除失败,需要手动改表哦", toUserName="filehelper")
        print("删除失败,需要手动改一下哦")

def set_Scheduler(timing,noticeMsg):
    sched = BlockingScheduler()
    trigger = CronTrigger(hour=int(timing.split(":")[0]),minute=int(timing.split(":")[1]),second=int(timing.split(":")[2]))
    sched.add_job(send_Notice, trigger, args=[noticeMsg]) #定时发送提醒
    #sched.add_job(send_Notice, "cron",hour=int(timing.split(":")[0]),minute=int(timing.split(":")[1]),second=int(timing.split(":")[2]),args=[noticeMsg])
    sched.start()
    print("已启动计划任务")

def send_Notice(noticeMsg):
    itchat.send(noticeMsg, toUserName="filehelper")
    print("发送计划提醒")

def get_Dict(lists,userid):
    for list_Dicts in lists:
        list_Dict(list_Dicts,userid)

# 递归遍历字典里的内容，并按类型发送消息
def list_Dict(dicts,userid):
    if type(dicts) == list: 
        get_Dict(dicts,userid)
    else:
        #print("开始遍历")
        for key,value in dicts.items():
            try: #尝试遍历子级字典或列表
                #print("\nKeys:"+key)
                list_Dict(value,userid)
            except AttributeError: #不存在子级则代表已取出内容，根据类型回复消息，目前只捣鼓了 新闻 和 一般文字回复
                #print("\nKeys:"+key+" value:"+str(value)+"\n")
                if key == "text":
                    itchat.send(" "+value,toUserName=userid)
                if key == "name":
                    itchat.send(" "+value,toUserName=userid)
                if key == "icon" and value:
                    # 取网络图片暂存
                    if value[0] == "/": #返回的URL格式不一致，需要看情况补全
                       value = "http:"+str(value)
                    img = requests.get(value, stream=True)
                    imageStorage = io.BytesIO()
                    for block in img.iter_content(1024):
                        imageStorage.write(block)
                    imageStorage.seek(0)
                    itchat.send_image(imageStorage,toUserName=userid)
                if key == "detailurl":
                    itchat.send(" "+value,toUserName=userid)
                    time.sleep(1)
                    itchat.send("点击链接看详情哟",toUserName=userid)
                    time.sleep(2) #为了避免多条新闻轰炸（微信也不允许连发过多），设置了延时


def get_Response(msg,user):
    print("请求图灵回复")
    # 构造了要发送给服务器的数据
    apiUrl = "http://openapi.tuling123.com/openapi/api/v2"
    data = {
        "reqType":0,
        "perception": {
            "inputText": {
                "text": msg
            },
            "selfInfo": {
                "location": {
                    "city": "广州",
                    "province": "广东",
                    "street": "你心里"
                }
            }
        },
        "userInfo": {
            "apiKey": turlingKey,
            "userId": user
        }
    }
    json_data = json.dumps(data) #转换为json格式

    try:
        r = requests.post(apiUrl, data=json_data).json()
        print(r)  #返回值为列表与字典的嵌套
        val = r["results"]#图灵机器人2.0 api里支持5种不同类型的回复，这一步先返回result不判断类型
        return val
    except: # 如果服务器没能正常交互（返回非json或无法连接），那么就会进入下面的return
        print("请求异常")
        # 将会返回一个None
        return

# 图灵机器人回复模块
def get_TulingReply(msg,user,userid):
    defaultReply = "闭嘴，说人话" # 为了保证在图灵Key出现问题的时候仍旧可以回复，这里设置一个默认回复
    reply = get_Response(msg,user) # 如果图灵Key出现问题，那么reply将会是None
    if reply:
        list_Dict(reply,userid)
    else:
        itchat.send(defaultReply, toUserName=userid)


# 执行指令
def get_Reaction(message,userid):
    global robotToVip,robotToAll,permissionUser,permissionUserName,initData

    #判断是不是指令
    if message[0] == "*": 
        #定制提醒及回复
        if message == "*傻狗":
            win32api.MessageBox(0, "微信来消息啦", "傻狗信息",win32con.MB_OK) # 接收到消息弹框提醒
            itchat.send("来啦来啦", toUserName=userid)

        elif message == "*我是傻狗":
            itchat.send("傻狗，你咋不上天，还想关我电脑", toUserName=userid)

        # cmd命令，可以实现远程操作电脑
        elif message[0:4] == "*cmd":
            print("执行命令行")
            os.system(message.strip(message[0:5])) # 获得指令的另一种写法，实际和*open一个功能
            itchat.send(" >>喳", toUserName=userid)

        # 待机命令
        elif message == "*待机":
            print("准备待机")
            itchat.send(" >>待机成功", toUserName=userid)
            os.system("rundll32.exe powrProf.dll SetSuspendState")

        # 关机命令, 仅支持自己控制
        elif message == "*关机" and userid == "filehelper":
            print("正在关机")
            itchat.send(" >>正在关机", toUserName=userid)
            os.system("shutdown -s -t 10")

        # 截屏查看当前工作桌面
        elif message == "*截屏":
            print("正在截屏")
            get_SceenShot(userid)

        # cmd打开文件夹或应用程序 可自行修改
        elif message.split("|")[0] == "*open":
            print("打开")
            os.system(message.split("|")[1])
            itchat.send(" >>喳", toUserName=userid)

        #下载文件指令
        elif message.split("|")[0] == "*download":
            print("下载文件"+message.split("|")[1])
            itchat.send_file(message.split("|")[1], toUserName=userid)
        #拦截cd命令通过os.chdir来实现目录切换
        elif message.split("|")[0] == "*cd":
            os.chdir(message.split("|")[1])
            itchat.send(" >>已经切换目录", toUserName=userid)

        #设置提醒
        elif message.split("|")[0] == "*plan":
            if userid == "filehelper":
                add_Plan(message.split("|")[1],message.split("|")[2])
            else: #目前数据结构其他用户只能建立临时提醒任务
                myplan = Thread(target=set_Scheduler, args=(message.split("|")[1],message.split("|")[2]))
                myplan.start()
                itchat.send(" 我将会在 "+timing+"提醒你:\n"+noticeMsg, toUserName=userid) 



        # 机器人开关
        elif message == "*观诗音来":
            if userid == "filehelper":
                robotToVip = True
                if not initData['robotToVip']:
                    try:
                        initData['robotToVip'][0] = "开"
                        update_dataDict(excel,initData)
                    except:
                        itchat.send("删除失败,需要手动改表哦", toUserName="filehelper")
                        print("改表失败,如果想默认开启,记得手动改一下哦")
            elif not userid in tulingList:
                tulingList.append(userid)
            itchat.send(" >>已开启机器人观诗音，现在不需要加 - 也可以和小鸡儿机器人聊天啦", toUserName=userid)

        elif message == "*观诗音走":
            if userid == "filehelper":
                robotToVip = False
                if initData['robotToVip']:
                    try:
                        initData['robotToVip'][0] = "关"
                        print(robotToVip)
                        update_dataDict(excel,initData)
                        print("update_dataDict!")
                    except Exception as e:
                        itchat.send("删除失败,需要手动改表哦", toUserName="filehelper")
                        print("改表失败,如果想默认关闭,记得手动改一下哦")
                        print(str(e))
            elif userid in tulingList:
                tulingList.remove(userid)
            itchat.send(" >>已关闭机器人观诗音，如果要临时召唤她，请在信息最开头加 - ", toUserName=userid)

        # 本人专用设置
        elif message == "*delplan" and userid == "filehelper":
            del_Plan() #清空提醒计划

        elif message == "*开大" and userid == "filehelper":
            robotToAll = True # 默认都是关闭
            itchat.send(" >>观诗音撩骚全场，会自动回复全部好友（不包括群聊）", toUserName=userid)

        elif message == "*闭嘴" and userid == "filehelper":
            robotToAll = False
            itchat.send(" >>观诗音自闭了，如果要临时召唤她，请在信息最开头加 - ", toUserName=userid)

        elif message.split("|")[0] == "*授权" and userid == "filehelper":
            try:
                permissionUser.append(get_UserName(message.split("|")[1]))
                itchat.send(" 添加成功", toUserName=userid)
                itchat.send(othersMsg, toUserName=permissionUser[-1])
                if not message.split("|")[1] in permissionUserName:
                    permissionUserName.append(message.split("|")[1])
                    try:
                        initData['permissionUserName'].append(message.split("|")[1])
                        update_dataDict(excel,initData)
                    except:
                        itchat.send("删除失败,需要手动改表哦", toUserName="filehelper")
                        print("改表失败,记得手动改一下哦")
            except:
                itchat.send(" 没找到这个人", toUserName=userid)

        elif message.split("|")[0] == "*夺权" and userid == "filehelper":
            try:
                permissionUser.remove(get_UserName(message.split("|")[1]))
                itchat.send(" 删除成功", toUserName=userid)
                if message.split("|")[1] in permissionUserName:
                    permissionUserName.remove(message.split("|")[1])
                    try:
                        initData['permissionUserName'].remove(message.split("|")[1])
                        update_dataDict(excel,initData)
                    except:
                        itchat.send("删除失败,需要手动改表哦", toUserName="filehelper")
                        print("改表失败,记得手动改一下哦")
            except:
                itchat.send(" 这个人并没有获得授权", toUserName=userid)
                

    #如果非指令则和图灵机器人聊天
    else:
        if userid == "filehelper": 
            print("开始和小鸡儿器人聊天")
            user = "koon"
            get_TulingReply(message,user,"filehelper")

        elif message[0] == "-":
            print("小鸡儿机器人正在和别人聊天")
            user = userid[1:10] #取其中若干个字符做为机器人user标识
            get_TulingReply(message[1:],user,userid)

        elif userid in tulingList and robotToVip:
            user = userid[1:10]
            get_TulingReply(message,user,userid)


# 自动回应个人消息
@itchat.msg_register("Text")
def text_reply(msg):
    global flag
    message = msg["Text"]
    userid = msg["FromUserName"]

    # 文件助手命令逻辑
    # 如果发送消息给文件传输助手
    if msg.toUserName == "filehelper":
        # 显示命令内容
        print(userid+":"+msg["Content"])
        if not message[0] == " ": # 避免图灵回应自己发送的信息
            try:
                get_Reaction(message,"filehelper")
            except:
                itchat.send(" >>我就不干,你管我什么原因", toUserName="filehelper")
    elif userid in permissionUser: # 有权限用户同样获得控制权
        print(userid+":"+msg["Content"])
        try:
            get_Reaction(message,userid)
        except:
            itchat.send(" >>我就不干,你管我什么原因", toUserName="filehelper")
    else:
        if robotToAll:
            get_TulingReply(message,user,userid)
            

if __name__ == "__main__":
    itchat.auto_login(hotReload=True, enableCmdQR=True)

    # 从excel表读取新变量
    if not os.path.isfile('.\\setting.xls'):
        excel = input("未找到配表,请手动将表格拖进来:") 
    else:
        excel = '.\\setting.xls'
    initData = get_dataDict(excel,0,u'setting') #表格内容以字典形式返回，第一列为keys

    # 把字典相关变量取出来,作为全局变量
    permissionUserName = initData['permissionUserName']
    turlingKey = str(initData['turlingKey'][0])
    myMsg = merge_txtMsg(initData['myMsg'])
    othersMsg = merge_txtMsg(initData['othersMsg'])
    plansNum = int(initData['plansNum'][0])
    timeSet = initData['timeSet']
    noticeMsg = initData['noticeMsg']

    if initData['robotToVip'][0] == "开":  
        robotToVip = True
    else:
        robotToVip = False
    if initData['robotToAll'][0] == "开":  
        robotToAll = True
    else:
        robotToAll = False

    # 预设任务提醒
    if plansNum > 0:
        for i in range(plansNum):
            myplan = Thread(target=set_Scheduler, args=(timeSet[i],noticeMsg[i]))
            myplan.start()
            print("启动第"+str(i+1)+"个任务，时间"+ timeSet[i]+"\n"+noticeMsg[i]+"\n")
        #print("已启动多线程,共"+str(i+1)+"个任务")

    # 根据permissionUserName内容自动取得UserName
    permissionUser = []
    permissionUser = get_permissionUser(permissionUserName,permissionUser)
    turlingList = permissionUser # 初始化图灵自动回复的人
    for username in permissionUser:
        itchat.send(othersMsg, toUserName=username) # 发通知已经开启功能

    itchat.send(myMsg, toUserName="filehelper")
    itchat.run()
    print("已启动监听")


  