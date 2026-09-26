"""
Intelligent Business Analytics Dashboard - Model Training & Data Generation Pipeline
Synthesizes a realistic B2B SaaS business dataset, trains an interpretable 
RandomForestClassifier pipeline, and serializes the model and metrics.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    confusion_matrix
)

# Base Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

DATASET_PATH = os.path.join(DATA_DIR, "business_analytics_dataset.csv")
MODEL_PKL_PATH = os.path.join(MODELS_DIR, "model.pkl")
METRICS_JSON_PATH = os.path.join(MODELS_DIR, "metrics.json")
METADATA_JSON_PATH = os.path.join(MODELS_DIR, "metadata.json")


def generate_business_dataset(n_samples: int = 5000, random_seed: int = 42) -> pd.DataFrame:
    """
    Generates a realistic B2B enterprise customer dataset with realistic
    feature interactions affecting customer churn/retention.
    """
    np.random.seed(random_seed)

    customer_ids = [f"CUST-{10000 + i}" for i in range(n_samples)]
    
    # Contract Length (1, 12, 24, 36 months)
    contract_choices = [1, 12, 24, 36]
    contract_probs = [0.35, 0.40, 0.18, 0.07]
    contract_length = np.random.choice(contract_choices, size=n_samples, p=contract_probs)

    contract_type_map = {
        1: "Month-to-Month",
        12: "Annual",
        24: "Multi-Year",
        36: "Multi-Year"
    }
    contract_type = [contract_type_map[c] for c in contract_length]

    # Service Tier
    service_tiers = np.random.choice(["Starter", "Growth", "Enterprise"], size=n_samples, p=[0.45, 0.38, 0.17])

    # Monthly charges based on tier
    tier_base_cost = {
        "Starter": np.random.uniform(49.0, 99.0, size=n_samples),
        "Growth": np.random.uniform(149.0, 299.0, size=n_samples),
        "Enterprise": np.random.uniform(399.0, 899.0, size=n_samples)
    }
    monthly_charges = np.zeros(n_samples)
    for i, tier in enumerate(service_tiers):
        monthly_charges[i] = round(tier_base_cost[tier][i], 2)

    # Customer Tenure (months active)
    tenure_months = np.random.geometric(p=0.04, size=n_samples)
    tenure_months = np.clip(tenure_months, 1, 72)

    # Total charges (approx tenure * monthly + historical variance)
    total_charges = np.round(tenure_months * monthly_charges * np.random.uniform(0.92, 1.05, size=n_samples), 2)

    # Product Usage Score (0 - 100)
    base_usage = np.random.normal(loc=65, scale=18, size=n_samples)
    product_usage_score = np.clip(base_usage, 5, 100).round(1)

    # Net Promoter Score (NPS: 0 to 10)
    # Higher usage generally correlates with higher satisfaction
    nps_raw = (product_usage_score / 10) + np.random.normal(loc=0, scale=1.8, size=n_samples)
    nps_score = np.clip(nps_raw.round(), 0, 10).astype(int)

    # Support Tickets in the Last Quarter (0 - 12)
    # Dissatisfied or struggling users submit more tickets
    ticket_lambda = np.where(product_usage_score < 40, 4.2, 1.5)
    support_tickets = np.random.poisson(lam=ticket_lambda, size=n_samples)
    support_tickets_quarter = np.clip(support_tickets, 0, 14)

    # Payment Delay Days (0 - 45)
    delay_prob = np.where(contract_length == 1, 0.30, 0.08)
    has_delay = np.random.binomial(1, delay_prob, size=n_samples)
    payment_delay_days = (has_delay * np.random.exponential(scale=10, size=n_samples)).astype(int)
    payment_delay_days = np.clip(payment_delay_days, 0, 50)

    # Latent Churn Propensity Function (Ground Truth Probability)
    # Logit model with real-world business weighting
    logit = (
        - 1.4
        + 0.85 * (contract_length == 1)               # Month-to-month contracts churn much more
        - 0.90 * (contract_length >= 24)              # Multi-year lock-in protects retention
        - 0.035 * (product_usage_score - 50)          # Higher engagement reduces churn
        - 0.22 * (nps_score - 5)                      # High NPS protects retention
        + 0.28 * support_tickets_quarter              # Support friction drives churn
        + 0.045 * payment_delay_days                  # Late payments indicate credit/cashflow stress
        - 0.015 * tenure_months                       # Long tenured accounts have sticky habits
        + 0.001 * (monthly_charges - 200)             # Price sensitivity
        + np.random.normal(0, 0.45, size=n_samples)   # Realistic unobserved variance
    )
    
    churn_prob = 1.0 / (1.0 + np.exp(-logit))
    has_churned = (np.random.rand(n_samples) < churn_prob).astype(int)

    df = pd.DataFrame({
        "customer_id": customer_ids,
        "tenure_months": tenure_months,
        "contract_length_months": contract_length,
        "contract_type": contract_type,
        "service_tier": service_tiers,
        "monthly_charges": monthly_charges,
        "total_charges": total_charges,
        "product_usage_score": product_usage_score,
        "nps_score": nps_score,
        "support_tickets_quarter": support_tickets_quarter,
        "payment_delay_days": payment_delay_days,
        "has_churned": has_churned
    })

    return df


def train_and_export():
    print("[1/4] Generating business analytics dataset...")
    df = generate_business_dataset(n_samples=5000, random_seed=42)
    df.to_csv(DATASET_PATH, index=False)
    print(f"      Saved {len(df)} records to {DATASET_PATH}")

    # Features and Target
    target_col = "has_churned"
    features_num = [
        "tenure_months",
        "contract_length_months",
        "monthly_charges",
        "total_charges",
        "product_usage_score",
        "nps_score",
        "support_tickets_quarter",
        "payment_delay_days"
    ]
    features_cat = ["contract_type", "service_tier"]

    X = df[features_num + features_cat]
    y = df[target_col]

    print("[2/4] Splitting and fitting ML Pipeline (Random Forest)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), features_num),
            ("cat", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), features_cat)
        ]
    )

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=180,
            max_depth=9,
            min_samples_leaf=4,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        ))
    ])

    model.fit(X_train, y_train)

    print("[3/4] Evaluating model performance metrics...")
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    auc = float(roc_auc_score(y_test, y_pred_proba))

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = [int(v) for v in cm.ravel()]

    # ROC Curve points (downsampled to 40 points for clean Chart.js rendering)
    fpr_raw, tpr_raw, thresholds = roc_curve(y_test, y_pred_proba)
    idx_sample = np.linspace(0, len(fpr_raw) - 1, min(40, len(fpr_raw))).astype(int)
    roc_points = [
        {"x": round(float(fpr_raw[i]), 4), "y": round(float(tpr_raw[i]), 4)}
        for i in idx_sample
    ]
    # Ensure (0,0) and (1,1) endpoints are exact
    if roc_points[0] != {"x": 0.0, "y": 0.0}:
        roc_points.insert(0, {"x": 0.0, "y": 0.0})
    if roc_points[-1] != {"x": 1.0, "y": 1.0}:
        roc_points.append({"x": 1.0, "y": 1.0})

    # Feature Importance extraction
    rf = model.named_steps["classifier"]
    cat_encoder = model.named_steps["preprocessor"].named_transformers_["cat"]
    encoded_cat_features = list(cat_encoder.get_feature_names_out(features_cat))
    all_feature_names = features_num + encoded_cat_features
    importances = rf.feature_importances_

    # Clean display names for features
    display_names = {
        "tenure_months": "Customer Tenure (Months)",
        "contract_length_months": "Contract Term (Months)",
        "monthly_charges": "Monthly Recurring Spend",
        "total_charges": "Lifetime Value / Total Spend",
        "product_usage_score": "Product Engagement Score",
        "nps_score": "Net Promoter Score (NPS)",
        "support_tickets_quarter": "Support Tickets (Quarter)",
        "payment_delay_days": "Payment Delays (Days)",
        "contract_type_Month-to-Month": "Contract: Month-to-Month",
        "contract_type_Multi-Year": "Contract: Multi-Year",
        "service_tier_Growth": "Tier: Growth",
        "service_tier_Enterprise": "Tier: Enterprise"
    }

    feature_importance_list = []
    for name, imp in sorted(zip(all_feature_names, importances), key=lambda x: x[1], reverse=True):
        feature_importance_list.append({
            "feature": name,
            "display_name": display_names.get(name, name.replace("_", " ").title()),
            "importance": round(float(imp), 4),
            "percentage": round(float(imp) * 100, 2)
        })

    metrics_payload = {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(auc, 4),
        "confusion_matrix": {
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn,
            "true_positive": tp,
            "total_test_samples": int(len(y_test)),
            "accuracy_pct": round(acc * 100, 1),
            "specificity_pct": round((tn / (tn + fp)) * 100, 1) if (tn + fp) > 0 else 0
        },
        "roc_curve": roc_points,
        "feature_importance": feature_importance_list,
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "model_type": "Random Forest Ensemble (Pipeline)",
        "parameters": {
            "n_estimators": 180,
            "max_depth": 9,
            "min_samples_leaf": 4,
            "class_weight": "balanced",
            "cross_validation": "5-Fold Stratified Split",
            "scaler": "StandardScaler",
            "encoder": "OneHotEncoder(drop='first')"
        }
    }

    print("[4/4] Saving model.pkl, metrics.json, and metadata.json...")
    joblib.dump(model, MODEL_PKL_PATH)

    with open(METRICS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    # Metadata for dataset explorer and form fields
    metadata_payload = {
        "dataset_name": "Enterprise B2B Customer Analytics & Health Dataset",
        "total_records": len(df),
        "features_count": len(features_num) + len(features_cat),
        "missing_values": int(df.isna().sum().sum()),
        "target_column": target_col,
        "class_distribution": {
            "retained": int((df[target_col] == 0).sum()),
            "churned": int((df[target_col] == 1).sum()),
            "churn_rate_pct": round(float((df[target_col] == 1).mean()) * 100, 1)
        },
        "features": {
            "tenure_months": {"type": "integer", "min": int(df["tenure_months"].min()), "max": int(df["tenure_months"].max()), "mean": round(float(df["tenure_months"].mean()), 1), "description": "Number of continuous months the customer has subscribed to the platform."},
            "contract_length_months": {"type": "integer", "options": [1, 12, 24, 36], "description": "Duration of active committed contract agreement in months."},
            "contract_type": {"type": "categorical", "options": ["Month-to-Month", "Annual", "Multi-Year"], "description": "Contract billing cadence and renewal commitment tier."},
            "service_tier": {"type": "categorical", "options": ["Starter", "Growth", "Enterprise"], "description": "SaaS package subscription level and feature permissions."},
            "monthly_charges": {"type": "float", "min": float(df["monthly_charges"].min()), "max": float(df["monthly_charges"].max()), "mean": round(float(df["monthly_charges"].mean()), 2), "description": "Current recurring monthly license spend ($ USD)."},
            "total_charges": {"type": "float", "min": float(df["total_charges"].min()), "max": float(df["total_charges"].max()), "mean": round(float(df["total_charges"].mean()), 2), "description": "Cumulative historical payments received from this customer ($ USD)."},
            "product_usage_score": {"type": "float", "min": float(df["product_usage_score"].min()), "max": float(df["product_usage_score"].max()), "mean": round(float(df["product_usage_score"].mean()), 1), "description": "Telemetry engagement index tracking DAU/MAU and feature depth (0-100 scale)."},
            "nps_score": {"type": "integer", "min": 0, "max": 10, "mean": round(float(df["nps_score"].mean()), 1), "description": "Customer satisfaction score recorded during the latest quarterly review."},
            "support_tickets_quarter": {"type": "integer", "min": int(df["support_tickets_quarter"].min()), "max": int(df["support_tickets_quarter"].max()), "mean": round(float(df["support_tickets_quarter"].mean()), 1), "description": "Technical and operational support tickets logged in past 90 days."},
            "payment_delay_days": {"type": "integer", "min": int(df["payment_delay_days"].min()), "max": int(df["payment_delay_days"].max()), "mean": round(float(df["payment_delay_days"].mean()), 1), "description": "Average overdue invoice latency in days over the last 3 billing cycles."}
        },
        "sample_profiles": [
            {
                "label": "Low Risk: Enterprise Champion",
                "tag": "Safe Account",
                "values": {
                    "tenure_months": 36,
                    "contract_length_months": 24,
                    "contract_type": "Multi-Year",
                    "service_tier": "Enterprise",
                    "monthly_charges": 580.0,
                    "total_charges": 20880.0,
                    "product_usage_score": 92.5,
                    "nps_score": 9,
                    "support_tickets_quarter": 1,
                    "payment_delay_days": 0
                }
            },
            {
                "label": "Moderate Risk: Growth Account",
                "tag": "Attention Needed",
                "values": {
                    "tenure_months": 11,
                    "contract_length_months": 12,
                    "contract_type": "Annual",
                    "service_tier": "Growth",
                    "monthly_charges": 220.0,
                    "total_charges": 2420.0,
                    "product_usage_score": 61.0,
                    "nps_score": 6,
                    "support_tickets_quarter": 3,
                    "payment_delay_days": 8
                }
            },
            {
                "label": "Critical Risk: Disengaged SMB",
                "tag": "Immediate Danger",
                "values": {
                    "tenure_months": 3,
                    "contract_length_months": 1,
                    "contract_type": "Month-to-Month",
                    "service_tier": "Starter",
                    "monthly_charges": 89.0,
                    "total_charges": 267.0,
                    "product_usage_score": 24.0,
                    "nps_score": 2,
                    "support_tickets_quarter": 7,
                    "payment_delay_days": 21
                }
            }
        ]
    }

    with open(METADATA_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata_payload, f, indent=2)

    print("\n[SUCCESS] Model training and artifacts completed successfully!")
    print(f"Accuracy:  {acc*100:.2f}%")
    print(f"Precision: {prec*100:.2f}%")
    print(f"Recall:    {rec*100:.2f}%")
    print(f"F1 Score:  {f1*100:.2f}%")
    print(f"ROC-AUC:   {auc:.4f}")


if __name__ == "__main__":
    train_and_export()
