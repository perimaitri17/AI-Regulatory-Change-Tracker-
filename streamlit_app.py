import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Page config
st.set_page_config(
    page_title="AI Regulatory Change Tracker",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS - simplified
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%);
    color: white;
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    text-align: center;
}
.change-card {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    border-left: 4px solid #3b82f6;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin: 1rem 0;
}
.severity-high { border-left-color: #dc2626 !important; }
.severity-medium { border-left-color: #f59e0b !important; }
.severity-low { border-left-color: #10b981 !important; }
</style>
""", unsafe_allow_html=True)

# Data
@st.cache_data
def load_data():
    return pd.DataFrame([
        {
            'Region': 'US',
            'Authority': 'FDA',
            'Title': 'New Drug Application Review Timeline Update',
            'Therapeutic_Area': 'Oncology',
            'Product': 'Keytruda (Pembrolizumab)',
            'Manufacturer': 'Merck',
            'Change_Type': 'Approval Process',
            'Severity': 'High',
            'Date': '2025-08-10',
            'Description': 'FDA announces expedited review process for combination therapies in metastatic melanoma',
            'Impact': 'May accelerate approval timeline by 3-6 months for qualifying products',
            'Document_Changes': 'Updates required to Module 2.7 Clinical Summary and Risk Assessment sections',
            'Status': 'Active'
        },
        {
            'Region': 'EU',
            'Authority': 'EMA',
            'Title': 'GLP-1 Agonist Manufacturing Guidelines',
            'Therapeutic_Area': 'Diabetes',
            'Product': 'Ozempic (Semaglutide)',
            'Manufacturer': 'Novo Nordisk',
            'Change_Type': 'Manufacturing',
            'Severity': 'Medium',
            'Date': '2025-08-09',
            'Description': 'Updated manufacturing quality requirements for GLP-1 receptor agonists',
            'Impact': 'New stability testing protocols required, may affect production timelines',
            'Document_Changes': 'CMC section 3.2.P.8 requires additional stability data and impurity profiles',
            'Status': 'Pending Review'
        },
        {
            'Region': 'India',
            'Authority': 'CDSCO',
            'Title': 'Cardiovascular Drug Safety Monitoring',
            'Therapeutic_Area': 'Cardiology',
            'Product': 'Lipitor (Atorvastatin)',
            'Manufacturer': 'Pfizer',
            'Change_Type': 'Safety Monitoring',
            'Severity': 'High',
            'Date': '2025-08-08',
            'Description': 'Enhanced pharmacovigilance requirements for statin medications',
            'Impact': 'Quarterly safety reports now mandatory, increased AERS reporting frequency',
            'Document_Changes': 'Risk Management Plan (RMP) requires update to Section 3 - Safety Specification',
            'Status': 'Implementation Required'
        },
        {
            'Region': 'US',
            'Authority': 'FDA',
            'Title': 'Oncology Real-World Evidence Guidelines',
            'Therapeutic_Area': 'Oncology',
            'Product': 'CAR-T Therapies',
            'Manufacturer': 'Multiple',
            'Change_Type': 'Clinical Evidence',
            'Severity': 'High',
            'Date': '2025-08-07',
            'Description': 'New requirements for real-world evidence in CAR-T cell therapy submissions',
            'Impact': 'Additional long-term follow-up studies required, expanded patient registries',
            'Document_Changes': 'Clinical Study Report template updated - new Section 16 for RWE data',
            'Status': 'Active'
        }
    ])

# Load data
df = load_data()

# Header
st.markdown("""
<div class="main-header">
    <h1>🏥 AI Regulatory Change Tracker</h1>
    <p>Pharma-focused regulatory intelligence with workflow automation</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("🔍 Filters")

# Filters
regions = ['All Regions'] + sorted(df['Region'].unique().tolist())
selected_region = st.sidebar.selectbox("Select Region", regions)

therapeutic_areas = ['All Areas'] + sorted(df['Therapeutic_Area'].unique().tolist())
selected_therapeutic = st.sidebar.selectbox("Select Therapeutic Area", therapeutic_areas)

search_term = st.sidebar.text_input("🔍 Search Products/Companies")

# Apply filters
filtered_df = df.copy()

if selected_region != 'All Regions':
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]

if selected_therapeutic != 'All Areas':
    filtered_df = filtered_df[filtered_df['Therapeutic_Area'] == selected_therapeutic]

if search_term:
    mask = (filtered_df['Product'].str.contains(search_term, case=False, na=False) |
            filtered_df['Manufacturer'].str.contains(search_term, case=False, na=False))
    filtered_df = filtered_df[mask]

# Main content
tab1, tab2 = st.tabs(["📊 Regulatory Changes", "⚡ Workflow Automation"])

with tab1:
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Changes", len(filtered_df))
    
    with col2:
        high_count = len(filtered_df[filtered_df['Severity'] == 'High'])
        st.metric("High Impact", high_count)
    
    with col3:
        active_count = len(filtered_df[filtered_df['Status'] == 'Active'])
        st.metric("Active Changes", active_count)
    
    with col4:
        impl_count = len(filtered_df[filtered_df['Status'] == 'Implementation Required'])
        st.metric("Action Required", impl_count)
    
    # Charts
    if len(filtered_df) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            region_counts = filtered_df['Region'].value_counts()
            fig1 = px.pie(values=region_counts.values, names=region_counts.index, 
                         title="Changes by Region")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            severity_counts = filtered_df['Severity'].value_counts()
            fig2 = px.bar(x=severity_counts.index, y=severity_counts.values,
                         title="Changes by Severity")
            st.plotly_chart(fig2, use_container_width=True)
    
    # Display changes
    st.subheader(f"📋 Regulatory Changes ({len(filtered_df)} found)")
    
    for idx, row in filtered_df.iterrows():
        severity_class = f"severity-{row['Severity'].lower()}"
        
        with st.expander(f"🔍 {row['Title']} - {row['Product']}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="change-card {severity_class}">
                    <h4>📍 {row['Region']} - {row['Authority']}</h4>
                    <p><strong>Product:</strong> {row['Product']}</p>
                    <p><strong>Manufacturer:</strong> {row['Manufacturer']}</p>
                    <p><strong>Therapeutic Area:</strong> {row['Therapeutic_Area']}</p>
                    <p><strong>Severity:</strong> {row['Severity']}</p>
                    <p><strong>Status:</strong> {row['Status']}</p>
                    <p><strong>Date:</strong> {row['Date']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="change-card">
                    <h4>📝 Description</h4>
                    <p>{row['Description']}</p>
                    
                    <h4>💼 Business Impact</h4>
                    <p>{row['Impact']}</p>
                    
                    <h4>📄 Document Changes Required</h4>
                    <p style="background: #fef2f2; padding: 10px; border-radius: 5px;">
                        {row['Document_Changes']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"📧 Send Alert", key=f"alert_{idx}"):
                    st.success("✅ Alert sent!")
            with col2:
                if st.button(f"📅 Schedule Review", key=f"schedule_{idx}"):
                    st.success("✅ Review scheduled!")
            with col3:
                if st.button(f"📊 Generate Report", key=f"report_{idx}"):
                    st.success("✅ Report generated!")

with tab2:
    st.header("⚡ Workflow Automation")
    st.subheader("Free Integration Options Available Now")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📧 Email Notifications
        Automated alerts via SMTP integration
        
        🟢 **Status:** Active
        """)
    
    with col2:
        st.markdown("""
        ### 💬 Slack Integration  
        Real-time notifications to team channels
        
        🟢 **Status:** Ready to Connect
        """)
    
    with col3:
        st.markdown("""
        ### 🔗 Webhook API
        Connect to existing workflow systems
        
        🔵 **Status:** Available
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 🤖 Automated Actions Available
    - ✅ Auto-generate document change summaries
    - ✅ Schedule team notifications based on severity
    - ✅ Create calendar reminders for compliance deadlines  
    - ✅ Export filtered reports to CSV/PDF
    - ✅ Trigger workflow integrations via webhooks
    - ✅ Generate regulatory impact assessments
    """)
    
    # Configuration
    st.subheader("⚙️ Quick Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("📧 Email for Alerts", placeholder="regulatory@company.com")
        st.selectbox("🔔 Alert Frequency", ["Immediate", "Daily", "Weekly"])
    
    with col2:
        st.multiselect("👥 Team Members", ["Regulatory", "Quality", "Legal", "Product"])
        st.selectbox("⚠️ Severity Threshold", ["All", "Medium & High", "High Only"])

# Footer
st.markdown("---")
st.markdown(f"🔄 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("🌐 Data sources: FDA, EMA, CDSCO")
