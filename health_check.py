"""
Health check script for UnityAid deployment.
Run this to verify all components are working properly.
"""

import streamlit as st
import sys
import importlib.util

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'streamlit',
        'folium',
        'streamlit_folium', 
        'geopy',
        'spacy',
        'google.generativeai',
        'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'streamlit_folium':
                import streamlit_folium
            elif package == 'google.generativeai':
                import google.generativeai
            else:
                __import__(package)
            st.success(f"✅ {package} - OK")
        except ImportError:
            st.error(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_spacy_model():
    """Check if spaCy English model is available."""
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        st.success("✅ spaCy English model - OK")
        return True
    except OSError:
        st.error("❌ spaCy English model - MISSING")
        st.info("Run: python -m spacy download en_core_web_sm")
        return False

def check_api_keys():
    """Check API key configuration."""
    try:
        from app_streamlit import get_api_key
        api_key = get_api_key("GOOGLE_API_KEY")
        if api_key:
            st.success("✅ Google API Key - Configured")
            return True
        else:
            st.warning("⚠️ Google API Key - Not configured (app will use fallbacks)")
            return False
    except Exception as e:
        st.error(f"❌ API Key check failed: {e}")
        return False

def main():
    st.title("🆘 UnityAid Health Check")
    st.write("Verifying deployment readiness...")
    
    st.header("📦 Dependency Check")
    deps_ok = check_dependencies()
    
    st.header("🔤 spaCy Model Check") 
    spacy_ok = check_spacy_model()
    
    st.header("🔑 API Configuration Check")
    api_ok = check_api_keys()
    
    st.header("📊 Overall Status")
    if deps_ok and spacy_ok:
        st.success("🎉 All systems ready! UnityAid is deployment-ready.")
        if not api_ok:
            st.info("ℹ️ Google API not configured - some features will use fallbacks")
    else:
        st.error("❌ Issues found. Please resolve before deploying.")
        
    st.header("🚀 Next Steps")
    st.write("If all checks pass:")
    st.write("1. Push to GitHub")
    st.write("2. Deploy on Streamlit Cloud")
    st.write("3. Configure secrets in deployment settings")
    st.write("4. Test live application")

if __name__ == "__main__":
    main()