import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

from Big_Mamma.data_base import update_db
from Big_Mamma.get_data import get_sports_event_europe
from Big_Mamma.data_base import create_connection


def requete(date_from, date_to, cat_filter, prod_filter):
    '''
    execute a SQL request to get sales within dates and with the filters
    :param date_from: the start date of the sales to get in the format 'YYYY-MM-DD'
    :param date_to: the end date of the sales to get in the same format
    :param cat_filter: the categorie selected or 'All' if no selection
    :param prod_filter: the product selected or 'All' if no selection

    return a list of list
    '''
    if prod_filter == "All":
        prod_filter = "%"
    if cat_filter == "All":
        cat_filter = "%"
    req = conn.execute(
        """
        SELECT date ,i.Name,v.montant_total, i.Categorie
        FROM Ventes v
        JOIN items i ON i.id = v.item_id
        WHERE i.Categorie LIKE ? AND i.Name LIKE ? AND v.date >= DATE(?) AND v.date <= DATE(?)
        """,
        (cat_filter, prod_filter, date_from, date_to),
    )
    reponse = req.fetchall()
    return reponse

#create connexion to the DB
db_path = os.path.join(os.path.join(os.path.join(os.path.join(os.path.dirname(__file__), 'Big_Mamma'),'Big_Mamma'),'data'),'sales.db')
conn = create_connection(db_path)

# SQL to get all categories
req = conn.execute(
    """
    SELECT DISTINCT categorie
    FROM items
    """
)
noms_cat = ["All"] #add the 'all' selection
for i in req.fetchall():
    noms_cat.append(i[0])

#SQL to get all the products names
req = conn.execute(
    """
    SELECT DISTINCT name
    FROM items
    """
)
noms_prod = ["All"]#add the 'all' selection
for i in req.fetchall():
    noms_prod.append(i[0])

#SQL to get the first date of the DB
req = conn.execute(
    """
    SELECT DISTINCT date
    FROM Ventes
    ORDER BY date ASC
    LIMIT 1
    """
)
date_from = pd.to_datetime(req.fetchone()[0])

#SQL to get the last date
req = conn.execute(
    """
    SELECT DISTINCT date
    FROM Ventes
    ORDER BY date DESC
    LIMIT 1
    """
)
date_to = pd.to_datetime(req.fetchone()[0])

# Start of web front
st.set_page_config(layout="wide")

"# :pizza: Big Mamma Sales Viz :pizza:" #Title

with st.sidebar: #side bar with filters

    "# ⚙️ Select filters ✅"

    date_from = st.date_input(
        "Date from:", date_from, max_value=date_to, min_value=date_from
    )
    date_to = st.date_input("Date to:", date_to, max_value=date_to, min_value=date_from)

    categorie = st.selectbox("Categories", noms_cat)
    product = st.selectbox("Products:", noms_prod)

    col1, col2 = st.columns(2)

    with col1:
        sports = st.button("Search Sports Events")

    with col2:
        if st.button("Refresh Google sheet data"):
            conn.close()
            update_db()
            conn = create_connection(db_path)

# SQL to get the sales with the filters
result = pd.DataFrame(
    requete(date_from, date_to, categorie, product),
    columns=["Date", "Product", "Total Sales", "Category"],
)

#print sales graph on the page
"## 📊 Sales per product"
st.plotly_chart(
    px.bar(data_frame=result, x="Date", y="Total Sales", color="Product"),
    use_container_width=True,
)

#if the button to get sports events is press
if sports:
    "## ⚽️ Sports Events at the same time 🏆"
    events = get_sports_event_europe(date_from, date_to)
    if 'error' in events.columns:
        st.error(f'Error with the sports API. Code error : {events.iloc[0,0]}')
    else:
        events["Start date"] = pd.to_datetime(events["Start date"])
        events["End date"] = pd.to_datetime(events["End date"])
        graph = px.scatter(
            x=[events["Start date"], events["End date"]],
            y=events["name"],
            color=events["name"],
            custom_data=[events["Start date"], events["End date"], events["locations"]],
            labels={"value": "Date", "y": "Event"},
            height=np.sqrt(len(events)) * 100,
        )
        #custom hover mode on graph
        graph.update_traces(
            mode="markers+lines",
            hovertemplate="<br>".join(
                [
                    "Event: %{y}",
                    "Start Date: %{customdata[0]}",
                    "End Date: %{customdata[1]}",
                    "City: %{customdata[2]}",
                ]
            ),
        )
        graph.update_layout(showlegend=False)
        st.plotly_chart(graph, use_container_width=True)

conn.close()
