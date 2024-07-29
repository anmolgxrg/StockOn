import streamlit as st
import pandas as pd
import io
import regex as re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import openai
import time


# Set OpenAI API key
# openai.api_key = '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'

# Function to clean and correct item names using OpenAI
# def clean_and_correct_name(name):
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": f"Correct and complete the following grocery store product name, and expand any acronyms, reply back with only name nothing else: {name}"}
#             ]
#         )
#         corrected_name = response.choices[0].message['content'].strip()
#         return corrected_name
#     except openai.error.RateLimitError:
#         st.error("Rate limit exceeded. Please try again later.")
#         return name

# Set page configuration to wide format
st.set_page_config(layout="wide", page_title="StockOn", page_icon="https://www.psu.edu/favicon.ico")


def app():
    st.title('Order')
    st.write('Welcome to the Order page!')

# Style for the app
st.markdown(
    """
    <style>
    html, body {
        padding: 0;
        margin: 0;
    }
    .title-wrapper {
        font-size: 3em; 
        color: transparent; 
        margin: 10px 60px;
        font-weight: bold; 
        background-image: linear-gradient(to right, rgb(2, 0, 36) 0%, rgb(63, 76, 183) 35%, rgb(0, 212, 255) 100%);
        -webkit-background-clip: text;
        background-clip: text;
    }
    .data-table th, .data-table td {
        padding: 10px;
        text-align: left;
    }
    .data-table th {
        background-color: #f4f4f4;
    }
    </style>
    """,
    unsafe_allow_html=True
)

img_1 = "logo.png"

header_col_1, header_col_2 = st.columns([1, 10])
header_col_1.image(img_1, width=150, use_column_width=False)
header_col_2.markdown('<div class="title-wrapper">StockOn</div>', unsafe_allow_html=True)

# Storage areas for "Provisions"
provisions_storage_areas = {
    "HERSHEY ICE CREAM FRZ": "Hershey Ice Cream Freezer",
    "FREEZER MERCHANDISER": "Freezer Merchandise",
    "HEALTH/BEAUTY": "Health and Beauty",
    "RETAIL FREEZER BERKEY": "Retail Freezer",
    "RETAIL SHELVES": "Retail Shelves",
    "PEPSI COOLER": "Pepsi Cooler",
    "REFRIGERATED MERCHANDISER": "Refrigerated Merchandise",
    "SUPPLIES": "Supplies",
    "SPECIAL ORDERS": "Special Orders",
    "CSTR PEPSI": "Pepsi",
    "CSTR CHIP VENDORS": "Chip Vendors",
    "CSTR FROZEN": "Frozen",
    "CSTR COOLER": "Cooler",
    "CSTR GROCERY & SUPPLIES": "Grocery & Supplies",
    "CSTR SWT&SALTY SNACKS&CANDY": "Sweet & Salty Snacks & Candy",
    "NEW ITEMS": "New Items"
}

# Create tabs
tab1, tab2 = st.tabs(["Upload/Edit", "Preview/Download"])

def clean_hershey_item(name):
    match = re.match(r"\$ HERSHEY \d+OZ (.+)", name)
    if match:
        return match.group(1)
    return name

def fuzzy_search(term, choices, limit=5):
    return process.extract(term, choices, limit=limit)

with tab1:
    # Upload Excel file
    st.title("Upload Excel File")
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)

        # Extract Storage Number and Storage Area Raw
        df[['Storage Number', 'Storage Area Raw']] = df['Storage Area / Storage Sequence'].str.extract(r'(\d{2})\s(.+)/\d{4}')

        # Apply the updated dictionary to map storage area names
        df['Storage Area'] = df['Storage Area Raw'].map(provisions_storage_areas)

        # Add Order Quantity column if not present
        if 'Order Quantity' not in df.columns:
            df['Order Quantity'] = 0

        # Ensure Order Quantity is an integer column and handle NaN values
        df['Order Quantity'] = df['Order Quantity'].fillna(0).astype(int)

        # Remove dollar sign from item names and split Name into Item and Quantity
        df['Name'] = df['Name'].str.replace('$', '', regex=False)
        df['Name'] = df.apply(lambda x: clean_hershey_item(x['Name']) if x['Storage Area'] == 'Hershey Ice Cream Freezer' else x['Name'], axis=1)
        
        # Apply clean_and_correct_name only to the first 5 items
        for i in range(min(5, len(df))):
            # df.at[i, 'Name'] = clean_and_correct_name(df.at[i, 'Name'])
            time.sleep(1)  # Add delay between API calls
        
        name_quantity = df['Name'].str.extract(r'(.+?)\s(\d+\.?\d*\s?(OZ|CT|L|ML)?)')
        df['Item Name'] = name_quantity[0]
        df['Quantity'] = name_quantity[1]

        # Filter out rows with nan in 'Item Name'
        df = df.dropna(subset=['Item Name'])

        # Add End Count column
        df['End Count'] = df['End Count'].fillna(0).astype(int) if 'End Count' in df.columns else 0

        # Location Selector
        location = st.selectbox("Select Location", ["Stacks", "Outpost", "Provisions"])

        # Filter by Order Category
        if location == "Provisions":
            storage_areas = list(provisions_storage_areas.values())
        else:
            storage_areas = [""]  # Placeholder for other locations

        selected_category = st.selectbox("Select Storage Area", storage_areas)

        if selected_category:
            filtered_df = df[df['Storage Area'] == selected_category]

            # Searchable item names
            search_term = st.text_input("Search Item Names")
            if search_term:
                item_names = filtered_df['Item Name'].tolist()
                fuzzy_results = fuzzy_search(search_term, item_names)
                matched_names = [result[0] for result in fuzzy_results]
                filtered_df = filtered_df[filtered_df['Item Name'].isin(matched_names)]

            # Display the table with editable order quantity and side-by-side input
            st.markdown(f"<h3>{location} Items</h3>", unsafe_allow_html=True)
            for index, row in filtered_df.iterrows():
                st.markdown(
                    f"<div style='display: flex; justify-content: space-between;'><div>{row['Item Name']}</div><div>{row['Quantity']}</div><div>{row['End Count']}</div><div>{st.number_input('', min_value=0, value=int(row['Order Quantity']), key='{}_{}'.format(row['Item Name'], index))}</div></div>",
                    unsafe_allow_html=True
                )

with tab2:
    if uploaded_file:
        st.header("Data Preview")

        preview_df = filtered_df[['Item Name', 'Quantity', 'End Count', 'Order Quantity']]

        st.dataframe(preview_df)

        # Add a download button to download the DataFrame as an Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            preview_df.to_excel(writer, index=False, sheet_name='Sheet1')
        output.seek(0)

        st.download_button(
            label="Download Modified Data",
            data=output,
            file_name="modified_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
