
import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import warnings; warnings.simplefilter('ignore')
import pandas as pd
import numpy as np
from datetime import date
from datetime import timedelta
from calendar import monthrange
from dateutil.relativedelta import *

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

tf=st.session_state['tradeflow']

#import freight data
spot=st.session_state['spot']

spot_w=spot.resample('W-Sat').mean()
spot_m=spot.resample('M').mean()
spot_q=spot.resample('Q').mean()


cutoff = pd.to_datetime('today')
curryear=cutoff.year
currmonth=cutoff.month
currday=cutoff.day
todaypath='Historicals/'+str(pd.to_datetime('today').year*10000+pd.to_datetime('today').month*100+pd.to_datetime('today').day)

today = pd.to_datetime('today')
td=today.date()
today=pd.to_datetime(td)
lastsun = today - timedelta(days=today.weekday()) + timedelta(days=6, weeks=-1)
nextsun= lastsun+timedelta(days=7)
wkcutoff=lastsun



st.title('Panamax Trade Flow')
st.text('Dry Bulk Freight (Trade Flow) Interactive Dashboard')


st.markdown('## **Panamax Trade Flow and Correlation Charts**')

cncoal=st.radio('Exclude China Coastal Coal Trade?',options=['Y','N'],key='cncoal')

tf_pmx=tf[tf['segment']=='Panamax']
if cncoal=='Y':
    tf_pmx=tf_pmx[~((tf_pmx['commodity_group']=='Coal')&(tf_pmx['load_country']=='China')&(tf_pmx['discharge_country']=='China'))]

tf_pmx.set_index('Date',inplace=True)
tf_pmx.index=pd.to_datetime(tf_pmx.index)

tf_pmx['Cargo and Country']=tf_pmx['commodity_group']+'_'+tf_pmx['load_country']
tf_pmx['Cargo and Country']=np.where(tf_pmx['Cargo and Country'].isin(['Coal_Australia','Soybeans_Brazil','Coal_Indonesia','Coal_Russia','Corn_Brazil','Coal_USA','Soybeans_USA','Coal_Canada','Coal_China','Coal_South Africa','Bauxite_Australia','Coal_Colombia']),tf_pmx['Cargo and Country'],'Others')
tf_pmx_pivot=tf_pmx.pivot_table(index='Date',columns='Cargo and Country',values='voy_intake_mt',aggfunc='sum')
tf_pmx_pivot.index=pd.to_datetime(tf_pmx_pivot.index)

tf_pmx_ocean=tf_pmx.pivot_table(index='Date',columns='load_ocean',values='voy_intake_mt',aggfunc='sum')
tf_pmx_ocean.index=pd.to_datetime(tf_pmx_ocean.index)

tf_pmx_cargo=tf_pmx.pivot_table(index='Date',columns='commodity_group',values='voy_intake_mt',aggfunc='sum')
tf_pmx_cargo.index=pd.to_datetime(tf_pmx_cargo.index)

tf_pmx_country=tf_pmx.pivot_table(index='Date',columns='load_group',values='voy_intake_mt',aggfunc='sum')
tf_pmx_country.index=pd.to_datetime(tf_pmx_country.index)

tf_pmx['Route']=tf_pmx['load_ocean']+'_'+tf_pmx['discharge_ocean']
tf_pmx_route=tf_pmx.pivot_table(index='Date',columns='Route',values='voy_intake_mt',aggfunc='sum')
tf_pmx_route.index=pd.to_datetime(tf_pmx_route.index)

tf_pmx['Cargo and Ocean']=tf_pmx['commodity_group']+'_'+tf_pmx['load_ocean']
tf_pmx_pivot2=tf_pmx.pivot_table(index='Date',columns='Cargo and Ocean',values='voy_intake_mt',aggfunc='sum')
tf_pmx_pivot2.index=pd.to_datetime(tf_pmx_pivot2.index)

freq1=st.radio('Select Frequency',options=['Weekly','Monthly','Quarterly'],key='freq1')

