# My First Streamlit App

A starter template for building Streamlit web applications.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the App

```bash
streamlit run app.py
```

Your browser will automatically open to `http://localhost:8501`

## 📁 Project Structure

```
my_first_app/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🎯 Customization

### Modify the App

1. Open `app.py` in your favorite code editor
2. Make your changes
3. Save the file
4. Streamlit will automatically reload!

### Change the Title

```python
st.set_page_config(
    page_title="My Custom Title",
    page_icon="🎨"
)
```

### Add New Widgets

Check out the examples in the `../examples/` folder for inspiration!

## 🌐 Deploy to Cloud

When you're ready to share your app with the world, pick one:

- **Streamlit-only app** → [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)
  (Streamlit Community Cloud — one-click deploy, great for dashboards and
  demos)
- **Streamlit + separate backend (FastAPI, DB, etc.)** →
  [RENDER_DEPLOYMENT_GUIDE.md](../RENDER_DEPLOYMENT_GUIDE.md) (Render.com —
  two web services, from-scratch walkthrough)

Both are free and assume no prior cloud experience.

## 📚 Learn More

- [Streamlit Documentation](https://docs.streamlit.io)
- [Tutorial README](../README.md)
- [Example Apps](../examples/)

## 💡 Ideas for Your App

- Data dashboard
- ML model demo
- Data analysis tool
- Interactive visualization
- Form/survey application
- File processor
- API demo

**Happy Building! 🎉**
