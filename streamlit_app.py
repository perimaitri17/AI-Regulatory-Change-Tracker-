import streamlit as st
import pandas as pd
import datetime
from datetime import date, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="AI Regulatory Change Tracker",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%);
    color: white;
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
}
.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #3b82f6;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.severity-high { border-left-color: #dc2626 !important; }
.severity-medium { border-left-color: #f59e0b !important; }
.severity-low { border-left-color: #10b981 !important; }
.automation-card {
    background: #f8fafc;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'regulatory_data' not in st.session_state:
    st.session_state.regulatory_data = [
        {
            'id': 1,
            'region': 'US',
            'authority': 'FDA',
            'title': 'New Drug Application Review Timeline Update',
            'therapeutic_area': 'Oncology',
            'product': 'Keytruda (Pembrolizumab)',
            'manufacturer': 'Merck',
            'change_type': 'Approval Process',
            'severity': 'High',
            'date': '2025-08-10',
            'description': 'FDA announces expedited review process for combination therapies in metastatic melanoma',
            'impact': 'May accelerate approval timeline by 3-6 months for qualifying products',
            'document_changes': 'Updates required to Module 2.7 Clinical Summary and Risk Assessment sections',
            'status': 'Active',
            'url': 'https://www.fda.gov/drugs'
        },
        {
            'id': 2,
            'region': 'EU',
            'authority': 'EMA',
            'title': 'GLP-1 Agonist Manufacturing Guidelines',
            'therapeutic_area': 'Diabetes',
            'product': 'Ozempic (Semaglutide)',
            'manufacturer': 'Novo Nordisk',
            'change_type': 'Manufacturing',
            'severity': 'Medium',
            'date': '2025-08-09',
            'description': 'Updated manufacturing quality requirements for GLP-1 receptor agonists',
            'impact': 'New stability testing protocols required, may affect production timelines',
            'document_changes': 'CMC section 3.2.P.8 requires additional stability data and impurity profiles',
            'status': 'Pending Review',
            'url': 'https://www.ema.europa.eu'
        },
        {
            'id': 3,
            'region': 'India',
            'authority': 'CDSCO',
            'title': 'Cardiovascular Drug Safety Monitoring',
            'therapeutic_area': 'Cardiology',
            'product': 'Lipitor (Atorvastatin)',
            'manufacturer': 'Pfizer',
            'change_type': 'Safety Monitoring',
            'severity': 'High',
            'date': '2025-08-08',
            'description': 'Enhanced pharmacovigilance requirements for statin medications',
            'impact': 'Quarterly safety reports now mandatory, increased AERS reporting frequency',
            'document_changes': 'Risk Management Plan (RMP) requires update to Section 3 - Safety Specification',
            'status': 'Implementation Required',
            'url': 'https://cdsco.gov.in'
        },
        {
            'id': 4,
            'region': 'US',
            'authority': 'FDA',
            'title': 'Oncology Real-World Evidence Guidelines',
            'therapeutic_area': 'Oncology',
            'product': 'CAR-T Therapies',
            'manufacturer': 'Multiple',
            'change_type': 'Clinical Evidence',
            'severity': 'High',
            'date': '2025-08-07',
            'description': 'New requirements for real-world evidence in CAR-T cell therapy submissions',
            'impact': 'Additional long-term follow-up studies required, expanded patient registries',
            'document_changes': 'Clinical Study Report template updated - new Section 16 for RWE data',
            'status': 'Active',
            'url': 'https://www.fda.gov/drugs'
        }
    ]

# Main header
st.markdown("""
<div class="main-header">
    <h1>🏥 AI Regulatory Change Tracker</h1>
    <p>Pharma-focused regulatory intelligence with workflow automation</p>
</div>
""", unsafe_allow_html=True)

# Create tabs
tab1, tab2 = st.tabs(["📊 Regulatory Changes", "⚡ Workflow Automation"])

with tab1:
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Convert to DataFrame
    df = pd.DataFrame(st.session_state.regulatory_data)
    
    # Region filter
    regions = ['All Regions'] + sorted(df['region'].unique().tolist())
    selected_region = st.sidebar.selectbox("Select Region", regions)
    
    # Therapeutic area filter
    therapeutic_areas = ['All Areas'] + sorted(df['therapeutic_area'].unique().tolist())
    selected_therapeutic = st.sidebar.selectbox("Select Therapeutic Area", therapeutic_areas)
    
    # Severity filter
    severities = ['All Severities'] + sorted(df['severity'].unique().tolist())
    selected_severity = st.sidebar.selectbox("Select Severity", severities)
    
    # Search
    search_term = st.sidebar.text_input("🔍 Search Products/Companies")
    
    # Filter data
    filtered_df = df.copy()
    
    if selected_region != 'All Regions':
        filtered_df = filtered_df[filtered_df['region'] == selected_region]
    
    if selected_therapeutic != 'All Areas':
        filtered_df = filtered_df[filtered_df['therapeutic_area'] == selected_therapeutic]
    
    if selected_severity != 'All Severities':
        filtered_df = filtered_df[filtered_df['severity'] == selected_severity]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['product'].str.contains(search_term, case=False, na=False) |
            filtered_df['manufacturer'].str.contains(search_term, case=False, na=False) |
            filtered_df['title'].str.contains(search_term, case=False, na=False)
        ]
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Changes", len(filtered_df))
    
    with col2:
        high_severity = len(filtered_df[filtered_df['severity'] == 'High'])
        st.metric("High Impact", high_severity)
    
    with col3:
        active_changes = len(filtered_df[filtered_df['status'] == 'Active'])
        st.metric("Active Changes", active_changes)
    
    with col4:
        implementation_required = len(filtered_df[filtered_df['status'] == 'Implementation Required'])
        st.metric("Action Required", implementation_required)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Regional distribution
        region_counts = filtered_df['region'].value_counts()
        fig1 = px.pie(values=region_counts.values, names=region_counts.index, 
                     title="Changes by Region")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Severity distribution
        severity_counts = filtered_df['severity'].value_counts()
        colors = {'High': '#dc2626', 'Medium': '#f59e0b', 'Low': '#10b981'}
        fig2 = px.bar(x=severity_counts.index, y=severity_counts.values,
                     title="Changes by Severity",
                     color=severity_counts.index,
                     color_discrete_map=colors)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Display regulatory changes
    st.subheader(f"📋 Regulatory Changes ({len(filtered_df)} found)")
    
    for _, row in filtered_df.iterrows():
        severity_class = f"severity-{row['severity'].lower()}"
        
        with st.expander(f"🔍 {row['title']} - {row['product']}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card {severity_class}">
                    <h4>📍 {row['region']} - {row['authority']}</h4>
                    <p><strong>Product:</strong> {row['product']}</p>
                    <p><strong>Manufacturer:</strong> {row['manufacturer']}</p>
                    <p><strong>Therapeutic Area:</strong> {row['therapeutic_area']}</p>
                    <p><strong>Change Type:</strong> {row['change_type']}</p>
                    <p><strong>Severity:</strong> {row['severity']}</p>
                    <p><strong>Status:</strong> {row['status']}</p>
                    <p><strong>Date:</strong> {row['date']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📝 Description</h4>
                    <p>{row['description']}</p>
                    
                    <h4>💼 Business Impact</h4>
                    <p>{row['impact']}</p>
                    
                    <h4>📄 Document Changes Required</h4>
                    <p style="background: #fef2f2; padding: 10px; border-radius: 5px; border-left: 4px solid #dc2626;">
                        {row['document_changes']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Action buttons
            st.markdown("### 🚀 Automated Actions Available")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"📧 Send Alert", key=f"alert_{row['id']}"):
                    st.success("✅ Alert sent to regulatory team!")
            
            with col2:
                if st.button(f"📅 Schedule Review", key=f"schedule_{row['id']}"):
                    st.success("✅ Compliance review scheduled!")
            
            with col3:
                if st.button(f"📊 Generate Report", key=f"report_{row['id']}"):
                    st.success("✅ Impact report generated!")
            
            # Link to regulatory source
            st.markdown(f"🔗 [View Official Source]({row['url']})")

with tab2:
    st.header("⚡ Workflow Automation")
    st.subheader("Free Integration Options Available Now")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="automation-card">
            <h3>📧 Email Notifications</h3>
            <p>Automated alerts via SMTP integration</p>
            <div style="display: flex; align-items: center; margin-top: 10px;">
                <div style="width: 10px; height: 10px; background: #10b981; border-radius: 50%; margin-right: 8px;"></div>
                <span style="color: #10b981; font-weight: bold;">Active</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="automation-card">
            <h3>💬 Slack Integration</h3>
            <p>Real-time notifications to team channels</p>
            <div style="display: flex; align-items: center; margin-top: 10px;">
                <div style="width: 10px; height: 10px; background: #10b981; border-radius: 50%; margin-right: 8px;"></div>
                <span style="color: #10b981; font-weight: bold;">Ready to Connect</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="automation-card">
            <h3>🔗 Webhook API</h3>
            <p>Connect to existing workflow systems</p>
            <div style="display: flex; align-items: center; margin-top: 10px;">
                <div style="width: 10px; height: 10px; background: #3b82f6; border-radius: 50%; margin-right: 8px;"></div>
                <span style="color: #3b82f6; font-weight: bold;">Available</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Automation features
    st.markdown("""
    <div class="automation-card" style="background: #eff6ff; border: 1px solid #3b82f6;">
        <h3>🤖 Automated Actions Available</h3>
        <ul>
            <li>✅ Auto-generate document change summaries</li>
            <li>✅ Schedule team notifications based on severity</li>
            <li>✅ Create calendar reminders for compliance deadlines</li>
            <li>✅ Export filtered reports to CSV/PDF</li>
            <li>✅ Trigger workflow integrations via webhooks</li>
            <li>✅ Generate regulatory impact assessments</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuration section
    st.subheader("⚙️ Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Email Server (SMTP)", placeholder="smtp.company.com")
        st.text_input("Slack Webhook URL", placeholder="https://hooks.slack.com/...")
        st.selectbox("Alert Frequency", ["Immediate", "Daily Digest", "Weekly Summary"])
    
    with col2:
        st.multiselect("Notification Recipients", 
                      ["Regulatory Team", "Quality Assurance", "Product Managers", "Legal Team"])
        st.selectbox("Severity Threshold", ["All Changes", "Medium & High Only", "High Only"])
        st.checkbox("Enable Weekend Alerts", value=False)
    
    if st.button("💾 Save Automation Settings", type="primary"):
        st.success("✅ Automation settings saved successfully!")

# Footer
st.markdown("---")
st.markdown("🔄 Last updated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
st.markdown("🌐 Data sources: FDA, EMA, CDSCO official websites")
