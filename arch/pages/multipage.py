import streamlit as st

class MultiPage:
    def __init__(self):
        self.pages = []

    def add_page(self, title, func):
        self.pages.append({
            "title": title,
            "function": func
        })

    def run(self):
        st.session_state.current_page = st.session_state.get("current_page", "Home")
        
        page = next((page for page in self.pages if page['title'] == st.session_state.current_page), self.pages[0])
        page['function']()
        
        st.sidebar.write("Navigation")
        for page in self.pages:
            if st.button(page['title']):
                st.session_state.current_page = page['title']
                st.experimental_rerun()
