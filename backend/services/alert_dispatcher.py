import os
import logging
from typing import Dict, List, Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlertDispatcher")

# Production Disease-to-Advisory Marathi Knowledge Engine
DISEASE_KNOWLEDGE_BASE: Dict[str, Dict[str, str]] = {
    "pink_bollworm": {
        "marathi_name": "गुलाबी बोंडअळी (Pink Bollworm)",
        "remedy_mr": "तात्काळ फेरोमोन ट्रॅप लावा आणि निंबोळी अर्क ५% किंवा प्रोफिनोफॉस ५०% EC (३० मिली/१० लिटर) फवारणी करा. महा-अॅग्रो केंद्रात अनुदान उपलब्ध आहे.",
        "remedy_hi": "तुरंत फेरोमोन ट्रैप लगाएं और नीम अर्क 5% या प्रोफिनोफॉस 50% EC कीटनाशक का छिड़काव करें।"
    },
    "soybean_rust": {
        "marathi_name": "सोयाबीन तांबेरा (Soybean Rust)",
        "remedy_mr": "हेक्साकोनाझोल ५% EC (१० मिली) किंवा टेब्युकोनाझोल (१० मिली/१० लिटर) पाणी मिसळून तात्काळ फवारणी करा.",
        "remedy_hi": "हेक्साकोनाज़ोल 5% EC या टेबुकोनाज़ोल का प्रति 10 लीटर पानी में मिलाकर छिड़काव करें।"
    },
    "cotton_leaf_curl": {
        "marathi_name": "कापूस पाने कुरळे रोग (Leaf Curl Virus)",
        "remedy_mr": "पांढऱ्या माशीच्या नियंत्रणासाठी डायमेथोएट ३०% EC (१५ मिली/१० लिटर) फवारा.",
        "remedy_hi": "सफेद मक्खी नियंत्रण के लिए डाइमेथोएट का छिड़काव करें।"
    },
    "tomato_early_blight": {
        "marathi_name": "टोमॅटो करपा रोग (Early Blight)",
        "remedy_mr": "मँकोझेब ७५% WP (२५ ग्रॅम/१० लिटर) किंवा कॉपर ऑक्सिक्लोराईडची फवारणी करा.",
        "remedy_hi": "मैंकोजेब 75% WP का छिड़काव करें।"
    }
}

class AlertDispatcher:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        self.client: Optional[Client] = None
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {str(e)}")

    def build_localized_sms(self, farmer_name: str, district: str, disease_key: str, custom_advisory: Optional[str] = None, lang: str = "mr") -> str:
        """Disease aur location ke hisaab se authentic Marathi/Hindi SMS generate karta hai"""
        disease_info = DISEASE_KNOWLEDGE_BASE.get(
            disease_key.lower().replace(" ", "_"), 
            {
                "marathi_name": disease_key,
                "remedy_mr": custom_advisory or "नजीकच्या कृषी विस्तार अधिकाऱ्यांशी संपर्क साधावा.",
                "remedy_hi": custom_advisory or "निकटतम कृषि विशेषज्ञ से संपर्क करें।"
            }
        )

        disease_label = disease_info["marathi_name"] if lang == "mr" else disease_key
        advisory_body = custom_advisory if custom_advisory else disease_info.get(f"remedy_{lang}", disease_info["remedy_mr"])

        if lang == "mr":
            return (
                f"🚨 [PeekRakshak कृषी चेतावणी]\n"
                f"शेतकरी बांधव {farmer_name},\n"
                f"{district} जिल्ह्यात '{disease_label}' प्रादुर्भाव नोंदवला गेला आहे.\n\n"
                f"तातडीचा उपाय:\n{advisory_body}\n\n"
                f"MahaAgro केंद्रात अनुदानित औषधे उपलब्ध आहेत."
            )
        else:
            return (
                f"🚨 [PeekRakshak Alert]\n"
                f"किसान {farmer_name},\n"
                f"{district} जिले में '{disease_key}' का प्रकोप देखा गया है।\n\n"
                f"सलाह:\n{advisory_body}"
            )

    def dispatch_sms(self, to_phone: str, body: str) -> Dict:
        """Twilio Live API endpoint execution"""
        if not self.client or not self.from_number:
            logger.warning(f"[GATEWAY UNCONFIGURED] SMS to {to_phone} simulated. Twilio credentials not found in env.")
            return {"success": True, "provider": "simulation", "to": to_phone, "sid": "SIMULATED_SID"}
        
        try:
            message = self.client.messages.create(
                body=body,
                from_=self.from_number,
                to=to_phone
            )
            logger.info(f"SMS dispatched to {to_phone} successfully. SID: {message.sid}")
            return {"success": True, "provider": "twilio", "to": to_phone, "sid": message.sid}
        except TwilioRestException as e:
            logger.error(f"Twilio API Error sending to {to_phone}: {e.msg} (Code: {e.code})")
            return {"success": False, "error": e.msg, "code": e.code}

# Singleton instance for Backend Routes
dispatcher = AlertDispatcher()

def trigger_outbreak_broadcast(district: str, disease_key: str, custom_advisory: Optional[str] = None, target_farmers: Optional[List[Dict]] = None) -> Dict:
    """
    Production entrypoint: Backend API isko direct call karega jab dashboard se trigger aayega.
    """
    # Demo targets fallback
    if not target_farmers:
        target_farmers = [
            {"name": "Ramesh Patil", "phone": "+919876543210", "lang": "mr"},
            {"name": "Suresh Deshmukh", "phone": "+919811122233", "lang": "mr"}
        ]

    results = []
    for farmer in target_farmers:
        message_text = dispatcher.build_localized_sms(
            farmer_name=farmer["name"],
            district=district,
            disease_key=disease_key,
            custom_advisory=custom_advisory,
            lang=farmer.get("lang", "mr")
        )
        res = dispatcher.dispatch_sms(farmer["phone"], message_text)
        results.append(res)

    return {
        "status": "completed",
        "district": district,
        "disease": disease_key,
        "total_dispatched": len(results),
        "details": results
    }

if __name__ == "__main__":
    print("Testing Live Advisory Builder & Dispatch Pipeline...")
    output = trigger_outbreak_broadcast(
        district="Yavatmal",
        disease_key="pink_bollworm"
    )
    print("\nExecution Summary:", output)
