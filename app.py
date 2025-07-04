from flask import Flask, render_template, request
import pandas as pd
import json
import random
import os

app = Flask(__name__)

# BACA JSON dataset
with open("tmdb_dataset.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)
df = pd.DataFrame(data)

# PEMETAAN MOOD KE GENRE
mood_genre_map = {
    "senang": ["komedi", "Percintaan", "Keluarga", "Animasi"],
    "sedih": ["Drama", "Percintaan", "Musik"],
    "tegang": ["Kengerian", "Kejahatan", "Misteri", "Cerita Seru"],
    "semangat": ["Aksi", "Petualangan", "Fantasi"],
    "santai": ["Animasi", "Keluarga", "Dokumenter"]
}

@app.route("/")
def landing():
    return render_template("index.html")

@app.route("/mood")
def mood():
    return render_template("mood.html")

@app.route("/rekomendasi", methods=["POST"])
def rekomendasi():
    moods_raw = request.form.get("mood")
    selected_moods = [m.strip() for m in moods_raw.split(",") if m.strip()]
    genres = []
    for mood in selected_moods:
        genres.extend(mood_genre_map.get(mood.lower(), []))

    # Filter berdasarkan genre
    hasil = df[df["genres"].str.contains("|".join(genres), case=False, na=False)]

    # Prioritaskan yang punya platform streaming (Netflix diutamakan)
    hasil = hasil.sort_values(
        by="streaming_providers",
        key=lambda x: x.str.contains("Netflix", na=False).astype(int),
        ascending=False
    )

    rekomendasi = hasil.sample(n=min(10, len(hasil)), random_state=None)

    return render_template("rekomendasi.html", mood=", ".join(selected_moods), rekomendasi=rekomendasi.to_dict(orient="records"))

@app.route("/detail/<int:item_id>")
def detail(item_id):
    detail_data = next((item for item in data if item["id"] == item_id), None)
    if not detail_data:
        return "Tontonan tidak ditemukan", 404

    release_year = ""
    if detail_data.get("release_date"):
        release_year = detail_data["release_date"].split("-")[0]

    return render_template("detail.html", detail=detail_data, release_year=release_year)

@app.route("/castandcrew/<int:item_id>")
def cast_and_crew(item_id):
    detail_data = next((item for item in data if item["id"] == item_id), None)
    if not detail_data:
        return "Cast & crew tidak ditemukan", 404

    return render_template("castandcrew.html", detail=detail_data)

@app.route("/cari")
def cari():
    query = request.args.get("query", "")
    hasil = df[df["title"].str.contains(query, case=False, na=False)]
    return render_template("cari.html", query=query, hasil=hasil.to_dict(orient="records"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
