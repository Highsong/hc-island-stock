#!/usr/bin/env python3
"""Minimal Streamlit app test"""

import streamlit as st

st.title("Test App")
st.write("This is a minimal test")

if st.button("Test Button"):
    st.write("Button clicked successfully!")

st.write("App loaded without errors")