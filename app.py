"""
OmniMetrics AI - Intelligent Business Analytics Dashboard
Flask Application Server & Prediction Engine
"""

import os
import json
import logging
import joblib
import numpy as np
import pandas as pd
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file,
    abort
)
from flask_cors import CORS
from config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Load model and artifacts into memory at startup
_model = None
_metrics = None
_metadata = None
_dataset_df = None


def load_artifacts():
    global _model, _metrics, _metadata, _dataset_df
    try:
        if os.path.exists(Config.MODEL_PATH):
            _model = joblib.load(Config.MODEL_PATH)
            logger.info("Successfully loaded ML model from %s", Config.MODEL_PATH)
        else:
            logger.warning("Model file not found at %s. Predictions will be unavailable until trained.", Config.MODEL_PATH)

        if os.path.exists(Config.METRICS_PATH):
            with open(Config.METRICS_PATH, "r", encoding="utf-8") as f:
                _metrics = json.load(f)
            logger.info("Loaded metrics metadata.")

        if os.path.exists(Config.METADATA_PATH):
            with open(Config.METADATA_PATH, "r", encoding="utf-8") as f:
                _metadata = json.load(f)
            logger.info("Loaded dataset metadata.")

        if os.path.exists(Config.DATA_PATH):
            _dataset_df = pd.read_csv(Config.DATA_PATH)
            logger.info("Loaded dataset into memory (%d rows).", len(_dataset_df))
    except Exception as e:
        logger.error("Error loading application artifacts: %s", str(e), exc_info=True)


load_artifacts()


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def generate_recommendations(prob: float, inputs: dict) -> list:
    """
    Generates tailored, prescriptive business retention recommendations
    based on the customer's risk profile and specific behavioral indicators.
    """
    recs = []

    # High / Critical risk recommendations
    if prob >= 0.65:
        recs.append({
            "title": "Immediate Executive Sponsor Outreach",
            "priority": "Critical",
            "badge_color": "danger",
            "action": "Assign senior leadership or VIP Customer Success Director to conduct an emergency health-check call within 24 hours.",
            "impact": "Reduces churn risk by 28% for enterprise accounts through direct escalation resolution."
        })
        if inputs.get("contract_type") == "Month-to-Month":
            recs.append({
                "title": "Propose Annual Renewal with Incentive",
                "priority": "High",
                "badge_color": "warning",
                "action": "Offer a 15% discount or 2 months free platform credits in exchange for locking into a 12-month committed agreement.",
                "impact": "Transitions account from high-volatility month-to-month to predictable annual recurring revenue."
            })
    elif prob >= 0.35:
        recs.append({
            "title": "Quarterly Business Review (QBR) Scheduling",
            "priority": "Medium",
            "badge_color": "warning",
            "action": "Schedule a milestone review to align on ROI deliverables, feature roadmap, and team usage goals.",
            "impact": "Re-establishes perceived value and strengthens vendor alignment before renewal window."
        })
    else:
        recs.append({
            "title": "Expansion & Upsell Opportunity",
            "priority": "Growth",
            "badge_color": "success",
            "action": "Account exhibits high engagement and loyalty. Introduce advanced add-ons, higher tier features, or multi-seat volume expansion.",
            "impact": "Increases Net Revenue Retention (NRR) and Customer Lifetime Value (LTV)."
        })

    # Specific friction driver triggers
    if inputs.get("support_tickets_quarter", 0) >= 4:
        recs.append({
            "title": "Technical Escalation & Dedicated Support Audit",
            "priority": "High",
            "badge_color": "danger",
            "action": f"Client logged {inputs.get('support_tickets_quarter')} support tickets in the last quarter. Deploy a Solutions Architect to conduct a thorough technical onboarding audit and resolve open blockers.",
            "impact": "Eliminates product friction which is currently the #1 correlated churn vector."
        })

    if inputs.get("product_usage_score", 100) < 45:
        recs.append({
            "title": "Targeted Feature Adoption & Re-training Workshop",
            "priority": "High",
            "badge_color": "warning",
            "action": f"Product engagement score is currently {inputs.get('product_usage_score')}/100. Deliver tailored workflow templates and conduct a live training session for their team.",
            "impact": "Lifts product engagement into sticky habits zone (>60/100 score)."
        })

    if inputs.get("payment_delay_days", 0) > 10:
        recs.append({
            "title": "Finance & Invoice Alignment Check",
            "priority": "Medium",
            "badge_color": "info",
            "action": f"Invoices have an average latency of {inputs.get('payment_delay_days')} days. Review billing contact details and offer automated ACH or flexible milestone invoicing.",
            "impact": "Prevents involuntary churn caused by procurement or billing workflow friction."
        })

    if inputs.get("nps_score", 10) <= 5:
        recs.append({
            "title": "CSAT Sentiment Recovery Protocol",
            "priority": "Medium",
            "badge_color": "warning",
            "action": "Conduct a 15-minute voice-of-customer interview to collect feedback and create a transparent resolution ticket.",
            "impact": "Transforms passive or detractor stakeholders into loyal product advocates."
        })

    return recs[:4]  # Return top 4 most pertinent


