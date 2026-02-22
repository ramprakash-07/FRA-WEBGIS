"""
FRA Household Eligibility Assessment Engine
Combines household data with patta details to suggest eligible government schemes
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class EligibilityEngine:
    """Engine to assess FRA household eligibility for government schemes"""
    
    def __init__(self):
        self.schemes_database = self._load_schemes_database()
        self.eligibility_rules = self._load_eligibility_rules()
    
    def _load_schemes_database(self) -> Dict[str, Any]:
        """Load government schemes database"""
        return {
            "agricultural_schemes": {
                "PM_KISAN": {
                    "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
                    "description": "Direct income support of Rs. 6,000 per year to small and marginal farmers",
                    "benefit_amount": "Rs. 6,000 per year",
                    "ministry": "Ministry of Agriculture & Farmers Welfare",
                    "website": "https://pmkisan.gov.in",
                    "eligibility_criteria": {
                        "land_ownership": True,
                        "cultivates_crops": True,
                        "social_category": ["General", "SC", "ST", "OBC"],
                        "min_land_area": 0.01,  # hectares
                        "max_land_area": 2.0,   # hectares
                        "exclusions": ["Government employees", "Income tax payers"]
                    }
                },
                "PMFBY": {
                    "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
                    "description": "Crop insurance scheme for farmers",
                    "benefit_amount": "Up to 100% of sum insured",
                    "ministry": "Ministry of Agriculture & Farmers Welfare",
                    "website": "https://pmfby.gov.in",
                    "eligibility_criteria": {
                        "cultivates_crops": True,
                        "land_ownership": True,
                        "bank_account": True
                    }
                }
            },
            "housing_schemes": {
                "PMAY": {
                    "name": "Pradhan Mantri Awas Yojana (PMAY)",
                    "description": "Housing for all by 2022",
                    "benefit_amount": "Rs. 1.5-2.5 lakhs",
                    "ministry": "Ministry of Housing and Urban Affairs",
                    "website": "https://pmaymis.gov.in",
                    "eligibility_criteria": {
                        "bpl_status": True,
                        "owns_house": False,
                        "house_type": ["Kutcha", "Homeless"],
                        "social_category": ["SC", "ST", "OBC"],
                        "bank_account": True
                    }
                }
            },
            "employment_schemes": {
                "MGNREGA": {
                    "name": "Mahatma Gandhi National Rural Employment Guarantee Act",
                    "description": "100 days of guaranteed wage employment",
                    "benefit_amount": "Rs. 200-300 per day",
                    "ministry": "Ministry of Rural Development",
                    "website": "https://nrega.nic.in",
                    "eligibility_criteria": {
                        "willing_mgnrega": True,
                        "adults_count": 1,
                        "bank_account": True,
                        "ration_card": True
                    }
                }
            },
            "forest_rights_schemes": {
                "FRA_TITLE": {
                    "name": "Forest Rights Act - Individual Forest Rights",
                    "description": "Recognition of individual forest rights",
                    "benefit_amount": "Land title up to 4 hectares",
                    "ministry": "Ministry of Tribal Affairs",
                    "website": "https://tribal.nic.in",
                    "eligibility_criteria": {
                        "tribal_district": True,
                        "collects_forest_produce": True,
                        "social_category": ["ST"],
                        "land_ownership": False
                    }
                },
                "FRA_COMMUNITY": {
                    "name": "Forest Rights Act - Community Forest Rights",
                    "description": "Recognition of community forest rights",
                    "benefit_amount": "Community forest management rights",
                    "ministry": "Ministry of Tribal Affairs",
                    "website": "https://tribal.nic.in",
                    "eligibility_criteria": {
                        "tribal_district": True,
                        "collects_forest_produce": True,
                        "social_category": ["ST"]
                    }
                }
            },
            "social_welfare_schemes": {
                "PMJAY": {
                    "name": "Pradhan Mantri Jan Arogya Yojana (PMJAY)",
                    "description": "Health insurance for poor and vulnerable families",
                    "benefit_amount": "Up to Rs. 5 lakhs per family per year",
                    "ministry": "Ministry of Health and Family Welfare",
                    "website": "https://pmjay.gov.in",
                    "eligibility_criteria": {
                        "bpl_status": True,
                        "social_category": ["SC", "ST", "OBC"],
                        "total_family_members": 1
                    }
                },
                "PMUY": {
                    "name": "Pradhan Mantri Ujjwala Yojana (PMUY)",
                    "description": "Free LPG connections to poor households",
                    "benefit_amount": "Free LPG connection + Rs. 1,600 subsidy",
                    "ministry": "Ministry of Petroleum and Natural Gas",
                    "website": "https://pmuy.gov.in",
                    "eligibility_criteria": {
                        "bpl_status": True,
                        "clean_fuel": False,
                        "social_category": ["SC", "ST", "OBC"]
                    }
                }
            },
            "infrastructure_schemes": {
                "JAL_JEEVAN": {
                    "name": "Jal Jeevan Mission",
                    "description": "Tap water connection to every household",
                    "benefit_amount": "Free tap water connection",
                    "ministry": "Ministry of Jal Shakti",
                    "website": "https://jaljeevanmission.gov.in",
                    "eligibility_criteria": {
                        "tap_water": False,
                        "rural_area": True
                    }
                },
                "SAUBHAGYA": {
                    "name": "Pradhan Mantri Sahaj Bijli Har Ghar Yojana (SAUBHAGYA)",
                    "description": "Electricity connection to every household",
                    "benefit_amount": "Free electricity connection",
                    "ministry": "Ministry of Power",
                    "website": "https://saubhagya.gov.in",
                    "eligibility_criteria": {
                        "electricity": False,
                        "bpl_status": True
                    }
                }
            }
        }
    
    def _load_eligibility_rules(self) -> Dict[str, Any]:
        """Load eligibility assessment rules"""
        return {
            "scoring_weights": {
                "social_category": {"ST": 1.0, "SC": 0.9, "OBC": 0.8, "General": 0.7},
                "bpl_status": {"Yes": 1.0, "No": 0.5},
                "land_ownership": {"Yes": 0.8, "No": 0.3},
                "house_type": {"Homeless": 1.0, "Kutcha": 0.8, "Semi Pucca": 0.6, "Pucca": 0.4},
                "amenities": {"tap_water": 0.2, "electricity": 0.2, "clean_fuel": 0.2, "toilet_facility": 0.2}
            },
            "priority_factors": {
                "tribal_district": 1.5,
                "forest_produce_collection": 1.3,
                "widowed_disabled": 1.2,
                "elderly_members": 1.1
            }
        }
    
    def assess_eligibility(self, fra_data: Dict[str, Any], patta_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Assess eligibility for government schemes based on FRA household data and patta details
        
        Args:
            fra_data: FRA household data from the collection form
            patta_data: Optional patta document data
            
        Returns:
            Dictionary containing eligibility assessment results
        """
        assessment_result = {
            "assessment_date": datetime.now().isoformat(),
            "household_id": fra_data.get("aadhaar_number", "unknown"),
            "head_name": fra_data.get("head_name", "unknown"),
            "eligible_schemes": [],
            "priority_schemes": [],
            "ineligible_schemes": [],
            "overall_score": 0.0,
            "recommendations": [],
            "patta_integration": {}
        }
        
        # Integrate patta data if available
        if patta_data:
            assessment_result["patta_integration"] = self._integrate_patta_data(fra_data, patta_data)
        
        # Assess each scheme category
        for category, schemes in self.schemes_database.items():
            for scheme_id, scheme_info in schemes.items():
                eligibility_result = self._check_scheme_eligibility(fra_data, scheme_info, patta_data)
                
                if eligibility_result["eligible"]:
                    assessment_result["eligible_schemes"].append({
                        "scheme_id": scheme_id,
                        "category": category,
                        **scheme_info,
                        "eligibility_score": eligibility_result["score"],
                        "reasons": eligibility_result["reasons"]
                    })
                else:
                    assessment_result["ineligible_schemes"].append({
                        "scheme_id": scheme_id,
                        "category": category,
                        "name": scheme_info["name"],
                        "reasons": eligibility_result["reasons"]
                    })
        
        # Sort schemes by eligibility score
        assessment_result["eligible_schemes"].sort(key=lambda x: x["eligibility_score"], reverse=True)
        
        # Get top 5 priority schemes
        assessment_result["priority_schemes"] = assessment_result["eligible_schemes"][:5]
        
        # Calculate overall score
        assessment_result["overall_score"] = self._calculate_overall_score(fra_data, patta_data)
        
        # Generate recommendations
        assessment_result["recommendations"] = self._generate_recommendations(assessment_result)
        
        return assessment_result
    
    def _integrate_patta_data(self, fra_data: Dict[str, Any], patta_data: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate patta data with FRA household data"""
        integration = {
            "patta_verified": True,
            "land_area_match": False,
            "survey_number_match": False,
            "owner_name_match": False,
            "integrated_data": {}
        }
        
        # Check land area match
        fra_land_area = fra_data.get("land_area_hectares", "")
        patta_land_area = patta_data.get("hectares", "")
        
        if fra_land_area and patta_land_area:
            try:
                fra_area = float(fra_land_area)
                patta_area = float(patta_land_area)
                integration["land_area_match"] = abs(fra_area - patta_area) < 0.1
            except ValueError:
                pass
        
        # Check survey number match
        fra_survey = fra_data.get("survey_numbers", "")
        patta_survey = patta_data.get("survey_number", "")
        
        if fra_survey and patta_survey:
            integration["survey_number_match"] = patta_survey in fra_survey
        
        # Check owner name match (simplified)
        fra_name = fra_data.get("head_name", "").lower()
        patta_name = patta_data.get("owner_name", "").lower()
        
        if fra_name and patta_name:
            integration["owner_name_match"] = any(word in patta_name for word in fra_name.split())
        
        # Create integrated data
        integration["integrated_data"] = {
            "verified_land_area": patta_data.get("hectares", fra_data.get("land_area_hectares", "")),
            "verified_survey_numbers": patta_data.get("survey_number", fra_data.get("survey_numbers", "")),
            "verified_owner": patta_data.get("owner_name", fra_data.get("head_name", "")),
            "verified_village": patta_data.get("village", ""),
            "verified_district": patta_data.get("district", ""),
            "patta_number": patta_data.get("patta_number", ""),
            "document_ref": patta_data.get("document_ref", "")
        }
        
        return integration
    
    def _check_scheme_eligibility(self, fra_data: Dict[str, Any], scheme_info: Dict[str, Any], patta_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Check eligibility for a specific scheme"""
        criteria = scheme_info["eligibility_criteria"]
        reasons = []
        score = 0.0
        eligible = True
        
        # Check each eligibility criterion
        for criterion, requirement in criteria.items():
            if criterion == "land_ownership":
                has_land = fra_data.get("owns_house") == "Yes" or fra_data.get("land_area_hectares", "")
                if requirement and not has_land:
                    eligible = False
                    reasons.append("No land ownership")
                elif requirement and has_land:
                    score += 0.2
                    reasons.append("✓ Has land ownership")
            
            elif criterion == "cultivates_crops":
                cultivates = fra_data.get("cultivates_crops") == "Yes"
                if requirement and not cultivates:
                    eligible = False
                    reasons.append("Does not cultivate crops")
                elif requirement and cultivates:
                    score += 0.2
                    reasons.append("✓ Cultivates crops")
            
            elif criterion == "social_category":
                household_category = fra_data.get("social_category", "")
                if household_category not in requirement:
                    eligible = False
                    reasons.append(f"Social category {household_category} not eligible")
                else:
                    score += 0.3
                    reasons.append(f"✓ Eligible social category: {household_category}")
            
            elif criterion == "bpl_status":
                is_bpl = fra_data.get("bpl_status") == "Yes"
                if requirement and not is_bpl:
                    eligible = False
                    reasons.append("Not Below Poverty Line")
                elif requirement and is_bpl:
                    score += 0.3
                    reasons.append("✓ Below Poverty Line")
            
            elif criterion == "bank_account":
                has_account = fra_data.get("bank_account") == "Yes"
                if requirement and not has_account:
                    eligible = False
                    reasons.append("No bank account")
                elif requirement and has_account:
                    score += 0.1
                    reasons.append("✓ Has bank account")
            
            elif criterion == "tribal_district":
                is_tribal = fra_data.get("tribal_district") == "Yes"
                if requirement and not is_tribal:
                    eligible = False
                    reasons.append("Not in tribal district")
                elif requirement and is_tribal:
                    score += 0.4
                    reasons.append("✓ Located in tribal district")
            
            elif criterion == "collects_forest_produce":
                collects = fra_data.get("collects_forest_produce") == "Yes"
                if requirement and not collects:
                    eligible = False
                    reasons.append("Does not collect forest produce")
                elif requirement and collects:
                    score += 0.3
                    reasons.append("✓ Collects forest produce")
            
            elif criterion == "willing_mgnrega":
                willing = fra_data.get("willing_mgnrega") == "Yes"
                if requirement and not willing:
                    eligible = False
                    reasons.append("Not willing for MGNREGA work")
                elif requirement and willing:
                    score += 0.2
                    reasons.append("✓ Willing for MGNREGA work")
            
            elif criterion == "min_land_area":
                land_area = fra_data.get("land_area_hectares", "")
                if land_area:
                    try:
                        area = float(land_area)
                        if area < requirement:
                            eligible = False
                            reasons.append(f"Land area {area} hectares below minimum {requirement}")
                        else:
                            score += 0.2
                            reasons.append(f"✓ Land area {area} hectares meets requirement")
                    except ValueError:
                        pass
            
            elif criterion == "max_land_area":
                land_area = fra_data.get("land_area_hectares", "")
                if land_area:
                    try:
                        area = float(land_area)
                        if area > requirement:
                            eligible = False
                            reasons.append(f"Land area {area} hectares exceeds maximum {requirement}")
                        else:
                            score += 0.1
                            reasons.append(f"✓ Land area {area} hectares within limit")
                    except ValueError:
                        pass
        
        # Apply priority factors
        if fra_data.get("tribal_district") == "Yes":
            score *= self.eligibility_rules["priority_factors"]["tribal_district"]
        
        if fra_data.get("collects_forest_produce") == "Yes":
            score *= self.eligibility_rules["priority_factors"]["forest_produce_collection"]
        
        if fra_data.get("has_widowed_disabled") == "Yes":
            score *= self.eligibility_rules["priority_factors"]["widowed_disabled"]
        
        elderly_count = fra_data.get("elderly_count", "")
        if elderly_count and int(elderly_count) > 0:
            score *= self.eligibility_rules["priority_factors"]["elderly_members"]
        
        return {
            "eligible": eligible,
            "score": min(score, 1.0),  # Cap at 1.0
            "reasons": reasons
        }
    
    def _calculate_overall_score(self, fra_data: Dict[str, Any], patta_data: Optional[Dict[str, Any]] = None) -> float:
        """Calculate overall eligibility score"""
        score = 0.0
        
        # Base score from social category
        social_category = fra_data.get("social_category", "General")
        score += self.eligibility_rules["scoring_weights"]["social_category"].get(social_category, 0.5)
        
        # BPL status
        bpl_status = fra_data.get("bpl_status", "No")
        score += self.eligibility_rules["scoring_weights"]["bpl_status"].get(bpl_status, 0.5)
        
        # Land ownership
        owns_land = fra_data.get("owns_house") == "Yes" or fra_data.get("land_area_hectares", "")
        score += self.eligibility_rules["scoring_weights"]["land_ownership"]["Yes"] if owns_land else self.eligibility_rules["scoring_weights"]["land_ownership"]["No"]
        
        # House type
        house_type = fra_data.get("house_type", "Pucca")
        score += self.eligibility_rules["scoring_weights"]["house_type"].get(house_type, 0.4)
        
        # Amenities
        amenities_score = 0.0
        if fra_data.get("tap_water") == "Yes":
            amenities_score += self.eligibility_rules["scoring_weights"]["amenities"]["tap_water"]
        if fra_data.get("electricity") == "Yes":
            amenities_score += self.eligibility_rules["scoring_weights"]["amenities"]["electricity"]
        if fra_data.get("clean_fuel") == "Yes":
            amenities_score += self.eligibility_rules["scoring_weights"]["amenities"]["clean_fuel"]
        if fra_data.get("toilet_facility") == "Private":
            amenities_score += self.eligibility_rules["scoring_weights"]["amenities"]["toilet_facility"]
        
        score += amenities_score
        
        # Patta verification bonus
        if patta_data:
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_recommendations(self, assessment_result: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        eligible_count = len(assessment_result["eligible_schemes"])
        priority_count = len(assessment_result["priority_schemes"])
        
        if eligible_count > 0:
            recommendations.append(f"🎯 You are eligible for {eligible_count} government schemes")
            recommendations.append(f"⭐ Top priority schemes: {', '.join([s['name'] for s in assessment_result['priority_schemes'][:3]])}")
        
        if assessment_result["overall_score"] > 0.8:
            recommendations.append("🌟 High eligibility score - Apply for multiple schemes")
        elif assessment_result["overall_score"] > 0.6:
            recommendations.append("✅ Good eligibility score - Focus on top priority schemes")
        else:
            recommendations.append("📋 Moderate eligibility - Consider improving documentation")
        
        # Specific recommendations based on data
        if assessment_result.get("patta_integration", {}).get("patta_verified"):
            recommendations.append("📄 Patta document verified - Enhanced scheme eligibility")
        
        if not assessment_result.get("patta_integration", {}).get("patta_verified"):
            recommendations.append("📄 Consider uploading patta document for enhanced eligibility")
        
        return recommendations
    
    def save_assessment(self, assessment_result: Dict[str, Any], output_path: str = None) -> str:
        """Save assessment result to JSON file"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            household_id = assessment_result.get("household_id", "unknown")
            output_path = f"fra_assessment_{household_id}_{timestamp}.json"
        
        os.makedirs("assessments", exist_ok=True)
        full_path = os.path.join("assessments", output_path)
        
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(assessment_result, f, ensure_ascii=False, indent=2)
        
        return full_path

# Example usage and testing
if __name__ == "__main__":
    # Test the eligibility engine
    engine = EligibilityEngine()
    
    # Sample FRA data
    sample_fra_data = {
        "head_name": "Ram Singh Bhil",
        "aadhaar_number": "123456789012",
        "mobile_number": "9876543210",
        "social_category": "ST",
        "complete_address": "Khargone Village, Khargone District, Madhya Pradesh",
        "total_family_members": "5",
        "adults_count": "3",
        "elderly_count": "1",
        "bpl_status": "Yes",
        "has_widowed_disabled": "No",
        "owns_house": "Yes",
        "house_type": "Kutcha",
        "land_area_hectares": "1.5",
        "survey_numbers": "123",
        "cultivates_crops": "Yes",
        "crops_list": "Rice, Wheat",
        "tap_water": "No",
        "toilet_facility": "Open Defecation",
        "electricity": "No",
        "clean_fuel": "No",
        "ration_card": "Yes",
        "bank_account": "Yes",
        "tribal_district": "Yes",
        "collects_forest_produce": "Yes",
        "forest_products": "Bamboo, Honey",
        "willing_mgnrega": "Yes",
        "enrolled_schemes": "None"
    }
    
    # Sample patta data
    sample_patta_data = {
        "district": "Khargone",
        "village": "Khargone",
        "patta_number": "12345",
        "owner_name": "Ram Singh Bhil",
        "survey_number": "123",
        "hectares": "1.5",
        "document_ref": "RTR123/2024"
    }
    
    # Run assessment
    result = engine.assess_eligibility(sample_fra_data, sample_patta_data)
    
    # Save result
    output_file = engine.save_assessment(result)
    print(f"Assessment saved to: {output_file}")
    print(f"Eligible schemes: {len(result['eligible_schemes'])}")
    print(f"Priority schemes: {[s['name'] for s in result['priority_schemes']]}")

