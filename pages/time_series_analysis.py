import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Read the CSV file
df = pd.read_csv('DATA.csv')

# Convert date column to datetime
df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')

# Convert sales_amount to numeric, handling any non-numeric values
df['sales_amount'] = pd.to_numeric(df['sales_amount'], errors='coerce')

# Add time hierarchies
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['quarter'] = df['date'].dt.quarter
df['month_name'] = df['date'].dt.strftime('%B')
df['quarter_name'] = 'Q' + df['quarter'].astype(str)

# Page config
st.set_page_config(page_title="Time Series Analysis", layout="wide")
st.title("Hierarchical Time Series Analysis")

# Sidebar filters
st.sidebar.header("Filters")

# Add region filter
selected_regions = st.sidebar.multiselect(
    "Select Regions",
    options=df['region'].unique(),
    default=df['region'].unique()
)

selected_products = st.sidebar.multiselect(
    "Select Products",
    options=df['product'].unique(),
    default=df['product'].unique()
)

# Filter the data
filtered_df = df[
    (df['product'].isin(selected_products)) &
    (df['region'].isin(selected_regions))
]

# Create tabs for different analyses
tab1, tab2, tab3 = st.tabs(["Revenue Distribution", "Order Status Distribution", "Product Performance"])

with tab1:
    st.header("Revenue Distribution Over Time")
    
    # Hierarchical revenue data
    revenue_hierarchy = filtered_df.groupby(['year', 'quarter_name', 'month_name'])['sales_amount'].sum().reset_index()
    
    # Create treemap for revenue hierarchy
    fig1 = px.treemap(
        revenue_hierarchy,
        path=[px.Constant("Total"), 'year', 'quarter_name', 'month_name'],
        values='sales_amount',
        title='Revenue Distribution: Year → Quarter → Month',
        color='sales_amount',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Monthly trend line
    monthly_revenue = filtered_df.groupby('date')['sales_amount'].sum().reset_index()
    fig2 = px.line(
        monthly_revenue,
        x='date',
        y='sales_amount',
        title='Daily Revenue Trend',
        labels={'date': 'Date', 'sales_amount': 'Revenue'}
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.header("Order Status Distribution Over Time")
    
    # Calculate order status distribution by month
    status_dist = filtered_df.groupby(['year', 'month_name', 'order_status']).size().reset_index(name='count')
    
    # Create sunburst chart for order status hierarchy
    fig3 = px.sunburst(
        status_dist,
        path=['year', 'month_name', 'order_status'],
        values='count',
        title='Order Status Distribution: Year → Month → Status'
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # Stacked bar chart showing status distribution over time
    fig4 = px.bar(
        status_dist,
        x='month_name',
        y='count',
        color='order_status',
        title='Monthly Order Status Distribution',
        barmode='stack'
    )
    st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.header("Product Performance Over Time")
    
    # Product performance metrics
    product_metrics = filtered_df.groupby(['year', 'month_name', 'product']).agg({
        'sales_amount': 'sum',
        'order_status': lambda x: (x == 'Returned').mean() * 100,  # Return rate
    }).reset_index()
    product_metrics.columns = ['year', 'month_name', 'product', 'revenue', 'return_rate']
    
    # Create scatter plot matrix
    fig5 = px.scatter(
        product_metrics,
        x='revenue',
        y='return_rate',
        color='product',
        size='revenue',
        hover_data=['year', 'month_name'],
        title='Product Performance: Revenue vs Return Rate'
    )
    st.plotly_chart(fig5, use_container_width=True)
    
    # Heatmap of product performance by month
    pivot_data = filtered_df.pivot_table(
        values='sales_amount',
        index='product',
        columns='month_name',
        aggfunc='sum'
    )
    
    fig6 = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='Viridis'
    ))
    fig6.update_layout(
        title='Product Performance Heatmap by Month',
        xaxis_title='Month',
        yaxis_title='Product'
    )
    st.plotly_chart(fig6, use_container_width=True)

# Add time-based metrics in sidebar
st.sidebar.markdown("### Time-Based Metrics")

# Current month metrics
current_month = filtered_df['date'].max().strftime('%B %Y')
current_month_data = filtered_df[filtered_df['date'] == filtered_df['date'].max()]

st.sidebar.markdown(f"#### {current_month} Metrics")
st.sidebar.metric(
    "Monthly Revenue",
    f"${current_month_data['sales_amount'].sum():,.2f}"
)
st.sidebar.metric(
    "Monthly Orders",
    len(current_month_data)
)

# Month-over-month growth
current_month_revenue = filtered_df[filtered_df['date'].dt.month == filtered_df['date'].dt.month.max()]['sales_amount'].sum()
prev_month_revenue = filtered_df[filtered_df['date'].dt.month == filtered_df['date'].dt.month.max() - 1]['sales_amount'].sum()
if prev_month_revenue != 0:
    mom_growth = ((current_month_revenue - prev_month_revenue) / prev_month_revenue) * 100
    st.sidebar.metric(
        "Month-over-Month Growth",
        f"{mom_growth:,.1f}%",
        delta=f"{mom_growth:,.1f}%"
    ) 