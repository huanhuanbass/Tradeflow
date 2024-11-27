
import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import warnings; warnings.simplefilter('ignore')
import pandas as pd
import numpy as np
from datetime import date
from datetime import timedelta
from calendar import monthrange

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


st.title('Trade Flow Forecast')
st.text('Dry Bulk Freight (Trade Flow) Interactive Dashboard')


st.markdown('## **Iron Ore Forecast**')

inputio=pd.read_excel('Forecast/Iron Ore Input.xlsx')

fcstsl1=st.selectbox('Select the Date When the Forecast is Made',options=inputio['Forecast Date'].unique(),key='fcstsl1')

fcstio=inputio[inputio['Forecast Date']=='2024Q2']
fcstio['Vale+CSN']=fcstio['Vale']+fcstio['CSN']
fcstio['RT+BHP+FMG']=fcstio['Rio Tinto']+fcstio['BHP']+fcstio['FMG']

actio=tf[tf['commodity_group']=='Iron Ore']
actio=actio[actio['Year']>2015]

sizesplitio=actio.copy()
distanceio=actio.copy()

actio=actio.pivot_table(index=['Year','Month'],columns='load_group',values='voy_intake_mt',aggfunc='sum')
actio.reset_index(inplace=True)
actio['Quarter']=((actio['Month']-(actio['Month']+2)%3)+2)/3

st.markdown('#### **----Brazil**')

fcstiobzl=fcstio[['Year','Quarter','Vale+CSN']]
actiobzl=actio[['Year','Month','Quarter','Brazil']]

actiobzl_q=actiobzl.groupby(['Year','Quarter']).sum()
actiobzl_q.reset_index(inplace=True)
actiobzl_q=actiobzl_q[['Year','Quarter','Brazil']]
actiobzl_q.rename(columns={'Brazil':'Brazil_q'},inplace=True)

actiobzl=pd.merge(actiobzl,actiobzl_q,on=['Year','Quarter'],how='outer')

fcstiobzl1=fcstiobzl.copy()
fcstiobzl2=fcstiobzl.copy()
fcstiobzl3=fcstiobzl.copy()

fcstiobzl1['Month']=fcstiobzl1['Quarter']*3-2
fcstiobzl2['Month']=fcstiobzl2['Quarter']*3-1
fcstiobzl3['Month']=fcstiobzl3['Quarter']*3

fcstiobzl123=pd.concat([fcstiobzl1,fcstiobzl2,fcstiobzl3])
fcstiobzl123.sort_values(by=['Year','Month'],ascending=True,inplace=True)

actiobzl=pd.merge(actiobzl,fcstiobzl123,on=['Year','Quarter','Month'],how='outer')

actiobzl['Seasonal_act']=np.where((actiobzl['Year']==cutoff.year)&(actiobzl['Quarter']>=cutoff.quarter),0,actiobzl['Brazil']/actiobzl['Brazil_q'])
actiobzl['Seasonal_act']=np.where(actiobzl['Year']>cutoff.year,0,actiobzl['Seasonal_act'])

actiobzlssn=actiobzl[['Year','Month','Seasonal_act']]
actiobzlssn=actiobzlssn[actiobzlssn['Year']==cutoff.year-1]
actiobzlssn.drop(columns='Year',inplace=True)
actiobzlssn.rename(columns={'Seasonal_act':'Seasonal_fcst'},inplace=True)

actiobzl=pd.merge(actiobzl,actiobzlssn,on='Month',how='left')
actiobzl['Seasonal']=np.where((actiobzl['Year']==cutoff.year)&(actiobzl['Quarter']>=cutoff.quarter),actiobzl['Seasonal_fcst'],actiobzl['Seasonal_act'])
actiobzl['Seasonal']=np.where(actiobzl['Year']>cutoff.year,actiobzl['Seasonal_fcst'],actiobzl['Seasonal'])


actiobzl['Vale+CSN_m']=actiobzl['Vale+CSN']*actiobzl['Seasonal']
actiobzl['Vale+CSN_m']=actiobzl['Vale+CSN_m']*1000
actiobzl['Brazil_extrp']=np.where((actiobzl['Year']>=cutoff.year)&(actiobzl['Month']>=cutoff.month),actiobzl['Brazil']/cutoff.day*monthrange(cutoff.year,cutoff.month)[1],actiobzl['Brazil'])
actiobzl['Date']=pd.to_datetime(dict(year=actiobzl['Year'],month=actiobzl['Month'],day=1))

plotiobzl=actiobzl[['Date','Brazil_extrp','Brazil','Vale+CSN_m']]
plotiobzl.set_index('Date',inplace=True)



fig=px.line(plotiobzl,width=1000,height=500,title='Brazil Iron Ore Export vs Miners Guidance')
fig.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
fig.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
fig.update_layout(template=draft_template)
st.plotly_chart(fig)


fcstiobzlssn=actiobzl.pivot_table(index='Month',columns='Year',values='Vale+CSN_m',aggfunc='sum')
ssnplot=px.line(fcstiobzlssn,width=1000,height=500,title='Brazil Majors Iron Ore Export Forecast Seasonality')
ssnplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
ssnplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
ssnplot['data'][-2]['line']['width']=5
ssnplot['data'][-2]['line']['color']='black'
ssnplot.update_layout(yaxis_title='Million Tonnes')
ssnplot.update_layout(template=draft_template)
st.plotly_chart(ssnplot)


rain=pd.read_excel('Data/Brazil Rainfall.xlsx')
staterain=rain.drop(columns=['ICAO','Station Name','Latitude','Longitude','Elevation (m)'])
staterain=staterain.groupby(by='Admin').mean()
staterain=staterain.transpose()
iorain=staterain[['Minas Gerais','Para']]
iorain['Minas Gerais+Para']=iorain['Minas Gerais']+iorain['Para']
iorain.rename(columns={'Para':'Para Rainfall'},inplace=True)
iorain.index=pd.to_datetime(iorain.index)
iorainact=actiobzl[['Date','Brazil']]
iorainact.rename(columns={'Brazil':'Brazil Export'},inplace=True)
iorainact.set_index('Date',inplace=True)

raincheck=pd.merge(iorain,iorainact,left_index=True,right_index=True,how='inner')

rev=st.radio('Reverse Rainfall?',options=['N','Y'],key='rev')
state=st.selectbox('Select Brazil State',options=['Minas Gerais+Para','Para Rainfall','Minas Gerais'])

subplot_fig = make_subplots(specs=[[{"secondary_y": True}]])
fig1=px.line(raincheck[state])
fig2=px.line(raincheck['Brazil Export'])
fig2.update_traces(yaxis='y2')
subplot_fig.add_traces(fig1.data + fig2.data)
subplot_fig.update_layout(title='Brazil Export vs Rainfall',width=1000,height=500)
subplot_fig.layout.xaxis.title='Date'
subplot_fig.layout.yaxis.title='mm'
subplot_fig.layout.yaxis2.title='mt'
if rev=='Y':
    subplot_fig.update_layout(
        yaxis = dict(autorange="reversed")
    )
    subplot_fig.layout.yaxis.title='mm (reversed axis)'
    subplot_fig.update_layout(title='Brazil Export vs Rainfall (rainfall axis reversed)',width=1000,height=500)
subplot_fig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))
subplot_fig.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
subplot_fig.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
subplot_fig.update_layout(template=draft_template)
st.plotly_chart(subplot_fig)

st.markdown('###### **----Brazil Iron Ore Segment Share**')
sizesplitiobzl=sizesplitio[sizesplitio['load_group']=='Brazil']
sizesplitiobzl=sizesplitiobzl.pivot_table(index=['Year','Month'],columns='segment',values='voy_intake_mt',aggfunc='sum')
sizesplitiobzl=sizesplitiobzl.div(sizesplitiobzl.sum(axis=1),axis=0)

