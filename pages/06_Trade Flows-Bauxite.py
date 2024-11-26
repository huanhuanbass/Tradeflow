from oceanbolt.sdk.client import APIClient
base_client = APIClient('eyJhbGciOiJSUzI1NiIsImtpZCI6ImUxNmUwNWI1NTZmNjVjYWEyNTg0ODU0N2FmYjNjZjI4IiwidHlwIjoiSldUIn0.eyJhdWQiOiJodHRwczovL2FwaS5vY2VhbmJvbHQuY29tIiwiZXhwIjoxNzMxNTk4NjIwLCJpYXQiOjE2OTk5NzYyNzEsImlzcyI6Imh0dHBzOi8vYXV0aC5vY2VhbmJvbHQuY29tLyIsImtpZCI6ImUxNmUwNWI1NTZmNjVjYWEyNTg0ODU0N2FmYjNjZjI4Iiwia3R5cGUiOiJhcGlrZXkiLCJvYmtpZCI6IlJ2VndVT2pZaGhXSjY3NU8iLCJvcmdpZCI6ImNvZmNvIiwic3ViIjoiYXV0aDB8NjU1MzUwNDEyOGQ4Nzg1M2JlZGY2NDdiIn0.UIsNEUGlFvKJyN4a-3kj6xcbbrygoC3B0xWZVSLdpEx7uSyr2ZD3i-lJ3PgiEoOOJettAcnuGjh0NwgaL_Qx4T-GAxvLqdAKJe_8c-hOzETmeHdeme8HfxIGg5i3bPY_PvRx1RGfAjKy9y9sFB3Qe1ARB-Q2KDwN55sVNQIX7Cdyvpxm2WbAEaGyqZzW4kik4FAYOqYVfUgfRWVNAtv372LQlnCF82PC6JeZKJifHu6WBWh3Y7ATVt1QZDe9yF7ITFGAHsQooVu9hEpJ-VvEcf_fEVGIJYJIN0bhJQtw_lOCW_VVMy2n4RolaGsmqpnNdDqh2PctZWVF3MoYO4j2YC8a8sZ_FvouchjrMs6YX81DIfm2EjFqQ_vZE4SBTEiKYZ-_T1UvwHB7MuqT1Ubhpk0pjkoH0hP1k04dBRZc5kxlvwEPDTvX_K2HAM2eYfY10iF-R_iLcO7eU7pR_-Ch0iwelt5xEabFzVIMqTxNoDZHAaaZR0YhR58Md3bD7Xr9kk3ZSvfBJ-ctbEd2uKj_GrdVyKE4bEZSoV_QZ4YoQGO6lVhR5hDwfrqNioWqj1JKlwJ-Q1V8L3396DQzE6gtHgccP951QzEBfe1SUMItyjeULa4FjQUFhm7PsQKqUxMg6kZumDYYKpM-_qI0g24PvhuwH_7lW3cRqe7v-018qhU')

import streamlit as st
import plotly.express as px
import warnings; warnings.simplefilter('ignore')
import pandas as pd
import numpy as np
from datetime import date
from datetime import timedelta

import plotly.graph_objects as go

draft_template = go.layout.Template()
draft_template.layout.annotations = [
    dict(
        name="draft watermark",
        text="COFCO Internal Use Only",
        textangle=0,
        opacity=0.1,
        font=dict(color="black", size=70),
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
    )
]

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)

plot_ticks='inside'
plot_tickwidth=2
plot_ticklen=10
plot_title_font_color='dodgerblue'
plot_title_font_size=25
plot_legend_font_size=15
plot_axis=dict(tickfont = dict(size=15))

cutoff = pd.to_datetime('today')
curryear=cutoff.year
currmonth=cutoff.month
currday=cutoff.day
todaypath='Historicals/'+str(pd.to_datetime('today').year*10000+pd.to_datetime('today').month*100+pd.to_datetime('today').day)

today = pd.to_datetime('today')
lastsun = today - timedelta(days=today.weekday()) + timedelta(days=6, weeks=-1)
nextsun= lastsun+timedelta(days=7)
wkcutoff=lastsun


bauxite_country_list=['Guinea','Australia']


tf=st.session_state['tradeflow']


st.title('Bauxite Trade Flow')
st.text('Dry Bulk Freight (Bauxite) Interactive Dashboard')



@st.cache_data
def load_bauxite_data():
    bauxite=tf[tf['commodity_group']=='Bauxite']
    bauxite_country_list=['Guinea','Australia']
    EUlist=['Austria','Belgium','Bulgaria','Croatia','Cyprus','Czechia','Denmark','Estonia','Finland','France','Germany','Greece',
            'Hungary','Ireland','Italy','Latvia','Lithuania','Luxembourg','Malta','Netherlands','Poland','Portugal','Romania',
            'Slovakia','Slovenia','Spain','Sweden']
    bauxite['load_group']=np.where(bauxite['load_country'].isin(bauxite_country_list),bauxite['load_country'],'Others')
    bauxite['discharge_group']=np.where(bauxite['discharge_country'].isin(EUlist),'EU',bauxite['discharge_country'])
    bauxite['discharge_group']=np.where(bauxite['discharge_group'].isin(['China','Singapore','Unknown Country']),bauxite['discharge_group'],'Others')
    return bauxite

