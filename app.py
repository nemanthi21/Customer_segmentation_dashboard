import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


st.set_page_config(
    page_title='Customer Segmentation Dashboard',
    layout='wide'
)

#load data
def load_data():
    df=pd.read_csv('data/finalRFM_data.csv')
    return df
try:
    rfm=load_data()
    st.success("Data loaded successfully")
except Exception as e:
    st.error("Data loading failed")
    st.stop()


st.title("Customer Segmentation Analysis Dashboard")
st.markdown(""" 
This dashboard analysis customer behaviour using RFM Score and segment customers into distinct groups for targeted marketing strategies.
            """)
st.markdown("---")

st.sidebar.header("Filters")

#check if segment column exists
if 'Segment' in rfm.columns:
    segments=['All']+ list(rfm["Segment"].unique())
    selected_segment=st.sidebar.selectbox("Select segment",segments)

    if selected_segment !='All':
        filtered_data=rfm[rfm["Segment"]==selected_segment]
    else:
        filtered_data=rfm

else:
    st.sidebar.warning("No segment column found")
    filtered_data=rfm
    selected_segment='All'

with st.expander("Dataset Information"):
    col1,col2,col3=st.columns(3)
    col1.metric("Total customers" , len(rfm))
    col2.metric("Filtered Customers",len(filtered_data))
    col3.metric("Features",len(rfm.columns))

    st.dataframe(filtered_data.head(10))

st.markdown("---")

st.header("Key Perfomance Indicators")

col1,col2,col3,col4=st.columns(4)

with col1:
    total_customers=len(filtered_data)
    st.metric(
        label="Total customers",
        value=f"{total_customers}",
        delta=f"{selected_segment}"
    )

with col2:
    if 'Monetary' in filtered_data.columns:
        avg_monetary = filtered_data['Monetary'].mean()
        st.metric(
            label="Avg Customer Value",
            value=f"{avg_monetary:,.0f}"
        )
    else:
        st.metric("Avg Customer Value", "N/A")

with col3:
    if 'Frequency' in filtered_data.columns:
        avg_frequency=filtered_data['Frequency'].mean()
        st.metric(
            label="Avg Purchase Frequency",
            value=f'{avg_frequency:.1f}'
        )
    else:
        st.metric("avg frequency",)

with col4:
    if "Recency" in filtered_data.columns:
        avg_recency=filtered_data['Recency'].mean()
        st.metric(
            label="Avg visiting recency ",
            value=f"{avg_recency:.0f} days"
        )
    else:
        st.metric("Avg frequency ",'N/A')

st.markdown("---")

st.header("Customer Segmentation Visualization")
has_rfm=all(col in rfm.columns for col in ['Recency','Frequency','Monetary'])
has_segment='Segment' in rfm.columns

if has_segment:
    col1,col2=st.columns(2)

    with col1:
        st.subheader("Customer Distribution by Segment")
        segment_counts=rfm["Segment"].value_counts().reset_index()
        segment_counts.columns=['Segment','Count']

        fig_pie=px.pie(
            segment_counts,
            values='Count',
            names='Segment',
            title='Segment Distribution',
            color_discrete_sequence=px.colors.qualitative.Set3

        )
        st.plotly_chart(fig_pie , use_container_width=True)

    with col2:
        st.subheader("Customers per segment")
        fig_bar=px.bar(
                segment_counts,
             x='Segment',
            y='Count',
            title='Number of customers by segment',
            color='Segment',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_bar , use_container_width=True)

if has_rfm:
    st.markdown("---")

    st.subheader("RFM Metrics Distribution")

    col1,col2,col3=st.columns(3)

    with col1:
        fig_recency=px.histogram(
            filtered_data,
            x='Recency',
            title='Recency Distribution',
            nbins=50,
            color_discrete_sequence=["#E26AEF"]
        )
        st.plotly_chart(fig_recency , use_container_width=True)
    
    with col2:
        fig_freq=px.histogram(
            filtered_data,
            x="Frequency",
            title="Frequency Distribution",
            nbins=50,
            color_discrete_sequence=["#6ABCEF"]


        )
        st.plotly_chart(fig_freq,use_container_width=True)
    
    with col3:
        fig_monetory=px.histogram(
            filtered_data,
            x="Monetary",
            title="Monetary Distribution",
            nbins=50,
            color_discrete_sequence=["#6AEF7C"]
        )
        st.plotly_chart(fig_monetory,use_container_width=True)

if has_segment and has_rfm:
    st.markdown("---")

    st.subheader("Segment Statistics")

    segment_stats=rfm.groupby('Segment').agg({
        'Recency':'mean',
        'Frequency':'mean',
        'Monetary':['mean','sum','count']
    }).round(2)

    segment_stats.columns=['Avg Recency','Avg Frequency','Avg Monetary','Total Revenue','Customer Count']
    segment_stats=segment_stats.reset_index()

    st.dataframe(segment_stats,use_container_width=True)
    st.markdown("---")

    st.subheader("Segment Profile Comparison")

    fig_profile=go.Figure()

    for metric in ['Avg Recency','Avg Frequency','Avg Monetary']:
        fig_profile.add_trace(go.Bar(
            name=metric,
            x=segment_stats['Segment'],
            y=segment_stats[metric]
        ))

        fig_profile.update_layout(
            title='Average RFM Values by segment',
            barmode='group',
            xaxis_title='Segment',
            yaxis_title='Value'
        )

        st.plotly_chart(fig_profile,use_container_width=True)
st.markdown("---")
st.header("Key Insights & Recommendations")

if has_segment:
    segments_found = rfm['Segment'].unique()

    insights = {
        'VVIP Customers': {
            'emoji': '🌟',
            'color': 'green',
            'insight': 'Focus on retention programs and VIP experiences. These customers generate the highest revenue.'
        },
        'VIP Customers': {
            'emoji': '📊',
            'color': 'blue',
            'insight': 'Target with upselling campaigns. They have potential to move to high-value segment.'
        },
        'Regular Customers': {
            'emoji': '💡',
            'color': 'orange',
            'insight': 'Engage with educational content and entry-level offers to build loyalty.'
        },
        'Lost Customers': {
            'emoji': '⚠️',
            'color': 'red',
            'insight': 'Implement win-back campaigns immediately with special discounts.'
        }
    }

    cols_per_row = 3
    for i in range(0, len(segments_found), cols_per_row):
        cols = st.columns(cols_per_row)
        for col, segment in zip(cols, segments_found[i:i+cols_per_row]):
            info = insights.get(
                segment,
                {'emoji': '📌', 'color': 'gray', 'insight': 'Analyze this segment further.'}
            )
            with col:
                st.markdown(f"### {info['emoji']} {segment}")
                st.markdown(f":{info['color']}[{info['insight']}]")

else:
    st.info("Segment column not found. Please ensure your data includes customer segments.")

st.markdown("---")
st.markdown(""" 
            Built with Streamlit 🎈 | Customer Segmentation Analysis Project
            """)
