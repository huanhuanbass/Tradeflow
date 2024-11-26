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


coal_country_list=['Australia','Indonesia','South Africa','Russia','USA','Colombia','China','Canada']



tf=st.session_state['tradeflow']


st.title('Coal Trade Flow')
st.text('Dry Bulk Freight (Coal) Interactive Dashboard')

cncoal=st.radio('Exclude China Coastal Coal Trade?',options=['Y','N'],key='cncoal')

@st.cache_data
def load_coal_data():
    coal=tf[tf['commodity_group']=='Coal']
    coal_country_list=['Australia','Indonesia','South Africa','Russian Federation','United States','Colombia','China','Canada']
    EUlist=['Austria','Belgium','Bulgaria','Croatia','Cyprus','Czechia','Denmark','Estonia','Finland','France','Germany','Greece',
            'Hungary','Ireland','Italy','Latvia','Lithuania','Luxembourg','Malta','Netherlands','Poland','Portugal','Romania',
            'Slovakia','Slovenia','Spain','Sweden']
    coal['load_group']=np.where(coal['load_country'].isin(coal_country_list),coal['load_country'],'Others')
    coal['discharge_group']=np.where(coal['discharge_country'].isin(EUlist),'EU',coal['discharge_country'])
    coal['discharge_group']=np.where(coal['discharge_group'].isin(['EU','China','India','Turkey','Unknown Country','Japan','Korea, Republic of','Hong Kong','Taiwan, Province of China']),coal['discharge_group'],'Others')
    coal['discharge_group']=np.where(coal['discharge_group'].isin(['EU','China','India','Turkey','Unknown Country','Others']),coal['discharge_group'],'JapanKoreaTWHK')
    coal['discharge_group']=np.where(coal['discharge_zone'].isin(['South East Asia']),'South East Asia',coal['discharge_group'])
    return coal

coal_raw=load_coal_data()
coal=coal_raw.copy()

if cncoal=='Y':
    coal=coal[~((coal['commodity_group']=='Coal')&(coal['load_country']=='China')&(coal['discharge_country']=='China'))]

freq_coal=st.radio('Select Frequency',options=['Weekly','Monthly'],key='freq_coal')

