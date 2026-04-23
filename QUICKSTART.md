# Streamlit Quick Start Guide

Get started with Streamlit in 5 minutes!

> **Where this fits:** this is **step 1** of the tutorial. After running your
> first app here, head back to the main [README.md](README.md) for the
> full walkthrough of concepts, widgets, layouts, caching, and state.

## 🚀 Installation

```bash
pip install streamlit
```

Verify installation:
```bash
streamlit --version
```

---

## 📝 Create Your First App

### Step 1: Create a Python File

Create `hello.py`:

```python
import streamlit as st

st.title("Hello, Streamlit! 👋")

name = st.text_input("What's your name?")

if name:
    st.write(f"Hello, {name}!")
    st.balloons()
```

### Step 2: Run Your App

```bash
streamlit run hello.py
```

Your browser will automatically open to `http://localhost:8501`

**That's it! You've created your first Streamlit app!** 🎉

---

## 🎯 Try the Examples

We've created 5 example apps for you:

### 1. Hello World (Simplest)
```bash
cd examples
streamlit run 01_hello_world.py
```

### 2. Basic Widgets
```bash
streamlit run 02_basic_widgets.py
```

### 3. Data Visualization
```bash
streamlit run 03_data_visualization.py
```

### 4. Interactive App (BMI Calculator)
```bash
streamlit run 04_interactive_app.py
```

### 5. Advanced Features
```bash
streamlit run 05_advanced_features.py
```

---

## 🛠️ Start Your Own Project

### Option 1: Use the Template

```bash
cd my_first_app
pip install -r requirements.txt
streamlit run app.py
```

Then modify `app.py` to build your own app!

### Option 2: Start from Scratch

1. Create a new directory:
   ```bash
   mkdir my_streamlit_app
   cd my_streamlit_app
   ```

2. Create `app.py`:
   ```python
   import streamlit as st

   st.title("My App")
   st.write("Hello, World!")
   ```

3. Run it:
   ```bash
   streamlit run app.py
   ```

---

## 📚 Common Commands

```bash
# Run an app
streamlit run app.py

# Run on a different port
streamlit run app.py --server.port 8502

# Disable file watching (for production)
streamlit run app.py --server.fileWatcherType none

# Get help
streamlit --help
```

---

## 🎨 Essential Concepts

### 1. Display Text

```python
import streamlit as st

st.title("Title")
st.header("Header")
st.write("Anything")
st.markdown("**Bold** and *italic*")
```

### 2. Add Widgets

```python
# User input
name = st.text_input("Name")
age = st.slider("Age", 0, 100, 25)
option = st.selectbox("Choose", ["A", "B", "C"])

# Button
if st.button("Click me"):
    st.write("Button clicked!")
```

### 3. Display Data

```python
import pandas as pd

df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6]
})

st.dataframe(df)  # Interactive table
st.line_chart(df) # Line chart
```

### 4. Layout

```python
# Columns
col1, col2 = st.columns(2)
col1.write("Column 1")
col2.write("Column 2")

# Sidebar
st.sidebar.title("Sidebar")
option = st.sidebar.selectbox("Choose", ["A", "B"])

# Tabs
tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])
tab1.write("Content 1")
tab2.write("Content 2")
```

### 5. Caching (Performance!)

```python
@st.cache_data
def load_data():
    # This only runs once!
    return pd.read_csv("large_file.csv")

df = load_data()  # Fast after first load
```

---

## 🌐 Deploy to Cloud (Free!)

Pick one of two paths depending on what you're building:

### Path A — Streamlit-only app → Streamlit Community Cloud

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. Go to [share.streamlit.io](https://share.streamlit.io), click **New app**,
   select your repo, click **Deploy**.

Full walkthrough: **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**.

### Path B — Streamlit + FastAPI backend → Render.com

For apps with a separate Python backend (API, ML model server, DB). You'll
deploy two services and wire them together with an environment variable.

Full walkthrough: **[RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)**.

---

## 🆘 Troubleshooting

### App won't start

```bash
# Check if Streamlit is installed
pip list | grep streamlit

# Reinstall if needed
pip install --upgrade streamlit
```

### Port already in use

```bash
# Use a different port
streamlit run app.py --server.port 8502
```

### Changes not appearing

- Streamlit auto-reloads on save
- If not working, click "Always rerun" in browser
- Or press 'R' in the terminal

### Module not found

```bash
# Install missing package
pip install package_name
```

---

## 📖 Next Steps

1. ✅ **Read**: [README.md](README.md) - Full tutorial
2. 🚀 **Try**: Run the example apps
3. 🎨 **Build**: Create your own app using the template
4. 🌐 **Deploy**: Put your app online
5. 📚 **Learn**: Check out the resources

---

## 🔗 Quick Links

- **Full tutorial**: [README.md](README.md)
- **Deploy (Streamlit only)**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Deploy (Streamlit + FastAPI on Render)**: [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)
- **Cheat Sheet**: [resources/cheatsheet.md](resources/cheatsheet.md)
- **Best Practices**: [resources/best_practices.md](resources/best_practices.md)
- **Official Docs**: [docs.streamlit.io](https://docs.streamlit.io)

---

## 💡 Pro Tips

1. **Use `st.write()`** - it's magic and displays almost anything
2. **Cache everything expensive** - use `@st.cache_data`
3. **Organize with tabs** - great for multi-view apps
4. **Test early and often** - run your app as you develop
5. **Read the docs** - Streamlit's docs are excellent

---

**Happy Streamlit-ing! 🎈**

Need help? Check the [Streamlit Forum](https://discuss.streamlit.io) or [Documentation](https://docs.streamlit.io)
