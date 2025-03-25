import streamlit as st
from scrape import scrape_website, clean_body_content, split_dom_content
from ai_handler import process_content_with_ai
import concurrent.futures
import pandas as pd
import io

def convert_to_dataframe(results):
    """Convert real estate data to a structured DataFrame"""
    data = []
    for idx, content in results:
        # Initialize default values
        row = {
            'Section': f'Part {idx}',
            'Location': '',
            'Price': '',
            'Property Type': '',
            'Size': '',
            'Developer': ''
        }
        
        # Parse the structured content
        lines = content.split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key in row:
                    row[key] = value
        
        data.append(row)
    
    return pd.DataFrame(data)

# Streamlit UI
st.title("AI Web Scraper")

# Initialize session state for storing results
if 'results' not in st.session_state:
    st.session_state.results = []
if 'cleaned_content' not in st.session_state:
    st.session_state.cleaned_content = None

# Input URL
url = st.text_input("Enter Website URL")

if url:
    if st.button("Scrape Website"):
        with st.spinner("Scraping website..."):
            # Scrape website
            dom_content = scrape_website(url)
            
            if dom_content:
                # Clean the content
                st.session_state.cleaned_content = clean_body_content(dom_content)
                st.success("Website scraped successfully!")
            else:
                st.error("Failed to scrape the website. Please try again.")

# Create tabs for different views
if st.session_state.cleaned_content is not None:
    content_tab, analysis_tab = st.tabs(["Raw Content", "AI Analysis"])
    
    with content_tab:
        st.text_area("DOM Content", st.session_state.cleaned_content, height=300)
    
    with analysis_tab:
        # Get user query
        user_query = st.text_area("What would you like to know about this content?")
        
        if user_query and st.button("Analyze Content"):
            # Split content into chunks
            content_chunks = split_dom_content(st.session_state.cleaned_content)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Process chunks in parallel
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(process_content_with_ai, chunk, user_query)
                    for chunk in content_chunks
                ]
                
                # Collect results
                st.session_state.results = []
                for idx, future in enumerate(concurrent.futures.as_completed(futures), 1):
                    result = future.result()
                    st.session_state.results.append((idx, result))
                    # Update progress
                    progress = idx / len(content_chunks)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing chunk {idx}/{len(content_chunks)}")
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Display results
            st.success("Analysis complete!")
            
            # Create a DataFrame from results
            df = convert_to_dataframe(st.session_state.results)
            
            # Add export buttons
            col1, col2 = st.columns(2)
            
            # CSV export
            csv = df.to_csv(index=False).encode('utf-8')
            with col1:
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="analysis_results.csv",
                    mime="text/csv"
                )
            
            # Excel export
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Analysis Results')
            
            with col2:
                st.download_button(
                    label="Download Excel",
                    data=buffer.getvalue(),
                    file_name="analysis_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            # Display results in expandable sections
            for idx, result in sorted(st.session_state.results):
                with st.expander(f"Analysis Part {idx}"):
                    st.markdown(result)
