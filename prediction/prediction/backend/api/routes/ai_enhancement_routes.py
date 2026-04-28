import os
import json
import urllib.error
import urllib.request
from flask import Blueprint, jsonify, request
from datetime import datetime
import traceback

ai_enhancement_bp = Blueprint('ai_enhancement', __name__)

def get_openai_client():
    """Get OpenAI or OpenRouter API key from environment."""
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip() or os.getenv("OPENAI_API_KEY", "").strip()
    return api_key

def get_gemini_client():
    """Get Gemini API key from environment."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    return api_key

import urllib.parse
from xml.etree import ElementTree

def get_fda_drug_warnings(drug_name):
    """Fetch FDA boxed warnings and precautions for a drug."""
    try:
        url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:\"{urllib.parse.quote(drug_name)}\"&limit=1"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("results"):
                result = data["results"][0]
                warnings = result.get("boxed_warning", []) + result.get("warnings_and_cautions", []) + result.get("precautions", []) + result.get("warnings", []) + result.get("do_not_use", []) + result.get("stop_use", [])
                if warnings:
                    return f"FDA Warnings for {drug_name}: " + " ".join(warnings)[:500] + "..."
    except Exception as e:
        print(f"Error fetching FDA data for {drug_name}: {e}")
    return f"No direct FDA boxed warnings found in API for {drug_name}."

def get_pubmed_articles(disease):
    """Fetch recent clinical literature from PubMed."""
    try:
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(disease)}+guidelines&retmode=json&retmax=3&sort=pub+date"
        req = urllib.request.Request(search_url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            id_list = data.get("esearchresult", {}).get("idlist", [])
            
        if not id_list:
            return ""
            
        ids = ",".join(id_list)
        summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids}&retmode=json"
        req_sum = urllib.request.Request(summary_url, method="GET")
        with urllib.request.urlopen(req_sum, timeout=10) as resp_sum:
            sum_data = json.loads(resp_sum.read().decode("utf-8"))
            articles = sum_data.get("result", {})
            
        links = []
        for uid in id_list:
            if uid in articles:
                title = articles[uid].get("title", "Clinical Study")
                links.append(f"- {title} (https://pubmed.ncbi.nlm.nih.gov/{uid}/)")
                
        if links:
            return "\nRecent PubMed Clinical Literature:\n" + "\n".join(links)
    except Exception as e:
        print(f"Error fetching PubMed data for {disease}: {e}")
    return ""

@ai_enhancement_bp.route('/enhanced-diagnosis', methods=['POST'])
def enhanced_diagnosis():
    """Enhance diagnosis using multiple AI models."""
    try:
        data = request.get_json()
        features = data.get('features', [])
        disease_type = data.get('disease', 'diabetes')
        prescription = data.get('prescription', '')
        
        if not features:
            return jsonify({"error": "features are required"}), 400
        
        enhanced_results = {}
        
        # OpenAI Enhancement
        openai_key = get_openai_client()
        if openai_key:
            try:
                openai_result = call_openai_enhancement(features, disease_type, prescription, openai_key)
                enhanced_results["openai"] = openai_result
            except Exception as e:
                enhanced_results["openai"] = {"error": str(e)}
        
        # Gemini Enhancement
        gemini_key = get_gemini_client()
        if gemini_key:
            try:
                gemini_result = call_gemini_enhancement(features, disease_type, prescription, gemini_key)
                enhanced_results["gemini"] = gemini_result
            except Exception as e:
                enhanced_results["gemini"] = {"error": str(e)}
        
        # Combine results
        combined_analysis = combine_ai_results(enhanced_results, disease_type)
        
        return jsonify({
            "status": "success",
            "data": {
                "enhanced_results": enhanced_results,
                "combined_analysis": combined_analysis,
                "disease_type": disease_type,
                "features": features
            }
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Enhanced diagnosis failed: {str(e)}"}), 500

def call_openai_enhancement(features, disease_type, prescription, api_key):
    """Call OpenAI API for enhanced analysis."""
    
    # Format features for readability
    feature_descriptions = {
        "diabetes": ["Glucose", "Blood Pressure", "BMI", "Age", "Insulin", "Skin Thickness", "Pregnancies", "Diabetes Pedigree"],
        "heart": ["Age", "Sex", "Chest Pain Type", "Resting BP", "Cholesterol", "Fasting BS", "Max HR", "Exercise Angina"],
        "mental": ["Age", "Gender", "Family History", "Work Interference", "Sleep Hours", "Stress Level", "Social Support", "Treatment Seeking"]
    }
    
    descriptions = feature_descriptions.get(disease_type, ["Feature " + str(i+1) for i in range(len(features))])
    
    pubmed_info = get_pubmed_articles(disease_type)
    
    prompt = f"""
    As a medical AI assistant, analyze the following {disease_type} health data and provide comprehensive insights:
    
    Patient Data:
    {json.dumps(dict(zip(descriptions, features)), indent=2)}
    
    Prescription Notes: {prescription or 'None provided'}
    {pubmed_info}
    
    Please provide:
    1. Risk assessment with percentage
    2. Key health indicators that need attention
    3. Lifestyle recommendations
    4. When to seek medical help
    5. Preventive measures
    
    Format your response as structured JSON with keys: risk_assessment, key_indicators, recommendations, when_to_seek_help, preventive_measures
    """
    
    model_name = "mistralai/mistral-7b-instruct:free" if os.getenv("OPENROUTER_API_KEY") else "gpt-4o-mini"
    
    req_body = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": "You are a medical AI assistant providing health analysis. Always respond in valid JSON format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 500,
        "temperature": 0.3
    }
    
    api_url = "https://openrouter.ai/api/v1/chat/completions" if os.getenv("OPENROUTER_API_KEY") else "https://api.openai.com/v1/chat/completions"
    req = urllib.request.Request(
        api_url,
        data=json.dumps(req_body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Healthcare AI Platform"
        },
        method="POST",
    )
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    
    try:
        choices = body.get("choices", [])
        if choices and len(choices) > 0:
            message = choices[0].get("message", {})
            content = (message.get("content") or "").strip()
            
            # Try to parse as JSON
            try:
                return json.loads(content)
            except:
                return {"analysis": content}
        else:
            return {"error": "No response from OpenAI"}
    except Exception as e:
        return {"error": f"Failed to parse OpenAI response: {str(e)}"}

def call_gemini_enhancement(features, disease_type, prescription, api_key):
    """Call Gemini API for enhanced analysis."""
    
    # Format features for readability
    feature_descriptions = {
        "diabetes": ["Glucose", "Blood Pressure", "BMI", "Age", "Insulin", "Skin Thickness", "Pregnancies", "Diabetes Pedigree"],
        "heart": ["Age", "Sex", "Chest Pain Type", "Resting BP", "Cholesterol", "Fasting BS", "Max HR", "Exercise Angina"],
        "mental": ["Age", "Gender", "Family History", "Work Interference", "Sleep Hours", "Stress Level", "Social Support", "Treatment Seeking"]
    }
    
    descriptions = feature_descriptions.get(disease_type, ["Feature " + str(i+1) for i in range(len(features))])
    
    prompt = f"""
    Analyze the following {disease_type} health data and provide medical insights:
    
    Patient Data: {json.dumps(dict(zip(descriptions, features)), indent=2)}
    Prescription: {prescription or 'None'}
    
    Provide analysis covering:
    - Risk level (Low/Moderate/High) with confidence
    - Critical indicators
    - Recommended actions
    - Follow-up suggestions
    """
    
    req_body = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 500
        }
    }
    
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
        data=json.dumps(req_body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    
    try:
        candidates = body.get("candidates", [])
        if candidates and len(candidates) > 0:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if parts and len(parts) > 0:
                text = parts[0].get("text", "").strip()
                return {"analysis": text}
        else:
            return {"error": "No response from Gemini"}
    except Exception as e:
        return {"error": f"Failed to parse Gemini response: {str(e)}"}

def combine_ai_results(results, disease_type):
    """Combine results from multiple AI models."""
    combined = {
        "consensus_risk": "Moderate",
        "confidence": 0.5,
        "key_insights": [],
        "recommendations": [],
        "sources_used": []
    }
    
    risk_votes = {"Low": 0, "Moderate": 0, "High": 0}
    all_insights = []
    all_recommendations = []
    
    for source, result in results.items():
        if "error" in result:
            continue
            
        combined["sources_used"].append(source)
        
        # Extract risk assessment
        if "risk_assessment" in result:
            risk_text = result["risk_assessment"].lower()
            if "high" in risk_text:
                risk_votes["High"] += 1
            elif "low" in risk_text:
                risk_votes["Low"] += 1
            else:
                risk_votes["Moderate"] += 1
        
        # Extract insights
        if "key_indicators" in result:
            if isinstance(result["key_indicators"], list):
                all_insights.extend(result["key_indicators"])
            else:
                all_insights.append(str(result["key_indicators"]))
        
        if "analysis" in result:
            all_insights.append(result["analysis"])
        
        # Extract recommendations
        if "recommendations" in result:
            if isinstance(result["recommendations"], list):
                all_recommendations.extend(result["recommendations"])
            else:
                all_recommendations.append(str(result["recommendations"]))
        
        if "preventive_measures" in result:
            if isinstance(result["preventive_measures"], list):
                all_recommendations.extend(result["preventive_measures"])
            else:
                all_recommendations.append(str(result["preventive_measures"]))
    
    # Determine consensus risk
    if risk_votes["High"] > risk_votes["Low"] and risk_votes["High"] > risk_votes["Moderate"]:
        combined["consensus_risk"] = "High"
    elif risk_votes["Low"] > risk_votes["Moderate"]:
        combined["consensus_risk"] = "Low"
    else:
        combined["consensus_risk"] = "Moderate"
    
    # Calculate confidence based on agreement
    total_votes = sum(risk_votes.values())
    if total_votes > 0:
        max_votes = max(risk_votes.values())
        combined["confidence"] = max_votes / total_votes
    
    # Consolidate insights and recommendations
    combined["key_insights"] = list(set(all_insights))[:5]  # Top 5 unique insights
    combined["recommendations"] = list(set(all_recommendations))[:5]  # Top 5 unique recommendations
    
    return combined

@ai_enhancement_bp.route('/medicine-interaction-check', methods=['POST'])
def medicine_interaction_check():
    """Check for drug interactions using AI."""
    try:
        data = request.get_json()
        medications = data.get('medications', [])
        
        if not medications:
            return jsonify({"error": "medications are required"}), 400
        
        openai_key = get_openai_client()
        if not openai_key:
            return jsonify({"error": "OpenAI API key not configured"}), 503
            
        fda_warnings = []
        for med in medications:
            warning = get_fda_drug_warnings(med)
            if warning:
                fda_warnings.append(warning)
                
        fda_text = "\n\n".join(fda_warnings)
        
        prompt = f"""
        As a pharmaceutical AI assistant, analyze the following medications and format the official FDA label warnings if provided:
        
        Medications: {', '.join(medications)}
        
        Official FDA Label Data:
        {fda_text}
        
        Please provide:
        1. List of potential drug interactions
        2. Severity levels (Mild/Moderate/Severe)
        3. Recommendations for monitoring
        4. When to contact healthcare provider
        
        Format as JSON with keys: interactions, severity_levels, monitoring_recommendations, when_to_contact_provider
        """
        
        model_name = "mistralai/mistral-7b-instruct:free" if os.getenv("OPENROUTER_API_KEY") else "gpt-4o-mini"
        
        req_body = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a pharmaceutical AI assistant. Always respond in valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 400,
            "temperature": 0.2
        }
        
        api_url = "https://openrouter.ai/api/v1/chat/completions" if os.getenv("OPENROUTER_API_KEY") else "https://api.openai.com/v1/chat/completions"
        req = urllib.request.Request(
            api_url,
            data=json.dumps(req_body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_key}",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "Healthcare AI Platform"
            },
            method="POST",
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        
        try:
            choices = body.get("choices", [])
            if choices and len(choices) > 0:
                message = choices[0].get("message", {})
                content = (message.get("content") or "").strip()
                
                try:
                    return json.loads(content)
                except:
                    return {"analysis": content}
            else:
                return {"error": "No response from OpenAI"}
        except Exception as e:
            return {"error": f"Failed to parse response: {str(e)}"}
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Drug interaction check failed: {str(e)}"}), 500
