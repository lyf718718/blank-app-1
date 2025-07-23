import streamlit as st
import pandas as pd
import re
from io import StringIO

# Set page config
st.set_page_config(
    page_title="Text Classification Tool",
    page_icon="🔍",
    layout="wide"
)

# Title and description
st.title("🔍 Text Classification Tool")
st.markdown("Upload your dataset and classify text using customizable dictionaries for urgency and exclusive marketing terms.")

# Initialize session state for dictionaries
if 'dictionaries' not in st.session_state:
    st.session_state.dictionaries = {
        'urgency_marketing': {
            'limited', 'limited time', 'limited run', 'limited edition', 'order now',
            'last chance', 'hurry', 'while supplies last', 'before they\'re gone',
            'selling out', 'selling fast', 'act now', 'don\'t wait', 'today only',
            'expires soon', 'final hours', 'almost gone'
        },
        'exclusive_marketing': {
            'exclusive', 'exclusively', 'exclusive offer', 'exclusive deal',
            'members only', 'vip', 'special access', 'invitation only',
            'premium', 'privileged', 'limited access', 'select customers',
            'insider', 'private sale', 'early access'
        }
    }

def classify_text(text, dictionary):
    """Check if text contains any terms from dictionary"""
    if pd.isna(text):
        return 0
    
    text_lower = str(text).lower()
    
    # Check for exact phrase matches first, then word matches
    for term in sorted(dictionary, key=len, reverse=True):
        if term in text_lower:
            return 1
    return 0

# Sidebar for dictionary management
st.sidebar.header("📚 Dictionary Management")

# Dictionary editing
for dict_name in st.session_state.dictionaries.keys():
    with st.sidebar.expander(f"Edit {dict_name.replace('_', ' ').title()}", expanded=False):
        current_terms = list(st.session_state.dictionaries[dict_name])
        current_terms_str = '\n'.join(sorted(current_terms))
        
        new_terms_str = st.text_area(
            f"Terms for {dict_name}:",
            value=current_terms_str,
            height=200,
            key=f"terms_{dict_name}",
            help="Enter one term per line. Phrases are supported."
        )
        
        if st.button(f"Update {dict_name}", key=f"update_{dict_name}"):
            new_terms = set(term.strip() for term in new_terms_str.split('\n') if term.strip())
            st.session_state.dictionaries[dict_name] = new_terms
            st.success(f"Updated {dict_name} with {len(new_terms)} terms!")

# Add custom dictionary option
with st.sidebar.expander("➕ Add Custom Dictionary", expanded=False):
    new_dict_name = st.text_input("Dictionary Name:", placeholder="e.g., discount_marketing")
    new_dict_terms = st.text_area("Terms (one per line):", placeholder="Enter terms here...", height=150)
    
    if st.button("Add Dictionary"):
        if new_dict_name and new_dict_terms:
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', new_dict_name.lower())
            terms_set = set(term.strip() for term in new_dict_terms.split('\n') if term.strip())
            st.session_state.dictionaries[clean_name] = terms_set
            st.success(f"Added new dictionary: {clean_name}")
        else:
            st.error("Please provide both dictionary name and terms.")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📁 Upload Dataset")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type="csv",
        help="Upload a CSV file with a 'Statement' column to classify"
    )
    
    # Sample data option
    if st.button("Use Sample Data"):
        sample_data = {
            'ID': [1, 2, 3, 4, 5],
            'Statement': [
                'Limited time offer - order now!',
                'Exclusive deal for VIP members only',
                'Regular product description here',
                'Hurry, while supplies last! Premium access included',
                'Standard marketing message'
            ]
        }
        st.session_state.df = pd.DataFrame(sample_data)
        st.success("Sample data loaded!")

with col2:
    st.header("⚙️ Current Dictionaries")
    for dict_name, terms in st.session_state.dictionaries.items():
        with st.expander(f"{dict_name.replace('_', ' ').title()} ({len(terms)} terms)"):
            st.write(", ".join(sorted(terms)))

