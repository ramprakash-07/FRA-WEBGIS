import json
import random
from datetime import datetime

class FRAChatbot:
    def __init__(self):
        self.responses = {
            'greeting': [
                "Hello! I'm your FRA Atlas assistant. How can I help you today?",
                "Welcome to FRA Atlas! I can help you with forest rights information, scheme recommendations, and data analysis.",
                "Hi there! I'm here to assist you with Forest Rights Act queries and village analysis."
            ],
            'fra_info': [
                "The Forest Rights Act (FRA) 2006 recognizes the rights of forest-dwelling communities over land and forest resources.",
                "FRA covers Individual Forest Rights (IFR), Community Rights (CR), and Community Forest Resource Rights (CFR).",
                "The Act aims to strengthen conservation while empowering forest communities with legal rights."
            ],
            'schemes': [
                "Current active schemes include PM-KISAN, Jal Shakti Mission, MGNREGA, DAJGUA, and Van Dhan Vikas.",
                "Scheme eligibility depends on land use patterns, forest coverage, and village characteristics.",
                "I can help you understand which schemes your village qualifies for based on our analysis."
            ],
            'data_query': [
                "Our system processes satellite imagery using AI to classify land use into farmland, forest, water bodies, and homesteads.",
                "We use Sentinel-2 satellite data with 10-meter resolution for accurate land use mapping.",
                "The classification accuracy of our AI model is 94.2% based on validation studies."
            ],
            'help': [
                "You can ask me about:\n• Forest Rights Act information\n• Government schemes\n• Village data analysis\n• Land use classification\n• Satellite imagery\n• Export options",
                "I can help you understand the dashboard, export reports, or explain our recommendations.",
                "Try asking: 'What schemes is my village eligible for?' or 'How accurate is the land classification?'"
            ]
        }
        
        self.context_keywords = {
            ('hello', 'hi', 'hey', 'greeting'): 'greeting',
            ('fra', 'forest rights act', 'rights', 'act'): 'fra_info',
            ('scheme', 'schemes', 'pm-kisan', 'mgnrega', 'jal shakti', 'dajgua'): 'schemes',
            ('data', 'satellite', 'imagery', 'classification', 'accuracy', 'ai'): 'data_query',
            ('help', 'assist', 'support', 'guide'): 'help'
        }
    
    def get_response(self, user_input):
        """Generate response based on user input"""
        user_input_lower = user_input.lower()
        
        # Determine context
        context = 'help'  # default
        for keywords, ctx in self.context_keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                context = ctx
                break
        
        # Get base response
        base_response = random.choice(self.responses[context])
        
        # Add personalized elements
        response = {
            'text': base_response,
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'suggestions': self.get_suggestions(context),
            'quick_actions': self.get_quick_actions(context)
        }
        
        return response
    
    def get_suggestions(self, context):
        """Get contextual suggestions"""
        suggestions = {
            'greeting': ["Show me village information", "What schemes are available?", "How does the AI work?"],
            'fra_info': ["Tell me about schemes", "Show land use data", "Export village report"],
            'schemes': ["Check eligibility", "View recommendations", "Download scheme details"],
            'data_query': ["Show classification results", "View satellite imagery", "Export analysis"],
            'help': ["Village analysis", "Scheme recommendations", "Export options"]
        }
        
        return suggestions.get(context, [])
    
    def get_quick_actions(self, context):
        """Get quick action buttons"""
        actions = {
            'greeting': [
                {'text': '📊 View Dashboard', 'action': 'show_dashboard'},
                {'text': '🗺️ Village Map', 'action': 'show_map'}
            ],
            'schemes': [
                {'text': '🎯 Check Eligibility', 'action': 'check_schemes'},
                {'text': '📄 Download Info', 'action': 'download_schemes'}
            ],
            'data_query': [
                {'text': '📈 View Stats', 'action': 'show_stats'},
                {'text': '🛰️ Satellite Data', 'action': 'show_satellite'}
            ]
        }
        
        return actions.get(context, [])

# Initialize chatbot
fra_chatbot = FRAChatbot()
