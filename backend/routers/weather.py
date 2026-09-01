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

# Multi-Condition Agronomic Pathogen Matrix per Crop
CROP_DISEASE_MATRIX = {
    "cotton": [
        {
            "disease_en": "Cotton Bacterial Blight / Black Arm",
            "disease_hi": "कपास का झुलसा / करपा रोग",
            "disease_mr": "कापूस जिवाणू करपा",
            "condition": lambda t, h, r: h >= 80.0 and r >= 40.0 and 24.0 <= t <= 33.0,
            "risk_calc": lambda t, h, r: min(95, int(50 + (h - 80) * 2 + (r - 40) * 0.5)),
            "advisory_en": "Continuous moisture detected ({h}% hum, {r}% rain). Spray Copper Oxychloride 50% WP @ 25g/10L water.",
            "advisory_hi": "लगातार नमी और बारिश ({h}% आर्द्रता). कॉपर ऑक्सीक्लोराइड 50% WP @ 2.5 ग्राम/लीटर का छिड़काव करें।",
            "advisory_mr": "अति-आर्द्र हवामान ({h}% आर्द्रता). कॉपर ऑक्सिक्लोराईड @ २५ ग्रॅम/१० ली. पाण्यात मिसळून फवारा."
        },
        {
            "disease_en": "Cotton Grey Mildew / Dahiya",
            "disease_hi": "दहिया रोग (ग्रे मिल्ड्यू)",
            "disease_mr": "दहिया रोग",
            "condition": lambda t, h, r: 65.0 <= h < 80.0 and 20.0 <= t <= 30.0,
            "risk_calc": lambda t, h, r: min(75, int(40 + (h - 65) * 1.5)),
            "advisory_en": "Moderate humidity ({h}%) and warm temp ({t}°C) favor Grey Mildew. Spray Carbendazim 50% WP @ 1g/L.",
            "advisory_hi": "मध्यम आर्द्रता ({h}%) व तापमान ({t}°C) से दहिया का खतरा। कार्बेन्डाजिम 50% WP @ 1 ग्राम/लीटर छिड़कें।",
            "advisory_mr": "ढगाळ व दमट वातावरणामुळे ({h}%) दहिया रोगाचा धोका. कार्बेन्डाझिम ५०% WP @ १ ग्रॅम/लीटर फवारा."
        },
        {
            "disease_en": "Sucking Pests (Aphids & Thrips)",
            "disease_hi": "रस चूसक कीट (माहू व थ्रिप्स)",
            "disease_mr": "रसशोषक किडे (मावा व तुडतुडे)",
            "condition": lambda t, h, r: t > 32.0 and h < 60.0,
            "risk_calc": lambda t, h, r: min(80, int(45 + (t - 32) * 4)),
            "advisory_en": "Dry hot weather ({t}°C) accelerates pest multiplication. Install yellow sticky traps and monitor undersides of leaves.",
            "advisory_hi": "गर्म और शुष्क मौसम ({t}°C). पीले चिपचिपे ट्रैप लगाएं और पत्तों के नीचे निगरानी करें।",
            "advisory_mr": "कोरडे व उष्ण हवामान ({t}°C). पिवळे चिकट सापळे लावा आणि नियमित पाहणी करा."
        }
    ],
    "rice": [
        {
            "disease_en": "Rice Sheath Blight & Brown Spot",
            "disease_hi": "धान का शीथ ब्लाइट व भूरा धब्बा",
            "disease_mr": "भात पानांवरील तपकिरी ठिपके व करपा",
            "condition": lambda t, h, r: h >= 70.0 and 25.0 <= t <= 34.0,
            "risk_calc": lambda t, h, r: min(85, int(45 + (h - 70) * 1.8)),
            "advisory_en": "Warm humid conditions ({t}°C, {h}% humidity) trigger fungal sheath blight. Apply Hexaconazole 5% EC @ 2ml/L.",
            "advisory_hi": "गर्म व नम वातावरण ({t}°C, {h}% नमी) से शीथ ब्लाइट का खतरा। हेक्साकोनाजोल 5% EC का छिड़काव करें।",
            "advisory_mr": "उष्ण व दमट हवामान ({t}°C, {h}% आर्द्रता). हेक्साकोनाझोल ५% EC @ २ मिली/लीटर फवारावे."
        },
        {
            "disease_en": "Rice Blast (Pyricularia)",
            "disease_hi": "धान का ब्लास्ट (झोंका रोग)",
            "disease_mr": "भात मानमोडी करपा (ब्लास्ट)",
            "condition": lambda t, h, r: h >= 80.0 and 18.0 <= t <= 25.0,
            "risk_calc": lambda t, h, r: min(92, int(55 + (h - 80) * 2.5)),
            "advisory_en": "Cool daytime temp ({t}°C) and morning dew trigger Rice Blast. Apply Tricyclazole 75% WP @ 0.6g/L immediately.",
            "advisory_hi": "ठंडा मौसम ({t}°C) व भारी ओस से ब्लास्ट का उच्च प्रकोप। ट्राइसाइक्लाजोल 75% WP का छिड़काव करें।",
            "advisory_mr": "थंड हवामान ({t}°C) व अति-दव पडल्यास ब्लास्टचा उद्रेक. ट्रायसायक्लॅझोल ७५% WP त्वरित फवारावे."
        }
    ],
    "groundnut": [
        {
            "disease_en": "Tikka Leaf Spot (Cercospora)",
            "disease_hi": "मूंगफली का टिक्का रोग",
            "disease_mr": "भुईमूग टिक्का रोग",
            "condition": lambda t, h, r: h >= 68.0 and 22.0 <= t <= 32.0,
            "risk_calc": lambda t, h, r: min(82, int(40 + (h - 68) * 2.0)),
            "advisory_en": "Foliar wetness ({h}% humidity) promotes leaf spot pustules. Spray Mancozeb 75% WP @ 2.5g/L.",
            "advisory_hi": "हवा में आर्द्रता ({h}%). टिक्का रोग रोकथाम हेतु मैंकोजेब 75% WP @ 2.5 ग्राम/लीटर छिड़कें।",
            "advisory_mr": "हवेतील ओलावा ({h}%). टिक्का नियंत्रणासाठी मॅन्कोझेब ७५% WP @ २.५ ग्रॅम/लीटर फवारा."
        },
        {
            "disease_en": "Collar Rot / Root Sclerotium",
            "disease_hi": "कॉलर रोट / जड़ सड़न",
            "disease_mr": "खोडकुज / मुळकुज",
            "condition": lambda t, h, r: r >= 50.0 or (h >= 85.0 and t >= 30.0),
            "risk_calc": lambda t, h, r: min(90, int(50 + (r - 50) * 0.8)),
            "advisory_en": "Excess soil moisture ({r}% rain). Drench root zone with Trichoderma viride bio-fungicide.",
            "advisory_hi": "खेत में अत्यधिक पानी ({r}% बारिश). ट्राइकोडर्मा विरिडी से जड़ क्षेत्र में ड्रेन्चिंग करें।",
            "advisory_mr": "शेतात पाणी साचल्यास खोडकुजचा धोका. ट्रायकोडर्मा व्हिरिडीची आळवणी (drenching) करावी."
        }
    ],
    "ragi": [
        {
            "disease_en": "Ragi Blast & Leaf Spot",
            "disease_hi": "रागी करपा / ब्लास्ट रोग",
            "disease_mr": "नाचणी मानमोडी / करपा",
            "condition": lambda t, h, r: h >= 75.0 and 20.0 <= t <= 30.0,
            "risk_calc": lambda t, h, r: min(78, int(40 + (h - 75) * 1.8)),
            "advisory_en": "Mild humidity risk ({h}%). Spray 5% Neem Seed Kernel Extract preventively.",
            "advisory_hi": "मध्यम आर्द्रता ({h}%). बचाव के लिए 5% नीम अर्क का छिड़काव करें।",
            "advisory_mr": "हवेत आर्द्रता वाढल्यास ({h}%) ५% निंबोळी अर्काची प्रतिबंधात्मक फवारणी करा."
        }
    ],
    "sugarcane": [
        {
            "disease_en": "Sugarcane Red Rot",
            "disease_hi": "गन्ने का लाल सड़न रोग",
            "disease_mr": "ऊस लाल कुज (रेड रॉट)",
            "condition": lambda t, h, r: r >= 50.0 and t >= 28.0,
            "risk_calc": lambda t, h, r: min(88, int(50 + (r - 50) * 0.8)),
            "advisory_en": "Water stagnation detected ({r}% rain risk). Ensure field furrow drainage immediately.",
            "advisory_hi": "जलभराव का जोखिम ({r}% बारिश). खेत की नालियों से पानी की त्वरित निकासी सुनिश्चित करें।",
            "advisory_mr": "पाणी साचल्यास लाल कुजचा धोका. शेतातील पाण्याचा त्वरित निचरा करा."
        }
    ]
}