sz1=st.selectbox('Select Vessel Size',options=['Capesize','Panamax','Supramax','Handysize'],key='sz1')
sz=sizesplitiobzl.pivot_table(index='Month',columns='Year',values=sz1,aggfunc='mean')

szplot=px.line(sz,width=1000,height=500,title='Brazil Iron Ore Export Size Split for '+sz1)
szplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
szplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
szplot['data'][-1]['line']['width']=5
szplot['data'][-1]['line']['color']='black'
szplot.update_layout(yaxis_title='Million Tonnes')
szplot.update_layout(template=draft_template)
st.plotly_chart(szplot)

st.markdown('###### **----Brazil Iron Ore Sailing Days**')
distanceiobzl=distanceio[distanceio['load_group']=='Brazil']
distanceiobzl=distanceiobzl.pivot_table(index=['Year','Month'],columns='segment',values='voy_sea_duration',aggfunc='mean')
distanceiobzl=distanceiobzl/60/24

sd=distanceiobzl.pivot_table(index='Month',columns='Year',values=sz1,aggfunc='mean')

sdplot=px.line(sd,width=1000,height=500,title='Brazil Iron Ore Export Sailing Days for '+sz1)
sdplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
sdplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
sdplot['data'][-1]['line']['width']=5
sdplot['data'][-1]['line']['color']='black'
sdplot.update_layout(yaxis_title='Million Tonnes')
sdplot.update_layout(template=draft_template)
st.plotly_chart(sdplot)



st.markdown('#### **----Australia**')

fcstioau=fcstio[['Year','Quarter','RT+BHP+FMG']]
actioau=actio[['Year','Month','Quarter','Australia']]

actioau_q=actioau.groupby(['Year','Quarter']).sum()
actioau_q.reset_index(inplace=True)
actioau_q=actioau_q[['Year','Quarter','Australia']]
actioau_q.rename(columns={'Australia':'Australia_q'},inplace=True)

actioau=pd.merge(actioau,actioau_q,on=['Year','Quarter'],how='outer')

fcstioau1=fcstioau.copy()
fcstioau2=fcstioau.copy()
fcstioau3=fcstioau.copy()

fcstioau1['Month']=fcstioau1['Quarter']*3-2
fcstioau2['Month']=fcstioau2['Quarter']*3-1
fcstioau3['Month']=fcstioau3['Quarter']*3

fcstioau123=pd.concat([fcstioau1,fcstioau2,fcstioau3])
fcstioau123.sort_values(by=['Year','Month'],ascending=True,inplace=True)

actioau=pd.merge(actioau,fcstioau123,on=['Year','Quarter','Month'],how='outer')
actioau['Seasonal_act']=np.where((actioau['Year']==cutoff.year)&(actioau['Quarter']>=cutoff.quarter),0,actioau['Australia']/actioau['Australia_q'])
actioau['Seasonal_act']=np.where(actioau['Year']>cutoff.year,0,actioau['Seasonal_act'])

actioaussn=actioau[['Year','Month','Seasonal_act']]
actioaussn=actioaussn[actioaussn['Year']==cutoff.year-1]
actioaussn.drop(columns='Year',inplace=True)
actioaussn.rename(columns={'Seasonal_act':'Seasonal_fcst'},inplace=True)
actioau=pd.merge(actioau,actioaussn,on='Month',how='left')

actioau['Seasonal']=np.where((actioau['Year']==cutoff.year)&(actioau['Quarter']>=cutoff.quarter),actioau['Seasonal_fcst'],actioau['Seasonal_act'])
actioau['Seasonal']=np.where(actioau['Year']>cutoff.year,actioau['Seasonal_fcst'],actioau['Seasonal'])

actioau['RT+BHP+FMG_m']=actioau['RT+BHP+FMG']*actioau['Seasonal']
actioau['RT+BHP+FMG_m']=actioau['RT+BHP+FMG_m']*1000
actioau['Australia_extrp']=np.where((actioau['Year']>=cutoff.year)&(actioau['Month']>=cutoff.month),actioau['Australia']/cutoff.day*monthrange(cutoff.year,cutoff.month)[1],actioau['Australia'])
actioau['Date']=pd.to_datetime(dict(year=actioau['Year'],month=actioau['Month'],day=1))

plotioau=actioau[['Date','Australia_extrp','Australia','RT+BHP+FMG_m']]
plotioau.set_index('Date',inplace=True)


fig=px.line(plotioau,width=1000,height=500,title='Australia Majors Iron Ore Export vs Miners Guidance')
fig.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
fig.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
fig.update_layout(template=draft_template)
st.plotly_chart(fig)

fcstioaussn=actioau.pivot_table(index='Month',columns='Year',values='RT+BHP+FMG_m',aggfunc='sum')
ssnplot=px.line(fcstioaussn,width=1000,height=500,title='Australia Iron Ore Export Forecast Seasonality')
ssnplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
ssnplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
ssnplot['data'][-2]['line']['width']=5
ssnplot['data'][-2]['line']['color']='black'
ssnplot.update_layout(yaxis_title='Million Tonnes')
ssnplot.update_layout(template=draft_template)
st.plotly_chart(ssnplot)

st.markdown('###### **----Australia Iron Ore Segment Share**')
sizesplitioau=sizesplitio[sizesplitio['load_group']=='Australia']
sizesplitioau=sizesplitioau.pivot_table(index=['Year','Month'],columns='segment',values='voy_intake_mt',aggfunc='sum')
sizesplitioau=sizesplitioau.div(sizesplitioau.sum(axis=1),axis=0)

sz2=st.selectbox('Select Vessel Size',options=['Capesize','Panamax','Supramax','Handysize'],key='sz2')
sz=sizesplitioau.pivot_table(index='Month',columns='Year',values=sz2,aggfunc='mean')

szplot=px.line(sz,width=1000,height=500,title='Australia Iron Ore Export Size Split for '+sz2)
szplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
szplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
szplot['data'][-1]['line']['width']=5
szplot['data'][-1]['line']['color']='black'
szplot.update_layout(yaxis_title='Million Tonnes')
szplot.update_layout(template=draft_template)
st.plotly_chart(szplot)

st.markdown('###### **----Australia Iron Ore Sailing Days**')
distanceioau=distanceio[distanceio['load_group']=='Australia']
distanceioau=distanceioau.pivot_table(index=['Year','Month'],columns='segment',values='voy_sea_duration',aggfunc='mean')
distanceioau=distanceioau/60/24

sd=distanceioau.pivot_table(index='Month',columns='Year',values=sz2,aggfunc='mean')

sdplot=px.line(sd,width=1000,height=500,title='Australia Iron Ore Export Sailing Days for '+sz2)
sdplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
sdplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
sdplot['data'][-1]['line']['width']=5
sdplot['data'][-1]['line']['color']='black'
sdplot.update_layout(yaxis_title='Million Tonnes')
sdplot.update_layout(template=draft_template)
st.plotly_chart(sdplot)



st.markdown('## **Soybeans Forecast**')

inputsb=pd.read_excel('Forecast/Soybeans Input.xlsx')

fcstsl2=st.selectbox('Select the Date When the Forecast is Made',options=inputsb['Forecast Date'].unique(),key='fcstsl2')

fcstsb=inputsb[inputsb['Forecast Date']=='2024Q2']


actsb=tf[tf['commodity_group']=='Soybeans']
sizesplitsb=actsb.copy()
distancesb=actsb.copy()
actsb=actsb[actsb['Year']>2015]
actsb=actsb.pivot_table(index=['Year','Month'],columns='load_group',values='voy_intake_mt',aggfunc='sum')
actsb.reset_index(inplace=True)