def identify_risk_drivers(inputs: dict) -> list:
    """
    Identifies which user inputs deviate most unfavorably from benchmarks.
    """
    drivers = []

    if inputs.get("contract_type") == "Month-to-Month":
        drivers.append({"name": "Month-to-Month Agreement", "impact": "High Risk", "detail": "Absence of contractual lock-in creates high vulnerability to month-end cancellations."})
    
    if inputs.get("support_tickets_quarter", 0) >= 4:
        drivers.append({"name": "Excessive Support Ticket Volume", "impact": "High Risk", "detail": f"{inputs['support_tickets_quarter']} tickets logged (vs industry healthy baseline of < 2)."})

    if inputs.get("product_usage_score", 100) < 50:
        drivers.append({"name": "Depressed Product Engagement", "impact": "High Risk", "detail": f"Usage score of {inputs['product_usage_score']}/100 indicates underutilization."})

    if inputs.get("payment_delay_days", 0) > 14:
        drivers.append({"name": "Chronic Payment Delay", "impact": "Medium Risk", "detail": f"{inputs['payment_delay_days']} days overdue indicates budgetary or operational resistance."})

    if inputs.get("nps_score", 10) <= 4:
        drivers.append({"name": "Detractor NPS Rating", "impact": "Medium Risk", "detail": f"NPS score {inputs['nps_score']}/10 signals active dissatisfaction with ROI."})

    if inputs.get("tenure_months", 0) <= 3:
        drivers.append({"name": "Early-Stage Account Vulnerability", "impact": "Medium Risk", "detail": "Account is in high-risk first 90-day onboarding window."})

    if not drivers:
        drivers.append({"name": "Favorable Contract Commitment", "impact": "Low Risk", "detail": "Multi-month lock-in provides strong retention baseline."})
        drivers.append({"name": "Healthy Engagement Metrics", "impact": "Low Risk", "detail": "Usage frequency and NPS meet or exceed enterprise targets."})

    return drivers


# ---------------------------------------------------------
# Page Routes
# ---------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html", active_page="home")


@app.route("/prediction")
def prediction_page():
    return render_template("prediction.html", active_page="prediction")


@app.route("/performance")
def performance_page():
    return render_template("performance.html", active_page="performance")


@app.route("/dataset")
def dataset_page():
    return render_template("dataset.html", active_page="dataset")


@app.route("/about")
def about_page():
    return render_template("about.html", active_page="about")


@app.route("/contact")
def contact_page():
    return render_template("contact.html", active_page="contact")


