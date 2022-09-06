import os
import datetime
import csv
import pandas as pd
import tweepy

# Twitter Deverloper Portalで取得
ck = ''
cs = ''
at = ''
ats = ''
client = tweepy.Client(consumer_key=ck, consumer_secret=cs, access_token=at, access_token_secret=ats)

# 今日の日付を取得(例：2022-09-04)
tdy = datetime.date.today()

# 現在時刻(例：2022-09-04 13:18:50.472626)
dt_now = datetime.datetime.now()
# 日付の型を取得をする場合は print(type(dt_now)) を実行

# CSVの日付のフォーマットを指定（datetimeで比較するため）
dateFormatter = "%Y-%m-%d %H:%M"

# AWS EC2上のcrontabだとフルパスを指定しないと動かないため。テスト用は"data_test.csv"
csvFile = os.path.dirname(__file__) + "/data_live.csv"

# read_csvでCSVの一行目をヘッダー情報（変数headerに格納）、残りを二次元配列として処理。
arr = pd.read_csv(csvFile) 
header = arr.columns.values
valueArray = arr.values

# ツイート対象件数の初期化
matchCount = 0

# ループ回数の初期化
loop = 0

for line in valueArray:
    # dt_nowと番組配信日時を比較するため、strptimeとdateFormatterを利用。
    progDateTime = datetime.datetime.strptime(line[0]+" "+line[2], dateFormatter) 
    # 配信開始時刻を過ぎていて、
    # ツイート回数（column5）= 0、
    # 削除フラグ（column7） = 0 のレコードを取得    
    if  dt_now >= progDateTime and line[5] == 0 and line[7] == 0:
        matchCount += 1 # ツイート対象件数の加算
        tweetTxt = "「" + line[3] + "」" + "の最新エピソードが公開されました。アニメを見るなら「dアニメストア」https://animestore.docomo.ne.jp/animestore/" + " 番組URLはこちら→" + line[4]
        # print(tweetTxt) # 変数の中身を確認したいときはこの行を生かす。 
        client.create_tweet(text=tweetTxt) # Twitter APIツイート
        valueArray[loop][5] += 1 #ツイート回数を加算
    loop += 1 # for文1ループごとに加算

# ツイート対象がない場合は「ツイート対象がありません」と表示してツイートせずに終了。
if matchCount == 0 :
    print("ツイート対象がありません。")

# NumPy配列ndarrayをリストに変換: tolist()
csvIndex = header.tolist()
csvBody =  valueArray.tolist()
# 先頭にインデックス行を追加
csvBody.insert(0, csvIndex)

# CSVファイルを上書き
with open(csvFile, 'w') as file:
    writer = csv.writer(file, lineterminator='\n')
    writer.writerows(csvBody)
