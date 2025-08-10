"""
AI Enhancement Module using Free Hugging Face Models
This adds intelligent summarization and impact analysis without paid APIs
"""

import os
import warnings
warnings.filterwarnings('ignore')

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    from transformers import T5ForConditionalGeneration, T5Tokenizer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️  Transformers not available. Install with: pip install transformers torch")

class AIEnhancer:
    def __init__(self):
        self.summarizer = None
        self.classifier = None
        self.sentiment_analyzer = None
        
        if TRANSFORMERS_AVAILABLE:
            self._load_models()
    
    def _load_models(self):
        """Load free models from Hugging Face"""
        try:
            print("🤖 Loading AI models...")
            
            # Summarization model (lightweight)
            self.summarizer = pipeline(
                "summarization",
                model="sshleifer/distilbart-cnn-6-6",
                max_length=150,
                min_length=30,
                device=-1  # CPU only for free version
            )
            
            # Text classification for impact analysis
            self.classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",  # Alternative: "distilbert-base-uncased"
                device=-1
            )
            
            # Sentiment/urgency analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=-1
            )
            
            print("✅ AI models loaded successfully!")
            
        except Exception as e:
            print(f"⚠️  Could not load AI models: {e}")
            print("💡 Using fallback rule-based analysis")
    
    def generate_smart_summary(self, content: str) -> str:
        """Generate intelligent summary using AI"""
        if not self.summarizer or len(content) < 100:
            return self._fallback_summary(content)
        
        try:
            # Clean and prepare text
            clean_content = self._clean_text(content)
            if len(clean_content) < 100:
                return clean_content
            
            # Use AI summarizer
            summary = self.summarizer(
                clean_content[:1024],  # Limit input length
                max_length=100,
                min_length=25,
                do_sample=False
            )
            
            return summary[0]['summary_text']
            
        except Exception as e:
            print(f"AI summarization failed: {e}")
            return self._fallback_summary(content)
    
    def analyze_impact_areas(self, content: str) -> list:
        """AI-powered impact area detection"""
        if not TRANSFORMERS_AVAILABLE:
            return self._rule_based_impact_analysis(content)
        
        try:
            # Define impact categories with keywords
            impact_categories = {
                'Clinical Trials': [
                    'clinical trial', 'study protocol', 'patient enrollment',
                    'biomarker', 'endpoint', 'statistical analysis'
                ],
                'Manufacturing': [
                    'quality control', 'manufacturing', 'facility inspection',
                    'GMP', 'batch records', 'sterile production'
                ],
                'Labeling': [
                    'labeling', 'package insert', 'prescribing information',
                    'contraindication', 'warning', 'dosage'
                ],
                'Pharmacovigilance': [
                    'adverse event', 'safety monitoring', 'REMS',
                    'post-marketing', 'surveillance', 'risk evaluation'
                ],
                'Marketing': [
                    'promotional', 'advertising', 'marketing materials',
                    'commercial', 'launch', 'sales'
                ],
                'Regulatory Affairs': [
                    'submission', 'filing', 'regulatory pathway',
                    'approval', 'guidance', 'compliance'
                ]
            }
            
            content_lower = content.lower()
            detected_areas = []
            
            # Score each category
            for category, keywords in impact_categories.items():
                score = sum(1 for keyword in keywords if keyword in content_lower)
                if score >= 2:  # Threshold for relevance
                    detected_areas.append(category)
            
            return detected_areas if detected_areas else ['General Regulatory']
            
        except Exception as e:
            return self._rule_based_impact_analysis(content)
    
    def assess_urgency_level(self, title: str, content: str) -> dict:
        """AI-powered urgency assessment"""
        text = f"{title} {content}"
        
        try:
            if self.sentiment_analyzer:
                # Analyze sentiment/urgency
                result = self.sentiment_analyzer(text[:512])
                sentiment_score = result[0]['score']
                
                # Custom urgency keywords
                urgent_keywords = [
                    'immediate', 'urgent', 'critical', 'emergency',
                    'recall', 'warning', 'death', 'serious adverse'
                ]
                
                high_priority_keywords = [
                    'safety', 'black box', 'contraindication',
                    'withdrawal', 'suspension', 'investigation'
                ]
                
                text_lower = text.lower()
                
                # Calculate urgency score
                urgent_score = sum(1 for keyword in urgent_keywords if keyword in text_lower)
                priority_score = sum(1 for keyword in high_priority_keywords if keyword in text_lower)
                
                if urgent_score > 0 or sentiment_score < 0.3:
                    risk_level = 'high'
                elif priority_score > 0 or sentiment_score < 0.6:
                    risk_level = 'medium'
                else:
                    risk_level = 'low'
                
                return {
                    'risk_level': risk_level,
                    'confidence': sentiment_score,
                    'reasoning': f"Detected {urgent_score} urgent + {priority_score} high-priority indicators"
                }
        
        except Exception as e:
            pass
        
        # Fallback to rule-based
        return self._rule_based_risk_assessment(text)
    
    def generate_action_items(self, change_data: dict) -> list:
        """Generate specific action items based on change analysis"""
        actions = []
        
        risk_level = change_data.get('risk_level', 'medium')
        impact_areas = change_data.get('impact_areas', [])
        title = change_data.get('title', '')
        
        # Risk-based actions
        if risk_level == 'high':
            actions.append("🚨 IMMEDIATE: Convene emergency compliance review within 24 hours")
            actions.append("📞 URGENT: Notify all stakeholders and halt affected processes if necessary")
        
        # Area-specific actions
        for area in impact_areas:
            if area == 'Labeling':
                actions.append("📋 Review and update all product labeling materials")
                actions.append("🔍 Audit current package inserts for compliance gaps")
            
            elif area == 'Clinical Trials':
                actions.append("🧪 Assess impact on ongoing clinical studies")
                actions.append("📊 Update study protocols if required")
            
            elif area == 'Manufacturing':
                actions.append("🏭 Inspect manufacturing processes for compliance")
                actions.append("📝 Update quality control procedures")
            
            elif area == 'Pharmacovigilance':
                actions.append("🔒 Review safety monitoring procedures")
                actions.append("📈 Update risk evaluation protocols")
            
            elif area == 'Marketing':
                actions.append("📢 Review all promotional materials for compliance")
                actions.append("🎯 Update marketing approval processes")
        
        # General actions
        actions.append("📄 Document compliance assessment in regulatory files")
        actions.append("⏰ Set timeline for implementation based on regulatory deadlines")
        
        return actions[:6]  # Limit to top 6 actions
    
    def _clean_text(self, text: str) -> str:
        """Clean text for processing"""
        import re
        # Remove extra whitespace and special characters
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\.\,\;\:\!\?]', '', text)
        return text.strip()
    
    def _fallback_summary(self, content: str) -> str:
        """Rule-based summary when AI is not available"""
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 10]
        if len(sentences) <= 2:
            return content[:200] + "..." if len(content) > 200 else content
        
        # Take first 2 most relevant sentences
        summary_sentences = sentences[:2]
        summary = '. '.join(summary_sentences) + '.'
        
        return summary[:250] + "..." if len(summary) > 250 else summary
    
    def _rule_based_impact_analysis(self, content: str) -> list:
        """Fallback rule-based impact analysis"""
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
    
    def _rule_based_risk_assessment(self, text: str) -> dict:
        """Fallback rule-based risk assessment"""
        high_risk_keywords = [
            'recall', 'warning', 'safety', 'death', 'serious', 'urgent',
            'immediate', 'black box', 'contraindication', 'withdrawal'
        ]
        
        medium_risk_keywords = [
            'labeling', 'indication', 'dosage', 'administration', 'clinical',
            'trial', 'study', 'efficacy', 'approval', 'guidance'
        ]
        
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in high_risk_keywords):
            return {'risk_level': 'high', 'confidence': 0.8, 'reasoning': 'High-risk keywords detected'}
        elif any(keyword in text_lower for keyword in medium_risk_keywords):
            return {'risk_level': 'medium', 'confidence': 0.7, 'reasoning': 'Medium-risk keywords detected'}
        else:
            return {'risk_level': 'low', 'confidence': 0.6, 'reasoning': 'No high-risk indicators found'}

