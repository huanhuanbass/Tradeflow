from oceanbolt.sdk.client import APIClient
base_client = APIClient('eyJhbGciOiJSUzI1NiIsImtpZCI6ImUxNmUwNWI1NTZmNjVjYWEyNTg0ODU0N2FmYjNjZjI4IiwidHlwIjoiSldUIn0.eyJhdWQiOiJodHRwczovL2FwaS5vY2VhbmJvbHQuY29tIiwiZXhwIjoxNzA2MjgyMzQwLCJpYXQiOjE2NzQ3NDY0MDksImlzcyI6Imh0dHBzOi8vYXV0aC5vY2VhbmJvbHQuY29tLyIsImtpZCI6ImUxNmUwNWI1NTZmNjVjYWEyNTg0ODU0N2FmYjNjZjI4Iiwia3R5cGUiOiJhcGlrZXkiLCJvYmtpZCI6Im5QQ1o4N1Vabm5DWmdqZGQiLCJvcmdpZCI6InZhdHRlbmZhbGwiLCJzdWIiOiJhdXRoMHw2M2QxNDk5NGY3YWY3NjEwNmFjNWI1NDEifQ.GLW-WFKi525qMul76neKHolnVLENjgE__obx8e15Oayw10pVMVyXutNuCD7GkR0lpuV8yQNHEQG4iImz10KBKejzB7KH3F_WaUGVOtkOkX461M-jSz-utIhAvr111FK7MHe2jvqIHfV-ts-K3Pk5COJyTBBQBIG2HMzxbmh-0OCfZb_M5APsWLJ-mQdbs1dTjRg7RHy5jaMJSjcV0iFSz_RO-9QaSAlg1snBOaIx_uqQFGjMwDiiiE7b3fmi_Q4ngRq67UVlAb7tiiqxc0Y_LDEewL5eVnDllaDNYORBBtrzwTUaYOMi3GldinmB1psskX5OWvhn2LXhQNowqY2QpxsGTQEoCxqZQ0riseiS8_EE5CE9GKV2kMZL9e_xW1idiFAETXNSFHj9tuc4-SP5WO2kjiN7HvUFPDqSbhzanCYxjTpAMaQfhEd1Zno5iJmS3x6oBHivDiB6ccYdBDImgUD-WMh4M_EVIvcXdqu9bbOuXfUExPX78-qYqGbvlbkA219FKPzXaYIz4npgm3IYArpRFP63ClBJaH8JGJ-bdMc8Nj5hGFtqigfwjbyz-vb3u8mZ11Q5tHY_kDqlaeNRmcHrMSVpkFgF3M6PBcRObp-iABHaEz2B3kdIgD7GPF5ZlOa6Jn7ZV1w0ply_GFLNJoZItNR5rpUKYyc98WcE9cc')

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




st.title('Trade Flow Summary')
st.text('Dry Bulk Freight (Trade Flow) Interactive Dashboard')


st.markdown('## **All Trade Flows**')
freq2=st.radio('Select Frequency',options=['Weekly','Monthly'],key='freq2')
cargo_list=st.multiselect('Select Other Commodities',options=tf['commodity_group'].unique(),default=['Coal'],key='cargolist')
seg_list=st.multiselect('Select Vessel Segment',options=tf['segment'].unique(),default=['Capesize','Panamax','Supramax','Handysize'],key='seglist')
load_list=st.multiselect('Select Loading Countries',options=tf['load_group'].unique(),default=['Australia'],key='loadlist')
disch_list=st.multiselect('Select Discharing Groups',options=tf['discharge_group'].unique(),default=tf['discharge_group'].unique(),key='dischlist')
yrsl=st.multiselect('Select Years for Seasonal Line Chart',options=np.arange(2015,curryear+1),default=np.arange(curryear-4,curryear+1),key='year')
yrsl2=st.multiselect('Select Years for Split Area Chart',options=np.arange(2015,curryear+1),default=np.arange(curryear-1,curryear+1),key='year2')
split=st.selectbox('Select Split/Grouping Method',options=['by Size','by Load Country','by Cargo','by Discharge Group'])

