import streamlit as st
import pandas as pd
import re
from collections import defaultdict
import io

# Set page config
st.set_page_config(
    page_title="Marketing Tactics Classifier",
    page_icon="🎯",
    layout="wide"
)

def classify_statement(text, dictionaries):
    """Classify a statement based on marketing tactic dictionaries."""
    if pd.isna(text):
        return {}
    
    text_lower = text.lower()
    results = {}
    
    for tactic, keywords in dictionaries.items():
        matches = []
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matches.append(keyword)
        
        results[tactic] = {
            'present': len(matches) > 0,
            'count': len(matches),
            'matches': matches
        }
    
    return results

def process_classification(df, dictionaries, text_column):
    """Process the classification for the entire dataframe."""
    # Apply classification
    df['classification'] = df[text_column].apply(lambda x: classify_statement(x, dictionaries))
    
    # Extract results to separate columns
    for tactic in dictionaries.keys():
        df[f'{tactic}_present'] = df['classification'].apply(lambda x: x.get(tactic, {}).get('present', False))
        df[f'{tactic}_count'] = df['classification'].apply(lambda x: x.get(tactic, {}).get('count', 0))
        df[f'{tactic}_matches'] = df['classification'].apply(lambda x: ', '.join(x.get(tactic, {}).get('matches', [])))
    
    return df

def create_sample_data():
    """Create sample data for demonstration."""
    sample_data = {
        'ID': [1, 2, 3, 4, 5],
        'Statement': [
            "Limited time offer! Get 50% off before it's gone!",
            "This is a regular product description with no special tactics.",
            "Exclusive VIP access for members only - don't wait!",
            "Premium quality materials used in manufacturing.",
            "Hurry! While supplies last - exclusive deal for today only!"
        ]
    }
    return pd.DataFrame(sample_data)

# Initialize session state
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

# Main app
st.title("🎯 Marketing Tactics Classifier")
st.markdown("Upload your dataset and classify marketing statements based on customizable tactics dictionaries.")

# Sidebar for dictionary management
st.sidebar.header("📚 Marketing Tactics Dictionaries")

# Dictionary editor
st.sidebar.subheader("Edit Dictionaries")

# Create expandable sections for each dictionary
for tactic_name, keywords in st.session_state.dictionaries.items():
    with st.sidebar.expander(f"Edit {tactic_name.replace('_', ' ').title()}"):
        # Convert set to text for editing
        keywords_text = '\n'.join(sorted(keywords))
        
        # Text area for editing keywords
        new_keywords_text = st.text_area(
            f"Keywords for {tactic_name}:",
            value=keywords_text,
            height=150,
            key=f"edit_{tactic_name}",
            help="Enter one keyword per line"
        )
        
        if st.button(f"Update {tactic_name}", key=f"update_{tactic_name}"):
            # Update the dictionary
            new_keywords = set([keyword.strip() for keyword in new_keywords_text.split('\n') if keyword.strip()])
            st.session_state.dictionaries[tactic_name] = new_keywords
            st.sidebar.success(f"Updated {tactic_name}!")

# Add new dictionary
st.sidebar.subheader("Add New Dictionary")
with st.sidebar.expander("Create New Tactic"):
    new_tactic_name = st.text_input("Tactic Name:", key="new_tactic_name")
    new_tactic_keywords = st.text_area("Keywords (one per line):", key="new_tactic_keywords", height=100)
    
    if st.button("Add New Tactic"):
        if new_tactic_name and new_tactic_keywords:
            # Clean up the name
            clean_name = new_tactic_name.lower().replace(' ', '_')
            keywords = set([keyword.strip() for keyword in new_tactic_keywords.split('\n') if keyword.strip()])
            
            if keywords:
                st.session_state.dictionaries[clean_name] = keywords
                st.sidebar.success(f"Added new tactic: {new_tactic_name}!")
                # Clear the inputs
                st.session_state.new_tactic_name = ""
                st.session_state.new_tactic_keywords = ""
            else:
                st.sidebar.error("Please enter at least one keyword.")
        else:
            st.sidebar.error("Please enter both tactic name and keywords.")

# Reset dictionaries button
if st.sidebar.button("Reset to Default Dictionaries"):
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
    st.sidebar.success("Reset to default dictionaries!")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📁 Upload Dataset")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file containing the text data you want to classify"
    )
    
    # Option to use sample data
    use_sample = st.checkbox("Use sample data for demonstration")
    
    df = None
    
    if use_sample:
        df = create_sample_data()
        st.success("Sample data loaded!")
    elif uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"File uploaded successfully! Shape: {df.shape}")
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")

