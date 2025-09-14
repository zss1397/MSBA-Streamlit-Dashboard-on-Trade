# Install Streamlit
pip install streamlit plotly pandas numpy

# Save the code as 'app.py' and run
streamlit run app.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Lebanon Trade & Economic Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .insight-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Create sample data function
@st.cache_data
def load_data():
    # Sample trade data based on Lebanese cities and regions
    np.random.seed(42)  # For reproducible results
    
    towns = ['Beirut', 'Tripoli', 'Sidon', 'Tyre', 'Zahle', 'Baalbek', 'Nabatieh', 'Jounieh', 'Byblos', 'Aley']
    regions = ['Beirut Governorate', 'North Lebanon', 'South Lebanon', 'Bekaa', 'Mount Lebanon']
    
    trade_data = []
    for i, town in enumerate(towns):
        trade_data.append({
            'City': town,
            'Region': np.random.choice(regions),
            'Small_Institutions': np.random.randint(20, 120),
            'Medium_Institutions': np.random.randint(5, 40),
            'Large_Institutions': np.random.randint(1, 15),
            'Service_Institutions': np.random.randint(10, 60),
            'Banking_Institutions': np.random.randint(2, 20),
            'Self_Employment': np.random.randint(15, 80),
            'Commerce_Activities': np.random.randint(20, 100),
            'Population': np.random.randint(50000, 2000000)
        })
    
    trade_df = pd.DataFrame(trade_data)
    
    # Calculate total institutions
    trade_df['Total_Institutions'] = (trade_df['Small_Institutions'] + 
                                    trade_df['Medium_Institutions'] + 
                                    trade_df['Large_Institutions'])
    
    # Sample debt data for regional comparison
    years = list(range(2015, 2025))
    countries = ['Lebanon', 'Jordan', 'Syria', 'Turkey', 'Egypt']
    
    debt_data = []
    for country in countries:
        base_debt = np.random.uniform(20000000000, 100000000000)  # 20B to 100B
        for year in years:
            trend_factor = (year - 2015) * 0.08
            seasonal_factor = np.sin((year - 2015) * 0.5) * 0.1
            noise = np.random.uniform(-0.15, 0.15)
            debt_value = base_debt * (1 + trend_factor + seasonal_factor + noise)
            
            debt_data.append({
                'Country': country,
                'Year': year,
                'External_Debt_USD': debt_value,
                'GDP_Ratio': np.random.uniform(40, 150)  # Debt-to-GDP ratio
            })
    
    debt_df = pd.DataFrame(debt_data)
    
    return trade_df, debt_df

# Load data
trade_df, debt_df = load_data()

# Main title
st.markdown('<h1 class="main-header">🏪 Lebanon Trade & Economic Analysis Dashboard</h1>', unsafe_allow_html=True)

# Sidebar for interactive controls
st.sidebar.header("🎛️ Interactive Controls")

# Interactive Feature 1: Region Filter
st.sidebar.subheader("Filter by Region")
selected_regions = st.sidebar.multiselect(
    "Select Regions to Display:",
    options=trade_df['Region'].unique(),
    default=trade_df['Region'].unique()
)

# Interactive Feature 2: Institution Size Focus
st.sidebar.subheader("Institution Analysis")
institution_focus = st.sidebar.selectbox(
    "Focus on Institution Size:",
    options=['All Sizes', 'Small Institutions', 'Medium Institutions', 'Large Institutions']
)

# Interactive Feature 3: Year Range for Debt Analysis
st.sidebar.subheader("Time Period Analysis")
year_range = st.sidebar.slider(
    "Select Year Range for Debt Analysis:",
    min_value=2015,
    max_value=2024,
    value=(2018, 2023),
    step=1
)

# Interactive Feature 4: Country Comparison
st.sidebar.subheader("Country Comparison")
selected_countries = st.sidebar.multiselect(
    "Compare Countries:",
    options=debt_df['Country'].unique(),
    default=['Lebanon', 'Jordan', 'Turkey']
)

# Filter data based on user selections
filtered_trade_df = trade_df[trade_df['Region'].isin(selected_regions)]
filtered_debt_df = debt_df[
    (debt_df['Year'] >= year_range[0]) & 
    (debt_df['Year'] <= year_range[1]) &
    (debt_df['Country'].isin(selected_countries))
]

# Main content area
col1, col2 = st.columns([2, 1])

with col2:
    # Key metrics
    st.subheader("📈 Key Metrics")
    
    total_institutions = filtered_trade_df['Total_Institutions'].sum()
    avg_institutions_per_city = filtered_trade_df['Total_Institutions'].mean()
    
    st.markdown(f"""
    <div class="metric-card">
        <h3>{total_institutions:,}</h3>
        <p>Total Commercial Institutions</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-card">
        <h3>{avg_institutions_per_city:.1f}</h3>
        <p>Average per City</p>
    </div>
    """, unsafe_allow_html=True)

