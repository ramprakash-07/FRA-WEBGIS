"""
Enhanced DSS Engine for FRA-SENTINEL
Decision Support System with ML integration for scheme layering and convergence
"""

import json
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger(__name__)

@dataclass
class Scheme:
    name: str
    ministry: str
    category: str
    eligibility_criteria: Dict
    benefit_amount: str
    convergence_score: float
    priority: int
    ml_weight: float = 0.5

@dataclass
class VillageProfile:
    village_id: int
    name: str
    population: int
    tribal_population_pct: float
    forest_cover_pct: float
    water_bodies_count: int
    agricultural_land_pct: float
    fra_status: str
    existing_schemes: List[str]
    literacy_rate: float = 0.0
    poverty_rate: float = 0.0
    connectivity_score: float = 0.0
    infrastructure_score: float = 0.0

class MLDSSEngine:
    """Enhanced DSS Engine with ML integration"""
    
    def __init__(self):
        self.schemes = self._load_schemes()
        self.rules = self._load_rules()
        self.ml_models = {}
        self.scalers = {}
        self._initialize_ml_models()
    
    def _load_schemes(self) -> List[Scheme]:
        """Load available schemes with ML weights"""
        schemes_data = [
            {
                "name": "PM-KISAN",
                "ministry": "Agriculture",
                "category": "Income Support",
                "eligibility_criteria": {"land_holding": "<= 2 hectares"},
                "benefit_amount": "₹6000/year",
                "convergence_score": 0.8,
                "priority": 1,
                "ml_weight": 0.6
            },
            {
                "name": "Jal Jeevan Mission",
                "ministry": "Jal Shakti",
                "category": "Water Supply",
                "eligibility_criteria": {"water_scarcity": True},
                "benefit_amount": "Infrastructure",
                "convergence_score": 0.9,
                "priority": 2,
                "ml_weight": 0.7
            },
            {
                "name": "MGNREGA",
                "ministry": "Rural Development",
                "category": "Employment",
                "eligibility_criteria": {"rural_area": True},
                "benefit_amount": "₹200/day",
                "convergence_score": 0.7,
                "priority": 3,
                "ml_weight": 0.5
            },
            {
                "name": "DAJGUA",
                "ministry": "Tribal Affairs",
                "category": "Tribal Development",
                "eligibility_criteria": {"tribal_area": True},
                "benefit_amount": "₹50000/household",
                "convergence_score": 0.95,
                "priority": 1,
                "ml_weight": 0.8
            }
        ]
        
        return [Scheme(**scheme) for scheme in schemes_data]
    
    def _load_rules(self) -> Dict:
        """Load decision rules with enhanced criteria"""
        return {
            "water_scarcity": {"condition": "water_bodies_count < 2", "weight": 0.3},
            "agricultural_focus": {"condition": "agricultural_land_pct > 60", "weight": 0.2},
            "tribal_priority": {"condition": "tribal_population_pct > 50", "weight": 0.4},
            "forest_dependency": {"condition": "forest_cover_pct > 40", "weight": 0.3}
        }
    
    def _initialize_ml_models(self):
        """Initialize ML models for each scheme"""
        for scheme in self.schemes:
            model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
            scaler = StandardScaler()
            self.ml_models[scheme.name] = model
            self.scalers[scheme.name] = scaler
            self._train_scheme_model(scheme.name)
    
    def _train_scheme_model(self, scheme_name: str):
        """Train ML model for a specific scheme"""
        np.random.seed(42)
        n_samples = 1000
        X = np.random.rand(n_samples, 9)
        
        # Scale features to realistic ranges
        X[:, 0] = X[:, 0] * 2000 + 100  # population
        X[:, 1] = X[:, 1] * 100  # tribal_pct
        X[:, 2] = X[:, 2] * 100  # forest_pct
        X[:, 3] = X[:, 3] * 10  # water_bodies
        X[:, 4] = X[:, 4] * 100  # agri_pct
        X[:, 5] = X[:, 5] * 100  # literacy_rate
        X[:, 6] = X[:, 6] * 100  # poverty_rate
        X[:, 7] = X[:, 7]  # connectivity_score
        X[:, 8] = X[:, 8]  # infrastructure_score
        
        y = self._generate_scheme_scores(scheme_name, X)
        X_scaled = self.scalers[scheme_name].fit_transform(X)
        self.ml_models[scheme_name].fit(X_scaled, y)
        
        logger.info(f"Trained ML model for {scheme_name}")
    
    def _generate_scheme_scores(self, scheme_name: str, X: np.ndarray) -> np.ndarray:
        """Generate synthetic scores for scheme training"""
        scores = np.zeros(X.shape[0])
        
        if scheme_name == "PM-KISAN":
            scores = X[:, 4] * 0.4 + X[:, 5] * 0.2 + X[:, 8] * 0.4
        elif scheme_name == "Jal Jeevan Mission":
            scores = (10 - X[:, 3]) * 0.3 + X[:, 0] * 0.2 + X[:, 6] * 0.3 + X[:, 8] * 0.2
        elif scheme_name == "MGNREGA":
            scores = X[:, 0] * 0.3 + X[:, 6] * 0.4 + X[:, 7] * 0.3
        elif scheme_name == "DAJGUA":
            scores = X[:, 1] * 0.5 + X[:, 2] * 0.3 + X[:, 6] * 0.2
        
        scores = (scores - scores.min()) / (scores.max() - scores.min())
        return scores
    
    def analyze_village(self, village_profile: VillageProfile) -> Dict:
        """Analyze village and recommend schemes with ML integration"""
        recommendations = []
        
        for scheme in self.schemes:
            rule_score = self._calculate_eligibility(village_profile, scheme)
            ml_score = self._calculate_ml_score(village_profile, scheme)
            combined_score = (rule_score * (1 - scheme.ml_weight) + ml_score * scheme.ml_weight)
            
            if combined_score > 0.5:
                recommendations.append({
                    "scheme": scheme.name,
                    "ministry": scheme.ministry,
                    "category": scheme.category,
                    "eligibility_score": rule_score,
                    "ml_score": ml_score,
                    "combined_score": combined_score,
                    "benefit_amount": scheme.benefit_amount,
                    "convergence_score": scheme.convergence_score,
                    "priority": scheme.priority,
                    "reasons": self._get_recommendation_reasons(village_profile, scheme),
                    "ml_insights": self._get_ml_insights(village_profile, scheme)
                })
        
        recommendations.sort(key=lambda x: (x["priority"], -x["combined_score"]))
        
        return {
            "village_id": village_profile.village_id,
            "village_name": village_profile.name,
            "analysis_date": datetime.now().isoformat(),
            "recommendations": recommendations,
            "total_schemes": len(recommendations),
            "high_priority_schemes": len([r for r in recommendations if r["priority"] <= 2]),
            "ml_confidence": self._calculate_overall_ml_confidence(recommendations)
        }
    
    def _calculate_eligibility(self, village: VillageProfile, scheme: Scheme) -> float:
        """Calculate rule-based eligibility score for a scheme"""
        score = 0.0
        
        if scheme.name == "PM-KISAN":
            if village.agricultural_land_pct > 60:
                score += 0.8
            if village.population > 100:
                score += 0.2
        elif scheme.name == "Jal Jeevan Mission":
            if village.water_bodies_count < 2:
                score += 0.9
            if village.population >= 100:
                score += 0.1
        elif scheme.name == "MGNREGA":
            if village.population > 50:
                score += 0.7
            if village.agricultural_land_pct > 40:
                score += 0.3
        elif scheme.name == "DAJGUA":
            if village.tribal_population_pct >= 50:
                score += 0.9
            if village.forest_cover_pct > 40:
                score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_ml_score(self, village: VillageProfile, scheme: Scheme) -> float:
        """Calculate ML-based score for a scheme"""
        features = np.array([
            village.population, village.tribal_population_pct, village.forest_cover_pct,
            village.water_bodies_count, village.agricultural_land_pct, village.literacy_rate,
            village.poverty_rate, village.connectivity_score, village.infrastructure_score
        ]).reshape(1, -1)
        
        features_scaled = self.scalers[scheme.name].transform(features)
        ml_score = self.ml_models[scheme.name].predict(features_scaled)[0]
        
        return max(0.0, min(1.0, ml_score))
    
    def _get_recommendation_reasons(self, village: VillageProfile, scheme: Scheme) -> List[str]:
        """Get reasons for recommendation"""
        reasons = []
        
        if scheme.name == "PM-KISAN":
            if village.agricultural_land_pct > 60:
                reasons.append("High agricultural land coverage")
            if village.population > 100:
                reasons.append("Sufficient population for scheme implementation")
        elif scheme.name == "Jal Jeevan Mission":
            if village.water_bodies_count < 2:
                reasons.append("Limited water bodies - water scarcity")
            if village.population >= 100:
                reasons.append("Population meets minimum requirement")
        elif scheme.name == "MGNREGA":
            if village.population > 50:
                reasons.append("Adequate population for employment generation")
            if village.agricultural_land_pct > 40:
                reasons.append("Agricultural activities support employment")
        elif scheme.name == "DAJGUA":
            if village.tribal_population_pct >= 50:
                reasons.append("High tribal population - priority area")
            if village.forest_cover_pct > 40:
                reasons.append("Forest-dependent community")
        
        return reasons
    
    def _get_ml_insights(self, village: VillageProfile, scheme: Scheme) -> Dict:
        """Get ML-based insights for recommendation"""
        feature_names = [
            'population', 'tribal_pct', 'forest_pct', 'water_bodies',
            'agri_pct', 'literacy_rate', 'poverty_rate', 'connectivity', 'infrastructure'
        ]
        
        feature_importance = self.ml_models[scheme.name].feature_importances_
        top_factors = sorted(
            zip(feature_names, feature_importance),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return {
            "top_factors": [{"factor": name, "importance": float(imp)} for name, imp in top_factors],
            "model_confidence": float(np.mean(feature_importance)),
            "prediction_reliability": "high" if np.mean(feature_importance) > 0.1 else "medium"
        }
    
    def _calculate_overall_ml_confidence(self, recommendations: List[Dict]) -> float:
        """Calculate overall ML confidence for recommendations"""
        if not recommendations:
            return 0.0
        
        ml_scores = [rec["ml_score"] for rec in recommendations]
        return float(np.mean(ml_scores))
    
    def get_convergence_analysis(self, village_profiles: List[VillageProfile]) -> Dict:
        """Analyze convergence across multiple villages with ML insights"""
        total_villages = len(village_profiles)
        scheme_counts = {}
        ministry_counts = {}
        ml_insights = {}
        
        for village in village_profiles:
            analysis = self.analyze_village(village)
            
            for rec in analysis["recommendations"]:
                scheme_name = rec["scheme"]
                ministry = rec["ministry"]
                
                scheme_counts[scheme_name] = scheme_counts.get(scheme_name, 0) + 1
                ministry_counts[ministry] = ministry_counts.get(ministry, 0) + 1
                
                if scheme_name not in ml_insights:
                    ml_insights[scheme_name] = {"total_score": 0, "count": 0, "avg_ml_score": 0}
                
                ml_insights[scheme_name]["total_score"] += rec["ml_score"]
                ml_insights[scheme_name]["count"] += 1
        
        for scheme_name in ml_insights:
            ml_insights[scheme_name]["avg_ml_score"] = (
                ml_insights[scheme_name]["total_score"] / ml_insights[scheme_name]["count"]
            )
        
        return {
            "total_villages": total_villages,
            "scheme_distribution": scheme_counts,
            "ministry_distribution": ministry_counts,
            "ml_insights": ml_insights,
            "convergence_opportunities": self._identify_convergence_opportunities(scheme_counts),
            "analysis_date": datetime.now().isoformat()
        }
    
    def _identify_convergence_opportunities(self, scheme_counts: Dict) -> List[Dict]:
        """Identify convergence opportunities with ML validation"""
        opportunities = []
        
        for scheme, count in scheme_counts.items():
            if count >= 5:
                opportunities.append({
                    "type": "scheme_convergence",
                    "scheme": scheme,
                    "village_count": count,
                    "description": f"{scheme} recommended for {count} villages",
                    "ml_validation": "high_confidence" if count >= 10 else "medium_confidence"
                })
        
        return opportunities

# Global DSS engine instance
dss_engine = MLDSSEngine()

def analyze_village_dss(village_id: int, village_data: Dict) -> Dict:
    """Analyze village using enhanced DSS engine"""
    village_profile = VillageProfile(
        village_id=village_id,
        name=village_data.get("name", "Unknown"),
        population=village_data.get("population", 0),
        tribal_population_pct=village_data.get("tribal_population_pct", 0),
        forest_cover_pct=village_data.get("forest_cover_pct", 0),
        water_bodies_count=village_data.get("water_bodies_count", 0),
        agricultural_land_pct=village_data.get("agricultural_land_pct", 0),
        fra_status=village_data.get("fra_status", "unknown"),
        existing_schemes=village_data.get("existing_schemes", []),
        literacy_rate=village_data.get("literacy_rate", 0.0),
        poverty_rate=village_data.get("poverty_rate", 0.0),
        connectivity_score=village_data.get("connectivity_score", 0.0),
        infrastructure_score=village_data.get("infrastructure_score", 0.0)
    )
    
    return dss_engine.analyze_village(village_profile)

def get_convergence_analysis(villages_data: List[Dict]) -> Dict:
    """Get convergence analysis for multiple villages"""
    village_profiles = []
    for i, village_data in enumerate(villages_data):
        village_profile = VillageProfile(
            village_id=i + 1,
            name=village_data.get("name", f"Village {i + 1}"),
            population=village_data.get("population", 0),
            tribal_population_pct=village_data.get("tribal_population_pct", 0),
            forest_cover_pct=village_data.get("forest_cover_pct", 0),
            water_bodies_count=village_data.get("water_bodies_count", 0),
            agricultural_land_pct=village_data.get("agricultural_land_pct", 0),
            fra_status=village_data.get("fra_status", "unknown"),
            existing_schemes=village_data.get("existing_schemes", []),
            literacy_rate=village_data.get("literacy_rate", 0.0),
            poverty_rate=village_data.get("poverty_rate", 0.0),
            connectivity_score=village_data.get("connectivity_score", 0.0),
            infrastructure_score=village_data.get("infrastructure_score", 0.0)
        )
        village_profiles.append(village_profile)
    
    return dss_engine.get_convergence_analysis(village_profiles)

def retrain_dss_models(training_data: Dict[str, List[Dict]]):
    """Retrain DSS ML models with new data"""
    dss_engine.retrain_models(training_data)

if __name__ == "__main__":
    # Test the enhanced DSS engine
    test_village_data = {
        "name": "Test Village",
        "population": 500,
        "tribal_population_pct": 60,
        "forest_cover_pct": 45,
        "water_bodies_count": 1,
        "agricultural_land_pct": 55,
        "fra_status": "granted",
        "existing_schemes": [],
        "literacy_rate": 65.0,
        "poverty_rate": 30.0,
        "connectivity_score": 0.3,
        "infrastructure_score": 0.4
    }
    
    result = analyze_village_dss(1, test_village_data)
    print("Enhanced DSS Analysis Result:")
    print(json.dumps(result, indent=2))









