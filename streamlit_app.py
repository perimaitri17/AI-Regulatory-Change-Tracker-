import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
        "Cardiovascular": ["CardioMax"],
        "CNS": ["NeuroFlex"],
        "Endocrine": ["DiabetesAid"],
        "Oncology": ["OncoCure"],
        "Immunology": ["ImmunePlus"]
    }
    
    affected_products = []
    
    for change in changes:
        change_text = change["title"].lower() + " " + change["summary"].lower()
        
        for category, product_names in impact_mapping.items():
            if any(cat_word in change_text for cat_word in [category.lower(), "cardio", "neuro", "diabetes", "oncology", "immuno"]):
                for product_name in product_names:
                    affected_products.append({
                        "change_id": change["id"],
                        "product_name": product_name,
                        "change_title": change["title"],
                        "risk_level": change["risk_level"],
                        "impact_areas": json.loads(change["impact_areas"])
                    })
    
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
                tracker = RegulatoryTracker()
                scraped_data = tracker.scrape_fda_updates()
                changes = tracker.detect_changes(scraped_data)
                st.success(f"Scan complete! Found {len(changes)} new changes.")
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
    tracker = RegulatoryTracker()
    recent_changes = tracker.get_recent_changes(days_back)
    
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
        st.metric("📦 Affected Products", len(set(p["product_name"] for p in affected_products)))
    
    # Charts
    if filtered_changes:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Changes by Risk Level")
            risk_counts = pd.DataFrame(filtered_changes)["risk_level"].value_counts()
            fig = px.pie(
                values=risk_counts.values, 
                names=risk_counts.index,
                color=risk_counts.index,
                color_discrete_map={"high": "#FF4B4B", "medium": "#FFA500", "low": "#28A745"}
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📈 Changes Over Time")
            df = pd.DataFrame(filtered_changes)
            df["detected_at"] = pd.to_datetime(df["detected_at"])
            df["date"] = df["detected_at"].dt.date
            
            daily_counts = df.groupby(["date", "risk_level"]).size().unstack(fill_value=0)
            
            fig = go.Figure()
            for risk_level in ["high", "medium", "low"]:
                if risk_level in daily_counts.columns:
                    fig.add_trace(go.Scatter(
                        x=daily_counts.index,
                        y=daily_counts[risk_level],
                        mode='lines+markers',
                        name=f"{risk_level.title()} Risk",
                        line=dict(color=get_risk_color(risk_level))
                    ))
            
            fig.update_layout(title="Daily Changes by Risk Level", xaxis_title="Date", yaxis_title="Number of Changes")
            st.plotly_chart(fig, use_container_width=True)
    
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
                    
                    if change["url"]:
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
                    impact_areas = json.loads(change["impact_areas"])
                    for area in impact_areas:
                        st.markdown(f"• {area}")
    
    # Product Impact Analysis
    st.subheader("🎯 Product Impact Analysis")
    
    if affected_products:
        impact_df = pd.DataFrame(affected_products)
        
        # Group by product
        product_impacts = impact_df.groupby("product_name").agg({
            "change_title": "count",
            "risk_level": lambda x: "high" if "high" in x.values else ("medium" if "medium" in x.values else "low")
        }).rename(columns={"change_title": "affected_changes"})
        
        # Display as cards
        cols = st.columns(3)
        for i, (product_name, data) in enumerate(product_impacts.iterrows()):
            with cols[i % 3]:
                risk_color = get_risk_color(data["risk_level"])
                st.markdown(f"""
                    <div style="border: 2px solid {risk_color}; border-radius: 10px; padding: 15px; margin: 10px 0;">
                        <h4>{product_name}</h4>
                        <p><strong>Affected Changes:</strong> {data['affected_changes']}</p>
                        <p><strong>Max Risk Level:</strong> 
                            <span style="color: {risk_color}; font-weight: bold;">
                                {data['risk_level'].upper()}
                            </span>
                        </p>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No product impacts detected in current changes.")
    
    # Action items
    st.subheader("✅ Recommended Actions")
    
    if filtered_changes:
        action_items = []
        for change in filtered_changes:
            if change["risk_level"] == "high":
                action_items.append(f"🚨 **URGENT:** Review and update documentation for: {change['title']}")
            elif change["risk_level"] == "medium":
                action_items.append(f"⚠️ **MEDIUM:** Assess impact on current processes: {change['title']}")
            else:
                action_items.append(f"ℹ️ **LOW:** Monitor for future implications: {change['title']}")
        
        for i, action in enumerate(action_items[:5], 1):
            st.markdown(f"{i}. {action}")
    else:
        st.info("No action items at this time. All systems up to date! ✅")
    
    # Footer
    st.markdown("---")
    st.markdown("🤖 **Powered by AI** | Built for Indegene Hackathon | Real-time regulatory intelligence")

if __name__ == "__main__":
    main()
