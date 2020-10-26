import streamlit as st

import os
import numpy as np
import pandas as pd
import plotly.express as px

from src.constants import DATA_DIR, map_fluorescence, fluorescence, ranking
from src.fetch_data import update_data
from src.inference import predict
from src.paginator import paginator

@st.cache
def load_data(data_path):
    file_path, download_status = update_data(data_path)
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
    return df, download_status
with st.spinner('Retreiving the latest data file...'):
    data, resp = load_data(DATA_DIR)
st.info(resp)

# HEADER
st.title('💎Simple Diamond Selector💎')
st.write('Welcome :wave: Currently we only consider **Round** diamonds with price between *$10K* and *$30K*. The latest model was trained without limiting price range, and has a mean absolute error of *$572* on test set. The model shows the biggest errors around borders of the price range.')
st.write('*Please also note:* we found the model predicts very high price on some diamonds while actual price is low, due to additional assessments provided by the GIA reports.')
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
sort_image_by = st.sidebar.selectbox(
    label='Sort diamonds by (descending)',
    options=('Estimated Difference', 'Predicted Price', 'Actual Price', 'Carat')
)
SORTCOL_MAP = {
    'Actual Price': 'price',
    'Carat': 'carat',
    'Estimated Difference': 'estimate_difference',
    'Predicted Price': 'predicted_price'
}

filtered_data = data[
    (data['carat'] >= carat_filter[0]) & (data['carat'] <= carat_filter[1]) &
    (data['price'] >= price_filter[0]) & (data['price'] <= price_filter[1]) &
    (data['color'].isin(color_filter)) &
    (data['clarity'].isin(clarity_filter)) &
    (data['fluorescence'].isin(fluorescence_filter))
].sort_values(by=SORTCOL_MAP[sort_image_by], ascending=False)

HOVER_DATA = ['cut', 'fluorescence', 'polish', 'symmetry', 'table', 'predicted_price']  

# MAIN CANVAS
st.write("Number of diamonds in selection: ", filtered_data.shape[0])

# Settings
MAIN_COLS = ['carat', 'price', 'id', 'predicted_price', 
             'estimate_difference', 'visualizationImageUrl']
ATTR_COLS = ['color', 'clarity', 'cut', 'fluorescence']
DETAILS_URL = 'https://www.bluenile.com/diamond-details/{}'


def extract_row(row):
    x, y, id, pp, ed, image = row[MAIN_COLS].values
    color, clarity, cut, fluorescence = row[ATTR_COLS].values
    url = DETAILS_URL.format(id)
    return (x, y, id, pp, ed, image, 
        color, clarity, cut, fluorescence, url)

# Show list of diamonds
n = filtered_data.shape[0]
for i, row in paginator("Select a page", list(range(n)), items_per_page=5, on_sidebar=False):
    row = filtered_data.iloc[i]
    x, y, id, pp, ed, image, color, clarity, cut, fluorescence, url = extract_row(row)
    # show list of diamonds
    st.write(
        '[![image]({})]({})'.format(image, url),
        'Carat: {}, Price: ${}; Suggested: ${}'.format(x, y, pp),
        '  \nID: [{}]({}) Color **{}**, Clarity **{}**, Cut **{}**, Fluorescence **{}**'.format(id, url, color, clarity, cut, fluorescence))

# Base chart
fig = px.scatter(filtered_data, x='carat', y='price', 
    symbol='clarity', color='color',
    hover_name='id',
    hover_data=HOVER_DATA
)
# Add annotation to top 5 suggested
for i in range(5):
    row = filtered_data.iloc[i]
    x, y, id, pp, ed, image, color, clarity, cut, fluorescence, url = extract_row(row)
    # add other attributes to the base chart
    fig.add_annotation(
        x=x, y=y, text="<a href='{}'>${}(+{})</a>".format(url, y, ed)
    )

st.markdown('---')
st.subheader('Diamonds on one Scatterplot')
st.markdown("My wife really doesn't like this chart. She said it is confusing, and unless I explained to her what is going on, she could not understand anything here. I tried to convince her this is a good summary of the information, but fine, it's alright.")
st.plotly_chart(fig, use_container_width=True)

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(filtered_data)