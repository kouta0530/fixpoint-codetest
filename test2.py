import datetime


def convertLogToDateTime(log: str) -> datetime:
    if(len(log) != 14):
        return log

    return datetime.datetime(int(log[:4]), int(log[4:6]), int(log[6:8]), int(log[8:10]), int(log[10:12]), int(log[12:14]))


def getLog(path: str) -> hash:
    hashLog = {}

    with open(path) as f:
        for s in f.readlines():
            ns = s.split(",")
            address = ns[1]

            if address not in hashLog:
                hashLog[address] = []

            hashLog[address].append([ns[0], ns[2].strip()])

    return hashLog


def main(path: str, N: int):
    malFunctionLog = {}
    hashLog = getLog(path)

    if hashLog is None:
        return "ログを取得できませんでした"

    for k in hashLog:
        logs = hashLog[k]
        tmplog = []
        # 故障回数
        count = 0

        for log in logs:
            if log[1] == "-" and len(tmplog) == 0:
                tmplog = log
                count += 1
                continue
            elif len(tmplog) == 0:
                continue

            if log[1] != "-" and len(tmplog) > 0:
                # 応答結果"-"がN回以上計測されたとき
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
                tmplog = []
                count = 0
            # 故障開始以降、応答結果が"-"のとき
            elif len(tmplog) > 0:
                count += 1


for i in range(1, 5):
    print(i)
    main("./log2.txt", i)