ctry1=st.selectbox('Select Export Country',options=['Brazil','USA','Argentina'],key='ctry1')

fcstsbctry=fcstsb[['Year','Month',ctry1]]
actsbctry=actsb[['Year','Month',ctry1]]
fcstsbctry.rename(columns={ctry1:ctry1+' FCST'},inplace=True)
actsbctry.rename(columns={ctry1:ctry1+' AIS'},inplace=True)


actsbctry=pd.merge(actsbctry,fcstsbctry,on=['Year','Month'],how='outer')
actsbctry[ctry1+' FCST']=actsbctry[ctry1+' FCST']*1000

actsbctry[ctry1+' AIS_extrp']=np.where((actsbctry['Year']>=cutoff.year)&(actsbctry['Month']>=cutoff.month),actsbctry[ctry1+' AIS']/cutoff.day*monthrange(cutoff.year,cutoff.month)[1],actsbctry[ctry1+' AIS'])
actsbctry['Date']=pd.to_datetime(dict(year=actsbctry['Year'],month=actsbctry['Month'],day=1))

plotsbctry=actsbctry[['Date',ctry1+' AIS_extrp',ctry1+' FCST',ctry1+' AIS']]
plotsbctry.set_index('Date',inplace=True)


fig=px.line(plotsbctry,width=1000,height=500,title=ctry1+' Soybeans Export')
fig.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
fig.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
fig.update_layout(template=draft_template)
st.plotly_chart(fig)

fcstsbctryssn=fcstsbctry.pivot_table(index='Month',columns='Year',values=ctry1+' FCST',aggfunc='sum')
fcstsbctryssn=fcstsbctryssn*1000
ssnplot=px.line(fcstsbctryssn,width=1000,height=500,title=ctry1+' Soybeans Export Forecast Seasonality')
ssnplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
ssnplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
ssnplot['data'][-2]['line']['width']=5
ssnplot['data'][-2]['line']['color']='black'
ssnplot.update_layout(yaxis_title='Million Tonnes')
ssnplot.update_layout(template=draft_template)
st.plotly_chart(ssnplot)

st.markdown('###### **----Segment Share**')
sizesplitsbctry=sizesplitsb[sizesplitsb['load_group']==ctry1]
sizesplitsbctry=sizesplitsbctry.pivot_table(index=['Year','Month'],columns='segment',values='voy_intake_mt',aggfunc='sum')
sizesplitsbctry=sizesplitsbctry.div(sizesplitsbctry.sum(axis=1),axis=0)

sz3=st.selectbox('Select Vessel Size',options=['Panamax','Supramax','Handysize','Capesize'],key='sz3')
sz=sizesplitsbctry.pivot_table(index='Month',columns='Year',values=sz3,aggfunc='mean')

szplot=px.line(sz,width=1000,height=500,title=ctry1+' Soybean Export Size Split for '+sz3)
szplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
szplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
szplot['data'][-1]['line']['width']=5
szplot['data'][-1]['line']['color']='black'
szplot.update_layout(yaxis_title='Million Tonnes')
szplot.update_layout(template=draft_template)
st.plotly_chart(szplot)


st.markdown('###### **----Sailing Days**')
distancesbctry=distancesb[distancesb['load_group']==ctry1]
distancesbctry=distancesbctry.pivot_table(index=['Year','Month'],columns='segment',values='voy_sea_duration',aggfunc='mean')
distancesbctry=distancesbctry/60/24

sd=distancesbctry.pivot_table(index='Month',columns='Year',values=sz3,aggfunc='mean')

sdplot=px.line(sd,width=1000,height=500,title=ctry1+' Soybean Export Sailing Days for '+sz3)
sdplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
sdplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
sdplot['data'][-1]['line']['width']=5
sdplot['data'][-1]['line']['color']='black'
sdplot.update_layout(yaxis_title='Million Tonnes')
sdplot.update_layout(template=draft_template)
st.plotly_chart(sdplot)



st.markdown('## **Corn Forecast**')

inputcn=pd.read_excel('Forecast/Corn Input.xlsx')

fcstsl3=st.selectbox('Select the Date When the Forecast is Made',options=inputcn['Forecast Date'].unique(),key='fcstsl3')
fcstcn=inputcn[inputcn['Forecast Date']=='2024Q2']


actcn=tf[tf['commodity_group']=='Corn']
sizesplitcn=actcn.copy()
distancecn=actcn.copy()
actcn=actcn[actcn['Year']>2015]
actcn=actcn.pivot_table(index=['Year','Month'],columns='load_group',values='voy_intake_mt',aggfunc='sum')
actcn.reset_index(inplace=True)


ctry2=st.selectbox('Select Export Country',options=['Brazil','USA','Argentina','Ukraine','EU'],key='ctry2')

fcstcnctry=fcstcn[['Year','Month',ctry2]]
actcnctry=actcn[['Year','Month',ctry2]]
fcstcnctry.rename(columns={ctry2:ctry2+' FCST'},inplace=True)
actcnctry.rename(columns={ctry2:ctry2+' AIS'},inplace=True)


actcnctry=pd.merge(actcnctry,fcstcnctry,on=['Year','Month'],how='outer')
actcnctry[ctry2+' FCST']=actcnctry[ctry2+' FCST']*1000

actcnctry[ctry2+' AIS_extrp']=np.where((actcnctry['Year']>=cutoff.year)&(actcnctry['Month']>=cutoff.month),actcnctry[ctry2+' AIS']/cutoff.day*monthrange(cutoff.year,cutoff.month)[1],actcnctry[ctry2+' AIS'])
actcnctry['Date']=pd.to_datetime(dict(year=actcnctry['Year'],month=actcnctry['Month'],day=1))

plotcnctry=actcnctry[['Date',ctry2+' AIS_extrp',ctry2+' FCST',ctry2+' AIS']]
plotcnctry.set_index('Date',inplace=True)


fig=px.line(plotcnctry,width=1000,height=500,title=ctry2+' Corn Export')
fig.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
fig.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
fig.update_layout(template=draft_template)
st.plotly_chart(fig)

fcstcnctryssn=fcstcnctry.pivot_table(index='Month',columns='Year',values=ctry2+' FCST',aggfunc='sum')
fcstcnctryssn=fcstcnctryssn*1000
ssnplot=px.line(fcstcnctryssn,width=1000,height=500,title=ctry2+' Corn Export Forecast Seasonality')
ssnplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
ssnplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
ssnplot['data'][-2]['line']['width']=5
ssnplot['data'][-2]['line']['color']='black'
ssnplot.update_layout(yaxis_title='Million Tonnes')
ssnplot.update_layout(template=draft_template)
st.plotly_chart(ssnplot)

st.markdown('###### **----Segment Share**')
sizesplitcnctry=sizesplitcn[sizesplitcn['load_group']==ctry2]
sizesplitcnctry=sizesplitcnctry.pivot_table(index=['Year','Month'],columns='segment',values='voy_intake_mt',aggfunc='sum')
sizesplitcnctry=sizesplitcnctry.div(sizesplitcnctry.sum(axis=1),axis=0)

sz4=st.selectbox('Select Vessel Size',options=['Panamax','Supramax','Handysize','Capesize'],key='sz4')
sz=sizesplitcnctry.pivot_table(index='Month',columns='Year',values=sz4,aggfunc='mean')

szplot=px.line(sz,width=1000,height=500,title=ctry2+' Corn Export Size Split for '+sz4)
szplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
szplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
szplot['data'][-1]['line']['width']=5
szplot['data'][-1]['line']['color']='black'
szplot.update_layout(yaxis_title='Million Tonnes')
szplot.update_layout(template=draft_template)
st.plotly_chart(szplot)

