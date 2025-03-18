%%writefile project1_map.py
import streamlit as st
import sys
sys.path.append('/content/drive/MyDrive/module')
import json
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import os
import pymysql
import pandas as pd
from mysql import connector
import contextily as ctx
import streamlit as st
import pymysql
import pandas as pd
import plotly.express as px

def get_shp(df):
    global sgg_car, sido_car
    sido_shp = gpd.read_file("C:/python_sw/p1/sido.shp", encoding = "utf-8")
    sgg_shp = gpd.read_file("C:/python_sw/p1/sgg.shp", encoding = "utf-8")
    
    args = {
        'host' : 'localhost',
        'user' : 'root',
        'password' : 'root1234',
        'port' : 3306,
        'database' : 'vehicle_db1'
    }
    

    data = df
    
    sido_data = data[data['district'] == '계']
    matched_rows = sido_shp[sido_shp['SIDO_NM'].str.contains('|'.join(sido_data['region']), na=False)]
    sido_car = matched_rows.merge(sido_data, left_on=matched_rows['SIDO_NM'].apply(lambda x: next((s for s in sido_shp['SIDO_NM'] if s in x), None)), right_on='region')
    
    sgg_data = data[data['district'] != '계']
    sgg_data['region'] = sgg_data['region'] + " " + sgg_data['district']
    matched_rows = sgg_shp[sgg_shp['address'].str.contains('|'.join(sgg_data['region']), na=False)]
    sgg_car = matched_rows.merge(sgg_data, left_on=matched_rows['address'].apply(lambda x: next((s for s in sgg_shp['address'] if s in x), None)), right_on='region')

    

def sido_map(year, month, type = "total_all"):
    """
    전체 시/도를 보여주는 함수임
    year: 목표 년도
    month: 목표 월
    type: 차량 종류 ex) 승합, 승용
    """
    plt.rcParams['font.family'] ='Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] =False

    option_date = "-".join([year, month])
    option_column = type

    global sido_car
    
    # merged_data를 GeoDataFrame으로 변환 (geometry 컬럼이 존재하는 경우)
    sido_car = gpd.GeoDataFrame(sido_car, geometry='geometry')
    sido_car = sido_car.set_crs("EPSG:5186", allow_override=True)
    sido_car[option_column] = pd.to_numeric(sido_car[option_column], errors='coerce')  # 변환할 수 없는 값은 NaN으로 처리
    
    sido_obj_car = sido_car
    sido_obj_car = sido_obj_car[sido_obj_car['record_month'] == option_date]
    
    dic = {
    'passenger' : '승용',
    'van' : '승합',
    'truck' : '화물',
    'special' : '특수',
    'government' : '관용',
    'private' : '자가용',
    'business' : '영업용',
    'total' : '합계',
    'all' : '전체'}
    
    index = [dic[type.split('_')[0]], dic[type.split('_')[1]]]
    
    # 단계구분도 그리기
    fig, ax = plt.subplots(figsize=(10, 10))
    sido_obj_car.set_geometry('geometry').plot(
        column=option_column,   # 기준 컬럼
        cmap='OrRd',    # 색상 맵
        legend=True,    # 범례 추가
        scheme='Quantiles',  # 단계구분 방식 ('Quantiles', 'EqualInterval', 'NaturalBreaks' 등 가능)
        k=5,            # 5단계 구분
        edgecolor='black',
        linewidth=0.5,
        alpha=0.8,      # 투명도 조절
        ax=ax,
        legend_kwds={'title': f"{index[1]} {index[0]}차 수"}
    )
        
    
    # 배경지도 추가 (contextily 사용)
    ctx.add_basemap(ax, crs=sido_obj_car.crs.to_string())
    # ctx.add_basemap(ax, crs="EPSG:5186")
    # ctx.add_basemap(ax, crs=sido_obj_car.crs.to_string(), source = ctx.providers.OpenStreetMap.Mapnik)
    
    for idx, row in sido_obj_car.iterrows():
        # 폴리곤의 중심 좌표를 계산
        centroid = row['geometry'].centroid
        # 시군구 이름을 표시 (원하는 텍스트 스타일을 추가 가능)
        ax.text(centroid.x, centroid.y, row['SIDO_NM'], fontsize=8, ha='center', color='black')
    
    # 플롯을 보여줌
    plt.title(f'{year}-{month} 전국 {index[1]} {index[0]}차 등록현황')
    st.pyplot(fig)

def sgg_map(year, month, region, type = "total_all"):
    """
    특정 시/도에 시/군/구를 보여주는 함수
    year: 목표 년도
    month: 목표 월
    type: 차량 종류 ex) 승합, 승용
    region: 특정 시ㅣ/도
    """
    plt.rcParams['font.family'] ='Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] =False
    option_date = "-".join([year, month])
    option_region = region
    option_column = type

    global sgg_car
    # merged_data를 GeoDataFrame으로 변환 (geometry 컬럼이 존재하는 경우)
    sgg_car = gpd.GeoDataFrame(sgg_car, geometry='geometry')
    sgg_car = sgg_car.set_crs("EPSG:5186", allow_override=True)
    sgg_car[option_column] = pd.to_numeric(sgg_car[option_column], errors='coerce')  # 변환할 수 없는 값은 NaN으로 처리

    sgg_obj_data = sgg_car
    sgg_obj_data = sgg_obj_data[sgg_obj_data['record_month'] == option_date]
    sgg_obj_data = sgg_obj_data[sgg_obj_data['SIDO'] == option_region]
    
    dic = {
    'passenger' : '승용',
    'van' : '승합',
    'truck' : '화물',
    'special' : '특수',
    'government' : '관용',
    'private' : '자가용',
    'business' : '영업용',
    'total' : '합계',
    'all' : '전체'}

    index = [dic[option_column.split('_')[0]], dic[option_column.split('_')[1]]]

    # 단계구분도 그리기
    fig, ax = plt.subplots(figsize=(10, 10))
    sgg_obj_data.set_geometry('geometry').plot(
        column=option_column,   # 기준 컬럼
        cmap='OrRd',    # 색상 맵
        legend=True,    # 범례 추가
        scheme='Quantiles',  # 단계구분 방식 ('Quantiles', 'EqualInterval', 'NaturalBreaks' 등 가능)
        k=5,            # 5단계 구분
        edgecolor='black',
        linewidth=0.5,
        alpha=0.8,      # 투명도 조절
        ax=ax,
        legend_kwds={'title': f"{index[1]} {index[0]}차 수"}
    )
    
    
    # 배경지도 추가 (contextily 사용)
    ctx.add_basemap(ax, crs=sgg_car.crs.to_string())
    
    for idx, row in sgg_obj_data.iterrows():
        # 폴리곤의 중심 좌표를 계산
        centroid = row['geometry'].centroid
        # 시군구 이름을 표시 (원하는 텍스트 스타일을 추가 가능)
        ax.text(centroid.x, centroid.y, row['district'], fontsize=8, ha='center', color='black')
    
    # 플롯을 보여줌
    plt.title(f"{year}-{month} {option_region} {index[1]} {index[0]}차 등록현황")
    st.pyplot(fig)


def before_map(df, year, month, region, type):  
    year = year.replace("-", '2025')
    month = month.replace("-", "02")
    get_shp(df)
    type1 = type + "_total"
    if  type == 'all':
        type1 = 'total_all'
    if region != '-':
        sgg_map(year, month, region, type1)
    else:
        sido_map(year, month, type1)
    
