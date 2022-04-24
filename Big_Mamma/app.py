import streamlit as st
from Big_Mamma.data_base import generate_db
from Big_Mamma.get_data import get_sports_event_europe
from Big_Mamma.data_base import create_connection
import pandas as pd
import plotly.express as px

import os
import sqlite3

st.set_page_config(layout="wide")

def requete(date_from,date_to,cat_filter,prod_filter):
    if prod_filter=='All':
        prod_filter='%'
    if cat_filter=='All':
        cat_filter='%'
    req=conn.execute('''SELECT date ,i.Name,v.montant_total, i.Categorie
FROM Ventes v
JOIN items i ON i.id = v.item_id
WHERE i.Categorie LIKE ? AND i.Name LIKE ? AND v.date >= DATE(?) AND v.date <= DATE(?)
''',(cat_filter, prod_filter,date_from,date_to))
    reponse=req.fetchall()
    return reponse


'# :pizza: Big Mamma Sales Viz :pizza:'

db_path=os.path.join(os.path.dirname(os.path.dirname(__file__)),'Big_Mamma/data/sales.db')

conn=create_connection(db_path)

req=conn.execute('''SELECT DISTINCT categorie
                 FROM items
                 ''')

noms_cat=['All']
for i in req.fetchall():
    noms_cat.append(i[0])

req=conn.execute('''SELECT DISTINCT name
                 FROM items
                 ''')

noms_prod=['All']
for i in req.fetchall():
    noms_prod.append(i[0])

req=conn.execute('''SELECT DISTINCT date
                 FROM Ventes
                 ORDER BY date ASC
                 ''')


date_from= pd.to_datetime(req.fetchone()[0])

req=conn.execute('''SELECT DISTINCT date
                 FROM Ventes
                 ORDER BY date DESC
                 ''')

date_to= pd.to_datetime(req.fetchone()[0])

with st.sidebar:

    '# ⚙️ Select filters ✅'

    date_from=st.date_input('Date from:',date_from,max_value=date_to,min_value=date_from)
    date_to=st.date_input('Date to:',date_to,max_value=date_to,min_value=date_from)

    categorie=st.selectbox('Categories', noms_cat)
    product=st.selectbox('Products:',noms_prod)

    col1, col2 = st.columns(2)

    with col1:
        sports=st.button('Search Sports Events')

    with col2:
        if st.button('Refresh Google sheet data'):
            conn.close()
            generate_db()
            conn=create_connection(db_path)

result=pd.DataFrame(requete(date_from,date_to,categorie,product),columns=['Date','Product','Total Sales','Category'])

'## 📊 Sales per product'
st.plotly_chart(px.bar(data_frame=result,x='Date',y='Total Sales',color='Product'),use_container_width=True)

if sports:
    '## ⚽️ Sports Events at the same time 🏆'
    events=get_sports_event_europe(date_from,date_to)
    events['Start date']=pd.to_datetime(events['Start date'])
    events['End date']=pd.to_datetime(events['End date'])
    graph=px.scatter(x=[events['Start date'],events['End date']],y=events['name'],color=events['name'],custom_data=[events['Start date'],
                                                                                                                    events['End date'],
                                                                                                                    events['locations']],
                                                                                                        labels={
                                                                                                        "value": "Date",
                                                                                                        "y": "Event"
                                                                                                    },)
    graph.update_traces(mode="markers+lines",hovertemplate="<br>".join([
        "Event: %{y}",
        "Start Date: %{customdata[0]}",
        "End Date: %{customdata[1]}",
        "City: %{customdata[2]}"
    ]))
    graph.update_layout(showlegend=False)
    st.plotly_chart(graph,use_container_width=True)

conn.close()
