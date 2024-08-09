KURULUM

1. Gerekli kütüphaneleri yüklemek için terminal veya komut istemcisine aşağıdaki komutları yazabilirsiniz:

pip install pandas jpype1

2. Zemberek kütüphanesini indirin ve proje dizinine yerleştirin. (zemberek-full.jar dosyası).

İndirme linki: https://github.com/ahmetaa/zemberek-nlp 

Bu linke girip "Jar Dağıtımları" kısmından Google Drive sayfasına tıklamalısınız. Burada farklı versiyonlar için jar dosyaları bulunmaktadır. Bu dosyaların içinden "distributions" dosyasını açmalı ve 0.17.1 sürümlü dosyadan zemberek-full.jar adlı dosyayı yüklemelisiniz.

3. Stop words ve korunan kelimeler dosyalarını proje dizinine yerleştirin.

KULLANIM

1. ZEMBEREK_PATH değişkenini, Zemberek kütüphanesinin yolunu gösterecek şekilde ayarlayın:

2. Stop words ve korunan kelimeler dosyalarının yolunu belirleyin:

3. Yazım hataları custom_corrections sözlüğü ile manuel olarak düzeltilebilir.
