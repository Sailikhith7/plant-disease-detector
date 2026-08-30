export type MockCase = {
  case_id: number;
  farmer_name: string;
  crop: string;
  disease: string;
  confidence: number;
  district: string;
  severity: "High" | "Medium" | "Low";
  status: string;

  // Location fields
  latitude?: number;
  longitude?: number;
  gps_lat?: number;
  gps_long?: number;

  // Case details
  image_url?: string;
  date?: string;

  // Resolution details
  resolution_date?: string;
  expert_diagnosis?: string;
  prescription?: string;
};


export const mockCases: MockCase[] = [

  // =========================================
  // PENDING EXPERT CASES
  // Confidence < 75%
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
    latitude: 20.42,
    longitude: 78.02,
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
    latitude: 20.15,
    longitude: 78.35,
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
    latitude: 20.31,
    longitude: 78.08,
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
    latitude: 20.27,
    longitude: 78.22,
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
    latitude: 20.36,
    longitude: 78.15,
  },

  {
    case_id: 102,
    farmer_name: "Suresh Shinde",
    crop: "Soybean",
    disease: "Soybean Rust",
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
    confidence: 68,
    district: "Nashik",
    severity: "Low",
    status: "Pending Expert",
    latitude: 20.01,
    longitude: 73.78,
  },


  // =========================================
  // RESOLVED CASES
  // Confidence >= 75%
  // =========================================

  {
    case_id: 104,
    farmer_name: "Ganesh More",
    crop: "Sugarcane",
    disease: "Red Rot",
    confidence: 82,
    district: "Kolhapur",
    severity: "High",
    status: "Resolved",
    latitude: 16.705,
    longitude: 74.24,
    resolution_date: "2026-08-20",
    expert_diagnosis:
      "Red rot symptoms were consistent with the field observations.",
    prescription:
      "Remove severely affected clumps and follow recommended disease management practices.",
  },

  {
    case_id: 105,
    farmer_name: "Vijay Pawar",
    crop: "Cotton",
    disease: "Cotton Leaf Curl",
    confidence: 79,
    district: "Akola",
    severity: "Medium",
    status: "Resolved",
    latitude: 20.70,
    longitude: 77.01,
    resolution_date: "2026-08-21",
    expert_diagnosis:
      "Cotton leaf curl symptoms were confirmed.",
    prescription:
      "Monitor whitefly activity and follow approved integrated pest management measures.",
  },

  {
    case_id: 106,
    farmer_name: "Prakash Deshmukh",
    crop: "Cotton",
    disease: "Pink Bollworm",
    confidence: 81,
    district: "Amravati",
    severity: "High",
    status: "Resolved",
    latitude: 20.93,
    longitude: 77.75,
    resolution_date: "2026-08-22",
    expert_diagnosis:
      "Pink Bollworm infestation was confirmed.",
    prescription:
      "Use recommended integrated pest management practices and monitor boll damage regularly.",
  },

  {
    case_id: 107,
    farmer_name: "Sunil Patil",
    crop: "Soybean",
    disease: "Soybean Rust",
    confidence: 88,
    district: "Latur",
    severity: "Medium",
    status: "Resolved",
    latitude: 18.40,
    longitude: 76.56,
    resolution_date: "2026-08-22",
    expert_diagnosis:
      "Soybean rust symptoms were confirmed.",
    prescription:
      "Monitor disease spread and follow the approved crop protection schedule.",
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
    resolution_date: "2026-08-23",
    expert_diagnosis:
      "Purple blotch symptoms were confirmed.",
    prescription:
      "Improve field sanitation and follow approved fungicide guidance.",
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
    resolution_date: "2026-08-23",
    expert_diagnosis:
      "Leaf spot symptoms were confirmed.",
    prescription:
      "Remove severely affected foliage and maintain recommended field hygiene.",
  },

  {
    case_id: 110,
    farmer_name: "Dinesh Pawar",
    crop: "Cotton",
    disease: "Cotton Leaf Curl",
    confidence: 84,
    district: "Wardha",
    severity: "Medium",
    status: "Resolved",
    latitude: 20.75,
    longitude: 78.60,
    resolution_date: "2026-08-24",
    expert_diagnosis:
      "Cotton leaf curl symptoms were confirmed.",
    prescription:
      "Monitor vector activity and follow approved integrated pest management measures.",
  },

  {
    case_id: 116,
    farmer_name: "Kavita Wankhede",
    crop: "Orange",
    disease: "Citrus Canker",
    confidence: 93,
    district: "Nagpur",
    severity: "High",
    status: "Resolved",
    latitude: 21.15,
    longitude: 79.09,
    resolution_date: "2026-08-24",
    expert_diagnosis:
      "Citrus canker symptoms were confirmed.",
    prescription:
      "Remove severely affected plant material and maintain orchard sanitation.",
  },

  {
    case_id: 117,
    farmer_name: "Sanjay Deshmukh",
    crop: "Soybean",
    disease: "Soybean Rust",
    confidence: 86,
    district: "Nagpur",
    severity: "Medium",
    status: "Resolved",
    latitude: 21.12,
    longitude: 79.08,
    resolution_date: "2026-08-25",
    expert_diagnosis:
      "Soybean rust symptoms were confirmed.",
    prescription:
      "Continue field monitoring and apply approved crop protection measures when required.",
  },

  {
    case_id: 118,
    farmer_name: "Rahul Shinde",
    crop: "Tomato",
    disease: "Early Blight",
    confidence: 83,
    district: "Nashik",
    severity: "Medium",
    status: "Resolved",
    latitude: 20.01,
    longitude: 73.78,
    resolution_date: "2026-08-25",
    expert_diagnosis:
      "Early blight was confirmed from the observed symptoms.",
    prescription:
      "Remove severely affected leaves and follow recommended fungicide practices.",
  },

  {
    case_id: 119,
    farmer_name: "Kiran Pawar",
    crop: "Grapes",
    disease: "Downy Mildew",
    confidence: 89,
    district: "Nashik",
    severity: "High",
    status: "Resolved",
    latitude: 20.18,
    longitude: 73.99,
    resolution_date: "2026-08-26",
    expert_diagnosis:
      "Downy mildew symptoms were confirmed.",
    prescription:
      "Improve canopy ventilation and follow approved disease management practices.",
  },

  {
    case_id: 120,
    farmer_name: "Vivek Deshmukh",
    crop: "Cotton",
    disease: "Cotton Leaf Curl",
    confidence: 78,
    district: "Nanded",
    severity: "Medium",
    status: "Resolved",
    latitude: 19.15,
    longitude: 77.32,
    resolution_date: "2026-08-26",
    expert_diagnosis:
      "Cotton leaf curl symptoms were confirmed.",
    prescription:
      "Monitor whitefly populations and follow integrated pest management measures.",
  },
];