import streamlit as st

def app():
    st.title('Home')
    st.write('Welcome to the Home page!')
    
    if st.button('Go to Inventory'):
        st.session_state.current_page = 'Inventory'
        st.experimental_rerun()
        
    if st.button('Go to Order'):
        st.session_state.current_page = 'Order'
        st.experimental_rerun()