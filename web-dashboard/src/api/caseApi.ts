import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export type CaseStatus =
  | "pending"
  | "Pending Expert"
  | "resolved";

export type CaseItem = {
  case_id: number;
  farmer_name?: string;
  crop: string;
  disease: string;
  confidence: number;
  district?: string;
  latitude?: number;
  longitude?: number;
  severity?: "High" | "Medium" | "Low";
  status: CaseStatus;
};

export async function getPendingCases() {
  const response = await api.get("/api/cases", {
    params: {
      status: "Pending Expert",
    },
  });

  return response.data;
}

export async function getCase(caseId: number) {
  const response = await api.get(`/api/cases/${caseId}`);

  return response.data;
}

export async function resolveCase(
  caseId: number,
  data: {
    expert_diagnosis: string;
    prescription: string;
  }
) {
  const response = await api.patch(
    `/api/cases/${caseId}`,
    data
  );

  return response.data;
}

export async function getHotspots() {
  const response = await api.get(
    "/api/analytics/hotspots"
  );

  return response.data;
}