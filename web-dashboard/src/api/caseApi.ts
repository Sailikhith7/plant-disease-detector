const API_BASE_URL = "http://localhost:8000";


// =========================================================
// GET CASES
// Backend:
// GET /api/cases/
// =========================================================

export async function getCases() {
  const response = await fetch(
    `${API_BASE_URL}/api/cases/`
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch cases (${response.status})`
    );
  }

  const data = await response.json();

  return data?.cases ?? [];
}


// =========================================================
// GET ANALYTICS
// Backend:
// GET /api/analytics/
// =========================================================

export async function getAnalytics() {
  const response = await fetch(
    `${API_BASE_URL}/api/analytics/`
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch analytics (${response.status})`
    );
  }

  const data = await response.json();

  return data?.metrics ?? {};
}


// =========================================================
// GET ACTIVE OUTBREAKS
// Backend:
// GET /api/alerts/outbreaks?threshold=5
// =========================================================

export async function getOutbreaks(
  threshold = 5
) {
  const response = await fetch(
    `${API_BASE_URL}/api/alerts/outbreaks?threshold=${threshold}`
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch outbreaks (${response.status})`
    );
  }

  return await response.json();
}


// =========================================================
// SEND BROADCAST ADVISORY
// Backend:
// POST /api/alerts/broadcast
// =========================================================

export async function sendBroadcastAdvisory(
  payload: {
    district: string;
    crop: string;
    disease: string;
    custom_message: string;
  }
) {
  const response = await fetch(
    `${API_BASE_URL}/api/alerts/broadcast`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify(payload),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.message ||
        "Broadcast request failed."
    );
  }

  return data;
}