

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


soybeans_country_list=['Brazil','USA','Argentina']


tf=st.session_state['tradeflow']


st.title('Soybeans Trade Flow')
st.text('Dry Bulk Freight (Soybeans) Interactive Dashboard')



@st.cache_data
def load_soybeans_data():
    soybeans=tf[tf['commodity_group']=='Soybeans']
    soybeans_country_list=['Brazil','USA','Argentina']
    EUlist=['Austria','Belgium','Bulgaria','Croatia','Cyprus','Czechia','Denmark','Estonia','Finland','France','Germany','Greece',
            'Hungary','Ireland','Italy','Latvia','Lithuania','Luxembourg','Malta','Netherlands','Poland','Portugal','Romania',
            'Slovakia','Slovenia','Spain','Sweden']
    soybeans['load_group']=np.where(soybeans['load_country'].isin(soybeans_country_list),soybeans['load_country'],'Others')
    soybeans['discharge_group']=np.where(soybeans['discharge_country'].isin(EUlist),'EU',soybeans['discharge_country'])
    soybeans['discharge_group']=np.where(soybeans['discharge_group'].isin(['EU','China','Unknown Country','Japan','Korea, Republic of','Hong Kong','Taiwan, Province of China']),soybeans['discharge_group'],'Others')
    soybeans['discharge_group']=np.where(soybeans['discharge_group'].isin(['EU','China','Unknown Country','Others']),soybeans['discharge_group'],'JapanKoreaTWHK')
    soybeans['discharge_group']=np.where(soybeans['discharge_zone'].isin(['South East Asia']),'South East Asia',soybeans['discharge_group'])

    return soybeans

soybeans=load_soybeans_data()

freq_soybeans=st.radio('Select Frequency',options=['Weekly','Monthly'],key='freq_soybeans')

