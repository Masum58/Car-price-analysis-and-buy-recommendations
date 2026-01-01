"""
Intelligent Car Comparison & Recommendation Engine
Solves: AI analysis, recommendation logic, comparison highlighting

This module adds the missing "decision layer" that:
1. Takes user context into account
2. Compares cars intelligently
3. Highlights better option
4. Provides AI reasoning
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class CarRecommendationEngine:
    """
    Smart car recommendation with user context
    """
    
    def __init__(self):
        self.weights = {
            "price": 0.25,
            "value": 0.20,
            "reliability": 0.20,
            "features": 0.15,
            "fuel_efficiency": 0.10,
            "safety": 0.10
        }
    
    def analyze_car_for_user(
        self, 
        car: Dict, 
        user_context: Dict,
        ml_prediction: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze car with user context
        
        Args:
            car: Car data from scraping
            user_context: User preferences, budget, usage
            ml_prediction: ML price prediction if available
            
        Returns:
            Comprehensive analysis with scores
        """
        
        analysis = {
            "car_id": car.get("details_url", "unknown"),
            "car_title": car.get("car_title", "Unknown"),
            "scores": {},
            "insights": [],
            "warnings": [],
            "user_fit": 0.0,
            "overall_score": 0.0
        }
        
        # 1. Price Score
        price_score = self._calculate_price_score(
            car, user_context, ml_prediction
        )
        analysis["scores"]["price"] = price_score
        
        # 2. Value Score
        value_score = self._calculate_value_score(car, ml_prediction)
        analysis["scores"]["value"] = value_score
        
        # 3. Reliability Score
        reliability_score = self._calculate_reliability_score(car)
        analysis["scores"]["reliability"] = reliability_score
        
        # 4. Features Score
        features_score = self._calculate_features_score(car, user_context)
        analysis["scores"]["features"] = features_score
        
        # 5. Fuel Efficiency Score
        fuel_score = self._calculate_fuel_score(car, user_context)
        analysis["scores"]["fuel_efficiency"] = fuel_score
        
        # 6. Safety Score
        safety_score = self._calculate_safety_score(car)
        analysis["scores"]["safety"] = safety_score
        
        # Calculate overall score
        analysis["overall_score"] = sum(
            analysis["scores"][key] * self.weights[key]
            for key in self.weights
        )
        
        # Calculate user fit (0-100)
        analysis["user_fit"] = analysis["overall_score"] * 100
        
        # Generate insights
        analysis["insights"] = self._generate_insights(car, analysis, user_context)
        
        # Generate warnings
        analysis["warnings"] = self._generate_warnings(car, analysis, user_context)
        
        return analysis
    
    def _calculate_price_score(
        self, 
        car: Dict, 
        user_context: Dict,
        ml_prediction: Optional[Dict]
    ) -> float:
        """Price affordability & fairness score"""
        try:
            price_str = car.get("price", "0")
            price = int(''.join(filter(str.isdigit, price_str))) if price_str else 0
            
            if price == 0:
                return 0.5
            
            budget = user_context.get("max_budget", 50000)
            
            # Budget fit
            if price > budget:
                budget_score = max(0, 1 - ((price - budget) / budget))
            else:
                budget_score = 1.0 - (price / budget) * 0.3  # Prefer not too cheap
            
            # ML fairness (if available)
            fairness_score = 0.8  # Default
            if ml_prediction:
                predicted = ml_prediction.get("predicted_price", price)
                diff_pct = abs(price - predicted) / predicted
                fairness_score = max(0, 1 - diff_pct)
            
            return (budget_score * 0.6) + (fairness_score * 0.4)
            
        except:
            return 0.5
    
    def _calculate_value_score(self, car: Dict, ml_prediction: Optional[Dict]) -> float:
        """Value for money score"""
        try:
            # Check if it's a good deal
            if ml_prediction:
                predicted = ml_prediction.get("predicted_price", 0)
                actual_str = car.get("price", "0")
                actual = int(''.join(filter(str.isdigit, actual_str)))
                
                if predicted > 0 and actual > 0:
                    savings = predicted - actual
                    savings_pct = savings / predicted
                    
                    # Good deal if actual < predicted
                    if savings_pct > 0.1:  # 10%+ savings
                        return 1.0
                    elif savings_pct > 0:
                        return 0.8
                    elif savings_pct > -0.1:  # Fair price
                        return 0.6
                    else:  # Overpriced
                        return 0.4
            
            # Default: moderate value
            return 0.7
            
        except:
            return 0.7
    
    def _calculate_reliability_score(self, car: Dict) -> float:
        """Brand & age reliability score"""
        try:
            # Brand reliability (simplified)
            brand_scores = {
                "toyota": 0.95,
                "honda": 0.90,
                "mazda": 0.88,
                "lexus": 0.95,
                "bmw": 0.75,
                "mercedes": 0.75,
                "audi": 0.75,
                "volkswagen": 0.80,
                "ford": 0.78,
                "volvo": 0.85
            }
            
            title = car.get("car_title", "").lower()
            brand_score = 0.75  # Default
            
            for brand, score in brand_scores.items():
                if brand in title:
                    brand_score = score
                    break
            
            # Age penalty
            hist = car.get("Vehicle_History", {})
            reg = hist.get("First_registration", "")
            
            if reg and "/" in reg:
                try:
                    year = int(reg.split("/")[-1])
                    age = 2025 - year
                    age_score = max(0.5, 1 - (age * 0.05))  # 5% per year
                except:
                    age_score = 0.8
            else:
                age_score = 0.8
            
            return (brand_score * 0.6) + (age_score * 0.4)
            
        except:
            return 0.75
    
    def _calculate_features_score(self, car: Dict, user_context: Dict) -> float:
        """Features match with user needs"""
        try:
            # Get all feature-related fields
            basic = car.get("Basic_Data", {})
            tech = car.get("Technical_Data", {})
            
            score = 0.5  # Base
            
            # Wanted features from user
            wanted = user_context.get("wanted_features", [])
            
            # Check seats
            req_seats = user_context.get("min_seats", 0)
            seats_str = basic.get("Seats", "5")
            try:
                seats = int(''.join(filter(str.isdigit, seats_str)))
                if seats >= req_seats:
                    score += 0.15
            except:
                pass
            
            # Check gearbox preference
            pref_gearbox = user_context.get("preferred_gearbox", "").lower()
            actual_gearbox = tech.get("Gearbox", "").lower()
            
            if pref_gearbox and pref_gearbox in actual_gearbox:
                score += 0.20
            
            # Bonus for modern features
            if any(word in str(car).lower() for word in ["navigation", "parking", "camera"]):
                score += 0.15
            
            return min(1.0, score)
            
        except:
            return 0.6
    
    def _calculate_fuel_score(self, car: Dict, user_context: Dict) -> float:
        """Fuel efficiency & type score"""
        try:
            energy = car.get("Energy_Consumption", {})
            fuel_type = energy.get("Fuel_type", "").lower()
            
            # User preference
            pref_fuel = user_context.get("preferred_fuel", "").lower()
            
            score = 0.6  # Base
            
            # Match preference
            if pref_fuel and pref_fuel in fuel_type:
                score += 0.3
            
            # Bonus for efficient types
            if "hybrid" in fuel_type or "electric" in fuel_type:
                score += 0.1
            
            return min(1.0, score)
            
        except:
            return 0.6
    
    def _calculate_safety_score(self, car: Dict) -> float:
        """Safety features score"""
        try:
            # Check for safety keywords
            car_str = str(car).lower()
            
            safety_keywords = [
                "abs", "airbag", "esp", "brake assist",
                "parking sensor", "camera", "blind spot"
            ]
            
            found = sum(1 for kw in safety_keywords if kw in car_str)
            
            score = 0.5 + (found * 0.08)  # 8% per feature
            
            return min(1.0, score)
            
        except:
            return 0.6
    
    def _generate_insights(
        self, 
        car: Dict, 
        analysis: Dict,
        user_context: Dict
    ) -> List[str]:
        """Generate human-readable insights"""
        insights = []
        
        scores = analysis["scores"]
        
        # Price insights
        if scores["price"] > 0.8:
            insights.append("✅ Well within your budget")
        elif scores["price"] < 0.5:
            insights.append("⚠️ Above your preferred budget")
        
        # Value insights
        if scores["value"] > 0.85:
            insights.append("💰 Excellent deal - below market price")
        elif scores["value"] < 0.5:
            insights.append("⚠️ Priced above market average")
        
        # Reliability insights
        if scores["reliability"] > 0.85:
            insights.append("🔧 Highly reliable brand and age")
        elif scores["reliability"] < 0.6:
            insights.append("⚠️ May require more maintenance")
        
        # Features insights
        if scores["features"] > 0.8:
            insights.append("⭐ Great feature match for your needs")
        
        # Fuel insights
        if scores["fuel_efficiency"] > 0.8:
            insights.append("⛽ Good fuel economy for your usage")
        
        return insights
    
    def _generate_warnings(
        self,
        car: Dict,
        analysis: Dict,
        user_context: Dict
    ) -> List[str]:
        """Generate warnings"""
        warnings = []
        
        scores = analysis["scores"]
        
        if scores["price"] < 0.4:
            warnings.append("Budget concern - significantly over budget")
        
        if scores["value"] < 0.5:
            warnings.append("Not the best value for money")
        
        if scores["reliability"] < 0.6:
            warnings.append("Higher maintenance risk")
        
        # Check mileage
        try:
            hist = car.get("Vehicle_History", {})
            mileage_str = hist.get("Mileage", "0")
            mileage = int(''.join(filter(str.isdigit, mileage_str)))
            
            if mileage > 150000:
                warnings.append("High mileage - thorough inspection recommended")
        except:
            pass
        
        return warnings
    
    def compare_two_cars(
        self,
        car_a: Dict,
        car_b: Dict,
        user_context: Dict,
        ml_predictions: Optional[Dict] = None
    ) -> Dict:
        """
        Compare two cars and determine better option
        
        Returns comprehensive comparison with recommendation
        """
        
        # Get ML predictions
        ml_a = ml_predictions.get("car_a") if ml_predictions else None
        ml_b = ml_predictions.get("car_b") if ml_predictions else None
        
        # Analyze both
        analysis_a = self.analyze_car_for_user(car_a, user_context, ml_a)
        analysis_b = self.analyze_car_for_user(car_b, user_context, ml_b)
        
        # Determine winner
        score_diff = analysis_a["user_fit"] - analysis_b["user_fit"]
        
        if abs(score_diff) < 5:  # Very close
            recommendation = "tie"
            confidence = "low"
        elif abs(score_diff) < 15:  # Close
            recommendation = "car_a" if score_diff > 0 else "car_b"
            confidence = "medium"
        else:  # Clear winner
            recommendation = "car_a" if score_diff > 0 else "car_b"
            confidence = "high"
        
        # Build comparison
        comparison = {
            "car_a": {
                "title": car_a.get("car_title"),
                "analysis": analysis_a,
                "is_better": recommendation == "car_a"
            },
            "car_b": {
                "title": car_b.get("car_title"),
                "analysis": analysis_b,
                "is_better": recommendation == "car_b"
            },
            "recommendation": recommendation,
            "confidence": confidence,
            "score_difference": abs(score_diff),
            "comparison_details": self._detailed_comparison(
                analysis_a, analysis_b
            ),
            "ai_reasoning": self._generate_reasoning(
                car_a, car_b, analysis_a, analysis_b, recommendation
            )
        }
        
        return comparison
    
    def _detailed_comparison(
        self,
        analysis_a: Dict,
        analysis_b: Dict
    ) -> Dict:
        """Detailed score comparison"""
        
        details = {}
        
        for category in analysis_a["scores"]:
            score_a = analysis_a["scores"][category]
            score_b = analysis_b["scores"][category]
            
            details[category] = {
                "car_a_score": round(score_a, 2),
                "car_b_score": round(score_b, 2),
                "winner": "car_a" if score_a > score_b else "car_b" if score_b > score_a else "tie",
                "difference": round(abs(score_a - score_b), 2)
            }
        
        return details
    
    def _generate_reasoning(
        self,
        car_a: Dict,
        car_b: Dict,
        analysis_a: Dict,
        analysis_b: Dict,
        recommendation: str
    ) -> str:
        """Generate AI explanation"""
        
        if recommendation == "tie":
            return (
                f"Both cars are very close matches for you. "
                f"Car A scores {analysis_a['user_fit']:.1f}/100 while "
                f"Car B scores {analysis_b['user_fit']:.1f}/100. "
                f"Consider other factors like seller reputation and test drive experience."
            )
        
        winner = analysis_a if recommendation == "car_a" else analysis_b
        loser = analysis_b if recommendation == "car_a" else analysis_a
        winner_name = "Car A" if recommendation == "car_a" else "Car B"
        
        # Find strongest advantages
        advantages = []
        for cat in winner["scores"]:
            if winner["scores"][cat] - loser["scores"][cat] > 0.15:
                advantages.append(cat.replace("_", " ").title())
        
        reasoning = (
            f"{winner_name} is the better choice with a score of "
            f"{winner['user_fit']:.1f}/100 vs {loser['user_fit']:.1f}/100. "
        )
        
        if advantages:
            reasoning += f"It excels in: {', '.join(advantages)}. "
        
        # Add top insight
        if winner["insights"]:
            reasoning += f"{winner['insights'][0]}"
        
        return reasoning


