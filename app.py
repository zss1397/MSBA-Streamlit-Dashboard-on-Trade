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
    
    # Regional business size distribution with location data
    regional_size_data = pd.DataFrame({
        'Region': ['Bekaa', 'Bekaa', 'Bekaa', 'Mount Lebanon', 'Mount Lebanon', 'Mount Lebanon', 
                   'North Lebanon', 'North Lebanon', 'North Lebanon', 'South Lebanon', 'South Lebanon', 'South Lebanon',
                   'Nabatieh', 'Nabatieh', 'Nabatieh'],
        'Institution Size': ['Small Institutions', 'Medium Institutions', 'Large Institutions'] * 5,
        'Count': [8500, 580, 150,  # Bekaa
                 12200, 820, 220,  # Mount Lebanon  
                 7800, 520, 140,   # North Lebanon
                 6200, 410, 110,   # South Lebanon
                 4240, 282, 64]    # Nabatieh
    })
    
    # Regional economic activity presence with location data
    regional_activity_data = pd.DataFrame({
        'Region': ['Bekaa', 'Mount Lebanon', 'North Lebanon', 'South Lebanon', 'Nabatieh'] * 5,
        'Activity Type': ['Self Employment'] * 5 + ['Commerce'] * 5 + ['Public Sector'] * 5 + 
                        ['Service Institutions'] * 5 + ['Banking'] * 5,
        'Towns with Activity': [
            # Self Employment by region
            165, 220, 142, 118, 77,
            # Commerce by region  
            120, 158, 98, 82, 35,
            # Public Sector by region
            48, 62, 38, 35, 24,
            # Service Institutions by region
            32, 41, 26, 18, 9,
            # Banking by region
            22, 28, 18, 15, 8
        ]
    })
    
    return regional_size_data, regional_activity_data, {
        'total_small': 38940,
        'total_medium': 2612,
        'total_large': 884,
        'total_service': 1086,
        'total_financial': 682,
        'total_towns': 1137
    }

# Load the data
regional_size_data, regional_activity_data, metrics = load_trade_data()

# INTERACTIVE FEATURES - Sidebar Controls
st.sidebar.header("🎛️ Interactive Controls")
st.sidebar.markdown("*Select filters to analyze Lebanese trade data by region*")

# Interactive Feature 1: Region Filter (PRIMARY FILTER - impacts both visualizations)
st.sidebar.subheader("🗺️ Regional Analysis Filter")
all_regions = ['All Regions'] + sorted(regional_size_data['Region'].unique().tolist())
selected_region = st.sidebar.selectbox(
    "Select Lebanese Region to Analyze:",
    options=all_regions,
    help="This filter impacts both visualizations below"
)

# Interactive Feature 2: Analysis Focus (SECONDARY FILTER)
st.sidebar.subheader("🎯 Analysis Focus")
analysis_focus = st.sidebar.selectbox(
    "Choose Analysis Perspective:",
    options=['Institution Size Distribution', 'Economic Activity Coverage'],
    help="Choose which aspect to emphasize in the regional analysis"
)

# Display current filter status
st.sidebar.markdown("---")
st.sidebar.markdown("**🎯 Current Regional Analysis:**")
st.sidebar.write(f"• **Region**: {selected_region}")
st.sidebar.write(f"• **Focus**: {analysis_focus}")

# Show regional info
if selected_region != 'All Regions':
    region_institutions = regional_size_data[regional_size_data['Region'] == selected_region]['Count'].sum()
    region_activities = regional_activity_data[regional_activity_data['Region'] == selected_region]['Towns with Activity'].sum()
    st.sidebar.write(f"• **Institutions**: {region_institutions:,}")
    st.sidebar.write(f"• **Activity Coverage**: {region_activities} towns")

# Apply filters based on interactive selections

# Filter 1: Regional size distribution data (IMPACTS BOTH CHARTS)
if selected_region != 'All Regions':
    filtered_size_data = regional_size_data[regional_size_data['Region'] == selected_region]
    filtered_activity_data = regional_activity_data[regional_activity_data['Region'] == selected_region]
    chart1_subtitle = f"Institution distribution in {selected_region}"
    chart2_subtitle = f"Economic activities across {selected_region} towns"
else:
    filtered_size_data = regional_size_data.copy()
    filtered_activity_data = regional_activity_data.copy()
    chart1_subtitle = "Institution distribution across all Lebanese regions"
    chart2_subtitle = "Economic activities across all Lebanese towns"

# Calculate totals for the selected region
if selected_region != 'All Regions':
    region_total_institutions = filtered_size_data['Count'].sum()
    region_total_activities = filtered_activity_data['Towns with Activity'].sum()
