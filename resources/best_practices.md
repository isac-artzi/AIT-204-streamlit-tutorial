# Streamlit Best Practices

Guidelines for building better Streamlit applications.

## 🎯 Performance

### 1. Use Caching Effectively

**DO:**
```python
@st.cache_data
def load_data():
    """Expensive operation - cache it!"""
    return pd.read_csv('large_file.csv')

@st.cache_resource
def load_model():
    """Load ML model once"""
    return joblib.load('model.pkl')
```

**DON'T:**
```python
# This loads the file on EVERY interaction!
df = pd.read_csv('large_file.csv')  # ❌ Slow!
```

### 2. Limit Data Display

**DO:**
```python
# Show only what's needed
st.dataframe(df.head(100))

# Or with pagination
page = st.number_input('Page', 1, len(df)//100)
st.dataframe(df.iloc[(page-1)*100:page*100])
```

**DON'T:**
```python
# Display entire huge dataset
st.dataframe(df)  # ❌ Slow for large data!
```

### 3. Use Session State Wisely

**DO:**
```python
# Initialize once
if 'expensive_result' not in st.session_state:
    st.session_state.expensive_result = expensive_computation()

# Reuse
result = st.session_state.expensive_result
```

**DON'T:**
```python
# Recompute every time
result = expensive_computation()  # ❌ Runs on every interaction!
```

---

## 🎨 User Experience

### 1. Provide Clear Instructions

**DO:**
```python
st.title("Data Analysis Tool")
st.markdown("""
### How to use:
1. Upload your CSV file below
2. Select columns to analyze
3. View results in the tabs
""")
```

**DON'T:**
```python
st.title("Tool")
# No explanation - users are confused ❌
```

### 2. Add Loading Indicators

**DO:**
```python
with st.spinner("Loading data..."):
    data = load_large_dataset()

st.success("Data loaded successfully!")
```

**DON'T:**
```python
data = load_large_dataset()  # ❌ App freezes with no feedback
```

### 3. Handle Errors Gracefully

**DO:**
```python
try:
    data = process_user_input(input_data)
    st.dataframe(data)
except ValueError as e:
    st.error(f"Invalid input: {str(e)}")
    st.info("Please check your data format and try again.")
except Exception as e:
    st.error("An unexpected error occurred.")
    st.exception(e)
```

**DON'T:**
```python
data = process_user_input(input_data)  # ❌ Crashes on bad input
```

### 4. Use Appropriate Widgets

**DO:**
```python
# For few options
choice = st.radio("Choose", ["A", "B", "C"])

# For many options
choice = st.selectbox("Choose", list(range(100)))

# For range selection
range_val = st.slider("Range", 0, 100, (20, 80))
```

**DON'T:**
```python
# Radio buttons for 100 options ❌ Clutters UI
choice = st.radio("Choose", list(range(100)))
```

---

## 🏗️ Code Organization

### 1. Structure Your Code

**DO:**
```python
# app.py

def load_data():
    """Load and prepare data."""
    # ... implementation

def create_visualizations(df):
    """Create charts and graphs."""
    # ... implementation

def main():
    """Main application logic."""
    st.title("My App")

    data = load_data()
    create_visualizations(data)

if __name__ == "__main__":
    main()
```

**DON'T:**
```python
# Everything in global scope ❌
st.title("My App")
df = pd.read_csv('data.csv')
st.line_chart(df)
# ... 500 lines of code
```

### 2. Use Meaningful Variable Names

**DO:**
```python
user_age = st.number_input("Age", 1, 120, 25)
filtered_data = df[df['age'] > user_age]
average_salary = filtered_data['salary'].mean()
```

**DON'T:**
```python
x = st.number_input("Age", 1, 120, 25)  # ❌ What is x?
d = df[df['age'] > x]
a = d['salary'].mean()
```

### 3. Add Comments and Docstrings