# ---------------------------------------------------------
# REST API Endpoints
# ---------------------------------------------------------

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    Prediction endpoint that ingests client parameters, feeds into model.pkl,
    and returns predictions, probabilities, risk tiers, and actionable steps.
    """
    global _model
    if _model is None:
        load_artifacts()
        if _model is None:
            return jsonify({
                "status": "error",
                "message": "Trained model artifact (model.pkl) is not loaded on the server. Please run train_model.py first."
            }), 503

    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"status": "error", "message": "Invalid JSON body provided."}), 400

    try:
        # Validate and extract numeric features
        validated_inputs = {}
        for feat in Config.REQUIRED_NUMERIC_FEATURES:
            if feat not in payload:
                return jsonify({"status": "error", "message": f"Missing required parameter '{feat}'"}), 422
            val = float(payload[feat])
            limits = Config.FEATURE_LIMITS.get(feat, {})
            min_val = limits.get("min", -1e9)
            max_val = limits.get("max", 1e9)
            if not (min_val <= val <= max_val):
                return jsonify({
                    "status": "error",
                    "message": f"Feature '{feat}' with value {val} is outside allowed boundaries [{min_val}, {max_val}]."
                }), 422
            validated_inputs[feat] = val

        # Validate and extract categorical features
        for feat in Config.REQUIRED_CATEGORICAL_FEATURES:
            if feat not in payload:
                return jsonify({"status": "error", "message": f"Missing required parameter '{feat}'"}), 422
            val = str(payload[feat]).strip()
            allowed = Config.CATEGORICAL_CHOICES.get(feat, [])
            if allowed and val not in allowed:
                return jsonify({
                    "status": "error",
                    "message": f"Invalid value '{val}' for '{feat}'. Allowed options: {allowed}"
                }), 422
            validated_inputs[feat] = val

        # Prepare DataFrame for scikit-learn pipeline
        input_df = pd.DataFrame([validated_inputs])

        # Execute prediction
        churn_prob = float(_model.predict_proba(input_df)[0][1])
        prediction_class = int(_model.predict(input_df)[0])
        retention_prob = round(1.0 - churn_prob, 4)

        # Risk Classification & Stratification
        if churn_prob >= 0.65:
            risk_tier = "Critical Risk"
            risk_status = "High Vulnerability"
            theme_color = "danger"
            badge_icon = "fa-triangle-exclamation"
            headline_summary = "High probability of immediate customer churn within the next 30 days."
        elif churn_prob >= 0.35:
            risk_tier = "Moderate Risk"
            risk_status = "Elevated Attention Needed"
            theme_color = "warning"
            badge_icon = "fa-circle-exclamation"
            headline_summary = "Account is experiencing friction. Proactive engagement required to preserve retention."
        else:
            risk_tier = "Low Risk"
            risk_status = "Healthy Account"
            theme_color = "success"
            badge_icon = "fa-circle-check"
            headline_summary = "Strong retention indicators and high satisfaction. Account is primed for expansion."

        # Financial Impact estimation
        monthly = validated_inputs["monthly_charges"]
        annual_arr = round(monthly * 12, 2)
        revenue_at_risk = round(annual_arr * churn_prob, 2)

        # Tailored Recommendations and Risk Drivers
        recommendations = generate_recommendations(churn_prob, validated_inputs)
        risk_drivers = identify_risk_drivers(validated_inputs)

        response_data = {
            "status": "success",
            "prediction": {
                "class": prediction_class,
                "label": "Churn Risk" if prediction_class == 1 else "Retained",
                "churn_probability": round(churn_prob, 4),
                "churn_percentage": round(churn_prob * 100, 1),
                "retention_probability": retention_prob,
                "retention_percentage": round(retention_prob * 100, 1),
                "risk_tier": risk_tier,
                "risk_status": risk_status,
                "theme_color": theme_color,
                "badge_icon": badge_icon,
                "summary": headline_summary,
                "financials": {
                    "annual_arr": annual_arr,
                    "revenue_at_risk": revenue_at_risk,
                    "currency": "USD"
                }
            },
            "risk_drivers": risk_drivers,
            "recommendations": recommendations,
            "submitted_features": validated_inputs
        }

        return jsonify(response_data), 200

    except Exception as e:
        logger.error("Prediction computation error: %s", str(e), exc_info=True)
        return jsonify({"status": "error", "message": f"Server error processing prediction: {str(e)}"}), 500


@app.route("/api/model-info", methods=["GET"])
def api_model_info():
    """Returns training metrics, ROC points, confusion matrix, and parameters."""
    if _metrics is None:
        load_artifacts()
    if _metrics is None:
        return jsonify({"status": "error", "message": "Metrics artifact not found"}), 404
    return jsonify({"status": "success", "data": _metrics})


@app.route("/api/metadata", methods=["GET"])
def api_metadata():
    """Returns dataset schemas, sample prefill profiles, and feature definitions."""
    if _metadata is None:
        load_artifacts()
    if _metadata is None:
        return jsonify({"status": "error", "message": "Metadata artifact not found"}), 404
    return jsonify({"status": "success", "data": _metadata})


@app.route("/api/dataset-stats", methods=["GET"])
def api_dataset_stats():
    """Computes distributions and correlations for Chart.js rendering on Dataset page."""
    global _dataset_df
    if _dataset_df is None:
        load_artifacts()
    if _dataset_df is None:
        return jsonify({"status": "error", "message": "Dataset not loaded on server."}), 404

    try:
        # Target Distribution
        churn_counts = _dataset_df["has_churned"].value_counts().to_dict()
        total_rows = len(_dataset_df)

        # Churn by Contract Type
        contract_churn = _dataset_df.groupby("contract_type")["has_churned"].agg(
            total="count",
            churned="sum"
        ).reset_index()
        contract_churn["churn_rate"] = (contract_churn["churned"] / contract_churn["total"] * 100).round(1)

        # Churn by Service Tier
        tier_churn = _dataset_df.groupby("service_tier")["has_churned"].agg(
            total="count",
            churned="sum"
        ).reset_index()
        tier_churn["churn_rate"] = (tier_churn["churned"] / tier_churn["total"] * 100).round(1)

        # Usage score buckets
        usage_bins = [0, 25, 50, 75, 100]
        usage_labels = ["0-25 (Crit)", "26-50 (Low)", "51-75 (Good)", "76-100 (High)"]
        _dataset_df["usage_group"] = pd.cut(_dataset_df["product_usage_score"], bins=usage_bins, labels=usage_labels)
        usage_churn = _dataset_df.groupby("usage_group", observed=False)["has_churned"].agg(
            total="count",
            churned="sum"
        ).reset_index()
        usage_churn["churn_rate"] = (usage_churn["churned"] / usage_churn["total"] * 100).fillna(0).round(1)

        stats = {
            "total_records": total_rows,
            "retained_count": int(churn_counts.get(0, 0)),
            "churned_count": int(churn_counts.get(1, 0)),
            "retained_pct": round(int(churn_counts.get(0, 0)) / total_rows * 100, 1),
            "churned_pct": round(int(churn_counts.get(1, 0)) / total_rows * 100, 1),
            "contract_type_churn": contract_churn.to_dict(orient="records"),
            "service_tier_churn": tier_churn.to_dict(orient="records"),
            "usage_group_churn": usage_churn.to_dict(orient="records")
        }
        return jsonify({"status": "success", "data": stats})
    except Exception as e:
        logger.error("Dataset stats generation error: %s", str(e), exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/dataset-sample", methods=["GET"])
def api_dataset_sample():
    """Returns paginated, searchable rows from the dataset."""
    global _dataset_df
    if _dataset_df is None:
        load_artifacts()
    if _dataset_df is None:
        return jsonify({"status": "error", "message": "Dataset not loaded."}), 404

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    search = request.args.get("search", "", type=str).strip().lower()
    sort_by = request.args.get("sort_by", "customer_id", type=str)
    sort_order = request.args.get("sort_order", "asc", type=str).lower()

    limit = max(5, min(limit, 50))  # bound limit between 5 and 50
    page = max(1, page)

    filtered_df = _dataset_df.copy()

    # Search filter across customer_id, contract_type, service_tier
    if search:
        mask = (
            filtered_df["customer_id"].astype(str).str.lower().str.contains(search) |
            filtered_df["contract_type"].astype(str).str.lower().str.contains(search) |
            filtered_df["service_tier"].astype(str).str.lower().str.contains(search)
        )
        filtered_df = filtered_df[mask]

    # Sort
    if sort_by in filtered_df.columns:
        ascending = (sort_order == "asc")
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)

    total_records = len(filtered_df)
    total_pages = max(1, (total_records + limit - 1) // limit)
    page = min(page, total_pages)

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    page_records = filtered_df.iloc[start_idx:end_idx].to_dict(orient="records")

    return jsonify({
        "status": "success",
        "data": {
            "records": page_records,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_records": total_records,
                "total_pages": total_pages,
                "has_prev": page > 1,
                "has_next": page < total_pages
            }
        }
    })


@app.route("/api/contact", methods=["POST"])
def api_contact():
    """Handles contact form submissions with validation."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "No input provided."}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()
    topic = data.get("topic", "General").strip()

    if not name or len(name) < 2:
        return jsonify({"status": "error", "message": "Please enter a valid name."}), 422
    if not email or "@" not in email or "." not in email:
        return jsonify({"status": "error", "message": "Please enter a valid email address."}), 422
    if not message or len(message) < 5:
        return jsonify({"status": "error", "message": "Please provide a detailed inquiry message."}), 422

    logger.info("Received contact inquiry from %s <%s> regarding '%s'", name, email, topic)
    return jsonify({
        "status": "success",
        "message": f"Thank you, {name}! Your inquiry regarding '{topic}' has been logged. Our analytics engineers will respond to {email} shortly."
    }), 200


@app.route("/download/dataset")
def download_dataset():
    """Allows downloading the dataset CSV directly."""
    if os.path.exists(Config.DATA_PATH):
        return send_file(
            Config.DATA_PATH,
            as_attachment=True,
            download_name="enterprise_business_analytics_dataset.csv",
            mimetype="text/csv"
        )
    abort(404, description="Dataset file not found.")


# ---------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------

@app.errorhandler(404)
def not_found_error(error):
    return render_template("base.html", error_title="404 - Page Not Found", error_message="The requested resource does not exist on this analytics server."), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template("base.html", error_title="500 - Internal Server Error", error_message="An unexpected server error occurred."), 500


if __name__ == "__main__":
    port = Config.PORT
    host = Config.HOST
    logger.info("Starting OmniMetrics AI server on http://%s:%d", host, port)
    app.run(host=host, port=port, debug=Config.DEBUG)
