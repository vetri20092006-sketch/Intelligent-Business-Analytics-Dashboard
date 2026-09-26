# OmniMetrics AI — Intelligent Business Analytics Dashboard

A modern, production-grade Machine Learning web application engineered for B2B enterprise analytics, customer churn intelligence, health scoring, and prescriptive retention strategies.

Designed with a bespoke **Obsidian & Electric Indigo / Cyan** design system, full dark/light theme toggle, interactive **Chart.js** performance diagnostics, and a modular Python **Flask** backend.

---

## 🌟 Key Features

1. **Modern, Non-Generic Startup UI/UX**:
   - Original visual identity avoiding generic AI templates or oversized cliché gradients.
   - Glassmorphic navigation header (`backdrop-filter: blur(16px)`).
   - Bespoke typography using Google's *Plus Jakarta Sans* and *Inter*.
   - Dark mode by default with a crisp light theme toggle saved in `localStorage`.
   - Polished micro-interactions: skeleton shimmer loaders, floating toast notifications, and animated confidence score gauge.

2. **Real-Time Prediction Studio (`/prediction`)**:
   - Categorized parameter inputs: Account Tenure, Contract Type, MRR, Product Engagement Score, NPS Sentiment, Support Tickets, and Invoice Delay.
   - 3 Quick Prefill Sample Scenarios (*Low-Risk Enterprise Champion*, *Moderate-Risk Growth Account*, *Critical-Risk SMB*).
   - Animated circular SVG confidence gauge indicating churn probability.
   - Financial Impact calculations: Annual Recurring Revenue (ARR) and Expected Revenue at Risk.
   - Transparent behavioral risk drivers and actionable retention recommendations.

3. **Interactive Model Diagnostics (`/performance`)**:
   - Out-of-sample statistical scorecard: **Accuracy**, **Precision**, **Recall**, **F1-Score**, and **ROC-AUC**.
   - Interactive **ROC Curve** with baseline reference and hover tooltips via Chart.js.
   - Interactive **2x2 Confusion Matrix** heatmap (TN, FP, FN, TP) with percentage distributions.
   - Ranked **Feature Importance** horizontal bar chart showing Gini influence.
   - Full model hyperparameter architecture specifications table.

4. **Dataset Explorer & Data Dictionary (`/dataset`)**:
   - Live paginated, sortable, and searchable table of customer records.
   - Class distribution donut chart and contract type churn correlation bar chart.
   - Comprehensive Data Dictionary with variable descriptions, allowable ranges, and domain logic.
   - Direct CSV export link.

5. **Self-Contained & Privacy First**:
   - Zero external cloud AI dependencies or paid API keys required.
   - Fast Python Flask server executing inferences in `< 15ms`.

---

## 📁 Project Folder Structure

```
intelligent-business-analytics/
├── app.py                          # Flask server & REST API endpoints
├── config.py                       # Application configuration & feature validation limits
├── train_model.py                  # Data generation & Scikit-Learn training pipeline
├── requirements.txt                # Python package dependencies
├── README.md                       # Complete project documentation & guide
│
├── data/
│   └── business_analytics_dataset.csv   # 5,000-record B2B customer analytics dataset
│
├── models/
│   ├── model.pkl                   # Trained serialized Scikit-Learn Pipeline
│   ├── metrics.json                # Precomputed validation metrics (ROC, CM, Accuracy)
│   └── metadata.json               # Schema specs, sample cases, and feature metadata
│
├── static/
│   ├── css/
│   │   ├── style.css               # Design system, CSS variables, dark/light theme, navbar, footer
│   │   ├── components.css          # Cards, buttons, forms, tables, gauge, toasts, badges
│   │   └── animations.css          # Skeleton shimmers, keyframes, transitions, pulse dots
│   └── js/
│       ├── main.js                 # Theme switcher, mobile drawer, toast manager, scroll-to-top
│       ├── prediction.js           # Prediction Studio form, slider sync, gauge animation, advice
│       ├── performance.js          # Chart.js initialization for ROC, CM, and Feature Importance
│       └── dataset.js              # Table pagination, live search filter, and distribution charts
│
└── templates/
    ├── base.html                   # Master layout with responsive navbar, toast container, footer
    ├── index.html                  # Home: Hero, capabilities, workflow timeline, and ROI impact
    ├── prediction.html             # Prediction Studio interface
    ├── performance.html            # Model Performance & Diagnostics
    ├── dataset.html                # Dataset Explorer & Data Dictionary
    ├── about.html                  # Architecture overview & ML workflow
    └── contact.html                # Contact inquiry form & integration FAQ
```

