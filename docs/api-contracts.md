# API Contracts (Frozen)

### 1. Submit Case (Farmer App -> Backend)
- **Endpoint:** `POST /api/cases`
- **Type:** `multipart/form-data`
- **Payload:**
  - `image`: File (Binary/JPEG)
  - `farmer_id`: String
  - `crop`: String (e.g., "cotton", "soybean")
  - `latitude`: Float
  - `longitude`: Float
  - `district`: String
  - `language`: String ("mr" | "hi" | "en")
- **Response (201 Created):**
  ```json
  {
    "case_id": "case_123",
    "crop": "cotton",
    "disease": "Pink Bollworm",
    "confidence": 0.85,
    "status": "auto_resolved",
    "requires_expert_review": false,
    "advisory": {
      "severity": "medium",
      "cultural": "Destroy crop residue",
      "biological": "Trichogramma bactrae",
      "chemical": "Chlorantraniliprole 18.5% SC"
    },
    "created_at": "2026-08-25T10:00:00Z"
  }

  {
  "expert_id": "exp_01",
  "confirmed_disease": "Pink Bollworm",
  "custom_prescription": "Apply 5% Neem seed kernel extract immediately.",
  "status": "resolved"
}

