# Streamlit-Google Sheet
## Modules
import streamlit as st 
from pandas import DataFrame

from gspread_pandas import Spread,Client
from google.oauth2 import service_account

# Application Related Module
import pubchempy as pcp
from pysmiles import read_smiles
# 
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np   

from datetime import datetime

import plotly.express as px  # interactive charts


# Disable certificate verification (Not necessary always)
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Create a Google Authentication connection object
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes = scope)
client = Client(scope=scope,creds=credentials)
spreadsheetname = "Database"
spread = Spread(spreadsheetname,client = client)

# Check the connection
# st.write(spread.url)

sh = client.open(spreadsheetname)
worksheet_list = sh.worksheets()

# Functions 
@st.cache_data(ttl=600)

# Get our worksheet names
def worksheet_names():
    sheet_names = []   
    for sheet in worksheet_list:
        sheet_names.append(sheet.title)  
    return sheet_names

# Get the sheet as dataframe
def load_the_spreadsheet(spreadsheetname):
    worksheet = sh.worksheet(spreadsheetname)
    df = DataFrame(worksheet.get_all_records())
    return df


# Update to Sheet
def update_the_spreadsheet(spreadsheetname,dataframe):
    col = ['Compound CID','Time_stamp']
    spread.df_to_sheet(dataframe[col],sheet = spreadsheetname,index = False)
    st.sidebar.info('Updated to GoogleSheet')


st.header('Performance Report')

# Check whether the sheets exists
what_sheets = worksheet_names()
#st.sidebar.write(what_sheets)
ws_choice = st.sidebar.radio('Available worksheets',what_sheets)

# Load data from worksheets
df = load_the_spreadsheet(ws_choice)
# Show the availibility as selection
# select_CID = st.sidebar.selectbox('CID',list(df['Compound CID']))
# values_list = worksheet.col_values(1)
# select_CID = st.sidebar.selectbox('CID',list(df['SN']))

# Now we can use the pubchempy module to dump information
# comp = pcp.Compound.from_cid(select_CID)
# comp_dict = comp.to_dict() # Converting to a dictinoary
# What Information look for ?
# options = ['molecular_weight' ,'molecular_formula',
#            'charge','atoms','elements','bonds']
# show_me = st.radio('What you want to see?',options)

# st.info(comp_dict[show_me])
# name = comp_dict['iupac_name']
# st.markdown(name)
# plot = st.checkbox('Canonical Smiles Plot')

# fig = px.bar(x=df['SN'], y=df['LOCATION'])
# fig.show()

# create two columns for charts
# fig_col1, fig_col2 = st.columns(2)

# with fig_col1:
#     st.markdown("### First Chart")
#     fig = px.density_heatmap(
#         data_frame=df, y="LOCATION", x="SN"
#     )
#     st.write(fig)

# bar_chart:
st.markdown("### Location Check")
bar_chart = px.bar(df,
                   x='SN',
                   y=df['LOCATION'],
                   text=df['LOCATION'],
                   color_discrete_sequence = ['#F63366']*len(df),
                   template= 'plotly_white')
st.plotly_chart(bar_chart)
#'ggplot2', 'seaborn', 'simple_white', 'plotly', 
# 'plotly_white', 'plotly_dark', 'presentation', 'xgridoff','ygridoff', 'gridon', 'none
   


add = st.sidebar.checkbox('Add CID')
if add :  
    cid_entry = st.sidebar.text_input('New CID')
    confirm_input = st.sidebar.button('Confirm')
    
    if confirm_input:
        now = datetime.now()
        opt = {'Compound CID': [cid_entry],
              'Time_stamp' :  [now]} 
        opt_df = DataFrame(opt)
        df = load_the_spreadsheet('Pending CID')
        new_df = df.append(opt_df,ignore_index=True)
        update_the_spreadsheet('Pending CID',new_df)
