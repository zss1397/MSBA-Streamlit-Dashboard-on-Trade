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
        height: 180px !important;
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
        font-size: 0.85rem;
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
    
    # Economic sector data for pie chart
    sector_data = pd.DataFrame({
        'Sector': ['Commercial Institutions', 'Service Institutions', 'Financial Institutions'],
        'Total Count': [42436, 1086, 682],
        'Percentage': [97.6, 2.4, 1.5]
    })
    
    # Comprehensive economic activity presence analysis (all 5 binary columns)
    activity_presence = pd.DataFrame({
        'Activity Type': ['Self Employment', 'Commerce', 'Public Sector', 'Service Institutions', 'Banking'],
        'Towns with Activity': [722, 493, 207, 126, 91],
        'Percentage': [63.5, 43.4, 18.2, 11.1, 8.0]
    })
    
    # Banking accessibility analysis (detailed)
    banking_data = pd.DataFrame({
        'Banking Access': ['Towns with Banking', 'Towns without Banking'],
        'Number of Towns': [91, 1046],
        'Access Rate': ['8.0%', '92.0%']
    })
    
    # Geographic data for Lebanon map - ALL 25 DISTRICTS (Real Data)
    top_commercial_towns = pd.DataFrame({
        'Town': ['Zahle', 'Baalbek-Hermel', 'Baabda', 'Sidon', 'Matn', 'Akkar', 'Mount Lebanon', 'Hermel', 'Nabatieh', 'Tyre', 'Keserwan', 'Zgharta', 'Aley', 'Byblos', 'Miniyeh-Danniyeh', 'South', 'Koura', 'Chouf', 'North', 'Rashaya', 'West Bekaa', 'Marjeyoun', 'Bent Jbeil', 'Hasbaya', 'Bsharri'],
        'Total_All_Business': [10981, 5446, 4152, 3513, 3280, 2360, 1707, 1600, 1544, 1395, 1223, 1184, 1150, 780, 695, 560, 524, 502, 440, 430, 420, 380, 350, 320, 280],
        'Region': ['Bekaa', 'Bekaa', 'Mount Lebanon', 'South Lebanon', 'Mount Lebanon', 'North Lebanon', 'Mount Lebanon', 'Bekaa', 'Nabatieh', 'South Lebanon', 'Mount Lebanon', 'North Lebanon', 'Mount Lebanon', 'Mount Lebanon', 'North Lebanon', 'South Lebanon', 'North Lebanon', 'Mount Lebanon', 'North Lebanon', 'Bekaa', 'Bekaa', 'Nabatieh', 'Nabatieh', 'Nabatieh', 'North Lebanon'],
        'lat': [33.8467, 34.0059, 33.8369, 33.5630, 33.8869, 34.5300, 33.8547, 34.3928, 33.3781, 33.2728, 34.0961, 34.3983, 33.8031, 34.1181, 34.4736, 33.5000, 34.3039, 33.7031, 34.4361, 33.5089, 33.8100, 33.3600, 33.1200, 33.4000, 34.2506],
        'lon': [35.9017, 36.2181, 35.5131, 35.3783, 35.6500, 36.1181, 35.8623, 36.3667, 35.4842, 35.2039, 35.8478, 35.8972, 35.8031, 35.6481, 36.0061, 35.4000, 35.7244, 35.6131, 35.8339, 35.8200, 35.9500, 35.5900, 35.3800, 35.6500, 36.0139]
    })
    
    return size_distribution, sector_data, activity_presence, banking_data, top_commercial_towns, {
        'total_small': 38940,
        'total_medium': 2612,
        'total_large': 884,
        'total_service': 1086,
        'total_financial': 682,
        'total_towns': 1137
    }

# Load the data
size_dist, sector_data, activity_data, banking_data, map_data, metrics = load_trade_data()

# INTERACTIVE FEATURES - Sidebar Controls
st.sidebar.header("🎛️ Interactive Controls")

# Interactive Feature 1: Region Filter
st.sidebar.subheader("Filter by Region")
all_regions = ['All Regions'] + sorted(map_data['Region'].unique().tolist())
selected_region = st.sidebar.selectbox(
    "Select Region to Analyze:",
    options=all_regions
)

