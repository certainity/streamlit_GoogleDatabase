# Streamlit-Google Sheet
## Modules
import streamlit as st 
from pandas import DataFrame
import datetime as dt

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
import plotly.graph_objects as go



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


# --- STREAMLIT SELECTION
sn = df['SN'].unique().tolist()
# ages = df['LOCATION'].unique().tolist()

# age_selection = st.slider('Age:',
#                         min_value= min(ages),
#                         max_value= max(ages),
#                         value=(min(ages),max(ages)))
# --- STREAMLIT date picker
# min_date = dt.datetime(2023,1,1)
# max_date = dt.date(2024,1,1)

# a_date = st.date_input("Pick a date", (min_date, max_date))

##this uses streamlit 'magic'!!!!
# "The date selected:", a_date
# "The type", type(a_date)
# "Singling out a date for dataframe filtering", a_date[0],a_date[-1]

# min_date = dt.datetime(2020,1,1)
# max_date = dt.date(2024,1,1)

# a_date = st.date_input("Pick a date", min_value=min_date, max_value=max_date)

# mn_date = dt.datetime(2020,1,1)
# mx_date = dt.date(2024,1,1)
# b_date = st.date_input("End date", min_value=mn_date, max_value=mx_date)

# ##this uses streamlit 'magic'!!!! 
# "The date selected:", a_date,b_date

today = dt.date.today()
tomorrow = today + dt.timedelta(days=1)
start_date = st.date_input('Start date', today)
end_date = st.date_input('End date', tomorrow)

st.dataframe(df)

stime = start_date
time1 = stime.strftime("%Y-%m-%d %H:%M:%S")
etime= end_date
time2 = etime.strftime("%Y-%m-%d 23:59:59")
df2 = df.query('Time_stamp >= @time1 and Time_stamp <= @time2')

# df2 = df.loc[(df['Time_stamp'] >= time1) & (df['Time_stamp'] < time2)]

# df2 = df[(df['Time_stamp'] > "2023-04-12") & (df['Time_stamp']< "2023-04-13")]
# print(df2)
st.dataframe(df2)

if time1 < time2:
    # st.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
        
# bar_chart:
# st.markdown("### Location Check")
    bar_chart = px.bar(df2,
                   x='SN',
                   y='LOCATION',
                   text='LOCATION',
                   color_discrete_sequence = ['#F63366']*len(df2),
                   template= 'plotly',
                   title="Location Check",
                  )
    bar_chart.layout.xaxis.fixedrange = True
    bar_chart.layout.yaxis.fixedrange = True
    st.plotly_chart(bar_chart,theme='streamlit',)


#'ggplot2', 'seaborn', 'simple_white', 'plotly', 
# 'plotly_white', 'plotly_dark', 'presentation', 'xgridoff','ygridoff', 'gridon', 'none
else:
    st.error('Error: End date must be equal or greater then start date.')


# department_selection = st.multiselect('SN:',
#                                     sn,
#                                     default=sn)

# --- FILTER DATAFRAME BASED ON SELECTION
# mask = (df['SN'].isin(department_selection))
# number_of_result = df[mask].shape[0]
# st.markdown(f'*Available Results: {number_of_result}*')

# --- GROUP DATAFRAME AFTER SELECTION
# df_grouped = df[mask].groupby(by=['SN']).count()[['LOCATION']]
# df_grouped = df_grouped.rename(columns={'LOCATION': 'Time_stamp'})
# df_grouped = df_grouped.reset_index()



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
