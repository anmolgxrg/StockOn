import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
import base64

st.set_page_config(layout="wide", page_title="StockOn", page_icon="/favicon.ico")

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
st.title('StockOn - Beta Test')

categories_items = {
    "DRY STORAGE - PAPER & PACKAGING": ["1187", "2268", "1479", "3090", "1714", "1707", "2152", "0905", "3497", "6792", "3381", "4638", "3299", "7552", "3634", "3635", "3636", "3253", "1665", "1570", "4782", "1220", "1395", "3189", "3288", "3327", "3328", "1779",
                                        "4129", "3659", "3347", "3348", "4969", "0890", "4972", "3221", "4970", "4973"],
    "DRY STORAGE - FOOD": ["4552", "0404", "4892", "0407", "2276", "0099", "0193", "0200", "0205", "0496", "0427", "4622", "0421", "3505", "0062", "0399", "1392", "0350", "0348", "0347", "4227", "1817", "0314", "0330", "0120", "0663", "4876", "1247", "0211", "4114", 
                           "0087", "4763", "0244", "1474", "6398", "2214", "1390", "0018", "4071", "0057", "0113", "2459", "0117", "0118", "0108", "0443", "2213", "4826", "3515", "0134", "0098", "0298", "1643", "1271", "0275", "1145", "0284", "0285", "0288", "0287", 
                           "0286", "1444", "0282", "0280", "4712", "0259", "0256", "1334", "0250", "4387", "0241", "1900", "3147", "4003", "1626", "4675", "1223", "1396", "0093", "4086", "2568", "0208", "0262", "0238", "0276", "4386", "1422"],
    "WALK-IN FREEZER (MEATS)": ["0419", "2260", "4219", "0584", "0701", "0709", "3373", "4995", "0614", "4589", "0697", "2926", "0714", "0713", "3605", "0554"],
    "WALK-IN FREEZER": ["4354", "0501", "4692", "3295", "0390", "4832", "1045", "1455", "0313", "4921", "4511", "4548", "4540", "4533", "0511", "3552", "3599", "3571", "3522", "3585", "2151", "2881", "1192", "2040", "0582"],
    "WALK-IN": ["1568", "0010", "1941", "1486", "2283", "0984", "4798", "1302", "0328", "0578", "0464", "4940", "0457", "3719", "0021", "4042", "0456", "0926", "0631", "0231", "1526", "0469", "0576", "0168", "4021", "1400"],
    "SUPPLIES": ["4801", "3026", "0971", "6328", "2344", "7781", "2929", "2930", "2931", "2935", "2936", "3424", "4311", "3245", "3021", "3852", "1320", "3265", "3846", "1018", "1015", "4281", "4724", "4584", "4272", "3170", "4025", "4004", "4593", "4534", "4495"]
}

file_path = 'outpost.xlsx'

# Tabs for viewing and managing categories
tab1, tab2 = st.tabs(["View Data", "Manage Categories"])

with tab1:
    def load_data(sheet_name):
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=1, engine='openpyxl')
            df.columns = df.iloc[0]  # Set the first row as the header
            df = df[1:]  # Remove the first row from the DataFrame
            df.columns = ['Item ID', 'Name', 'Unit Size', 'PAR', 'Order Quantity']
            df['Order Quantity'] = df['Order Quantity'].fillna(0).astype(int)  # Replace NaN with 0 and convert to int
            return df
        except Exception as e:
            st.error(f"Error loading the Excel file: {e}")
            return pd.DataFrame()

    def save_data(df, sheet_name):
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        except Exception as e:
            st.error(f"Error saving the Excel file: {e}")

    # Select category
    category = st.selectbox('Select a category', categories_items.keys())

    # Load data
    df = load_data('OUTPOST MAIN ORDER')

    if not df.empty:
        # Initialize session state to keep track of quantities
        if 'order_quantities' not in st.session_state:
            st.session_state.order_quantities = {row['Item ID']: row['Order Quantity'] for _, row in df.iterrows()}

        # Filter data by category
        item_ids = categories_items[category]
        filtered_df = df[df['Item ID'].astype(str).isin(item_ids)]

        # Display data and allow editing
        if not filtered_df.empty:
            # Display headers
            header_col1, header_col2, header_col3, header_col4 = st.columns([1, 3, 1, 2])
            header_col1.write("**Item ID**")
            header_col2.write("**Name**")
            header_col3.write("**Unit Size**")
            header_col4.write("**Quantity**")
            st.markdown("---")

            for index, row in filtered_df.iterrows():
                item_id = row['Item ID']
                col1, col2, col3, col4 = st.columns([1, 3, 1, 2])
                col1.write(item_id)
                col2.write(row['Name'])
                col3.write(row['Unit Size'])
                if f"quantity_{index}" not in st.session_state:
                    st.session_state[f"quantity_{index}"] = st.session_state.order_quantities[item_id]
                st.session_state.order_quantities[item_id] = col4.number_input('', min_value=0, max_value=100, value=st.session_state[f"quantity_{index}"], key=f"quantity_{index}")
                
                # Add a horizontal rule after each row
                st.markdown("---")

            # Save changes to the Excel file
            if st.button('Save Changes'):
                for index, row in filtered_df.iterrows():
                    df.at[index, 'Order Quantity'] = st.session_state[f"quantity_{index}"]
                save_data(df, 'OUTPOST MAIN ORDER')
                st.success('Changes saved to the Excel file.')
        else:
            st.write('No items found for this category.')
    else:
        st.write('Unable to load data from the Excel file.')

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