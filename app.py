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
    
    # Fixed totals calculation
    total_small = 8500 + 12200 + 7800 + 6200 + 4240  # 38,940
    total_medium = 580 + 820 + 520 + 410 + 282       # 2,612  
    total_large = 150 + 220 + 140 + 110 + 64         # 684
    total_institutions = total_small + total_medium + total_large  # 42,236
    
    return regional_size_data, regional_activity_data, {
        'total_small': total_small,
        'total_medium': total_medium,
        'total_large': total_large,
        'total_institutions': total_institutions,
        'total_service': 1086,
        'total_financial': 682,
        'total_towns': 1137
    }

# Load the data
regional_size_data, regional_activity_data, metrics = load_trade_data()

# INTERACTIVE FEATURES - Sidebar Controls
st.sidebar.header("🎛️ Interactive Controls")
st.sidebar.markdown("*Select filters to analyze Lebanese trade data*")

# Interactive Feature 1: Region Filter (PRIMARY FILTER - impacts both visualizations)
st.sidebar.subheader("🗺️ Regional Analysis Filter")
all_regions = ['All Regions'] + sorted(regional_size_data['Region'].unique().tolist())
selected_region = st.sidebar.selectbox(
    "Select Lebanese Region to Analyze:",
    options=all_regions,
    help="This filter impacts both visualizations below"
)

# Interactive Feature 2: Institution Size Filter (SECONDARY FILTER - impacts both visualizations)
st.sidebar.subheader("🏢 Institution Size Filter")
institution_sizes = st.sidebar.multiselect(
    "Select Institution Sizes to Include:",
    options=['Small Institutions', 'Medium Institutions', 'Large Institutions'],
    default=['Small Institutions', 'Medium Institutions', 'Large Institutions'],
    help="Choose which business sizes to include in the analysis"
)

# Display current filter status
st.sidebar.markdown("---")
st.sidebar.markdown("**🎯 Current Analysis Filters:**")
st.sidebar.write(f"• **Region**: {selected_region}")
st.sidebar.write(f"• **Institution Sizes**: {', '.join(institution_sizes) if institution_sizes else 'None selected'}")

# Show regional info
if selected_region != 'All Regions':
    region_institutions = regional_size_data[regional_size_data['Region'] == selected_region]['Count'].sum()
    region_activities = regional_activity_data[regional_activity_data['Region'] == selected_region]['Towns with Activity'].sum()
    st.sidebar.write(f"• **Total Institutions**: {region_institutions:,}")
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

# Filter 2: Institution size filter (IMPACTS VISUALIZATION 1)
if institution_sizes:
    filtered_size_data = filtered_size_data[filtered_size_data['Institution Size'].isin(institution_sizes)]
    if len(institution_sizes) < 3:
        size_types = ' + '.join(institution_sizes)
        if selected_region != 'All Regions':
            chart1_subtitle = f"{size_types} in {selected_region}"
        else:
            chart1_subtitle = f"{size_types} across all Lebanese regions"
else:
    # If no institution sizes selected, create empty dataframe
    filtered_size_data = filtered_size_data.iloc[0:0]

# Calculate totals for the selected filters
if len(filtered_size_data) > 0:
    filtered_total_institutions = filtered_size_data['Count'].sum()
else:
    filtered_total_institutions = 0

if len(filtered_activity_data) > 0:
    filtered_total_activities = filtered_activity_data['Towns with Activity'].sum()
else:
    filtered_total_activities = 0

# Key Metrics Row (CORRECTED TOTALS)
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
with col_m1:
    st.metric("Total Commercial Institutions", f"{metrics['total_institutions']:,}")
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

# VISUALIZATION 1: Regional Business Size Distribution (INTERACTIVE - responds to both filters)
with col1:
    st.markdown("### 📊 Commercial Institution Size Distribution")
    st.markdown(f"*{chart1_subtitle}*")
    
    if len(filtered_size_data) > 0:
        # Aggregate data for the selected region(s) and institution sizes
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
        
        # Show filter-based insights
        if len(institution_sizes) < 3:
            st.info(f"🏢 Showing {', '.join(institution_sizes)} only: {filtered_total_institutions:,} institutions")
        elif selected_region != 'All Regions':
            st.info(f"🗺️ Regional Focus: {selected_region} has {filtered_total_institutions:,} total institutions")
        else:
            st.success(f"🇱🇧 National Overview: {filtered_total_institutions:,} institutions across all Lebanese regions")
    else:
        if not institution_sizes:
            st.warning("⚠️ Please select at least one institution size to display data")
        else:
            st.error("No data available for selected filters")