def reverse_geocode(lat: float, lon: float) -> str:
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    headers = {"User-Agent": "KisanMitra-AgroEngine/1.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            address = data.get("address", {})
            district = address.get("state_district") or address.get("county") or address.get("district") or address.get("city")
            state = address.get("state", "")
            if district and state:
                return f"{district}, {state}"
            elif district:
                return district
    except Exception:
        pass
    return "Guntur, Andhra Pradesh"

def fetch_open_meteo(lat: float, lon: float):
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
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

            wind = curr.get("wind_speed_10m", 8.0)
            rain_prob_curr = rain_probs[0] if rain_probs else 20.0
            precip = curr.get("precipitation", 0.0)

            # Strict Scientific Spray Safe Logic:
            # Spraying is strictly UNSAFE if rain chance >= 30%, wind >= 15 km/h, or currently precipitating
            spray_safe = (rain_prob_curr < 30.0 and wind < 15.0 and precip == 0.0)

            return {
                "temperature": curr.get("temperature_2m", 28.0),
                "humidity": curr.get("relative_humidity_2m", 70.0),
                "rain_prob": rain_prob_curr,
                "wind_speed": wind,
                "spray_safe": spray_safe,
                "forecast_5days": forecast
            }
    except Exception:
        pass

    return {
        "temperature": 28.2,
        "humidity": 72.0,
        "rain_prob": 43.0,
        "wind_speed": 5.2,
        "spray_safe": False,
        "forecast_5days": []
    }

def evaluate_crop_weather_risk(crop_key: str, temp: float, humidity: float, rain_prob: float, language: str):
    rules = CROP_DISEASE_MATRIX.get(crop_key, CROP_DISEASE_MATRIX["cotton"])
    t = round(temp, 1)
    h = round(humidity, 1)
    r = round(rain_prob, 1)

    for rule in rules:
        if rule["condition"](t, h, r):
            risk_pct = rule["risk_calc"](t, h, r)
            is_outbreak = risk_pct >= 70
            status = "HIGH_RISK" if is_outbreak else "MODERATE"
            
            disease_name = rule.get(f"disease_{language}", rule["disease_en"])
            raw_advisory = rule.get(f"advisory_{language}", rule["advisory_en"])
            formatted_advisory = raw_advisory.format(t=t, h=h, r=r)

            return {
                "crop": crop_key,
                "status": status,
                "risk_percentage": risk_pct,
                "is_outbreak_risk": is_outbreak,
                "potential_disease": disease_name,
                "advisory": formatted_advisory
            }

    # Safe Optimal State
    if language == "hi":
        safe_msg = f"वर्तमान तापमान ({t}°C) और आर्द्रता ({h}%) पर {crop_key.capitalize()} फसल सुरक्षित व रोगमुक्त है।"
    elif language == "mr":
        safe_msg = f"सध्याच्या तापमानात ({t}°C) आणि आर्द्रतेत ({h}%) {crop_key.capitalize()} पिकावर रोगाचा कोणताही धोका नाही."
    else:
        safe_msg = f"Current weather ({t}°C, {h}% humidity) is optimal and disease-free for {crop_key.capitalize()}."

    return {
        "crop": crop_key,
        "status": "OPTIMAL",
        "risk_percentage": 15,
        "is_outbreak_risk": False,
        "potential_disease": None,
        "advisory": safe_msg
    }

class SimulationInput(BaseModel):
    crop: str = "cotton"
    district: str = "Live Location"
    temperature: float = 28.0
    humidity: float = 85.0
    rain_prob: float = 60.0
    language: str = "mr"
    trigger_telegram: bool = False

@router.get("/crops-suitability")
def get_all_crops_suitability(
    lat: float = Query(16.49),
    lon: float = Query(80.50),
    district: Optional[str] = Query(None),
    language: str = Query("en")
):
    actual_district = district if (district and not district.startswith("Maharashtra")) else reverse_geocode(lat, lon)
    weather = fetch_open_meteo(lat, lon)
    
    crops_res = {}
    for c_key in CROP_DISEASE_MATRIX.keys():
        crops_res[c_key] = evaluate_crop_weather_risk(
            crop_key=c_key,
            temp=weather["temperature"],
            humidity=weather["humidity"],
            rain_prob=weather["rain_prob"],
            language=language
        )

    return {
        "status": "success",
        "district": actual_district,
        "coordinates": {"lat": lat, "lon": lon},
        "weather": weather,
        "crops": crops_res
    }

@router.get("/full-dashboard")
def get_full_weather_dashboard(
    crop: str = Query("cotton"),
    district: Optional[str] = Query(None),
    lat: Optional[float] = Query(16.49),
    lon: Optional[float] = Query(80.50),
    language: str = Query("en")
):
    actual_lat = lat if lat is not None else 16.49
    actual_lon = lon if lon is not None else 80.50
    actual_district = district if (district and not district.startswith("Maharashtra")) else reverse_geocode(actual_lat, actual_lon)
    weather = fetch_open_meteo(actual_lat, actual_lon)

    risk_info = evaluate_crop_weather_risk(
        crop_key=crop.lower().strip(),
        temp=weather["temperature"],
        humidity=weather["humidity"],
        rain_prob=weather["rain_prob"],
        language=language
    )

    return {
        "status": "success",
        "district": actual_district,
        "crop": crop,
        "weather": weather,
        "risk_assessment": {
            "is_outbreak_risk": risk_info["is_outbreak_risk"],
            "risk_percentage": risk_info["risk_percentage"],
            "potential_disease": risk_info["potential_disease"],
            "preventive_advisory": risk_info["advisory"]
        }
    }

@router.post("/simulate")
def simulate_and_dispatch(data: SimulationInput, background_tasks: BackgroundTasks):
    risk_info = evaluate_crop_weather_risk(
        crop_key=data.crop.lower().strip(),
        temp=data.temperature,
        humidity=data.humidity,
        rain_prob=data.rain_prob,
        language=data.language
    )

    return {
        "status": "success",
        "simulated": True,
        "is_outbreak_risk": risk_info["is_outbreak_risk"],
        "risk_percentage": risk_info["risk_percentage"],
        "potential_disease": risk_info["potential_disease"],
        "advisory": risk_info["advisory"],
        "telegram_dispatched": False
    }