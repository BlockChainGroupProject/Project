## 問題描述

1. 有2組資料A與B，我們想要得到A交集B，並同時不洩漏A和B的全部資料
2. 將A交集B所獲得的資料提交給第三方作分析時希望不用洩漏A交集B

## 實作方法

1. 用python架設socket server，讓user註冊後可以和其他user進行merge，之後藉由PSI技術取得交集

2. user可以向平台提出分析資料的請求

3. 傳輸及上傳資料的方式會就由將資料上傳至IPFS，並將CID提供給平台，vice versa

## Server Function需求

1. 註冊(done)
2. Database(done)
3. 登入(done)
4. Merge request(user交集功能)(todo)
5. CID傳遞(todo)
6. 上傳至IPFS(todo)

## Client Function需求

1. 接收訊息(done)
2. 回傳訊息(done)
3. PSI功能(todo)
4. 從IPFS上傳並下載(todo)
5. 將資料進行同態加密後傳給第三方平台(todo)

## Directory
* root/
 - test.py
 - client/
  - data/
  - enc data/
  - private key/
  - client.py
  - enc.py
  - upload ipfs.py
 - database/
  - users.db
 - server/
  - merge.py
  - server.py
  - test data
 - merge matrix.xlsx
 