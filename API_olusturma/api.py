from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from transformers import pipeline
from typing import List, Dict
import uvicorn

# FastAPI uygulamasını başlatalım
app = FastAPI()

# Entity recognition modelini yükleyelim
def load_entity_recognition_model(model_path):
    nlp = pipeline("ner", model=model_path, tokenizer=model_path)
    return nlp

# API Başlatılmadan önce model yüklensin
entity_model_path = r"C:\Users\beyza\Downloads\ner\ner"
nlp_model = load_entity_recognition_model(entity_model_path)

# Kullanıcıdan alınacak input için bir model tanımı
class UserInput(BaseModel):
    text: str

# API'nin giriş noktasını oluşturalım
@app.post("/process/")
async def process_text(input: UserInput):
    try:
        user_input = input.text
        # İşlenecek XLSX dosyalarının listesi
        file_list = [
            r"C:\Users\beyza\Downloads\redmiBudsEssential_duzenlenmis.xlsx",
            r"C:\Users\beyza\Downloads\jblTune510bt_duzenlenmis.xlsx",
            r"C:\Users\beyza\Downloads\pistonBasicEdition_duzenlenmis.xlsx",
            r"C:\Users\beyza\Downloads\jblTune500_duzenlenmis.xlsx"
        ]
        
        scores = process_xlsx_files(file_list, user_input)

        if not scores:
            raise HTTPException(status_code=404, detail="No categories identified.")

        # Skorları toplamalarına göre sırala
        sorted_scores = sorted(scores.items(), key=lambda x: sum(x[1].get('scores', {}).values()), reverse=True)

        return sorted_scores

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Entity'leri tanımlayalım ve kategorileri çıkartalım
def identify_categories(text, nlp_model):
    entities = nlp_model(text)
    categories = set()
    for entity in entities:
        category = entity['entity'].split('-')[-1].lower()  # Kategori ismi
        categories.add(category)
    return list(categories)

# Kategorilere göre puan hesaplaması yapalım
def calculate_scores(user_categories, model_data):
    category_total_counts = {category: 0 for category in user_categories}
    positive_category_counts = {category: 0 for category in user_categories}

    # Kategori sayımlarını yapalım
    for index, row in model_data.iterrows():
        model_categories = row['Categories'].lower().split(', ')  # Case insensitive karşılaştırma
        model_sentiments = row['Sentiments'].lower().split(', ')
        like_count = row.get('Beğeni Sayısı', 0)  # Beğeni Sayısını al, eğer NaN ise 0 olarak kabul et

        for category, sentiment in zip(model_categories, model_sentiments):
            if category in user_categories:
                category_total_counts[category] += 1 + like_count  # 1 (Yorum yapan) + Beğeni Sayısı
                if sentiment == 'positive':  # Pozitif sentiment ise sayıyı artır
                    positive_category_counts[category] += 1 + like_count  # 1 (Yorum yapan) + Beğeni Sayısı

    # Puanları hesaplayalım
    category_scores = {}
    for category in user_categories:
        total = category_total_counts[category]
        if total > 0:
            score = (positive_category_counts[category] / total) * 100
            category_scores[category] = score

    return category_scores

# Yıldız puanı hesaplaması yapalım
def calculate_star_rating(model_data):
    total_sentiments = len(model_data)
    positive_sentiments = len(model_data[model_data['Sentiments'].str.lower() == 'positive'])

    if total_sentiments > 0:
        star_rating = (positive_sentiments / total_sentiments) * 5
        return round(star_rating, 2)
    return 0

# XLSX dosyalarını işleme fonksiyonu
def process_xlsx_files(file_list, user_input):
    all_scores = {}
    for file_path in file_list:
        # XLSX dosyasını yükleyelim
        df = pd.read_excel(file_path)

        # NaN değerlerini içeren satırları silelim
        df.dropna(subset=["Yorum"], inplace=True)

        # Kullanıcı girdisinden kategorileri tanımlayalım
        user_categories = identify_categories(user_input, nlp_model)
        if not user_categories:
            continue

        # Puanlamayı yapalım
        category_scores = calculate_scores(user_categories, df)
        
        # Yıldız puanını hesaplayalım
        star_rating = calculate_star_rating(df)

        # Model adını ve diğer bilgileri "Model", "Ürün Marka", "Bağlantı Tipi", "Renk", "Fiyat", "Ürünün Ortalama Puanı" sütunlarından alalım
        model_name = df['Model'].iloc[0]
        brand_name = df['Ürün Marka'].iloc[0]
        connection_type = df['Bağlantı Tipi'].iloc[0]
        color = df['Renk'].iloc[0]
        price = df['Fiyat'].iloc[0]
        average_rating = df['Ürünün Ortalama Puanı'].iloc[0]

        all_scores[f"model: {model_name}"] = {
            "ürün marka": f"{brand_name}",
            "bağlantı tipi": f"{connection_type}",
            "renk": f"{color}",
            "fiyat": f"{price}",
            "ürün puanı": f"{average_rating}",
            "hesaplanan yıldız puanı": f"{star_rating}",
            "scores": category_scores
        }

    return all_scores

if _name_ == "_main_":
    uvicorn.run(app, host="0.0.0.0", port=8000)