# Interactive Feature 2: Institution Size Focus
st.sidebar.subheader("Institution Size Analysis")
size_focus = st.sidebar.selectbox(
    "Focus on Institution Size:",
    options=['All Sizes', 'Small Institutions Only', 'Medium Institutions Only', 'Large Institutions Only']
)

# Interactive Feature 3: Activity Type Display
st.sidebar.subheader("Activity Type Filter")
activity_types = st.sidebar.multiselect(
    "Show Activity Types:",
    options=['Self Employment', 'Commerce', 'Public Sector', 'Service Institutions', 'Banking'],
    default=['Self Employment', 'Commerce', 'Public Sector', 'Service Institutions', 'Banking']
)

# Interactive Feature 4: Map Business Size Filter
st.sidebar.subheader("Map Display Options")
min_business_count = st.sidebar.slider(
    "Minimum Business Count to Show on Map:",
    min_value=0,
    max_value=5000,
    value=0,
    step=100
)

# Apply filters based on interactive selections
# Filter map data by region
if selected_region != 'All Regions':
    filtered_map_data = map_data[map_data['Region'] == selected_region]
else:
    filtered_map_data = map_data.copy()

# Filter map data by business count
filtered_map_data = filtered_map_data[filtered_map_data['Total_All_Business'] >= min_business_count]

# Filter size distribution data
if size_focus == 'Small Institutions Only':
    filtered_size_dist = size_dist[size_dist['Institution Size'] == 'Small Institutions']
elif size_focus == 'Medium Institutions Only':
    filtered_size_dist = size_dist[size_dist['Institution Size'] == 'Medium Institutions']
elif size_focus == 'Large Institutions Only':
    filtered_size_dist = size_dist[size_dist['Institution Size'] == 'Large Institutions']
else:
    filtered_size_dist = size_dist.copy()

# Filter activity data
filtered_activity_data = activity_data[activity_data['Activity Type'].isin(activity_types)]

# Update metrics based on filters
if selected_region != 'All Regions':
    region_business_count = filtered_map_data['Total_All_Business'].sum()
    region_towns_count = len(filtered_map_data)
else:
    region_business_count = map_data['Total_All_Business'].sum()
    region_towns_count = len(map_data)

# Display current filter status
st.sidebar.markdown("---")
st.sidebar.markdown("**Current Filters:**")
st.sidebar.write(f"Region: {selected_region}")
st.sidebar.write(f"Size Focus: {size_focus}")
st.sidebar.write(f"Activity Types: {len(activity_types)} selected")
st.sidebar.write(f"Min Business Count: {min_business_count}")

# Key Metrics Row (Updated based on filters)
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
with col_m1:
    st.metric("Total Commercial Institutions", f"{metrics['total_small'] + metrics['total_medium'] + metrics['total_large']:,}")
with col_m2:
    st.metric("Small Businesses", f"{metrics['total_small']:,}")
with col_m3:
    st.metric("Service Institutions", f"{metrics['total_service']:,}")
with col_m4:
    if selected_region != 'All Regions':
        st.metric(f"Businesses in {selected_region}", f"{region_business_count:,}")
    else:
        st.metric("Financial Institutions", f"{metrics['total_financial']:,}")
with col_m5:
    if selected_region != 'All Regions':
        st.metric(f"Towns in {selected_region}", f"{region_towns_count:,}")
    else:
        st.metric("Towns Analyzed", f"{metrics['total_towns']:,}")

# 5 Trade Visualizations (Updated with Interactive Features)
col1, col2 = st.columns(2)