if freq_coal=='Weekly':
    st.header('World Coal Loadings')
    yr1=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr1')
    df=coal[coal['segment']!='Others']
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
    dfplot=px.line(df,width=1000,height=500,title='World Coal Weekly Loadings Seasonality')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr4=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr4')
    df=coal[coal['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='load_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr4]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='World Coal Weekly Loadings by Loading Countries')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr2=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr2')
    df=coal[coal['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='segment',values='voy_intake_mt',aggfunc='sum')/1000000 
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr2]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='World Coal Weekly Loadings Size Split')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr6=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr6')
    df=coal[coal['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr6]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='World Coal Weekly Loadings Destination Split')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)



    st.header('Coal Loadings from Different Loading Countries')
    lc1=st.selectbox('Select Loading Country',options=coal_country_list,key='lc1')
    yr8=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr8')
    df=coal[coal['load_country']==lc1]
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
    dfplot=px.line(df,width=1000,height=500,title='Coal Weekly Loadings Seasonality from '+str(lc1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr9=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr9')
    df=coal[coal['load_country']==lc1]
    df=df[df['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='segment',values='voy_intake_mt',aggfunc='sum')/1000000 
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr9]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Coal Weekly Loadings Size Split from '+str(lc1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr10=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr10')
    df=coal[coal['load_country']==lc1]
    df=df[df['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr10]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Coal Weekly Loadings Destination Split from '+str(lc1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    st.header('Coal Loadings on Different Sizes')
    size1=st.selectbox('Select Size',options=['Capesize','Panamax','Supramax','Handysize'],key='sz1')
    yr3=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr3')
    df=coal[coal['segment']==size1]
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
    dfplot=px.line(df,width=1000,height=500,title='Coal Weekly Loadings Seasonality on '+str(size1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr5=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr5')
    df=coal[coal['segment']==size1]
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='load_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr5]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Coal Weekly Loadings by Loading Countries on '+str(size1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr7=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr7')
    df=coal[coal['segment']==size1]
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr7]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Coal Weekly Loadings Destination Split on '+str(size1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    st.header('Coal Loadings from Different Countries on Different Sizes')
    lc4=st.selectbox('Select Loading Country',options=coal_country_list,key='lc4')
    size4=st.selectbox('Select Size',options=['Capesize','Panamax','Supramax','Handysize'],key='sz4')
    yr11=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr11')   
    df=coal[coal['load_country']==lc4]
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
    dfplot=px.line(df,width=1000,height=500,title='Coal Weekly Loadings Seasonality from ' +str(lc4)+' on '+str(size4))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr12=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr12')  
    df=coal[coal['load_country']==lc4]
    df=df[df['segment']==size4]
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr12]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Coal Weekly Loadings Destination Split from '+str(lc4)+' on '+str(size4))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

if freq_coal=='Monthly':
    st.header('World Coal Loadings')
    yr1=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr1')
    df=coal[coal['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df.set_index('Date',inplace=True)
    df=df[['voy_intake_mt']]
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df['Month']=df.index.month
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr1]
    df=df.pivot_table(index='Month',columns='Year',values='voy_intake_mt',aggfunc='sum')/1000000
    dfplot=px.line(df,width=1000,height=500,title='World Coal Monthly Loadings Seasonality')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr4=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr4')
    df=coal[coal['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='load_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr4]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='World Coal Monthly Loadings by Loading Countries')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr2=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr2')
    df=coal[coal['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='segment',values='voy_intake_mt',aggfunc='sum')/1000000 
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr2]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='World Coal Monthly Loadings Size Split')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr6=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr6')
    df=coal[coal['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr6]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='World Coal Monthly Loadings Destination Split')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)



    st.header('Coal Loadings from Different Loading Countries')
    lc1=st.selectbox('Select Loading Country',options=coal_country_list,key='lc1')
    yr8=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr8')
    df=coal[coal['load_country']==lc1]
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
    dfplot=px.line(df,width=1000,height=500,title='Coal Monthly Loadings Seasonality from '+str(lc1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr9=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr9')
    df=coal[coal['load_country']==lc1]
    df=df[df['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='segment',values='voy_intake_mt',aggfunc='sum')/1000000 
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr9]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Coal Monthly Loadings Size Split from '+str(lc1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr10=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr10')
    df=coal[coal['load_country']==lc1]
    df=df[df['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr10]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Coal Monthly Loadings Destination Split from '+str(lc1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    st.header('Coal Loadings on Different Sizes')
    size1=st.selectbox('Select Size',options=['Capesize','Panamax','Supramax','Handysize'],key='sz1')
    yr3=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr3')
    df=coal[coal['segment']==size1]
    df['Date']=pd.to_datetime(df['Date'])
    df.set_index('Date',inplace=True)
    df=df[['voy_intake_mt']]
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df['Month']=df.index.month
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr3]
    df=df.pivot_table(index='Month',columns='Year',values='voy_intake_mt',aggfunc='sum')/1000000
    dfplot=px.line(df,width=1000,height=500,title='Coal Monthly Loadings Seasonality on '+str(size1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr5=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr5')
    df=coal[coal['segment']==size1]
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='load_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr5]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Coal Monthly Loadings by Loading Countries on '+str(size1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr7=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr7')
    df=coal[coal['segment']==size1]
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr7]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Coal Monthly Loadings Destination Split on '+str(size1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    st.header('Coal Loadings from Different Countries on Different Sizes')
    lc4=st.selectbox('Select Loading Country',options=coal_country_list,key='lc4')
    size4=st.selectbox('Select Size',options=['Capesize','Panamax','Supramax','Handysize'],key='sz4')
    yr11=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr11')    
    df=coal[coal['load_country']==lc4]
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
    dfplot=px.line(df,width=1000,height=500,title='Coal Monthly Loadings Seasonality from ' +str(lc4)+' on '+str(size4))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr12=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr12')   
    df=coal[coal['load_country']==lc4]
    df=df[df['segment']==size4]
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr12]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Coal Monthly Loadings Destination Split from '+str(lc4)+' on '+str(size4))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)


