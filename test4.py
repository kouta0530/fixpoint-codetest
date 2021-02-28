import datetime


def convertLogToDateTime(log: str) -> datetime:
    if(len(log) != 14):
        return log

    return datetime.datetime(int(log[:4]), int(log[4:6]), int(log[6:8]), int(log[8:10]), int(log[10:12]), int(log[12:14]))


def getLog(path: str) -> (dict, dict):
    hashLog = {}
    network = {}

    with open(path) as f:
        for s in f.readlines():
            ns = s.split(",")
            # アドレスとアドレスのサブネットを取得
            address, subnet = getSubNetWork(ns[1])
            # サブネットを登録
            if subnet not in network:
                network[subnet] = []
            # アドレスを対応するサブネットに登録する
            if address not in hashLog:
                hashLog[address] = []
                network[subnet].append(address)

            hashLog[address].append([ns[0], ns[2].strip()])

    return hashLog, network


def getSubNetWork(address: str) -> (str, list):
    newAddress = address.split("/")
    addressList = [int(i) for i in newAddress[0].split(".")]
    mask = int(newAddress[1])
    maskValue = ""

    # サブネットマスクの作成
    for i in range(mask):
        maskValue += "1"

    for i in range(32 - mask):
        maskValue += "0"

    maskaddress = [int("0b"+maskValue[:8], 0), int("0b"+maskValue[8:16], 0),
                   int("0b"+maskValue[16:24], 0), int("0b"+maskValue[24:], 0)]

    # サーバーのアドレスとサブネットマスクのAND演算
    subnet = [str(int(bin(addressList[i] & maskaddress[i]), 0))
              for i in range(4)]
    return address, '.'.join(subnet)


def checkOverAvarageResponseTime(m: int, t: int, timelog) -> bool:
    m = m if m < len(timelog) else len(timelog)
    avgResponseTime = int(sum(timelog[len(timelog) - m:]) / m)

    return avgResponseTime > t


def checkSubNetworkFailer(servers: list, malFunctionLog: list) -> list:
    malServerNums = 0
    malStartDateTime = None
    malEndDateTime = None
    malDurationList = []
    subNetworkMalFunctionLog = []

    # サブネットに属するアドレスの故障ログをまとめる
    for srv in servers:
        if srv in malFunctionLog:
            subNetworkMalFunctionLog += malFunctionLog[srv]
    # 故障したログを確認日時順にソート
    subNetworkMalFunctionLog = sorted(
        subNetworkMalFunctionLog, key=lambda x: (x[0]))

    # サブネットごとの故障ログから故障を判定する
    # 詳しくはREADMEを参照
    for log in subNetworkMalFunctionLog:
        if log[1] == "start":
            malServerNums += 1
            if malServerNums == len(servers):
                malStartDateTime = log[0]
        elif log[1] == "fixed":
            if malServerNums == len(servers):
                malEndDateTime = log[0]
                malDurationList.append([malStartDateTime, malEndDateTime])

                malStartDateTime = None
                malEndDateTime = None

            malServerNums -= 1

    return malDurationList


def main(path: str, N=1, m=1, t=0):
    malFunctionLog = {}
    hashLog, network = getLog(path)

    # サブネットがないとき、サーバーもないため強制終了
    if hashLog is None or network is None:
        return "ログを取得できませんでした"

    for k in hashLog:
        logs = hashLog[k]
        tmplog = []
        timelog = []
        count = 0
        for log in logs:
            if log[1] == "-" and len(tmplog) == 0:
                tmplog = log
                count += 1
                continue
            elif len(tmplog) == 0:
                timelog.append(int(log[1]))
                continue

            if log[1] != "-" and len(tmplog) > 0:
                if count >= N:
                    if k not in malFunctionLog:
                        malFunctionLog[k] = []
                    startDateTime = convertLogToDateTime(tmplog[0])
                    fixedDateTime = convertLogToDateTime(log[0])

                    malFunctionLog[k].append(
                        [startDateTime, "start"])
                    malFunctionLog[k].append(
                        [fixedDateTime, "fixed"])

                    print("failed server", k, ":",
                          startDateTime, "~", fixedDateTime)

                timelog.append(int(log[1]))
                tmplog = []
                count = 0
            elif len(tmplog) > 0:
                count += 1

        if checkOverAvarageResponseTime(m, t, timelog):
            startDuration = convertLogToDateTime(logs[len(logs) - m - 1][0])
            endDuration = convertLogToDateTime(logs[-1][0])
            print("overload", k, ":", startDuration, "~", endDuration)

    print("")
    # サブネットごとの故障期間を求める
    for k in network:
        malDurationList = checkSubNetworkFailer(network[k], malFunctionLog)

        # 故障期間が空のとき、そのサブネットは故障していない
        if len(malDurationList) > 0:
            print("failed subnet:", k)
            for i in malDurationList:
                print(i[0], "~", i[1])


main("log4.txt", 2, m=2, t=500)