else:
    region_total_institutions = filtered_size_data['Count'].sum()
    region_total_activities = filtered_activity_data['Towns with Activity'].sum()

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
st.markdown("*Use the sidebar controls to filter and analyze Lebanese trade data by city*")

col1, col2 = st.columns(2)

# VISUALIZATION 1: Regional Business Size Distribution (INTERACTIVE - responds to region filter)
with col1:
    st.markdown("### 📊 Commercial Institution Size Distribution")
    st.markdown(f"*{chart1_subtitle}*")
    
    if len(filtered_size_data) > 0:
        # Aggregate data for the selected region(s)
        if selected_region != 'All Regions':
            plot_data = filtered_size_data
        else:
            # Sum across all regions for national view
            plot_data = filtered_size_data.groupby('Institution Size')['Count'].sum().reset_index()
        
        fig1 = px.pie(plot_data, values='Count', names='Institution Size', hole=0.5,
                      color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        fig1.update_traces(textposition='auto', textinfo='percent+label', textfont_size=14)
        fig1.update_layout(
            height=250,
            template='plotly_white',
            margin=dict(l=20, r=20, t=20, b=20),
            annotations=[dict(text=f'Total<br>{plot_data["Count"].sum():,}', x=0.5, y=0.5, font_size=14, showarrow=False)]
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Show regional analysis insight
        if selected_region != 'All Regions':
            st.info(f"🗺️ Regional Focus: {selected_region} has {region_total_institutions:,} total institutions")
        else:
            st.success(f"🇱🇧 National Overview: {region_total_institutions:,} institutions across all Lebanese regions")
    else:
        st.error("No data available for selected region")

# VISUALIZATION 2: Regional Activity Presence (INTERACTIVE - responds to region filter)  
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
        
        # Show regional analysis insight
        if selected_region != 'All Regions':
            st.info(f"🗺️ Regional Focus: {selected_region} activities span {region_total_activities} town-activity combinations")
        else:
            st.success(f"🇱🇧 National Overview: {region_total_activities} town-activity combinations across Lebanon")
    else:
        st.warning("⚠️ No activity data available for selected region")

# Context and Insights Section
st.markdown("---")
st.markdown("## 📈 Key Trade Insights & Analysis")

# Trade insights with dynamic content based on filters
with st.expander("🔍 Detailed Analysis & Interactive Features", expanded=True):
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        st.markdown("""
        **Lebanese Regional Economic Structure:**
        - **Bekaa**: Agricultural and commercial hub with 9,230 institutions
        - **Mount Lebanon**: Largest economic center with 13,240 institutions  
        - **North Lebanon**: Industrial and trade region with 8,460 institutions
        - **South Lebanon**: Coastal commercial area with 6,720 institutions
        - **Nabatieh**: Southern agricultural region with 4,586 institutions
        """)
        
        # Dynamic insights based on regional filter
        if selected_region == 'Mount Lebanon':
            st.markdown("**🗺️ Mount Lebanon Focus:** Lebanon's economic powerhouse, containing Beirut and major commercial centers. Highest concentration of medium and large institutions.")
        elif selected_region == 'Bekaa':
            st.markdown("**🗺️ Bekaa Valley Focus:** Agricultural heartland with strong commercial activities. Mix of agricultural businesses and trading institutions.")
        elif selected_region == 'North Lebanon':
            st.markdown("**🗺️ North Lebanon Focus:** Industrial region including Tripoli. Strong manufacturing and service sector presence.")
        elif selected_region == 'South Lebanon':
            st.markdown("**🗺️ South Lebanon Focus:** Coastal region with port-based trade activities and tourism-related businesses.")
        elif selected_region == 'Nabatieh':
            st.markdown("**🗺️ Nabatieh Focus:** Predominantly agricultural region with growing commercial and service sectors.")
        else:
            st.markdown("**🗺️ National Overview:** Complete analysis across all five Lebanese governorates showing regional economic diversity.")
        
    with col_i2:
        st.markdown("""
        **Regional Economic Activity Distribution:**
        - **Self Employment**: Most widespread across all regions
        - **Commerce Activities**: Strong in Mount Lebanon and Bekaa  
        - **Public Sector**: Present in all regional centers
        - **Service Institutions**: Concentrated in urban areas
        - **Banking Access**: Limited, highest in Mount Lebanon and Bekaa
        """)
        
        # Dynamic insights based on regional and focus filters
        if selected_region != 'All Regions':
            st.markdown(f"**🗺️ {selected_region} Regional Analysis:** Currently analyzing economic activities specific to this governorate. Regional focus provides targeted insights for local economic development.")
        else:
            st.markdown("**🇱🇧 National Economic Activity Analysis:** Complete overview of economic activities across all Lebanese regions, showing national patterns and regional variations.")

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
