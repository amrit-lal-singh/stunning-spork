import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Read the CSV file
df = pd.read_csv('DATA.csv')

# Convert sales_amount to numeric, handling any non-numeric values
df['sales_amount'] = pd.to_numeric(df['sales_amount'], errors='coerce')

# Create a Streamlit app
st.set_page_config(
    page_title="Sales Analysis Dashboard",
    layout="wide"
)

st.title("Sales Analysis Dashboard")

# Add filters in sidebar
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

selected_payment_methods = st.sidebar.multiselect(
    "Select Payment Methods",
    options=df['payment_method'].unique(),
    default=df['payment_method'].unique()
)

# Filter the data based on selections
filtered_df = df[
    (df['product'].isin(selected_products)) &
    (df['payment_method'].isin(selected_payment_methods)) &
    (df['region'].isin(selected_regions))
]

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Revenue Analysis", "Cancellation Analysis", "Return Analysis", "Hierarchical Time Series Analysis"])

with tab1:
    st.header("Product Revenue Analysis")
    
    # Calculate revenue by product
    product_revenue = filtered_df.groupby('product')['sales_amount'].sum().reset_index()
    product_revenue = product_revenue.sort_values('sales_amount', ascending=False)
    
    # Create a bar chart for product revenue
    fig1 = px.bar(
        product_revenue, 
        x='product', 
        y='sales_amount',
        title='Revenue by Product',
        labels={'product': 'Product', 'sales_amount': 'Total Revenue'},
        color='sales_amount',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Calculate revenue by payment method
    payment_revenue = filtered_df.groupby('payment_method')['sales_amount'].sum().reset_index()
    
    # Create a pie chart for payment method revenue
    fig2 = px.pie(
        payment_revenue, 
        values='sales_amount', 
        names='payment_method',
        title='Revenue by Payment Method'
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # Add revenue by region
    region_revenue = filtered_df.groupby('region')['sales_amount'].sum().reset_index()
    region_revenue = region_revenue.sort_values('sales_amount', ascending=False)
    
    # Create a bar chart for region revenue
    fig3 = px.bar(
        region_revenue,
        x='region',
        y='sales_amount',
        title='Revenue by Region',
        labels={'region': 'Region', 'sales_amount': 'Total Revenue'},
        color='sales_amount',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    st.header("Cancellation Analysis by Payment Method")
    
    # Filter for cancelled orders
    cancelled_df = filtered_df[filtered_df['order_status'] == 'Cancelled']
    
    # Calculate cancellation count by payment method
    cancellation_by_payment = cancelled_df.groupby('payment_method').size().reset_index(name='count')
    
    # Calculate total orders by payment method for percentage
    total_by_payment = filtered_df.groupby('payment_method').size().reset_index(name='total')
    
    # Merge to calculate cancellation rate
    cancellation_rate = pd.merge(cancellation_by_payment, total_by_payment, on='payment_method')
    cancellation_rate['cancellation_rate'] = cancellation_rate['count'] / cancellation_rate['total'] * 100
    
    # Create chart
    fig4 = px.bar(
        cancellation_rate,
        x='payment_method',
        y='cancellation_rate',
        title='Cancellation Rate by Payment Method (%)',
        labels={'payment_method': 'Payment Method', 'cancellation_rate': 'Cancellation Rate (%)'},
        color='cancellation_rate',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig4, use_container_width=True)
    
    # Add cancellation analysis by region
    cancellation_by_region = cancelled_df.groupby('region').size().reset_index(name='count')
    total_by_region = filtered_df.groupby('region').size().reset_index(name='total')
    
    # Merge to calculate cancellation rate by region
    cancellation_rate_region = pd.merge(cancellation_by_region, total_by_region, on='region')
    cancellation_rate_region['cancellation_rate'] = cancellation_rate_region['count'] / cancellation_rate_region['total'] * 100
    
    # Create chart for region cancellation
    fig5 = px.bar(
        cancellation_rate_region,
        x='region',
        y='cancellation_rate',
        title='Cancellation Rate by Region (%)',
        labels={'region': 'Region', 'cancellation_rate': 'Cancellation Rate (%)'},
        color='cancellation_rate',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig5, use_container_width=True)
    
    # Show raw data
    st.subheader("Cancelled Orders Data")
    st.dataframe(cancelled_df)

with tab3:
    st.header("Return Rate Analysis by Product")
    
    # Filter for returned orders
    returned_df = filtered_df[filtered_df['order_status'] == 'Returned']
    
    # Calculate return count by product
    return_by_product = returned_df.groupby('product').size().reset_index(name='count')
    
    # Calculate total orders by product for percentage
    total_by_product = filtered_df.groupby('product').size().reset_index(name='total')
    
    # Merge to calculate return rate
    return_rate = pd.merge(return_by_product, total_by_product, on='product')
    return_rate['return_rate'] = return_rate['count'] / return_rate['total'] * 100
    
    # Create chart
    fig6 = px.bar(
        return_rate,
        x='product',
        y='return_rate',
        title='Return Rate by Product (%)',
        labels={'product': 'Product', 'return_rate': 'Return Rate (%)'},
        color='return_rate',
        color_continuous_scale='Oranges'
    )
    st.plotly_chart(fig6, use_container_width=True)
    
    # Add return analysis by region
    return_by_region = returned_df.groupby('region').size().reset_index(name='count')
    
    # Reuse total_by_region or recalculate
    if 'total_by_region' not in locals():
        total_by_region = filtered_df.groupby('region').size().reset_index(name='total')
    
    # Merge to calculate return rate by region
    return_rate_region = pd.merge(return_by_region, total_by_region, on='region')
    return_rate_region['return_rate'] = return_rate_region['count'] / return_rate_region['total'] * 100
    
    # Create chart for region returns
    fig7 = px.bar(
        return_rate_region,
        x='region',
        y='return_rate',
        title='Return Rate by Region (%)',
        labels={'region': 'Region', 'return_rate': 'Return Rate (%)'},
        color='return_rate',
        color_continuous_scale='Oranges'
    )
    st.plotly_chart(fig7, use_container_width=True)
    
    # Show raw data
    st.subheader("Returned Orders Data")
    st.dataframe(returned_df)

with tab4:
    st.header("Hierarchical Time Series Analysis")

    # Convert date column to datetime
    filtered_df['date'] = pd.to_datetime(filtered_df['date'], format='%d/%m/%Y')

    # Add time hierarchies
    filtered_df['year'] = filtered_df['date'].dt.year
    filtered_df['month'] = filtered_df['date'].dt.month
    filtered_df['quarter'] = filtered_df['date'].dt.quarter
    filtered_df['month_name'] = filtered_df['date'].dt.strftime('%B')
    filtered_df['quarter_name'] = 'Q' + filtered_df['quarter'].astype(str)

    # Hierarchical decomposition for marketing spend
    marketing_hierarchy = filtered_df.groupby(['year', 'quarter_name', 'month_name', 'product', 'region', 'payment_method'])['marketing_spend'].sum().reset_index()

    fig_marketing = px.treemap(
        marketing_hierarchy,
        path=[px.Constant("Total Marketing Spend"), 'year', 'quarter_name', 'month_name', 'product', 'region', 'payment_method'],
        values='marketing_spend',
        title='Hierarchical Decomposition of Marketing Spend',
        color='marketing_spend',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_marketing, use_container_width=True)

    # Hierarchical decomposition for overall sales
    sales_hierarchy = filtered_df.groupby(['year', 'quarter_name', 'month_name', 'product', 'region', 'payment_method'])['sales_amount'].sum().reset_index()

    fig_sales = px.treemap(
        sales_hierarchy,
        path=[px.Constant("Total Sales"), 'year', 'quarter_name', 'month_name', 'product', 'region', 'payment_method'],
        values='sales_amount',
        title='Hierarchical Decomposition of Overall Sales',
        color='sales_amount',
        color_continuous_scale='Greens'
    )
    st.plotly_chart(fig_sales, use_container_width=True)

    # Monthly trend lines for marketing spend and sales with smoothing parameter
    st.sidebar.markdown("### Trend Smoothing")
    smoothing_window = st.sidebar.slider("Smoothing Window (days)", min_value=1, max_value=30, value=15)

    monthly_trends = filtered_df.groupby('date').agg({'marketing_spend': 'sum', 'sales_amount': 'sum'}).reset_index()
    monthly_trends['marketing_spend_smooth'] = monthly_trends['marketing_spend'].rolling(window=smoothing_window, min_periods=1).mean()
    monthly_trends['sales_amount_smooth'] = monthly_trends['sales_amount'].rolling(window=smoothing_window, min_periods=1).mean()

    fig_trends = px.line(
        monthly_trends,
        x='date',
        y=['marketing_spend_smooth', 'sales_amount_smooth'],
        title='Smoothed Monthly Trends: Marketing Spend vs Overall Sales',
        labels={'value': 'Amount', 'date': 'Date', 'variable': 'Metric'}
    )
    st.plotly_chart(fig_trends, use_container_width=True)

# Add information in sidebar
st.sidebar.markdown("### About")
st.sidebar.info("This dashboard provides interactive analysis of sales data including revenue contribution, cancellation rates, and return rates.")

# Add metrics
st.sidebar.markdown("### Key Metrics")
total_revenue = filtered_df['sales_amount'].sum()
total_orders = len(filtered_df)
cancellation_rate = len(cancelled_df) / total_orders * 100 if total_orders > 0 else 0
return_rate = len(returned_df) / total_orders * 100 if total_orders > 0 else 0

st.sidebar.metric("Total Revenue", f"${total_revenue:,.2f}")
st.sidebar.metric("Total Orders", total_orders)
st.sidebar.metric("Cancellation Rate", f"{cancellation_rate:.2f}%")
st.sidebar.metric("Return Rate", f"{return_rate:.2f}%")

# Add region breakdown metrics
st.sidebar.markdown("### Region Breakdown")
region_metrics = filtered_df.groupby('region')['sales_amount'].sum().reset_index()
for _, row in region_metrics.iterrows():
    st.sidebar.metric(f"{row['region']} Revenue", f"${row['sales_amount']:,.2f}")
