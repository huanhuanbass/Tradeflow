import streamlit as st
st.set_page_config(layout="wide")

st.title('Tradeflow Dashboard')

st.markdown('###### **:blue[----Made by Huanyu Chen]**')



import streamlit as st
import warnings; warnings.simplefilter('ignore')
import pandas as pd
import numpy as np
from datetime import date
from calendar import monthrange
from pandas.tseries.offsets import BDay
import requests
import ftplib
from math import ceil
from datetime import datetime
import time

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)



st.write('Loading Data...')

#Getting Trade Flow Data 
st.text('----Getting Trade Flow Data...')

@st.cache_data
def load_trade_flows_data():
    load_country_list=['Australia','Brazil','Canada','South Africa','India','Indonesia','Russia','USA','Colombia','China','Guinea','Argentina','Ukraine']
    segment_cat=['Capesize','Panamax','Supramax','Handysize','Others']

    step = 10000
    params = {
            "voyage_type" : 'laden',
            "dwt_from" : "5000",
            # "dwt_to" : "10000",
            "date_from" : "2015-01-01",
            "date_mode" : "started",
            "step" : str(step),
            }    
    url = "https://webservicesv5.axsmarine.com/rest/dry/voyages?"
    token = "4md5t0ITU0c8BQUe6HVngEfBsJdu1qIU"
    url = url + "token=" + token
    for name,value in params.items():
        url = url + "&" + name + "=" + value

    r = requests.get(url,verify=False).json()
    size = r['total']
    print(size, "lines to query")

    r = requests.get(url,verify=False).json()
    total = pd.DataFrame(r['results'])
    size = r['total']
    print(size, "lines to query")

    i=2
    while i <= ceil(size/step):
        print(i)
        url_loop = url + '&page=' + str(i)
        r_loop = requests.get(url_loop,verify=False).json()
        
        if 'message' in r_loop.keys() and r_loop['message'] == "Maximum hourly calls reached":
            waiting_minutes = 61 - datetime.now().minute + 1
            print("On a atteint le max horaire, attendre {} minutes".format(waiting_minutes))
            print(pd.to_datetime('today'))
            time.sleep(waiting_minutes * 60)
            r_loop = requests.get(url).json()
            
        total=pd.concat([total,pd.DataFrame(r_loop['results'])])
        i+=1

    tradeflow=total.copy()

    other_agri_list=['Grain','Agriprods','Breakbulk/Grain','Fertilizers/Grain','Bulk/Grain','Agriprods/Grain','Coal/Grain']

    tradeflow['commodity_group']=np.where(tradeflow['commodity'].isin(['Bauxite']),'Bauxite',tradeflow['commodity_group'])
    tradeflow['commodity_group']=np.where(tradeflow['commodity'].isin(['Soybeans']),'Soybeans',tradeflow['commodity_group'])
    tradeflow['commodity_group']=np.where(tradeflow['commodity'].isin(['Corn']),'Corn',tradeflow['commodity_group'])
    tradeflow['commodity_group']=np.where(tradeflow['commodity'].isin(['Wheat']),'Wheat',tradeflow['commodity_group'])
    tradeflow['commodity_group']=np.where(tradeflow['commodity'].isin(['Sugar']),'Sugar',tradeflow['commodity_group'])
    tradeflow['commodity_group']=np.where(tradeflow['commodity_group'].isin(other_agri_list),'Other Agri',tradeflow['commodity_group'])
    tradeflow['commodity_group']=np.where(tradeflow['commodity_group'].isin(['Iron Ore','Coal','Bauxite','Soybeans','Corn','Wheat','Other Agri','Sugar']),tradeflow['commodity_group'],'Other Bulk')
    tradeflow['segment']=pd.cut(tradeflow['vsl_dwt'],bins=[0,9999,42999,67999,109999,999999],labels=['Others','Handysize','Supramax','Panamax','Capesize'])
    tradeflow['subsegment']=pd.cut(tradeflow['vsl_dwt'],bins=[0,9999,26999,42999,49999,59999,67999,79999,89999,109999,139999,179999,249999,999999],labels=['Others','Small Handysize','Large Handysize','Handymax','Supramax','Ultramax','Panamax','Kamsarmax','Postpanamax','Babycape','Capesize','Large Capesize','VLOC'])

    tradeflow['Year']=pd.to_datetime(tradeflow['load_start_date']).dt.year
    tradeflow['Month']=pd.to_datetime(tradeflow['load_start_date']).dt.month
    tradeflow['Date']=pd.to_datetime(tradeflow['load_start_date']).dt.date
    tradeflow['load_group']=np.where(tradeflow['load_country'].isin(load_country_list),tradeflow['load_country'],'Others')

    EUlist=['Austria','Belgium','Bulgaria','Croatia','Cyprus','Czechia','Denmark','Estonia','Finland','France','Germany','Greece',
        'Hungary','Ireland','Italy','Latvia','Lithuania','Luxembourg','Malta','Netherlands','Poland','Portugal','Romania',
        'Slovakia','Slovenia','Spain','Sweden','United Kingdom']

    tradeflow['load_group']=np.where(tradeflow['load_country'].isin(EUlist),'EU',tradeflow['load_group'])
    tradeflow['discharge_group']=np.where(tradeflow['discharge_country'].isin(EUlist),'EU',tradeflow['discharge_country'])
    tradeflow['discharge_group']=np.where(tradeflow['discharge_group'].isin(['EU','China','India','Turkey','Unknown Country','Japan','Korea South','Hong Kong','Taiwan, Province of China']),tradeflow['discharge_group'],'Others')
    tradeflow['discharge_group']=np.where(tradeflow['discharge_group'].isin(['EU','China','India','Turkey','Unknown Country','Others']),tradeflow['discharge_group'],'JapanKoreaTWHK')
    tradeflow['discharge_group']=np.where(tradeflow['discharge_zone'].isin(['South East Asia']),'SEA',tradeflow['discharge_group'])
    
    tradeflow['segment']=pd.Categorical(tradeflow['segment'],categories=segment_cat)


    SAtl_America_list=['Carribbean','North Coast South America','East Coast Central America','East Coast South America']
    SAtl_Africa_list=['North West Africa','South West Africa','South Africa','South Atlantic']
    NAtl_America_list=['East Coast U.S','USG','East Coast Canada','Great Lakes']
    NAtl_Europe_list=['Antwerp Rotterdam Amsterdam Ghent','Baltic','North Continent','United Kingdom Ireland','Spain Atlantic','West Mediterranean','French Atlantic','East Mediterranean','Caspian Sea','Black Sea','Mid-North Atlantic']
    SPac_America_list=['West Coast South America','West Coast Central America','Mid Pacific','South Pacific']
    SPac_Australia_list=['New Zealand','East Aussie','West Aussie']
    NPac_America_list=['NoPac']
    NPac_Asia_list=['Far East','South East Asia']
    IndO_IndiaPG_list=['Red Sea','Arabian Gulf','West Coast India','East Africa','Indian Ocean','East Coast India']

    tradeflow['load_ocean']=np.where(tradeflow['load_zone'].isin(SAtl_America_list),'Atl_SAm','Others')
    tradeflow['load_ocean']=np.where(tradeflow['load_zone'].isin(SAtl_Africa_list),'Atl_Afr',tradeflow['load_ocean'])
    tradeflow['load_ocean']=np.where(tradeflow['load_zone'].isin(NAtl_America_list),'Atl_NAm',tradeflow['load_ocean'])
    tradeflow['load_ocean']=np.where(tradeflow['load_zone'].isin(NAtl_Europe_list),'Atl_Eur',tradeflow['load_ocean'])
    tradeflow['load_ocean']=np.where(tradeflow['load_zone'].isin(SPac_America_list),'Pac_SAm',tradeflow['load_ocean'])
    tradeflow['load_ocean']=np.where(tradeflow['load_zone'].isin(SPac_Australia_list),'Pac_Aus',tradeflow['load_ocean'])
    tradeflow['load_ocean']=np.where(tradeflow['load_zone'].isin(NPac_America_list),'Pac_NAm',tradeflow['load_ocean'])
    tradeflow['load_ocean']=np.where(tradeflow['load_zone'].isin(NPac_Asia_list),'Pac_Asia',tradeflow['load_ocean'])
    tradeflow['load_ocean']=np.where(tradeflow['load_zone'].isin(IndO_IndiaPG_list),'Ind_IDPG',tradeflow['load_ocean'])

    tradeflow['discharge_ocean']=np.where(tradeflow['discharge_zone'].isin(SAtl_America_list),'Atl_SAm','Others')
    tradeflow['discharge_ocean']=np.where(tradeflow['discharge_zone'].isin(SAtl_Africa_list),'Atl_Afr',tradeflow['discharge_ocean'])
    tradeflow['discharge_ocean']=np.where(tradeflow['discharge_zone'].isin(NAtl_America_list),'Atl_NAm',tradeflow['discharge_ocean'])
    tradeflow['discharge_ocean']=np.where(tradeflow['discharge_zone'].isin(NAtl_Europe_list),'Atl_Eur',tradeflow['discharge_ocean'])
    tradeflow['discharge_ocean']=np.where(tradeflow['discharge_zone'].isin(SPac_America_list),'Pac_SAm',tradeflow['discharge_ocean'])
    tradeflow['discharge_ocean']=np.where(tradeflow['discharge_zone'].isin(SPac_Australia_list),'Pac_Aus',tradeflow['discharge_ocean'])
    tradeflow['discharge_ocean']=np.where(tradeflow['discharge_zone'].isin(NPac_America_list),'Pac_NAm',tradeflow['discharge_ocean'])
    tradeflow['discharge_ocean']=np.where(tradeflow['discharge_zone'].isin(NPac_Asia_list),'Pac_Asia',tradeflow['discharge_ocean'])
    tradeflow['discharge_ocean']=np.where(tradeflow['discharge_zone'].isin(IndO_IndiaPG_list),'Ind_IDPG',tradeflow['discharge_ocean'])

    return tradeflow


tf=load_trade_flows_data()


print('Total Trade Flow Records: '+str(len(tf.index)))

if 'tradeflow' not in st.session_state:
    st.session_state['tradeflow']=tf

st.session_state['tradeflow']=tf


st.text('Trade Flow Data Done!')



st.write('All Data Loaded!!')








def update_data():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.cache_data.clear()

st.button('Update Data',on_click=update_data)


