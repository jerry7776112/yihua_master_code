import pandas as pd
import swifter
import re
import numpy as np
import json
from sentence_transformers import SentenceTransformer, util

def clean_body(text):
    # lower-case all characters
    text=text.lower()
            
    # remove twitter handles
    text= re.sub(r'@\S+', '',text) 
            
    # remove urls
    text= re.sub(r'http\S+', '',text) 
    text= re.sub(r'pic.\S+', '',text)
            
    text= re.sub(r'[^\w\s]+', '  ',text)
    text= re.sub(r'br', '  ',text)

    text=re.sub(r'\s+[a-zA-Z]\s+', ' ', text+' ') 

    text= re.sub("\s[\s]+", " ",text).strip()  
            
    return text

def semanticSimilarity(df_list):
    # Semantic analysis
    model = SentenceTransformer('all-MiniLM-L6-v2')
    sentences = df_list
    paraphrases = util.paraphrase_mining(model, sentences, show_progress_bar=True)

    pairs = []
    for paraphrase in paraphrases:
        score, i, j = paraphrase
        pairs.append([sentences[i], sentences[j], "{:.3f}".format(score)])
    return pairs

def mutipleSource(data):
    # data = data.dropna(subset=["related_link"])
    data['caption'] = data['related_link'].str.extract('//(www\.){0,1}(.*?)/')[1]
    data = data["caption"].value_counts().rename_axis('caption').reset_index(name='counts')
    data.replace(to_replace=r'^\s*$',value=np.nan,regex=True,inplace=True)
    data = data.dropna(subset=["caption"])
    data = data.dropna(subset=["counts"])
        
    data = data[~data['caption'].isin(['facebook.com', 'l.facebook.com', 'youtube.com', 'youtu.be'])]
    data.reset_index(inplace=True, drop=True)
    data = data["caption"]
        
        
    data = data.to_dict()
    print("MutiplePursueTest",data)

    return data


def mutipleSourceFB(data):
    # data = data.dropna(subset=["related_link"])
    # data['caption'] = data['related_link'].str.extract('//(www\.){0,1}(.*?)/')[1]
    data = data["caption"].value_counts().rename_axis('caption').reset_index(name='counts')
    data.replace(to_replace=r'^\s*$',value=np.nan,regex=True,inplace=True)
    data = data.dropna(subset=["caption"])
    data = data.dropna(subset=["counts"])
        
    data = data[~data['caption'].isin(['facebook.com', 'l.facebook.com', 'youtube.com', 'youtu.be'])]
    data.reset_index(inplace=True, drop=True)
    data = data["caption"]
        
        
    data = data.to_dict()
    print("MutiplePursueTest",data)

    return data