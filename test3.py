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


def checkOverAvarageResponseTime(m: int, t: int, timelog: list) -> bool:
    # 直近m回よりログの総数が少ない場合はログの総数をチェック数とする
    m = m if m < len(timelog) else len(timelog)
    avgResponseTime = int(sum(timelog[len(timelog) - m:]) / m)

    #　平均応答時間がtより大きい
    return avgResponseTime > t


def main(path: str, N=1, m=1, t=0):
    malFunctionLog = {}
    hashLog = getLog(path)

    if hashLog is None:
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
            # 応答が帰ってきたとき、応答時間を記録
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
            # 故障時は応答時間を記録しない
            elif len(tmplog) > 0:
                count += 1

        # 各サーバーの平均応答時間がtを超えているとき
        # 直近からm番目を開始確認日時
        # 直近を終了確認日時とする
        if checkOverAvarageResponseTime(m, t, timelog):
            startDuration = convertLogToDateTime(logs[len(logs) - m - 1][0])
            endDuration = convertLogToDateTime(logs[-1][0])
            print("overload", k, ":", startDuration, "~", endDuration)


main("./log3.txt", 2, m=2, t=263)
