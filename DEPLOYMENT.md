# 🚀 Deploying UnityAid on Streamlit Community Cloud

This guide walks you through deploying UnityAid on Streamlit Community Cloud for free public access.

## 📋 Prerequisites

1. **GitHub Repository**: Your UnityAid code must be in a public GitHub repository
2. **Google API Key**: For AI-powered priority classification and title generation
3. **Streamlit Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)

## 🔧 Pre-Deployment Setup

### 1. Ensure Repository is Ready

Your repository should contain these key files:
- ✅ `app_streamlit.py` (main application)
- ✅ `requirements.txt` (dependencies)
- ✅ `.streamlit/config.toml` (theme configuration)
- ✅ `packages.txt` (system packages if needed)
- ✅ `README.md` (documentation)

### 2. Get Google API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Generative Language API**
4. Go to **APIs & Services → Credentials**
5. Click **Create Credentials → API Key**
6. **Important**: Restrict the API key to your domain for security

## 🌐 Deployment Steps

### 1. Deploy to Streamlit Cloud

1. **Visit Streamlit Cloud**: Go to [share.streamlit.io](https://share.streamlit.io)

2. **Connect GitHub**: Sign in and connect your GitHub account

3. **Create New App**:
   - Repository: `your-username/UnityAid`
   - Branch: `main`
   - Main file path: `app_streamlit.py`
   - App URL: Choose a memorable name like `unityaid-emergency-response`

4. **Click "Deploy"**

### 2. Configure Secrets

After deployment starts, configure your secrets:

1. **Click "Settings"** on your app dashboard
2. **Go to "Secrets"** tab
3. **Add the following secrets**:

```toml
# Google API Configuration
GOOGLE_API_KEY = "your_google_api_key_here"
GOOGLE_MODEL = "gemini-1.5-flash"

# Feature Configuration
PRIORITIZER_CONFIDENCE_THRESHOLD = "0.7"
ENABLE_ENHANCED_CONTEXT = "true"
ENABLE_VISUAL_FEEDBACK = "true"
DEBUG_MODE = "false"
```

4. **Click "Save"**

### 3. Initial Deployment

The first deployment may take 5-10 minutes as Streamlit Cloud:
- Installs Python dependencies
- Downloads spaCy language model
- Sets up the environment

## ✅ Post-Deployment Verification

### 1. Test Core Features

Visit your deployed app and verify:

- ✅ **Dashboard loads** without errors
- ✅ **Maps display** correctly (Folium integration)
- ✅ **AI Agent tab** accepts input and processes tickets
- ✅ **Manual Ticket tab** creates tickets successfully
- ✅ **Location extraction** works with text descriptions
- ✅ **Ticket viewing** displays created tickets

### 2. Test AI Features

1. **Test AI Priority Classification**:
   - Enter: "Someone is unconscious and not breathing"
   - Should get high priority (4-5) with AI confidence

2. **Test Location Extraction**:
   - Enter: "CVS at 107th Street and Doral Boulevard"
   - Should extract coordinates and show confidence

3. **Test Conversational AI** (if PrioritizerAgent is configured):
   - Enter vague description: "Someone needs help"
   - Should ask clarifying questions

## 🔧 Troubleshooting

### Common Issues:

**1. "Import Error: PrioritizerAgent"**
- **Cause**: PrioritizerAgent module not properly configured
- **Solution**: The app falls back to heuristic classification - this is expected

**2. "spaCy Model Not Found"**
- **Cause**: English language model not installed
- **Solution**: Check requirements.txt includes the spaCy model URL

**3. "Google API Error"**
- **Cause**: Invalid or missing API key
- **Solution**: Verify GOOGLE_API_KEY in Streamlit secrets

**4. "Map Not Loading"**
- **Cause**: JavaScript/Folium integration issue
- **Solution**: Refresh page, check browser console

### Performance Optimization:

1. **Use Caching**: The app uses `@st.cache_data` for expensive operations
2. **Monitor Usage**: Check Streamlit Cloud usage dashboard
3. **Rate Limiting**: Be mindful of Google API rate limits

## 🌍 Going Live

### 1. Share Your App

Your app will be available at:
```
https://your-app-name.streamlit.app
```

### 2. Custom Domain (Optional)

For custom domains:
1. Upgrade to Streamlit Cloud Pro
2. Configure DNS settings
3. Update domain in settings

### 3. Monitoring

- **Streamlit Cloud Dashboard**: Monitor app health and usage
- **Google Cloud Console**: Monitor API usage and costs
- **GitHub**: Track code changes and issues

## 🔒 Security Best Practices

1. **API Key Security**:
   - Never commit API keys to repository
   - Use Streamlit secrets for sensitive data
   - Restrict API key to your domain

2. **Repository Security**:
   - Keep `.env` files in `.gitignore`
   - Regular security updates
   - Monitor for vulnerabilities

## 📊 Scaling Considerations

**Current Setup**: Suitable for development and small teams

**For Production Use**:
- Consider upgrading to Streamlit Cloud Pro
- Implement database persistence
- Add user authentication
- Set up monitoring and logging
- Consider load balancing for high traffic

## 🆘 Support

If you encounter issues:

1. **Check Logs**: Streamlit Cloud app logs
2. **GitHub Issues**: Report bugs in repository
3. **Community**: Streamlit Community Forum
4. **Documentation**: UnityAid README.md

---

**🎉 Congratulations!** Your UnityAid emergency response system is now live and helping coordinate disaster response efforts worldwide!