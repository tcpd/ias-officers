import streamlit as st
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
import matplotlib.pyplot as plt

@st.cache
def load_unigram_data():
    return pd.read_csv('./processed/unigram maps.csv')

@st.cache
def load_lists_data():
    return pd.read_csv('./processed/IAS subjects map.csv')

def filter_by_value(df, col, value):

    df = df.loc[df[col].str.contains(value)]
    df.sort_values(["Count"], ascending=False, inplace=True)
    df.drop(columns=[col], inplace=True)
    df.set_index(df.columns[0], inplace=True)

    return df.head(5)

unigram_data = load_unigram_data()
lists_data = load_lists_data()

st.subheader('Unigram maps')
st.write(unigram_data)



st.subheader('Select a category of expirence')
option_experience = st.selectbox("", unigram_data['Experience'].unique())

filtered_df_experience = filter_by_value(unigram_data.copy(), 'Experience', option_experience)
st.write(filtered_df_experience)
st.bar_chart(data=filtered_df_experience, height=600)


fig1, ax1 = plt.subplots()

ax1.pie(filtered_df_experience['Count'], labels=filtered_df_experience.index, autopct='%1.1f%%',)

# set background to transparent
fig1.patch.set_facecolor('none')
# set label color to white
[ax1.texts[i].set_color('w') for i in range(len(ax1.texts))]

ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

st.pyplot(fig1)

st.subheader('Select a Subject')
option_subject = st.selectbox("", unigram_data['Subject'].unique())

filtered_df_subject = filter_by_value(unigram_data.copy(), 'Subject', option_subject)
st.write(filtered_df_subject)
st.bar_chart(data=filtered_df_subject, height=600)