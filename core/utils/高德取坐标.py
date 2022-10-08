# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 16:45:53 2019
@author: libo6001

概要：
    将不标准，或过期的城市信息变更为最新的地市级行政区划。利用高德公开API完成此目的。
    核心内容，使用requests.get(https, parameters)获得返回内容；
    之后使用.json()将返回内容json化
    之后抽取所需内容即可
    
高德API开发者账号：
    KEY:8e2fa3e1ce7e4********

输入:
    df:含head的CSV文件
    id:ID列
    col_name:不标准的城市信息
    
输出：
    df_out:包含标准化后的城市信息的dataframe
"""

key = '8e2fa3e1ce7e4***********'  # 已隐藏

import requests
import pandas as pd
import time
#import time
#import sys
#reload(sys)
#sys.setdefaultencoding("utf-8")
 
def parse():
    '''
    读取数据，还未做调整
    '''
    datas = []
    totalListData = pd.read_csv('locs.csv')
    totalListDict = totalListData.to_dict('index')
    for i in range(0, len(totalListDict)):
        datas.append(str(totalListDict[i]['centroidx']) + ',' + str(totalListDict[i]['centroidy']))
    return datas
		
def transform(location):
    '''
    坐标转换，示例为将GPS坐标转高德坐标（国标）
    '''
    parameters = {'coordsys':'gps','locations': location, 'key': key}
    base = 'http://restapi.amap.com/v3/assistant/coordinate/convert'
    response = requests.get(base, parameters)
    answer = response.json()
    return answer['locations']
 
    
def getlocation(address, cityname=None):
    '''
    核心功能，获取坐标
    '''
    if cityname:
        parameters = {'city':cityname, 'key': key, 'address':address}
    else:
        parameters = {'key': key, 'address':address}
    base = 'https://restapi.amap.com/v3/geocode/geo?parameters'
    response = requests.get(base, parameters)
    answer = response.json()
    return answer['geocodes'][0]

def geocode(location):
    '''
    地理编码/逆编码
    '''
    parameters = {'location': location, 'key': '7ec25a9c6716bb26f0d25e9fdfa012b8'}
    base = 'http://restapi.amap.com/v3/geocode/regeo'
    response = requests.get(base, parameters)
    answer = response.json()
    return answer['regeocode']['addressComponent']['district'].encode('gbk','replace'),answer['regeocode']['formatted_address'].encode('gbk','replace')

def getcityname(df_city, citycode):
    t = (df_city
         .loc[df_city['citycode']==citycode, 'cityname']
         .values[0])
    return t

def getlocation_df(file_in, file_out, cityuse=False):
    '''
    功能：
        一键取坐标
    输入：
        file_in：输入文件路径，需要excel文件
        文件需要以下列：store_id, city, address
    输出：
        file_out: 输出文件路径，需要指定到文件名
    '''

    df_raw = pd.read_excel(file_in)

    time1 = time.time()
    dd = -1
    for i in range(df_raw.shape[0]):
        dd += 1
        tries = 3
        while (tries > 0):
            try:
                if cityuse:
                    t = getlocation(df_raw.loc[i, 'address'], df_raw[i, 'city'])['location']
                    p = getlocation(df_raw.loc[i, 'address'], df_raw[i, 'city'])['level']
                    q = getlocation(df_raw.loc[i, 'address'], df_raw[i, 'city'])['city']
                else:
                    t = getlocation(df_raw.loc[i, 'address'])['location']
                    p = getlocation(df_raw.loc[i, 'address'])['level']
                    q = getlocation(df_raw.loc[i, 'address'])['city']
                df_raw.loc[i, 'location'] = t
                df_raw.loc[i, 'level'] = p
                df_raw.loc[i, 'city_api'] = q
                break
            except:
                tries -= 1
        print('finish round %s / %s'%(dd, df_raw.shape[0]))
    time2 = time.time()
    print('each store cost about ' + str((time2-time1)/dd) + ' seconds')
    df_raw.to_excel(file_out, index=None)
    return df_raw
#%%
if __name__=='__main__':
#	i = 0
#	count = 0
#	df = pd.DataFrame(columns=['location','detail'])
#	#locations = parse(item)
#	locations = parse()
#	for location in locations:
#		dist, detail = geocode(transform(location))
#		df.loc[i] = [dist, detail]
#		i = i + 1
#	df.to_csv('locdetail.csv', index =False)
    df_raw = pd.read_csv('data/getlocation.csv', encoding='ANSI')
    time1 = time.time()
    dd = -1
    for i in range(len(df_raw['city'])):
        dd += 1
        try:
            t = getlocation(df_raw.loc[i, 'city'], df_raw.loc[i, 'address'])['location']
            p = getlocation(df_raw.loc[i, 'city'], df_raw.loc[i, 'address'])['level']
            df_raw.loc[i, 'location'] = t
            df_raw.loc[i, 'level'] = p
        except:
            pass
    time2 = time.time()
    print('each store cost about ' + str((time2-time1)/dd) + ' seconds')
    df_raw.to_csv('data/location_result.csv', encoding='ANSI')