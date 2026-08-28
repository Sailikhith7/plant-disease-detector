// Fetch active outbreaks
export async function getOutbreaks(threshold = 5) {
  const response = await fetch(
    `http://localhost:8000/api/alerts/outbreaks?threshold=${threshold}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch outbreaks");
  }

  return await response.json();
}


// Send broadcast advisory
export async function sendBroadcastAdvisory(payload: {
  district: string;
  crop: string;
  disease: string;
  custom_message: string;
}) {
  const response = await fetch(
    "http://localhost:8000/api/alerts/broadcast",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to send broadcast");
  }

  return await response.json();
}