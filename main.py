import psycopg2
import warnings
from flask import *
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import swifter
import re
import numpy as np
from datetime import *
import json
import Package.searchSQL
import Package.searchFbSQL
import Package.dataProcess



app=Flask(
    __name__,
    static_folder="public",
    static_url_path="/"
)
app.secret_key="any string but secret"

@app.errorhandler(500)
def handle_500_error(_error):
    return make_response(jsonify({"code": "500", "msg": "Oops! Can not find any data "}),500)


#connect to the db
con = psycopg2.connect(
    host = "localhost",
    database = "你的資料庫名稱",
    user = "帳號",
    password = "密碼"
)

# cursor
cur = con.cursor()
warnings.filterwarnings("ignore")
#====================================================================================================
@app.route('/api/facebook/v1/pursuesource')
def searchkeyword():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    search = request.args.get("search")
    similarityscore = request.args.get("similarityscore")
    page_name = request.args.get("page_name")
    link = request.args.get("link")

#====================================================================================================
# keyword
    if None not in (start_date, end_date, search, similarityscore):
        totalData = Package.searchSQL.searchKeyword(start_date, end_date, search)
# 資料處理========================================================================================================================

        df = pd.DataFrame(totalData)
        df['caption'] = df['related_link'].str.extract('//(www\.){0,1}(.*?)/')[1]
        # df = df[['source', 'page_name', 'body','caption', 'post_time']]

        # 先按時間排序以利後續進入adaptively
        df = df.sort_values(by=['post_time'])
        df.reset_index(inplace=True, drop=True)
        # initialPursue = df["caption"][0]
        df["post_time"] = df["post_time"].apply(str)
        

        # 資料初步清洗
        df1 = df.dropna(subset=["page_name"])
        df1 = df.dropna(subset=["body"])

        df1 = df1[["page_name", "body", "post_time"]]

        df2 = df1['page_name'].value_counts().rename_axis('page_name').reset_index(name='counts')
        df2 = df2.assign(id = range(1, len(df2)+1))
        df2["id"] = df2["id"].swifter.apply(str)
        id_to_page_name = df2.set_index("page_name")["id"].to_dict()

        source_to_page_name = df.set_index("page_name")["source"].to_dict()
        url_to_page_name = df.set_index("page_name")["url"].to_dict()
        caption_to_url = df.set_index("url")["caption"].to_dict()
        relatedLink_to_url = df.set_index("url")["related_link"].to_dict()

        # 資料清洗
        df1.reset_index(inplace=True, drop=True)
        df1['body']=df1['body'].swifter.apply(lambda x: Package.dataProcess.clean_body(x))
# 相似度分析========================================================================================================================

        # 轉換為list
        df_list = df1.values.tolist()
        # Semantic analysis
        pairs = Package.dataProcess.semanticSimilarity(df_list)

# 資料處理========================================================================================================================

        result = pd.DataFrame(pairs, columns = ["sentence1", "sentence2", "similarity"])

        result['similarity'] = result['similarity'].astype(float, errors = 'raise')

        cols = ["page_name1", "sentence1", "post_time1"]
        a = pd.DataFrame(result["sentence1"].tolist(), columns=cols)
        a["id1"] = a.page_name1.swifter.apply(lambda x: id_to_page_name[x])

        cols = ["page_name2", "sentence2", "post_time2"]
        b = pd.DataFrame(result["sentence2"].tolist(), columns=cols)
        b["id2"] = b.page_name2.swifter.apply(lambda x: id_to_page_name[x])

        c = pd.concat([a, b, result["similarity"]], axis = 1)

        # 只保留相似度??%(可自行設定)以上的資料
        similarity = float(similarityscore)
        d = c.query("similarity >= @similarity")

