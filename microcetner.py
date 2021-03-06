# import libraries for data backend
from modulefinder import STORE_NAME
import re
from tkinter.font import names
from tracemalloc import start
from unicodedata import name
from bs4 import BeautifulSoup
from numpy import choose
from prometheus_client import Metric
import requests
from urllib.request import urlopen
import pandas as pd
from pprint import pprint

# import libraries for streamlit app
from turtle import title
import plotly.express as px
from soupsieve import select
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ----- ----- ----- #
# ----- Data Backend ------ #
# ----- ----- ----- #

# Dictionary Of All Micro Center Stores in The USA
store_ids = {
'CA-Tustin' : 101,
'CO-Denver' : 181,
'GA-Duluth' : 65,
'GA-Marietta' : 41,
'IL-Chicago' : 151,
'IL-Wesmont' : 25,
'KS-Overland Park' : 191,
'MA-Cambridge' : 121,
'MD-Rockville' : 85,
'MI-Madison Heights' : 55,
'MN-St. Louis Park' : 45,
'MO-Brentwood' : 95,
'NJ-North Jersey' : 75,
'NY-Westbury' : 171,
'NY-Brooklyn' : 115,
'NY-Flushing' : 145,
'NY-Yonkers' : 105,
'OH-Columbus' : 141,
'OH-Mayfield Heights' : 51,
'OH-Sharonville' : 71,
'PA-St. Davids' : 61,
'TX-Houston' : 155,
'TX-Dallas' : 131,
'VA-Fairfax' : 81,
}

def get_headers():
    r = requests.get('http://httpbin.org/headers')

    your_head = r.json()
    user_agent = your_head['headers']['User-Agent']

    header_dictionary = {
    'User-Agent' : user_agent
    }
    return header_dictionary

your_header = get_headers()

# Function to Find Soup JSON For Page 1
def find_soup(integer):
    #headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
    headers  = your_header
    URL = f'https://www.microcenter.com/search/search_results.aspx?Ntk=all&sortby=match&rpp=96&N=4294966937&myStore=true&storeid={integer}&page=1'
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

# Function to Find Soup JSON For Page 2
def find_soup2(integer):
    #headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
    headers  = your_header
    URL = f'https://www.microcenter.com/search/search_results.aspx?Ntk=all&sortby=match&rpp=96&N=4294966937&myStore=true&storeid={integer}&page=2'
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

# Function to Find Product Information For One Store
def find_info(soup, integer):
    categories = soup.find_all('a', {'id':f'hypProductH2_{integer}'})
    for d in categories:
        data_name = (d.get('data-name'))
        data_brand = (d.get('data-brand'))
        data_price = (d.get('data-price'))
        href_link = 'https://www.microcenter.com'+ d.get('href')
        return data_name, data_brand, data_price, href_link

# Function to Find Ratings For Store Products
def find_ratings(soup, integer):
    categories = soup.find_all('li', {'id':f'pwrapper_{integer}', 'class' : 'product_wrapper'})
    ratelist = []
    for soup_class in categories:
        reviews = soup_class.find_all('div', {'class' : 'ratingstars'})
        for soup_class in reviews:
            div = soup_class.find_all('div')
            for i in div:
                for j in i:
                    ratelist.append(j.text)

    if ratelist[0] == '0 Reviews':
        stars = 0
        numbers = 0
        return stars, numbers
    else:
        stars = int(str(ratelist[0])[0:1])
        numbers = int(re.findall(r'\d+', ratelist[1])[0])
        return stars, numbers

# Function to Find Inventory Count For Store Products
def find_inventory(soup, integer):
    categories = soup.find_all('li', {'id':f'pwrapper_{integer}', 'class' : 'product_wrapper'})
    for soup_class in categories:
        inventory = soup_class.find_all('div', {'class' : 'stock'})
        for cut in inventory:
            return(str(cut.text))

# Function to Find Maximum Number Of Items Displayed For One Store
def find_item_num(soup):
    emplist = []
    categories = soup.find_all('div', {'id':'bottomPagination', 'class' : 'pagination'})
    for soup_class in categories:
        num = soup_class.find_all('p', {'class' : 'status'})
        for i in num:
            emplist.append(i.text)
            
    numbers = (re.findall(r'\d+', emplist[0]))
    return (int(numbers[2]))