# Enhanced Regulatory Tracker with AI
class AIEnhancedTracker:
    def __init__(self, db_path="regulatory_tracker.db"):
        from reg_scraper import RegulatoryTracker
        self.tracker = RegulatoryTracker(db_path)
        self.ai_enhancer = AIEnhancer()
    
    def process_changes_with_ai(self, scraped_data: list) -> list:
        """Process changes with AI enhancement"""
        enhanced_changes = []
        
        for item in scraped_data:
            # Generate AI summary
            ai_summary = self.ai_enhancer.generate_smart_summary(item['content'])
            
            # Analyze impact areas
            impact_areas = self.ai_enhancer.analyze_impact_areas(item['content'])
            
            # Assess urgency
            urgency_analysis = self.ai_enhancer.assess_urgency_level(item['title'], item['content'])
            
            # Create enhanced change object
            enhanced_change = {
                'source': item['source'],
                'title': item['title'],
                'url': item['url'],
                'content': item['content'],
                'ai_summary': ai_summary,
                'impact_areas': impact_areas,
                'risk_level': urgency_analysis['risk_level'],
                'confidence': urgency_analysis.get('confidence', 0.5),
                'reasoning': urgency_analysis.get('reasoning', ''),
                'detected_at': datetime.now().isoformat()
            }
            
            # Generate action items
            enhanced_change['action_items'] = self.ai_enhancer.generate_action_items(enhanced_change)
            
            enhanced_changes.append(enhanced_change)
        
        return enhanced_changes

# Usage example
if __name__ == "__main__":
    print("🤖 Testing AI Enhanced Regulatory Tracker")
    
    # Test AI enhancer
    enhancer = AIEnhancer()
    
    sample_text = """
    FDA announces new safety labeling requirements for all cardiovascular medications. 
    This update requires immediate implementation of black box warnings and updated 
    contraindications for patients with severe heart conditions.
    """
    
    print("\n📝 AI Summary:")
    summary = enhancer.generate_smart_summary(sample_text)
    print(summary)
    
    print("\n🎯 Impact Areas:")
    areas = enhancer.analyze_impact_areas(sample_text)
    print(areas)
    
    print("\n⚠️ Risk Assessment:")
    risk = enhancer.assess_urgency_level("FDA Safety Update", sample_text)
    print(f"Risk: {risk['risk_level']} (Confidence: {risk['confidence']:.2f})")
    
    print("\n✅ Action Items:")
    actions = enhancer.generate_action_items({
        'title': 'FDA Safety Update',
        'risk_level': risk['risk_level'],
        'impact_areas': areas
    })
    for i, action in enumerate(actions, 1):
        print(f"{i}. {action}")