st.markdown('###### **----Sailing Days**')
distancecnctry=distancecn[distancecn['load_group']==ctry2]
distancecnctry=distancecnctry.pivot_table(index=['Year','Month'],columns='segment',values='voy_sea_duration',aggfunc='mean')
distancecnctry=distancecnctry/60/24

sd=distancecnctry.pivot_table(index='Month',columns='Year',values=sz4,aggfunc='mean')

sdplot=px.line(sd,width=1000,height=500,title=ctry2+' Corn Export Sailing Days for '+sz4)
sdplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
sdplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
sdplot['data'][-1]['line']['width']=5
sdplot['data'][-1]['line']['color']='black'
sdplot.update_layout(yaxis_title='Million Tonnes')
sdplot.update_layout(template=draft_template)
st.plotly_chart(sdplot)


st.markdown('## **Wheat Forecast**')

inputwh=pd.read_excel('Forecast/Wheat Input.xlsx')

fcstsl4=st.selectbox('Select the Date When the Forecast is Made',options=inputwh['Forecast Date'].unique(),key='fcstsl4')

fcstwh=inputwh[inputwh['Forecast Date']=='2024Q2']


actwh=tf[tf['commodity_group']=='Wheat']
sizesplitwh=actwh.copy()
distancewh=actwh.copy()
actwh=actwh[actwh['Year']>2015]
actwh=actwh.pivot_table(index=['Year','Month'],columns='load_group',values='voy_intake_mt',aggfunc='sum')
actwh.reset_index(inplace=True)


ctry=st.selectbox('Select Export Country',options=['Australia','Argentina','Canada','Russia','USA','Ukraine','EU'],key='ctry')

fcstwhctry=fcstwh[['Year','Month',ctry]]
actwhctry=actwh[['Year','Month',ctry]]
fcstwhctry.rename(columns={ctry:ctry+' FCST'},inplace=True)
actwhctry.rename(columns={ctry:ctry+' AIS'},inplace=True)


actwhctry=pd.merge(actwhctry,fcstwhctry,on=['Year','Month'],how='outer')
actwhctry[ctry+' FCST']=actwhctry[ctry+' FCST']*1000

actwhctry[ctry+' AIS_extrp']=np.where((actwhctry['Year']>=cutoff.year)&(actwhctry['Month']>=cutoff.month),actwhctry[ctry+' AIS']/cutoff.day*monthrange(cutoff.year,cutoff.month)[1],actwhctry[ctry+' AIS'])
actwhctry['Date']=pd.to_datetime(dict(year=actwhctry['Year'],month=actwhctry['Month'],day=1))

plotwhctry=actwhctry[['Date',ctry+' AIS_extrp',ctry+' FCST',ctry+' AIS']]
plotwhctry.set_index('Date',inplace=True)


fig=px.line(plotwhctry,width=1000,height=500,title=ctry+' Wheat Export')
fig.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
fig.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
fig.update_layout(template=draft_template)
st.plotly_chart(fig)

fcstwhctryssn=fcstwhctry.pivot_table(index='Month',columns='Year',values=ctry+' FCST',aggfunc='sum')
fcstwhctryssn=fcstwhctryssn*1000
ssnplot=px.line(fcstwhctryssn,width=1000,height=500,title=ctry+' Wheat Export Forecast Seasonality')
ssnplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
ssnplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
ssnplot['data'][-2]['line']['width']=5
ssnplot['data'][-2]['line']['color']='black'
ssnplot.update_layout(yaxis_title='Million Tonnes')
ssnplot.update_layout(template=draft_template)
st.plotly_chart(ssnplot)

st.markdown('###### **----Segment Share**')
sizesplitwhctry=sizesplitwh[sizesplitwh['load_group']==ctry]
sizesplitwhctry=sizesplitwhctry.pivot_table(index=['Year','Month'],columns='segment',values='voy_intake_mt',aggfunc='sum')
sizesplitwhctry=sizesplitwhctry.div(sizesplitwhctry.sum(axis=1),axis=0)

sz5=st.selectbox('Select Vessel Size',options=['Panamax','Supramax','Handysize','Capesize'],key='sz5')
sz=sizesplitwhctry.pivot_table(index='Month',columns='Year',values=sz5,aggfunc='mean')

szplot=px.line(sz,width=1000,height=500,title=ctry+' Wheat Export Size Split for '+sz5)
szplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
szplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
szplot['data'][-1]['line']['width']=5
szplot['data'][-1]['line']['color']='black'
szplot.update_layout(yaxis_title='Million Tonnes')
szplot.update_layout(template=draft_template)
st.plotly_chart(szplot)

st.markdown('###### **----Sailing Days**')
distancewhctry=distancewh[distancewh['load_group']==ctry]
distancewhctry=distancewhctry.pivot_table(index=['Year','Month'],columns='segment',values='voy_sea_duration',aggfunc='mean')
distancewhctry=distancewhctry/60/24

sd=distancewhctry.pivot_table(index='Month',columns='Year',values=sz5,aggfunc='mean')

sdplot=px.line(sd,width=1000,height=500,title=ctry+' Wheat Export Sailing Days for '+sz5)
sdplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
sdplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
sdplot['data'][-1]['line']['width']=5
sdplot['data'][-1]['line']['color']='black'
sdplot.update_layout(yaxis_title='Million Tonnes')
sdplot.update_layout(template=draft_template)
st.plotly_chart(sdplot)


st.markdown('## **Sugar Forecast**')

inputsg=pd.read_excel('Forecast/Sugar Input.xlsx')

fcstsl5=st.selectbox('Select the Date When the Forecast is Made',options=inputwh['Forecast Date'].unique(),key='fcstsl5')

fcstsg=inputsg[inputsg['Forecast Date']=='2024Q2']


actsg=tf[tf['commodity_group']=='Sugar']
sizesplitsg=actsg.copy()
distancesg=actsg.copy()
actsg=actsg[actsg['Year']>2015]
actsg=actsg.pivot_table(index=['Year','Month'],columns='load_group',values='voy_intake_mt',aggfunc='sum')
actsg.reset_index(inplace=True)


ctry4=st.selectbox('Select Export Country',options=['Brazil'],key='ctry4')

fcstsgctry=fcstsg[['Year','Month',ctry4]]
actsgctry=actsg[['Year','Month',ctry4]]
fcstsgctry.rename(columns={ctry4:ctry4+' FCST'},inplace=True)
actsgctry.rename(columns={ctry4:ctry4+' AIS'},inplace=True)


actsgctry=pd.merge(actsgctry,fcstsgctry,on=['Year','Month'],how='outer')
actsgctry[ctry4+' FCST']=actsgctry[ctry4+' FCST']*1000

actsgctry[ctry4+' AIS_extrp']=np.where((actsgctry['Year']>=cutoff.year)&(actsgctry['Month']>=cutoff.month),actsgctry[ctry4+' AIS']/cutoff.day*monthrange(cutoff.year,cutoff.month)[1],actsgctry[ctry4+' AIS'])
actsgctry['Date']=pd.to_datetime(dict(year=actsgctry['Year'],month=actsgctry['Month'],day=1))

plotsgctry=actsgctry[['Date',ctry4+' AIS_extrp',ctry4+' FCST',ctry4+' AIS']]
plotsgctry.set_index('Date',inplace=True)


fig=px.line(plotsgctry,width=1000,height=500,title=ctry4+' Sugar Export')
fig.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
fig.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
fig.update_layout(template=draft_template)
st.plotly_chart(fig)