# Function For A List of All Product Information For One Store
def create_list2(store_id, store_integer):
    soup = find_soup(store_id)
    newlist = []
    if store_integer <= 96:
        for integer in range(0,store_integer):
            inventory_count = find_inventory(soup,integer).strip()
            inv_count = (re.findall(r'\d+', inventory_count))
            listprime = {
                'product_name' : find_info(soup,integer)[0],
                'brand_name' : find_info(soup,integer)[1],
                'product_price' : find_info(soup,integer)[2],
                'product_link' : find_info(soup,integer)[3],
                'product_star_count' : find_ratings(soup,integer)[0],
                'product_review_count' : find_ratings(soup,integer)[1],
                'product_inventory_count' : inv_count[0],
                #'product_inventory_name' : inventory_count
            }
            newlist.append(listprime)
    
    else:
        newsoup = find_soup2(store_id)
        second_page_integer = int(store_integer - 96)

        # Getting products between 1 and max items of 96
        for integer in range(0,96):
            inventory_count = find_inventory(soup,integer).strip()
            inv_count = (re.findall(r'\d+', inventory_count))
            listprime = {
                'product_name' : find_info(soup,integer)[0],
                'brand_name' : find_info(soup,integer)[1],
                'product_price' : find_info(soup,integer)[2],
                'product_link' : find_info(soup,integer)[3],
                'product_star_count' : find_ratings(soup,integer)[0],
                'product_review_count' : find_ratings(soup,integer)[1],
                'product_inventory_count' : inv_count[0],
                #'product_inventory_name' : inventory_count
            }
            newlist.append(listprime)
        
        # Getting products between 97 - store_integer
        #newurl = bottom_pagination(find_soup(store_integer))
        
        for integer in range(0,second_page_integer):
            inventory_count = find_inventory(newsoup,integer).strip()
            inv_count = (re.findall(r'\d+', inventory_count))
            listprime = {
                'product_name' : find_info(newsoup,integer)[0],
                'brand_name' : find_info(newsoup,integer)[1],
                'product_price' : find_info(newsoup,integer)[2],
                'product_link' : find_info(newsoup,integer)[3],
                'product_star_count' : find_ratings(newsoup,integer)[0],
                'product_review_count' : find_ratings(newsoup,integer)[1],
                'product_inventory_count' : inv_count[0],
                #'product_inventory_name' : inventory_count
            }
            newlist.append(listprime)
    return newlist

# Function For Pandas Dataframe
def get_df(store_list):
    store_data = pd.DataFrame(store_list, columns=['product_name', 'brand_name','product_price', 'product_link', 'product_star_count','product_review_count', 'product_inventory_count'])
    return store_data

# Final Call Function
@st.cache(allow_output_mutation=True, show_spinner=False)
def get_data(store_name):
        store_name_id = find_soup(store_ids[store_name])
        item_num = find_item_num(store_name_id)

        store_df = get_df(create_list2(store_ids[store_name],item_num))
        store_df['product_inventory_count'] = store_df['product_inventory_count'].astype('int64')
        store_df['product_price'] = store_df['product_price'].astype('float')
        return store_df

# ----- ----- ----- #
# ----- Data Charts ------ #
# ----- ----- ----- #

def pie_chart(df):
    pie_data = df['product_inventory_count'].to_list()
    pie_labels = df.index
    colors = sns.color_palette("hls",8)

    pie_label_size = pie_labels.size
    explode_list = []
    for i in range(0,pie_label_size):
        explode_list.append(0.02)

    max_value = max(pie_data)
    max_value_index = pie_data.index(max_value)
    explode_list[max_value_index] = 0.03

    pie_explode = explode_list

    plt.pie(pie_data, labels=pie_labels, colors=colors, autopct = '%0.0f%%', explode=explode_list, shadow= False, startangle=90,textprops={'color': 'Black', 'fontsize':25}, wedgeprops={'linewidth':6},center=(0.1,0.1), rotatelabels=True)
    plt.rcParams["figure.figsize"] = [50,50]

    gif_runner = st.image('processing.gif')

    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()

    gif_runner.empty()

def bar_chart(df):
    top_five_price = df.sort_values(by='product_price', ascending=False).nlargest(5, 'product_price')

    colors = sns.color_palette("hls",8)
    #ax, fig = plt.subplots(figsize=[15,7])
    #sns.barplot(x=top_five_price.index, y = 'product_price', data = top_five_price, palette= colors)

    fig = plt.subplots(figsize=[15,7])
    ax = sns.barplot(x=top_five_price.index, y = 'product_price', data = top_five_price, palette= colors)

    for bar, label in zip(ax.patches, top_five_price['product_price']):
        x = bar.get_x()
        width = bar.get_width()
        height = bar.get_height()
        ax.text(x+width/2., height + 1, label, ha="center") 

    gif_runner = st.image('processing.gif')

    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()

    gif_runner.empty()

