import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page config
st.set_page_config(
    page_title="MSBA 325 Trade Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS for compact layout
st.markdown("""
<style>
    .main .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    .stPlotlyChart {
        height: 250px !important;
    }
    h1 {
        color: #2E8B57;
        text-align: center;
        font-size: 1.8rem;
        margin-top: 0rem;
        margin-bottom: 0.5rem;
        padding: 0rem;
        line-height: 1.1;
    }
    h3 {
        font-size: 0.9rem;
        margin: 0.1rem 0 0.2rem 0;
        color: #333;
    }
    .element-container {
        margin-bottom: 0.2rem;
    }
    .stMarkdown {
        margin-bottom: 0.1rem;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("# Lebanon Trade Sector Analysis")

# Load and process trade data
@st.cache_data
def load_trade_data():
    
    # Business size distribution (uses actual counts from your data)
    size_distribution = pd.DataFrame({
        'Institution Size': ['Small Institutions', 'Medium Institutions', 'Large Institutions'],
        'Count': [38940, 2612, 884],
        'Percentage': [91.8, 6.2, 2.1]
    })
    
    # Comprehensive economic activity presence analysis (all 5 binary columns)
    activity_presence = pd.DataFrame({
        'Activity Type': ['Self Employment', 'Commerce', 'Public Sector', 'Service Institutions', 'Banking'],
        'Towns with Activity': [722, 493, 207, 126, 91],
        'Percentage': [63.5, 43.4, 18.2, 11.1, 8.0]
    })
    
    return size_distribution, activity_presence, {
        'total_small': 38940,
        'total_medium': 2612,
        'total_large': 884,
        'total_service': 1086,
        'total_financial': 682,
        'total_towns': 1137
    }

# Load the data
size_dist, activity_data, metrics = load_trade_data()

# INTERACTIVE FEATURES - Sidebar Controls
st.sidebar.header("🎛️ Interactive Controls")
st.sidebar.markdown("*Select filters to impact the two main visualizations*")

# Interactive Feature 1: Institution Size Focus (IMPACTS VISUALIZATION 1)
st.sidebar.subheader("📊 Institution Size Filter")
size_focus = st.sidebar.selectbox(
    "Focus Analysis on Institution Size:",
    options=['All Sizes', 'Small Institutions Only', 'Medium Institutions Only', 'Large Institutions Only'],
    help="This filter directly impacts the Institution Size Distribution chart"
)

# Interactive Feature 2: Activity Type Display (IMPACTS VISUALIZATION 2)
st.sidebar.subheader("🏬 Activity Type Filter")
activity_types = st.sidebar.multiselect(
    "Select Economic Activities to Display:",
    options=['Self Employment', 'Commerce', 'Public Sector', 'Service Institutions', 'Banking'],
    default=['Self Employment', 'Commerce', 'Public Sector', 'Service Institutions', 'Banking'],
    help="This filter directly impacts the Economic Activity Presence chart"
)

# Display current filter status
st.sidebar.markdown("---")
st.sidebar.markdown("**🎯 Current Active Filters:**")
st.sidebar.write(f"• Institution Size: **{size_focus}**")
st.sidebar.write(f"• Activity Types: **{len(activity_types)}** selected")
if len(activity_types) < 5:
    st.sidebar.write(f"  - Showing: {', '.join(activity_types)}")

# Apply filters based on interactive selections

# Filter 1: Size distribution data (IMPACTS CHART 1)
if size_focus == 'Small Institutions Only':
    filtered_size_dist = size_dist[size_dist['Institution Size'] == 'Small Institutions']
    chart1_subtitle = "Focus: Small Institutions (91.8% of total)"
elif size_focus == 'Medium Institutions Only':
    filtered_size_dist = size_dist[size_dist['Institution Size'] == 'Medium Institutions']
    chart1_subtitle = "Focus: Medium Institutions (6.2% of total)"
elif size_focus == 'Large Institutions Only':
    filtered_size_dist = size_dist[size_dist['Institution Size'] == 'Large Institutions']
    chart1_subtitle = "Focus: Large Institutions (2.1% of total)"
else:
    filtered_size_dist = size_dist.copy()
    chart1_subtitle = "All institution sizes included"

# Filter 2: Activity data (IMPACTS CHART 2)
filtered_activity_data = activity_data[activity_data['Activity Type'].isin(activity_types)]
if len(activity_types) == 5:
    chart2_subtitle = "All economic activity types included"
else:
    chart2_subtitle = f"Showing {len(activity_types)} of 5 activity types"

# Key Metrics Row
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
with col_m1:
    st.metric("Total Commercial Institutions", f"{metrics['total_small'] + metrics['total_medium'] + metrics['total_large']:,}")
with col_m2:
    st.metric("Small Businesses", f"{metrics['total_small']:,}")
with col_m3:
    st.metric("Service Institutions", f"{metrics['total_service']:,}")
with col_m4:
    st.metric("Financial Institutions", f"{metrics['total_financial']:,}")
with col_m5:
    st.metric("Towns Analyzed", f"{metrics['total_towns']:,}")

# Main Interactive Visualizations Section
st.markdown("---")
st.markdown("## 🎯 Interactive Trade Data Visualizations")
st.markdown("*Use the sidebar controls to filter and analyze the Lebanese trade data below*")

col1, col2 = st.columns(2)

# VISUALIZATION 1: Business Size Distribution (INTERACTIVE - responds to size_focus)
with col1:
    st.markdown("### 📊 Commercial Institution Size Distribution")
    st.markdown(f"*{chart1_subtitle}*")
    
    if len(filtered_size_dist) > 0:
        fig1 = px.pie(filtered_size_dist, values='Count', names='Institution Size', hole=0.5,
                      color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        fig1.update_traces(textposition='auto', textinfo='percent+label', textfont_size=14)
        fig1.update_layout(
            height=250,
            template='plotly_white',
            margin=dict(l=20, r=20, t=20, b=20),
            annotations=[dict(text=f'Total<br>{filtered_size_dist["Count"].sum():,}', x=0.5, y=0.5, font_size=14, showarrow=False)]
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Show impact of filter
        if size_focus != 'All Sizes':
            st.info(f"🎯 Filter Impact: Showing {filtered_size_dist['Count'].sum():,} institutions ({filtered_size_dist['Percentage'].iloc[0]}% of total)")
        else:
            st.success(f"📈 Total Analysis: {filtered_size_dist['Count'].sum():,} institutions across all sizes")
    else:
        st.error("No data available for selected filter")

# VISUALIZATION 2: Activity Presence (INTERACTIVE - responds to activity_types filter)
with col2:
    st.markdown("### 🏬 Economic Activity Presence Across Towns")
    st.markdown(f"*{chart2_subtitle}*")
    
    if len(filtered_activity_data) > 0:
        fig2 = px.bar(filtered_activity_data, y='Activity Type', x='Towns with Activity', orientation='h',
                      color='Towns with Activity', color_continuous_scale='RdYlGn',
                      text='Towns with Activity')
        fig2.update_traces(textposition='outside', textfont_size=12)
        fig2.update_layout(
            height=250,
            template='plotly_white',
            margin=dict(l=100, r=20, t=20, b=30),
            coloraxis_showscale=False,
            font=dict(size=11),
            xaxis_title='Number of Towns with Activity'
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Show impact of filter
        if len(activity_types) < 5:
            total_coverage = filtered_activity_data['Towns with Activity'].sum()
            st.info(f"🎯 Filter Impact: Selected activities cover {total_coverage:,} town-activity combinations")
        else:
            total_coverage = filtered_activity_data['Towns with Activity'].sum()
            st.success(f"📈 Complete Analysis: All activities cover {total_coverage:,} town-activity combinations")
    else:
        st.warning("⚠️ Please select at least one activity type from the sidebar")

# Context and Insights Section
st.markdown("---")
st.markdown("## 📈 Key Trade Insights & Analysis")

# Trade insights with dynamic content based on filters
with st.expander("🔍 Detailed Analysis & Interactive Features", expanded=True):
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        st.markdown("""
        **Lebanese Economic Structure:**
        - Small enterprises dominate: 38,940 institutions (91.8% of total)
        - Medium-sized businesses: 2,612 institutions (6.2% of total)
        - Large institutions: 884 businesses (2.1% of total)
        - Total commercial institutions: 42,436 establishments
        """)
        
        # Dynamic insights based on size filter
        if size_focus == 'Small Institutions Only':
            st.markdown("**🔍 Small Institution Focus:** These represent the backbone of Lebanon's economy, primarily family-owned businesses and individual enterprises.")
        elif size_focus == 'Medium Institutions Only':
            st.markdown("**🔍 Medium Institution Focus:** These businesses bridge the gap between small enterprises and large corporations, often regional players.")
        elif size_focus == 'Large Institutions Only':
            st.markdown("**🔍 Large Institution Focus:** Major corporations and establishments that drive significant economic activity and employment.")
        
    with col_i2:
        st.markdown(f"""
        **Economic Activity Distribution:**
        - Self Employment: Most widespread (722 towns - 63.5%)
        - Commerce Activities: Present in 493 towns (43.4%)  
        - Public Sector: Available in 207 towns (18.2%)
        - Service Institutions: Found in 126 towns (11.1%)
        - Banking Access: Limited to 91 towns (8.0%)
        """)
        
        # Dynamic insights based on activity filter
        if len(activity_types) < 5:
            selected_activities_text = ', '.join(activity_types)
            st.markdown(f"**🔍 Activity Focus:** Currently analyzing {selected_activities_text}. This represents {len(activity_types)} of 5 major economic activity categories.")
        else:
            st.markdown("**🔍 Complete Activity Analysis:** All economic activities included, providing comprehensive coverage of Lebanese trade patterns.")

# Interactive Feature Summary
st.markdown("---")
st.markdown("### 🎛️ Interactive Features Summary")
col_s1, col_s2 = st.columns(2)

with col_s1:
    st.markdown("""
    **Feature 1: Regional Analysis Filter**
    - Primary filter affecting both visualizations
    - Choose specific Lebanese governorates or view all regions
    - Shows institution distribution and activity presence by region
    - Provides targeted regional economic analysis
    """)

with col_s2:
    st.markdown("""
    **Feature 2: Analysis Focus Selector**
    - Choose perspective: Institution Size or Economic Activity
    - Emphasizes different aspects of the regional data
    - Complements the regional filter for deeper analysis
    - Enables focused interpretation of regional patterns
    """)

# Footer
st.markdown("---")
st.markdown("**MSBA 325 Trade Analysis Dashboard | Lebanese Commercial Institutions & Economic Activities**")
st.markdown("*Interactive data visualization demonstrating Streamlit and Plotly capabilities for business analytics*")
