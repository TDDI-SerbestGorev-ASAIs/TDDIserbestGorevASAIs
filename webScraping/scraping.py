from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import pandas as pd

# Selenium WebDriver ile Chrome'u başlat
driver = webdriver.Chrome()

# Trendyol ürün yorum sayfasına git 
url = '' #URL girin
driver.get(url)

# Sayfanın tamamen yüklenmesi için bekle
time.sleep(5)

# Ürün bilgilerini al
html_content = driver.page_source
html_sayfa = BeautifulSoup(html_content, "html.parser")

marka = html_sayfa.find("span", class_="product-brand")
urun_marka = marka.getText() if marka else "Ürün markası bulunamadı."

isim = html_sayfa.find("span", class_="product-name")
urun_ismi = isim.getText() if isim else "Ürün ismi bulunamadı."

fiyat = html_sayfa.find("span", class_="prc-dsc")
urun_fiyati = fiyat.getText() if fiyat else "Fiyat bulunamadı."

degerlendirmeYorumSayisi = html_sayfa.find("div", class_="ps-ratings__counts")
bol = degerlendirmeYorumSayisi.getText() if degerlendirmeYorumSayisi else "Degerlendirme sayisi bulunamadı."
degerlendirmeSayi, yorumSayi = bol.split("•")

# Sayıları ayrıştır ve uygun değişkenlerde sakla
degerlendirme_sayisi = int(degerlendirmeSayi.split()[0])
yorum_sayisi = int(yorumSayi.split()[0])


urunPuan = html_sayfa.find("div", class_="ps-ratings__count-text")
urun_puani = urunPuan.getText() if urunPuan else "Ürünün puanı bulunamadı."

SatıcıAdı = html_sayfa.find("span", class_="merchant-name")
satici_adi = SatıcıAdı.getText() if SatıcıAdı else "Ürün satıcı adı bulunamadı."

SatıcıPuanı = html_sayfa.find("div", class_="sl-pn")
satici_puani = SatıcıPuanı.getText() if SatıcıPuanı else "Ürün satıcı puanı bulunamadı."

# Yorumları almak için bir liste oluştur
all_comments = []
collected_comments = set()

last_height = driver.execute_script("return document.body.scrollHeight")

# 1.5 dakikalık zamanlayıcıyı başlatmak için zaman değişkeni
no_scroll_start_time = None

while True:
    # Sayfanın HTML içeriğini al
    html_content = driver.page_source
    html_sayfa = BeautifulSoup(html_content, "html.parser")

    # Yorumları al
    yorumlar = html_sayfa.find_all("div", class_="comment-text")
    satici_bilgileri = html_sayfa.find_all("span", class_="seller-name-info")  # Satıcı bilgilerini çek
    begeni_sayilari = html_sayfa.find_all("div", class_="rnr-com-like")  # Beğeni sayılarını çek

    if yorumlar and satici_bilgileri and begeni_sayilari:
        # Yorumları listeye ekle ve ekrana yazdır
        for yorum, satici, begeni in zip(yorumlar, satici_bilgileri, begeni_sayilari):
            yorum_text = yorum.getText()
            saticiAdiYorum = satici.getText() if satici else "Satıcı bilgisi bulunamadı."
            begeni_sayisi = begeni.find("span").getText() if begeni.find("span") else "Beğeni sayısı bulunamadı."

            # Yıldız puanını hesapla
            yildiz_puani = 0
            yorum_baslik = yorum.find_previous("div", class_="comment-header")
            if yorum_baslik:
                yorum_derecesi = yorum_baslik.find("div", class_="comment-rating")
                if yorum_derecesi:
                    yildizlar = yorum_derecesi.find_all("div", class_="full", style="width: 100%; max-width: 100%;")
                    yildiz_puani = len(yildizlar)

            if yorum_text not in collected_comments:  # Daha önce eklenmemişse
                collected_comments.add(yorum_text)
                all_comments.append({
                    'Ürün Marka': urun_marka,
                    'Ürün İsmi': urun_ismi,
                    'Fiyat': urun_fiyati,
                    'Değerlendirme Sayısı': degerlendirme_sayisi,
                    'Yorum Sayısı': yorum_sayisi,
                    'Ürünün Ortalama Puanı': urun_puani,
                    'Satıcı Adı': satici_adi,
                    'Satıcı Puanı': satici_puani,
                    'Yorum': yorum_text,
                    'Yorum Satıcı Adı': saticiAdiYorum,  # Yorumun altındaki satıcı adı
                    'Beğeni Sayısı': begeni_sayisi,  # Beğeni sayısı
                    'Yıldız Puanı': yildiz_puani  # Yıldız puanı
                })
                print(f"Yorum {len(all_comments)}: {yorum_text} - Satıcı: {saticiAdiYorum} - Beğeni Sayısı: {begeni_sayisi} - Yıldız: {yildiz_puani}")

    # Sayfayı biraz aşağı kaydır
    driver.execute_script("window.scrollBy(0, window.innerHeight);")

    # 2 saniye bekle
    time.sleep(2)

    # Yeni sayfa yüksekliğini kontrol et
    new_height = driver.execute_script("return document.body.scrollHeight")
    
    if new_height == last_height:
        if no_scroll_start_time is None:
            # Sayfa kaydırılamıyorsa ve zamanlayıcı başlamadıysa başlat
            no_scroll_start_time = time.time()
        else:
            # Sayfa kaydırılamıyorsa ve zamanlayıcı başladıysa geçen süreyi kontrol et
            elapsed_no_scroll_time = time.time() - no_scroll_start_time
            if elapsed_no_scroll_time > 90:  # 90 saniye = 1.5 dakika
                print("1.5 dakikadır sayfa kaydırılamıyor, veri çekme işlemi sonlandırılıyor.")
                break
    else:
        # Sayfa kaydırıldıysa zamanlayıcıyı sıfırla
        no_scroll_start_time = None
    
    last_height = new_height

# Tarayıcıyı kapat
driver.quit()

# Verileri bir DataFrame'e ekle
df = pd.DataFrame(all_comments)

# Veriyi Excel dosyasına kaydet
df.to_excel("urun_yorumlari.xlsx", index=False)

print("Veriler urun_yorumlari.xlsx dosyasına kaydedildi.")
