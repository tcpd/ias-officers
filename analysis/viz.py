import streamlit as st
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="IAS Subject Analysis", page_icon="📚", layout="centered")

colors = {}

lower = 100

def color_map(item):
    return colors[item]

@st.cache
def load_unigram_data():
    df = pd.read_csv('./processed/unigram maps.csv')
    df = df.loc[df["Experience"] != "N.A."]

    df["text"] = df["Count"].apply(lambda x: "size: "+str(x))

    for i, item in enumerate(df["Subject"].unique()):
        colors[item] = lower + i
    
    df["colors"] = df["Subject"].map(color_map)
    return df

@st.cache
def load_lists_data():
    return pd.read_csv('./processed/IAS subjects map.csv')

admin_categories = [
    "Land Revenue Mgmt & District Admn",
    "Personnel and General Administration",
    "Finance"
]

def filter_by_value(df, col, value, include_admin=True, number_of_rows=5, percentage=False, include_other=False):

    df = df.loc[df[col].str.contains(value)]
    df.sort_values(["Count"], ascending=False, inplace=True)

    if include_admin and col == "Subject":
        for category in admin_categories:
            df = df.loc[df["Experience"] != category]

    temp = df[number_of_rows:]
    df = pd.DataFrame(df.head(number_of_rows))
    value_sum = temp["Count"].sum()
    
    if include_other:
        df = df.append({
            df.columns[0]: "Other",
            df.columns[1]: "Other",
            "Count": value_sum
        }, ignore_index=True)

    df.drop(columns=[col], inplace=True)
    df.set_index(df.columns[0], inplace=True) 

    if percentage:
        sum = df["Count"].sum()
        df = pd.DataFrame(df["Count"].apply(lambda x: round(((x / sum) * 100), 2)))

    try:
        return df.drop(columns=["text", "colors"])
    except:
        return df

def scatter_plot(df, include_top_cat=True, min_value=50):
    if include_top_cat:
        df = df.loc[df["Experience"] != 'Land Revenue Mgmt & District Admn']
        df = df.loc[df["Experience"] != 'Personnel and General Administration']
        df = df.loc[df["Experience"] != 'Finance']

    df = df.loc[df["Count"] > min_value]
    max_value = df["Count"].max()

    length_y_axis = df["Subject"].unique().shape[0]
    length_x_axis = df["Experience"].unique().shape[0]

    fig = go.Figure(data=[go.Scatter(
        x=df["Experience"].to_list(),
        y=df["Subject"].to_list(),
        text=df["text"].to_list(),
        mode="markers",
        marker=dict(
            size=df["Count"].apply(lambda x: x*50/max_value).to_list(),
            color = df["colors"].to_list(),
        )
    )])

    fig = fig.update_layout(
        autosize=False,
        height=100 + (length_y_axis * 75),
        width=100 + (length_x_axis * 75),
    )

    # remove grid lines from the figure
    fig.update_xaxes(
        showgrid=False,
        type="category",
    )
    fig.update_yaxes(showgrid=False)
    
    return fig

def pie_chart(df):
    fig = px.pie(
        df, 
        names=df.index, 
        values=df["Count"], 
        title="Subjects",
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    return fig.update_traces(
        hoverinfo="label+percent",
        textinfo="value",
        insidetextfont=dict(
            color="white"
        ),
    )

unigram_data = load_unigram_data()
lists_data = load_lists_data()

st.subheader('Unigram maps')
st.write(unigram_data.drop(columns=["text", "colors"]))

st.sidebar.subheader('Select a category of expirence')
st.subheader('Number of Subject occurances with respect to chosen Category of Experience')
option_experience = st.sidebar.selectbox("", unigram_data['Experience'].unique())

include_other_experience = st.sidebar.checkbox("Include combined remaining entries")
number_of_rows_experience = st.sidebar.slider('Number of rows', min_value=1, max_value=8, value=5)

filtered_df_experience = filter_by_value(unigram_data.copy(), 'Experience', option_experience, number_of_rows=number_of_rows_experience, include_other=include_other_experience)
st.write(filtered_df_experience)
st.bar_chart(data=filtered_df_experience, height=600)

st.plotly_chart(pie_chart(filtered_df_experience))

st.sidebar.markdown("""<hr/>""", unsafe_allow_html=True)
st.markdown("""<hr/>""", unsafe_allow_html=True)

st.sidebar.subheader('Select a Subject')
st.subheader('Number of Category of Experience occurances with respect to chosen Subject')
option_subject = st.sidebar.selectbox("", unigram_data['Subject'].unique())

include_admin = st.sidebar.checkbox('Remove Top Admin Categories')
percentage = st.sidebar.checkbox('Show percentage', value=True)

number_of_rows = st.sidebar.slider('Number of rows', min_value=1, max_value=47, value=5)

filtered_df_subject = filter_by_value(unigram_data.copy(), 'Subject', option_subject, include_admin=include_admin, number_of_rows=number_of_rows, percentage=percentage)
st.write(filtered_df_subject)
st.bar_chart(data=filtered_df_subject, height=600)

st.plotly_chart(pie_chart(filtered_df_subject))

st.sidebar.markdown("""<hr/>""", unsafe_allow_html=True)
st.markdown("""<hr/>""", unsafe_allow_html=True)

st.sidebar.subheader('Bubble map')
st.subheader('Bubble map')
include_admin_scatter = st.sidebar.checkbox('Remove Top Admin Categories', key="include_admin_scatter")
num_range = st.sidebar.slider('Filter threshold', min_value=1, max_value=600, value=20)

st.plotly_chart(scatter_plot(unigram_data.copy(), include_top_cat=include_admin_scatter, min_value=num_range))