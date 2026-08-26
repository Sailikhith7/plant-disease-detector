import os
from typing import List, Dict

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "mock_sid")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "mock_token")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+1234567890")

DEMO_FARMERS_REGISTRY = [
    {
        "farmer_id": "FARM_101",
        "name": "Ramesh Patil",
        "district": "Yavatmal",
        "phone": "+919876543210",
        "preferred_lang": "mr"
    },
    {
        "farmer_id": "FARM_102",
        "name": "Suresh Deshmukh",
        "district": "Yavatmal",
        "phone": "+919811122233",
        "preferred_lang": "mr"
    },
    {
        "farmer_id": "FARM_103",
        "name": "Kishore Jadhav",
        "district": "Nanded",
        "phone": "+919844455566",
        "preferred_lang": "hi"
    }
]

ALERT_TEMPLATES = {
    "mr": (
        "🚨 [PeekRakshak Alert]\n"
        "नमस्कार {name} शेतकरी बांधव,\n"
        "{district} जिल्ह्यात '{disease}' रोगाचा प्रादुर्भाव आढळला आहे.\n"
        "उपाय: {advisory}\n"
        "नजीकच्या महा-अॅग्रो केंद्रात अनुदानित औषध उपलब्ध आहे."
    ),
    "hi": (
        "🚨 [PeekRakshak Alert]\n"
        "किसान भाई {name},\n"
        "{district} जिले में '{disease}' का प्रकोप पाया गया है।\n"
        "सलाह: {advisory}\n"
        "निकटतम कृषि केंद्र से संपर्क करें।"
    )
}

def get_farmers_by_district(district: str) -> List[Dict]:
    return [f for f in DEMO_FARMERS_REGISTRY if f["district"].lower() == district.lower()]

def send_sms_alert(to_phone: str, message_body: str) -> bool:
    try:
        if TWILIO_ACCOUNT_SID == "mock_sid" or "your_account_sid" in TWILIO_ACCOUNT_SID:
            print(f"\n[MOCK SMS DISPATCHED] -> To: {to_phone}")
            print(f"Message Content:\n{message_body}\n" + "-"*50)
            return True
        
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone
        )
        print(f"[SUCCESS] SMS sent to {to_phone} (SID: {message.sid})")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send SMS to {to_phone}: {str(e)}")
        return False

def broadcast_district_alert(district: str, disease: str, advisory: str) -> Dict:
    target_farmers = get_farmers_by_district(district)
    if not target_farmers:
        return {"status": "warning", "message": f"No farmers registered under {district}", "dispatched": 0}
    
    success_count = 0
    for farmer in target_farmers:
        lang = farmer.get("preferred_lang", "mr")
        template = ALERT_TEMPLATES.get(lang, ALERT_TEMPLATES["mr"])
        
        sms_text = template.format(
            name=farmer["name"],
            district=district,
            disease=disease,
            advisory=advisory
        )
        
        if send_sms_alert(farmer["phone"], sms_text):
            success_count += 1
            
    return {
        "status": "success",
        "district": district,
        "total_targets": len(target_farmers),
        "dispatched_count": success_count
    }

if __name__ == "__main__":
    print("========================================")
    print("  PEEKRAKSHAK SMS BOT SIMULATION")
    print("========================================")
    result = broadcast_district_alert(
        district="Yavatmal",
        disease="Pink Bollworm (बोंडअळी)",
        advisory="तात्काळ Neem Cake (Rs. 180) आणि Pheromone Trap चा वापर करा."
    )
    print("\nExecution Result:", result)
