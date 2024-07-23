
import pandas as pd
import re
import numpy as np
import emoji
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import matplotlib.pyplot as plt
import jpype
from jpype import JClass, getDefaultJVMPath, startJVM

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
generate_word_frequency = False

custom_stop_words_file = "stopWords.txt"
data_excel = 'products.xlsx'
temizlenmis_excel = 'sonuc.xlsx'
labellamak_icin = 'labellamak_icin.csv'

# Özel karakterleri temizleme fonksiyonu
def metni_tenizle(text, ozel_karakterin_boşlukla_degismesi, kucuk_harfe_cevirme, newline_karakteri_boslukla_degistirme, fazla_boslukları_silme, emoji_silme):
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
def fiyat_sutunu_tl_kaldirma(fiyat, tl_silme):
    if tl_silme:
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
        if re.search(r'bluetooth|kablosuz', urun_adı, re.IGNORECASE):
            return "kablosuz"
        elif re.search(r'kablolu', urun_adı, re.IGNORECASE):
            return "kablolu"
    return np.nan


# Zemberek ile kök bulma fonksiyonu(Lemmatization)
def kok_bulma(tokens):
    kelimelerin_kokleri = []
    ZEMBEREK_PATH = r"zemberek-full_old.jar"
    if not jpype.isJVMStarted():
        startJVM(getDefaultJVMPath(), '-ea', '-Djava.class.path=%s' % (ZEMBEREK_PATH))
    TurkishMorphology = JClass('zemberek.morphology.TurkishMorphology')
    morphology = TurkishMorphology.createWithDefaults()
    for token in tokens:
        analysis = morphology.analyzeAndDisambiguate(str(token)).bestAnalysis()
        kelimenin_koku = str(analysis[0].getLemmas()[0])
        if kelimenin_koku == "UNK":
            kelimenin_koku = token
        kelimelerin_kokleri.append(kelimenin_koku)
    return kelimelerin_kokleri

# POS etiketleme fonksiyonu(sözcük türü)
def pos_zemberek(tokens):
    pos_etiketleri = []
    ZEMBEREK_PATH = r"zemberek-full_old.jar"
    if not jpype.isJVMStarted():
        startJVM(getDefaultJVMPath(), '-ea', '-Djava.class.path=%s' % (ZEMBEREK_PATH))
    TurkishMorphology = JClass('zemberek.morphology.TurkishMorphology')
    morphology = TurkishMorphology.createWithDefaults()
    for token in tokens:
        analysis = morphology.analyzeAndDisambiguate(token).bestAnalysis()
        if analysis:
            best = analysis[0]
            pos_etiketleri.append((token, best.getPos().shortForm))
        else:
            pos_etiketleri.append((token, 'UNK'))
    return pos_etiketleri

# Kelime frekanslarını hesaplayan ve görselleştiren fonksiyon
def kelime_frekansi_ve_gorsellestirme(df):
    all_tokens = [token for sublist in df['Stop Words Çıkarılmış Hali'] for token in sublist]
    word_freq = Counter(all_tokens)
    common_words = word_freq.most_common(20)
    
    print("En sık geçen kelimeler ve frekansları:")
    for word, freq in common_words:
        print(f"{word}: {freq}")

    words, counts = zip(*common_words)
    plt.figure(figsize=(12, 8))
    plt.bar(words, counts)
    plt.xlabel('Kelimeler')
    plt.ylabel('Frekans')
    plt.title('En Sık Geçen Kelimeler')
    plt.xticks(rotation=45)
    plt.show()

# Excel dosyasını oku
df = pd.read_excel(data_excel)

# Renkler ve modeller için listeler
renkler = [] #datasetindeki ürünlerin renklerinin listesi buraya eklenmelidir
modeller = [] #datasetindeki modellerin listesi buraya eklenmelidir