**DO:**
```python
@st.cache_data
def preprocess_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare data for analysis.

    Args:
        raw_df: Raw input DataFrame

    Returns:
        Cleaned DataFrame with standardized columns
    """
    # Remove duplicates
    df = raw_df.drop_duplicates()

    # Standardize column names
    df.columns = df.columns.str.lower().str.replace(' ', '_')

    return df
```

---

## 🔒 Security

### 1. Use Secrets for Sensitive Data

**DO:**
```python
# In .streamlit/secrets.toml
# api_key = "your-secret-key"

# In app.py
api_key = st.secrets["api_key"]
response = requests.get(url, headers={"Authorization": api_key})
```

**DON'T:**
```python
# Hardcoded secrets ❌
api_key = "sk-1234567890abcdef"  # ❌ Never commit secrets!
```

### 2. Validate User Input

**DO:**
```python
uploaded_file = st.file_uploader("Upload CSV", type=['csv'])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        # Validate expected columns
        required_cols = ['name', 'age', 'email']
        if not all(col in df.columns for col in required_cols):
            st.error(f"Missing columns. Required: {required_cols}")
            st.stop()

        # Process data
        st.dataframe(df)

    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
```

**DON'T:**
```python
uploaded_file = st.file_uploader("Upload CSV")
df = pd.read_csv(uploaded_file)  # ❌ No validation, can crash
```

---

## 📱 Deployment

### 1. Pin Dependencies

**DO:**
```txt
# requirements.txt
streamlit==1.40.0
pandas==2.2.3
numpy==2.1.3
plotly==5.24.1
```

**DON'T:**
```txt
# requirements.txt
streamlit
pandas
numpy  # ❌ Versions can change and break your app
```

### 2. Test Locally Before Deploying

**DO:**
```bash
# Create fresh environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install from requirements.txt
pip install -r requirements.txt

# Test app
streamlit run app.py
```

### 3. Add .gitignore

**DO:**
```
# .gitignore
__pycache__/
*.py[cod]
.streamlit/secrets.toml
venv/
.env
*.csv
*.xlsx
.DS_Store
```

---

## 🎯 UI/UX Best Practices

### 1. Use Page Config

**DO:**
```python
st.set_page_config(
    page_title="My App",
    page_icon="🎯",
    layout="wide",
    menu_items={
        'Get Help': 'https://docs.example.com',
        'Report a bug': 'https://github.com/user/repo/issues',
        'About': '# My App v1.0\nDescription here'
    }
)
```

### 2. Organize with Layouts

**DO:**
```python
# Use tabs for different views
tab1, tab2, tab3 = st.tabs(["Data", "Analysis", "Settings"])

with tab1:
    st.dataframe(df)

with tab2:
    st.line_chart(df)

with tab3:
    show_settings()
```

### 3. Group Related Controls

**DO:**
```python
with st.sidebar:
    st.header("Filters")

    # Related filters together
    date_range = st.date_input("Date Range", [start, end])
    category = st.multiselect("Categories", categories)
    min_value = st.slider("Min Value", 0, 100)
```

### 4. Provide Visual Feedback

**DO:**
```python
if st.button("Process Data"):
    with st.spinner("Processing..."):
        result = process_data()

    st.success("✅ Processing complete!")
    st.balloons()
```

---

## 📊 Data Visualization

### 1. Choose Appropriate Chart Types

- **Line Chart**: Time series, trends
- **Bar Chart**: Category comparison
- **Scatter Plot**: Correlation, relationships
- **Histogram**: Distribution
- **Box Plot**: Statistical distribution, outliers
- **Heatmap**: Correlation matrix, intensity
- **Pie Chart**: Parts of whole (use sparingly!)

### 2. Make Charts Interactive

**DO:**
```python
import plotly.express as px

fig = px.scatter(
    df,
    x='age',
    y='salary',
    color='department',
    title='Salary vs Age by Department',
    hover_data=['name', 'years_experience']
)

st.plotly_chart(fig, use_container_width=True)
```

### 3. Add Context to Visualizations

