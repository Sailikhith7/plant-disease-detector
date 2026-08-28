export type MockCase = {
  case_id: number;
  farmer_name: string;
  crop: string;
  disease: string;
  confidence: number;
  district: string;
  severity: "High" | "Medium" | "Low";
  status: "Pending Expert" | "Resolved";

  latitude: number;
  longitude: number;

  resolution_date?: string;
  expert_diagnosis?: string;
  prescription?: string;
};

export const mockCases: MockCase[] = [
  // =========================================
  // YAVATMAL OUTBREAK DEMO
  // 6 COMPLAINTS
  // =========================================

  {
    case_id: 101,
    farmer_name: "Ramesh Patil",
    crop: "Cotton",
    disease: "Pink Bollworm",
    confidence: 56,
    district: "Yavatmal",
    severity: "High",
    status: "Pending Expert",
    latitude: 20.389,
    longitude: 78.13,
  },

  {
    case_id: 111,
    farmer_name: "Santosh Shinde",
    crop: "Cotton",
    disease: "Pink Bollworm",
    confidence: 61,
    district: "Yavatmal",
    severity: "High",
    status: "Pending Expert",
    latitude: 20.389,
    longitude: 78.13,
  },

  {
    case_id: 112,
    farmer_name: "Ganesh Rathod",
    crop: "Cotton",
    disease: "Pink Bollworm",
    confidence: 58,
    district: "Yavatmal",
    severity: "High",
    status: "Pending Expert",
    latitude: 20.389,
    longitude: 78.13,
  },

  {
    case_id: 113,
    farmer_name: "Vilas Pawar",
    crop: "Cotton",
    disease: "Pink Bollworm",
    confidence: 64,
    district: "Yavatmal",
    severity: "Medium",
    status: "Pending Expert",
    latitude: 20.389,
    longitude: 78.13,
  },

  {
    case_id: 114,
    farmer_name: "Mahesh More",
    crop: "Cotton",
    disease: "Pink Bollworm",
    confidence: 59,
    district: "Yavatmal",
    severity: "High",
    status: "Pending Expert",
    latitude: 20.389,
    longitude: 78.13,
  },

  {
    case_id: 115,
    farmer_name: "Ravi Jadhav",
    crop: "Cotton",
    disease: "Pink Bollworm",
    confidence: 67,
    district: "Yavatmal",
    severity: "Medium",
    status: "Pending Expert",
    latitude: 20.389,
    longitude: 78.13,
  },

  // =========================================
  // OTHER DISTRICTS
  // =========================================

  {
    case_id: 102,
    farmer_name: "Suresh Shinde",
    crop: "Soybean",
    disease: "Rust",
    confidence: 62,
    district: "Nanded",
    severity: "Medium",
    status: "Pending Expert",
    latitude: 19.15,
    longitude: 77.32,
  },

  {
    case_id: 103,
    farmer_name: "Mahesh Jadhav",
    crop: "Onion",
    disease: "Purple Blotch",
    confidence: 43,
    district: "Nashik",
    severity: "High",
    status: "Pending Expert",
    latitude: 20.005,
    longitude: 73.78,
  },

  {
    case_id: 104,
    farmer_name: "Ganesh More",
    crop: "Sugarcane",
    disease: "Leaf Spot",
    confidence: 68,
    district: "Kolhapur",
    severity: "Medium",
    status: "Pending Expert",
    latitude: 16.705,
    longitude: 74.24,
  },

  {
    case_id: 105,
    farmer_name: "Vijay Pawar",
    crop: "Cotton",
    disease: "Leaf Curl",
    confidence: 51,
    district: "Akola",
    severity: "High",
    status: "Pending Expert",
    latitude: 20.70,
    longitude: 77.01,
  },

  // =========================================
  // RESOLVED CASES
  // =========================================

  {
    case_id: 106,
    farmer_name: "Prakash Deshmukh",
    crop: "Cotton",
    disease: "Pink Bollworm",
    confidence: 81,
    district: "Amravati",
    severity: "Medium",
    status: "Resolved",
    latitude: 20.93,
    longitude: 77.75,
    resolution_date: "2026-08-18",
    expert_diagnosis:
      "Pink Bollworm infestation confirmed.",
    prescription:
      "Follow approved integrated pest management practices and monitor affected plants regularly.",
  },

  {
    case_id: 107,
    farmer_name: "Sunil Patil",
    crop: "Soybean",
    disease: "Rust",
    confidence: 88,
    district: "Latur",
    severity: "Low",
    status: "Resolved",
    latitude: 18.40,
    longitude: 76.56,
    resolution_date: "2026-08-19",
    expert_diagnosis:
      "Soybean rust confirmed.",
    prescription:
      "Remove heavily affected leaves and follow the approved crop protection schedule.",
  },

  {
    case_id: 108,
    farmer_name: "Ajay More",
    crop: "Onion",
    disease: "Purple Blotch",
    confidence: 76,
    district: "Pune",
    severity: "Medium",
    status: "Resolved",
    latitude: 18.52,
    longitude: 73.86,
    resolution_date: "2026-08-20",
    expert_diagnosis:
      "Purple Blotch symptoms confirmed.",
    prescription:
      "Improve field sanitation and follow approved fungicide guidance from the agriculture department.",
  },

  {
    case_id: 109,
    farmer_name: "Sachin Jadhav",
    crop: "Sugarcane",
    disease: "Leaf Spot",
    confidence: 91,
    district: "Sangli",
    severity: "Low",
    status: "Resolved",
    latitude: 16.85,
    longitude: 74.58,
    resolution_date: "2026-08-21",
    expert_diagnosis:
      "Sugarcane leaf spot confirmed.",
    prescription:
      "Remove severely affected foliage and maintain recommended field hygiene.",
  },

  {
    case_id: 110,
    farmer_name: "Dinesh Pawar",
    crop: "Cotton",
    disease: "Leaf Curl",
    confidence: 84,
    district: "Wardha",
    severity: "Low",
    status: "Resolved",
    latitude: 20.75,
    longitude: 78.60,
    resolution_date: "2026-08-22",
    expert_diagnosis:
      "Cotton leaf curl symptoms confirmed.",
    prescription:
      "Monitor vector activity and follow approved integrated pest management measures.",
  },
];