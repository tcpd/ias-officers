import streamlit as st
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
import matplotlib.pyplot as plt

admin_categories = [
    "Land Revenue Mgmt & District Admn",
    "Personnel and General Administration",
    "Finance"
]

@st.cache
def load_unigram_data():
    df = pd.read_csv('./processed/unigram maps.csv')
    df = df.loc[df["Experience"] != "N.A."]
    return df

@st.cache
def load_lists_data():
    return pd.read_csv('./processed/IAS subjects map.csv')

admin_categories = [
    "Land Revenue Mgmt & District Admn",
    "Personnel and General Administration",
    "Finance"
]

def filter_by_value(df, col, value, include_admin=True, number_of_rows=5, percentage=False):

    df = df.loc[df[col].str.contains(value)]
    df.sort_values(["Count"], ascending=False, inplace=True)

    if include_admin and col == "Subject":
        for category in admin_categories:
            df = df.loc[df["Experience"] != category]

    df.drop(columns=[col], inplace=True)
    df.set_index(df.columns[0], inplace=True)

    df = df.head(number_of_rows)

    if percentage:
        sum = df["Count"].sum()
        df = pd.DataFrame(df["Count"].apply(lambda x: (x / sum) * 100))

    return df

unigram_data = load_unigram_data()
lists_data = load_lists_data()

st.subheader('Unigram maps')
st.write(unigram_data)


st.subheader('Select a category of expirence')
option_experience = st.selectbox("", unigram_data['Experience'].unique())

filtered_df_experience = filter_by_value(unigram_data.copy(), 'Experience', option_experience, number_of_rows=500)
st.write(filtered_df_experience)
st.bar_chart(data=filtered_df_experience, height=600)


fig1, ax1 = plt.subplots()

ax1.pie(filtered_df_experience['Count'], labels=filtered_df_experience.index, autopct='%1.1f%%')

# set background to transparent
fig1.patch.set_facecolor('none')
# set label color to white
[ax1.texts[i].set_color('w') for i in range(len(ax1.texts))]

ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

st.pyplot(fig1)

st.subheader('Select a Subject')
option_subject = st.selectbox("", unigram_data['Subject'].unique())

include_admin = st.checkbox('Remove Top Admin Categories')
percentage = st.checkbox('Show percentage', value=True)

number_of_rows = st.slider('Number of rows', min_value=1, max_value=47, value=5)

filtered_df_subject = filter_by_value(unigram_data.copy(), 'Subject', option_subject, include_admin=include_admin, number_of_rows=number_of_rows, percentage=percentage)
st.write(filtered_df_subject)
st.bar_chart(data=filtered_df_subject, height=600)

fig2, ax2 = plt.subplots()
ax2.pie(filtered_df_subject['Count'], labels=filtered_df_subject.index, autopct='%1.1f%%')

fig2.patch.set_facecolor('none')
[ax2.texts[i].set_color('w') for i in range(len(ax2.texts))]
ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
st.pyplot(fig2)