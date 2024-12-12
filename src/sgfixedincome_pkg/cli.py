import streamlit as st

def run_app():
    """
    Entry point for running the Streamlit app
    """
    from .streamlit_app.app import main
    main()

if __name__ == "__main__":
    run_app()