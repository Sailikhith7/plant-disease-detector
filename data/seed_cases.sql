INSERT INTO cases (case_id, farmer_id, crop, disease, confidence, latitude, longitude, district, status, created_at)
VALUES
('case_01', 'FARM_101', 'Cotton', 'Pink Bollworm', 0.45, 20.3888, 78.1204, 'Yavatmal', 'pending_expert', NOW()),
('case_02', 'FARM_102', 'Soybean', 'Soybean Rust', 0.88, 19.1383, 77.3210, 'Nanded', 'auto_resolved', NOW()),
('case_03', 'FARM_103', 'Onion', 'Purple Blotch', 0.92, 19.9975, 73.7898, 'Nashik', 'auto_resolved', NOW()),
('case_04', 'FARM_104', 'Sugarcane', 'Red Rot', 0.40, 16.7050, 74.2433, 'Kolhapur', 'pending_expert', NOW()),
('case_05', 'FARM_105', 'Cotton', 'Leaf Curl Virus', 0.52, 20.7002, 77.0082, 'Akola', 'pending_expert', NOW());