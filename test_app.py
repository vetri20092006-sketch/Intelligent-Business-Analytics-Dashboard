"""
Automated System Verification Test Suite for OmniMetrics AI Platform
Validates all page routes, API endpoints, model inference, and error handling.
"""

import unittest
import json
from app import app

class OmniMetricsTestSuite(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_pages_status_codes(self):
        """Verifies that all 6 main pages load with HTTP 200."""
        routes = ["/", "/prediction", "/performance", "/dataset", "/about", "/contact"]
        for route in routes:
            response = self.app.get(route)
            self.assertEqual(response.status_code, 200, f"Route {route} failed with status {response.status_code}")
            self.assertIn(b"OmniMetrics", response.data)

    def test_api_model_info(self):
        """Verifies /api/model-info returns required metrics structure."""
        response = self.app.get("/api/model-info")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        m = data["data"]
        self.assertIn("accuracy", m)
        self.assertIn("precision", m)
        self.assertIn("recall", m)
        self.assertIn("f1_score", m)
        self.assertIn("roc_auc", m)
        self.assertIn("roc_curve", m)
        self.assertIn("confusion_matrix", m)
        self.assertIn("feature_importance", m)

    def test_api_dataset_stats(self):
        """Verifies /api/dataset-stats returns distribution counts."""
        response = self.app.get("/api/dataset-stats")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        s = data["data"]
        self.assertIn("total_records", s)
        self.assertIn("retained_count", s)
        self.assertIn("churned_count", s)
        self.assertEqual(s["total_records"], 5000)

    def test_api_dataset_sample(self):
        """Verifies /api/dataset-sample returns paginated records."""
        response = self.app.get("/api/dataset-sample?page=1&limit=5")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        records = data["data"]["records"]
        self.assertEqual(len(records), 5)
        self.assertIn("customer_id", records[0])
        self.assertIn("service_tier", records[0])

    def test_api_predict_success(self):
        """Tests successful inference and recommendation generation."""
        sample_payload = {
            "tenure_months": 24,
            "contract_length_months": 12,
            "contract_type": "Annual",
            "service_tier": "Growth",
            "monthly_charges": 199.0,
            "total_charges": 4776.0,
            "product_usage_score": 75.0,
            "nps_score": 8,
            "support_tickets_quarter": 1,
            "payment_delay_days": 0
        }
        response = self.app.post(
            "/api/predict",
            data=json.dumps(sample_payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        p = data["prediction"]
        self.assertIn("churn_probability", p)
        self.assertIn("churn_percentage", p)
        self.assertIn("risk_tier", p)
        self.assertIn("financials", p)
        self.assertGreater(len(data["recommendations"]), 0)
        self.assertGreater(len(data["risk_drivers"]), 0)

    def test_api_predict_validation_error(self):
        """Tests error response when missing fields are sent."""
        invalid_payload = {"tenure_months": 12}
        response = self.app.post(
            "/api/predict",
            data=json.dumps(invalid_payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 422)

    def test_api_contact(self):
        """Tests contact submission endpoint."""
        payload = {
            "name": "Sarah Connor",
            "email": "sarah@cyberdyne.com",
            "topic": "Model Customization",
            "message": "Interested in evaluating custom ML models."
        }
        response = self.app.post(
            "/api/contact",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")


if __name__ == "__main__":
    unittest.main()
