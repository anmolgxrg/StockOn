import streamlit as st
import pandas as pd
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

# Define categories and their corresponding item numbers
categories_items = {
    "dry storage - paper and packaging": [1187, 2268, 1479, 3090, 1714, 1707, 2152, 905, 3497, 6792, 3381, 4638, 3299, 7552, 3634, 3635, 3636, 3253, 1665, 1570, 4782, 1220, 1395, 3189, 3288],
    # Add other categories and their items here...
}

# Tabs for viewing and managing categories
tab1, tab2 = st.tabs(["View Data", "Manage Categories"])

with tab1:
    # Upload Excel file
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    if uploaded_file:
        # Load the Excel file
        excel_data = pd.ExcelFile(uploaded_file)

        # Dropdown to select the sheet
        sheet = st.selectbox('Select Sheet', excel_data.sheet_names)

        # Load data from the selected sheet
        sheet_data = pd.read_excel(uploaded_file, sheet_name=sheet)

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
        category = st.selectbox('Select Category', categories_items.keys())

        # Filter the data based on the selected category
        item_numbers = categories_items[category]
        filtered_data = sheet_data[sheet_data["Item Number"].isin(item_numbers)]

        # Display the filtered data without the default index
        st.dataframe(filtered_data.reset_index(drop=True))
    else:
        st.info("Please upload an Excel file to get started.")

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
                        new_category_items = list(map(int, new_category_items))
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
                new_category_items = list(map(int, new_category_items))
                categories_items[new_category_name] = new_category_items
                st.success(f"Category '{new_category_name}' added successfully!")
            except ValueError:
                st.error("Please enter valid item numbers.")
        else:
            st.error("Please fill in both fields.")