Bu proje, bir Excel dosyasındaki ürün verilerini temizlemek ve analiz etmek için geliştirilmiştir.

KURULUM

1. Gerekli kütüphaneleri yüklemek için terminal veya komut istemcisine aşağıdaki komutları yazabilirsiniz:

pip install pandas
pip install emoji

ÇALIŞTIRMA

1. Temizlemek istediğiniz veri setini içeren Excel dosyasının yolunu kodda belirtilen kısma yazınız.

| Parametre İsmi                      | Varsayılan Değer | Açıklama |
|-------------------------------------|------------------|----------|
| texts                               | -                | Önişleme yapılacak metinlerin listesi. |
| ozel_karakterin_boşlukla_degismesi  | True             | Metindeki özel karakterler (örneğin !, ?, @, # vb.) boşluklarla değiştirilir. |
| kucuk_harfe_cevirme                 | True             | Metindeki tüm harfler küçük harfe çevirerek büyük-küçük harf farkını ortadan kaldırarak tutarlı bir veri yapısı oluşturur. |
| newline_karakteri_boslukla_degistirme | True           | Metindeki yeni satır karakterleri (\n) boşluklarla değiştirilir. Bu, metindeki satırların tek bir satırda birleştirilmesini sağlar. |
| fazla_boslukları_silme              | True             | Metindeki fazla boşluklar kaldırılır ve sadece tek bir boşluk bırakılır. |
| emoji_silme                         | True             | Bu, metindeki emojilerin veri analizini etkilememesi için yapılır. |
| tl_silme                            | True             | Fiyat sütunundaki "TL" simgesi kaldırılır. |
| parantez_silme                      | True             | Beğeni sayısı sütunundaki parantez içindeki sayılar çıkarılır. Bu, parantez içindeki sayıların sade bir sayı formatında kalmasını sağlar. |
| renk_bilgisi_cikarma                | True             | Ürün ismi içinden renk bilgisi çıkarılır ve ayrı bir sütunda saklanır. |
| model_bilgisi_cikarma               | True             | Ürün ismi içinden model bilgisi çıkarılır ve ayrı bir sütunda saklanır. |
| baglanti_tipi_cikarma               | True             | Ürün ismi içinden bağlantı tipi bilgisi çıkarılır ve ayrı bir sütunda saklanır. |


Bu ayarları True veya False olarak değiştirerek veri temizleme ve analiz işlemlerini ihtiyacınıza göre özelleştirebilirsiniz.
