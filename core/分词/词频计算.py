# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 15:45:14 2020

@author: libo6001
"""
import pandas as pd
import jieba
import numpy as np


def cal_freq(df):
    '''
    功能：
        计算分词后词频，使用零售词库
    输入：
        pandas dataframe
        需要有'store_name'列
    输出：
        pandas dataframe
        {verb:分词;
        freq:词频}
    '''
    list_name = df['store_name'].dropna().to_list()
    t = [jieba.lcut(i) for i in list_name]
    tt = [i for j in t for i in j] 
    verb_freq = pd.Series(tt).value_counts().reset_index().replace('', np.nan).replace(' ', np.nan).dropna(axis=0)
    verb_freq.columns=['verb', 'freq']  
    return verb_freq