fcstsgctryssn=fcstsgctry.pivot_table(index='Month',columns='Year',values=ctry4+' FCST',aggfunc='sum')
fcstsgctryssn=fcstsgctryssn*1000
ssnplot=px.line(fcstsgctryssn,width=1000,height=500,title=ctry4+' Sugar Export Forecast Seasonality')
ssnplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
ssnplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
ssnplot['data'][-2]['line']['width']=5
ssnplot['data'][-2]['line']['color']='black'
ssnplot.update_layout(yaxis_title='Million Tonnes')
ssnplot.update_layout(template=draft_template)
st.plotly_chart(ssnplot)

st.markdown('###### **----Segment Share**')
sizesplitsgctry=sizesplitsg[sizesplitsg['load_group']==ctry4]
sizesplitsgctry=sizesplitsgctry.pivot_table(index=['Year','Month'],columns='segment',values='voy_intake_mt',aggfunc='sum')
sizesplitsgctry=sizesplitsgctry.div(sizesplitsgctry.sum(axis=1),axis=0)

sz6=st.selectbox('Select Vessel Size',options=['Panamax','Supramax','Handysize','Capesize'],key='sz6')
sz=sizesplitsgctry.pivot_table(index='Month',columns='Year',values=sz5,aggfunc='mean')

szplot=px.line(sz,width=1000,height=500,title=ctry4+' Sugar Export Size Split for '+sz6)
szplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
szplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
szplot['data'][-1]['line']['width']=5
szplot['data'][-1]['line']['color']='black'
szplot.update_layout(yaxis_title='Million Tonnes')
szplot.update_layout(template=draft_template)
st.plotly_chart(szplot)

st.markdown('###### **----Sailing Days**')
distancesgctry=distancesg[distancesg['load_group']==ctry4]
distancesgctry=distancesgctry.pivot_table(index=['Year','Month'],columns='segment',values='voy_sea_duration',aggfunc='mean')
distancesgctry=distancesgctry/60/24

sd=distancesgctry.pivot_table(index='Month',columns='Year',values=sz5,aggfunc='mean')

sdplot=px.line(sd,width=1000,height=500,title=ctry4+' Sugar Export Sailing Days for '+sz5)
sdplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
sdplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
sdplot['data'][-1]['line']['width']=5
sdplot['data'][-1]['line']['color']='black'
sdplot.update_layout(yaxis_title='Million Tonnes')
sdplot.update_layout(template=draft_template)
st.plotly_chart(sdplot)






st.markdown('## **Summary**')

fcstiobzl_=actiobzl[['Year','Month','Vale+CSN_m']]
fcstioau_=actioau[['Year','Month','RT+BHP+FMG_m']]

fcstiobzl_=fcstiobzl_.set_index(['Year','Month'])
fcstioau_=fcstioau_.set_index(['Year','Month'])

fcstiobzl_.rename(columns={'Vale+CSN_m':'Brazil IO Majors FCST'},inplace=True)
fcstioau_.rename(columns={'RT+BHP+FMG_m':'Australia IO Majors FCST'},inplace=True)

fcstsb_=fcstsb.drop(columns={'Forecast Date','Quarter'})
fcstsb_.set_index(['Year','Month'],inplace=True)
fcstsb_.columns=[str(col)+' SBS FCST' for col in fcstsb_.columns]
fcstsb_=fcstsb_*1000

fcstcn_=fcstcn.drop(columns={'Forecast Date','Quarter'})
fcstcn_.set_index(['Year','Month'],inplace=True)
fcstcn_.columns=[str(col)+' CORN FCST' for col in fcstcn_.columns]
fcstcn_=fcstcn_*1000


fcstwh_=fcstwh.drop(columns={'Forecast Date','Quarter'})
fcstwh_.set_index(['Year','Month'],inplace=True)
fcstwh_.columns=[str(col)+' WHEAT FCST' for col in fcstwh_.columns]
fcstwh_=fcstwh_*1000


fcstsg_=fcstsg.drop(columns={'Forecast Date','Quarter'})
fcstsg_.set_index(['Year','Month'],inplace=True)
fcstsg_.columns=[str(col)+' SUGAR FCST' for col in fcstsg_.columns]
fcstsg_=fcstsg_*1000


sumup=pd.merge(fcstiobzl_,fcstioau_,left_index=True,right_index=True,how='outer')
sumup=pd.merge(sumup,fcstsb_,left_index=True,right_index=True,how='outer')
sumup=pd.merge(sumup,fcstcn_,left_index=True,right_index=True,how='outer')
sumup=pd.merge(sumup,fcstwh_,left_index=True,right_index=True,how='outer')
sumup=pd.merge(sumup,fcstsg_,left_index=True,right_index=True,how='outer')

sumup.reset_index(inplace=True)
sumup['Date']=pd.to_datetime(dict(year=sumup['Year'],month=sumup['Month'],day=1))
sumup.set_index('Date',inplace=True)
sumup.drop(columns=['Year','Month'],inplace=True)

caperef=tf[tf['segment']=='Capesize']
pmxref=tf[tf['segment']=='Panamax']
smxref=tf[tf['segment']=='Supramax']
ttlref=tf.copy()

ttlsplit=ttlref.pivot_table(index=['Year','Month'],columns=['commodity_group','load_group'],values='voy_intake_mt',aggfunc='sum')
capesplit=caperef.pivot_table(index=['Year','Month'],columns=['commodity_group','load_group'],values='voy_intake_mt',aggfunc='sum')
pmxsplit=pmxref.pivot_table(index=['Year','Month'],columns=['commodity_group','load_group'],values='voy_intake_mt',aggfunc='sum')
smxsplit=smxref.pivot_table(index=['Year','Month'],columns=['commodity_group','load_group'],values='voy_intake_mt',aggfunc='sum')
capesplit=capesplit/ttlsplit
pmxsplit=pmxsplit/ttlsplit
smxsplit=smxsplit/ttlsplit


capesplitio=capesplit['Iron Ore']
capesplitio=capesplitio[['Brazil','Australia']]
capesplitio.columns=[str(col)+' IO Majors FCST' for col in capesplitio.columns]
capesplitsb=capesplit['Soybeans']
capesplitsb=capesplitsb[['Brazil','Argentina','USA']]
capesplitsb.columns=[str(col)+' SBS FCST' for col in capesplitsb.columns]
capesplitcn=capesplit['Corn']
capesplitcn=capesplitcn[['Brazil','Argentina','USA','Ukraine','EU']]
capesplitcn.columns=[str(col)+' CORN FCST' for col in capesplitcn.columns]
capesplitwh=capesplit['Wheat']
capesplitwh=capesplitwh[['Australia','Argentina','USA','Canada','Ukraine','Russia','EU']]
capesplitwh.columns=[str(col)+' WHEAT FCST' for col in capesplitwh.columns]
capesplitsg=capesplit['Sugar']
capesplitsg=capesplitsg[['Brazil']]
capesplitsg.columns=[str(col)+' WHEAT FCST' for col in capesplitsg.columns]
capesplit=pd.merge(capesplitio,capesplitsb,left_index=True,right_index=True,how='outer')
capesplit=pd.merge(capesplit,capesplitcn,left_index=True,right_index=True,how='outer')
capesplit=pd.merge(capesplit,capesplitwh,left_index=True,right_index=True,how='outer')
capesplit=pd.merge(capesplit,capesplitsg,left_index=True,right_index=True,how='outer')
capesplit.fillna(inplace=True,method='ffill')
capesplit.fillna(inplace=True,method='bfill')
capesplit.reset_index(inplace=True)
capesplit.index=pd.to_datetime(dict(year=capesplit['Year'],month=capesplit['Month'],day=1))
capesplit=capesplit[capesplit['Year']>2015]
capesplit=capesplit.reindex(sumup.index)
capesplit.drop(columns=['Year','Month'],inplace=True)
for clm in capesplit.columns:
    capesplit[clm]=np.where(capesplit[clm].index>cutoff,capesplit[clm].shift(12),capesplit[clm])
    capesplit[clm]=np.where(capesplit[clm].index.year>curryear,capesplit[clm].shift(12),capesplit[clm])
