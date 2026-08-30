const API_BASE_URL = "http://127.0.0.1:8000/api";

// =========================================================
// GET ALL CASES
// =========================================================

export async function getCases() {
  const response = await fetch(`${API_BASE_URL}/cases/`);

  if (!response.ok) {
    throw new Error(`Failed to fetch cases (${response.status})`);
  }

  const data = await response.json();

  if (Array.isArray(data)) {
    return data;
  }
  return data?.cases ?? [];
}


// =========================================================
// GET SINGLE CASE
// =========================================================

export async function getCase(caseId: string) {
  const response = await fetch(
    `${API_BASE_URL}/cases/${encodeURIComponent(caseId)}`
  );

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));

    throw new Error(
      data?.detail || `Failed to fetch case (${response.status})`
    );
  }

  return await response.json();
}


// =========================================================
// RESOLVE CASE
// =========================================================
// Backend:
// POST /api/cases/{case_id}/resolve
//
// Body:
// {
//   "expert_response": "..."
// }
// =========================================================

export async function resolveCase(
  caseId: string,
  expertResponse: string
) {
  const response = await fetch(
    `${API_BASE_URL}/cases/${encodeURIComponent(caseId)}/resolve`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        expert_response: expertResponse,
      }),
    }
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.message ||
        `Failed to resolve case (${response.status})`
    );
  }

  return data;
}


// =========================================================
// GET ANALYTICS
// =========================================================

export async function getAnalytics() {
  const response = await fetch(
    `${API_BASE_URL}/analytics/`
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch analytics (${response.status})`
    );
  }

  const data = await response.json();

  return data?.metrics ?? data ?? {};
}


// =========================================================
// GET ACTIVE OUTBREAKS
// =========================================================

export async function getOutbreaks(
  threshold = 5
) {
  const response = await fetch(
    `${API_BASE_URL}/alerts/outbreaks?threshold=${threshold}`
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
    `${API_BASE_URL}/alerts/broadcast`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
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