# Visualization 1: Business Size Distribution (Interactive - responds to size_focus)
with col1:
    if size_focus == 'All Sizes':
        chart_title = "Commercial Institution Size Distribution"
    else:
        chart_title = f"Focus: {size_focus}"
    
    st.markdown(f"### {chart_title}")
    
    if len(filtered_size_dist) > 0:
        fig1 = px.pie(filtered_size_dist, values='Count', names='Institution Size', hole=0.5,
                      color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        fig1.update_traces(textposition='auto', textinfo='percent+label', textfont_size=12)
        fig1.update_layout(
            height=180,
            template='plotly_white',
            margin=dict(l=30, r=30, t=5, b=10),
            annotations=[dict(text=f'Total<br>{filtered_size_dist["Count"].sum():,}', x=0.5, y=0.5, font_size=12, showarrow=False)]
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No data available for selected filter")

# Visualization 2: Economic Sector Distribution
with col2:
    st.markdown("### Economic Sector Distribution")
    fig2 = px.pie(sector_data, values='Total Count', names='Sector',
                  color_discrete_sequence=['#FFD700', '#4169E1', '#8A2BE2'])
    fig2.update_traces(textposition='auto', textinfo='percent+label', textfont_size=12)
    fig2.update_layout(
        height=180,
        template='plotly_white',
        margin=dict(l=30, r=30, t=5, b=10)
    )
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

# Visualization 3: Activity Presence (Interactive - responds to activity_types filter)
with col3:
    st.markdown("### Economic Activity Presence Across Towns")
    
    if len(filtered_activity_data) > 0:
        fig3 = px.bar(filtered_activity_data, y='Activity Type', x='Towns with Activity', orientation='h',
                      color='Towns with Activity', color_continuous_scale='RdYlGn')
        fig3.update_layout(
            height=180,
            template='plotly_white',
            margin=dict(l=80, r=10, t=5, b=25),
            coloraxis_showscale=False,
            font=dict(size=10),
            xaxis_title='Number of Towns'
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Please select at least one activity type")

# Visualization 4: Banking Accessibility
with col4:
    st.markdown("### Banking Institution Accessibility")
    fig4 = px.bar(banking_data, x='Banking Access', y='Number of Towns',
                  color='Banking Access', color_discrete_sequence=['#1f77b4', '#ff7f0e'])
    fig4.update_layout(
        height=180,
        template='plotly_white',
        margin=dict(l=30, r=10, t=5, b=40),
        font=dict(size=10),
        showlegend=False,
        yaxis_title='Number of Towns'
    )
    # Add percentage labels on bars
    fig4.add_annotation(x=0, y=91 + 30, text='8.0%', showarrow=False, font=dict(size=12, color='black'))
    fig4.add_annotation(x=1, y=1046 + 30, text='92.0%', showarrow=False, font=dict(size=12, color='black'))
    
    st.plotly_chart(fig4, use_container_width=True)

# Visualization 5: Geographic Map (Interactive - responds to region and business count filters)
if selected_region != 'All Regions':
    map_title = f"Business Distribution in {selected_region} (Min: {min_business_count} businesses)"
else:
    map_title = f"Business Distribution Across Lebanon (Min: {min_business_count} businesses)"

st.markdown(f"### {map_title}")

if len(filtered_map_data) > 0:
    fig5 = px.scatter_mapbox(filtered_map_data, 
                            lat='lat', lon='lon', 
                            size='Total_All_Business',
                            color='Total_All_Business',
                            hover_name='Town',
                            hover_data={'Total_All_Business': True, 'Region': True, 'lat': False, 'lon': False},
                            color_continuous_scale='Viridis',
                            size_max=25,
                            zoom=7 if selected_region == 'All Regions' else 8,
                            center=dict(lat=33.8547, lon=35.8623))

    fig5.update_layout(
        mapbox_style="open-street-map",
        height=300,
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_showscale=True
    )
    st.plotly_chart(fig5, use_container_width=True)
    
    # Show filtered results summary
    st.info(f"Showing {len(filtered_map_data)} towns/districts with {filtered_map_data['Total_All_Business'].sum():,} total businesses")
else:
    st.warning("No towns meet the current filter criteria. Try reducing the minimum business count.")

# Footer
st.markdown("**MSBA 325 Trade Analysis | Commercial Institutions • Service Activities • Economic Distribution**")

# Trade insights (Enhanced with interactive context)
with st.expander("📈 Key Trade Insights"):
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        st.markdown("""
        **Economic Structure:**
        - Small enterprises: 38,940 institutions (91.8% by volume)
        - Commercial sector dominates: 42,436 vs 1,768 service/financial
        - Limited large enterprise presence across Lebanon
        """)
    with col_i2:
        st.markdown(f"""
        **Current Analysis ({selected_region}):**
        - Activity types shown: {len(activity_types)} of 5 categories
        - Institution focus: {size_focus}
        - Map showing: {len(filtered_map_data)} locations
        - Minimum business threshold: {min_business_count:,}
        """)