def get_label_rotation(angle, offset):
    # Rotation must be specified in degrees :(
    rotation = np.rad2deg(angle + offset)
    if angle <= np.pi:
        alignment = "right"
        rotation = rotation + 180
    else: 
        alignment = "left"
    return rotation, alignment

def add_labels(angles, values, labels, offset, ax):
    
    # This is the space between the end of the bar and the label
    padding = 4
    
    # Iterate over angles, values, and labels, to add all of them.
    for angle, value, label, in zip(angles, values, labels):
        angle = angle
        
        # Obtain text rotation and alignment
        rotation, alignment = get_label_rotation(angle, offset)

        # And finally add the text
        ax.text(
            x=angle, 
            y=value + padding, 
            s=label, 
            ha=alignment, 
            va="center", 
            rotation=rotation, 
            rotation_mode="anchor"
        ) 

def grouped_bar_chart(test_df):
    test_df_sorted = (test_df.groupby(['brand_name']).apply(lambda x: x.sort_values(["product_review_count"], ascending = False)).reset_index(drop=True))

    VALUES = test_df_sorted["product_review_count"].values 
    LABELS = test_df_sorted["product_name"].values
    GROUP = test_df_sorted["brand_name"].values

    PAD = 3
    ANGLES_N = len(VALUES) + PAD * len(np.unique(GROUP))

    ANGLES = np.linspace(0, 2 * np.pi, num=ANGLES_N, endpoint=False)
    WIDTH = (2 * np.pi) / len(ANGLES)


    OFFSET = np.pi / 2

    # Specify offset
    #ax.set_theta_offset(OFFSET)
    offset = 0
    IDXS = []

    GROUPS_SIZE = []
    unique, counts = np.unique(GROUP, return_counts=True)
    result = np.column_stack((unique, counts))

    for i in range(0, len(result)):
        GROUPS_SIZE.append(result[i][1])
    for size in GROUPS_SIZE:
        IDXS += list(range(offset + PAD, offset + size + PAD))
        offset += size + PAD

    fig, ax = plt.subplots(figsize=(20, 10), subplot_kw={"projection": "polar"})

    ax.set_theta_offset(OFFSET)
    ax.set_ylim(-100, 100)
    ax.set_frame_on(False)
    ax.xaxis.grid(False)
    ax.yaxis.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])

    GROUPS_SIZE = []
    unique, counts = np.unique(GROUP, return_counts=True)
    result = np.column_stack((unique, counts))

    for i in range(0, len(result)):
        GROUPS_SIZE.append(result[i][1])
    COLORS = [f"C{i}" for i, size in enumerate(GROUPS_SIZE) for _ in range(size)]

    # Add bars to represent ...
    ax.bar(
        ANGLES[IDXS], VALUES, width=WIDTH, color=COLORS, 
        edgecolor="white", linewidth=2
    )

    add_labels(ANGLES[IDXS], VALUES, LABELS, OFFSET, ax)

    offset = 0 
    test_list = unique.tolist()
    for group, size in zip(test_list, GROUPS_SIZE):
        # Add line below bars
        x1 = np.linspace(ANGLES[offset + PAD], ANGLES[offset + size + PAD - 1], num=50)
        ax.plot(x1, [-5] * 50, color="#333333")
        
        # Add text to indicate group
        ax.text(
            np.mean(x1), -20, group, color="#333333", fontsize=14, 
            fontweight="bold", ha="center", va="center"
        )
        
        # Add reference lines at 20, 40, 60, and 80
        x2 = np.linspace(ANGLES[offset], ANGLES[offset + PAD - 1], num=50)
        ax.plot(x2, [20] * 50, color="#bebebe", lw=0.8)
        ax.plot(x2, [40] * 50, color="#bebebe", lw=0.8)
        ax.plot(x2, [60] * 50, color="#bebebe", lw=0.8)
        ax.plot(x2, [80] * 50, color="#bebebe", lw=0.8)
        
        offset += size + PAD

    gif_runner = st.image('processing.gif')

    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()

    gif_runner.empty()

def most_expensive(test_df):
    prices = test_df.sort_values(by=['product_price'], ascending=False).head(10).sort_values('product_price')
    my_range = range(0,len(prices))

    fig = plt.figure(figsize=(14,10))

    plt.hlines(y=prices['product_name'], xmin=0, xmax=prices['product_price'], color='black')
    plt.plot(prices['product_price'], my_range, "o", color = 'black')
    plt.xlabel('Price (USD)', fontsize=20)
    plt.ylabel('Product Name',fontsize=20)
    plt.yticks(fontsize=15)
    plt.xticks(fontsize=15)
    plt.xlim(0,max(prices['product_price'])+100)
    plt.grid()
    plt.title("Most Expensive Products", fontsize=20, x=0.5,y=1.02)

    gif_runner = st.image('processing.gif')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()
    gif_runner.empty()