capesplit.fillna(0,inplace=True)


pmxsplitio=pmxsplit['Iron Ore']
pmxsplitio=pmxsplitio[['Brazil','Australia']]
pmxsplitio.columns=[str(col)+' IO Majors FCST' for col in pmxsplitio.columns]
pmxsplitsb=pmxsplit['Soybeans']
pmxsplitsb=pmxsplitsb[['Brazil','Argentina','USA']]
pmxsplitsb.columns=[str(col)+' SBS FCST' for col in pmxsplitsb.columns]
pmxsplitcn=pmxsplit['Corn']
pmxsplitcn=pmxsplitcn[['Brazil','Argentina','USA','Ukraine','EU']]
pmxsplitcn.columns=[str(col)+' CORN FCST' for col in pmxsplitcn.columns]
pmxsplitwh=pmxsplit['Wheat']
pmxsplitwh=pmxsplitwh[['Australia','Argentina','USA','Canada','Ukraine','Russia','EU']]
pmxsplitwh.columns=[str(col)+' WHEAT FCST' for col in pmxsplitwh.columns]
pmxsplitsg=pmxsplit['Sugar']
pmxsplitsg=pmxsplitsg[['Brazil']]
pmxsplitsg.columns=[str(col)+' SUGAR FCST' for col in pmxsplitsg.columns]
pmxsplit=pd.merge(pmxsplitio,pmxsplitsb,left_index=True,right_index=True,how='outer')
pmxsplit=pd.merge(pmxsplit,pmxsplitcn,left_index=True,right_index=True,how='outer')
pmxsplit=pd.merge(pmxsplit,pmxsplitwh,left_index=True,right_index=True,how='outer')
pmxsplit=pd.merge(pmxsplit,pmxsplitsg,left_index=True,right_index=True,how='outer')
pmxsplit.fillna(inplace=True,method='ffill')
pmxsplit.fillna(inplace=True,method='bfill')
pmxsplit.reset_index(inplace=True)
pmxsplit.index=pd.to_datetime(dict(year=pmxsplit['Year'],month=pmxsplit['Month'],day=1))
pmxsplit=pmxsplit[pmxsplit['Year']>2015]
pmxsplit=pmxsplit.reindex(sumup.index)
pmxsplit.drop(columns=['Year','Month'],inplace=True)
for clm in pmxsplit.columns:
    pmxsplit[clm]=np.where(pmxsplit[clm].index>cutoff,pmxsplit[clm].shift(12),pmxsplit[clm])
    pmxsplit[clm]=np.where(pmxsplit[clm].index.year>curryear,pmxsplit[clm].shift(12),pmxsplit[clm])
pmxsplit.fillna(0,inplace=True)


smxsplitio=smxsplit['Iron Ore']
smxsplitio=smxsplitio[['Brazil','Australia']]
smxsplitio.columns=[str(col)+' IO Majors FCST' for col in smxsplitio.columns]
smxsplitsb=smxsplit['Soybeans']
smxsplitsb=smxsplitsb[['Brazil','Argentina','USA']]
smxsplitsb.columns=[str(col)+' SBS FCST' for col in smxsplitsb.columns]
smxsplitcn=smxsplit['Corn']
smxsplitcn=smxsplitcn[['Brazil','Argentina','USA','Ukraine','EU']]
smxsplitcn.columns=[str(col)+' CORN FCST' for col in smxsplitcn.columns]
smxsplitwh=smxsplit['Wheat']
smxsplitwh=smxsplitwh[['Australia','Argentina','USA','Canada','Ukraine','Russia','EU']]
smxsplitwh.columns=[str(col)+' WHEAT FCST' for col in smxsplitwh.columns]
smxsplitsg=smxsplit['Sugar']
smxsplitsg=smxsplitsg[['Brazil']]
smxsplitsg.columns=[str(col)+' SUGAR FCST' for col in smxsplitsg.columns]
smxsplit=pd.merge(smxsplitio,smxsplitsb,left_index=True,right_index=True,how='outer')
smxsplit=pd.merge(smxsplit,smxsplitcn,left_index=True,right_index=True,how='outer')
smxsplit=pd.merge(smxsplit,smxsplitwh,left_index=True,right_index=True,how='outer')
smxsplit=pd.merge(smxsplit,smxsplitsg,left_index=True,right_index=True,how='outer')
smxsplit.fillna(inplace=True,method='ffill')
smxsplit.fillna(inplace=True,method='bfill')
smxsplit.reset_index(inplace=True)
smxsplit.index=pd.to_datetime(dict(year=smxsplit['Year'],month=smxsplit['Month'],day=1))
smxsplit=smxsplit[smxsplit['Year']>2015]
smxsplit=smxsplit.reindex(sumup.index)
smxsplit.drop(columns=['Year','Month'],inplace=True)
for clm in smxsplit.columns:
    smxsplit[clm]=np.where(smxsplit[clm].index>cutoff,smxsplit[clm].shift(12),smxsplit[clm])
    smxsplit[clm]=np.where(smxsplit[clm].index.year>curryear,smxsplit[clm].shift(12),smxsplit[clm])
smxsplit.fillna(0,inplace=True)


capedays=caperef.pivot_table(index=['Year','Month'],columns=['commodity_group','load_group'],values='voy_sea_duration',aggfunc='mean')
capedays=capedays/60/24
capedaysio=capedays['Iron Ore']
capedaysio=capedaysio[['Brazil','Australia']]
capedaysio.columns=[str(col)+' IO Majors FCST' for col in capedaysio.columns]
capedayssb=capedays['Soybeans']
capedayssb['Argentina']=25
capedayssb['USA']=25
capedayssb=capedayssb[['Brazil','Argentina','USA']]
capedayssb.columns=[str(col)+' SBS FCST' for col in capedayssb.columns]
capedayscn=capedays['Corn']
capedayscn['Argentina']=25
capedayscn['Ukraine']=25
capedayscn['EU']=25
capedayscn=capedayscn[['Brazil','Argentina','USA','Ukraine','EU']]
capedayscn.columns=[str(col)+' CORN FCST' for col in capedayscn.columns]
capedayswh=capedays['Wheat']
capedayswh['Australia']=25
capedayswh['Argentina']=25
capedayswh['USA']=25
capedayswh['Canada']=25
capedayswh['Ukraine']=25
capedayswh['EU']=25
capedayswh=capedayswh[['Australia','Argentina','USA','Canada','Ukraine','Russia','EU']]
capedayssg=capedays['Sugar']
capedayssg['Brazil']=25
capedayssg=capedayssg[['Brazil']]
capedayssg.columns=[str(col)+' SUGAR FCST' for col in capedayssg.columns]
capedays=pd.merge(capedaysio,capedayssb,left_index=True,right_index=True,how='outer')
capedays=pd.merge(capedays,capedayscn,left_index=True,right_index=True,how='outer')
capedays=pd.merge(capedays,capedayswh,left_index=True,right_index=True,how='outer')
capedays=pd.merge(capedays,capedayssg,left_index=True,right_index=True,how='outer')
capedays.fillna(inplace=True,method='ffill')
capedays.fillna(inplace=True,method='bfill')
capedays.reset_index(inplace=True)
capedays.index=pd.to_datetime(dict(year=capedays['Year'],month=capedays['Month'],day=1))
capedays=capedays[capedays['Year']>2015]
capedays=capedays.reindex(sumup.index)
capedays.drop(columns=['Year','Month'],inplace=True)
for clm in capedays.columns:
    capedays[clm]=np.where(capedays[clm].index>cutoff,capedays[clm].shift(12),capedays[clm])
    capedays[clm]=np.where(capedays[clm].index.year>curryear,capedays[clm].shift(12),capedays[clm])