# 資料處理========================================================================================================================
        # 資料按時間排序
        d['post_time1'] = pd.to_datetime(d['post_time1'])
        d['post_time2'] = pd.to_datetime(d['post_time2'])
        d = d.sort_values(by=['post_time1'])
        d.reset_index(inplace=True, drop=True)

        e = d[["id1", "page_name1", "sentence1", "post_time1", "id2", "page_name2", "sentence2", "post_time2"]]
        e1 = e[["page_name1", "sentence1", "post_time1"]]
        e1.rename(columns = {'page_name1':'page_name', "sentence1":"body", 'post_time1':'post_time'}, inplace = True)
        e1_2 = e[["page_name2", "sentence2", "post_time2"]]
        e1_2.rename(columns = {'page_name2':'page_name', "sentence2":"body", 'post_time2':'post_time'}, inplace = True)

        e1_3 = pd.concat([e1, e1_2], axis=0).drop_duplicates().reset_index(drop=True)
        e1_3 = e1_3.sort_values(by=['post_time'])
        e1_3.reset_index(inplace=True, drop=True)

        e1_3["source"] = e1_3.page_name.swifter.apply(lambda x: source_to_page_name[x])
        e1_3["url"] = e1_3.page_name.swifter.apply(lambda x: url_to_page_name[x])
        e1_3["caption"] = e1_3.url.swifter.apply(lambda x: caption_to_url[x])
        e1_3["related_link"] = e1_3.url.swifter.apply(lambda x: relatedLink_to_url[x])
        e1_3 = e1_3.replace(np.nan, None)
# 初始可疑訊息網址結果========================================================================================================================
        
        initialPursue = e1_3["caption"][0]
        e1_4 = e1_3["page_name"].value_counts().rename_axis('page_name').reset_index(name='counts')
        
        if initialPursue is None:
                page = e1_4["page_name"].to_dict()
                print("測試結果:",initialPursue)
                print("Number of pages:",len(e1_4))
                totalDataList = []
                count = 0
                for id in e1_4["page_name"].values:
                        count += 1
                        totalDataList.append(Package.searchSQL.api_call_page(start_date, end_date, id))
                        print("編號:"+str(count),id)
                data = pd.concat(totalDataList)
        # 產生多個網址========================================================================================================================
                data = Package.dataProcess.mutipleSource(data)
                result = Response(json.dumps({"code": "200", "msg": "MutiplePursue Success!!","date":f"{start_date}""~"f"{end_date}", "keyword":f"{search}", "initialPursue source":f"{initialPursue}", "page":f"{page}", "MutiplePursue source": f"{data}"}), mimetype='application/json')
                return result
        
        else:
                print("測試結果:",initialPursue)

                print("===============================================================================")
                print("initialPursue Success!!")
                print("===============================================================================")

# 將初始可疑訊息網址進行搜尋，抓出包含該網址之資料========================================================================================================================

                searchlinkdata1 = Package.searchSQL.searchLink(start_date, end_date, initialPursue)

# 產生包含初始可疑訊息網址之資料========================================================================================================================

                totalData1 = searchlinkdata1

                totalpage1 = totalData1["page_name"].value_counts().rename_axis('page_name').reset_index(name='counts')
                page = totalpage1["page_name"].to_dict()
                print("Number of pages:",len(totalpage1))
# 迭代該資料之Page_name========================================================================================================================

                print("===============================================================================")
                print("第一次迭代Page_name!!")
                print("===============================================================================")

# 資料處理========================================================================================================================

                totalDataList = []
                count = 0
                for id in totalpage1["page_name"].values:
                        count += 1
                        totalDataList.append(Package.searchSQL.api_call_page(start_date, end_date, id))
                        print("編號:"+str(count),id)
                
                data = pd.concat(totalDataList)
        # 產生多個網址========================================================================================================================
                data = Package.dataProcess.mutipleSource(data)
                result = Response(json.dumps({"code": "200", "msg": "MutiplePursue Success!!", "date":f"{start_date}""~"f"{end_date}", "keyword":f"{search}", "initialPursue source":f"{initialPursue}", "page":f"{page}", "MutiplePursue source": f"{data}"}), mimetype='application/json')
                return result

#====================================================================================================
    if None not in (start_date, end_date, page_name):
        data = Package.searchSQL.searchPage(start_date, end_date, page_name)
# 產生多個網址========================================================================================================================
        data = Package.dataProcess.mutipleSource(data)
        result = Response(json.dumps({"code": "200", "msg": "MutiplePursue Success!!", "date":f"{start_date}""~"f"{end_date}", "page":f"{page_name}", "MutiplePursue source": f"{data}"}), mimetype='application/json')
        return result
#====================================================================================================
    if None not in (start_date, end_date, link):
        searchlinkdata1 = Package.searchSQL.searchLink2(start_date, end_date, link)
        totalData1 = searchlinkdata1
        totalpage1 = totalData1["page_name"].value_counts().rename_axis('page_name').reset_index(name='counts')
        print("Number of pages:",len(totalpage1))
        page = totalpage1["page_name"].to_dict()