if freq1=='Weekly':
    tf_pmx_w=tf_pmx[['voy_intake_mt']].resample('W-Sat').sum()/1000000
    tf_pmx_w=tf_pmx_w[tf_pmx_w.index<wkcutoff]
    tf_pmx_w['Year']=tf_pmx_w.index.year
    tf_pmx_w['Week']=tf_pmx_w.index.isocalendar().week
    tf_pmx_w.loc[tf_pmx_w[tf_pmx_w.index.date==date(2016,1,2)].index,'Week']=0
    tf_pmx_w.loc[tf_pmx_w[tf_pmx_w.index.date==date(2021,1,2)].index,'Week']=0
    tf_pmx_w.loc[tf_pmx_w[tf_pmx_w.index.date==date(2022,1,1)].index,'Week']=0
    yrsl=st.multiselect('Select Years',options=tf_pmx_w['Year'].unique(),default=np.arange(curryear-4,curryear+1),key='year0')
    tf_pmx_w=tf_pmx_w[tf_pmx_w['Year'].isin(yrsl)]
    tf_pmx_w_seasonal=tf_pmx_w.pivot_table(index='Week',columns='Year',values='voy_intake_mt',aggfunc='sum')
    pmxplot=px.line(tf_pmx_w_seasonal,width=1000,height=500,title='Panamax Weekly Loadings Seasonality')
    pmxplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    pmxplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    pmxplot['data'][-1]['line']['width']=5
    pmxplot['data'][-1]['line']['color']='black'
    pmxplot.update_layout(yaxis_title='Million Tonnes')
    pmxplot.update_layout(template=draft_template)
    st.plotly_chart(pmxplot)

    tf_pmx_w_corr=pd.merge(tf_pmx_w,spot_w,how='left',left_index=True,right_index=True)
    tf_pmx_w_corr.reset_index(inplace=True)
    lag=st.number_input('Input Lag for Correlation Chart',value=0,step=1,key='lagw')
    if lag>0:
        tf_pmx_w_corr=tf_pmx_w_corr.reindex(range(len(tf_pmx_w_corr)+abs(lag)))
        for i in range(abs(lag)):
            tf_pmx_w_corr.iloc[-abs(lag)+i,0]=tf_pmx_w_corr.iloc[-abs(lag)+i-1,0]+relativedelta(days=7)

    tf_pmx_w_corr['voy_intake_mt']=tf_pmx_w_corr['voy_intake_mt'].shift(lag)
    cor=tf_pmx_w_corr[['voy_intake_mt','P4TC']].corr().iloc[0,1].round(2)
    tf_pmx_w_corr.set_index('Date',inplace=True)

    subplot_fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig1=px.line(tf_pmx_w_corr['voy_intake_mt'])
    fig2=px.line(tf_pmx_w_corr['P4TC'])
    fig2.update_traces(yaxis='y2')
    subplot_fig.add_traces(fig1.data + fig2.data)
    subplot_fig.update_layout(title='Panamax Weekly Loadings Correlation vs P4TC (corr: '+str(cor)+')',width=1000,height=500)
    subplot_fig.layout.xaxis.title='Date'
    subplot_fig.layout.yaxis.title='Million Tonnes'
    subplot_fig.layout.yaxis2.title='P4TC'
    subplot_fig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))
    subplot_fig.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    subplot_fig.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    subplot_fig.update_layout(template=draft_template)
    st.plotly_chart(subplot_fig)

    fig0 = px.scatter(tf_pmx_w_corr, x='voy_intake_mt', y='P4TC')
    fig0.update_layout(title='Panamax Weekly Loadings Correlation vs P4TC (corr: '+str(cor)+')',width=1000,height=500)
    fig0.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig0.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig0.update_layout(template=draft_template)
    st.plotly_chart(fig0)

    tf_pmx_cargo_w=tf_pmx_cargo.resample('W-Sat').sum()/1000000
    yrsl001c=st.multiselect('Select Years',options=tf_pmx_cargo_w.index.year.unique(),default=np.arange(curryear-1,curryear+1),key='year001c')
    tf_pmx_cargo_w=tf_pmx_cargo_w[pd.to_datetime(tf_pmx_cargo_w.index.date)<pd.to_datetime(wkcutoff)]
    tf_pmx_cargo_w.sort_index(ascending=False,inplace=True)
    tf_pmx_cargo_w.sort_values(by=tf_pmx_cargo_w.index[0], ascending=False, axis=1,inplace=True)    
    tf_pmx_cargo_w=tf_pmx_cargo_w[tf_pmx_cargo_w.index.year.isin(yrsl001c)]
    fig3=px.area(tf_pmx_cargo_w,width=1000,height=500,title='Panamax Weekly Loadings by Cargo')
    fig3.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig3.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig3.update_layout(template=draft_template)
    st.plotly_chart(fig3)

    tf_pmx_country_w=tf_pmx_country.resample('W-Sat').sum()/1000000
    yrsl001cc=st.multiselect('Select Years',options=tf_pmx_country_w.index.year.unique(),default=np.arange(curryear-1,curryear+1),key='year001cc')
    tf_pmx_country_w=tf_pmx_country_w[pd.to_datetime(tf_pmx_country_w.index.date)<pd.to_datetime(wkcutoff)]
    tf_pmx_country_w.sort_index(ascending=False,inplace=True)
    tf_pmx_country_w.sort_values(by=tf_pmx_country_w.index[0], ascending=False, axis=1,inplace=True)    
    tf_pmx_country_w=tf_pmx_country_w[tf_pmx_country_w.index.year.isin(yrsl001cc)]
    fig3=px.area(tf_pmx_country_w,width=1000,height=500,title='Panamax Weekly Loadings by Load Country')
    fig3.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig3.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig3.update_layout(template=draft_template)
    st.plotly_chart(fig3)

    tf_pmx_ocean_w=tf_pmx_ocean.resample('W-Sat').sum()/1000000
    yrsl001o=st.multiselect('Select Years',options=tf_pmx_ocean_w.index.year.unique(),default=np.arange(curryear-1,curryear+1),key='year001o')
    tf_pmx_ocean_w=tf_pmx_ocean_w[pd.to_datetime(tf_pmx_ocean_w.index.date)<pd.to_datetime(wkcutoff)]
    tf_pmx_ocean_w.sort_index(ascending=False,inplace=True)
    tf_pmx_ocean_w.sort_values(by=tf_pmx_ocean_w.index[0], ascending=False, axis=1,inplace=True)    
    tf_pmx_ocean_w=tf_pmx_ocean_w[tf_pmx_ocean_w.index.year.isin(yrsl001o)]
    fig3=px.area(tf_pmx_ocean_w,width=1000,height=500,title='Panamax Weekly Loadings by Load Ocean')
    fig3.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig3.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig3.update_layout(template=draft_template)
    st.plotly_chart(fig3)

    tf_pmx_pivot_w=tf_pmx_pivot.resample('W-Sat').sum()/1000000
    yrsl001=st.multiselect('Select Years',options=tf_pmx_pivot_w.index.year.unique(),default=np.arange(curryear-1,curryear+1),key='year001')
    tf_pmx_pivot_w=tf_pmx_pivot_w[pd.to_datetime(tf_pmx_pivot_w.index.date)<pd.to_datetime(wkcutoff)]
    tf_pmx_pivot_w.sort_index(ascending=False,inplace=True)
    tf_pmx_pivot_w.sort_values(by=tf_pmx_pivot_w.index[0], ascending=False, axis=1,inplace=True)    
    tf_pmx_pivot_w=tf_pmx_pivot_w[tf_pmx_pivot_w.index.year.isin(yrsl001)]
    fig3=px.area(tf_pmx_pivot_w,width=1000,height=500,title='Panamax Weekly Loadings by Cargo and Load Country')
    fig3.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig3.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig3.update_layout(template=draft_template)
    st.plotly_chart(fig3)

    tf_pmx_pivot2_w=tf_pmx_pivot2.resample('W-Sat').sum()/1000000
    yrsl002=st.multiselect('Select Years',options=tf_pmx_pivot2_w.index.year.unique(),default=np.arange(curryear-1,curryear+1),key='year002')
    tf_pmx_pivot2_w=tf_pmx_pivot2_w[pd.to_datetime(tf_pmx_pivot2_w.index.date)<pd.to_datetime(wkcutoff)]
    tf_pmx_pivot2_w.sort_index(ascending=False,inplace=True)
    tf_pmx_pivot2_w.sort_values(by=tf_pmx_pivot2_w.index[0], ascending=False, axis=1,inplace=True)    
    tf_pmx_pivot2_w=tf_pmx_pivot2_w[tf_pmx_pivot2_w.index.year.isin(yrsl002)]
    fig3=px.area(tf_pmx_pivot2_w,width=1000,height=500,title='Panamax Weekly Loadings by Cargo and Load Ocean')
    fig3.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig3.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig3.update_layout(template=draft_template)
    st.plotly_chart(fig3)

    tf_pmx_route_w=tf_pmx_route.resample('W-Sat').sum()/1000000
    yrsl001r=st.multiselect('Select Years',options=tf_pmx_route_w.index.year.unique(),default=np.arange(curryear-1,curryear+1),key='year001r')
    tf_pmx_route_w=tf_pmx_route_w[pd.to_datetime(tf_pmx_route_w.index.date)<pd.to_datetime(wkcutoff)]
    tf_pmx_route_w.sort_index(ascending=False,inplace=True)
    tf_pmx_route_w.sort_values(by=tf_pmx_route_w.index[0], ascending=False, axis=1,inplace=True)    
    tf_pmx_route_w=tf_pmx_route_w[tf_pmx_route_w.index.year.isin(yrsl001r)]
    fig3=px.area(tf_pmx_route_w,width=1000,height=500,title='Panamax Weekly Loadings by Route')
    fig3.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig3.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig3.update_layout(template=draft_template)
    st.plotly_chart(fig3)


