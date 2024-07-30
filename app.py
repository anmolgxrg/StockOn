import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
import base64

# Set page configuration to wide format
st.set_page_config(layout="wide", page_title="StockOn", page_icon="/favicon.ico")

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
    </style>
    """,
    unsafe_allow_html=True
)

# Define categories and their corresponding item numbers
categories_items = {
    "DRY STORAGE - PAPER & PACKAGING": ["1187", "2268", "1479", "3090", "1714", "1707", "2152", "0905", "3497", "6792", "3381", "4638", "3299", "7552", "3634", "3635", "3636", "3253", "1665", "1570", "4782", "1220", "1395", "3189", "3288", "3327", "3328", "1779", "4129", "3659", "3347", "3348", "4969", "0890", "4972", "3221", "4970", "4973"],
    "DRY STORAGE - FOOD": ["4552", "0404", "4892", "0407", "2276", "0099", "0193", "0200", "0205", "0496", "0427", "4622", "0421", "3505", "0062", "0399", "1392", "0350", "0348", "0347", "4227", "1817", "0314", "0330", "0120", "0663", "4876", "1247", "0211", "4114", "0087", "4763", "0244", "1474", "6398", "2214", "1390", "0018", "4071", "0057", "0113", "2459", "0117", "0118", "0108", "0443", "2213", "4826", "3515", "0134", "0098", "0298", "1643", "1271", "0275", "1145", "0284", "0285", "0288", "0287", "0286", "1444", "0282", "0280", "4712", "0259", "0256", "1334", "0250", "4387", "0241", "1900", "3147", "4003", "1626", "4675", "1223", "1396", "0093", "4086", "2568", "0208", "0262", "0238", "0276", "4386", "1422"],
    "WALK-IN FREEZER (MEATS)": ["0419", "2260", "4219", "0584", "0701", "0709", "3373", "4995", "0614", "4589", "0697", "2926", "0714", "0713", "3605", "0554"],
    "WALK-IN FREEZER": ["4354", "0501", "4692", "3295", "0390", "4832", "1045", "1455", "0313", "4921", "4511", "4548", "4540", "4533", "0511", "3552", "3599", "3571", "3522", "3585", "2151", "2881", "1192", "2040", "0582"],
    "WALK-IN": ["1568", "0010", "1941", "1486", "2283", "0984", "4798", "1302", "0328", "0578", "0464", "4940", "0457", "3719", "0021", "4042", "0456", "0926", "0631", "0231", "1526", "0469", "0576", "0168", "4021", "1400"],
    "SUPPLIES": ["4801", "3026", "0971", "6328", "2344", "7781", "2929", "2930", "2931", "2935", "2936", "3424", "4311", "3245", "3021", "3852", "1320", "3265", "3846", "1018", "1015", "4281", "4724", "4584", "4272", "3170", "4025", "4004", "4593", "4534", "4495"]
}

# Path to the Excel file
excel_file_path = 'THE OUTPOST ORDER FORM 01042024 copy.xlsx'

# Tabs for viewing and managing categories
tab1, tab2 = st.tabs(["View Data", "Manage Categories"])

def adjust_order_quantity(data, index, adjustment):
    current_quantity = data.at[index, 'Order Quantity']
    if pd.isna(current_quantity):
        current_quantity = 0
    new_quantity = max(0, current_quantity + adjustment)
    data.at[index, 'Order Quantity'] = new_quantity
    if adjustment > 0:
        data.at[index, 'Order Date'] = datetime.now().strftime('%Y-%m-%d')

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="updated_sheet.xlsx">Download Updated Sheet</a>'

def to_excel(data):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    data.to_excel(writer, index=False, sheet_name=sheet)
    writer.close()
    processed_data = output.getvalue()
    return processed_data

if os.path.exists(excel_file_path):
    with tab1:
        # Load the Excel file
        excel_data = pd.ExcelFile(excel_file_path)

        # Dropdown to select the sheet
        sheet = st.selectbox('Select Sheet', excel_data.sheet_names)

        # Load data from the selected sheet
        sheet_data = pd.read_excel(excel_file_path, sheet_name=sheet)

        # Define column renaming mapping
        columns_rename_mapping = {
            sheet_data.columns[0]: "Item Number",
            sheet_data.columns[1]: "Item Description",
            sheet_data.columns[2]: "Unit Size",
            sheet_data.columns[3]: "Order Date",
            sheet_data.columns[4]: "Order Quantity"
        }

        # Rename columns
        sheet_data.rename(columns=columns_rename_mapping, inplace=True)

        # Dropdown to select the category
        category = st.selectbox('Select Category', list(categories_items.keys()))

        # Filter the data based on the selected category
        item_numbers = categories_items[category]
        filtered_data = sheet_data[sheet_data["Item Number"].astype(str).isin(item_numbers)]

        # Display the filtered data with buttons
        st.write("<style>th, td {padding: 10px;} th {background-color: #f4f4f4;} table {width: 100%;}</style>", unsafe_allow_html=True)
        st.write("<table class='data-table'>", unsafe_allow_html=True)
        st.write("<tr><th>Item Number</th><th>Item Description</th><th>Unit Size</th><th>Order Date</th><th>Order Quantity</th><th>Actions</th></tr>", unsafe_allow_html=True)
        for index, row in filtered_data.iterrows():
            st.write("<tr>", unsafe_allow_html=True)
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.write(row['Item Number'])
            col2.write(row['Item Description'])
            col3.write(row['Unit Size'])
            col4.write(row['Order Date'])
            col5.write(row['Order Quantity'])
            with col6:
                if st.button("+", key=f"plus_{index}"):
                    adjust_order_quantity(sheet_data, index, 1)
                if st.button("-", key=f"minus_{index}"):
                    adjust_order_quantity(sheet_data, index, -1)
                st.write("<br>", unsafe_allow_html=True)
            st.write("</tr>", unsafe_allow_html=True)

        # Download button for the updated sheet
        if st.button("Download Updated Sheet"):
            st.markdown(get_table_download_link(sheet_data), unsafe_allow_html=True)
else:
    st.info("Excel file not found. Please make sure the file exists in the same directory.")

with tab2:
    st.write("Manage Categories and Items")

    # Display existing categories and their items
    st.write("### Existing Categories")
    categories_to_delete = []
    categories_to_update = {}

    for category, items in list(categories_items.items()):
        with st.expander(f"{category}"):
            st.write(f"**Item Numbers**: {', '.join(map(str, items))}")

            # Form to edit category
            new_category_name = st.text_input(f"Edit Name for '{category}'", category, key=f"name_{category}")
            new_category_items = st.text_area(f"Edit Item Numbers for '{category}' (comma separated)", ', '.join(map(str, items)), key=f"items_{category}").split(',')

            if st.button(f"Update '{category}'", key=f"update_{category}"):
                if new_category_name and new_category_items:
                    try:
                        new_category_items = list(map(str.strip, new_category_items))
                        categories_to_update[category] = (new_category_name, new_category_items)
                        st.success(f"Category '{new_category_name}' updated successfully!")
                    except ValueError:
                        st.error("Please enter valid item numbers.")
                else:
                    st.error("Please fill in both fields.")

            if st.button(f"Delete '{category}'", key=f"delete_{category}"):
                categories_to_delete.append(category)
                st.success(f"Category '{category}' deleted successfully!")

    # Apply updates and deletions after iteration
    for category, (new_category_name, new_category_items) in categories_to_update.items():
        categories_items[new_category_name] = new_category_items
        if new_category_name != category:
            del categories_items[category]

    for category in categories_to_delete:
        del categories_items[category]

    # Form to add a new category
    st.write("### Add New Category")
    new_category_name = st.text_input("New Category Name", key="new_category_name")
    new_category_items = st.text_area("Item Numbers (comma separated)", key="new_category_items").split(',')

    if st.button("Add Category", key="add_category"):
        if new_category_name and new_category_items:
            try:
                new_category_items = list(map(str.strip, new_category_items))
                categories_items[new_category_name] = new_category_items
                st.success(f"Category '{new_category_name}' added successfully!")
            except ValueError:
                st.error("Please enter valid item numbers.")
        else:
            st.error("Please fill in both fields.")