# 迭代該資料之Page_name========================================================================================================================

        print("===============================================================================")
        print("第一次迭代Page_name!!")
        print("===============================================================================")

# 資料處理========================================================================================================================

        totalDataList = []
        count = 0
        for id in totalpage1["page_name"].values:
            count += 1
            totalDataList.append(Package.searchSQL.api_call_page(start_date, end_date, id))
            print("編號:"+str(count),id)

        data = pd.concat(totalDataList)
# 產生多個網址========================================================================================================================
        data = Package.dataProcess.mutipleSource(data)
        result = Response(json.dumps({"code": "200", "msg": "MutiplePursue Success!!", "date":f"{start_date}""~"f"{end_date}", "initialPursue source":f"{link}", "page":f"{page}", "MutiplePursue source": f"{data}"}), mimetype='application/json')
        return result
# # only iterate page==================================================================================================================
#     elif (start_date, end_date, search) is not None:
#         totalData = Package.searchSQL.searchKeyword(start_date, end_date, search)
#         df = pd.DataFrame(totalData)
#         e1_4 = df["page_name"].value_counts().rename_axis('page_name').reset_index(name='counts')        
#         page = e1_4["page_name"].to_dict()
#         print("Number of pages:",len(e1_4))
#         totalDataList = []
#         count = 0
#         for id in e1_4["page_name"].values:
#                 count += 1
#                 totalDataList.append(Package.searchSQL.api_call_page(start_date, end_date, id))
#                 print("編號:"+str(count),id)
#         data = pd.concat(totalDataList)
# # 產生多個網址========================================================================================================================
#         data = Package.dataProcess.mutipleSourceFB(data)
#         result = Response(json.dumps({"code": "200", "msg": "MutiplePursue Success!!", "date":f"{start_date}""~"f"{end_date}", "keyword":f"{search}", "initialPursue source":"None(Only iterate pages)", "page":f"{page}", "MutiplePursue source": f"{data}"}), mimetype='application/json')
#         return result
#====================================================================================================    
#     return result
#API FB====================================================================================================
@app.route('/3000/cdal/api/facebook/v1/pursuesource')
def searchkeywordFB():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    search = request.args.get("search")
    similarityscore = request.args.get("similarityscore")
    page_name = request.args.get("page_name")
    link = request.args.get("link")

#====================================================================================================
# keyword
    if None not in (start_date, end_date, search, similarityscore):
        totalData = Package.searchFbSQL.searchKeyword(start_date, end_date, search)
# 資料處理========================================================================================================================

        df = pd.DataFrame(totalData)
        # 先按時間排序以利後續進入adaptively
        df = df.sort_values(by=['post_time'])
        df.reset_index(inplace=True, drop=True)
        df["post_time"] = df["post_time"].apply(str)
        
        # 資料初步清洗
        df1 = df.dropna(subset=["page_name"])
        df1 = df.dropna(subset=["body"])
        df1 = df1[["page_name", "body", "post_time"]]
        df2 = df1['page_name'].value_counts().rename_axis('page_name').reset_index(name='counts')
        df2 = df2.assign(id = range(1, len(df2)+1))
        df2["id"] = df2["id"].swifter.apply(str)
        id_to_page_name = df2.set_index("page_name")["id"].to_dict()
        source_to_page_name = df.set_index("page_name")["source"].to_dict()
        url_to_page_name = df.set_index("page_name")["url"].to_dict()
        caption_to_url = df.set_index("url")["caption"].to_dict()
        relatedLink_to_url = df.set_index("url")["related_link"].to_dict()

        # 資料清洗
        df1.reset_index(inplace=True, drop=True)
        df1['body']=df1['body'].swifter.apply(lambda x: Package.dataProcess.clean_body(x))
# 相似度分析========================================================================================================================

        # 轉換為list
        df_list = df1.values.tolist()
        # Semantic analysis
        pairs = Package.dataProcess.semanticSimilarity(df_list)

