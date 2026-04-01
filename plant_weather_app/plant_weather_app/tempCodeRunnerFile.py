from flask import Flask, render_template, request
import requests, os, io
from PIL import Image
import numpy as np

# 🌤️ OpenWeatherMap API Key
API_KEY = "655387fefd10cf813b1f79540ecef6af"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 🌍 Translations + Desi Ilaaj
translations = {
    "en": {
        "temp_label": "Temperature",
        "condition": "Condition",
        "infected_area": "Infected Area",
        "summary": "Summary",
        "treatment": "Treatment",
        "desi_treatment": "Traditional Remedy",
        "plant_health": "Plant Health Analysis",
        "weather_details": "Weather Details",
        "healthy": (
            "Healthy",
            "No visible disease detected.",
            "Maintain regular watering and sunlight.",
            "No desi treatment needed, just give proper sunlight and water regularly."
        ),
        "minor": (
            "Minor Spots",
            "Early signs of stress or mild infection.",
            "Spray mild fungicide and prune affected leaves.",
            "Mix neem oil with water and spray on leaves twice a week."
        ),
        "leafspot": (
            "Leaf Spot Disease",
            "Possible fungal or bacterial leaf spot.",
            "Use neem oil or copper-based fungicide.",
            "Grind neem leaves and garlic together, mix in water and spray on leaves."
        ),
        "severe": (
            "Severe Infection",
            "Heavy infection likely (blight or rot).",
            "Remove infected leaves & apply antifungal spray.",
            "Boil ash + neem leaves in water, cool it, and spray on affected areas daily for 3 days."
        ),
        "crop_name": "Crop / Plant Image"
    },
    "hi": {
        "temp_label": "तापमान",
        "condition": "मौसम की स्थिति",
        "infected_area": "संक्रमित क्षेत्र",
        "summary": "सारांश",
        "treatment": "उपचार",
        "desi_treatment": "देसी इलाज",
        "plant_health": "फसल स्वास्थ्य विश्लेषण",
        "weather_details": "मौसम का विवरण",
        "healthy": (
            "स्वस्थ",
            "कोई रोग नहीं मिला।",
            "नियमित सिंचाई और धूप बनाए रखें।",
            "कोई देसी इलाज की जरूरत नहीं, बस सही धूप और पानी दें।"
        ),
        "minor": (
            "हल्के धब्बे",
            "तनाव या हल्के संक्रमण के प्रारंभिक संकेत।",
            "हल्का फफूंदनाशी छिड़कें और प्रभावित पत्तियाँ काटें।",
            "नीम तेल और पानी मिलाकर हफ्ते में दो बार छिड़काव करें।"
        ),
        "leafspot": (
            "पत्ती धब्बा रोग",
            "संभावित फफूंद या बैक्टीरियल संक्रमण।",
            "नीम तेल या कॉपर आधारित फफूंदनाशी का प्रयोग करें।",
            "नीम की पत्तियाँ और लहसुन पीसकर पानी में मिलाएँ और छिड़काव करें।"
        ),
        "severe": (
            "गंभीर संक्रमण",
            "भारी संक्रमण (झुलसा या सड़न)।",
            "संक्रमित पत्तियाँ हटाएँ और एंटीफंगल स्प्रे करें।",
            "राख और नीम की पत्तियाँ उबालकर ठंडा करें और रोज़ प्रभावित जगह पर छिड़कें।"
        ),
        "crop_name": "फसल / पौधे की छवि"
    },
    "pa": {
        "temp_label": "ਤਾਪਮਾਨ",
        "condition": "ਮੌਸਮ ਦੀ ਸਥਿਤੀ",
        "infected_area": "ਸੰਕਰਮਿਤ ਖੇਤਰ",
        "summary": "ਸੰਖੇਪ",
        "treatment": "ਇਲਾਜ",
        "desi_treatment": "ਦੇਸੀ ਇਲਾਜ",
        "plant_health": "ਫਸਲ ਸਿਹਤ ਵਿਸ਼ਲੇਸ਼ਣ",
        "weather_details": "ਮੌਸਮ ਵੇਰਵਾ",
        "healthy": (
            "ਸਿਹਤਮੰਦ",
            "ਕੋਈ ਬਿਮਾਰੀ ਨਹੀਂ ਮਿਲੀ।",
            "ਨਿਯਮਿਤ ਪਾਣੀ ਅਤੇ ਧੂਪ ਰੱਖੋ।",
            "ਕੋਈ ਦੇਸੀ ਇਲਾਜ ਦੀ ਲੋੜ ਨਹੀਂ, ਸਿਰਫ਼ ਪਾਣੀ ਤੇ ਧੂਪ ਦਿਓ।"
        ),
        "minor": (
            "ਹਲਕੇ ਧੱਬੇ",
            "ਤਣਾਅ ਜਾਂ ਹਲਕੀ ਸੰਕਰਮਣ ਦੀ ਸ਼ੁਰੂਆਤ।",
            "ਹਲਕਾ ਫੰਗੀਸਾਈਡ ਛਿੜਕੋ ਅਤੇ ਪ੍ਰਭਾਵਿਤ ਪੱਤੇ ਕੱਟੋ।",
            "ਨੀਮ ਦਾ ਤੇਲ ਪਾਣੀ ਵਿੱਚ ਮਿਲਾ ਕੇ ਹਫ਼ਤੇ ਵਿੱਚ ਦੋ ਵਾਰੀ ਛਿੜਕੋ।"
        ),
        "leafspot": (
            "ਪੱਤਾ ਦਾਗ ਬਿਮਾਰੀ",
            "ਸੰਭਾਵਿਤ ਫੰਗਲ ਜਾਂ ਬੈਕਟੀਰੀਆ ਸੰਕਰਮਣ।",
            "ਨੀਮ ਤੇਲ ਜਾਂ ਤਾਂਬੇ-ਅਧਾਰਤ ਫੰਗੀਸਾਈਡ ਵਰਤੋ।",
            "ਨੀਮ ਦੇ ਪੱਤੇ ਤੇ ਲਸਣ ਪੀਸ ਕੇ ਪਾਣੀ ਨਾਲ ਮਿਲਾ ਕੇ ਛਿੜਕੋ।"
        ),
        "severe": (
            "ਗੰਭੀਰ ਸੰਕਰਮਣ",
            "ਭਾਰੀ ਸੰਕਰਮਣ (ਝੁਲਸਾ ਜਾਂ ਸੜਨ)।",
            "ਸੰਕਰਮਿਤ ਪੱਤੇ ਹਟਾਓ ਅਤੇ ਐਂਟੀਫੰਗਲ ਸਪਰੇ ਕਰੋ।",
            "ਰਾਖ ਤੇ ਨੀਮ ਦੇ ਪੱਤੇ ਉਬਾਲ ਕੇ ਠੰਢੇ ਕਰਕੇ ਹਰ ਰੋਜ਼ ਛਿੜਕੋ।"
        ),
        "crop_name": "ਫਸਲ / ਪੌਦੇ ਦੀ ਤਸਵੀਰ"
    }
}


