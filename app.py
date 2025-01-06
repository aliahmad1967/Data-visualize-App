import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from io import BytesIO

# Custom styling
st.set_page_config(layout="wide")

# Custom CSS
st.markdown("""
<style>
    /* Main layout */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Headers */
    .main-header {
        color: #0D92F4;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .sub-header {
        color: #0D92F4;
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #0D92F4;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #77CDFF;
    }
    
    /* File uploader */
    .uploadedFile {
        border: 2px dashed #77CDFF;
        border-radius: 5px;
        padding: 1rem;
    }
    
    /* Checkbox and selectbox */
    .stCheckbox > label {
        color: #0D92F4;
        font-weight: 500;
    }
    
    .stSelectbox > label {
        color: #0D92F4;
        font-weight: 500;
    }
    
    /* Error messages */
    .stAlert {
        background-color: #F95454;
        color: white;
    }
    
    /* Download buttons */
    .download-buttons {
        background-color: #C62E2E;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        text-decoration: none;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def clean_column_names(df):
    """Clean column names by removing spaces and special characters"""
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    df.columns = df.columns.str.replace('[^\w\s]', '', regex=True)
    return df

def remove_duplicates(df):
    """Remove duplicate rows from dataframe"""
    original_shape = df.shape[0]
    df = df.drop_duplicates()
    st.info(f"Removed {original_shape - df.shape[0]} duplicate rows")
    return df

def handle_missing_values(df, method):
    """Handle missing values based on selected method"""
    if method == 'Remove rows':
        df = df.dropna()
    elif method == 'Fill with mean':
        for col in df.select_dtypes(include=[np.number]).columns:
            df[col] = df[col].fillna(df[col].mean())
    elif method == 'Fill with median':
        for col in df.select_dtypes(include=[np.number]).columns:
            df[col] = df[col].fillna(df[col].median())
    elif method == 'Fill with zero':
        df = df.fillna(0)
    return df

# Main header
st.markdown('<p class="main-header">Data Sweeper</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #F95454;">A-Ansari</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #77CDFF;">Clean, visualize, and transform your data with ease</p>', unsafe_allow_html=True)


# Create two columns for layout
col1, col2 = st.columns([1, 4])

with col1:
    st.markdown('<p class="sub-header">Upload Data</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # Read the file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        with col2:
            st.markdown('<p class="sub-header">Data Preview</p>', unsafe_allow_html=True)
            st.dataframe(df.head(), use_container_width=True)
        
        # Data cleaning options
        st.markdown('<p class="sub-header">Data Cleaning Options</p>', unsafe_allow_html=True)
        
        # Create three columns for cleaning options
        clean_col1, clean_col2, clean_col3 = st.columns(3)
        
        with clean_col1:
            clean_cols = st.checkbox("Clean column names")
            if clean_cols:
                df = clean_column_names(df)
        
        with clean_col2:
            remove_dups = st.checkbox("Remove duplicate rows")
            if remove_dups:
                df = remove_duplicates(df)
        
        with clean_col3:
            if df.isnull().values.any():
                missing_method = st.selectbox(
                    "Handle missing values",
                    ['Remove rows', 'Fill with mean', 'Fill with median', 'Fill with zero']
                )
                df = handle_missing_values(df, missing_method)
        
        # Data visualization
        st.markdown('<p class="sub-header">Data Visualization</p>', unsafe_allow_html=True)
        
        # Create columns for visualization options
        viz_col1, viz_col2, viz_col3 = st.columns(3)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            with viz_col1:
                x_col = st.selectbox("X-axis", df.columns)
            with viz_col2:
                y_col = st.selectbox("Y-axis", numeric_cols)
            with viz_col3:
                plot_type = st.selectbox(
                    "Plot type",
                    ['Scatter', 'Line', 'Bar', 'Box', 'Histogram']
                )
            
            # Create a custom color scheme for plots
            colors = ['#0D92F4', '#77CDFF', '#F95454', '#C62E2E']
            
            if plot_type == 'Scatter':
                fig = px.scatter(df, x=x_col, y=y_col, color_discrete_sequence=colors)
            elif plot_type == 'Line':
                fig = px.line(df, x=x_col, y=y_col, color_discrete_sequence=colors)
            elif plot_type == 'Bar':
                fig = px.bar(df, x=x_col, y=y_col, color_discrete_sequence=colors)
            elif plot_type == 'Box':
                fig = px.box(df, x=x_col, y=y_col, color_discrete_sequence=colors)
            else:
                fig = px.histogram(df, x=x_col, color_discrete_sequence=colors)
            
            # Update plot layout
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#0D92F4'},
                title_font_color='#0D92F4',
                legend_title_font_color='#0D92F4'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Download options
        st.markdown('<p class="sub-header">Download Cleaned Data</p>', unsafe_allow_html=True)
        
        download_col1, download_col2 = st.columns(2)
        
        with download_col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name="cleaned_data.csv",
                mime="text/csv"
            )
        
        with download_col2:
            excel_buffer = BytesIO()
            df.to_excel(excel_buffer, index=False)
            excel_data = excel_buffer.getvalue()
            st.download_button(
                label="Download as Excel",
                data=excel_data,
                file_name="cleaned_data.xlsx",
                mime="application/vnd.ms-excel"
            )
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