with col1:
    # Insight box
    st.markdown(f"""
    <div class="insight-box">
        <strong>💡 Key Insights:</strong><br>
        • Analyzing <strong>{len(selected_regions)}</strong> regions with <strong>{len(filtered_trade_df)}</strong> cities<br>
        • Total of <strong>{total_institutions:,}</strong> commercial institutions<br>
        • Debt analysis covers <strong>{year_range[1] - year_range[0] + 1}</strong> years across <strong>{len(selected_countries)}</strong> countries
    </div>
    """, unsafe_allow_html=True)

# Visualization 1: Interactive Bar Chart
st.subheader("🏢 Commercial Institutions by City and Size")

# Prepare data based on institution focus
if institution_focus == 'All Sizes':
    fig1 = px.bar(
        filtered_trade_df, 
        x='City', 
        y=['Small_Institutions', 'Medium_Institutions', 'Large_Institutions'],
        title=f"Distribution of Institution Sizes Across {len(selected_regions)} Selected Regions",
        labels={'value': 'Number of Institutions', 'variable': 'Institution Size'},
        color_discrete_map={
            'Small_Institutions': '#ff7f0e',
            'Medium_Institutions': '#2ca02c', 
            'Large_Institutions': '#1f77b4'
        }
    )
    fig1.update_layout(barmode='group', height=500)
else:
    column_map = {
        'Small Institutions': 'Small_Institutions',
        'Medium Institutions': 'Medium_Institutions', 
        'Large Institutions': 'Large_Institutions'
    }
    selected_column = column_map[institution_focus]
    
    fig1 = px.bar(
        filtered_trade_df,
        x='City',
        y=selected_column,
        title=f"{institution_focus} Distribution Across Cities",
        color='Region',
        height=500
    )
    fig1.update_layout(showlegend=True)

fig1.update_xaxes(tickangle=45)
st.plotly_chart(fig1, use_container_width=True)

# Visualization 2: Interactive Line Chart for Debt Analysis
st.subheader("💰 External Debt Trends Analysis")

fig2 = px.line(
    filtered_debt_df,
    x='Year',
    y='External_Debt_USD',
    color='Country',
    title=f"External Debt Trends ({year_range[0]}-{year_range[1]})",
    labels={'External_Debt_USD': 'External Debt (USD)'},
    markers=True
)

fig2.update_layout(
    height=500,
    yaxis_tickformat='.2s',
    hovermode='x unified'
)

# Add annotations for Lebanon if selected
if 'Lebanon' in selected_countries:
    lebanon_data = filtered_debt_df[filtered_debt_df['Country'] == 'Lebanon']
    if not lebanon_data.empty:
        max_debt_year = lebanon_data.loc[lebanon_data['External_Debt_USD'].idxmax(), 'Year']
        max_debt_value = lebanon_data['External_Debt_USD'].max()
        
        fig2.add_annotation(
            x=max_debt_year,
            y=max_debt_value,
            text=f"Peak: ${max_debt_value/1e9:.1f}B",
            showarrow=True,
            arrowhead=2,
            arrowcolor="red"
        )

st.plotly_chart(fig2, use_container_width=True)

# Additional Analysis Section
st.subheader("🔍 Detailed Analysis")

col3, col4 = st.columns(2)

with col3:
    # Pie chart for regional distribution
    regional_totals = filtered_trade_df.groupby('Region')['Total_Institutions'].sum().reset_index()
    
    fig3 = px.pie(
        regional_totals,
        values='Total_Institutions',
        names='Region',
        title="Institution Distribution by Region",
        hole=0.4
    )
    fig3.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    # Scatter plot: Population vs Total Institutions
    fig4 = px.scatter(
        filtered_trade_df,
        x='Population',
        y='Total_Institutions',
        size='Commerce_Activities',
        color='Region',
        title="Population vs Commercial Institutions",
        hover_data=['City'],
        size_max=20
    )
    fig4.update_layout(height=400)
    st.plotly_chart(fig4, use_container_width=True)

# Summary Statistics
st.subheader("📊 Summary Statistics")

col5, col6 = st.columns(2)

with col5:
    st.write("**Trade Data Summary (Filtered)**")
    st.dataframe(filtered_trade_df.describe(), use_container_width=True)

with col6:
    st.write("**Debt Data Summary (Filtered)**")
    debt_summary = filtered_debt_df.groupby('Country')['External_Debt_USD'].agg(['mean', 'max', 'min']).round(0)
    debt_summary.columns = ['Average Debt', 'Maximum Debt', 'Minimum Debt']
    st.dataframe(debt_summary, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666666;'>
    <p>📊 Interactive Dashboard created for MSBA 325 - Streamlit Practice Activity</p>
    <p>Data includes Lebanese commercial institutions and regional debt analysis</p>
</div>
""", unsafe_allow_html=True)
