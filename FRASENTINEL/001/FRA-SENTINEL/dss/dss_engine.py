import json

class FRADecisionSupportSystem:
    """
    Decision Support System for Forest Rights Act implementation
    """
    
    def __init__(self):
        # Define scheme thresholds and criteria
        self.schemes = {
            'PM-KISAN': {
                'criteria': {
                    'min_farmland_percent': 20,
                    'min_area_hectares': 0.5,
                    'required_status': ['Approved', 'Verified']
                },
                'benefit': 'Rs. 6,000 annual direct benefit transfer',
                'ministry': 'Ministry of Agriculture'
            },
            'Jal Shakti Mission': {
                'criteria': {
                    'max_water_percent': 15,
                    'population_factor': True
                },
                'benefit': 'Water infrastructure development',
                'ministry': 'Ministry of Jal Shakti'
            },
            'MGNREGA': {
                'criteria': {
                    'min_rural_area': True,
                    'unemployment_indicator': True
                },
                'benefit': '100 days guaranteed employment',
                'ministry': 'Ministry of Rural Development'
            },
            'DAJGUA - Forest Enhancement': {
                'criteria': {
                    'min_forest_percent': 30,
                    'tribal_village': True
                },
                'benefit': 'Forest conservation and livelihood programs',
                'ministry': 'Ministry of Tribal Affairs'
            },
            'Van Dhan Vikas': {
                'criteria': {
                    'min_forest_percent': 25,
                    'tribal_population': True
                },
                'benefit': 'Forest produce value addition',
                'ministry': 'Ministry of Tribal Affairs'
            }
        }
    
    def evaluate_village(self, village_data, land_use_stats):
        """
        Evaluate a village for various scheme eligibilities
        """
        recommendations = []
        
        # Extract key parameters
        farmland_percent = land_use_stats.get('farmland', {}).get('percentage', 0)
        forest_percent = land_use_stats.get('forest', {}).get('percentage', 0)
        water_percent = land_use_stats.get('water', {}).get('percentage', 0)
        area_hectares = village_data.get('area_hectares', 0)
        claim_status = village_data.get('claim_status', 'Pending')
        
        # Evaluate each scheme
        for scheme_name, scheme_info in self.schemes.items():
            criteria = scheme_info['criteria']
            eligible = True
            priority = 'Medium'
            reasons = []
            
            if scheme_name == 'PM-KISAN':
                if farmland_percent < criteria['min_farmland_percent']:
                    eligible = False
                else:
                    reasons.append(f"Sufficient agricultural area ({farmland_percent:.1f}%)")
                    if farmland_percent > 40:
                        priority = 'High'
                
                if area_hectares < criteria['min_area_hectares']:
                    eligible = False
                    reasons.append(f"Land area below minimum ({area_hectares} ha)")
                
                if claim_status not in criteria['required_status']:
                    eligible = False
                    reasons.append(f"Claim status: {claim_status}")
            
            elif scheme_name == 'Jal Shakti Mission':
                if water_percent > criteria['max_water_percent']:
                    eligible = False
                else:
                    reasons.append(f"Low water coverage ({water_percent:.1f}%)")
                    if water_percent < 5:
                        priority = 'High'
                    elif water_percent < 10:
                        priority = 'Medium'
                    else:
                        priority = 'Low'
            
            elif scheme_name == 'MGNREGA':
                # Always eligible for rural areas with approved FRA
                if claim_status in ['Approved', 'Verified']:
                    reasons.append("Rural employment opportunities available")
                    if farmland_percent > 30:
                        priority = 'High'
                        reasons.append("High agricultural activity indicates employment needs")
                else:
                    eligible = False
            
            elif scheme_name == 'DAJGUA - Forest Enhancement':
                if forest_percent < criteria['min_forest_percent']:
                    eligible = False
                else:
                    reasons.append(f"Significant forest cover ({forest_percent:.1f}%)")
                    if forest_percent > 50:
                        priority = 'High'
            
            elif scheme_name == 'Van Dhan Vikas':
                if forest_percent < criteria['min_forest_percent']:
                    eligible = False
                else:
                    reasons.append(f"Forest resources available ({forest_percent:.1f}%)")
                    if forest_percent > 40:
                        priority = 'High'
            
            if eligible:
                recommendations.append({
                    'scheme': scheme_name,
                    'priority': priority,
                    'reasons': reasons,
                    'benefit': scheme_info['benefit'],
                    'ministry': scheme_info['ministry'],
                    'eligibility_score': self._calculate_score(scheme_name, village_data, land_use_stats)
                })
        
        # Sort by priority and eligibility score
        priority_order = {'High': 3, 'Medium': 2, 'Low': 1}
        recommendations.sort(key=lambda x: (priority_order[x['priority']], x['eligibility_score']), reverse=True)
        
        return recommendations
    
    def _calculate_score(self, scheme_name, village_data, land_use_stats):
        """Calculate eligibility score for prioritization"""
        score = 0
        
        farmland_percent = land_use_stats.get('farmland', {}).get('percentage', 0)
        forest_percent = land_use_stats.get('forest', {}).get('percentage', 0)
        water_percent = land_use_stats.get('water', {}).get('percentage', 0)
        
        if scheme_name == 'PM-KISAN':
            score = farmland_percent * 2
        elif scheme_name == 'Jal Shakti Mission':
            score = (20 - water_percent) * 3  # Higher score for less water
        elif scheme_name == 'MGNREGA':
            score = (farmland_percent + forest_percent) * 1.5
        elif 'Forest' in scheme_name or 'Van Dhan' in scheme_name:
            score = forest_percent * 2.5
        
        return min(score, 100)  # Cap at 100
    
    def generate_village_report(self, village_data, land_use_stats):
        """Generate comprehensive report for a village"""
        recommendations = self.evaluate_village(village_data, land_use_stats)
        
        report = {
            'village_info': village_data,
            'land_use_analysis': land_use_stats,
            'recommendations': recommendations,
            'summary': {
                'total_schemes': len(recommendations),
                'high_priority': len([r for r in recommendations if r['priority'] == 'High']),
                'potential_benefits': [r['benefit'] for r in recommendations]
            }
        }
        
        return report

