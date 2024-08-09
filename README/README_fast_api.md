Bu proje, bir NER (Adlandırılmış Varlık Tanıma) modeli kullanarak metinleri işler ve belirli kategorilere göre puanlama yapar.

GEREKSİNİMLER

Python 3.7+
FastAPI
Uvicorn
Pydantic
Pandas
Transformers

KURULUM

Gerekli paketleri yüklemek için aşağıdaki adımları izleyin:

```bash
pip install fastapi uvicorn pandas transformers pydantic
```
KULLANIM

1. main.py dosyasındaki entity_model_path değişkenini kendi model dosya yolunuza göre ayarlayın.

2. Uygulamayı başlatın: 

uvicorn main:app --reload

3. API'yi test edin:

POST: '/process/'
Body: '{ "text": "İşlenecek metin buraya gelecek." }