pmxdays=pmxref.pivot_table(index=['Year','Month'],columns=['commodity_group','load_group'],values='voy_sea_duration',aggfunc='mean')
pmxdays=pmxdays/60/24
pmxdaysio=pmxdays['Iron Ore']
pmxdaysio=pmxdaysio[['Brazil','Australia']]
pmxdaysio.columns=[str(col)+' IO Majors FCST' for col in pmxdaysio.columns]
pmxdayssb=pmxdays['Soybeans']
pmxdayssb=pmxdayssb[['Brazil','Argentina','USA']]
pmxdayssb.columns=[str(col)+' SBS FCST' for col in pmxdayssb.columns]
pmxdayscn=pmxdays['Corn']
pmxdayscn=pmxdayscn[['Brazil','Argentina','USA','Ukraine','EU']]
pmxdayscn.columns=[str(col)+' CORN FCST' for col in pmxdayscn.columns]
pmxdayswh=pmxdays['Wheat']
pmxdayswh=pmxdayswh[['Australia','Argentina','USA','Canada','Ukraine','Russia','EU']]
pmxdayswh.columns=[str(col)+' WHEAT FCST' for col in pmxdayswh.columns]
pmxdayssg=pmxdays['Sugar']
pmxdayssg=pmxdayssg[['Brazil']]
pmxdayssg.columns=[str(col)+' SUGAR FCST' for col in pmxdayssg.columns]
pmxdays=pd.merge(pmxdaysio,pmxdayssb,left_index=True,right_index=True,how='outer')
pmxdays=pd.merge(pmxdays,pmxdayscn,left_index=True,right_index=True,how='outer')
pmxdays=pd.merge(pmxdays,pmxdayswh,left_index=True,right_index=True,how='outer')
pmxdays=pd.merge(pmxdays,pmxdayssg,left_index=True,right_index=True,how='outer')
pmxdays.fillna(inplace=True,method='ffill')
pmxdays.fillna(inplace=True,method='bfill')
pmxdays.reset_index(inplace=True)
pmxdays.index=pd.to_datetime(dict(year=pmxdays['Year'],month=pmxdays['Month'],day=1))
pmxdays=pmxdays[pmxdays['Year']>2015]
pmxdays=pmxdays.reindex(sumup.index)
pmxdays.drop(columns=['Year','Month'],inplace=True)
for clm in pmxdays.columns:
    pmxdays[clm]=np.where(pmxdays[clm].index>cutoff,pmxdays[clm].shift(12),pmxdays[clm])
    pmxdays[clm]=np.where(pmxdays[clm].index.year>curryear,pmxdays[clm].shift(12),pmxdays[clm])


smxdays=smxref.pivot_table(index=['Year','Month'],columns=['commodity_group','load_group'],values='voy_sea_duration',aggfunc='mean')
smxdays=smxdays/60/24
smxdaysio=smxdays['Iron Ore']
smxdaysio=smxdaysio[['Brazil','Australia']]
smxdaysio.columns=[str(col)+' IO Majors FCST' for col in smxdaysio.columns]
smxdayssb=smxdays['Soybeans']
smxdayssb=smxdayssb[['Brazil','Argentina','USA']]
smxdayssb.columns=[str(col)+' SBS FCST' for col in smxdayssb.columns]
smxdayscn=smxdays['Corn']
smxdayscn=smxdayscn[['Brazil','Argentina','USA','Ukraine','EU']]
smxdayscn.columns=[str(col)+' CORN FCST' for col in smxdayscn.columns]
smxdayswh=smxdays['Wheat']
smxdayswh=smxdayswh[['Australia','Argentina','USA','Canada','Ukraine','Russia','EU']]
smxdayswh.columns=[str(col)+' WHEAT FCST' for col in smxdayswh.columns]
smxdayssg=smxdays['Sugar']
smxdayssg=smxdayssg[['Brazil']]
smxdayssg.columns=[str(col)+' SUGAR FCST' for col in smxdayssg.columns]
smxdays=pd.merge(smxdaysio,smxdayssb,left_index=True,right_index=True,how='outer')
smxdays=pd.merge(smxdays,smxdayscn,left_index=True,right_index=True,how='outer')
smxdays=pd.merge(smxdays,smxdayswh,left_index=True,right_index=True,how='outer')
smxdays=pd.merge(smxdays,smxdayssg,left_index=True,right_index=True,how='outer')
smxdays.fillna(inplace=True,method='ffill')
smxdays.fillna(inplace=True,method='bfill')
smxdays.reset_index(inplace=True)
smxdays.index=pd.to_datetime(dict(year=smxdays['Year'],month=smxdays['Month'],day=1))
smxdays=smxdays[smxdays['Year']>2015]
smxdays=smxdays.reindex(sumup.index)
smxdays.drop(columns=['Year','Month'],inplace=True)
for clm in smxdays.columns:
    smxdays[clm]=np.where(smxdays[clm].index>cutoff,smxdays[clm].shift(12),smxdays[clm])
    smxdays[clm]=np.where(smxdays[clm].index.year>curryear,smxdays[clm].shift(12),smxdays[clm])


capetons=sumup*capesplit
pmxtons=sumup*pmxsplit
smxtons=sumup*smxsplit

capetondays=sumup*capesplit*capedays
pmxtondays=sumup*pmxsplit*pmxdays
smxtondays=sumup*smxsplit*smxdays



st.markdown('#### **----Iron Ore**')
iore=sumup[['Brazil IO Majors FCST','Australia IO Majors FCST']]

yrsl1=st.multiselect('Select Years',options=iore.index.year.unique(),default=np.arange(curryear-4,curryear+1),key='year1')

ioresl=iore[iore.index.year.isin(yrsl1)]
freq1=st.radio('Select Frequency',options=['Monthly','Quarterly','Yearly'],key='freq1')

if freq1=='Quarterly':
    ioresl=ioresl.resample('Q').sum()
    ioresl.index=ioresl.index.year.astype(str)+'_Q'+ioresl.index.quarter.astype(str)

if freq1=='Yearly':
    ioresl=ioresl.resample('Y').sum()
    ioresl.index=ioresl.index.year.astype(str)

fig_iore=px.bar(ioresl,width=1000,height=500,title='Export Seaborne Trade Volume Outlook for Iron Ore')
fig_iore.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
fig_iore.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
fig_iore.update_layout(template=draft_template)
st.plotly_chart(fig_iore)


st.markdown('#### **----Oilseeds and Grains**')
agri=sumup[['Brazil SBS FCST','USA SBS FCST','Argentina SBS FCST',
            'Brazil CORN FCST','USA CORN FCST','Argentina CORN FCST','Ukraine CORN FCST','EU CORN FCST',
            'Australia WHEAT FCST','Argentina WHEAT FCST','Canada WHEAT FCST','Russia WHEAT FCST','USA WHEAT FCST','Ukraine WHEAT FCST','EU WHEAT FCST',
            'Brazil SUGAR FCST']]

yrsl2=st.multiselect('Select Years',options=agri.index.year.unique(),default=np.arange(curryear-4,curryear+1),key='year2')

agrisl=agri[agri.index.year.isin(yrsl2)]
freq2=st.radio('Select Frequency',options=['Monthly','Quarterly','Yearly'],key='freq2')

if freq2=='Quarterly':
    agrisl=agrisl.resample('Q').sum()
    agrisl.index=agrisl.index.year.astype(str)+'_Q'+agrisl.index.quarter.astype(str)

