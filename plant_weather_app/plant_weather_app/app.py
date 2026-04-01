from flask import Flask, render_template, request, url_for
import requests, os, io
from PIL import Image
import numpy as np

# 🌤️ OpenWeatherMap API Key
API_KEY = "655387fefd10cf813b1f79540ecef6af"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# 🌾 Crop Info + Similar Crops + Desi Ilaaj
crop_info = {
    "Wheat": {"similar": ["Barley", "Oats", "Rye"], "desi": "Neem oil + ash mix spray for early leaf spots."},
    "Rice": {"similar": ["Paddy", "Sugarcane", "Maize"], "desi": "Use cow urine + turmeric water spray weekly."},
    "Cotton": {"similar": ["Soybean", "Sunflower", "Maize"], "desi": "Neem + garlic water spray helps prevent infection."},
    "Mustard": {"similar": ["Cabbage", "Cauliflower", "Broccoli"], "desi": "Apply ash and neem oil for fungal protection."},
    "Unknown": {"similar": ["Wheat", "Rice", "Cotton"], "desi": "Neem oil + cow urine spray works for all crops."}
}


# 🌍 Language Translation
translations = {
    "en": {
        "temp_label": "Temperature",
        "condition": "Condition",
        "infected_area": "Infected Area",
        "summary": "Summary",
        "treatment": "Treatment",
        "desi_treatment": "Traditional Remedy",
        "similar_crops": "Similar Crops",
        "similar_desi": "Desi Ilaaj for Similar Crops",
        "crop_name": "Detected Crop",
        "healthy": ("Healthy", "No visible disease detected.", "Maintain sunlight & watering.", "No desi treatment needed."),
        "minor": ("Minor Spots", "Early signs of stress.", "Use neem oil spray twice a week.", "Neem oil and garlic water mix."),
        "leafspot": ("Leaf Spot", "Possible fungal infection.", "Use copper fungicide.", "Neem + ash spray daily."),
        "severe": ("Severe Infection", "Heavy infection detected.", "Remove infected leaves.", "Use neem + turmeric mix water spray.")
    },
    "hi": {
        "temp_label": "तापमान",
        "condition": "मौसम की स्थिति",
        "infected_area": "संक्रमित क्षेत्र",
        "summary": "सारांश",
        "treatment": "इलाज",
        "desi_treatment": "देसी इलाज",
        "similar_crops": "समान फसलें",
        "similar_desi": "समान फसलों का देसी इलाज",
        "crop_name": "पहचानी गई फसल",
        "healthy": ("स्वस्थ", "कोई रोग नहीं मिला।", "धूप और पानी बनाए रखें।", "कोई इलाज की जरूरत नहीं।"),
        "minor": ("हल्के धब्बे", "थोड़ा संक्रमण।", "नीम तेल छिड़कें।", "नीम तेल + लहसुन पानी मिलाकर हफ्ते में दो बार छिड़कें।"),
        "leafspot": ("पत्ती धब्बा रोग", "फफूंद संक्रमण संभव।", "कॉपर फफूंदनाशी लगाएं।", "नीम + राख पानी छिड़कें।"),
        "severe": ("गंभीर संक्रमण", "भारी संक्रमण मिला।", "संक्रमित पत्तियाँ हटाएँ।", "नीम + हल्दी पानी रोज़ छिड़कें।")
    },
    "pa": {
        "temp_label": "ਤਾਪਮਾਨ",
        "condition": "ਮੌਸਮ",
        "infected_area": "ਸੰਕਰਮਿਤ ਖੇਤਰ",
        "summary": "ਸੰਖੇਪ",
        "treatment": "ਇਲਾਜ",
        "desi_treatment": "ਦੇਸੀ ਇਲਾਜ",
        "similar_crops": "ਇਕੋ ਜਿਹੀਆਂ ਫਸਲਾਂ",
        "similar_desi": "ਇਕੋ ਜਿਹੀਆਂ ਫਸਲਾਂ ਲਈ ਦੇਸੀ ਇਲਾਜ",
        "crop_name": "ਪਛਾਣੀ ਫਸਲ",
        "healthy": ("ਸਿਹਤਮੰਦ", "ਕੋਈ ਬਿਮਾਰੀ ਨਹੀਂ।", "ਧੂਪ ਅਤੇ ਪਾਣੀ ਦਿਓ।", "ਕੋਈ ਇਲਾਜ ਦੀ ਲੋੜ ਨਹੀਂ।"),
        "minor": ("ਹਲਕੇ ਧੱਬੇ", "ਹਲਕੀ ਬਿਮਾਰੀ।", "ਨੀਮ ਤੇਲ ਛਿੜਕੋ।", "ਨੀਮ ਤੇਲ ਪਾਣੀ ਨਾਲ ਮਿਲਾ ਕੇ ਛਿੜਕੋ।"),
        "leafspot": ("ਪੱਤਾ ਦਾਗ", "ਫੰਗਸ ਦਾ ਸੰਕਰਮਣ।", "ਕਾਪਰ ਛਿੜਕੋ।", "ਨੀਮ ਤੇ ਲਸਣ ਪਾਣੀ ਨਾਲ ਮਿਲਾ ਕੇ ਛਿੜਕੋ।"),
        "severe": ("ਗੰਭੀਰ ਬਿਮਾਰੀ", "ਭਾਰੀ ਬਿਮਾਰੀ।", "ਪੱਤੇ ਹਟਾਓ।", "ਨੀਮ ਤੇ ਹਲਦੀ ਪਾਣੀ ਛਿੜਕੋ।")
    }
}


# 🌦️ Weather Fetch
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
        return {"error": f"Weather not found: {e}"}


# 🌿 Image Analyzer
def analyze_image(img_bytes, lang):
    im = Image.open(io.BytesIO(img_bytes)).convert("RGB").resize((300, 300))
    arr = np.array(im)

    R, G, B = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    brown_mask = ((R > 100) & (G > 60) & (B < 100))
    yellow_mask = ((R > 160) & (G > 140) & (B < 100))
    infected = np.logical_or(brown_mask, yellow_mask)
    percent = infected.sum() / infected.size * 100

    t = translations.get(lang, translations["en"])

    # 🧠 Smart Crop Guess (based on color tone)
    avg_color = np.mean(arr.reshape(-1, 3), axis=0)
    Rm, Gm, Bm = avg_color
    if Gm > Rm and Gm > Bm:
        crop = "Wheat"
    elif Bm > Gm and Bm > Rm:
        crop = "Rice"
    elif Rm > Gm and Rm > Bm:
        crop = "Cotton"
    elif (Rm + Gm) / 2 > Bm:
        crop = "Mustard"
    else:
        crop = "Unknown"

    # 🔍 Select Disease Level
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
        "percent": round(percent, 2),
        "crop_name": crop,
        "similar": crop_info[crop]["similar"],
        "similar_desi": crop_info[crop]["desi"]
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
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # ✅ Fixed path for HTML rendering (Image will always show)
        image_path = url_for('static', filename=f'uploads/{filename}')
        with open(filepath, "rb") as f:
            img_bytes = f.read()

        analysis = analyze_image(img_bytes, lang)

    if not weather.get("error"):
        map_url = f"https://www.google.com/maps?q={weather['lat']},{weather['lon']}&z=10"

    labels = translations.get(lang, translations["en"])

    return render_template(
        'result.html',
        weather=weather,
        analysis=analysis,
        image_path=image_path,
        map_url=map_url,
        labels=labels,
        lang=lang
    )


if __name__ == "__main__":
    app.run(debug=True)
