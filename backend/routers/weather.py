import os
import requests
from typing import Optional
from fastapi import APIRouter, Query, BackgroundTasks
from pydantic import BaseModel

router = APIRouter(
    prefix="/weather",
    tags=["Weather Risk & Telegram Outbreak Advisory"]
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
DEFAULT_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

DISTRICT_COORDINATES = {
    "Ahilyanagar (Ahmednagar)": {"lat": 19.0952, "lon": 74.7496},
    "Akola": {"lat": 20.7002, "lon": 77.0082},
    "Amravati": {"lat": 20.9374, "lon": 77.7796},
    "Beed": {"lat": 18.9891, "lon": 75.7601},
    "Bhandara": {"lat": 21.1714, "lon": 79.6547},
    "Buldhana": {"lat": 20.5293, "lon": 76.1843},
    "Chandrapur": {"lat": 19.9615, "lon": 79.2961},
    "Chhatrapati Sambhajinagar (Aurangabad)": {"lat": 19.8762, "lon": 75.3433},
    "Dhule": {"lat": 20.9042, "lon": 74.7749},
    "Jalgaon": {"lat": 21.0077, "lon": 75.5626},
    "Kolhapur": {"lat": 16.7050, "lon": 74.2433},
    "Nagpur": {"lat": 21.1458, "lon": 79.0882},
    "Nashik": {"lat": 19.9975, "lon": 73.7898},
    "Pune": {"lat": 18.5204, "lon": 73.8567},
    "Ratnagiri": {"lat": 16.9902, "lon": 73.3120},
    "Solapur": {"lat": 17.6599, "lon": 75.9064},
    "Wardha": {"lat": 20.7453, "lon": 78.6022},
    "Yavatmal": {"lat": 20.3888, "lon": 78.1204}
}

# Multi-Disease Risk Matrix for 5 Crops
CROP_DISEASE_RULES = {
    "cotton": [
        {
            "disease": "Bacterial Blight / करपा (Cotton)",
            "min_temp": 22.0, "max_temp": 34.0, "min_humidity": 70.0,
            "advisory_mr": "हवेत अति-आर्द्रतेमुळे करपा रोगाचा धोका आहे. कॉपर ऑक्सिक्लोराईड @ २५ ग्रॅम/१० ली. फवारा.",
            "advisory_hi": "हवा में अधिक नमी से करपा/झुलसा रोग का खतरा है। कॉपर ऑक्सीक्लोराइड 50% WP का छिड़काव करें।",
            "advisory_en": "High risk of Bacterial Blight due to humid conditions. Spray Copper Oxychloride 50% WP."
        },
        {
            "disease": "Grey Mildew / दहिया रोग",
            "min_temp": 18.0, "max_temp": 28.0, "min_humidity": 60.0,
            "advisory_mr": "ढगाळ वातावरणामुळे दहिया रोगाचा प्रादुर्भाव संभवतो. कार्बेन्डाझिम फवारा.",
            "advisory_hi": "बादल छाए रहने से दहिया रोग का जोखिम। कार्बेन्डाजिम का छिड़काव करें।",
            "advisory_en": "Moderate risk of Grey Mildew. Spray Carbendazim 50% WP."
        }
    ],
    "rice": [
        {
            "disease": "Rice Blast / भात करपा",
            "min_temp": 18.0, "max_temp": 30.0, "min_humidity": 70.0,
            "advisory_mr": "ढगाळ वातावरण व आर्द्रतेमुळे भातावर करप्याचा धोका. ट्रायसायक्लॅझोल ७५% WP फवारा.",
            "advisory_hi": "नमी और बादलों के कारण धान में ब्लास्ट/करपा का खतरा। ट्राइसाइक्लाजोल 75% WP का छिड़काव करें।",
            "advisory_en": "High Blast risk detected due to overcast sky. Apply Tricyclazole 75% WP."
        },
        {
            "disease": "Brown Spot / तपकिरी ठिपके",
            "min_temp": 24.0, "max_temp": 34.0, "min_humidity": 65.0,
            "advisory_mr": "तपकिरी ठिपके रोगासाठी पोषक हवामान. मॅन्कोझेब २.५ ग्रॅम/ली फवारावे.",
            "advisory_hi": "ब्राउन स्पॉट रोग के अनुकूल मौसम। मैंकोजेब का छिड़काव करें।",
            "advisory_en": "Risk of Brown Leaf Spot. Apply Mancozeb @ 2.5g/L water."
        }
    ],
    "groundnut": [
        {
            "disease": "Tikka Leaf Spot / टिक्का रोग",
            "min_temp": 20.0, "max_temp": 32.0, "min_humidity": 68.0,
            "advisory_mr": "टिक्का रोगास पोषक हवामान. कार्बेन्डाझिम १२% + मॅन्कोझेब ६३% WP फवारा.",
            "advisory_hi": "टिक्का रोग का जोखिम। कार्बेन्डाजिम + मैंकोजेब का निवारक छिड़काव करें।",
            "advisory_en": "Outbreak risk for Tikka Leaf Spot. Spray Mancozeb + Carbendazim."
        }
    ],
    "ragi": [
        {
            "disease": "Ragi Blast / मानमोडी करपा",
            "min_temp": 20.0, "max_temp": 32.0, "min_humidity": 65.0,
            "advisory_mr": "नाचणीवर मानमोडी/करपा रोगाचा प्रादुर्भाव संभवतो. ५% निंबोळी अर्क फवारा.",
            "advisory_hi": "रागी पर ब्लास्ट रोग का जोखिम। 5% नीम अर्क का छिड़काव करें।",
            "advisory_en": "Weather triggers Ragi Blast. Spray 5% Neem Seed Extract."
        }
    ],
    "sugarcane": [
        {
            "disease": "Red Rot / लाल कुज",
            "min_temp": 26.0, "max_temp": 38.0, "min_humidity": 65.0,
            "advisory_mr": "शेतात ओलावा वाढल्यास लाल कुज रोगाचा धोका. पाण्याचा त्वरित निचरा करा.",
            "advisory_hi": "खेत में नमी से लाल सड़न का खतरा। जल निकासी सुनिश्चित करें।",
            "advisory_en": "Risk of Red Rot. Ensure immediate soil drainage."
        }
    ]
}


def send_telegram_alert_sync(district: str, crop: str, disease: str, risk_percent: int, advisory: str):
    if not TELEGRAM_BOT_TOKEN:
        print(f"[Telegram Alert Log] {district} | {crop} | {disease} | {risk_percent}%")
        return True

    text = (
        f"🚨 *कृषी हवामान इशारा | PikRakshak Alert*\n\n"
        f"📍 *District/जिल्हा:* {district}\n"
        f"🌾 *Crop/पीक:* {crop.upper()}\n"
        f"🦠 *Potential Disease:* {disease} ({risk_percent}% Risk)\n\n"
        f"📢 *Advisory:* {advisory}\n\n"
        f"_Automated Agrometeorological Warning System_"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": DEFAULT_CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=4)
        return True
    except Exception as e:
        print(f"Telegram error: {e}")
        return False


def fetch_open_meteo(lat: float, lon: float):
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        "&forecast_days=5&timezone=auto"
    )
    try:
        resp = requests.get(url, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            curr = data.get("current", {})
            daily = data.get("daily", {})

            forecast = []
            dates = daily.get("time", [])
            t_max = daily.get("temperature_2m_max", [])
            t_min = daily.get("temperature_2m_min", [])
            rain_probs = daily.get("precipitation_probability_max", [])

            for i in range(len(dates)):
                forecast.append({
                    "date": dates[i],
                    "max_temp": t_max[i] if i < len(t_max) else 31.0,
                    "min_temp": t_min[i] if i < len(t_min) else 22.0,
                    "rain_prob": rain_probs[i] if i < len(rain_probs) else 20
                })

            wind = curr.get("wind_speed_10m", 11.0)
            return {
                "temperature": curr.get("temperature_2m", 28.5),
                "humidity": curr.get("relative_humidity_2m", 65.0),
                "rain_prob": rain_probs[0] if rain_probs else 20,
                "wind_speed": wind,
                "uv_index": 6,
                "spray_safe": (wind < 15.0 and curr.get("precipitation", 0.0) == 0.0),
                "forecast_5days": forecast
            }
    except Exception:
        pass

    return {
        "temperature": 28.0,
        "humidity": 65.0,
        "rain_prob": 20,
        "wind_speed": 10.0,
        "uv_index": 6,
        "spray_safe": True,
        "forecast_5days": [
            {"date": "08-31", "max_temp": 30.0, "min_temp": 22.0, "rain_prob": 20},
            {"date": "09-01", "max_temp": 29.0, "min_temp": 21.0, "rain_prob": 40},
            {"date": "09-02", "max_temp": 28.0, "min_temp": 21.0, "rain_prob": 60},
            {"date": "09-03", "max_temp": 31.0, "min_temp": 23.0, "rain_prob": 15},
            {"date": "09-04", "max_temp": 32.0, "min_temp": 24.0, "rain_prob": 10}
        ]
    }


class SimulationInput(BaseModel):
    crop: str = "cotton"
    district: str = "Dhule"
    temperature: float = 28.0
    humidity: float = 85.0
    rain_prob: float = 60.0
    language: str = "mr"
    trigger_telegram: bool = False


@router.get("/full-dashboard")
def get_full_weather_dashboard(
    crop: str = Query("rice"),
    district: str = Query("Dhule"),
    language: str = Query("mr")
):
    crop_key = crop.lower().strip()
    coords = DISTRICT_COORDINATES.get(district, {"lat": 20.9042, "lon": 74.7749})
    weather = fetch_open_meteo(coords["lat"], coords["lon"])

    rules = CROP_DISEASE_RULES.get(crop_key, CROP_DISEASE_RULES["cotton"])
    outbreak = False
    triggered_disease = None
    advisory = ""
    risk_percent = 25

    for rule in rules:
        if (rule["min_temp"] <= weather["temperature"] <= rule["max_temp"]) and (weather["humidity"] >= rule["min_humidity"]):
            outbreak = True
            risk_percent = 88 if weather["humidity"] < 80 else 94
            triggered_disease = rule["disease"]
            advisory = rule.get(f"advisory_{language}", rule["advisory_en"])
            break

    if not outbreak:
        if language == "hi":
            advisory = f"अगले ५ दिनों में {crop.capitalize()} फसल के लिए मौसम सुरक्षित और रोगमुक्त रहेगा।"
        elif language == "mr":
            advisory = f"पुढील ५ दिवसांत {crop.capitalize()} पिकासाठी हवामान अनुकूल व रोगमुक्त राहील."
        else:
            advisory = f"Weather conditions for {crop.capitalize()} are safe and optimal for the next 5 days."

    return {
        "status": "success",
        "district": district,
        "crop": crop,
        "weather": weather,
        "risk_assessment": {
            "is_outbreak_risk": outbreak,
            "risk_percentage": risk_percent,
            "potential_disease": triggered_disease,
            "preventive_advisory": advisory
        }
    }


@router.post("/simulate")
def simulate_and_dispatch(data: SimulationInput, background_tasks: BackgroundTasks):
    crop_key = data.crop.lower().strip()
    rules = CROP_DISEASE_RULES.get(crop_key, CROP_DISEASE_RULES["cotton"])

    outbreak = False
    triggered_disease = None
    advisory = ""
    risk_percent = 20

    for rule in rules:
        if (rule["min_temp"] <= data.temperature <= rule["max_temp"]) and (data.humidity >= rule["min_humidity"]):
            outbreak = True
            risk_percent = 92 if data.humidity >= 80 else 82
            triggered_disease = rule["disease"]
            advisory = rule.get(f"advisory_{data.language}", rule["advisory_en"])
            break

    if not outbreak:
        t = round(data.temperature, 1)
        h = round(data.humidity, 1)
        if data.language == "hi":
            advisory = f"इस तापमान ({t}°C) और आर्द्रता ({h}%) पर {data.crop.capitalize()} फसल सुरक्षित है।"
        elif data.language == "mr":
            advisory = f"या तापमानात ({t}°C) आणि आर्द्रतेत ({h}%) {data.crop.capitalize()} पिकाला कोणताही धोका नाही."
        else:
            advisory = f"At {t}°C and {h}% humidity, conditions are safe for {data.crop.capitalize()}."

    if data.trigger_telegram and outbreak:
        background_tasks.add_task(
            send_telegram_alert_sync,
            data.district,
            data.crop,
            triggered_disease or "Fungal Infection",
            risk_percent,
            advisory
        )

    return {
        "status": "success",
        "simulated": True,
        "is_outbreak_risk": outbreak,
        "risk_percentage": risk_percent,
        "potential_disease": triggered_disease,
        "advisory": advisory,
        "telegram_dispatched": data.trigger_telegram and outbreak
    }

