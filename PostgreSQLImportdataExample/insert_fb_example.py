import gzip
import json
import os
from db_manager.db_manager import DBM

pttdb = DBM(host='localhost', port='5432', user='帳號', password='密碼', database="資料庫名稱")

# 寫入字串安全性檢查
def safe_str(s="", fix_percent=True):
    if s:
        if fix_percent:
            s = s.replace('%', '%%')
        s = s.replace("'", "''")
        return s
    else:
        return ""

def insert(file,table):
    print('--- Insert File : ' + file + ' ---')
    with gzip.open(file, 'rt', encoding="UTF-8") as f:
        lines_num = 0
        for line in f:
            lines_num += 1
            tmp_data = {}
            try:

                data = json.loads(line)
                tmp_data = data
                str_col = [
                    'title',
                    'description',
                    'body',
                    'post_id',
                    'source',
                    'data_category',
                    'page_category',
                    'post_status',
                    'post_identity',
                    'from_id',
                    'from_name',
                    'page_name',
                    'caption',
                    'url',
                    'related_link',
                    'attachment_type',
                    'attachment_url',
                    'image_md5',
                ]

                array_col = [
                    'hashtag',
                    'image_links',
                    'image_alts',
                    'post_tags',
                    'comments'
                ]

                float_col = [
                    'diff',
                    'diff_comment',
                    'diff_share',
                ]

                for col in str_col:
                    data[col] = safe_str(str(data.get(col, '')))

                for col in array_col:
                    data[col] = safe_str(json.dumps(data.get(col, '[]')))

                for col in float_col:
                    if col in data:
                        if len(data.get(col, '')) == 0:  # 如果是空字串 刪掉不插入float8 欄位
                            del data[col]

                pttdb.insert(table, data)

            except Exception as e:
                print(e + "  " + str(tmp_data))

    return lines_num


for root, dirs, files in os.walk(".\example_data"): 
        for file in files:
            if file.find(".gz") != -1:
                total = 0
                total=total+insert(os.path.join(root, file),'fb')  # 輸入資料表名稱
print("total:"+ str(total))  