# Streamlit Community Cloud Deployment Guide

A complete step-by-step guide to deploying your Streamlit app to the cloud **for free**!

> **Where this fits:** this is **step 5a** of the tutorial — use it when your
> app is a single Streamlit script with no separate backend. If your app has a
> FastAPI (or other) backend service, use **[RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)** instead.
> Need to persist user data? See **[DATABASE_GUIDE.md](DATABASE_GUIDE.md)** —
> writing to a file on Streamlit Community Cloud does NOT survive redeploys.
> New here? Start at the [README](README.md).

## 🌐 What is Streamlit Cloud?

**Streamlit Cloud** (previously Streamlit Sharing) is a free platform for deploying, managing, and sharing Streamlit apps. It's the easiest way to put your app online and share it with the world.

### Features

- ✅ **Free** - No credit card required
- ✅ **Easy** - Deploy in minutes with a few clicks
- ✅ **Automatic Updates** - Redeploys when you push to GitHub
- ✅ **Custom URLs** - Get a unique URL for your app
- ✅ **Secrets Management** - Securely store API keys and passwords
- ✅ **Resource Limits** - 1 GB RAM, reasonable for most apps

---

## 🎯 Prerequisites

Before you start, you'll need:

1. **A Streamlit app** - Your `app.py` file
2. **GitHub account** - Free at [github.com](https://github.com)
3. **Streamlit Cloud account** - Free at [share.streamlit.io](https://share.streamlit.io)

---

## 📋 Step-by-Step Deployment

### Step 1: Prepare Your App Files

Your project folder should contain at minimum:

```
my-streamlit-app/
├── app.py                 # Your main Streamlit app
├── requirements.txt       # Python dependencies
└── README.md             # Project description (optional but recommended)
```

#### 1.1 Create `requirements.txt`

List all Python packages your app needs:

```txt
streamlit>=1.40.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.14.0
```

**How to generate automatically:**

```bash
# If you're using a virtual environment
pip freeze > requirements.txt

# Or manually list only what you need (recommended)
# This keeps your deployment faster and cleaner
```

#### 1.2 Optional: Create `.streamlit/config.toml`

For custom configuration (colors, theme, etc.):

```bash
mkdir .streamlit
```

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#F63366"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
```

#### 1.3 Optional: Add `.gitignore`

Prevent committing unnecessary files:

```
# Create .gitignore file
__pycache__/
*.py[cod]
*$py.class
.DS_Store
.streamlit/secrets.toml
*.csv
*.xlsx
venv/
env/
```

---

### Step 2: Push to GitHub

#### 2.1 Initialize Git Repository (if not already)

```bash
cd my-streamlit-app
git init
```

#### 2.2 Add and Commit Files

```bash
# Add all files
git add .

# Commit
git commit -m "Initial commit: My Streamlit app"
```

#### 2.3 Create GitHub Repository

1. Go to [github.com](https://github.com)
2. Click the **"+"** icon → **"New repository"**
3. Name your repository (e.g., `my-streamlit-app`)
4. Choose **Public** (required for free Streamlit Cloud)
5. **Don't** initialize with README (you already have files)
6. Click **"Create repository"**

#### 2.4 Push to GitHub

GitHub will show you commands like:

```bash
git remote add origin https://github.com/YOUR_USERNAME/my-streamlit-app.git
git branch -M main
git push -u origin main
```

Run these commands in your terminal.

**Verify:** Visit your GitHub repository to confirm files are uploaded.

---

### Step 3: Deploy to Streamlit Cloud

#### 3.1 Sign Up for Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign up"** or **"Continue with GitHub"**
3. Authorize Streamlit to access your GitHub account

#### 3.2 Deploy Your App

1. Click **"New app"** button
2. You'll see a form with three fields:

   ```
   Repository:     YOUR_USERNAME/my-streamlit-app
   Branch:         main
   Main file path: app.py
   ```

3. **Advanced settings** (optional):
   - **Python version**: Choose your Python version (default is usually fine)
   - **Secrets**: Add API keys or passwords (see below)

4. Click **"Deploy!"**

#### 3.3 Wait for Deployment

- Streamlit Cloud will:
  - Clone your repository
  - Install dependencies from `requirements.txt`
  - Start your app
  - Provide a public URL

- This usually takes **2-5 minutes**
- You'll see a build log showing progress

#### 3.4 Access Your App

Once deployed, you'll get a URL like:

```
https://YOUR_USERNAME-my-streamlit-app-main-app-xyz123.streamlit.app
```

🎉 **Your app is now live and accessible to anyone!**

---

## 🔐 Managing Secrets

For API keys, passwords, or sensitive data:

### In Your App Code

```python
import streamlit as st

# Access secrets
api_key = st.secrets["api_key"]
db_password = st.secrets["database"]["password"]

# Use in your app
response = call_api(api_key)
```

### In Streamlit Cloud Dashboard

1. Go to your app dashboard at [share.streamlit.io](https://share.streamlit.io)
2. Click on your app
3. Click **"Settings"** → **"Secrets"**
4. Add your secrets in TOML format:

```toml
# Simple secrets
api_key = "your-api-key-here"
openai_key = "sk-..."

# Nested secrets
[database]
host = "db.example.com"
username = "admin"
password = "secret123"

[aws]
access_key = "AKIA..."
secret_key = "wJalr..."
```

5. Click **"Save"**
6. Your app will automatically restart with the secrets available

### Local Development

For local testing, create `.streamlit/secrets.toml`:

```toml
api_key = "your-test-key"
```

**Important:** Add this to `.gitignore` so it's never committed!

---

## 🔄 Updating Your App

### Automatic Updates

Streamlit Cloud automatically redeploys when you push to GitHub:

```bash
# Make changes to your app
# Edit app.py

# Commit and push
git add app.py
git commit -m "Update: Added new feature"
git push

# Streamlit Cloud will automatically detect the change and redeploy!
```

### Manual Reboot

If needed, you can manually reboot from the dashboard:

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click on your app
3. Click **"︙"** (three dots) → **"Reboot app"**

---

## 🎨 Custom Domain (Optional)

Streamlit Cloud provides a default URL, but you can use your own domain:

1. **Get a custom domain** (from GoDaddy, Namecheap, etc.)
2. In Streamlit Cloud dashboard:
   - Go to app settings
   - Click **"Custom domain"**
   - Follow instructions to add DNS records
3. Add your domain (e.g., `myapp.com`)

**Note:** Custom domains may require a paid plan in the future.

---

## 📊 Monitoring Your App

### App Metrics

Streamlit Cloud provides basic metrics:

1. Go to your app dashboard
2. Click on your app
3. View:
   - **Active users**
   - **Resource usage** (CPU, Memory)
   - **Error logs**

### Logs

View real-time logs:

1. Click **"Manage app"** → **"Logs"**
2. See `print()` statements and errors
3. Use for debugging

### Analytics (Optional)

Add Google Analytics or other tracking:

```python
import streamlit as st
import streamlit.components.v1 as components

# Google Analytics
ga_code = """
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
"""

components.html(ga_code, height=0)
```

---

## 🐛 Troubleshooting

### App Won't Deploy

**Error: "No module named 'X'"**

```bash
# Add missing package to requirements.txt
echo "package-name>=1.0.0" >> requirements.txt
git add requirements.txt
git commit -m "Add missing dependency"
git push
```

**Error: "Memory limit exceeded"**

- Streamlit Cloud free tier has 1 GB RAM
- Optimize your app:
  - Use `@st.cache_data` for data
  - Load smaller datasets
  - Reduce memory-heavy operations

**Error: "Build failed"**

- Check build logs for specific errors
- Ensure `requirements.txt` has correct package names
- Try pinning specific versions (e.g., `pandas==2.0.0`)

### App is Slow

**Optimization tips:**

```python
import streamlit as st

# 1. Cache expensive operations
@st.cache_data
def load_data():
    return pd.read_csv('large_file.csv')

# 2. Use session state for persistence
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# 3. Limit data displayed
st.dataframe(df.head(100))  # Instead of entire dataset

# 4. Use lightweight libraries
# Consider alternatives to heavy libraries
```

### App Shows Old Version

1. Check if GitHub has latest code
2. Manually reboot app from dashboard
3. Clear browser cache
4. Check if deployment is still in progress

---

## 💰 Pricing & Limits

### Free Tier (Streamlit Community Cloud)

- **Cost**: Free
- **Public apps**: Supported (repo must be public)
- **Private apps**: Limited; see current terms on streamlit.io
- **Resources**: ~1 GB RAM, shared CPU (subject to change — check docs)
- **Sleep behavior**: Apps may go to sleep after inactivity and wake on next visit

> Streamlit Community Cloud's exact limits change over time. Always check
> [docs.streamlit.io/deploy/streamlit-community-cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud)
> for the latest.

### Paid Tiers (Streamlit Cloud Teams/Enterprise)

For private apps or more resources:

- Visit [streamlit.io/cloud](https://streamlit.io/cloud) for pricing
- Features:
  - Private repositories
  - More resources
  - Team collaboration
  - SSO authentication
  - Priority support

---

## 📱 Best Practices for Deployment

### 1. Optimize for Performance

```python
# ✅ Good: Cache data loading
@st.cache_data
def load_data():
    return pd.read_csv('data.csv')

# ❌ Bad: Load data every time
df = pd.read_csv('data.csv')  # Runs on every interaction!
```

### 2. Handle Errors Gracefully

```python
import streamlit as st

try:
    data = load_external_data()
    st.dataframe(data)
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please try again later or contact support.")
```

### 3. Add Loading Indicators

```python
import streamlit as st
import time

with st.spinner('Loading data...'):
    data = expensive_computation()
    time.sleep(2)

st.success('Done!')
```

### 4. Use Secrets for Sensitive Data

```python
# ❌ Bad: Hardcoded credentials
api_key = "sk-1234567890abcdef"

# ✅ Good: Use secrets
api_key = st.secrets["api_key"]
```

### 5. Add App Metadata

```python
import streamlit as st

st.set_page_config(
    page_title="My Awesome App",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.example.com/help',
        'Report a bug': "https://www.example.com/bug",
        'About': "# My Awesome App v1.0\nBuilt with Streamlit!"
    }
)
```

### 6. Version Your Dependencies

```txt
# ✅ Good: Specific versions
streamlit==1.40.0
pandas==2.2.3
numpy==2.1.3

# ⚠️ Okay: Minimum versions
streamlit>=1.40.0
pandas>=2.0.0

# ❌ Bad: No versions (can break unexpectedly)
streamlit
pandas
```

---

## 🎯 Example: Complete Deployment Workflow

Let's deploy a simple app from scratch:

### 1. Create Your App

**File: `app.py`**
```python
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Random Data Generator", page_icon="🎲")

st.title("🎲 Random Data Generator")
st.write("Generate random datasets for testing")

n_rows = st.slider("Number of rows", 10, 1000, 100)
n_cols = st.slider("Number of columns", 1, 10, 3)

if st.button("Generate Data"):
    data = np.random.randn(n_rows, n_cols)
    df = pd.DataFrame(data, columns=[f'Column_{i+1}' for i in range(n_cols)])

    st.dataframe(df)
    st.line_chart(df)

    csv = df.to_csv(index=False)
    st.download_button("Download CSV", csv, "data.csv", "text/csv")
```

### 2. Create Requirements

**File: `requirements.txt`**
```txt
streamlit>=1.40.0
pandas>=2.0.0
numpy>=1.24.0
```

### 3. Create README

**File: `README.md`**
```markdown
# Random Data Generator

A simple Streamlit app to generate random datasets for testing.

## Features
- Adjustable rows and columns
- Data visualization
- CSV download

## Live Demo
[Try it here](https://your-app-url.streamlit.app)
```

### 4. Deploy

```bash
# Initialize git
git init

# Add files
git add .

# Commit
git commit -m "Initial commit: Random data generator"

# Create GitHub repo and push
gh repo create my-random-data-app --public --source=. --remote=origin --push

# Or manually:
# 1. Create repo on GitHub
# 2. git remote add origin https://github.com/YOUR_USERNAME/my-random-data-app.git
# 3. git push -u origin main
```

### 5. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository
4. Click "Deploy"
5. Wait 2-3 minutes
6. Share your URL! 🎉

---

## 🔗 Useful Links

- **Streamlit Cloud**: [share.streamlit.io](https://share.streamlit.io)
- **Documentation**: [docs.streamlit.io/streamlit-cloud](https://docs.streamlit.io/streamlit-cloud)
- **Community Forum**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub**: [github.com/streamlit/streamlit](https://github.com/streamlit/streamlit)
- **Gallery**: [streamlit.io/gallery](https://streamlit.io/gallery)

---

## ✅ Deployment Checklist

Before deploying, make sure you have:

- [ ] Working Streamlit app (`app.py`)
- [ ] `requirements.txt` with all dependencies
- [ ] `.gitignore` to exclude sensitive files
- [ ] `README.md` with project description
- [ ] Code pushed to **public** GitHub repository
- [ ] No hardcoded secrets (use `st.secrets` instead)
- [ ] Tested app locally with `streamlit run app.py`
- [ ] Optimized with caching where appropriate
- [ ] Error handling for user inputs
- [ ] Loading indicators for slow operations

---

## 🎉 Congratulations!

You now know how to deploy Streamlit apps to the cloud!

**Next steps:**
1. Build something awesome
2. Deploy it
3. Share with the world
4. Get feedback
5. Iterate and improve

**Happy deploying! 🚀**