elif freq1=='Monthly':
    tf_pmx_m=tf_pmx[['voy_intake_mt']].resample('M').sum()/1000000
    tf_pmx_m=tf_pmx_m[tf_pmx_m.index<wkcutoff]
    tf_pmx_m['Year']=tf_pmx_m.index.year
    tf_pmx_m['Month']=tf_pmx_m.index.month
    yrsl=st.multiselect('Select Years',options=tf_pmx_m['Year'].unique(),default=np.arange(curryear-6,curryear+1),key='year0')
    tf_pmx_m=tf_pmx_m[tf_pmx_m['Year'].isin(yrsl)]
    tf_pmx_m_seasonal=tf_pmx_m.pivot_table(index='Month',columns='Year',values='voy_intake_mt',aggfunc='sum')
    pmxplot=px.line(tf_pmx_m_seasonal,width=1000,height=500,title='Panamax Monthly Loadings Seasonality')
    pmxplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    pmxplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    pmxplot['data'][-1]['line']['width']=5
    pmxplot['data'][-1]['line']['color']='black'
    pmxplot.update_layout(yaxis_title='Million Tonnes')
    pmxplot.update_layout(template=draft_template)
    st.plotly_chart(pmxplot)

    tf_pmx_m_corr=pd.merge(tf_pmx_m,spot_m,how='left',left_index=True,right_index=True)
    tf_pmx_m_corr.reset_index(inplace=True)
    lag=st.number_input('Input Lag for Correlation Chart',value=0,step=1,key='lagm')
    if lag>0:
        tf_pmx_m_corr=tf_pmx_m_corr.reindex(range(len(tf_pmx_m_corr)+abs(lag)))
        for i in range(abs(lag)):
            tf_pmx_m_corr.iloc[-abs(lag)+i,0]=tf_pmx_m_corr.iloc[-abs(lag)+i-1,0]+relativedelta(months=1)

    tf_pmx_m_corr['voy_intake_mt']=tf_pmx_m_corr['voy_intake_mt'].shift(lag)
    cor=tf_pmx_m_corr[['voy_intake_mt','P4TC']].corr().iloc[0,1].round(2)
    tf_pmx_m_corr.set_index('Date',inplace=True)

    subplot_fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig1=px.line(tf_pmx_m_corr['voy_intake_mt'])
    fig2=px.line(tf_pmx_m_corr['P4TC'])
    fig2.update_traces(yaxis='y2')
    subplot_fig.add_traces(fig1.data + fig2.data)
    subplot_fig.update_layout(title='Panamax Monthly Loadings Correlation vs P4TC (corr: '+str(cor)+')',width=1000,height=500)
    subplot_fig.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    subplot_fig.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    subplot_fig.layout.xaxis.title='Date'
    subplot_fig.layout.yaxis.title='Million Tonnes'
    subplot_fig.layout.yaxis2.title='P4TC'
    subplot_fig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))
    subplot_fig.update_layout(template=draft_template)
    st.plotly_chart(subplot_fig)

    fig0 = px.scatter(tf_pmx_m_corr, x='voy_intake_mt', y='P4TC')
    fig0.update_layout(title='Panamax Monthly Loadings Correlation vs P4TC (corr: '+str(cor)+')',width=1000,height=500)
    fig0.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig0.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig0.update_layout(template=draft_template)
    st.plotly_chart(fig0)

    tf_pmx_cargo_m=tf_pmx_cargo.resample('M').sum()/1000000
    yrsl001c=st.multiselect('Select Years',options=tf_pmx_cargo_m.index.year.unique(),default=np.arange(curryear-1,curryear+1),key='year001c')
    tf_pmx_cargo_m=tf_pmx_cargo_m[pd.to_datetime(tf_pmx_cargo_m.index.date)<pd.to_datetime(wkcutoff)]
    tf_pmx_cargo_m.sort_index(ascending=False,inplace=True)
    tf_pmx_cargo_m.sort_values(by=tf_pmx_cargo_m.index[0], ascending=False, axis=1,inplace=True)    
    tf_pmx_cargo_m=tf_pmx_cargo_m[tf_pmx_cargo_m.index.year.isin(yrsl001c)]
    fig3=px.area(tf_pmx_cargo_m,width=1000,height=500,title='Panamax Monthly Loadings by Cargo')
    fig3.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig3.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig3.update_layout(template=draft_template)
    st.plotly_chart(fig3)

    tf_pmx_country_m=tf_pmx_country.resample('M').sum()/1000000
    yrsl001cc=st.multiselect('Select Years',options=tf_pmx_country_m.index.year.unique(),default=np.arange(curryear-1,curryear+1),key='year001cc')
    tf_pmx_country_m=tf_pmx_country_m[pd.to_datetime(tf_pmx_country_m.index.date)<pd.to_datetime(wkcutoff)]
    tf_pmx_country_m.sort_index(ascending=False,inplace=True)
    tf_pmx_country_m.sort_values(by=tf_pmx_country_m.index[0], ascending=False, axis=1,inplace=True)    
    tf_pmx_country_m=tf_pmx_country_m[tf_pmx_country_m.index.year.isin(yrsl001cc)]
    fig3=px.area(tf_pmx_country_m,width=1000,height=500,title='Panamax Monthly Loadings by Load Country')
    fig3.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig3.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig3.update_layout(template=draft_template)
    st.plotly_chart(fig3)

    tf_pmx_ocean_m=tf_pmx_ocean.resample('M').sum()/1000000
    yrsl001o=st.multiselect('Select Years',options=tf_pmx_ocean_m.index.year.unique(),default=np.arange(curryear-1,curryear+1),key='year001o')
    tf_pmx_ocean_m=tf_pmx_ocean_m[pd.to_datetime(tf_pmx_ocean_m.index.date)<pd.to_datetime(wkcutoff)]
    tf_pmx_ocean_m.sort_index(ascending=False,inplace=True)
    tf_pmx_ocean_m.sort_values(by=tf_pmx_ocean_m.index[0], ascending=False, axis=1,inplace=True)    
    tf_pmx_ocean_m=tf_pmx_ocean_m[tf_pmx_ocean_m.index.year.isin(yrsl001o)]
    fig3=px.area(tf_pmx_ocean_m,width=1000,height=500,title='Panamax Monthly Loadings by Load Ocean')
    fig3.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig3.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig3.update_layout(template=draft_template)
    st.plotly_chart(fig3)

    tf_pmx_pivot_m=tf_pmx_pivot.resample('M').sum()/1000000
    yrsl002=st.multiselect('Select Years',options=tf_pmx_pivot_m.index.year.unique(),default=np.arange(curryear-1,curryear+1),key='year002')    
    tf_pmx_pivot_m=tf_pmx_pivot_m[pd.to_datetime(tf_pmx_pivot_m.index.date)<pd.to_datetime(wkcutoff)]
    tf_pmx_pivot_m.sort_index(ascending=False,inplace=True)
    tf_pmx_pivot_m.sort_values(by=tf_pmx_pivot_m.index[0], ascending=False, axis=1,inplace=True)   
    tf_pmx_pivot_m=tf_pmx_pivot_m[tf_pmx_pivot_m.index.year.isin(yrsl002)]
    fig3=px.area(tf_pmx_pivot_m,width=1000,height=500,title='Panamax Monthly Loadings by Cargo and Origin')
    fig3.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig3.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig3.update_layout(template=draft_template)
    st.plotly_chart(fig3)

    tf_pmx_pivot2_m=tf_pmx_pivot2.resample('M').sum()/1000000
    yrsl002m=st.multiselect('Select Years',options=tf_pmx_pivot2_m.index.year.unique(),default=np.arange(curryear-1,curryear+1),key='year002m')
    tf_pmx_pivot2_m=tf_pmx_pivot2_m[pd.to_datetime(tf_pmx_pivot2_m.index.date)<pd.to_datetime(wkcutoff)]
    tf_pmx_pivot2_m.sort_index(ascending=False,inplace=True)
    tf_pmx_pivot2_m.sort_values(by=tf_pmx_pivot2_m.index[0], ascending=False, axis=1,inplace=True)    
    tf_pmx_pivot2_m=tf_pmx_pivot2_m[tf_pmx_pivot2_m.index.year.isin(yrsl002m)]
    fig3=px.area(tf_pmx_pivot2_m,width=1000,height=500,title='Panamax Monthly Loadings by Cargo and Load Ocean')
    fig3.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig3.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig3.update_layout(template=draft_template)
    st.plotly_chart(fig3)

    tf_pmx_route_m=tf_pmx_route.resample('M').sum()/1000000
    yrsl001r=st.multiselect('Select Years',options=tf_pmx_route_m.index.year.unique(),default=np.arange(curryear-1,curryear+1),key='year001r')
    tf_pmx_route_m=tf_pmx_route_m[pd.to_datetime(tf_pmx_route_m.index.date)<pd.to_datetime(wkcutoff)]
    tf_pmx_route_m.sort_index(ascending=False,inplace=True)
    tf_pmx_route_m.sort_values(by=tf_pmx_route_m.index[0], ascending=False, axis=1,inplace=True)    
    tf_pmx_route_m=tf_pmx_route_m[tf_pmx_route_m.index.year.isin(yrsl001r)]
    fig3=px.area(tf_pmx_route_m,width=1000,height=500,title='Panamax Monthly Loadings by Route')
    fig3.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig3.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig3.update_layout(template=draft_template)
    st.plotly_chart(fig3)


