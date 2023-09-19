import requests
import urllib3
import json
import time
import datetime
import threading

urllib3.disable_warnings()

myHeaders = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Mobile Safari/537.36 Edg/97.0.1072.62"
}
s = requests.session()
s.headers = myHeaders

dynmapDomain = "https://map.oiercraft.top" # 您的服务器dynmap域名
myIP = "115.192.87.200" # 您自己的IP(防止发出的消息又被接收)


def getRes(): # 获取服务器信息
    while True:
        t = int(time.time() * 1000 - 2000)
        res = s.get(
            dynmapDomain+"/up/world/world/" + str(t), verify=False
        ).content
        res = res.decode("utf-8")

        try:
            res = json.loads(res)
        except:
            time.sleep(3)
            continue

        break
    return res


def sendMsg(msg): # 向服务器发送消息
    while True:
        try:
            post = s.post(
                dynmapDomain+"/up/sendmessage",
                json={"name": "", "message": msg},
                timeout=10000,
                verify=False,
            )
        except:
            continue

        break
    return post.status_code


def showPlayerList(): # 玩家列表
    currentCount = getRes()["currentcount"]
    playerList = getRes()["players"]
    print("目前有 " + str(currentCount) + " 名玩家在线")
    for p in playerList:
        print("玩家名称: " + p["name"])
        print("玩家位置: " + str(p["x"]) + "," + str(p["y"]) + "," + str(p["z"]))
        print("玩家血量/盔甲值: " + str(p["health"]) + " / " + str(p["armor"]))
    return


def broadCastPlayerPos() -> None: # 广播玩家位置
    while True:
        playerList = getRes()["players"]
        for p in playerList:
            code = sendMsg(
                "[坐标广播]玩家 "
                + p["name"]
                + " 位于坐标 "
                + str(p["x"])
                + ","
                + str(p["y"])
                + ","
                + str(p["z"])
            )
            if code == 200:
                print(datetime.datetime.now().strftime("[%H:%M:%S] ")+"成功广播坐标")
            else:
                print(datetime.datetime.now().strftime("[%H:%M:%S] ")+"广播坐标失败:错误码 " + str(code))

        time.sleep(30) # 每隔30秒广播一次


def showServerMsg() -> None: #接收服务器消息
    while True:
        updates = getRes()["updates"]
        for u in updates:
            if u["type"] == "chat":
                if u["playerName"] != myIP:
                    print(datetime.datetime.now().strftime("[%H:%M:%S] ")+u["playerName"] + ":" + u["message"])
            elif u["type"] == "playerjoin":
                print(datetime.datetime.now().strftime("[%H:%M:%S] ")+u["playerName"] + " 加入了游戏")
            elif u["type"] == "playerquit":
                print(datetime.datetime.now().strftime("[%H:%M:%S] ")+u["playerName"] + " 退出了游戏")
        time.sleep(2)
    return


msgThread = threading.Thread(target=showServerMsg)
msgThread.start() # 接收服务器消息线程

broadCastThread = threading.Thread(target=broadCastPlayerPos)
broadCastThread.start() # 广播玩家坐标线程

while True:
    msg = input()
    if msg == "show":
        showPlayerList()
    else:
        sendMsg(msg)
