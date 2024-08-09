import pandas as pd
import re
import numpy as np
import emoji

ozel_karakterin_boşlukla_degismesi = True
kucuk_harfe_cevirme = True
newline_karakteri_boslukla_degistirme = True
fazla_boslukları_silme = True
emoji_silme = True
tl_silme = True
parantez_silme = True
renk_bilgisi_cikarma = True
model_bilgisi_cikarma = True
baglanti_tipi_cikarma = True

data_excel =  r" " #xlsx uzantılı data setinin path'ini buraya eklemek gerekmektedir 
output = 'sonuc.xlsx' # çıktının dosya adını burdan belirleyebilirsiniz

# Excel dosyasını oku
df = pd.read_excel(data_excel)

# Stop words listesini dosyadan okuma fonksiyonu
def stop_words_cikarma(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        stop_words = set(line.strip() for line in file)
    return stop_words
    
stop_words = stop_words_cikarma(r"C:\Users\beyza\Downloads\stopWords (5).txt")
    
# Stop words'leri kaldırma fonksiyonu
def stop_word_silme(text, stop_words):
    tokens = text.split()  # Cümleyi tokenlara ayır
    filtered_tokens = [word for word in tokens if word not in stop_words]  # Stop words'leri kaldır
    return ' '.join(filtered_tokens)  # Tokenları tekrar birleştir
    
# Özel karakterleri temizleme fonksiyonu
def temizle_metni(text, ozel_karakterin_boşlukla_degismesi, kucuk_harfe_cevirme, newline_karakteri_boslukla_degistirme, fazla_boslukları_silme, emoji_silme):
    if ozel_karakterin_boşlukla_degismesi:
        text = re.sub(r'[^\w\s]', ' ', text)
    if kucuk_harfe_cevirme:
        text = text.lower()
    if newline_karakteri_boslukla_degistirme:
        text = text.replace('\n', ' ')
    if fazla_boslukları_silme:
        text = re.sub(r'\s+', ' ', text).strip()
    if emoji_silme:
        text = emoji.replace_emoji(text, replace='')
    return text

# Fiyat sütunundaki TL'yi kaldırma fonksiyonu
def  fiyat_sutunu_tl_kaldirma(fiyat, remove_tl):
    if remove_tl:
        return re.sub(r'TL', '', str(fiyat)).strip()
    return str(fiyat).strip()

# Beğeni Sayısı sütunundaki parantezleri kaldırma fonksiyonu
def begeni_sayisi_parantez_kaldirma(begeni, parantez_silme):
    if parantez_silme:
        match = re.search(r'\((\d+)\)', str(begeni))
        return match.group(1) if match else np.nan
    return str(begeni).strip()

# Renk, model, bağlantı tipi gibi bilgileri çıkarmak için yardımcı fonksiyonlar
def renk(urun_adı, renkler, renk_bilgisi_cikarma):
    if renk_bilgisi_cikarma:
        for renk in renkler:
            if re.search(r'\b' + renk + r'\b', urun_adı, re.IGNORECASE):
                return renk.capitalize()
    return np.nan

def model(urun_adı, modeller, model_bilgisi_cikarma):
    if model_bilgisi_cikarma:
        for model in modeller:
            if re.search(r'\b' + model + r'\b', urun_adı, re.IGNORECASE):
                return model
    return np.nan

def baglanti_tipi(urun_adı, baglanti_tipi_cikarma):
    if baglanti_tipi_cikarma:
        if re.search(r'bluetooth|kablosuz|wireless', urun_adı, re.IGNORECASE):
            return "kablosuz"
        elif re.search(r'kablolu', urun_adı, re.IGNORECASE):
            return "kablolu"
    return np.nan


# Renkler ve modeller için listeler
renkler = [ "siyah", "beyaz", "mavi", "kırmızı", "yeşil", "gri", "altın", "gümüş", "pembe", "mor", "turuncu", "sarı", "lacivert", "kahverengi"]


modeller = ['airpods pro 2.nesil', 'airpods 3.nesil', 'airpods 3.nesil lightning', 'apple lightning konnektörlü', 'freebuds se', 'tune 510bt', 'tune 520bt', 'tune 560bt', 'tune 570bt', 'c100sı', 'tune 500', 'vibe 100 tws', 'wave 300 tws', 'tah4205', 'galaxy buds fe', 'eo-ia500b', 'galaxy buds 2', 'ehs61', 'redmi buds 4 active', 'redmi buds 4 lite', 'mi true wireless earphones 2 basic', 'piston basic edition', 'redmi buds 3 lite', 'redmi buds 3', 'redmi buds essential','tune t510bt']
# Remove "devamını oku" and the preceding text up to the previous space
df['Yorum'] = df['Yorum'].apply(lambda x: re.sub(r'\S*devamını oku', '', x, flags=re.IGNORECASE).strip())


# Metin temizleme ve yeni sütunlar ekleme
df['Yorum'] = df['Yorum'].apply(lambda x: temizle_metni(x, ozel_karakterin_boşlukla_degismesi, kucuk_harfe_cevirme, newline_karakteri_boslukla_degistirme, fazla_boslukları_silme, emoji_silme))

# Stop words'leri kaldırma
df['Yorum'] = df['Yorum'].apply(lambda x: stop_word_silme(x, stop_words))


df['Ürün İsmi'] = df['Ürün İsmi'].apply(lambda x: temizle_metni(x, ozel_karakterin_boşlukla_degismesi, kucuk_harfe_cevirme, newline_karakteri_boslukla_degistirme, fazla_boslukları_silme, emoji_silme))
df['Ürün Marka'] = df['Ürün Marka'].apply(lambda x: temizle_metni(x, ozel_karakterin_boşlukla_degismesi, kucuk_harfe_cevirme, newline_karakteri_boslukla_degistirme, fazla_boslukları_silme, emoji_silme))
df['Satıcı Adı'] = df['Satıcı Adı'].apply(lambda x: temizle_metni(x, ozel_karakterin_boşlukla_degismesi, kucuk_harfe_cevirme, newline_karakteri_boslukla_degistirme, fazla_boslukları_silme, emoji_silme))
df['Yorum Satıcı Adı'] = df['Yorum Satıcı Adı'].apply(lambda x: temizle_metni(x, ozel_karakterin_boşlukla_degismesi, kucuk_harfe_cevirme, newline_karakteri_boslukla_degistirme, fazla_boslukları_silme, emoji_silme))

df['Fiyat'] = df['Fiyat'].apply(lambda x: fiyat_sutunu_tl_kaldirma(x, tl_silme))
df['Beğeni Sayısı'] = df['Beğeni Sayısı'].apply(lambda x: begeni_sayisi_parantez_kaldirma(x, parantez_silme))

df['Renk'] = df['Ürün İsmi'].apply(lambda x: renk(x, renkler, renk_bilgisi_cikarma))
df['Model'] = df['Ürün İsmi'].apply(lambda x: model(x, modeller, model_bilgisi_cikarma))
df['Bağlantı Tipi'] = df['Ürün İsmi'].apply(lambda x: baglanti_tipi(x, baglanti_tipi_cikarma))


# stringe çevirme işlemi
df['Renk'] = df['Renk'].astype(str)
df['Model'] = df['Model'].astype(str)
df['Bağlantı Tipi'] = df['Bağlantı Tipi'].astype(str)

# Küçük harfe çevirme işlemi
df['Renk'] = df['Renk'].str.lower()
df['Model'] = df['Model'].str.lower()
df['Bağlantı Tipi'] = df['Bağlantı Tipi'].str.lower()

# Tamamen aynı olan satırlardan sadece bir tanesini bırak
df = df.drop_duplicates()

df.to_excel(output, index=False)
