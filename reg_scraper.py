import requests
from bs4 import BeautifulSoup
import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
import difflib
import re
from dataclasses import dataclass
from typing import List, Dict, Optional
import time

@dataclass
class RegulatoryChange:
    source: str
    title: str
    url: str
    content: str
    change_type: str  # 'new', 'updated', 'removed'
    risk_level: str  # 'low', 'medium', 'high'
    detected_at: str
    summary: str = ""
    impact_areas: List[str] = None

class RegulatoryTracker:
    def __init__(self, db_path="regulatory_tracker.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regulatory_documents (
                id INTEGER PRIMARY KEY,
                source TEXT,
                title TEXT,
                url TEXT UNIQUE,
                content_hash TEXT,
                content TEXT,
                last_updated TEXT,
                created_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detected_changes (
                id INTEGER PRIMARY KEY,
                source TEXT,
                title TEXT,
                url TEXT,
                change_type TEXT,
                risk_level TEXT,
                summary TEXT,
                impact_areas TEXT,
                detected_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def scrape_fda_updates(self) -> List[Dict]:
        """Scrape FDA drug updates (free RSS/web scraping)"""
        sources = [
            {
                'name': 'FDA_DRUGS',
                'url': 'https://www.fda.gov/drugs/drug-safety-and-availability/drug-recalls',
                'type': 'html'
            },
            {
                'name': 'FDA_NEWS',
                'url': 'https://www.fda.gov/news-events/fda-newsroom/press-announcements',
                'type': 'html'
            }
        ]
        
        scraped_data = []
        
        for source in sources:
            try:
                print(f"Scraping {source['name']}...")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(source['url'], headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract articles/updates (adjust selectors based on actual HTML)
                articles = soup.find_all(['article', 'div'], class_=re.compile(r'.*news.*|.*update.*|.*announcement.*'))[:10]
                
                for article in articles:
                    title_elem = article.find(['h1', 'h2', 'h3', 'h4', 'a'])
                    if title_elem:
                        title = title_elem.get_text().strip()
                        link_elem = article.find('a')
                        url = link_elem.get('href') if link_elem else source['url']
                        
                        # Make URL absolute
                        if url.startswith('/'):
                            url = 'https://www.fda.gov' + url
                        
                        content = article.get_text().strip()[:1000]  # First 1000 chars
                        
                        scraped_data.append({
                            'source': source['name'],
                            'title': title,
                            'url': url,
                            'content': content
                        })
                        
                time.sleep(1)  # Be respectful to servers
                
            except Exception as e:
                print(f"Error scraping {source['name']}: {e}")
                
        return scraped_data
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate hash of content for change detection"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def detect_changes(self, scraped_data: List[Dict]) -> List[RegulatoryChange]:
        """Detect changes by comparing with stored data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        detected_changes = []
        
        for item in scraped_data:
            content_hash = self.calculate_content_hash(item['content'])
            
            # Check if document exists
            cursor.execute(
                "SELECT content_hash, content FROM regulatory_documents WHERE url = ?",
                (item['url'],)
            )
            result = cursor.fetchone()
            
            if result is None:
                # New document
                change = RegulatoryChange(
                    source=item['source'],
                    title=item['title'],
                    url=item['url'],
                    content=item['content'],
                    change_type='new',
                    risk_level=self.assess_risk_level(item['title'], item['content']),
                    detected_at=datetime.now().isoformat(),
                    summary=self.generate_basic_summary(item['content']),
                    impact_areas=self.identify_impact_areas(item['content'])
                )
                detected_changes.append(change)
                
                # Store new document
                cursor.execute('''
                    INSERT INTO regulatory_documents 
                    (source, title, url, content_hash, content, last_updated, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item['source'], item['title'], item['url'], content_hash, 
                    item['content'], datetime.now().isoformat(), datetime.now().isoformat()
                ))
                
            elif result[0] != content_hash:
                # Document updated
                old_content = result[1]
                diff = self.generate_diff(old_content, item['content'])
                
                change = RegulatoryChange(
                    source=item['source'],
                    title=item['title'],
                    url=item['url'],
                    content=diff,
                    change_type='updated',
                    risk_level=self.assess_risk_level(item['title'], diff),
                    detected_at=datetime.now().isoformat(),
                    summary=self.generate_basic_summary(diff),
                    impact_areas=self.identify_impact_areas(diff)
                )
                detected_changes.append(change)
                
                # Update document
                cursor.execute('''
                    UPDATE regulatory_documents 
                    SET content_hash = ?, content = ?, last_updated = ?
                    WHERE url = ?
                ''', (content_hash, item['content'], datetime.now().isoformat(), item['url']))
        
        # Store detected changes
        for change in detected_changes:
            cursor.execute('''
                INSERT INTO detected_changes 
                (source, title, url, change_type, risk_level, summary, impact_areas, detected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                change.source, change.title, change.url, change.change_type,
                change.risk_level, change.summary, json.dumps(change.impact_areas), 
                change.detected_at
            ))
        
        conn.commit()
        conn.close()
        
        return detected_changes
    
    def generate_diff(self, old_content: str, new_content: str) -> str:
        """Generate human-readable diff"""
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        
        diff = list(difflib.unified_diff(old_lines, new_lines, lineterm='', n=3))
        return '\n'.join(diff)
    
    def assess_risk_level(self, title: str, content: str) -> str:
        """Assess risk level based on keywords"""
        high_risk_keywords = [
            'recall', 'warning', 'safety', 'death', 'serious', 'urgent',
            'immediate', 'black box', 'contraindication', 'withdrawal'
        ]
        
        medium_risk_keywords = [
            'labeling', 'indication', 'dosage', 'administration', 'clinical',
            'trial', 'study', 'efficacy', 'approval', 'guidance'
        ]
        
        text = (title + ' ' + content).lower()
        
        if any(keyword in text for keyword in high_risk_keywords):
            return 'high'
        elif any(keyword in text for keyword in medium_risk_keywords):
            return 'medium'
        else:
            return 'low'
    
    def identify_impact_areas(self, content: str) -> List[str]:
        """Identify which areas are impacted"""
        areas = {
            'Clinical Trials': ['clinical', 'trial', 'study', 'protocol'],
            'Labeling': ['label', 'labeling', 'package insert', 'prescribing'],
            'Manufacturing': ['manufacturing', 'quality', 'facility', 'inspection'],
            'Pharmacovigilance': ['safety', 'adverse', 'reaction', 'monitoring'],
            'Marketing': ['promotion', 'advertising', 'marketing', 'commercial'],
            'Regulatory Affairs': ['submission', 'filing', 'application', 'review']
        }
        
        content_lower = content.lower()
        impacted_areas = []
        
        for area, keywords in areas.items():
            if any(keyword in content_lower for keyword in keywords):
                impacted_areas.append(area)
        
        return impacted_areas if impacted_areas else ['General']
    
    def generate_basic_summary(self, content: str) -> str:
        """Generate basic summary without AI (for free version)"""
        sentences = content.split('.')[:3]  # First 3 sentences
        summary = '. '.join(s.strip() for s in sentences if s.strip())
        return summary[:200] + "..." if len(summary) > 200 else summary
    
    def get_recent_changes(self, days: int = 7) -> List[Dict]:
        """Get recent changes from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT * FROM detected_changes 
            WHERE detected_at > ? 
            ORDER BY detected_at DESC
        ''', (cutoff_date,))
        
        columns = ['id', 'source', 'title', 'url', 'change_type', 'risk_level', 
                  'summary', 'impact_areas', 'detected_at']
        
        changes = []
        for row in cursor.fetchall():
            change_dict = dict(zip(columns, row))
            change_dict['impact_areas'] = json.loads(change_dict['impact_areas'])
            changes.append(change_dict)
        
        conn.close()
        return changes

# Example usage and demo
if __name__ == "__main__":
    tracker = RegulatoryTracker()
    
    print("🔍 Scraping regulatory sources...")
    scraped_data = tracker.scrape_fda_updates()
    print(f"Found {len(scraped_data)} documents")
    
    print("📊 Detecting changes...")
    changes = tracker.detect_changes(scraped_data)
    print(f"Detected {len(changes)} changes")
    
    print("\n📋 Recent Changes Summary:")
    recent_changes = tracker.get_recent_changes(30)
    for i, change in enumerate(recent_changes[:5], 1):
        print(f"\n{i}. {change['title'][:60]}...")
        print(f"   Source: {change['source']} | Type: {change['change_type']} | Risk: {change['risk_level']}")
        print(f"   Impact: {', '.join(change['impact_areas'])}")
        print(f"   Summary: {change['summary'][:100]}...")