# ============================================
# Helper Functions for API Integration
# ============================================

def get_user_context_from_request(request_data: Dict) -> Dict:
    """Extract user context from API request"""
    
    return {
        "max_budget": request_data.get("max_budget", 50000),
        "min_seats": request_data.get("min_seats", 5),
        "preferred_gearbox": request_data.get("preferred_gearbox", ""),
        "preferred_fuel": request_data.get("preferred_fuel", ""),
        "wanted_features": request_data.get("wanted_features", []),
        "usage_type": request_data.get("usage_type", "daily"),  # daily/family/business
        "priority": request_data.get("priority", "balanced")  # price/features/reliability
    }


def format_comparison_for_ui(comparison: Dict) -> Dict:
    """Format comparison result for UI display"""
    
    return {
        "recommended_car": comparison["recommendation"],
        "confidence": comparison["confidence"],
        "car_a": {
            "highlight": comparison["car_a"]["is_better"],
            "score": round(comparison["car_a"]["analysis"]["user_fit"], 1),
            "insights": comparison["car_a"]["analysis"]["insights"][:3],
            "warnings": comparison["car_a"]["analysis"]["warnings"]
        },
        "car_b": {
            "highlight": comparison["car_b"]["is_better"],
            "score": round(comparison["car_b"]["analysis"]["user_fit"], 1),
            "insights": comparison["car_b"]["analysis"]["insights"][:3],
            "warnings": comparison["car_b"]["analysis"]["warnings"]
        },
        "reasoning": comparison["ai_reasoning"],
        "detailed_scores": comparison["comparison_details"]
    }