elif freq1=='Quarterly':
    tf_pmx_q=tf_pmx[['voy_intake_mt']].resample('Q').sum()/1000000
    tf_pmx_q=tf_pmx_q[tf_pmx_q.index<wkcutoff]
    tf_pmx_q['Year']=tf_pmx_q.index.year
    tf_pmx_q['Quarter']=tf_pmx_q.index.quarter
    yrsl=st.multiselect('Select Years',options=tf_pmx_q['Year'].unique(),default=np.arange(curryear-6,curryear),key='year0')
    tf_pmx_q=tf_pmx_q[tf_pmx_q['Year'].isin(yrsl)]
    tf_pmx_q_seasonal=tf_pmx_q.pivot_table(index='Quarter',columns='Year',values='voy_intake_mt',aggfunc='sum')
    pmxplot=px.line(tf_pmx_q_seasonal,width=1000,height=500,title='Panamax Quarterly Loadings Seasonality')
    pmxplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    pmxplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    pmxplot['data'][-1]['line']['width']=5
    pmxplot['data'][-1]['line']['color']='black'
    pmxplot.update_layout(yaxis_title='Million Tonnes')
    pmxplot.update_layout(template=draft_template)
    st.plotly_chart(pmxplot)

    tf_pmx_q_corr=pd.merge(tf_pmx_q,spot_q,how='left',left_index=True,right_index=True)
    tf_pmx_q_corr.reset_index(inplace=True)
    lag=st.number_input('Input Lag for Correlation Chart',value=0,step=1,key='lagq')
    if lag>0:
        tf_pmx_q_corr=tf_pmx_q_corr.reindex(range(len(tf_pmx_q_corr)+abs(lag)))
        for i in range(abs(lag)):
            tf_pmx_q_corr.iloc[-abs(lag)+i,0]=tf_pmx_q_corr.iloc[-abs(lag)+i-1,0]+relativedelta(months=3)

    tf_pmx_q_corr['voy_intake_mt']=tf_pmx_q_corr['voy_intake_mt'].shift(lag)
    cor=tf_pmx_q_corr[['voy_intake_mt','P4TC']].corr().iloc[0,1].round(2)
    tf_pmx_q_corr.set_index('Date',inplace=True)

    subplot_fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig1=px.line(tf_pmx_q_corr['voy_intake_mt'])
    fig2=px.line(tf_pmx_q_corr['P4TC'])
    fig2.update_traces(yaxis='y2')
    subplot_fig.add_traces(fig1.data + fig2.data)
    subplot_fig.update_layout(title='Panamax Quarterly Loadings Correlation vs P4TC (corr: '+str(cor)+')',width=1000,height=500)
    subplot_fig.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    subplot_fig.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    subplot_fig.layout.xaxis.title='Date'
    subplot_fig.layout.yaxis.title='Million Tonnes'
    subplot_fig.layout.yaxis2.title='P4TC'
    subplot_fig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))
    subplot_fig.update_layout(template=draft_template)
    st.plotly_chart(subplot_fig)

    fig0 = px.scatter(tf_pmx_q_corr, x='voy_intake_mt', y='P4TC')
    fig0.update_layout(title='Panamax Quarterly Loadings Correlation vs P4TC (corr: '+str(cor)+')',width=1000,height=500)
    fig0.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig0.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig0.update_layout(template=draft_template)
    st.plotly_chart(fig0)

    tf_pmx_cargo_q=tf_pmx_cargo.resample('Q').sum()/1000000
    yrsl001c=st.multiselect('Select Years',options=tf_pmx_cargo_q.index.year.unique(),default=np.arange(curryear-1,curryear+1),key='year001c')
    tf_pmx_cargo_q=tf_pmx_cargo_q[pd.to_datetime(tf_pmx_cargo_q.index.date)<pd.to_datetime(wkcutoff)]
    tf_pmx_cargo_q.sort_index(ascending=False,inplace=True)
    tf_pmx_cargo_q.sort_values(by=tf_pmx_cargo_q.index[0], ascending=False, axis=1,inplace=True)    
    tf_pmx_cargo_q=tf_pmx_cargo_q[tf_pmx_cargo_q.index.year.isin(yrsl001c)]
    fig3=px.area(tf_pmx_cargo_q,width=1000,height=500,title='Panamax Quarterly Loadings by Cargo')
    fig3.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig3.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig3.update_layout(template=draft_template)
    st.plotly_chart(fig3)

    tf_pmx_country_q=tf_pmx_country.resample('Q').sum()/1000000
    yrsl001cc=st.multiselect('Select Years',options=tf_pmx_country_q.index.year.unique(),default=np.arange(curryear-1,curryear+1),key='year001cc')
    tf_pmx_country_q=tf_pmx_country_q[pd.to_datetime(tf_pmx_country_q.index.date)<pd.to_datetime(wkcutoff)]
    tf_pmx_country_q.sort_index(ascending=False,inplace=True)
    tf_pmx_country_q.sort_values(by=tf_pmx_country_q.index[0], ascending=False, axis=1,inplace=True)    
    tf_pmx_country_q=tf_pmx_country_q[tf_pmx_country_q.index.year.isin(yrsl001cc)]
    fig3=px.area(tf_pmx_country_q,width=1000,height=500,title='Panamax Quarterly Loadings by Load Country')
    fig3.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig3.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig3.update_layout(template=draft_template)
    st.plotly_chart(fig3)

    tf_pmx_ocean_q=tf_pmx_ocean.resample('Q').sum()/1000000
    yrsl001o=st.multiselect('Select Years',options=tf_pmx_ocean_q.index.year.unique(),default=np.arange(curryear-1,curryear+1),key='year001o')
    tf_pmx_ocean_q=tf_pmx_ocean_q[pd.to_datetime(tf_pmx_ocean_q.index.date)<pd.to_datetime(wkcutoff)]
    tf_pmx_ocean_q.sort_index(ascending=False,inplace=True)
    tf_pmx_ocean_q.sort_values(by=tf_pmx_ocean_q.index[0], ascending=False, axis=1,inplace=True)    
    tf_pmx_ocean_q=tf_pmx_ocean_q[tf_pmx_ocean_q.index.year.isin(yrsl001o)]
    fig3=px.area(tf_pmx_ocean_q,width=1000,height=500,title='Panamax Quarterly Loadings by Load Ocean')
    fig3.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig3.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig3.update_layout(template=draft_template)
    st.plotly_chart(fig3)

    tf_pmx_pivot_q=tf_pmx_pivot.resample('Q').sum()/1000000
    yrsl003=st.multiselect('Select Years',options=tf_pmx_pivot_q.index.year.unique(),default=np.arange(curryear-3,curryear+1),key='year003')    
    tf_pmx_pivot_q=tf_pmx_pivot_q[pd.to_datetime(tf_pmx_pivot_q.index.date)<pd.to_datetime(wkcutoff)]
    tf_pmx_pivot_q.sort_index(ascending=False,inplace=True)
    tf_pmx_pivot_q.sort_values(by=tf_pmx_pivot_q.index[0], ascending=False, axis=1,inplace=True)    
    tf_pmx_pivot_q=tf_pmx_pivot_q[tf_pmx_pivot_q.index.year.isin(yrsl003)]
    fig3=px.area(tf_pmx_pivot_q,width=1000,height=500,title='Panamax Quarterly Loadings by Cargo and Origin')
    fig3.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig3.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig3.update_layout(template=draft_template)
    st.plotly_chart(fig3)

    tf_pmx_pivot2_q=tf_pmx_pivot2.resample('Q').sum()/1000000
    yrsl002m=st.multiselect('Select Years',options=tf_pmx_pivot2_q.index.year.unique(),default=np.arange(curryear-1,curryear+1),key='year002m')
    tf_pmx_pivot2_q=tf_pmx_pivot2_q[pd.to_datetime(tf_pmx_pivot2_q.index.date)<pd.to_datetime(wkcutoff)]
    tf_pmx_pivot2_q.sort_index(ascending=False,inplace=True)
    tf_pmx_pivot2_q.sort_values(by=tf_pmx_pivot2_q.index[0], ascending=False, axis=1,inplace=True)    
    tf_pmx_pivot2_q=tf_pmx_pivot2_q[tf_pmx_pivot2_q.index.year.isin(yrsl002m)]
    fig3=px.area(tf_pmx_pivot2_q,width=1000,height=500,title='Panamax Quarterly Loadings by Cargo and Load Ocean')
    fig3.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig3.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig3.update_layout(template=draft_template)
    st.plotly_chart(fig3)

    tf_pmx_route_q=tf_pmx_route.resample('Q').sum()/1000000
    yrsl001r=st.multiselect('Select Years',options=tf_pmx_route_q.index.year.unique(),default=np.arange(curryear-1,curryear+1),key='year001r')
    tf_pmx_route_q=tf_pmx_route_q[pd.to_datetime(tf_pmx_route_q.index.date)<pd.to_datetime(wkcutoff)]
    tf_pmx_route_q.sort_index(ascending=False,inplace=True)
    tf_pmx_route_q.sort_values(by=tf_pmx_route_q.index[0], ascending=False, axis=1,inplace=True)    
    tf_pmx_route_q=tf_pmx_route_q[tf_pmx_route_q.index.year.isin(yrsl001r)]
    fig3=px.area(tf_pmx_route_q,width=1000,height=500,title='Panamax Quarterly Loadings by Route')
    fig3.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
    fig3.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
    fig3.update_layout(template=draft_template)
    st.plotly_chart(fig3)