def least_expensive(test_df):
    prices = test_df.sort_values(by=['product_price'], ascending=True).head(10).sort_values('product_price')
    my_range = range(0,len(prices))

    fig = plt.figure(figsize=(14,10))

    plt.hlines(y=prices['product_name'], xmin=0, xmax=prices['product_price'], color='black')
    plt.plot(prices['product_price'], my_range, "o", color = 'black')
    plt.xlabel('Price (USD)', fontsize=20)
    plt.ylabel('Product Name',fontsize=20)
    plt.yticks(fontsize=15)
    plt.xticks(fontsize=15)
    plt.xlim(0,max(prices['product_price'])+100)
    plt.grid()
    plt.title("Least Expensive Products", fontsize=20, x=0.5,y=1.02)

    gif_runner = st.image('processing.gif')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()
    gif_runner.empty()

# ----- ----- ----- #
# ----- ----- ----- #
# ----- ----- ----- #
# ----- ----- ----- #
# ----- ----- ----- #
# ----- ----- ----- #
# ----- Main App ----- #
# ----- ----- ----- #
# ----- ----- ----- #
# ----- ----- ----- #
# ----- ----- ----- #
# ----- ----- ----- #
# ----- ----- ----- #

# ----- TITLE BAR ----- # 
st.set_page_config(page_title="Micro Center Dashboard", page_icon=":computer:", layout="wide")

# ----- Main Title ------ #
st.title(":computer: Micro Center Graphics Processing Units :computer:")
st.markdown("##")

# ----- BACKGROUND ----- # 
col1, col2, col3 = st.columns([0.5,4,0.5])
with col2:
    main_gif = st.image('main.gif', use_column_width=True)

# ----- SIDE BAR ----- # 
st.sidebar.header("Filters")

# ----- Select Store ----- #
mystore = store_ids.keys()
dropdown = st.sidebar.selectbox("Please Select Micro Center Store:", mystore)
start_execution = st.sidebar.button('Get Data')

# ----- Initialize Session State ------ #
if "load_state" not in st.session_state:
    st.session_state.load_state = False