# ============================================
# Example Usage
# ============================================

if __name__ == "__main__":
    # Example usage
    engine = CarRecommendationEngine()
    
    # Mock user context
    user_context = {
        "max_budget": 30000,
        "min_seats": 5,
        "preferred_gearbox": "automatic",
        "preferred_fuel": "diesel",
        "wanted_features": ["navigation", "parking sensors"],
        "usage_type": "family",
        "priority": "balanced"
    }
    
    # Mock car data
    car_a = {
        "car_title": "BMW 320d Touring",
        "price": "€28,500",
        "details_url": "https://example.com/car-a",
        "Basic_Data": {"Seats": "5"},
        "Technical_Data": {"Gearbox": "Automatic"},
        "Vehicle_History": {"First_registration": "03/2019", "Mileage": "65,000 km"},
        "Energy_Consumption": {"Fuel_type": "Diesel"}
    }
    
    car_b = {
        "car_title": "Audi A4 Avant",
        "price": "€32,900",
        "details_url": "https://example.com/car-b",
        "Basic_Data": {"Seats": "5"},
        "Technical_Data": {"Gearbox": "Automatic"},
        "Vehicle_History": {"First_registration": "05/2020", "Mileage": "45,000 km"},
        "Energy_Consumption": {"Fuel_type": "Diesel"}
    }
    
    # Compare
    result = engine.compare_two_cars(car_a, car_b, user_context)
    
    # Format for UI
    ui_result = format_comparison_for_ui(result)
    
    print(json.dumps(ui_result, indent=2))