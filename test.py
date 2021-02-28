import datetime


def convertLogToDateTime(log: str) -> datetime:
    # 確認日時のフォーマットが不正のときは入力値を返す
    if(len(log) != 14):
        return log

    return datetime.datetime(int(log[:4]), int(log[4:6]), int(log[6:8]), int(log[8:10]), int(log[10:12]), int(log[12:14]))


def getLog(path: str) -> hash:
    hashLog = {}

    with open(path) as f:
        for s in f.readlines():
            # 確認日時、サーバーアドレス、応答結果の配列に変換
            ns = s.split(",")
            address = ns[1]

            # サーバーアドレスごとにログをまとめる
            if address not in hashLog:
                hashLog[address] = []

            hashLog[address].append([ns[0], ns[2].strip()])

    return hashLog


def main(path):
    malFunctionLog = {}
    hashLog = getLog(path)

    # ログが取得できないときは強制終了
    if hashLog is None:
        return "ログを取得できませんでした"

    # サーバーごとにログを確認する
    for k in hashLog:
        logs = hashLog[k]
        tmplog = []

        for log in logs:
            # tmplogが空のとき、そのサーバーが故障していることを示す
            if log[1] == "-" and len(tmplog) == 0:
                tmplog = log
                continue
            elif len(tmplog) == 0:
                continue
            # すでに故障していて、応答が帰ってきたとき
            if log[1] != "-" and len(tmplog) > 0:
                # 初めてそのサーバーが故障したときkeyを追加
                if k not in malFunctionLog:
                    malFunctionLog[k] = []

                # 開始期間と終了期間を読み込み、記録する
                startDateTime = convertLogToDateTime(tmplog[0])
                fixedDateTime = convertLogToDateTime(log[0])

                malFunctionLog[k].append(
                    [startDateTime, "start"])
                malFunctionLog[k].append(
                    [fixedDateTime, "fixed"])

                print("failed server", k, ":",
                      startDateTime, "~", fixedDateTime)

                tmplog = []


main("./log.txt")
