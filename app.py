import streamlit as st

import os
import numpy as np
import pandas as pd
import plotly.express as px

from src.constants import DATA_PATH, map_fluorescence, fluorescence, ranking
from src.inference import predict

@st.cache
def load_data(file_path):
    df = pd.read_csv(file_path)
    df.drop(columns=['dateSet', 'strikethroughPrice', 'skus', 'v360BaseUrl',
                     'shapeCode', 'imageUrl', 'detailsPageUrl'], inplace=True)
    df.drop_duplicates(inplace=True)
    # keep only diamonds with images
    df.dropna(subset=['visualizationImageUrl'], inplace=True)
    # reduce fluorescence options
    df['fluorescence'] = df['fluorescence'].map(map_fluorescence)
    # predict diamonds price using trained model
    df['predicted_price'] = predict(df).astype(int)
    # compute difference and sort in descending order by (predicted_price - actual_price)
    df['estimate_difference'] = df['predicted_price'] - df['price']
    df.sort_values(by=['estimate_difference'], ascending=False, inplace=True)
    return df
data = load_data(DATA_PATH)

# HEADER
st.title('💎Simple Diamond Selector💎')
st.write('Welcome :wave: Currently we only consider **Round** diamonds within price range of *$10K and $30K*. The latest model has a mean absolute error of *$572* on test set. The model shows the biggest errors around borders of the price range.')
st.write('*Please also note:* we found the model predicts very high price on some diamonds while actual price is low, due to additional assessments provided by the GIA reports.')
st.write('*Dataset Date: 2020-07-20*')
st.write('---')


# SIDEBAR
# Add a slider
st.sidebar.title("Options")
st.sidebar.info("Use this section to filter down diamonds.")

carat_filter = st.sidebar.slider(
    label='Carat',
    min_value=1.0, max_value=4.0, value=(1.5, 3.0), step=0.01, format='%f'
)
price_filter = st.sidebar.slider(
    label='Price',
    min_value=1e4, max_value=3e4, value=(12000.0, 25000.0), step=100., format='%f'
)
color_filter = st.sidebar.multiselect(
    label='Color',
    options=ranking['color'],
    default=ranking['color'][-3:]
)
clarity_filter = st.sidebar.multiselect(
    label='Clarity',
    options=ranking['clarity'],
    default=ranking['clarity'][-3:]
)
fluorescence_filter = st.sidebar.multiselect(
    label='Fluorescence',
    options=fluorescence,
    default=fluorescence[-1:]
)
top_n_annotation = st.sidebar.slider(
    label='Show Top N Recommendations',
    min_value=1, max_value=10, value=5, step=1
)


filtered_data = data[
    (data['carat'] >= carat_filter[0]) & (data['carat'] <= carat_filter[1]) &
    (data['price'] >= price_filter[0]) & (data['price'] <= price_filter[1]) &
    (data['color'].isin(color_filter)) &
    (data['clarity'].isin(clarity_filter)) &
    (data['fluorescence'].isin(fluorescence_filter))
]

HOVER_DATA = ['cut', 'fluorescence', 'polish', 'symmetry', 'table', 'predicted_price']  

# MAIN CANVAS
# Scatterplot
st.write("Number of diamonds in selection: ", filtered_data.shape[0], '(Showing top: ', top_n_annotation, ')')

fig = px.scatter(filtered_data, x='carat', y='price', 
    symbol='clarity', color='color',
    hover_name='id',
    hover_data=HOVER_DATA
)

for n in range(top_n_annotation):
    row = filtered_data.iloc[n]
    x, y, id, pp, ed, image = row[['carat', 'price', 'id', 'predicted_price', 
                                   'estimate_difference', 'visualizationImageUrl']].values
    url = 'https://www.bluenile.com/diamond-details/{}'.format(id)
    # other attributes
    color, clarity, cut, fluorescence = row[['color', 'clarity', 'cut', 'fluorescence']].values
    fig.add_annotation(
        x=x,
        y=y,
        text="<a href='{}'>${}(+{})</a>".format(url, y, ed)
    )
    st.write(
        '[![image]({})]({})'.format(image, url),
        'Carat: {}, Price: ${}; Suggested: ${}'.format(x, y, pp),
        '  \nID: [{}]({}) Color **{}**, Clarity **{}**, Cut **{}**, Fluorescence **{}**'.format(id, url, color, clarity, cut, fluorescence))

st.markdown('---')
st.subheader('Diamonds on one Scatterplot')
st.markdown("My wife really doesn't like this chart. She said it is confusing, and unless I explained to her what is going on, she could not understand anything here. I tried to convince her this is a good summary of the information, but fine, it's alright.")
st.plotly_chart(fig, use_container_width=True)

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(filtered_data)