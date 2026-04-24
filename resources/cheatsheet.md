# Streamlit Cheatsheet

Quick reference for common Streamlit commands.

## 📄 Text & Display

```python
import streamlit as st

# Text elements
st.title("App Title")
st.header("Header")
st.subheader("Subheader")
st.text("Fixed width text")
st.markdown("**Bold** and *italic*")
st.caption("Small caption text")
st.code("print('Hello')", language='python')
st.latex(r"\alpha + \beta = \gamma")

# Display data
st.write("Anything")  # Magic function - displays anything
st.json({"key": "value"})
st.metric("Metric", 42, delta=5)
```

## 📊 Data Display

```python
import pandas as pd

df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

st.dataframe(df)           # Interactive table
st.table(df)               # Static table
st.json({"key": "value"})  # JSON
```

## 📈 Charts

```python
# Built-in charts
st.line_chart(df)
st.area_chart(df)
st.bar_chart(df)
st.map(df_with_lat_lon)

# Plotly charts
import plotly.express as px
fig = px.scatter(df, x='A', y='B')
st.plotly_chart(fig)

# Matplotlib/Seaborn
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([1, 2, 3])
st.pyplot(fig)

# Altair
import altair as alt
chart = alt.Chart(df).mark_point().encode(x='A', y='B')
st.altair_chart(chart)
```

## 🎛️ Input Widgets

```python
# Text input
name = st.text_input("Name", placeholder="Enter name")
message = st.text_area("Message", height=100)
password = st.text_input("Password", type="password")

# Number input
number = st.number_input("Number", min_value=0, max_value=100, value=50)
slider = st.slider("Slider", 0, 100, 50)
slider_range = st.slider("Range", 0, 100, (25, 75))

# Date/Time
date = st.date_input("Date")
time = st.time_input("Time")

# Selection
option = st.selectbox("Choose", ["A", "B", "C"])
options = st.multiselect("Choose multiple", ["A", "B", "C"])
radio = st.radio("Pick one", ["A", "B", "C"])

# Boolean
checkbox = st.checkbox("Agree")
toggle = st.toggle("Enable")

# File upload
file = st.file_uploader("Upload", type=['csv', 'txt'])

# Color picker
color = st.color_picker("Color", "#00f900")

# Buttons
if st.button("Click me"):
    st.write("Clicked!")

if st.download_button("Download", data="content", file_name="file.txt"):
    st.write("Downloaded!")
```

## 📐 Layout

```python
# Columns
col1, col2, col3 = st.columns(3)
col1.write("Column 1")
col2.write("Column 2")
col3.write("Column 3")

# Or with context manager
with col1:
    st.write("In column 1")

# Tabs
tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])
with tab1:
    st.write("Tab 1 content")

# Sidebar
st.sidebar.title("Sidebar")
st.sidebar.button("Button")

# Expander
with st.expander("Expand me"):
    st.write("Hidden content")

# Container
with st.container():
    st.write("In container")

# Empty placeholder
placeholder = st.empty()
placeholder.text("Initial")
# Later...
placeholder.text("Updated")
```

## 🗄️ Caching

```python
# Cache data
@st.cache_data
def load_data():
    return pd.read_csv("data.csv")

# Cache resources (models, connections)
@st.cache_resource
def load_model():
    return load_ml_model()

# Clear cache
st.cache_data.clear()
st.cache_resource.clear()
```

## 💾 Session State

```python
# Initialize
if 'counter' not in st.session_state:
    st.session_state.counter = 0

# Read
count = st.session_state.counter

# Write
st.session_state.counter += 1

# Delete
del st.session_state.counter

# Widget with key (auto-stored in session state)
name = st.text_input("Name", key="user_name")
# Access with: st.session_state.user_name
```

## 🎨 Status & Messages

```python
# Status messages
st.success("Success!")
st.info("Info")
st.warning("Warning")
st.error("Error")
st.exception(Exception("Error"))

# Progress
progress = st.progress(0)
progress.progress(50)  # 0-100

# Spinner
with st.spinner("Loading..."):
    # Expensive operation
    time.sleep(2)

# Balloons/Snow
st.balloons()
st.snow()
```