bauxite=load_bauxite_data()

freq_bauxite=st.radio('Select Frequency',options=['Weekly','Monthly'],key='freq_bauxite')

if freq_bauxite=='Weekly':
    st.header('World Bauxite Loadings')
    yr1=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr1')
    df=bauxite[bauxite['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df.set_index('Date',inplace=True)
    df=df[['voy_intake_mt']]
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df['Week']=df.index.isocalendar().week
    df.loc[df[df.index.date==date(2016,1,2)].index,'Week']=0
    df.loc[df[df.index.date==date(2021,1,2)].index,'Week']=0
    df.loc[df[df.index.date==date(2022,1,1)].index,'Week']=0
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr1]
    df=df.pivot_table(index='Week',columns='Year',values='voy_intake_mt',aggfunc='sum')/1000000
    dfplot=px.line(df,width=1000,height=500,title='World Bauxite Weekly Loadings Seasonality')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr4=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr4')
    df=bauxite[bauxite['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='load_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr4]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='World Bauxite Weekly Loadings by Loading Countries')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr2=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr2')
    df=bauxite[bauxite['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='segment',values='voy_intake_mt',aggfunc='sum')/1000000 
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr2]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='World Bauxite Weekly Loadings Size Split')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr6=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr6')
    df=bauxite[bauxite['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr6]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='World Bauxite Weekly Loadings Destination Split')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)



    st.header('Bauxite Loadings from Different Loading Countries')
    lc1=st.selectbox('Select Loading Country',options=bauxite_country_list,key='lc1')
    yr8=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr8')
    df=bauxite[bauxite['load_country']==lc1]
    df=df[df['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df.set_index('Date',inplace=True)
    df=df[['voy_intake_mt']]
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df['Week']=df.index.isocalendar().week
    df.loc[df[df.index.date==date(2016,1,2)].index,'Week']=0
    df.loc[df[df.index.date==date(2021,1,2)].index,'Week']=0
    df.loc[df[df.index.date==date(2022,1,1)].index,'Week']=0
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr8]
    df=df.pivot_table(index='Week',columns='Year',values='voy_intake_mt',aggfunc='sum')/1000000
    dfplot=px.line(df,width=1000,height=500,title='Bauxite Weekly Loadings Seasonality from '+str(lc1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr9=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr9')
    df=bauxite[bauxite['load_country']==lc1]
    df=df[df['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='segment',values='voy_intake_mt',aggfunc='sum')/1000000 
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr9]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Bauxite Weekly Loadings Size Split from '+str(lc1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr10=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr10')
    df=bauxite[bauxite['load_country']==lc1]
    df=df[df['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr10]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Bauxite Weekly Loadings Destination Split from '+str(lc1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    st.header('Bauxite Loadings on Different Sizes')
    size1=st.selectbox('Select Size',options=['Capesize','Panamax','Supramax','Handysize'],key='sz1')
    yr3=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr3')
    df=bauxite[bauxite['segment']==size1]
    df['Date']=pd.to_datetime(df['Date'])
    df.set_index('Date',inplace=True)
    df=df[['voy_intake_mt']]
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df['Week']=df.index.isocalendar().week
    df.loc[df[df.index.date==date(2016,1,2)].index,'Week']=0
    df.loc[df[df.index.date==date(2021,1,2)].index,'Week']=0
    df.loc[df[df.index.date==date(2022,1,1)].index,'Week']=0
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr3]
    df=df.pivot_table(index='Week',columns='Year',values='voy_intake_mt',aggfunc='sum')/1000000
    dfplot=px.line(df,width=1000,height=500,title='Bauxite Weekly Loadings Seasonality on '+str(size1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr5=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr5')
    df=bauxite[bauxite['segment']==size1]
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='load_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr5]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Bauxite Weekly Loadings by Loading Countries on '+str(size1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr7=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr7')
    df=bauxite[bauxite['segment']==size1]
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr7]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Bauxite Weekly Loadings Destination Split on '+str(size1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    st.header('Bauxite Loadings from Different Countries on Different Sizes')
    lc4=st.selectbox('Select Loading Country',options=bauxite_country_list,key='lc4')
    size4=st.selectbox('Select Size',options=['Capesize','Panamax','Supramax','Handysize'],key='sz4')
    yr11=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr11')  
    df=bauxite[bauxite['load_country']==lc4]
    df=df[df['segment']==size4]
    df['Date']=pd.to_datetime(df['Date'])
    df.set_index('Date',inplace=True)
    df=df[['voy_intake_mt']]
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df['Week']=df.index.isocalendar().week
    df.loc[df[df.index.date==date(2016,1,2)].index,'Week']=0
    df.loc[df[df.index.date==date(2021,1,2)].index,'Week']=0
    df.loc[df[df.index.date==date(2022,1,1)].index,'Week']=0
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr11]
    df=df.pivot_table(index='Week',columns='Year',values='voy_intake_mt',aggfunc='sum')/1000000
    dfplot=px.line(df,width=1000,height=500,title='Bauxite Weekly Loadings Seasonality from ' +str(lc4)+' on '+str(size4))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr12=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr12')   
    df=bauxite[bauxite['load_country']==lc4]
    df=df[df['segment']==size4]
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr12]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Bauxite Weekly Loadings Destination Split from '+str(lc4)+' on '+str(size4))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

if freq_bauxite=='Monthly':
    st.header('World Bauxite Loadings')
    yr1=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr1')
    df=bauxite[bauxite['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df.set_index('Date',inplace=True)
    df=df[['voy_intake_mt']]
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df['Month']=df.index.month
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr1]
    df=df.pivot_table(index='Month',columns='Year',values='voy_intake_mt',aggfunc='sum')/1000000
    dfplot=px.line(df,width=1000,height=500,title='World Bauxite Monthly Loadings Seasonality')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr4=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr4')
    df=bauxite[bauxite['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='load_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr4]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='World Bauxite Monthly Loadings by Loading Countries')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr2=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr2')
    df=bauxite[bauxite['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='segment',values='voy_intake_mt',aggfunc='sum')/1000000 
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr2]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='World Bauxite Monthly Loadings Size Split')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr6=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr6')
    df=bauxite[bauxite['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr6]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='World Bauxite Monthly Loadings Destination Split')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)


    st.header('Bauxite Loadings from Different Loading Countries')
    lc1=st.selectbox('Select Loading Country',options=bauxite_country_list,key='lc1')
    yr8=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr8')
    df=bauxite[bauxite['load_country']==lc1]
    df=df[df['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df.set_index('Date',inplace=True)
    df=df[['voy_intake_mt']]
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df['Month']=df.index.month
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr8]
    df=df.pivot_table(index='Month',columns='Year',values='voy_intake_mt',aggfunc='sum')/1000000
    dfplot=px.line(df,width=1000,height=500,title='Bauxite Monthly Loadings Seasonality from '+str(lc1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr9=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr9')
    df=bauxite[bauxite['load_country']==lc1]
    df=df[df['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='segment',values='voy_intake_mt',aggfunc='sum')/1000000 
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr9]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Bauxite Monthly Loadings Size Split from '+str(lc1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr10=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr10')
    df=bauxite[bauxite['load_country']==lc1]
    df=df[df['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr10]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Bauxite Monthly Loadings Destination Split from '+str(lc1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    st.header('Bauxite Loadings on Different Sizes')
    size1=st.selectbox('Select Size',options=['Capesize','Panamax','Supramax','Handysize'],key='sz1')
    yr3=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr3')
    df=bauxite[bauxite['segment']==size1]
    df['Date']=pd.to_datetime(df['Date'])
    df.set_index('Date',inplace=True)
    df=df[['voy_intake_mt']]
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df['Month']=df.index.month
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr3]
    df=df.pivot_table(index='Month',columns='Year',values='voy_intake_mt',aggfunc='sum')/1000000
    dfplot=px.line(df,width=1000,height=500,title='Bauxite Monthly Loadings Seasonality on '+str(size1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr5=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr5')
    df=bauxite[bauxite['segment']==size1]
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='load_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr5]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Bauxite Monthly Loadings by Loading Countries on '+str(size1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr7=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr7')
    df=bauxite[bauxite['segment']==size1]
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr7]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Bauxite Monthly Loadings Destination Split on '+str(size1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)


    st.header('Bauxite Loadings from Different Countries on Different Sizes')
    lc4=st.selectbox('Select Loading Country',options=bauxite_country_list,key='lc4')
    size4=st.selectbox('Select Size',options=['Capesize','Panamax','Supramax','Handysize'],key='sz4')
    yr11=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr11')   
    df=bauxite[bauxite['load_country']==lc4]
    df=df[df['segment']==size4]
    df['Date']=pd.to_datetime(df['Date'])
    df.set_index('Date',inplace=True)
    df=df[['voy_intake_mt']]
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df['Month']=df.index.month
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr11]
    df=df.pivot_table(index='Month',columns='Year',values='voy_intake_mt',aggfunc='sum')/1000000
    dfplot=px.line(df,width=1000,height=500,title='Bauxite Monthly Loadings Seasonality from ' +str(lc4)+' on '+str(size4))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr12=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr12')   
    df=bauxite[bauxite['load_country']==lc4]
    df=df[df['segment']==size4]
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr12]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Bauxite Monthly Loadings Destination Split from '+str(lc4)+' on '+str(size4))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)