st.button(label='Get Charts', key='get_chart')
if st.session_state.get('get_chart'):
    df=tf[tf['commodity_group'].isin(cargo_list)]
    df=df[df['segment'].isin(seg_list)]
    df=df[df['load_group'].isin(load_list)]
    df=df[df['discharge_group'].isin(disch_list)]
    df['Date']=pd.to_datetime(df['Date'])
    df.set_index('Date',inplace=True)

    if split=='by Load Country':
        dfsplit=df.pivot_table(index='Date',columns='load_group',values='voy_intake_mt',aggfunc='sum')/1000000
    elif split=='by Cargo':
        dfsplit=df.pivot_table(index='Date',columns='commodity_group',values='voy_intake_mt',aggfunc='sum')/1000000
    elif split=='by Size':
        dfsplit=df.pivot_table(index='Date',columns='segment',values='voy_intake_mt',aggfunc='sum')/1000000
    elif split=='by Discharge Group':
        dfsplit=df.pivot_table(index='Date',columns='discharge_group',values='voy_intake_mt',aggfunc='sum')/1000000



    if freq2=='Monthly':
        df=df[['voy_intake_mt']]
        dfm=df.resample('M').sum()
        dfm['Year']=dfm.index.year
        dfm['Month']=dfm.index.month
        dfm=dfm[dfm.index<cutoff]
        dfm=dfm[dfm['Year'].isin(yrsl)]
        dfmpv=dfm.pivot_table(index='Month',columns='Year',values='voy_intake_mt',aggfunc='sum')/1000000
        dfmpvplot=px.line(dfmpv,width=1000,height=500,title=str(cargo_list)+' Monthly Loadings Seasonality '+'on Size'+str(seg_list)+'from'+str(load_list)+'to'+str(disch_list))
        dfmpvplot['data'][-1]['line']['width']=5
        dfmpvplot['data'][-1]['line']['color']='black'
        dfmpvplot.update_layout(yaxis_title='Million Tonnes')
        st.plotly_chart(dfmpvplot)

        dfspm=dfsplit.resample('M').sum()
        dfspm=dfspm[dfspm.index<cutoff]
        dfspm=dfspm[dfspm.index.year.isin(yrsl2)]

        dfspplot=px.area(dfspm,width=1000,height=500,title=str(cargo_list)+' Monthly Loadings '+'on Size'+str(seg_list)+'from'+str(load_list)+'to'+str(disch_list))
        dfspplot.update_layout(yaxis_title='Million Tonnes')
        dfspplot.update_layout(template=draft_template)
        st.plotly_chart(dfspplot)



    elif freq2=='Weekly':
        df=df[['voy_intake_mt']]
        dfw=df.resample('W-Sat').sum()
        dfw['Year']=dfw.index.year
        dfw['Week']=dfw.index.isocalendar().week
        dfw.loc[dfw[dfw.index.date==date(2016,1,2)].index,'Week']=0
        dfw.loc[dfw[dfw.index.date==date(2021,1,2)].index,'Week']=0
        dfw.loc[dfw[dfw.index.date==date(2022,1,1)].index,'Week']=0
        dfw=dfw[dfw.index<wkcutoff]
        dfw=dfw[dfw['Year'].isin(yrsl)]
        dfwpv=dfw.pivot_table(index='Week',columns='Year',values='voy_intake_mt',aggfunc='sum')/1000000
        dfwpvplot=px.line(dfwpv,width=1000,height=500,title=str(cargo_list)+' Weekly Loadings Seasonality '+'on Size'+str(seg_list)+'from'+str(load_list)+'to'+str(disch_list))
        dfwpvplot['data'][-1]['line']['width']=5
        dfwpvplot['data'][-1]['line']['color']='black'
        dfwpvplot.update_layout(yaxis_title='Million Tonnes')
        dfwpvplot.update_layout(template=draft_template)
        st.plotly_chart(dfwpvplot)

        dfspw=dfsplit.resample('W-Sat').sum()
        dfspw=dfspw[dfspw.index<cutoff]
        dfspw=dfspw[dfspw.index.year.isin(yrsl2)]

        dfspplot=px.area(dfspw,width=1000,height=500,title=str(cargo_list)+' Weekly Loadings '+'on Size'+str(seg_list)+'from'+str(load_list)+'to'+str(disch_list))
        dfspplot.update_layout(yaxis_title='Million Tonnes')
        st.plotly_chart(dfspplot)



st.markdown('## **Trade Flows Rank by Importance**')


yr0=st.selectbox('Select Year',options=np.arange(curryear-1,2015,-1))
seg_list0=st.selectbox('Select Vessel Segment',options=['Capesize','Panamax','Supramax','Handysize'])
group_method=st.multiselect('Select Grouping Method',options=['commodity_group','load_country','discharge_country'],default=['commodity_group','load_country'],key='group')
tf_yr=tf[tf['Year']==yr0]
tf_yr=tf_yr[tf_yr['segment']==seg_list0]

tf_yr_group=tf_yr.groupby(group_method).agg({'voy_intake_mt':'sum','voy_sea_duration':'mean'})
tf_yr_group['voy_intake_mt']=tf_yr_group['voy_intake_mt']/1000000
tf_yr_group['voy_sea_duration']=tf_yr_group['voy_sea_duration']/(60*24)
tf_yr_group.rename(columns={'voy_intake_mt':'Volume in Millions','voy_sea_duration':'Duration in Days'},inplace=True)
tf_yr_group['Tondays in Millions']=tf_yr_group['Volume in Millions']*tf_yr_group['Duration in Days']
tf_yr_group['Volume%']=tf_yr_group['Volume in Millions']/tf_yr_group['Volume in Millions'].sum()
tf_yr_group['Tondays%']=tf_yr_group['Tondays in Millions']/tf_yr_group['Tondays in Millions'].sum()
tf_yr_group.sort_values(by='Tondays%',ascending=False,inplace=True)

mapper={'Volume in Millions': '{0:.1f}', 'Duration in Days': '{0:.1f}', 'Tondays in Millions': '{0:.0f}','Volume%': '{0:.2f}','Tondays%': '{0:.2f}'}
st.write(tf_yr_group.style.format(mapper))


print('Total Trade Flow Records: '+str(len(tf.index)))

