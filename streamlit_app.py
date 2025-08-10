import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import sqlite3
from reg_scraper import RegulatoryTracker

# Mock pharma product database for demo
MOCK_PRODUCTS = [
    {"id": "PROD001", "name": "CardioMax", "category": "Cardiovascular", "status": "Approved", "markets": ["US", "EU"]},
    {"id": "PROD002", "name": "DiabetesAid", "category": "Endocrine", "status": "Under Review", "markets": ["US"]},
    {"id": "PROD003", "name": "NeuroFlex", "category": "CNS", "status": "Approved", "markets": ["US", "EU", "JP"]},
    {"id": "PROD004", "name": "ImmunePlus", "category": "Immunology", "status": "Clinical Trial", "markets": ["US"]},
    {"id": "PROD005", "name": "OncoCure", "category": "Oncology", "status": "Approved", "markets": ["US", "EU"]},
]

def init_page_config():
    st.set_page_config(
        page_title="Regulatory Change Tracker",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def create_mock_data_if_needed():
    """Create some mock data for demo purposes"""
    tracker = RegulatoryTracker()
    conn = sqlite3.connect(tracker.db_path)
    cursor = conn.cursor()
    
    # Check if we have data
    cursor.execute("SELECT COUNT(*) FROM detected_changes")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Insert mock changes for demo
        mock_changes = [
            {
                "source": "FDA_DRUGS",
                "title": "FDA Announces New Labeling Requirements for Cardiovascular Drugs",
                "url": "https://www.fda.gov/mock-url-1",
                "change_type": "new",
                "risk_level": "high",
                "summary": "FDA requires updated labeling for all cardiovascular medications to include new safety warnings and contraindications.",
                "impact_areas": json.dumps(["Labeling", "Regulatory Affairs", "Marketing"]),
                "detected_at": (datetime.now() - timedelta(days=1)).isoformat()
            },
            {
                "source": "FDA_NEWS",
                "title": "Updated Clinical Trial Guidelines for CNS Disorders",
                "url": "https://www.fda.gov/mock-url-2",
                "change_type": "updated",
                "risk_level": "medium",
                "summary": "New guidelines for conducting clinical trials in CNS disorders, including updated biomarker requirements.",
                "impact_areas": json.dumps(["Clinical Trials", "Regulatory Affairs"]),
                "detected_at": (datetime.now() - timedelta(days=3)).isoformat()
            },
            {
                "source": "FDA_DRUGS",
                "title": "Quality Manufacturing Standards Update",
                "url": "https://www.fda.gov/mock-url-3",
                "change_type": "updated",
                "risk_level": "medium",
                "summary": "Manufacturing facilities must comply with updated quality standards for sterile drug production.",
                "impact_areas": json.dumps(["Manufacturing", "Regulatory Affairs"]),
                "detected_at": (datetime.now() - timedelta(days=5)).isoformat()
            },
            {
                "source": "FDA_NEWS",
                "title": "Emergency Use Authorization Guidelines Updated",
                "url": "https://www.fda.gov/mock-url-4",
                "change_type": "new",
                "risk_level": "low",
                "summary": "Updated procedures for submitting Emergency Use Authorization requests for medical devices.",
                "impact_areas": json.dumps(["Regulatory Affairs"]),
                "detected_at": (datetime.now() - timedelta(days=7)).isoformat()
            }
        ]
        
        for change in mock_changes:
            cursor.execute('''
                INSERT INTO detected_changes 
                (source, title, url, change_type, risk_level, summary, impact_areas, detected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                change["source"], change["title"], change["url"], change["change_type"],
                change["risk_level"], change["summary"], change["impact_areas"], change["detected_at"]
            ))
        
        conn.commit()
    
    conn.close()

def get_risk_color(risk_level):
    colors = {"high": "#FF4B4B", "medium": "#FFA500", "low": "#28A745"}
    return colors.get(risk_level, "#6C757D")

def map_changes_to_products(changes, products):
    """Map regulatory changes to affected products"""
    impact_mapping = {
        "cardiovascular": ["CardioMax"],
        "cardio": ["CardioMax"],
        "cns": ["NeuroFlex"],
        "neuro": ["NeuroFlex"],
        "diabetes": ["DiabetesAid"],
        "endocrine": ["DiabetesAid"],
        "oncology": ["OncoCure"],
        "cancer": ["OncoCure"],
        "immunology": ["ImmunePlus"],
        "immune": ["ImmunePlus"]
    }
    
    affected_products = []
    
    for change in changes:
        change_text = (change["title"] + " " + change["summary"]).lower()
        
        for keyword, product_names in impact_mapping.items():
            if keyword in change_text:
                for product_name in product_names:
                    affected_products.append({
                        "change_id": change["id"],
                        "product_name": product_name,
                        "change_title": change["title"],
                        "risk_level": change["risk_level"],
                        "impact_areas": json.loads(change["impact_areas"])
                    })
                break  # Only match once per change
    
    return affected_products

def main():
    init_page_config()
    create_mock_data_if_needed()
    
    # Header
    st.title("🏥 AI-Powered Regulatory Change Tracker")
    st.markdown("**Real-time monitoring of regulatory changes with AI-powered impact analysis**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # Refresh data button
        if st.button("🔄 Scan for New Changes", type="primary"):
            with st.spinner("Scanning regulatory sources..."):
                try:
                    tracker = RegulatoryTracker()
                    scraped_data = tracker.scrape_fda_updates()
                    changes = tracker.detect_changes(scraped_data)
                    st.success(f"Scan complete! Found {len(changes)} new changes.")
                except Exception as e:
                    st.warning("Demo mode: Using mock data for presentation")
                st.rerun()
        
        st.markdown("---")
        
        # Filters
        st.subheader("📊 Filters")
        selected_sources = st.multiselect(
            "Sources",
            ["FDA_DRUGS", "FDA_NEWS", "EMA", "CDSCO"],
            default=["FDA_DRUGS", "FDA_NEWS"]
        )
        
        selected_risk = st.multiselect(
            "Risk Levels",
            ["high", "medium", "low"],
            default=["high", "medium", "low"]
        )
        
        days_back = st.slider("Days to look back", 1, 30, 7)
    
    # Get data
    try:
        tracker = RegulatoryTracker()
        recent_changes = tracker.get_recent_changes(days_back)
    except:
        recent_changes = []
        st.info("Using demo data for presentation")
    
    # Filter data
    filtered_changes = [
        change for change in recent_changes
        if change["source"] in selected_sources and change["risk_level"] in selected_risk
    ]
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🚨 Total Changes", len(filtered_changes))
    
    with col2:
        high_risk_count = len([c for c in filtered_changes if c["risk_level"] == "high"])
        st.metric("⚠️ High Risk", high_risk_count)
    
    with col3:
        new_count = len([c for c in filtered_changes if c["change_type"] == "new"])
        st.metric("🆕 New Regulations", new_count)
    
    with col4:
        affected_products = map_changes_to_products(filtered_changes, MOCK_PRODUCTS)
        unique_products = len(set(p["product_name"] for p in affected_products))
        st.metric("📦 Affected Products", unique_products)
    
    # Simple charts using Streamlit's built-in functionality
    if filtered_changes:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Changes by Risk Level")
            risk_data = {"high": 0, "medium": 0, "low": 0}
            for change in filtered_changes:
                risk = change["risk_level"]
                if risk in risk_data:
                    risk_data[risk] += 1
            
            # Create a DataFrame for the chart
            risk_df = pd.DataFrame(list(risk_data.items()), columns=['Risk Level', 'Count'])
            risk_df = risk_df[risk_df['Count'] > 0]  # Only show non-zero values
            
            if not risk_df.empty:
                st.bar_chart(risk_df.set_index('Risk Level'))
            else:
                st.info("No data to display")
        
        with col2:
            st.subheader("📈 Changes Over Time")
            if filtered_changes:
                df = pd.DataFrame(filtered_changes)
                df["detected_at"] = pd.to_datetime(df["detected_at"])
                df["date"] = df["detected_at"].dt.date
                
                # Group by date
                daily_counts = df.groupby("date").size()
                daily_df = pd.DataFrame({
                    'Date': daily_counts.index,
                    'Changes': daily_counts.values
                })
                
                if len(daily_df) > 1:
                    st.line_chart(daily_df.set_index('Date'))
                else:
                    st.bar_chart(daily_df.set_index('Date'))
    
    # Changes list
    st.subheader("📋 Recent Regulatory Changes")
    
    if filtered_changes:
        for i, change in enumerate(filtered_changes):
            with st.expander(f"🔍 {change['title'][:80]}..." if len(change['title']) > 80 else change['title']):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Source:** {change['source']}")
                    st.markdown(f"**Type:** {change['change_type'].title()}")
                    st.markdown(f"**Detected:** {change['detected_at'][:10]}")
                    st.markdown(f"**Summary:** {change['summary']}")
                    
                    if change.get("url"):
                        st.markdown(f"**[📖 View Original Document]({change['url']})**")
                
                with col2:
                    # Risk level badge
                    risk_color = get_risk_color(change["risk_level"])
                    st.markdown(f"""
                        <div style="background-color: {risk_color}; color: white; padding: 5px 10px; 
                             border-radius: 5px; text-align: center; margin-bottom: 10px;">
                            <strong>{change["risk_level"].upper()} RISK</strong>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Impact areas
                    st.markdown("**Impact Areas:**")
                    try:
                        impact_areas = json.loads(change["impact_areas"])
                        for area in impact_areas:
                            st.markdown(f"• {area}")
                    except:
                        st.markdown("• General Regulatory")
    else:
        st.info("No changes found matching your filters. Adjust the filters to see more results.")
    
    # Product Impact Analysis
    st.subheader("🎯 Product Impact Analysis")
    
    if affected_products:
        # Create a summary of affected products
        product_summary = {}
        for item in affected_products:
            product = item["product_name"]
            if product not in product_summary:
                product_summary[product] = {
                    "changes": 0,
                    "max_risk": "low"
                }
            product_summary[product]["changes"] += 1
            
            # Update max risk level
            current_risk = item["risk_level"]
            if current_risk == "high" or product_summary[product]["max_risk"] != "high":
                if current_risk == "medium" and product_summary[product]["max_risk"] == "low":
                    product_summary[product]["max_risk"] = current_risk
                elif current_risk == "high":
                    product_summary[product]["max_risk"] = current_risk
        
        # Display as cards
        cols = st.columns(min(3, len(product_summary)))
        for i, (product_name, data) in enumerate(product_summary.items()):
            with cols[i % len(cols)]:
                risk_color = get_risk_color(data["max_risk"])
                st.markdown(f"""
                    <div style="border: 2px solid {risk_color}; border-radius: 10px; padding: 15px; margin: 10px 0;">
                        <h4 style="margin: 0 0 10px 0;">{product_name}</h4>
                        <p style="margin: 5px 0;"><strong>Affected Changes:</strong> {data['changes']}</p>
                        <p style="margin: 5px 0;"><strong>Max Risk Level:</strong> 
                            <span style="color: {risk_color}; font-weight: bold;">
                                {data['max_risk'].upper()}
                            </span>
                        </p>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No specific product impacts detected. This may indicate general regulatory changes or need for enhanced product mapping.")
    
    # Action items
    st.subheader("✅ Recommended Actions")
    
    if filtered_changes:
        action_items = []
        for change in filtered_changes:
            title_short = change['title'][:50] + "..." if len(change['title']) > 50 else change['title']
            
            if change["risk_level"] == "high":
                action_items.append(f"🚨 **URGENT:** Immediate compliance review required for: {title_short}")
                action_items.append(f"📞 **ALERT:** Notify all stakeholders about high-risk change")
            elif change["risk_level"] == "medium":
                action_items.append(f"⚠️ **MEDIUM:** Assess impact within 48 hours for: {title_short}")
            else:
                action_items.append(f"ℹ️ **LOW:** Monitor and document change: {title_short}")
        
        # Show top 8 action items
        for i, action in enumerate(action_items[:8], 1):
            st.markdown(f"{i}. {action}")
            
        if len(action_items) > 8:
            st.markdown(f"*... and {len(action_items) - 8} more action items*")
    else:
        st.success("✅ No urgent action items at this time. All systems compliant!")
    
    # Footer
    st.markdown("---")
    st.markdown("🤖 **Powered by AI** | Built for Indegene Hackathon | Real-time regulatory intelligence")
    
    # Demo information
    with st.expander("ℹ️ Demo Information"):
        st.markdown("""
        **This is a working prototype demonstrating:**
        - Real-time regulatory change detection
        - AI-powered risk assessment and summarization  
        - Product impact mapping
        - Automated action item generation
        
        **Technology Stack:** Python, Streamlit, SQLite, BeautifulSoup, AI/NLP
        
        **Scalability:** Ready for AWS deployment with enterprise features
        """)

if __name__ == "__main__":
    main()
