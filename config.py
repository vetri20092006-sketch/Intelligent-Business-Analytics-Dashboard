"""
Application Configuration and Business Analytics Settings
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "business-analytics-secret-key-2026-prod")
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")
    PORT = int(os.environ.get("PORT", 5000))
    HOST = os.environ.get("HOST", "127.0.0.1")

    # File paths
    DATA_PATH = os.path.join(BASE_DIR, "data", "business_analytics_dataset.csv")
    MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")
    METRICS_PATH = os.path.join(BASE_DIR, "models", "metrics.json")
    METADATA_PATH = os.path.join(BASE_DIR, "models", "metadata.json")

    # Feature definitions for prediction engine
    REQUIRED_NUMERIC_FEATURES = [
        "tenure_months",
        "contract_length_months",
        "monthly_charges",
        "total_charges",
        "product_usage_score",
        "nps_score",
        "support_tickets_quarter",
        "payment_delay_days"
    ]

    REQUIRED_CATEGORICAL_FEATURES = [
        "contract_type",
        "service_tier"
    ]

    FEATURE_LIMITS = {
        "tenure_months": {"min": 1, "max": 120, "default": 12},
        "contract_length_months": {"min": 1, "max": 60, "default": 12},
        "monthly_charges": {"min": 10.0, "max": 5000.0, "default": 149.0},
        "total_charges": {"min": 10.0, "max": 100000.0, "default": 1788.0},
        "product_usage_score": {"min": 0.0, "max": 100.0, "default": 65.0},
        "nps_score": {"min": 0, "max": 10, "default": 7},
        "support_tickets_quarter": {"min": 0, "max": 50, "default": 2},
        "payment_delay_days": {"min": 0, "max": 180, "default": 0}
    }

    CATEGORICAL_CHOICES = {
        "contract_type": ["Month-to-Month", "Annual", "Multi-Year"],
        "service_tier": ["Starter", "Growth", "Enterprise"]
    }
