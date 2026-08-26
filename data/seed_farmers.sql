CREATE TABLE IF NOT EXISTS farmers (
    id SERIAL PRIMARY KEY,
    farmer_id VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    district VARCHAR(50) NOT NULL,
    taluka VARCHAR(50),
    primary_crop VARCHAR(50) NOT NULL,
    preferred_lang VARCHAR(10) DEFAULT 'mr',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alert_dispatches (
    id SERIAL PRIMARY KEY,
    case_id VARCHAR(100),
    district VARCHAR(50) NOT NULL,
    disease VARCHAR(100) NOT NULL,
    farmer_phone VARCHAR(20) NOT NULL,
    message_body TEXT NOT NULL,
    gateway_status VARCHAR(50) NOT NULL,
    dispatched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO farmers (farmer_id, full_name, phone_number, district, taluka, primary_crop, preferred_lang)
VALUES
('MH_YAV_001', 'Ramesh Patil', '+919876543210', 'Yavatmal', 'Pusad', 'Cotton', 'mr'),
('MH_YAV_002', 'Suresh Deshmukh', '+919811122233', 'Yavatmal', 'Darwha', 'Cotton', 'mr'),
('MH_NAN_001', 'Kishore Jadhav', '+919844455566', 'Nanded', 'Hadgaon', 'Soybean', 'mr'),
('MH_NAS_001', 'Sunil Shinde', '+919833344455', 'Nashik', 'Niphad', 'Tomato', 'mr'),
('MH_AKO_001', 'Gajanan Raut', '+919822233344', 'Akola', 'Akot', 'Cotton', 'mr')
ON CONFLICT (farmer_id) DO NOTHING;