st.markdown('## **Panamax Trade Flows Numbers**')

st.write('Trade Flows for All Sizes: Atlantic')
tf_group=tf.pivot_table(index=['commodity_group','load_country'],columns='Date',values='voy_intake_mt',aggfunc='sum')
tf_group=tf_group[tf_group.index.isin([['Soybeans','Brazil'],['Coal','USA'],['Coal','Russia'],['Coal','Canada'],['Coal','South Africa'],['Soybeans','USA'],['Coal','Colombia'],['Corn','Brazil']])]
tf_group=tf_group/1000000
tf_group=tf_group.iloc[::-1]
tf_group=tf_group.transpose() 
tf_group.index=pd.to_datetime(tf_group.index)
tf_group=tf_group.resample('W-Sat').sum()
tf_group=tf_group[tf_group.index<wkcutoff]
tf_group.sort_index(ascending=False,inplace=True)
tf_group.index=tf_group.index.date
tf_group['Total']=tf_group.sum(axis=1)
tf_group=tf_group.head(2)
st.write(tf_group.style.format('{0:.1f}'))

st.write('Trade Flows for All Sizes: Pacific')
tf_group=tf.pivot_table(index=['commodity_group','load_country'],columns='Date',values='voy_intake_mt',aggfunc='sum')
tf_group=tf_group[tf_group.index.isin([['Coal','Indonesia'],['Coal','Australia'],['Bauxite','Australia'],['Coal','Russia']])]
tf_group=tf_group/1000000
tf_group=tf_group.iloc[::-1]
tf_group=tf_group.transpose() 
tf_group.index=pd.to_datetime(tf_group.index)
tf_group=tf_group.resample('W-Sat').sum()
tf_group=tf_group[tf_group.index<wkcutoff]
tf_group.sort_index(ascending=False,inplace=True)
tf_group.index=tf_group.index.date
tf_group['Total']=tf_group.sum(axis=1)
tf_group=tf_group.head(2)
st.write(tf_group.style.format('{0:.1f}'))


