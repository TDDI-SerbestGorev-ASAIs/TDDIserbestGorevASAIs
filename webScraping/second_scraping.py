#Müşteri yorumlarını yıldız bazlı çekmek istediğimizde kullandığımız kod

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import pandas as pd
import os

# veri çekmek istediğiniz sayfanın değerlendirme URL listesini tanımlayın
urls = [ ] 
num = 5  # ürüne kaç yıldız vermiş olan müşterilerin yorumlarını çekmek istiyorsanız belirtin
file_name = " "  # Verileri kaydetmek için dosya adı oluşturunuz "HuaweiFreebudsSe.xlsx" gibi

# Selenium WebDriver ile Chrome'u başlat
driver = webdriver.Chrome()

# Yıldız puanına göre tıklama işlemi
try:
    driver.get(urls[0])
    time.sleep(5)  # Sayfanın yüklenmesi için bekleyin
    
    # Gizlilik politikasını kapatmak için
    try:
        # Sayfayı biraz aşağı kaydırarak butonun görünür olmasını sağlayın
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(1)
        accept_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        accept_button.click()
        print("Gizlilik politikası kabul edildi.")
    except Exception as e:
        print(f"Gizlilik politikası kabul düğmesi bulunamadı veya zaten kapalı. Hata: {e}")
    
    time.sleep(2)  # Kapatma işleminden sonra bekleyin
    # Yıldız puanı elementini bul ve tıklayın
    star_elements = driver.find_elements(By.CLASS_NAME, "ps-stars__content")
    for star_element in star_elements:
        stars = star_element.find_elements(By.CLASS_NAME, "full")
        full_width_stars = [star for star in stars if "width: 100%; max-width: 100%;" in star.get_attribute("style")]
        if len(full_width_stars) == num:  # KAÇ YILDIZLI YORUMLARI GETİRMEK İSTİYORSAK O SAYIYI YAZACAĞIZ
            star_element.click()
            time.sleep(5)  # Sayfanın yeniden yüklenmesi için bekleyin
            print(f"{num} yıldızlı yorumlar geldi.")
            break

except Exception as e:
    # Element bulunamazsa veya başka bir hata olursa
    print(f"Tıklama işlemi gerçekleşmedi. Hata: {e}")
    
# Tüm yorumları saklamak için bir liste oluştur
all_comments = []

# Yıldız puanına göre sayfa içeriğini tekrar al ve yorumları işleme başla
html_content = driver.page_source
html_sayfa = BeautifulSoup(html_content, "html.parser")

# Ürün bilgilerini al
marka = html_sayfa.find("span", class_="product-brand")
urun_marka = marka.getText() if marka else "Ürün markası bulunamadı."

isim = html_sayfa.find("span", class_="product-name")
urun_ismi = isim.getText() if isim else "Ürün ismi bulunamadı."

fiyat = html_sayfa.find("span", class_="prc-dsc")
urun_fiyati = fiyat.getText() if fiyat else "Fiyat bulunamadı."

degerlendirmeYorumSayisi = html_sayfa.find("div", class_="ps-ratings__counts")
bol = degerlendirmeYorumSayisi.getText() if degerlendirmeYorumSayisi else "Degerlendirme sayisi bulunamadı."
degerlendirmeSayi, yorumSayi = bol.split("•")

# Sayıları ayrıştırdık
degerlendirme_sayisi = int(degerlendirmeSayi.split()[0])
yorum_sayisi = int(yorumSayi.split()[0])

urunPuan = html_sayfa.find("div", class_="ps-ratings__count-text")
urun_puani = urunPuan.getText() if urunPuan else "Ürünün puanı bulunamadı."

SatıcıAdı = html_sayfa.find("span", class_="merchant-name")
satici_adi = SatıcıAdı.getText() if SatıcıAdı else "Ürün satıcı adı bulunamadı."

SatıcıPuanı = html_sayfa.find("div", class_="sl-pn")
satici_puani = SatıcıPuanı.getText() if SatıcıPuanı else "Ürün satıcı puanı bulunamadı."

collected_comments = set()
last_height = driver.execute_script("return document.body.scrollHeight")
no_scroll_start_time = None

while True:
    html_content = driver.page_source
    html_sayfa = BeautifulSoup(html_content, "html.parser")

    yorumlar = html_sayfa.find_all("div", class_="comment-text")
    satici_bilgileri = html_sayfa.find_all("span", class_="seller-name-info")
    begeni_sayilari = html_sayfa.find_all("div", class_="rnr-com-like")

    if yorumlar and satici_bilgileri and begeni_sayilari:
        for yorum, satici, begeni in zip(yorumlar, satici_bilgileri, begeni_sayilari):
            yorum_text = yorum.getText()
            saticiAdiYorum = satici.getText() if satici else "Satıcı bilgisi bulunamadı."
            begeni_sayisi = begeni.find("span").getText() if begeni.find("span") else "Beğeni sayısı bulunamadı."

            yildiz_puani = 0
            yorum_baslik = yorum.find_previous("div", class_="comment-header")
            if yorum_baslik:
                yorum_derecesi = yorum_baslik.find("div", class_="comment-rating")
                if yorum_derecesi:
                    yildizlar = yorum_derecesi.find_all("div", class_="full", style="width: 100%; max-width: 100%;")
                    yildiz_puani = len(yildizlar)

            if yorum_text not in collected_comments:
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
                    'Yorum Satıcı Adı': saticiAdiYorum,
                    'Beğeni Sayısı': begeni_sayisi,
                    'Yıldız Puanı': yildiz_puani
                })
                print(f"Yorum {len(all_comments)}: {yorum_text} - Satıcı: {saticiAdiYorum} - Beğeni Sayısı: {begeni_sayisi} - Yıldız: {yildiz_puani}")

    driver.execute_script("window.scrollBy(0, window.innerHeight);")
    time.sleep(5)

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        if no_scroll_start_time is None:
            no_scroll_start_time = time.time()
        else:
            elapsed_no_scroll_time = time.time() - no_scroll_start_time
            if elapsed_no_scroll_time > 240:
                print("4 dakikadır sayfa kaydırılamıyor, veri çekme işlemi sonlandırılıyor.")
                break
    else:
        no_scroll_start_time = None

    last_height = new_height

# Tarayıcıyı kapat
driver.quit()

# Verileri bir DataFrame'e ekle
df_new = pd.DataFrame(all_comments)

if os.path.exists(file_name):
    df_existing = pd.read_excel(file_name)
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
else:
    df_combined = df_new

df_combined.to_excel(file_name, index=False)

print(f"Veriler {file_name} dosyasına kaydedildi.")
