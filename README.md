<<<<<<< HEAD
# Crop Yield Prediction

A small project that predicts crop yield and shows **5 simple results**.

1. Predicted yield (tonnes per hectare)
2. Estimated production (total tonnes)
3. Historical average yield
4. Weather snapshot
5. Yield outlook (above / near / below average)

## Project layout

```text
.
├── data/sample_crop_yield.csv   # training data
├── frontend/                    # HTML + CSS + JS page
├── scripts/train.py             # train the model
├── scripts/run_app.py           # start the web app
└── src/crop_yield_prediction/   # Python code
```

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Optional: copy `.env.example` to `.env` and add an OpenWeather API key if you want live weather.

## Train

```bash
python scripts/train.py
```

## Run the website

```bash
python scripts/run_app.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The page shows prediction results and an analysis section with charts: yield by crop, yield by state, yield by year, and rainfall by season.

If the model is not trained yet, the first prediction will train it automatically.
=======
# Crop-Analysis-
>>>>>>> 4f0f3f8250663b024a0427e70c286d8354e1a6f6
