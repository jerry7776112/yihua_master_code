import psycopg2
import pandas.io.sql as sqlio

#connect to the db
con = psycopg2.connect(
    host = "localhost",
    database = "你的資料庫名稱",
    user = "帳號",
    password = "密碼"
)

# cursor
cur = con.cursor()

def searchKeyword(start_date, end_date, search):
    cur.execute(
        f"""
        SELECT * FROM public.fb1112
        WHERE post_time BETWEEN '{start_date}'AND '{end_date}'
        AND (title &@ '{search}'
        OR body &@ '{search}'
        OR description &@ '{search}')
        """)
    result = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    totalData = []
    for row in result:
        r = dict(zip(columns, row))
        totalData.append(r)
    return totalData



def searchLink(start_date, end_date, initialPursue):
    try:
        data = sqlio.read_sql_query(
            f"""
            SELECT * FROM public.fb1112
            WHERE post_time BETWEEN '{start_date}' AND '{end_date}' 
            AND (caption &@ '{initialPursue}' 
            OR url &@ '{initialPursue}'
            OR related_link &@ '{initialPursue}'
            OR attachment_url &@ '{initialPursue}')
            """, con)
        return data
    except:
        pass

def searchLink2(start_date, end_date, link):
    try:
        data = sqlio.read_sql_query(
            f"""
            SELECT * FROM public.fb1112
            WHERE post_time BETWEEN '{start_date}'AND '{end_date}'
            AND (caption &@ '{link}' 
            OR url &@ '{link}'
            OR related_link &@ '{link}'
            OR attachment_url &@ '{link}')
            """, con)
        return data
    except:
        pass 

def api_call_page(start_date, end_date, id):
    try:
        data = sqlio.read_sql_query(
            f"""
            SET ENABLE_SEQSCAN TO OFF;
            SELECT * FROM public.fb1112
            WHERE post_time BETWEEN '{start_date}'AND '{end_date}' 
            AND (page_name &@ '{id}'
            OR from_name &@ '{id}')
            """, con)
        return data
    except:
        pass