# 資料處理========================================================================================================================

        result = pd.DataFrame(pairs, columns = ["sentence1", "sentence2", "similarity"])
        result['similarity'] = result['similarity'].astype(float, errors = 'raise')
        cols = ["page_name1", "sentence1", "post_time1"]
        a = pd.DataFrame(result["sentence1"].tolist(), columns=cols)
        a["id1"] = a.page_name1.swifter.apply(lambda x: id_to_page_name[x])
        cols = ["page_name2", "sentence2", "post_time2"]
        b = pd.DataFrame(result["sentence2"].tolist(), columns=cols)
        b["id2"] = b.page_name2.swifter.apply(lambda x: id_to_page_name[x])
        c = pd.concat([a, b, result["similarity"]], axis = 1)

        # 只保留相似度??%(可自行設定)以上的資料
        similarity = float(similarityscore)
        d = c.query("similarity >= @similarity")

# 資料處理========================================================================================================================
        # 資料按時間排序
        d['post_time1'] = pd.to_datetime(d['post_time1'])
        d['post_time2'] = pd.to_datetime(d['post_time2'])
        d = d.sort_values(by=['post_time1'])
        d.reset_index(inplace=True, drop=True)

        e = d[["id1", "page_name1", "sentence1", "post_time1", "id2", "page_name2", "sentence2", "post_time2"]]
        e1 = e[["page_name1", "sentence1", "post_time1"]]
        e1.rename(columns = {'page_name1':'page_name', "sentence1":"body", 'post_time1':'post_time'}, inplace = True)
        e1_2 = e[["page_name2", "sentence2", "post_time2"]]
        e1_2.rename(columns = {'page_name2':'page_name', "sentence2":"body", 'post_time2':'post_time'}, inplace = True)

        e1_3 = pd.concat([e1, e1_2], axis=0).drop_duplicates().reset_index(drop=True)
        e1_3 = e1_3.sort_values(by=['post_time'])
        e1_3.reset_index(inplace=True, drop=True)

        e1_3["source"] = e1_3.page_name.swifter.apply(lambda x: source_to_page_name[x])
        e1_3["url"] = e1_3.page_name.swifter.apply(lambda x: url_to_page_name[x])
        e1_3["caption"] = e1_3.url.swifter.apply(lambda x: caption_to_url[x])
        e1_3["related_link"] = e1_3.url.swifter.apply(lambda x: relatedLink_to_url[x])
        e1_3 = e1_3.replace(np.nan, None)
        e1_3 = e1_3.replace("", None)
# 初始可疑訊息網址結果========================================================================================================================
        
        initialPursue = e1_3["caption"][0]
        # print("測試結果:",initialPursue)
        e1_4 = e1_3["page_name"].value_counts().rename_axis('page_name').reset_index(name='counts')
        
        if initialPursue is None:
                
                page = e1_4["page_name"].to_dict()
                print("測試結果:",initialPursue)
                print("Number of pages:",len(e1_4))
                totalDataList = []
                count = 0
                for id in e1_4["page_name"].values:
                        count += 1
                        totalDataList.append(Package.searchFbSQL.api_call_page(start_date, end_date, id))
                        print("編號:"+str(count),id)

                # data = pd.DataFrame(totalDataList)
                data = pd.concat(totalDataList)
        # 產生多個網址========================================================================================================================
                data = Package.dataProcess.mutipleSourceFB(data)
                result = Response(json.dumps({"code": "200", "msg": "MutiplePursue Success!!", "date":f"{start_date}""~"f"{end_date}", "keyword":f"{search}", "initialPursue source":f"{initialPursue}", "page":f"{page}", "MutiplePursue source": f"{data}"}), mimetype='application/json')
                # result = Response(json.dumps({"code": "3000", "msg": "MutiplePursue Success!!", "keyword":f"{search}", "initialPursue source":f"{initialPursue}", "MutiplePursue source": f"{data}"}), mimetype='application/json')
                return result
        
        else:
                print("測試結果:",initialPursue)

                print("===============================================================================")
                print("initialPursue Success!!")
                print("===============================================================================")

# 將初始可疑訊息網址進行搜尋，抓出包含該網址之資料========================================================================================================================

                searchlinkdata1 = Package.searchFbSQL.searchLink(start_date, end_date, initialPursue)

# 產生包含初始可疑訊息網址之資料========================================================================================================================

                totalData1 = pd.DataFrame(searchlinkdata1)

                totalpage1 = totalData1["page_name"].value_counts().rename_axis('page_name').reset_index(name='counts')
                # totalpage1 = totalpage1[~totalpage1['caption'].isin(['facebook.com', 'l.facebook.com', 'youtube.com', 'youtu.be'])]
                page = totalpage1["page_name"].to_dict()
                print("Number of pages:",len(totalpage1))
