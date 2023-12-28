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
        SELECT
        source,
        post_time, 
        page_name, 
        url, 
        title, 
        body,
        related_link


        FROM public.fb1112
        WHERE post_time BETWEEN '{start_date}'AND '{end_date}'
        AND (title &@ '{search}'
        OR body &@ '{search}'
        OR description &@ '{search}')

        UNION

        SELECT
        ptt.source, 
        post_time, 
        from_board||' '||from_name AS page_name,
        url, 
        title, 
        body,
        CAST('related_links' AS TEXT)
        -- ptt.related_links
        FROM public.ptt
        WHERE post_time BETWEEN '{start_date}'AND '{end_date}'
        AND (title &@ '{search}'
        OR body &@ '{search}')
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
            SELECT
            source,
            post_time, 
            page_name, 
            url, 
            title, 
            body,
            related_link

            FROM public.fb1112
            WHERE post_time BETWEEN '{start_date}'AND '{end_date}' 
            AND (caption &@ '{initialPursue}' 
            OR url &@ '{initialPursue}'
            OR related_link &@ '{initialPursue}'
            OR attachment_url &@ '{initialPursue}')

            UNION

            SELECT

            ptt.source, 
            post_time, 
            from_board||' '||from_name AS page_name,
            url, 
            title, 
            body,
            CAST('related_links' AS TEXT)
            FROM public.ptt
            WHERE post_time BETWEEN '{start_date}'AND '{end_date}' 
            AND (url &@ '{initialPursue}'
            OR CAST('related_links' AS TEXT) &@ '{initialPursue}')
            """, con)
        return data
    except:
        pass
    

def searchLink2(start_date, end_date, link):
    try:
        data = sqlio.read_sql_query(
            f"""
            SELECT
            source,
            post_time, 
            page_name, 
            url, 
            title, 
            body,
            related_link

            FROM public.fb1112
            WHERE post_time BETWEEN '{start_date}'AND '{end_date}'
            AND (caption &@ '{link}' 
            OR url &@ '{link}'
            OR related_link &@ '{link}'
            OR attachment_url &@ '{link}')

            UNION

            SELECT

            ptt.source, 
            post_time, 
            from_board||' '||from_name AS page_name,
            url, 
            title, 
            body,
            CAST('related_links' AS TEXT)
            FROM public.ptt
            WHERE post_time BETWEEN '{start_date}'AND '{end_date}'
            AND (url &@ '{link}'
            OR CAST('related_links' AS TEXT) &@ '{link}')
            """, con)
        return data
    except:
        pass
    

def api_call_page(start_date, end_date, id):
    try:
        data = sqlio.read_sql_query(
            f"""
            SELECT
            source,
            post_time, 
            page_name, 
            url, 
            title, 
            body,
            related_link
            -- CAST('related_link' AS jsonb)

            FROM public.fb1112
            WHERE post_time BETWEEN '{start_date}'AND '{end_date}' 
            AND page_name &@ '{id}'

            UNION

            SELECT

            source, 
            post_time, 
            from_board||' '||from_name AS page_name,
            url, 
            title, 
            body,
            CAST('related_links' AS TEXT)
            FROM public.ptt
            WHERE post_time BETWEEN '{start_date}'AND '{end_date}' 
            AND (from_board &@ '{id}'
            OR from_name &@ '{id}') 
            """,con)
        return data
    except:
        pass
    


def searchPage(start_date, end_date, page_name):
    try:
        data = sqlio.read_sql_query(
            f"""
            SELECT
            source,
            post_time, 
            page_name, 
            url, 
            title, 
            body,
            related_link
            -- CAST('related_link' AS jsonb)

            FROM public.fb1112
            WHERE post_time BETWEEN '{start_date}'AND '{end_date}'
            AND page_name &@ '{page_name}'

            UNION

            SELECT

            source, 
            post_time, 
            from_board||' '||from_name AS page_name,
            url, 
            title, 
            body,
            CAST('related_links' AS TEXT)
            FROM public.ptt
            WHERE post_time BETWEEN '{start_date}'AND '{end_date}'
            AND (from_board &@ '{page_name}'
            OR from_name &@ '{page_name}') 
            """, con)
        return data
    except:
        pass
    
    