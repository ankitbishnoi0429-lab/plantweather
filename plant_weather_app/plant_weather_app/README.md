Plant + Weather + Simple Plant Disease Detector
===============================================

What's included
- Flask app (app.py)
- Simple heuristic plant-analysis (color-spot detection). If you have a trained Keras model, place `plant_disease_model.h5` in the project root and the app will try to use it.
- Uses OpenWeatherMap API for temperature and coordinates. The API key is set in `app.py`.

How to run
1. Create a virtualenv and activate it.
2. pip install -r requirements.txt
3. Optional: pip install tensorflow if you will use a Keras model.
4. python app.py
5. Open http://127.0.0.1:5000 in your browser.

Notes
- I set the provided API key in app.py. If it does not match your weather provider, replace `API_KEY` in app.py with your correct key.
- The plant-disease detection here is a simple heuristic — to improve accuracy you should add a trained model (e.g. TensorFlow/Keras) and update labels.