**DO:**
```python
st.subheader("Sales Trend")
st.markdown("📈 Sales have increased 23% over the last quarter")

st.line_chart(sales_data)

st.caption("Data updated daily. Last update: 2024-01-14")
```

---

## 🗄 Databases

Full walkthrough in **[DATABASE_GUIDE.md](../DATABASE_GUIDE.md)**. The rules
that bite people most often:

### 1. Cache your connection

**DO:**
```python
@st.cache_resource
def get_conn():
    return psycopg.connect(DB_URL, sslmode="require", autocommit=True)
```

**DON'T:** open a connection inside the main script body — you'd create a
new one on every rerun, every click.

### 2. Always parameterize queries

**DO:**
```python
cur.execute("SELECT * FROM users WHERE email = %s", (email,))
```

**DON'T:**
```python
cur.execute(f"SELECT * FROM users WHERE email = '{email}'")  # ❌ SQL injection
```

### 3. Know your filesystem's lifetime

- **Local laptop:** files persist forever.
- **Streamlit Community Cloud / Render free:** files (including SQLite DBs)
  written at runtime are WIPED on every redeploy, cold start, or restart.
- **Fix:** use a managed database (Supabase, Neon, Render Postgres) for any
  data you need to keep.

### 4. Secrets never go in code

**DO:** read the DB URL from `st.secrets` locally, and from
`os.environ["DATABASE_URL"]` on hosts that use env vars (Render, Fly, etc.).
Put a template at `.streamlit/secrets.toml.example` and `.gitignore` the real
`secrets.toml`.

**DON'T:** paste the URL into `app.py`, log it, or display it in UI error
messages.

### 5. `CREATE TABLE IF NOT EXISTS` is fine for tutorials

For real apps, graduate to a migration tool (Alembic, `supabase db push`)
so schema changes are tracked, reviewable, and reversible.

---

## ♿ Accessibility

### 1. Use Descriptive Labels

**DO:**
```python
age = st.number_input(
    "Enter your age",
    min_value=0,
    max_value=120,
    help="Age in years"
)
```

**DON'T:**
```python
age = st.number_input("Age", 0, 120)  # ❌ Not descriptive enough
```

### 2. Provide Alt Text for Images

**DO:**
```python
st.image(
    "chart.png",
    caption="Sales growth over time",
    use_container_width=True
)
```

### 3. Use Color Wisely

- Don't rely solely on color to convey information
- Ensure sufficient contrast
- Test with colorblind simulators

---

## 🧪 Testing

### 1. Test Edge Cases

```python
# Test with:
- Empty DataFrames
- Missing values
- Invalid file formats
- Large datasets
- Special characters
- Different screen sizes
```

### 2. Get Feedback Early

- Share app with users early
- Gather feedback
- Iterate based on usage

---

## 📚 Documentation

### 1. Add In-App Help

**DO:**
```python
with st.expander("ℹ️ How to use this tool"):
    st.markdown("""
    1. Upload your data file
    2. Select analysis type
    3. View results below
    4. Download report
    """)
```

### 2. Create a README

Include:
- Purpose of the app
- How to run locally
- Requirements
- Features
- Screenshots
- Deployment instructions

---

## 📋 Checklist Before Deployment

- [ ] All secrets moved to `st.secrets` (not hardcoded)
- [ ] Dependencies pinned in `requirements.txt`
- [ ] Tested with fresh install
- [ ] Error handling implemented
- [ ] Loading indicators added
- [ ] Help text and instructions provided
- [ ] `.gitignore` configured
- [ ] README.md created
- [ ] Performance optimized (caching used)
- [ ] Code organized and commented
- [ ] Tested on different screen sizes
- [ ] Tested with various data inputs

---

## 🎓 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [30 Days of Streamlit](https://30days.streamlit.app)
- [Streamlit Gallery](https://streamlit.io/gallery)
- [Streamlit Forum](https://discuss.streamlit.io)

---

**Remember:** The best Streamlit apps are simple, fast, and user-friendly!