## ⚙️ Configuration

```python
# Page config (must be first Streamlit command)
st.set_page_config(
    page_title="App Title",
    page_icon="🎯",
    layout="wide",  # or "centered"
    initial_sidebar_state="expanded"  # or "collapsed"
)
```

## 🔐 Secrets

```python
# Access secrets from .streamlit/secrets.toml
api_key = st.secrets["api_key"]
db_password = st.secrets["database"]["password"]
```

## 🎮 Control Flow

```python
# Stop execution
st.stop()

# Rerun app
st.rerun()

# Form (submit button triggers rerun)
with st.form("my_form"):
    name = st.text_input("Name")
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write(f"Hello {name}")
```

## 📱 Media

```python
# Images
st.image("path/to/image.jpg", caption="Caption", width=300)

# Audio
st.audio("path/to/audio.mp3")

# Video
st.video("path/to/video.mp4")
```

## 🔧 Utilities

```python
# Echo code
with st.echo():
    # This code will be displayed
    x = 10

# Help
st.help(pd.DataFrame)

# Divider
st.divider()
```

## 🗄 Databases

Full walkthrough: **[DATABASE_GUIDE.md](../DATABASE_GUIDE.md)**. Cheat-version:

```python
import sqlite3, os
import psycopg
import streamlit as st

# --- SQLite: read-only (bundled .db) -----------------------------------------
@st.cache_resource
def ro_conn():
    return sqlite3.connect("file:data.db?mode=ro", uri=True, check_same_thread=False)

# --- SQLite: persistent local file -------------------------------------------
@st.cache_resource
def sqlite_conn():
    conn = sqlite3.connect("app.db", check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, body TEXT)")
    return conn

# --- Postgres (Supabase / Neon / Render / etc.) ------------------------------
@st.cache_resource
def pg_conn():
    url = st.secrets.get("supabase", {}).get("DATABASE_URL") or os.environ["DATABASE_URL"]
    return psycopg.connect(url, sslmode="require", autocommit=True)

# Always parameterize queries — never f-strings.
# SQLite: ? placeholders.    Postgres: %s placeholders.
```

⚠️ On **Streamlit Community Cloud** and **Render free tier**, the filesystem
is ephemeral — SQLite files written at runtime vanish on redeploy. Use
Postgres (e.g. Supabase) for real persistence.

## 📦 Advanced

```python
# Custom components
import streamlit.components.v1 as components
components.html("<h1>Custom HTML</h1>")

# Custom CSS
st.markdown("""
    <style>
    .custom-class { color: red; }
    </style>
""", unsafe_allow_html=True)

# Query parameters
query_params = st.query_params
st.query_params.update({"key": "value"})
```

## 💡 Quick Tips

1. **Import convention**: `import streamlit as st`
2. **Automatic rerun**: App reruns on any widget interaction
3. **Top-to-bottom**: Code executes from top to bottom on each rerun
4. **Cache wisely**: Use caching for expensive operations
5. **Session state**: Persist data across reruns
6. **Sidebar**: Perfect for controls and navigation

## 📚 Common Patterns

### Loading Data Once

```python
@st.cache_data
def get_data():
    return pd.read_csv("data.csv")

df = get_data()  # Only loads once
```

### Stateful Counter

```python
if 'count' not in st.session_state:
    st.session_state.count = 0

if st.button("Increment"):
    st.session_state.count += 1

st.write(f"Count: {st.session_state.count}")
```

### Conditional Display

```python
option = st.radio("Choose", ["Show Chart", "Show Table"])

if option == "Show Chart":
    st.line_chart(data)
else:
    st.table(data)
```

### Form Submission

```python
with st.form("entry_form"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0)
    submitted = st.form_submit_button("Submit")

    if submitted:
        st.write(f"{name} is {age} years old")
```

---

**More help:**
- [Official Cheat Sheet](https://docs.streamlit.io/library/cheatsheet)
- [API Reference](https://docs.streamlit.io/library/api-reference)
- [Streamlit Gallery](https://streamlit.io/gallery)
