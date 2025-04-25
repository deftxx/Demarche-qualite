"""
Simplified translation utility for the Quality Tools application (English-only)
"""
import streamlit as st

def translate_text(text):
    """
    Simple identity function that returns the original text (English-only)

    Args:
        text (str): The text to translate

    Returns:
        str: The original text
    """
    return text

def initialize_translation():
    """
    Initialize translation in the Streamlit session state (English-only)
    """
    # Set language to English
    if 'language' not in st.session_state:
        st.session_state.language = 'en'

    # Set up translation function as identity function
    if 'translate' not in st.session_state:
        st.session_state.translate = translate_text