# 迭代該資料之Page_name========================================================================================================================

                print("===============================================================================")
                print("第一次迭代Page_name!!")
                print("===============================================================================")
# 資料處理========================================================================================================================

                totalDataList = []
                count = 0
                for id in totalpage1["page_name"].values:
                        count += 1
                        totalDataList.append(Package.searchFbSQL.api_call_page(start_date, end_date, id))
                        print("編號:"+str(count),id)
                
                data = pd.concat(totalDataList)
        # 產生多個網址========================================================================================================================
                data = Package.dataProcess.mutipleSourceFB(data)

                result = Response(json.dumps({"code": "200", "msg": "MutiplePursue Success!!", "date":f"{start_date}""~"f"{end_date}", "keyword":f"{search}", "initialPursue source":f"{initialPursue}", "page":f"{page}", "MutiplePursue source": f"{data}"}), mimetype='application/json')
                return result

#====================================================================================================
    if None not in (start_date, end_date, page_name):
        data = Package.searchFbSQL.api_call_page(start_date, end_date, page_name)
        # data = pd.DataFrame(data)
# 產生多個網址========================================================================================================================
        data = Package.dataProcess.mutipleSourceFB(data)
        result = Response(json.dumps({"code": "200", "msg": "MutiplePursue Success!!", "date":f"{start_date}""~"f"{end_date}", "page":f"{page_name}", "MutiplePursue source": f"{data}"}), mimetype='application/json')
        return result
#====================================================================================================
    if None not in (start_date, end_date, link):
        searchlinkdata1 = Package.searchFbSQL.searchLink2(start_date, end_date, link)
        totalData1 = searchlinkdata1

        totalpage1 = totalData1["page_name"].value_counts().rename_axis('page_name').reset_index(name='counts')
        page = totalpage1["page_name"].to_dict()
        print("Number of pages:",len(totalpage1))
# 迭代該資料之Page_name========================================================================================================================

        print("===============================================================================")
        print("第一次迭代Page_name!!")
        print("===============================================================================")

# 資料處理========================================================================================================================

        totalDataList = []
        count = 0
        for id in totalpage1["page_name"].values:
            count += 1
            totalDataList.append(Package.searchFbSQL.api_call_page(start_date, end_date, id))
            print("編號:"+str(count),id)

        # data = pd.DataFrame(totalDataList)
        data = pd.concat(totalDataList)
# 產生多個網址========================================================================================================================
        data = Package.dataProcess.mutipleSourceFB(data)
        result = Response(json.dumps({"code": "200", "msg": "MutiplePursue Success!!", "date":f"{start_date}""~"f"{end_date}","initialPursue source":f"{link}", "page":f"{page}","MutiplePursue source": f"{data}"}), mimetype='application/json')
        return result
# # Only Iterate Pages=================================================================================================================
#     elif (start_date, end_date, search) is not None:
#         totalData = Package.searchFbSQL.searchKeyword(start_date, end_date, search)
#         df = pd.DataFrame(totalData)
#         e1_4 = df["page_name"].value_counts().rename_axis('page_name').reset_index(name='counts')        
#         page = e1_4["page_name"].to_dict()
#         print("Number of pages:",len(e1_4))
#         totalDataList = []
#         count = 0
#         for id in e1_4["page_name"].values:
#                 count += 1
#                 totalDataList.append(Package.searchFbSQL.api_call_page(start_date, end_date, id))
#                 print("編號:"+str(count),id)

#         # data = pd.DataFrame(totalDataList)
#         data = pd.concat(totalDataList)
# # 產生多個網址========================================================================================================================
#         data = Package.dataProcess.mutipleSourceFB(data)
#         result = Response(json.dumps({"code": "200", "msg": "MutiplePursue Success!!", "date":f"{start_date}""~"f"{end_date}", "keyword":f"{search}", "initialPursue source":"None(Only iterate pages)", "page":f"{page}", "MutiplePursue source": f"{data}"}), mimetype='application/json')
#         return result
#====================================================================================================
# 啟動伺服器
# app.config['JSON_AS_ASCII'] = False
app.run(port=3000)