# VISUALIZATION 2: Regional Activity Presence (INTERACTIVE - responds to region filter)  
with col2:
    st.markdown("### 🏬 Economic Activity Presence Across Towns")
    st.markdown(f"*{chart2_subtitle}*")
    
    if len(filtered_activity_data) > 0:
        # Aggregate data for cleaner visualization
        if selected_region != 'All Regions':
            # For single region, show simple bar chart
            plot_data2 = filtered_activity_data
            fig2 = px.bar(plot_data2, x='Towns with Activity', y='Activity Type', orientation='h',
                          color='Activity Type', 
                          color_discrete_sequence=['#2E8B57', '#4ECDC4', '#FF6B6B', '#45B7D1', '#FFA07A'],
                          text='Towns with Activity')
        else:
            # For all regions, sum by activity type for cleaner view
            plot_data2 = filtered_activity_data.groupby('Activity Type')['Towns with Activity'].sum().reset_index()
            plot_data2 = plot_data2.sort_values('Towns with Activity', ascending=True)
            fig2 = px.bar(plot_data2, x='Towns with Activity', y='Activity Type', orientation='h',
                          color='Activity Type',
                          color_discrete_sequence=['#2E8B57', '#4ECDC4', '#FF6B6B', '#45B7D1', '#FFA07A'],
                          text='Towns with Activity')
        
        fig2.update_traces(textposition='outside', textfont_size=12, texttemplate='%{text}')
        fig2.update_layout(
            height=250,
            template='plotly_white',
            margin=dict(l=120, r=40, t=20, b=30),
            showlegend=False,
            font=dict(size=11),
            xaxis_title='Number of Towns with Activity',
            yaxis_title='',
            xaxis=dict(showgrid=True, gridcolor='lightgray'),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Show regional analysis insight
        if selected_region != 'All Regions':
            st.info(f"🗺️ Regional Focus: {selected_region} activities span {filtered_total_activities} town-activity combinations")
        else:
            st.success(f"🇱🇧 National Overview: {filtered_total_activities} town-activity combinations across Lebanon")
    else:
        st.warning("⚠️ No activity data available for selected region")

# Context and Insights Section (CONVERTED TO BULLET POINTS)
st.markdown("---")
st.markdown("## 📈 Key Trade Insights & Analysis")

# Trade insights with bullet points instead of filter-style content
with st.expander("🔍 Detailed Analysis & Interactive Features", expanded=True):
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        st.markdown("**Lebanese Regional Economic Structure:**")
        st.markdown("- **Bekaa** - Agricultural and commercial hub with 9,230 institutions")
        st.markdown("- **Mount Lebanon** - Largest economic center with 13,240 institutions")
        st.markdown("- **North Lebanon** - Industrial and trade region with 8,460 institutions")
        st.markdown("- **South Lebanon** - Coastal commercial area with 6,720 institutions")
        st.markdown("- **Nabatieh** - Southern agricultural region with 4,586 institutions")
        
        # Dynamic insights based on regional filter (in bullet format)
        if selected_region == 'Mount Lebanon':
            st.markdown("**🗺️ Mount Lebanon Regional Analysis:**")
            st.markdown("- Lebanon's economic powerhouse containing Beirut and major commercial centers")
            st.markdown("- Highest concentration of medium and large institutions (1,040 total)")
            st.markdown("- Dominant in financial and service sectors")
            st.markdown("- Key driver of national economic activity")
        elif selected_region == 'Bekaa':
            st.markdown("**🗺️ Bekaa Valley Regional Analysis:**")
            st.markdown("- Agricultural heartland with strong commercial activities")
            st.markdown("- Mix of agricultural businesses and trading institutions")
            st.markdown("- Strong self-employment and commerce presence")
            st.markdown("- Important food production and distribution hub")
        elif selected_region == 'North Lebanon':
            st.markdown("**🗺️ North Lebanon Regional Analysis:**")
            st.markdown("- Industrial region including Tripoli port city")
            st.markdown("- Strong manufacturing and service sector presence")
            st.markdown("- Significant commercial and trade activities")
            st.markdown("- Strategic location for regional commerce")
        elif selected_region == 'South Lebanon':
            st.markdown("**🗺️ South Lebanon Regional Analysis:**")
            st.markdown("- Coastal region with port-based trade activities")
            st.markdown("- Tourism-related businesses and services")
            st.markdown("- Agricultural and fishing industries")
            st.markdown("- Cross-border trade significance")
        elif selected_region == 'Nabatieh':
            st.markdown("**🗺️ Nabatieh Regional Analysis:**")
            st.markdown("- Predominantly agricultural region")
            st.markdown("- Growing commercial and service sectors")
            st.markdown("- Smallest but developing economic base")
            st.markdown("- Traditional and modern business mix")
        else:
            st.markdown("**🇱🇧 National Economic Overview:**")
            st.markdown("- Complete analysis across all five Lebanese governorates")
            st.markdown("- Shows regional economic diversity and specialization")
            st.markdown("- Mount Lebanon dominates with 31% of all institutions")
            st.markdown("- Small businesses comprise 92% of all commercial institutions")
        
    with col_i2:
        st.markdown("**Regional Economic Activity Distribution:**")
        st.markdown("- **Self Employment** - Most widespread across all regions (722 towns)")
        st.markdown("- **Commerce Activities** - Strong in Mount Lebanon and Bekaa (493 towns)")
        st.markdown("- **Public Sector** - Present in all regional centers (207 towns)")
        st.markdown("- **Service Institutions** - Concentrated in urban areas (126 towns)")
        st.markdown("- **Banking Access** - Limited coverage, highest in Mount Lebanon (91 towns)")
        
        # Dynamic activity insights based on regional filter (in bullet format)
        if selected_region != 'All Regions':
            region_activities_detail = filtered_activity_data.groupby('Activity Type')['Towns with Activity'].sum().to_dict()
            st.markdown(f"**🗺️ {selected_region} Activity Analysis:**")
            for activity, count in region_activities_detail.items():
                st.markdown(f"- **{activity}** - {count} towns with activity")
            st.markdown(f"- **Total Coverage** - {sum(region_activities_detail.values())} town-activity combinations")
        else:
            st.markdown("**🇱🇧 National Activity Analysis:**")
            st.markdown("- **Complete Coverage** - 1,639 town-activity combinations across Lebanon")
            st.markdown("- **Self Employment Dominance** - Present in 44% of all town-activity combinations")
            st.markdown("- **Commerce Concentration** - Strong presence in major economic centers")
            st.markdown("- **Service Distribution** - Varies significantly by regional development level")



st.markdown("---")
st.markdown("### 📊 Key Insights & Analysis Summary")
col_final1, col_final2 = st.columns(2)

with col_final1:
    st.markdown("**Economic Distribution Insights:**")
    st.markdown("- Small businesses dominate Lebanon's commercial landscape (92% of institutions)")
    st.markdown("- Mount Lebanon leads with 31% of all commercial institutions")
    st.markdown("- Regional specialization varies significantly across governorates")
    st.markdown("- Banking access remains limited, concentrated in major centers")

with col_final2:
    st.markdown("**Interactive Dashboard Benefits:**")
    st.markdown("- Real-time filtering enables targeted regional analysis")
    st.markdown("- Dynamic visualizations adapt to user selections")
    st.markdown("- Comprehensive view of Lebanese trade sector structure")
    st.markdown("- Professional analytics tool built with Streamlit and Plotly")


# Interactive Features Summary & Final Analysis
st.markdown("---")
st.markdown("### 🎛️ Interactive Features Summary")
col_s1, col_s2 = st.columns(2)

with col_s1:
    st.markdown("**Feature 1: Regional Analysis Filter**")
    st.markdown("- Primary filter affecting both visualizations")
    st.markdown("- Choose specific Lebanese governorates or view all regions")
    st.markdown("- Shows institution distribution and activity presence by region")
    st.markdown("- Provides targeted regional economic analysis")
    st.markdown("- Updates metrics and insights dynamically")

with col_s2:
    st.markdown("**Feature 2: Institution Size Filter**")
    st.markdown("- Secondary filter affecting the pie chart visualization")
    st.markdown("- Select which business sizes to include (Small/Medium/Large)")
    st.markdown("- Enables analysis of specific institution scales")
    st.markdown("- Combines with regional filter for detailed insights")
    st.markdown("- Updates totals and percentages dynamically")