if freq2=='Yearly':
    agrisl=agrisl.resample('Y').sum()
    agrisl.index=agrisl.index.year.astype(str)


fig_argi=px.bar(agrisl,width=1000,height=500,title='Export Seaborne Trade Volume Outlook for Oilseeds and Grains')
fig_argi.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
fig_argi.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size-3,xaxis=plot_axis,yaxis=plot_axis)
fig_argi.update_layout(template=draft_template)
st.plotly_chart(fig_argi)


st.markdown('#### **----Capesize**')
yrsl3=st.multiselect('Select Years',options=capetons.index.year.unique(),default=np.arange(curryear-4,curryear+1),key='year3')

capetonssl=capetons[capetons.index.year.isin(yrsl3)]
freq3=st.radio('Select Frequency',options=['Monthly','Quarterly','Yearly'],key='freq3')

if freq3=='Quarterly':
    capetonssl=capetonssl.resample('Q').sum()
    capetonssl.index=capetonssl.index.year.astype(str)+'_Q'+capetonssl.index.quarter.astype(str)

if freq3=='Yearly':
    capetonssl=capetonssl.resample('Y').sum()
    capetonssl.index=capetonssl.index.year.astype(str)


fig_cape=px.bar(capetonssl,width=1000,height=500,title='Capesize Tonnes Outlook')
fig_cape.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
fig_cape.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size-3,xaxis=plot_axis,yaxis=plot_axis)
fig_cape.update_layout(template=draft_template)
st.plotly_chart(fig_cape)

capetondayssl=capetondays[capetondays.index.year.isin(yrsl3)]

if freq3=='Quarterly':
    capetondayssl=capetondayssl.resample('Q').sum()
    capetondayssl.index=capetondayssl.index.year.astype(str)+'_Q'+capetondayssl.index.quarter.astype(str)

if freq3=='Yearly':
    capetondayssl=capetondayssl.resample('Y').sum()
    capetondayssl.index=capetondayssl.index.year.astype(str)


fig_cape=px.bar(capetondayssl,width=1000,height=500,title='Capesize Tondays Outlook')
fig_cape.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
fig_cape.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size-3,xaxis=plot_axis,yaxis=plot_axis)
fig_cape.update_layout(template=draft_template)
st.plotly_chart(fig_cape)

st.markdown('#### **----Panamax**')
yrsl4=st.multiselect('Select Years',options=pmxtons.index.year.unique(),default=np.arange(curryear-4,curryear+1),key='year4')

pmxtonssl=pmxtons[pmxtons.index.year.isin(yrsl4)]
freq4=st.radio('Select Frequency',options=['Monthly','Quarterly','Yearly'],key='freq4')

if freq4=='Quarterly':
    pmxtonssl=pmxtonssl.resample('Q').sum()
    pmxtonssl.index=pmxtonssl.index.year.astype(str)+'_Q'+pmxtonssl.index.quarter.astype(str)

if freq4=='Yearly':
    pmxtonssl=pmxtonssl.resample('Y').sum()
    pmxtonssl.index=pmxtonssl.index.year.astype(str)


fig_pmx=px.bar(pmxtonssl,width=1000,height=500,title='Panamax Tonnes Outlook')
fig_pmx.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
fig_pmx.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size-3,xaxis=plot_axis,yaxis=plot_axis)
fig_pmx.update_layout(template=draft_template)
st.plotly_chart(fig_pmx)

pmxtondayssl=pmxtondays[pmxtondays.index.year.isin(yrsl4)]

if freq4=='Quarterly':
    pmxtondayssl=pmxtondayssl.resample('Q').sum()
    pmxtondayssl.index=pmxtondayssl.index.year.astype(str)+'_Q'+pmxtondayssl.index.quarter.astype(str)

if freq4=='Yearly':
    pmxtondayssl=pmxtondayssl.resample('Y').sum()
    pmxtondayssl.index=pmxtondayssl.index.year.astype(str)


fig_pmx=px.bar(pmxtondayssl,width=1000,height=500,title='Panamax Tondays Outlook')
fig_pmx.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
fig_pmx.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size-3,xaxis=plot_axis,yaxis=plot_axis)
fig_pmx.update_layout(template=draft_template)
st.plotly_chart(fig_pmx)


st.markdown('#### **----Supramax**')
yrsl5=st.multiselect('Select Years',options=smxtons.index.year.unique(),default=np.arange(curryear-4,curryear+1),key='year5')

smxtonssl=smxtons[smxtons.index.year.isin(yrsl5)]
freq5=st.radio('Select Frequency',options=['Monthly','Quarterly','Yearly'],key='freq5')

if freq5=='Quarterly':
    smxtonssl=smxtonssl.resample('Q').sum()
    smxtonssl.index=smxtonssl.index.year.astype(str)+'_Q'+smxtonssl.index.quarter.astype(str)

if freq5=='Yearly':
    smxtonssl=smxtonssl.resample('Y').sum()
    smxtonssl.index=smxtonssl.index.year.astype(str)


fig_smx=px.bar(smxtonssl,width=1000,height=500,title='Supramax Tonnes Outlook')
fig_smx.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
fig_smx.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size-3,xaxis=plot_axis,yaxis=plot_axis)
fig_smx.update_layout(template=draft_template)
st.plotly_chart(fig_smx)

smxtondayssl=smxtondays[smxtondays.index.year.isin(yrsl5)]

if freq5=='Quarterly':
    smxtondayssl=smxtondayssl.resample('Q').sum()
    smxtondayssl.index=smxtondayssl.index.year.astype(str)+'_Q'+smxtondayssl.index.quarter.astype(str)

if freq5=='Yearly':
    smxtondayssl=smxtondayssl.resample('Y').sum()
    smxtondayssl.index=smxtondayssl.index.year.astype(str)


fig_smx=px.bar(smxtondayssl,width=1000,height=500,title='Supramax Tondays Outlook')
fig_smx.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
fig_smx.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size-3,xaxis=plot_axis,yaxis=plot_axis)
fig_smx.update_layout(template=draft_template)
st.plotly_chart(fig_smx)


st.markdown('#### **----By Selection**')

sumsl=st.multiselect('Select Items',options=sumup.columns,default=['Brazil SBS FCST','USA SBS FCST','Argentina SBS FCST'],key='sumsl')
sumup=sumup[sumsl]

fig1=px.area(sumup,width=1000,height=500,title='Export Seaborne Trade Volume Outlook for Selected Items')
fig1.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
fig1.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
fig1.update_layout(template=draft_template)
st.plotly_chart(fig1)

sumup['Total']=sumup.sum(axis=1)
sumupttl=sumup[['Total']]

sumupttl['Year']=sumupttl.index.year
sumupttl['Month']=sumupttl.index.month

sumupttl=sumupttl.pivot_table(index='Month',columns='Year',values='Total',aggfunc='sum')

yrsl=st.multiselect('Select Years',options=sumupttl.columns,default=[curryear-1,curryear],key='yrsl')
sumupttl=sumupttl[yrsl]


st.write('Selected: '+str(sumsl))
sumplot=px.line(sumupttl,width=1000,height=500,title='Seasonality Outlook for Selected Items')
sumplot.update_xaxes(ticks=plot_ticks, tickwidth=plot_tickwidth,  ticklen=plot_ticklen)
sumplot.update_layout(title_font_color=plot_title_font_color,title_font_size=plot_title_font_size,legend_font_size=plot_legend_font_size,xaxis=plot_axis,yaxis=plot_axis)
sumplot['data'][-1]['line']['width']=5
sumplot['data'][-1]['line']['color']='black'
sumplot.update_layout(yaxis_title='Million Tonnes')
sumplot.update_layout(template=draft_template)
st.plotly_chart(sumplot)

