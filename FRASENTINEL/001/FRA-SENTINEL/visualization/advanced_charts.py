import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class AdvancedChartGenerator:
    def __init__(self):
        self.color_scheme = {
            'primary': '#2c5234',
            'secondary': '#4a7c59',
            'accent': '#7cb342',
            'farmland': '#ffeb3b',
            'forest': '#4caf50',
            'water': '#2196f3',
            'homestead': '#ff5722'
        }
    
    def create_3d_land_use_chart(self, classification_stats):
        """Create 3D visualization of land use"""
        categories = list(classification_stats.keys())
        percentages = [stats['percentage'] for stats in classification_stats.values()]
        areas = [stats.get('area_hectares', 0) for stats in classification_stats.values()]
        
        fig = go.Figure(data=[go.Scatter3d(
            x=categories,
            y=percentages,
            z=areas,
            mode='markers+text',
            marker=dict(
                size=[p/2 for p in percentages],
                color=[self.color_scheme.get(cat, '#gray') for cat in categories],
                opacity=0.8,
                line=dict(width=2, color='white')
            ),
            text=categories,
            textposition="middle center"
        )])
        
        fig.update_layout(
            title='3D Land Use Analysis',
            scene=dict(
                xaxis_title='Land Type',
                yaxis_title='Percentage',
                zaxis_title='Area (Hectares)'
            ),
            template='plotly_white'
        )
        
        return fig.to_json()
    
    def create_trend_analysis_chart(self):
        """Create trend analysis over time"""
        # Generate mock time series data
        dates = pd.date_range(start='2023-01-01', end='2024-08-31', freq='M')
        
        # Mock data for different metrics
        forest_cover = np.random.normal(42, 2, len(dates))
        water_availability = np.random.normal(8, 1, len(dates))
        agricultural_area = np.random.normal(35, 3, len(dates))
        
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Forest Cover %', 'Water Availability %', 'Agricultural Area %'),
            vertical_spacing=0.1
        )
        
        # Forest cover trend
        fig.add_trace(
            go.Scatter(
                x=dates, y=forest_cover,
                mode='lines+markers',
                name='Forest Cover',
                line=dict(color=self.color_scheme['forest'], width=3),
                fill='tonexty'
            ),
            row=1, col=1
        )
        
        # Water availability trend
        fig.add_trace(
            go.Scatter(
                x=dates, y=water_availability,
                mode='lines+markers',
                name='Water Availability',
                line=dict(color=self.color_scheme['water'], width=3),
                fill='tonexty'
            ),
            row=2, col=1
        )
        
        # Agricultural area trend
        fig.add_trace(
            go.Scatter(
                x=dates, y=agricultural_area,
                mode='lines+markers',
                name='Agricultural Area',
                line=dict(color=self.color_scheme['farmland'], width=3),
                fill='tonexty'
            ),
            row=3, col=1
        )
        
        fig.update_layout(
            title='Land Use Trends Over Time',
            template='plotly_white',
            height=800
        )
        
        return fig.to_json()
    
    def create_scheme_impact_chart(self):
        """Create scheme impact visualization"""
        schemes = ['PM-KISAN', 'Jal Shakti', 'MGNREGA', 'DAJGUA', 'Van Dhan Vikas']
        impact_before = [45, 25, 60, 20, 15]
        impact_after = [78, 55, 82, 45, 35]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Before Implementation',
            x=schemes,
            y=impact_before,
            marker_color='lightgray'
        ))
        
        fig.add_trace(go.Bar(
            name='After Implementation',
            x=schemes,
            y=impact_after,
            marker_color=self.color_scheme['primary']
        ))
        
        fig.update_layout(
            title='Scheme Impact Analysis',
            xaxis_title='Government Schemes',
            yaxis_title='Impact Score',
            barmode='group',
            template='plotly_white'
        )
        
        return fig.to_json()
    
    def create_village_comparison_radar(self, villages_data):
        """Create radar chart comparing villages"""
        categories = ['Forest Coverage', 'Water Availability', 'Agricultural Area', 
                     'Infrastructure', 'Scheme Coverage']
        
        fig = go.Figure()
        
        # Mock data for multiple villages
        villages = ['Khargone', 'Sendhwa', 'Maheshwar']
        colors = ['#2c5234', '#4a7c59', '#7cb342']
        
        for i, village in enumerate(villages):
            values = np.random.uniform(20, 90, len(categories))
            values = np.append(values, values[0])  # Complete the circle
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                fill='toself',
                name=village,
                line_color=colors[i]
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            title='Village Comparison Analysis',
            template='plotly_white'
        )
        
        return fig.to_json()
    
    def create_real_time_dashboard(self):
        """Create real-time metrics dashboard"""
        # Mock real-time data
        metrics = {
            'Active Claims': {'value': 1247, 'change': '+5.2%', 'trend': 'up'},
            'Approved This Month': {'value': 89, 'change': '+12.3%', 'trend': 'up'},
            'Scheme Coverage': {'value': 73.8, 'change': '+2.1%', 'trend': 'up'},
            'Data Accuracy': {'value': 94.2, 'change': '+0.8%', 'trend': 'up'}
        }
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=list(metrics.keys()),
            specs=[[{"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "indicator"}, {"type": "indicator"}]]
        )
        
        positions = [(1,1), (1,2), (2,1), (2,2)]
        colors = ['#2c5234', '#4a7c59', '#7cb342', '#66bb6a']
        
        for i, (metric, data) in enumerate(metrics.items()):
            row, col = positions[i]
            
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=data['value'],
                    delta={'reference': data['value'] * 0.95, 'relative': True},
                    title={"text": metric},
                    number={'font': {'color': colors[i]}},
                    domain={'row': row-1, 'column': col-1}
                ),
                row=row, col=col
            )
        
        fig.update_layout(
            title='Real-time Dashboard Metrics',
            template='plotly_white',
            height=600
        )
        
        return fig.to_json()

# Initialize chart generator
chart_generator = AdvancedChartGenerator()