if freq_soybeans=='Weekly':
    st.header('World Soybeans Loadings')
    yr1=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr1')
    df=soybeans[soybeans['segment']!='Others']
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
    dfplot=px.line(df,width=1000,height=500,title='World Soybeans Weekly Loadings Seasonality')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr4=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr4')
    df=soybeans[soybeans['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='load_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr4]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='World Soybeans Weekly Loadings by Loading Countries')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr2=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr2')
    df=soybeans[soybeans['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='segment',values='voy_intake_mt',aggfunc='sum')/1000000 
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr2]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='World Soybeans Weekly Loadings Size Split')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr6=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr6')
    df=soybeans[soybeans['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr6]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='World Soybeans Weekly Loadings Destination Split')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)



    st.header('Soybeans Loadings from Different Loading Countries')
    lc1=st.selectbox('Select Loading Country',options=soybeans_country_list,key='lc1')
    yr8=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr8')
    df=soybeans[soybeans['load_group']==lc1]
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
    dfplot=px.line(df,width=1000,height=500,title='Soybeans Weekly Loadings Seasonality from '+str(lc1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr9=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr9')
    df=soybeans[soybeans['load_group']==lc1]
    df=df[df['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='segment',values='voy_intake_mt',aggfunc='sum')/1000000 
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr9]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Soybeans Weekly Loadings Size Split from '+str(lc1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr10=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr10')
    df=soybeans[soybeans['load_group']==lc1]
    df=df[df['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr10]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Soybeans Weekly Loadings Destination Split from '+str(lc1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    st.header('Soybeans Loadings on Different Sizes')
    size1=st.selectbox('Select Size',options=['Panamax','Supramax','Capesize','Handysize'],key='sz1')
    yr3=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr3')
    df=soybeans[soybeans['segment']==size1]
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
    dfplot=px.line(df,width=1000,height=500,title='Soybeans Weekly Loadings Seasonality on '+str(size1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr5=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr5')
    df=soybeans[soybeans['segment']==size1]
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='load_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr5]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Soybeans Weekly Loadings by Loading Countries on '+str(size1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr7=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr7')
    df=soybeans[soybeans['segment']==size1]
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr7]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Soybeans Weekly Loadings Destination Split on '+str(size1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    st.header('Soybeans Loadings from Different Countries on Different Sizes')
    lc4=st.selectbox('Select Loading Country',options=soybeans_country_list,key='lc4')
    size4=st.selectbox('Select Size',options=['Panamax','Supramax','Capesize','Handysize'],key='sz4')
    yr11=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr11')  
    df=soybeans[soybeans['load_group']==lc4]
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
    dfplot=px.line(df,width=1000,height=500,title='Soybeans Weekly Loadings Seasonality from ' +str(lc4)+' on '+str(size4))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr12=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr12')   
    df=soybeans[soybeans['load_group']==lc4]
    df=df[df['segment']==size4]
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('W-Sat').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr12]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Soybeans Weekly Loadings Destination Split from '+str(lc4)+' on '+str(size4))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

if freq_soybeans=='Monthly':
    st.header('World Soybeans Loadings')
    yr1=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr1')
    df=soybeans[soybeans['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df.set_index('Date',inplace=True)
    df=df[['voy_intake_mt']]
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df['Month']=df.index.month
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr1]
    df=df.pivot_table(index='Month',columns='Year',values='voy_intake_mt',aggfunc='sum')/1000000
    dfplot=px.line(df,width=1000,height=500,title='World Soybeans Monthly Loadings Seasonality')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr4=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr4')
    df=soybeans[soybeans['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='load_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr4]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='World Soybeans Monthly Loadings by Loading Countries')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr2=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr2')
    df=soybeans[soybeans['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='segment',values='voy_intake_mt',aggfunc='sum')/1000000 
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr2]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='World Soybeans Monthly Loadings Size Split')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr6=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr6')
    df=soybeans[soybeans['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr6]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='World Soybeans Monthly Loadings Destination Split')
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)


    st.header('Soybeans Loadings from Different Loading Countries')
    lc1=st.selectbox('Select Loading Country',options=soybeans_country_list,key='lc1')
    yr8=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr8')
    df=soybeans[soybeans['load_group']==lc1]
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
    dfplot=px.line(df,width=1000,height=500,title='Soybeans Monthly Loadings Seasonality from '+str(lc1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr9=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr9')
    df=soybeans[soybeans['load_group']==lc1]
    df=df[df['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='segment',values='voy_intake_mt',aggfunc='sum')/1000000 
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr9]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Soybeans Monthly Loadings Size Split from '+str(lc1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr10=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr10')
    df=soybeans[soybeans['load_group']==lc1]
    df=df[df['segment']!='Others']
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr10]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Soybeans Monthly Loadings Destination Split from '+str(lc1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    st.header('Soybeans Loadings on Different Sizes')
    size1=st.selectbox('Select Size',options=['Panamax','Supramax','Capesize','Handysize'],key='sz1')
    yr3=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr3')
    df=soybeans[soybeans['segment']==size1]
    df['Date']=pd.to_datetime(df['Date'])
    df.set_index('Date',inplace=True)
    df=df[['voy_intake_mt']]
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df['Month']=df.index.month
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr3]
    df=df.pivot_table(index='Month',columns='Year',values='voy_intake_mt',aggfunc='sum')/1000000
    dfplot=px.line(df,width=1000,height=500,title='Soybeans Monthly Loadings Seasonality on '+str(size1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr5=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr5')
    df=soybeans[soybeans['segment']==size1]
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='load_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr5]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Soybeans Monthly Loadings by Loading Countries on '+str(size1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr7=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr7')
    df=soybeans[soybeans['segment']==size1]
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr7]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Soybeans Monthly Loadings Destination Split on '+str(size1))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)


    st.header('Soybeans Loadings from Different Countries on Different Sizes')
    lc4=st.selectbox('Select Loading Country',options=soybeans_country_list,key='lc4')
    size4=st.selectbox('Select Size',options=['Panamax','Supramax','Capesize','Handysize'],key='sz4')
    yr11=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-4,step=1,key='yr11')   
    df=soybeans[soybeans['load_group']==lc4]
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
    dfplot=px.line(df,width=1000,height=500,title='Soybeans Monthly Loadings Seasonality from ' +str(lc4)+' on '+str(size4))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot['data'][-1]['line']['width']=5
    dfplot['data'][-1]['line']['color']='black'
    dfplot.update_layout(yaxis_title='Million Tonnes')
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)

    yr12=st.number_input('Input Start Year',min_value=2015,max_value=curryear,value=curryear-2,step=1,key='yr12')   
    df=soybeans[soybeans['load_group']==lc4]
    df=df[df['segment']==size4]
    df['Date']=pd.to_datetime(df['Date'])
    df=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000   
    df=df.resample('M').sum()
    df['Year']=df.index.year
    df=df[df.index<wkcutoff]
    df=df[df['Year']>=yr12]
    df.drop(columns=['Year'],inplace=True)
    dfplot=px.area(df,width=1000,height=500,title='Soybeans Monthly Loadings Destination Split from '+str(lc4)+' on '+str(size4))
    dfplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    dfplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    dfplot.update_layout(template=draft_template)
    st.plotly_chart(dfplot)