---

## 🚀 Quickstart Installation & Running

### 1. Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- `pip` package manager

### 2. Install Dependencies
Navigate into the project directory and install the packages:
```bash
cd intelligent-business-analytics
python -m pip install -r requirements.txt
```

### 3. Generate Data & Train Model (Already Pre-trained!)
To rebuild or train the model from scratch:
```bash
python train_model.py
```
This automatically produces:
- `data/business_analytics_dataset.csv`
- `models/model.pkl`
- `models/metrics.json`
- `models/metadata.json`

### 4. Start the Web Server
Launch the Flask development server:
```bash
python app.py
```
Then open your browser and navigate to:
**`http://127.0.0.1:5000`**

---

## 🔄 How to Replace the Dataset & Trained ML Model

This project is built to allow dropping in your own custom dataset and `.pkl` model file:

### Step 1: Replace the Dataset File
Place your custom dataset CSV in the `data/` folder:
```bash
# Overwrite the existing file:
data/business_analytics_dataset.csv
```

### Step 2: Drop In Your Trained Model (`.pkl`)
Save your trained scikit-learn model or pipeline with `joblib` or `pickle` and save it directly to:
```bash
models/model.pkl
```
*Example Python snippet used to export your model:*
```python
import joblib

# Export your trained pipeline or classifier:
joblib.dump(my_trained_pipeline, "models/model.pkl")
```

### Step 3: Update Feature Names in `config.py` (If Features Differ)
If your dataset uses different feature column names, open `config.py` and modify the feature lists:
```python
# In config.py:
REQUIRED_NUMERIC_FEATURES = [
    "your_num_feature_1",
    "your_num_feature_2",
    # ...
]

REQUIRED_CATEGORICAL_FEATURES = [
    "your_cat_feature_1",
    # ...
]
```
Then match the `<input name="...">` tags inside `templates/prediction.html` with your new column names.

### Step 4: Retrain or Refresh Metrics
You can also customize `train_model.py` to point to your new dataset and run:
```bash
python train_model.py
```
This will automatically recalculate the ROC curve coordinates, Confusion Matrix, and feature importance rankings, updating `models/metrics.json` so the **Model Performance** page reflects your new model immediately.

---

## 📡 REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `POST /api/predict` | `POST` | Ingests JSON customer parameters, executes `model.pkl` inference, and returns risk tier, confidence %, financial impact, and prescriptive recommendations. |
| `GET /api/model-info` | `GET` | Returns model evaluation metrics (Accuracy, Precision, Recall, F1, ROC points, Confusion Matrix, Feature Importance). |
| `GET /api/dataset-stats` | `GET` | Returns aggregated distributions, correlations, and class balance for Chart.js rendering. |
| `GET /api/dataset-sample` | `GET` | Returns paginated, searchable, and sortable dataset rows. Parameters: `page`, `limit`, `search`, `sort_by`, `sort_order`. |
| `POST /api/contact` | `POST` | Validates and logs customer support / integration inquiries. |
| `GET /download/dataset` | `GET` | Downloads the raw CSV dataset file. |

---

## 🎨 UI/UX Features & Accessibility

- **Keyboard Accessible**: All forms, modals, tabs, and buttons are accessible via Tab and Enter keys with clear `:focus-visible` styling.
- **Responsive Layout**: Designed with fluid CSS Grid and Flexbox for mobile screens (375px+), tablets (768px+), laptops, and ultra-wide desktops.
- **Dark/Light Mode**: Seamless toggle button with instant `data-theme` variable switching and localStorage persistence.
- **Graceful Error Handling**: Client-side validation with inline error hints, plus server-side validation error codes (`400`, `422`, `500`).