with col2:
    st.header("📊 Current Dictionaries")
    for tactic_name, keywords in st.session_state.dictionaries.items():
        st.subheader(tactic_name.replace('_', ' ').title())
        st.write(f"**{len(keywords)} keywords**")
        with st.expander("View keywords"):
            st.write(", ".join(sorted(keywords)))

# Data processing section
if df is not None:
    st.header("🔍 Data Processing")
    
    # Column selection
    text_columns = [col for col in df.columns if df[col].dtype == 'object']
    
    if text_columns:
        selected_column = st.selectbox(
            "Select the column containing text to classify:",
            text_columns,
            index=0 if 'Statement' in text_columns else 0
        )
        
        # Preview data
        st.subheader("📋 Data Preview")
        st.dataframe(df.head(10))
        
        # Process button
        if st.button("🚀 Run Classification", type="primary"):
            with st.spinner("Processing classifications..."):
                try:
                    # Process the data
                    result_df = process_classification(df.copy(), st.session_state.dictionaries, selected_column)
                    
                    # Store results in session state
                    st.session_state.result_df = result_df
                    
                    st.success("Classification completed!")
                    
                except Exception as e:
                    st.error(f"Error during classification: {str(e)}")
    else:
        st.warning("No text columns found in the uploaded data.")

# Results section
if 'result_df' in st.session_state:
    st.header("📈 Results")
    
    result_df = st.session_state.result_df
    
    # Summary statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Statements", len(result_df))
    
    with col2:
        any_tactic_cols = [f'{t}_present' for t in st.session_state.dictionaries.keys()]
        statements_with_tactics = (result_df[any_tactic_cols].any(axis=1)).sum()
        st.metric("Statements with Tactics", statements_with_tactics)
    
    with col3:
        percentage = (statements_with_tactics / len(result_df)) * 100 if len(result_df) > 0 else 0
        st.metric("Percentage with Tactics", f"{percentage:.1f}%")
    
    # Tactic-specific summary
    st.subheader("📊 Tactic Summary")
    
    summary_data = []
    for tactic in st.session_state.dictionaries.keys():
        total_present = result_df[f'{tactic}_present'].sum()
        percentage = (total_present / len(result_df)) * 100 if len(result_df) > 0 else 0
        summary_data.append({
            'Tactic': tactic.replace('_', ' ').title(),
            'Count': total_present,
            'Percentage': f"{percentage:.1f}%"
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)
    
    # Detailed results
    st.subheader("🔍 Detailed Results")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        show_all = st.radio("Show results:", ["All statements", "Only statements with tactics"])
    
    with col2:
        selected_tactics = st.multiselect(
            "Filter by tactics:",
            options=list(st.session_state.dictionaries.keys()),
            default=list(st.session_state.dictionaries.keys())
        )
    
    # Apply filters
    display_df = result_df.copy()
    
    if show_all == "Only statements with tactics":
        any_tactic_cols = [f'{t}_present' for t in selected_tactics]
        if any_tactic_cols:
            display_df = display_df[display_df[any_tactic_cols].any(axis=1)]
    
    # Select columns to display
    base_cols = ['ID'] if 'ID' in display_df.columns else []
    base_cols.append(selected_column)
    
    result_cols = []
    for tactic in selected_tactics:
        result_cols.extend([f'{tactic}_present', f'{tactic}_matches'])
    
    display_cols = base_cols + result_cols
    final_display_df = display_df[display_cols]
    
    # Display the filtered results
    st.dataframe(final_display_df, use_container_width=True)
    
    # Download results
    st.subheader("💾 Download Results")
    
    # Prepare download data
    csv_buffer = io.StringIO()
    result_df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    st.download_button(
        label="📥 Download Classified Data (CSV)",
        data=csv_data,
        file_name="classified_marketing_data.csv",
        mime="text/csv"
    )

# Instructions
with st.expander("ℹ️ How to use this app"):
    st.markdown("""
    ### Instructions:
    
    1. **Upload your data**: Click on "Choose a CSV file" to upload your dataset, or check "Use sample data" to try the app
    
    2. **Edit dictionaries**: Use the sidebar to modify existing marketing tactic dictionaries or add new ones
    
    3. **Select text column**: Choose which column contains the text you want to classify
    
    4. **Run classification**: Click "Run Classification" to analyze your data
    
    5. **View results**: Explore the summary statistics and detailed results
    
    6. **Download**: Save your classified data as a CSV file
    
    ### Data Format:
    Your CSV should have at least one column containing text data. The app will automatically detect text columns.
    
    ### Dictionary Format:
    Each dictionary contains keywords/phrases that define a marketing tactic. Keywords are case-insensitive and can include phrases with spaces.
    """)
