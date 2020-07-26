import streamlit as st

import os
import numpy as np
import pandas as pd
import plotly.express as px

from app.constants import DATA_PATH, map_fluorescence, fluorescence, ranking
from app.inference import predict

@st.cache
def load_data(file_path):
    df = pd.read_csv(file_path)
    df.drop(columns=['dateSet', 'strikethroughPrice', 'skus', 
                     'shapeCode', 'imageUrl', 'detailsPageUrl', 'v360BaseUrl'], inplace=True)
    df.drop_duplicates(inplace=True)
    # reduce fluorescence options
    df['fluorescence'] = df['fluorescence'].map(map_fluorescence)
    # predict diamonds price using trained model
    df['predicted_price'] = np.round(predict(df))
    # compute difference and sort in descending order by (predicted_price - actual_price)
    df['estimate_difference'] = df['predicted_price'] - df['price']
    df.sort_values(by=['estimate_difference'], ascending=False, inplace=True)
    return df
data = load_data(DATA_PATH)

# HEADER
st.title('Simple Diamond Selector')
st.write('Currently only explore Round diamonds within price range of $10K and $30K.')
st.write('Latest model has a mean absolute error of $572 on test set.')
st.write('However, the model shows the biggest erros around borders of the price range.')


# SIDEBAR
# Add a slider
st.sidebar.title("Options")
st.sidebar.info("Use this section to filter down diamonds on the plot.")

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
    label='Show Top N Annotations',
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
fig = px.scatter(filtered_data, x='carat', y='price', 
    symbol='clarity', color='color',
    hover_name='id',
    hover_data=HOVER_DATA
)
for n in range(top_n_annotation):
    x, y, id, pp, ed = filtered_data[['carat', 'price', 'id', 'predicted_price', 
                                  'estimate_difference']].iloc[n].values
    fig.add_annotation(
        x=x,
        y=y,
        text="Estimate: <a href='https://www.bluenile.com/diamond-details/{}'>${}(+{})</a>".format(id, int(pp), int(ed))
    )


st.plotly_chart(fig, use_container_width=True)

st.write("Number of diamonds on the plot: ", filtered_data.shape[0])

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(filtered_data)