# yihua_master_code
### 安裝相關套件
* ```pip install -r requirements. txt```

### 匯入大量資料集至PostgreSQL:
* 請參考[PostgreSQLImportdataExample](https://github.com/jerry7776112/yihua_master_code/tree/main/PostgreSQLImportdataExample "link")

### 修改欲使用之資料庫相關資訊:
* main.py: 
    ```
    con = psycopg2.connect(
        host = "localhost", 
        database = "你的資料庫名稱", 
        user = "帳號", 
        password = "密碼"
    )
    ```
* searchSQL.py: 
    ```
    con = psycopg2.connect(
        host = "localhost", 
        database = "你的資料庫名稱", 
        user = "帳號", 
        password = "密碼"
    )
    ```
* searchFbSQL.py: 
    ```
    con = psycopg2.connect(
        host = "localhost", 
        database = "你的資料庫名稱", 
        user = "帳號", 
        password = "密碼"
    )
    ```
### 啟動API:
* ``` python main.py ```

### API Parameters
* start_date: **輸入起始日期**  EX: 2021-11-01
* end_date: **輸入結束日期** EX: 2021-12-31
* search: **輸入關鍵字** EX: 萊豬
* similarityscore: **想要取多少相似度以上的資料，輸入零或小數點** EX: 0 or 0.8
* page_name: **輸入粉絲專頁名稱**

### API Example:
**Search Ketword**
*  http://127.0.0.1:3000/api/facebook/v1/pursuesource?start_date=2021-11-01&end_date=2021-12-01&search=台灣島正式更名中國台灣省&similarityscore=0

| Parameters | Type| API |
|:-------:|:-----:|:------:|
| start_date, end_date, Disinformation,Score   |  GET  |/api/facebook/v1/pursuesource?{start_date}&{end_date}&{search}&{Score} |

**EXAMPLE RESPONSE:**
```
STATUS CODE - 200: Successful responses
RESPONSE MODEL - application/json
{
 "code": "200",
 "msg": "MutiplePursue Success!!",
 "date": "2021-11-01~2021-12-01",
 "keyword": "台灣正式回歸",
 "initialPursue source": "qiqu.world",
 "page": "{0: '全球時事追蹤', 1: '风味美食网', 2: '我看到 , 就分享', 3: '八卦-靠北-娛樂'},
"MutiplePursue source": "{0: 'qiqu.world', 1: 'mybezza.live', 2: 'nanyang.news', 3: 'qiqi.world'}
}
STATUS CODE - 500: Unexpected error or exception occurred
```
**Search Page**
*  http://127.0.0.1:3000/api/facebook/v1/pursuesource?start_date=2021-11-01&end_date=2021-12-01&page_name=我看到 , 就分享

| Parameters | Type| API |
|:-------:|:-----:|:------:|
| start_date, end_date, page_name   |  GET  |/api/facebook/v1/pursuesource?{start_date}&{end_date}&{page_name} |

**EXAMPLE RESPONSE:**
```
STATUS CODE - 200: Successful responses
RESPONSE MODEL - application/json
{
 "code": "200",
 "msg": "MutiplePursue Success!!",
 "date": "2021-11-01~2021-12-01",
 "page": "我看到 , 就分享",
 "MutiplePursue source": "{0: 'qiqu.world', 1: 'kanwatch.co'}"
}
STATUS CODE - 500: Unexpected error or exception occurred
```
**Search URL**
*  http://127.0.0.1:3000/api/facebook/v1/pursuesource?start_date=2021-11-01&end_date=2021-12-01&link=qiqu.world

| Parameters | Type| API |
|:-------:|:-----:|:------:|
| start_date, end_date, link   |  GET  |/api/facebook/v1/pursuesource?{start_date}&{end_date}&{link} |

**EXAMPLE RESPONSE:**
```
STATUS CODE - 200: Successful responses
RESPONSE MODEL - application/json
{
 "code": "200",
 "msg": "MutiplePursue Success!!",
 "date": "2021-11-01~2021-11-15",
 "initialPursue source": "qiqu.pro",
 "page": "{0: '生活点滴 818', 1: '新闻追追追', 2: '棱镜世界 Prism World', 3: '当今世界 Fantasy 
World', 4: '環球時報 Global Times', 5: '爆笑天堂'}",
 "MutiplePursue source": "{0: 'qiqu.pro', 1: 'qiqi.world', 2: 'nanyang.news', 3: 'ppoo.club'}"
}
STATUS CODE - 500: Unexpected error or exception occurred
```