# File processing
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.session_state.df = df
        st.success(f"✅ File uploaded successfully! {len(df)} rows loaded.")
    except Exception as e:
        st.error(f"Error reading file: {e}")

# Classification and results
if 'df' in st.session_state:
    df = st.session_state.df.copy()
    
    st.header("🎯 Classification Results")
    
    # Check if Statement column exists
    if 'Statement' not in df.columns:
        st.error("❌ The dataset must contain a 'Statement' column for classification.")
        st.write("Available columns:", list(df.columns))
    else:
        # Run classification
        if st.button("🚀 Run Classification", type="primary"):
            with st.spinner("Classifying text..."):
                # Apply classification for each dictionary
                for dict_name, terms in st.session_state.dictionaries.items():
                    df[f'{dict_name}_detected'] = df['Statement'].apply(
                        lambda x: classify_text(x, terms)
                    )
                
                st.session_state.classified_df = df
                st.success("✅ Classification completed!")
        
        # Display results if classification has been run
        if 'classified_df' in st.session_state:
            classified_df = st.session_state.classified_df
            
            # Summary statistics
            st.subheader("📊 Summary Statistics")
            summary_cols = st.columns(len(st.session_state.dictionaries))
            
            for i, dict_name in enumerate(st.session_state.dictionaries.keys()):
                with summary_cols[i]:
                    count = classified_df[f'{dict_name}_detected'].sum()
                    total = len(classified_df)
                    percentage = (count / total) * 100 if total > 0 else 0
                    
                    st.metric(
                        label=dict_name.replace('_', ' ').title(),
                        value=f"{count}/{total}",
                        delta=f"{percentage:.1f}%"
                    )
            
            # Display classified data
            st.subheader("📋 Classified Data")
            
            # Filter options
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                show_detected_only = st.checkbox("Show only detected statements")
            
            with filter_col2:
                selected_dict = st.selectbox(
                    "Filter by dictionary:",
                    ["All"] + list(st.session_state.dictionaries.keys())
                )
            
            # Apply filters
            display_df = classified_df.copy()
            if show_detected_only:
                detection_cols = [f'{dict_name}_detected' for dict_name in st.session_state.dictionaries.keys()]
                mask = display_df[detection_cols].sum(axis=1) > 0
                display_df = display_df[mask]
            
            if selected_dict != "All":
                mask = display_df[f'{selected_dict}_detected'] == 1
                display_df = display_df[mask]
            
            # Display dataframe
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Download options
            st.subheader("💾 Download Results")
            col1, col2 = st.columns(2)
            
            with col1:
                csv = classified_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Full Results (CSV)",
                    data=csv,
                    file_name="classified_data.csv",
                    mime="text/csv"
                )
            
            with col2:
                if len(display_df) > 0:
                    filtered_csv = display_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Filtered Results (CSV)",
                        data=filtered_csv,
                        file_name="filtered_classified_data.csv",
                        mime="text/csv"
                    )

# Instructions
with st.expander("ℹ️ How to Use This Tool"):
    st.markdown("""
    1. **Upload your CSV file** or use sample data to get started
    2. **Customize dictionaries** in the sidebar - add, remove, or modify terms
    3. **Add custom dictionaries** for specific classification needs
    4. **Run classification** to analyze your text data
    5. **View results** with summary statistics and detailed classifications
    6. **Download results** as CSV files for further analysis
    
    **CSV Format Requirements:**
    - Must contain a column named 'Statement' with text to classify
    - Can contain additional columns (ID, etc.) which will be preserved
    
    **Dictionary Management:**
    - Terms are case-insensitive
    - Supports both single words and phrases
    - Longer phrases are matched first for accuracy
    """)

# Footer
st.markdown("---")
st.markdown("Built with Streamlit 🎈 | Text Classification Tool")
