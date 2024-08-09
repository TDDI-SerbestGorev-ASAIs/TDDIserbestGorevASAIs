MODEL
** proje model drive linki : "https://drive.google.com/drive/folders/14E4iM4HaC0BeN97iRRQa4TEByO7MwVXS?usp=drive_link"

Bu proje, BERT tabanlı bir model kullanarak metinlerdeki varlıkları tanımlayıp bu varlıklar üzerinde duygu analizi yapmayı amaçlamaktadır. 

KURULUM

1. Aşağıdaki Python kütüphanelerini yükleyin:

!pip install simpletransformers
!pip install nltk
!pip install pandas
!pip install transformers

ÇALIŞMA 

1. Google Drive'ı bağlayıp veriyi pandas DataFrame'e aktarın.

df = pd.read_csv("/content/veri.csv")