# 🌦️ Weather (city or pincode)
def get_weather(location):
    try:
        if location.isdigit():
            url = f"https://api.openweathermap.org/data/2.5/weather?zip={location},IN&appid={API_KEY}&units=metric"
        else:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}&units=metric"

        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()

        return {
            "city": data.get("name", location),
            "temp": data["main"]["temp"],
            "desc": data["weather"][0]["description"].title(),
            "lat": data["coord"]["lat"],
            "lon": data["coord"]["lon"]
        }
    except Exception as e:
        return {"error": f"Weather data not found: {e}"}


# 🌿 Image Analyzer with Desi Ilaaj
def analyze_image(img_bytes, lang):
    im = Image.open(io.BytesIO(img_bytes)).convert("RGB").resize((300, 300))
    arr = np.array(im)
    R, G, B = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    brown_mask = ((R > 100) & (G > 60) & (B < 100))
    yellow_mask = ((R > 160) & (G > 140) & (B < 100))
    infected = np.logical_or(brown_mask, yellow_mask)
    percent = infected.sum() / infected.size * 100

    t = translations.get(lang, translations["en"])

    if percent < 1.5:
        result = t["healthy"]
    elif percent < 5:
        result = t["minor"]
    elif percent < 20:
        result = t["leafspot"]
    else:
        result = t["severe"]

    return {
        "status": result[0],
        "summary": result[1],
        "treatment": result[2],
        "desi": result[3],
        "percent": round(percent, 2)
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    location = request.form.get('city')
    lang = request.form.get('language', 'en')
    file = request.files.get('plant_image')

    weather = get_weather(location)
    image_path, analysis, map_url = None, None, None

    if file and file.filename:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        with open(filepath, "rb") as f:
            img_bytes = f.read()
        analysis = analyze_image(img_bytes, lang)
        image_path = "/" + filepath.replace("\\", "/")

    if not weather.get("error"):
        map_url = f"https://www.google.com/maps?q={weather['lat']},{weather['lon']}&z=10"

    labels = translations.get(lang, translations["en"])

    return render_template(
        'result.html',
        weather=weather,
        analysis=analysis,
        image_path=image_path,
        map_url=map_url,
        lang=lang,
        labels=labels
    )


if __name__ == "__main__":
    app.run(debug=True)