# Metin temizleme ve yeni sütunlar ekleme
df['Yorum'] = df['Yorum'].apply(lambda x: metni_tenizle(x, ozel_karakterin_boşlukla_degismesi, kucuk_harfe_cevirme, newline_karakteri_boslukla_degistirme, fazla_boslukları_silme, emoji_silme))
df['Ürün İsmi'] = df['Ürün İsmi'].apply(lambda x: metni_tenizle(x, ozel_karakterin_boşlukla_degismesi, kucuk_harfe_cevirme, newline_karakteri_boslukla_degistirme, fazla_boslukları_silme, emoji_silme))
df['Ürün Marka'] = df['Ürün Marka'].apply(lambda x: metni_tenizle(x, ozel_karakterin_boşlukla_degismesi, kucuk_harfe_cevirme, newline_karakteri_boslukla_degistirme, fazla_boslukları_silme, emoji_silme))
df['Satıcı Adı'] = df['Satıcı Adı'].apply(lambda x: metni_tenizle(x, ozel_karakterin_boşlukla_degismesi, kucuk_harfe_cevirme, newline_karakteri_boslukla_degistirme, fazla_boslukları_silme, emoji_silme))
df['Yorum Satıcı Adı'] = df['Yorum Satıcı Adı'].apply(lambda x: metni_tenizle(x, ozel_karakterin_boşlukla_degismesi, kucuk_harfe_cevirme, newline_karakteri_boslukla_degistirme, fazla_boslukları_silme, emoji_silme))

df['Fiyat'] = df['Fiyat'].apply(lambda x: fiyat_sutunu_tl_kaldirma(x, tl_silme))
df['Beğeni Sayısı'] = df['Beğeni Sayısı'].apply(lambda x: begeni_sayisi_parantez_kaldirma(x, parantez_silme))

df['Renk'] = df['Ürün İsmi'].apply(lambda x: renk(x, renkler, renk_bilgisi_cikarma))
df['Model'] = df['Ürün İsmi'].apply(lambda x: model(x, modeller, model_bilgisi_cikarma))
df['Bağlantı Tipi'] = df['Ürün İsmi'].apply(lambda x: baglanti_tipi(x, baglanti_tipi_cikarma))

# Küçük harfe çevirme işlemi
df['Renk'] = df['Renk'].str.lower()
df['Model'] = df['Model'].str.lower()
df['Bağlantı Tipi'] = df['Bağlantı Tipi'].str.lower()


# Tamamen aynı olan satırlardan sadece bir tanesini bırak
df = df.drop_duplicates()

# Stop words verilerini indirme
nltk.download('stopwords')
nltk_stop_words = set(stopwords.words('turkish'))

# Kendi stop words dosyasını okuma
with open(custom_stop_words_file, 'r', encoding='utf-8') as f:
    custom_stop_words = set(f.read().splitlines())

# NLTK stop words ve kendi stop words'leri birleştirme
combined_stop_words = nltk_stop_words.union(custom_stop_words)

def tokenize_comment(comment):
    tokens = word_tokenize(comment)
    return tokens

def stop_word_silme(tokens):
    filtered_tokens = [word for word in tokens if word not in combined_stop_words]
    return filtered_tokens

# Yorumları tokenlarına ayır ve yeni bir sütuna ekle
df['Yorum Tokenleri'] = df['Yorum'].apply(tokenize_comment)

# Tokenların köklerini bul ve yeni bir sütuna ekle
df['Köklerine Ayrılmış Yorumlar'] = df['Yorum Tokenleri'].apply(kok_bulma)

# Stop words'leri çıkar ve yeni bir sütuna ekle
df['Stop Words Çıkarılmış Hali'] = df['Köklerine Ayrılmış Yorumlar'].apply(stop_word_silme)

# Zemberek ile POS etiketleme ve yeni sütun ekleme
df['POS Etiketleri'] = df['Stop Words Çıkarılmış Hali'].apply(pos_zemberek)

# Temizlenmiş ve tokenize edilmiş veri setini yeni bir Excel dosyasına kaydedin
df.to_excel(temizlenmis_excel)

# Kelime frekansı ve görselleştirme fonksiyonunu isteğe bağlı olarak çalıştır
if generate_word_frequency:
    kelime_frekansi_ve_gorsellestirme(df)

# cümle halinde yazma fonksiyonu
def tokens_to_sentence(tokens):
    return ' '.join(tokens)

# Yeni sütun: Token_Lemma_StopWords (cümle halinde)
df['Token_Lemma_StopWords'] = df['Stop Words Çıkarılmış Hali'].apply(tokens_to_sentence)

# labellamak_icin.csv dosyasını oluşturma
labellamak_icin_df = df[['Yorum', 'Token_Lemma_StopWords']]
labellamak_icin_df.to_csv(labellamak_icin, index=False)
