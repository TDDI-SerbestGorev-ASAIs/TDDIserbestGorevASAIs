import pandas as pd
import re
from jpype import JClass, startJVM, shutdownJVM, getDefaultJVMPath
import jpype

# Zemberek'i başlat
ZEMBEREK_PATH = r"C:\Users\beyza\Downloads\zemberek-full (3).jar"
if not jpype.isJVMStarted():
    startJVM(getDefaultJVMPath(), '-ea', '-Djava.class.path=%s' % (ZEMBEREK_PATH))

# Zemberek sınıflarını yükle
morphology = JClass('zemberek.morphology.TurkishMorphology').createWithDefaults()
TurkishSpellChecker = JClass('zemberek.normalization.TurkishSpellChecker')
Paths = JClass('java.nio.file.Paths')

# Stop words listesini yükle
def load_stop_words(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return set(line.strip() for line in file)

def load_protected_words(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return set(line.strip() for line in file)

# Olumsuzluk kelimeleri listesi
negation_words = ['değil', 'yok', 'hiç', 'asla', 'hayır']

# Sesli harfler
vowels = 'aeıioöuü'
back_vowels = 'aıou'
front_vowels = 'eiöü'

# Stop words dosyasının yolu
stop_words_file =  r" " # stop words listesinin path'ini ekleyin. Bizim kullandığımıza stopWords.txt den ulaşabilirsiniz.
stop_words = load_stop_words(stop_words_file)

protected_words_file = r" " # proje için önemli olan ve değişmemesi gereken kelimelerin listesini hazırladık korunanKelimeler.txt dosyasından da ona ulaşabilirsiniz. Path'ini burada belirtin
protected_words = load_protected_words(protected_words_file)

# zemberek kütüphanesinin spell checker'ının düzeltemediği bazı kelimeleri bu sözlükte topladık
custom_corrections = {
    # 'hatalıkelime': 'düzgünkelime'
    'kırıklığ': 'kırıklık',
    'kulaklıgı':'kulaklığı',
    'kısıklıgi':'kısıklığı',
    'sarki':'şarkı',
    'cizirtisi':'cızırtısı',
    'cizirti':'cızırtı',
    'atakadaşlar':'arkadaşlar',
    'jarz':'şarj',
    'kulaklığ':'kulaklık',
    'kulaklik':'kulaklık',
    'sarj': 'şarj',
    'şarz':'şarj',
    'hastahane': 'hastane',
    'çalışoyormu': 'çalışıyor mu',
    'şarz': 'şarj',
    'hemde': 'hem de',
    'almistim': 'almıştım',
    'atmasini': 'atmasını',
    'tt': 'tt',
    '3G': '3G',
    'banu': 'banu',
    'tunçelli': 'tunçelli',
    'berkan': 'berkan',
    'yatirimi': 'yatırımı',
    'intro': 'intro',
    'bi': 'bir',
    'bı': 'bir',
    'asya': 'asya',
    'aq': 'aq',
    'lı': 'lı',
    'zikeriz': 'sikeriz',
    'satilirken': 'satılırken',
    'celikler': 'çelikler',
    'bisey': 'bir şey',
    'cimere': 'cimere',
    'tl': 'tl',
    'hayirdir': 'hayırdır',
    'nerde': 'nerede',
    'gozunu': 'gözünü',
    'celikler': 'çelikler',
    'buyrun': 'buyrun',
    'Buyrun': 'buyrun',
    'buna': 'buna',
    'cigabayt': 'gigabayt',
    'okadar': 'o kadar',
    'hirsiz': 'hırsız',
    'Bisey': 'bir şey',
    'demektir': 'demektir',
    '3gb': '3 gb',
    'kullanacam': 'kullanacağım',
    'geçicem': 'geçeceğim',
    'tabiki': 'tabiki',
    'TCELL': 'tcell',
    'musterinizim': 'müşterinizim',
    '1gb': '1 gb',
    'acaip': 'acayip' ,
    'acanda': 'açınca',
    'acilmir': 'açılmıyor',
    'alıcam': 'alacağım',
    'ni': 'ni',
    'nı': 'nı',
    'hıc': 'hiç',
    'Hıc': 'hiç',
    'birtanesinden': 'bir tanesinden',
    'kulaktada': 'kulakta da',
    'kamdiriyorsunuz': 'kandırıyorsunuz',
    'f': 'f',
    'p': 'p',
    '2ayda': '2 ayda',
    'pismanim': 'pişmanım',
    'kullanınımı': 'kullanımı',
    'red': 'red',
    'gec': 'geç',
    'haketmiyor': 'hak etmiyor',
    'eslesme': 'eşleşme',
    'kulanamadım': 'kullanamadım',
    'gönderebiliyonuz': 'gönderebiliyorsunuz',
    'boguk': 'boğuk',
    'BOGUK': 'boğuk',
    'Boguk': 'boğuk',
    'calıyor': 'çalıyor',
    'vericem': 'vereceğim',
    'kullabilirz': 'kullanabiliriz',
    'start': 'start',
    'pause': 'pause',
    'çalışıyormu': 'çalışıyor mu',
    'bağa': 'baya',
    'USTASIDA': 'ustası da',
    '_k': '_k',
    'iİade': 'iade',
    'EDİCEM': 'edeceğim',
    'qulaqciq': 'kulaklık',
    'elimede': 'elime de',
    'diswrdaki': 'dışardaki',
    'başkadı': 'başladı',
    'bendemi': 'bende mi',
    'Telefonlada': 'telefonla da',
    'almayin': 'almayın',
    'seviyeside': 'seviyesi de',
    '4ay': '4 ay',
    'alali': 'alalı',
    'fln': 'falan',
    'cikti': 'çıktı',
    'nolur': 'nolur',
    'turkcr': 'turkcr',
    'arti': 'artı',
    'cihazi': 'cihazı',
    'varmı': 'var mı',
    'bare': 'bari',
    'seside': 'sesi de',
    'dı': 'dı',
    'paketlemeside': 'paketlemesi de',
    'nerden': 'nereden',
    'turkcr': 'turkcr',
    'arti': 'artı',
    'cihazi': 'cihazı',
    'varmı': 'var mı',
    'ıyı':'iyi',
    'acma': 'açma',
    'tusu': 'tuş',
    'çalışmıyormu': 'çalışmıyor mu',
    'Şuanlık': 'şu anlık',
    'fakan': 'falan',
    'şuanlık': 'şu anlık',
    'kaliteai': 'kalitesi',
    'Fp': 'fp',
    'FP': 'fp',
    'Typ': 'type',
    'typ': 'type',
    'sifir': 'sıfır',
    'mic': 'mikrofon',
    'flan': 'falan',
    'drek': 'direkt',
    'yeğanlar': 'yeğenler',
    'yaxşıdır': 'iyidir',
    'cikiyor': 'çıkıyor',
    'yinede': 'yine de',
    'type': 'type',
    'muthis': 'müthiş',
    'yildiz':'yıldız',
    'alınnn':'alın',
    'asiri':'aşırı',
    'hizli':'hızlı',
    'ayfon':'iphone',
    'no':'numara',
    'urun': 'ürün',
    'saolun':'sağ olun',
    'alabi':'alabi',
    'li':'li',
    'rsi':'rsi',
    'ni':'ni',
    'z':'z',
    'g': 'g',
    'olurmusunuz': 'olur musunuz',
    'typce': 'type c',
    'edicem': 'edeceğim',
    'çooook':'çok',
    'çoook':'çok',
    'vibe': 'vibe',
    'girl': 'girl',
    'math': 'math',
    'bendede': 'bende de',
    'kizim': 'kızım',
    'karsi': 'karşı',
    'ileriyor': 'iletiyor',
    'kalıtesi': 'kalitesi',
    'nin': 'nin',
    'katileti': 'kalitesi',
    'geckindir': 'geçkin',
    'aldirin': 'aldır',
    'kalıteli': 'kaliteli',
    'kullağ': 'kulak',
    'kulağ': 'kulak',
    'ade':'iade',
    'gecirmiyor': 'geçirmiyor',
    'fp': 'fp',
    'gonul': 'gönül',
    'İphone': 'iphone',
    'teredü': 'tereddüt',
    'Kateli': 'kaliteli',
    'katesi': 'kalitesi',
    'almistik': 'almıştık',
    'omru': 'ömrü',
    'dı': 'dı',
    'hamıya': 'hepinize',
    'əla': 'harika',
    'tövsiyə': 'tavsiye',
    'basıt': 'basit',
    'acilmis':'açılmış',
    'ri': 'ri',
    'ka': 'ka',
    'tşk': 'teşekkür',
    'suanlık': 'şu anlık',
    'ıkı': 'iki',
    'assiri': 'aşırı',
    'bakıcaz': 'bakacağız',
    'kapagi': 'kapağı',
    'vercem': 'vereceğim',
    'poco': 'poco',
    'lerde': 'lerde',
    'edicem':'edicem',
    'ozur':'özür',
    'guya':'güya',
    'agrı': 'ağrı',
    'h': 'h',
    'r': 'r',
    'k': 'k',
    'abest': 'abest',
    'yildiz': 'yıldız',
    'urunmus': 'ürünmüş',
    'sağlamadi': 'sağlamadı',
    'aras': 'aras',
    'duruyom': 'duruyorum',
    'ikisinide': 'ikisini de',
    'olub': 'olup',
    'müq': 'mükemmel',
    'vermemim': 'vermemin',
    'satjı': 'şarjı',
    'ozenliydi': 'özenliydi',
    'korgo': 'kargo',
    'huzli': 'hızlı',
    'kurutum': 'kuruttum',
    'gyat': 'gayet',
    'bebişin': 'bebişin',
    'almaın': 'almayın',
    'ıyı': 'iyi',
    'muthis': 'müthiş',
    'alınnn': 'alın',
    'asiri': 'aşırı',
    'max':'max',
    'takili':'takılı',
    'mezilden':'menzilinden',
    'kalirim':'kalırım',
    'insalh':'inşallah',
    'israrımdan':'ısrarımdan',
    'goat':'goat',  
    'storedan':'mağaza', 
    'omru':'ömrü',
    'noise':'gürültü',
    'volumede':'volume',
    'ipad':'ipad',
    'yiki':'iyiki',
    'yarayağını':'yaracağını',
    'onuda':'onuda',
    'deyilmi':'değil mi',
    'gecebilir':'geçebilir',
    'music':'müzik',
    'anc':'anc',
    'saticisindan':'satıcısından',
    'prodan':'pro',
    'değermi':'değer mi',
    'hari':'harika',
    'sound':'ses',
    'kardon':'kardon',
    'acinca':'açınca',
    'aliyo':'alıyor',
    'odemezsiniz':'ödemez',
    'hizli':'hızlı',
    'ode':'öde',
    'dıs':'dış',
    'diş':'dış',
    'dis':'dış',
    'ıc':'iç',
    'ic':'iç',
    'ıç':'iç',
    'kdr':'kadar',
    'alirdim':'alırdım',
    'alirdi':'alırdı',
    'alir':'alır',
    'msj':'mesaj',
    'amazing':'harika',
    'product':'ürün',
    'comes':'gelmek',
    'new':'yeni',
    'and':'ve',
    'garantı':'garanti',
    'dk':'dakika',
    'algiliyor':'algılıyor',
    'yi':'yi',
    'soze':'söze',
    'aga':'arkadaş',
    'musteri':'müşteri',
    'efso':'efsane',
    'c':'c',
    'qr':'qr',
    's':'s',
    'l': 'l',
    'se':'se',
    'cizirtisi,':'cızırtı',
    'cizirti':'cızırtı',
    'deği':'değil',
    'sarki':'şarkı',
    'şarki':'şarkı',
    'sarkı':'şarkı',
    'gecirmesi':'geçirmesi',
    'kucuk':'küçük',
    'buyuk':'büyük',
    'phone':'telefon',
    'jarz':'şarj',
    'buda':'bu da',
    'oda':'o da',
    'şuda':'şu da',
    'ustunede':'üstüne de',
    'alıcam':'alacağım',
    'smal':'small',
    'ikisaatten':'iki saatten',
    'allmayınn':'almayın',
    'deymez':'değmez',
    'samsun':'samsung',
    'şua':'şuan',
    'qulaqciq':'kulaklık',
    'bendemi':'bende mi',
    'hisirti':'hışırtı',
    'benze':'bence',
    'hoj':'hoş',
    'hojj':'hoş',
    'hojjj':'hoş',
    'drek':'direkt',
    'iyide':'iyi de',
    'kötüde':'kötü de',
    'cizirti':'cızırtı',
    'esim':'eşim',
    'müren':'müren',
    'iciniz':'içiniz',
    'olaun':'olsun',
    'cvp':'cevap',
    'saglikli':'sağlıklı',
    'terettüt':'tereddüt',
    'iykide':'iyi ki de',
    'ıphone':'iphone',
    'tereddütüm':'tereddüt',
    'ztn':'zaten',
    'gedi':'geldi',
    'very':'çok',
    'delivery':'teslimat',
    '5k':'5k',
    'aplee':'apple',
    'kalir':'kalır',
    'bagınızı':'bağınızı',
    'aldm':'aldım',
    'gorustum':'görüştüm',
    'güncellicem':'güncelleyeceğim',
    'lol':'lol',
    'konusa':'konuda',
    'şahaneee':'şahane',
    'yanlıs':'yanlış',
    'yanlis':'yanlış',
    'yanlıslıkla':'yanlışlıkla',
    'yanlislikla':'yanlışlıkla',
    'yanlıslık':'yanlışlık',
    'yanlislik':'yanlışlık',
    'napalım':'ne yapalım',
    'gorsel':'görsel',
    'saglik':'sağlık',
    'sunger':'sünger',
    'eşimede':'eşime de',
    'guzal':'güzel',
    'hicbi':'hiçbir',
    'kulakli':'kulaklık',
    'muzigi':'müziği',
    'sinif':'sınıf',
    'full':'full',
    'arizalandi':'arızalandı',
    'koselerin':'köşelerin',
    'kiii':'ki',
    'kii':'ki',
    'yapiniz':'yapınız',
    'yapilmiş':'yapılmış',
    'operlör':'hoparlör',
    'temassiz':'temassız',
    'temassizlik':'temassızlık',
    'gordum':'gördüm',
    'suan':'şu an',
    'yasamadim':'yaşamadım',
    'tatli':'tatlı',
    'bayagi':'bayağı',
    'nden':'neden',
    'iyidi':'iyiydi',
    'resetlemek':'sıfırlamak',
    'yapıcam':'yapacağım',
    'lara':'lara',
    'fp':'fiyat performans',
    'nirazdaha':'biraz daha',
    'ata':'ara',
    'sikinti':'sıkıntı',
    'şark':'şarj',
    'cizirti':'cızırtı',
    'cizirtili':'cızırtılı',
    'jarz':'şarj',
    'sifirlama':'sıfırlama',
    'du': 'du',
    'hoc': 'hiç',
    'sayfayi': 'sayfayı',
    'hiz': 'hız',
    'interneti': 'interneti',
    'bisi': 'bir şey',
    'sori': 'sorry',
    'herbir': 'her bir',
    'akp': 'akp',
    'küsure': 'küsüre',
    'nolu': 'numaralı',
    'dsl': 'dsl',
    'bunuda': 'bunu da',
    'export': 'export',
    'wp': 'wp',
    'oçlar': 'oçlar',
    'w': 'w',
    'bergman': 'bergman',
    'demedi': 'demedi',
    'yarisini': 'yarısını',
    'iranda': 'iranda',
    'km': 'km',
    'üsküdarlı': 'üsküdarlı',
    'tr': 'tr',
    'ç': 'ç',
    'enigi': 'eniği',
    'yanımdaya': 'yanımdaya',
    'elon': 'elon',
    'passo': 'passo',
    'nın': 'nın',
    'so': 'so',
    'amk': 'amk',
    'ş': 'ş',
    'çin': 'çin',
    '3g': '3g','cardi': 'icardi',
    'mauro': 'mauro',
    '6a': '6a',
    'kacır': 'kacır',
    'd': 'd',
    'ltfn': 'lütfen',
    'anani': 'ananı',
    'oevladı': 'orospu evladı',
    'durumuda': 'durumu da',
    'elazigin': 'elazığın',
    'diger':'diğer',
    'sağlayıcı':'sağlayıcı',
    'saglayici':'sağlayıcı',
    'saglayıcı':'sağlayıcı',
    'wadofone':'vodafone',
    'yapsıs':'yapısı',
    'baska':'başka',
    'cizirti':'cızırtı',
    'problem':'problem',
    'kulaklığın':'kulaklık',
    'sutr':'süre',
    'kullanisli':'kullanışlı',
    'kalıtesı':'kalitesi',
    'bayildim':'bayıldım',
    'ürünrün':'ürün',
    'sarjindan':'şarjından',
    'kalıtelı':'kaliteli',
    'keliteli':'kaliteli',
    'iyikide':'iyi ki',
    'kulaklik':'kulaklık',
    'sarja':'şarja',
    'ürüni':'ürün',
    'bassı':'bas',
    'fiyatina':'fiyatına',
    'şarji':'şarjı',
    'şarzi':'şarjı',
    'bayildim':'bayıldım',
    'özellikle':'özellikle',
    'sağsalim':'sağ salim',
    'arkadsımda':'arkadaşımla',
    'hediye':'hediye'
}

# Spell check için
def spell_check(tokens):
    spell_checker = TurkishSpellChecker(morphology)
    corrected_tokens = []
    for token in tokens:
        if any(protected_word in token for protected_word in protected_words):
            print(f"Protected Word: {token} (No Correction)")
            corrected_tokens.append((token, '_PROTECTED'))
        elif token in custom_corrections:
            corrected_token = custom_corrections[token]
            print(f"Custom Correction: {token} -> {custom_corrections[token]}")
            corrected_tokens.append((corrected_token, '_CORRECTED'))
        elif not spell_checker.check(token):
            suggestions = spell_checker.suggestForWord(token)
            if suggestions.size() > 0:
                print(f"Original: {token}, Suggestion: {suggestions.get(0)}")
                corrected_tokens.append((suggestions.get(0), '_CORRECTED'))
            else:
                corrected_tokens.append((token, '_ORIGINAL'))
        else:
            corrected_tokens.append((token, '_ORIGINAL'))
    return corrected_tokens
# cümleyi tokenlarına ayırmak için
def tokenize(text):
    if not isinstance(text, str):
        return []
    tokens = re.findall(r'\b\w+\b', text)
    return [token for token in tokens if token.lower() not in stop_words]

#tokenları analiz etmek için
def analyze_token(token):
    return morphology.analyzeSentence(token)

#tokenları kök ve eklerine ayırıyoruz
def decompose_token(token):
    analysis = analyze_token(token)
    results = morphology.disambiguate(token, analysis).bestAnalysis()
    if results.size() > 0:
        root = results.get(0).getLemmas()[0]
        suffixes = results.get(0).getMorphemes()
        return root, suffixes
    return token, []

#protected_words dosyasında olan kelimeler dışında kök ve eklerine ayırmak için
def process_word(word):
    if word in protected_words:
        return word  # Kelime protected_words dosyasındaki kelimelerden biriyse aynı bırak
    root, suffixes = decompose_token(word)
    if root == 'UNK':
        return word  # Return the original word if it's 'UNK'
    return root  # Return the root without

#kelimenin olumsuzluk ekine sahip olup olmadığını kontrol eder
def has_negation_suffix(suffixes):
    return any('Neg' in str(suffix) for suffix in suffixes)
#fiil mi kontrol edilir
def is_verb(suffixes):
    return any('Verb' in str(suffix) for suffix in suffixes)
#sıfat mı kontrol edilir
def is_adjective(suffixes):
    return any('Adj' in str(suffix) for suffix in suffixes)

#olumsuzluk eki alan kelimeler etiketlenir
def mark_negations(tokens):
    marked_tokens = []
    for token, tag in tokens:
        root, suffixes = decompose_token(token)
        if has_negation_suffix(suffixes) or root == 'UNK':
            marked_tokens.append((token, '_NEG'))
        else:
            marked_tokens.append((token, tag))
    return marked_tokens

# -sız,-siz,-suz,-süz gibi olumsuzluk anlamı taşıyan ekleri içeren kelimeleri aynı bırakır
# olumsuzluk eki -ma,-me içeren kelimeler aynı kalır
# -ebilmek ekinin olumsuzu -ama, -eme, -amı, -emi eklerini zemberek kütüphanesi tanımlayaadığı için bu ekleri içeren kelimeler aynı bırakılır
# 'ma', 'me', 'mı', 'mü', 'amı','ama', 'eme','emi' be ekleri içeren korunması gereken kelimeler aynı kalırken diğer korunması gereken kelimeler custom_corrections kütüphanesinden öncelikle kontrol edilir
#bunlar dışındaki kelimeler de lemmatization işleminden geçer
def lemmatize_tokens(tokens):
    lemmatized_tokens = []
    for token, tag in tokens:
        # Java String'i Python str'ye dönüştür
        token = str(token)
        if any(suffix in token for suffix in negation_words):
            lemmatized_tokens.append((token, tag))
        elif token.endswith(('sız', 'süz','siz','suz')):
            # Eğer kelime 'sız' veya 'süz' ile bitiyorsa, kelimeyi olduğu gibi bırak
            lemmatized_tokens.append((token, tag))
        elif any(suffix in token for suffix in ['ama', 'eme', 'amı', 'emi']):
            lemmatized_tokens.append((token, tag))
        elif tag == '_PROTECTED':
            if any(substring in token for substring in ['ma', 'me', 'mı', 'mü', 'amı','ama', 'eme','emi']):
                lemmatized_tokens.append((token, tag))  # Return the original token if it contains any of these characters
            else:
                for protected_word in protected_words:
                    if protected_word in token:
                        if protected_word in custom_corrections:
                            corrected_word = custom_corrections[protected_word]
                            lemmatized_tokens.append((corrected_word, tag))
                        else:
                            lemmatized_tokens.append((protected_word, tag))
                        break
                else:
                    lemmatized_tokens.append((token, tag))  # If no protected word is found, leave it as is
        elif tag == '_NEG':
            lemmatized_tokens.append((token, tag))
        else:
            root, _ = decompose_token(token)
            if is_adjective(_):  # If it's an adjective
                lemmatized_tokens.append((token, tag))  # Preserve the adjective in its original form
            else:
                lemmatized_tokens.append((root, tag))
    return lemmatized_tokens

#kelimenin son sesli harfine bakar
def get_last_vowel(word):
    for char in reversed(word):
        if char in vowels:
            return char
    return None
#kelimenin son sesli harfine göre mastar eki eklenir    
def restore_negations(tokens):
    restored_tokens = []
    for root, suffixes in tokens:
        root_str = str(root)
        if isinstance(suffixes, str) and suffixes == '_ORIG':
            restored_tokens.append(root_str)
        else:
            if is_verb(suffixes):
                last_vowel = get_last_vowel(root_str)
                if last_vowel:
                    if last_vowel in back_vowels:
                        restored_tokens.append(root_str + 'mak')
                    elif last_vowel in front_vowels:
                        restored_tokens.append(root_str + 'mek')
                else:
                    restored_tokens.append(root_str + 'mak')
            else:
                restored_tokens.append(root_str)
    return restored_tokens
#zemberek kütüphanesi ile part of speech etiketlemesi yapılır
def pos_zemberek(tokens):
    pos_etiketleri = []
    for token in tokens:
        analysis = morphology.analyzeAndDisambiguate(token).bestAnalysis()
        if analysis:
            best = analysis.get(0)  # Fixed here to use get(0) instead of [0]
            pos_etiketleri.append((token, best.getPos().shortForm))
        else:
            pos_etiketleri.append((token, 'UNK'))
    return pos_etiketleri
  
#çekim ekleri kaldırılır
def remove_inflectional_suffixes(suffixes):
    inflectional_suffixes = {'Verb', 'Noun', 'Abl', 'Acc', 'Fut', 'Imp', 'Neg', 'Pst', 'Pres', 'Ptc', 'A2sg', 'A3sg', 'Pnon', 'Nom', 'P1sg', 'Loc', 'Gen', 'Dat'}
    filtered_suffixes = [suffix for suffix in suffixes if suffix not in inflectional_suffixes]
    return filtered_suffixes

def process_review(review):
    tokens = tokenize(review)
    tokens = spell_check(tokens)  # Apply spell check here
    marked_tokens = mark_negations(tokens)
    lemmatized_tokens = lemmatize_tokens(marked_tokens)
    restored_tokens = restore_negations(lemmatized_tokens)
    pos_etiketleri = pos_zemberek(restored_tokens)
    return {
        'tokens': tokens,
        'marked_tokens': marked_tokens,
        'lemmatized_tokens': lemmatized_tokens,
        'restored_tokens': restored_tokens,
        'pos_etiketleri': pos_etiketleri
    }

# Veriyi oku
input_file = r"C:\Users\beyza\sonuc.xlsx"
df = pd.read_excel(input_file)


def process_review_apply(review):

    processed_review = process_review(review)
    restored_tokens = processed_review['restored_tokens']
    processed_review_text = ' '.join(str(token) for token in restored_tokens)
    return pd.Series([processed_review_text])

def normalize_turkish_i(text):
    if isinstance(text, str):
        return text.replace('i̇', 'i')
    return text  
    
    # Tüm metin sütunlarını normalize etme
df['Yorum'] = df['Yorum'].apply(normalize_turkish_i)

# 'Yorum' sütununa işlemi uygula ve sonuçları yeni sütunlara ekle
df['text'] = df['Yorum'].apply(process_review_apply)

# İşlenmiş verileri kaydet
output_file = 'output_file.csv'
df[['text']].to_csv(output_file, index=False)

print(f"Processed data saved to {output_file}")