# ----- Getting Pandas Dataframe and Display Results ------ #
if start_execution or st.session_state.load_state:
    st.session_state.load_state = True
    with col2:
        main_gif.empty()
        gif_runner = st.image('processing.gif')
        st.session_state['data_frame'] = get_data(dropdown)
        data_frame = st.session_state['data_frame']
        data_frame['product_price'] = data_frame['product_price'].astype(float)
        data_frame['product_inventory_count'] = data_frame['product_inventory_count'].astype(int) 
        gif_runner.empty()   

    # ----- Top KPI ------
    max_high = data_frame['product_price'].max()
    min_low = data_frame['product_price'].min()
    average_price = round(data_frame['product_price'].mean(),2)
    median_price = data_frame['product_price'].median()
    total_inventory = data_frame['product_inventory_count'].sum()
    average_review = round(data_frame['product_star_count'].mean(),2)
    total_review_count = data_frame['product_review_count'].sum()

    # ----- SIDE BAR ----- #
    st.sidebar.subheader('Brand')
    selected_brands = st.sidebar.multiselect(label = "", options = data_frame['brand_name'].unique())
    st.sidebar.subheader('Price')
    min_value = st.sidebar.slider(label="Minimum Price", min_value= round(min_low), max_value=round(max_high))
    if min_value:
        max_value = st.sidebar.slider(label="Maximum Price", min_value= round(min_value), max_value=round(max_high))
    filter_inventory = st.sidebar.radio(label='Filter Inventory', options= ('Include All Items', 'Exclude Sold Out Items'))
    filter_reviews = st.sidebar.radio(label='Filter Reviews', options= ('Include All Items', 'Exclude Items With No Reviews'))    
    filter_data = st.sidebar.button('Filter Products')    

    selected_store = [key for key, value in store_ids.items() if value == store_ids[dropdown]][0]
    st.header(f"Data Descriptions For: {selected_store}")
    left_column, middle_column, right_column = st.columns(3)
    with left_column:
        st.header(":dollar: Price :dollar:")
        st.metric(label="Least Expensive", value = f"${min_low}")
        st.metric(label="Most Expensive", value = f"${max_high}")
        st.metric(label="Average Price", value = f"${average_price}")
        st.metric(label="Median Price", value = f"${median_price}")
    with middle_column:
        st.header(":house: Inventory :house:")
        st.metric(label="Total Products Sold", value = data_frame['product_name'].count())
        st.metric(label="Total Inventory Count", value = total_inventory)
    with right_column:
        st.header(":star: Reviews :star:")
        st.metric(label="Average Reviews", value = average_review)
        st.metric(label="Total Reviews", value = total_review_count)

    st.markdown("---")
    st.header("All Products For Your Store :point_down:")
    st.dataframe(data_frame)

    most_expensive(data_frame)

    least_expensive(data_frame)    

    # ----- Main Dashboard ----- # 
    
    # ----- Initalize Session State 2 ----- # 
    if "load_state2" not in st.session_state:
        st.session_state.load_state2 = False
        data_frame_prime = pd.DataFrame

    if filter_data or st.session_state.load_state2:
        st.session_state.load_state2 = True
        if filter_inventory == 'Include All Items':
            data_frame_prime = data_frame[data_frame['brand_name'].isin(selected_brands)]
            data_frame_prime = data_frame_prime[data_frame_prime['product_price'] > min_value]
            data_frame_prime = data_frame_prime[data_frame_prime['product_price'] < max_value]
            if filter_reviews == 'Include All Items':
                data_frame_prime = data_frame_prime
            else:
                data_frame_prime = data_frame_prime[data_frame_prime['product_review_count'] > 0]
        else:
            data_frame_prime = data_frame[data_frame['product_inventory_count']>0]
            data_frame_prime = data_frame_prime[data_frame['brand_name'].isin(selected_brands)]
            data_frame_prime = data_frame_prime[data_frame_prime['product_price'] > min_value]
            data_frame_prime = data_frame_prime[data_frame_prime['product_price'] < max_value]
            if filter_reviews == 'Include All Items':
                data_frame_prime = data_frame_prime
            else:
                data_frame_prime = data_frame_prime[data_frame_prime['product_review_count'] > 0] 

        #data_frame_prime = data_frame[data_frame['brand_name'].isin(selected_brands)]
        #data_frame_prime = data_frame_prime[data_frame_prime['product_price'] > min_value]
        #data_frame_prime = data_frame_prime[data_frame_prime['product_price'] < max_value]

        # ----- Filtered KPI ------ #
        max_high_prime = data_frame_prime['product_price'].max()
        min_low_prime = data_frame_prime['product_price'].min()
        average_price_prime = round(data_frame_prime['product_price'].mean(),2)
        median_price_prime = data_frame_prime['product_price'].median()
        total_inventory_prime = data_frame_prime['product_inventory_count'].sum()
        average_review_prime = round(data_frame_prime['product_star_count'].mean(),2)
        total_review_count_prime = data_frame_prime['product_review_count'].sum()

        st.markdown("---")
        st.header(f"Data Descriptions For: {selected_brands} With Prices Between {min_value} And {max_value} USD")
        left_column, middle_column, right_column = st.columns(3)
        with left_column:
            st.header(":dollar: Price :dollar:")
            st.metric(label="Least Expensive", value = f"${min_low_prime}")
            st.metric(label="Most Expensive", value = f"${max_high_prime}")
            st.metric(label="Average Price", value = f"${average_price_prime}")
            st.metric(label="Median Price", value = f"${median_price_prime}")
        with middle_column:
            st.header(":house: Inventory :house:")
            st.metric(label="Total Products Sold", value = data_frame_prime['product_name'].count())
            st.metric(label="Total Inventory Count", value = total_inventory_prime)
        with right_column:
            st.header(":star: Reviews :star:")
            st.metric(label="Average Reviews", value = average_review_prime)
            st.metric(label="Total Reviews", value = total_review_count_prime)

        # ----- Pie Chart ------ #
        # Distribution of Product Inventory
        grouped_df = data_frame_prime.groupby(by=['brand_name']).sum()

        graph_col1, graph_col2 = st.columns(2)

        with graph_col1:
            st.header(':bank: Distribution of Inventory :bank:')
            pie_chart(grouped_df)

        # ----- Bar Plot ------ #
        # Top Most Expensive Brand
        with graph_col2:
            st.header(':moneybag: Distribution of Price :moneybag:')
            bar_chart(grouped_df)

        # ----- Grouped Bar Chart ------ #
        # Total Review Count
        st.header(':star2: Distribution of Review Count :star2:')
        grouped_bar_chart(data_frame_prime)


        st.header("Your Products :point_down:")
        st.dataframe(data_frame_prime)
        

else:
    print("")




















# ----- Hide Streamlit Style ------ #
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_st_style, unsafe_allow_html=True)