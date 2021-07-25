import streamlit as st
import altair as alt
import pandas as pd
from vega_datasets import data
from random import randint
import numpy as np


@st.cache
def generate_population_data():
    """
    This method generates a random population data set.
    """
    return pd.DataFrame([{
        'year': year,
        'people': randint(1, 10),
        'sex': sex,
        'age': age
    } for age in range(0, 99) for year in range(1890, 2000)
                         for sex in (0, 1)])


def format_interval(r):
    """
    This method format the data in the central column of
    the plot.
    """
    left = int(r.left)
    right = int(r.right)
    if left <= 0:
        left = 0

    else:
        left += 1

    return f'[{left:03}, {right:03}]'


st.title('Altair Population Pyramid Example')
st.markdown('The original post in the altair documentation is [here](https://altair-viz.github.io/gallery/us_population_pyramid_over_time.html).')
st.markdown('The data in the original example is a real-world example with the data grouped by age. But in this tutorial, we will generate completely random data and group it our self.')

st.markdown('## Start with a randomly generated DataFrame')

original_col, our_data_col = st.beta_columns(2)

# Altair example data
population = data.population()
with original_col:
    st.markdown('### Original Altair data')
    population

population_df = generate_population_data()
with our_data_col:
    st.markdown('### Our Generated Data')
    population_df

st.markdown('## With year filter')
data_col, filter_col = st.beta_columns(2)

years = list(population_df.year.unique())
with filter_col:
    year = st.selectbox('Year:', years)
year_filtred = population_df[population_df.year == year]

with data_col:
    year_filtred


group_size = 10

sex_filter_grouping = year_filtred.groupby([
    pd.cut(year_filtred["age"], np.arange(-1, 100, group_size), include_lowest=False),
    'sex'
]).sum()
sex_filter_grouping['sex'] = [sex for range, sex in sex_filter_grouping.index]
sex_filter_grouping = sex_filter_grouping.set_index(
    pd.Index([
        format_interval(interval) for interval, _ in sex_filter_grouping.index
    ]))
sex_filter_grouping['age'] = sex_filter_grouping.index

st.markdown('## After grouping')
data_col, graph_col = st.beta_columns(2)

with data_col:
    sex_filter_grouping

base = alt.Chart(sex_filter_grouping).transform_calculate(
    gender=alt.expr.if_(alt.datum.sex == 1, 'Male', 'Female')).properties(
        width=250)

color_scale = alt.Scale(domain=['Male', 'Female'],
                        range=['#1f77b4', '#e377c2'])

left = base.transform_filter(alt.datum.gender == 'Female').encode(
    y=alt.Y('age:O', axis=None),
    x=alt.X('sum(people):Q',
            title='population',
            sort=alt.SortOrder('descending')),
    color=alt.Color('gender:N', scale=color_scale,
                    legend=None)).mark_bar().properties(title='Female')

middle = base.encode(
    y=alt.Y('age:O', axis=None),
    text=alt.Text('age:nominal'),
).mark_text().properties(width=50)

right = base.transform_filter(alt.datum.gender == 'Male').encode(
    y=alt.Y('age:O', axis=None),
    x=alt.X('sum(people):Q', title='population'),
    color=alt.Color('gender:N', scale=color_scale,
                    legend=None)).mark_bar().properties(title='Male')

chart = alt.concat(left, middle, right, spacing=5)

with graph_col:
    st.altair_chart(chart)