def test_dss():
    """Test the DSS with sample data"""
    dss = FRADecisionSupportSystem()
    
    # Sample village data
    village_data = {
        'village': 'Khargone',
        'patta_holder': 'Ram Singh',
        'area_hectares': 2.5,
        'claim_status': 'Approved',
        'latitude': 21.8225,
        'longitude': 75.6102
    }
    
    # Sample land use statistics
    land_use_stats = {
        'farmland': {'percentage': 35.0, 'pixels': 3500},
        'forest': {'percentage': 40.0, 'pixels': 4000},
        'water': {'percentage': 8.0, 'pixels': 800},
        'homestead': {'percentage': 17.0, 'pixels': 1700}
    }
    
    # Generate recommendations
    report = dss.generate_village_report(village_data, land_use_stats)
    
    print("=== FRA Decision Support System Report ===")
    print(f"Village: {report['village_info']['village']}")
    print(f"Patta Holder: {report['village_info']['patta_holder']}")
    print(f"Total Schemes Eligible: {report['summary']['total_schemes']}")
    print(f"High Priority Schemes: {report['summary']['high_priority']}")
    
    print("\n=== Land Use Analysis ===")
    for land_type, stats in report['land_use_analysis'].items():
        print(f"{land_type.capitalize()}: {stats['percentage']}%")
    
    print("\n=== Scheme Recommendations ===")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"{i}. {rec['scheme']} ({rec['priority']} Priority)")
        print(f"   Ministry: {rec['ministry']}")
        print(f"   Benefit: {rec['benefit']}")
        print(f"   Reasons: {', '.join(rec['reasons'])}")
        print(f"   Score: {rec['eligibility_score']:.1f}/100")
        print()
    
    return report

if __name__ == "__main__":
    test_dss()
