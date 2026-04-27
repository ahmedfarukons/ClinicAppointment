"""
Klinik Bilgi Tabanı — Kapsamlı Türkçe Dataset
==============================================
4 ana bölüm için yüzlerce Türkçe şikayet, semptom ve soru içerir.
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# BÖLÜM BAZINDA ÖRNEK SORULAR / ŞİKAYETLER
# ─────────────────────────────────────────────────────────────────────────────

DEPARTMENT_QUESTIONS: dict[str, list[str]] = {

    # ════════════════════════════════════════════════════════════════
    "Internal Medicine": [
        # Genel & sistemik
        "sürekli yorgun hissediyorum", "halsizlik var", "bitkinlik yaşıyorum",
        "enerjim yok", "sürekli uyku hali var", "kendimi kötü hissediyorum",
        "vücudumda kırgınlık var", "genel sağlık durumum bozuldu",
        "sık sık hasta oluyorum", "bağışıklığım düştü",
        # Ateş & enfeksiyon
        "ateşim var", "titreme ile birlikte ateş", "gece ateşi çıkıyor",
        "grip oldum", "soğuk algınlığı geçiriyorum", "nezle oldum",
        "gece terlemesi yaşıyorum", "sürekli terliyorum",
        "enfeksiyon olabilir mi", "mikrop kaptım galiba",
        # Kilo & iştah
        "sebepsiz kilo verdim", "kilo kaybediyorum", "iştahım yok",
        "yiyemiyorum", "sebepsiz kilo aldım", "kilo alıyorum duramıyorum",
        "şişmanlıyorum", "zayıflıyorum", "iştahsızlık yaşıyorum",
        # Baş ağrısı & baş dönmesi
        "baş ağrım var", "migren var", "baş dönmesi yaşıyorum",
        "başım dönüyor", "sersemlik hissediyorum", "dengesizlik var",
        "kafam ağrıyor", "yoğun baş ağrısı",
        # Mide & sindirim
        "mide ağrım var", "mide yanması yaşıyorum", "reflü var",
        "mide bulantısı var", "kusma var", "hazımsızlık yaşıyorum",
        "ishal var", "kabızlık var", "bağırsak sorunum var",
        "karın ağrısı var", "şişkinlik hissediyorum", "gaz sorunu var",
        "midemi bulanıyor", "mide krampı var",
        # Diyabet & şeker
        "şekerim yüksek", "diyabetim var", "insülin kullanıyorum",
        "açlık şekerime baktırmak istiyorum", "şeker problemi yaşıyorum",
        "hipoglisemi yaşıyorum", "kan şekerim düşüyor",
        # Tansiyon & dolaşım
        "tansiyonum yüksek", "yüksek tansiyon problemi var",
        "tansiyonum düşüyor", "tansiyon kontrolüne gitmek istiyorum",
        # Tiroid
        "tiroid sorunum var", "guatr var", "tiroid kontrolü yaptırmak istiyorum",
        "hipotiroid tedavisi görüyorum", "hipertiroid olabilirim",
        "boynum şişti", "boyunda kitle var",
        # Böbrek
        "böbrek ağrım var", "böbrek taşı olabilir mi", "idrar yaparken ağrı var",
        "sık idrara çıkıyorum", "az idrar yapıyorum", "idrar rengim değişti",
        # Karaciğer
        "karaciğer kontrolü yaptırmak istiyorum", "sarılık var",
        "karaciğerim iyi mi bilmiyorum", "hepatit kontrolü",
        # Solunum
        "öksürük var sürekli", "balgam var", "bronşit oldu",
        "zatürre geçirdim", "nefes almakta güçlük", "astım var",
        # Eklem & kas ağrısı
        "vücudumda ağrı var", "kas ağrısı yaşıyorum", "romatizma var",
        "eklem ağrım var", "fibromiyalji şüphesi", "sırt ağrım var",
        "bel ağrısı geçmiyor", "boyun ağrım var",
        # Vitamin & mineral
        "vitamin eksikliğim olabilir mi", "demir eksikliğim var",
        "b12 eksikliği taşıyorum", "d vitamini eksikliğim var",
        "anemi var kansızlık", "kansızlıktan dolayı baş dönmesi yaşıyorum",
        # Check-up & genel kontrol
        "genel check-up yaptırmak istiyorum", "iç hastalıkları kontrolü",
        "kan değerlerime baktırmak istiyorum", "dahiliyeye gitmem gerekiyor",
        "genel sağlık kontrolü", "hangi bölüme gitmeliyim genel şikayetlerim için",
        # Uyku
        "uyuyamıyorum", "uykusuzluk çekiyorum", "insomnia var",
        "gece uyandırıyor dalınamıyorum",
        # Diğer
        "sürekli susuzluk hissi", "çok su içiyorum", "ağız kuruluğu var",
        "terleme problemi var", "üşüme hissediyorum",
        "el ve ayaklarım soğuyor", "karıncalanma var",
    ],

    # ════════════════════════════════════════════════════════════════
    "Cardiology": [
        # Çarpıntı & ritim
        "kalbim hızlı atıyor", "kalp çarpıntısı var", "çarpıntı yaşıyorum",
        "nabzım çok hızlı", "nabzım yavaş", "nabzım düzensiz",
        "kalp ritmi bozuk", "atriyel fibrilasyon var", "aritmim var",
        "kalbim atlıyor", "kalp atlaması hissediyorum",
        # Göğüs ağrısı & baskı
        "göğsümde ağrı var", "göğüs ağrısı geçmiyor", "göğsümde baskı hissi",
        "göğsümde sıkışma var", "kalbimde batma hissi",
        "göğsümde yanma var", "sol göğsüm ağrıyor",
        "sol tarafımda ağrı var", "sol koluma vuran ağrı",
        "omzuma vuran göğüs ağrısı", "çeneme vuran ağrı",
        # Nefes darlığı
        "nefes darlığı yaşıyorum", "nefes alamıyorum", "nefes almakta zorlanıyorum",
        "merdiven çıkınca nefes kesiliyor", "yürürken nefes daralıyor",
        "yatar pozisyonda nefes sıkışıyor", "gece nefes darlığı",
        "çabuk nefes nefese kalıyorum",
        # Tansiyon
        "tansiyonum çok yüksek", "hipertansiyon var", "tansiyonum 160",
        "tansiyon 180 çıktı", "tansiyon düşüklüğü var", "hipotansiyon var",
        "tansiyonum çok değişiyor", "ilaçla tansiyon kontrol altında değil",
        # Ödem & şişme
        "ayaklarım şişiyor", "bacaklarım şişiyor", "ödem var",
        "vücudumda su toplanıyor", "sabah yüzüm şişiyor",
        # Bayılma & senkop
        "bayılıyorum", "bayılma atakları geçiriyorum", "ani bayılma",
        "bayılacak gibi oluyorum", "senkop geçirdim",
        "ani baş dönmesi ile düşüyorum",
        # Kalp yetmezliği belirtileri
        "kalp yetmezliği şüphem var", "kalp rahatsızlığım var",
        "önceden kalp ameliyatı geçirdim kontrol istiyorum",
        "stent takıldı kontrol gerekiyor",
        "bypass ameliyatı sonrası kontrol",
        # Kolesterol & damar
        "kolesterolüm yüksek", "trigliserit yüksekliği",
        "damar sertliği şüphesi", "kalp damarlarım tıkalı olabilir",
        "kardiyovasküler risk hesabı yaptırmak istiyorum",
        # Tetkik & tarama
        "ekg çektirmek istiyorum", "ekokardiyografi yaptırmak istiyorum",
        "kalp ultrasonu", "holter takmak istiyorum", "efor testi",
        "kalp kontrolü yaptırmak istiyorum",
        "kalp krizi riski değerlendirmesi istiyorum",
        # Egzersiz & aktivite
        "egzersiz yaparken kalbim zorlanıyor", "sporda kalp çarpıntısı",
        "spor yaparken göğüs ağrısı", "koşunca yoruluyorum",
        # Diğer
        "kardiyoloji randevusu almak istiyorum",
        "kalp sağlığımı kontrol ettirmek istiyorum",
        "kalp hastalığı aile geçmişim var",
        "kalp için kan sulandırıcı kullanıyorum",
        "pacemaker var kontrol etmek istiyorum",
        "kalp kapak sorunu var",
    ],

    # ════════════════════════════════════════════════════════════════
    "Dermatology": [
        # Akne & sivilce
        "sivilce çıktı", "akne problemi var", "kistik akne var",
        "yüzümde sivilce var", "sırtımda sivilce var",
        "göğsümde sivilce var", "alnımda sivilce çıktı",
        # Kızarıklık & inflamasyon
        "cildimde kızarıklık var", "ciltte yanma ve kızarıklık",
        "yüzümde kızarıklık", "yanaklarım kırmızı",
        "rosacea olabilir miyim", "kuperos var",
        # Kaşıntı
        "kaşıntı yaşıyorum", "vücudum kaşınıyor", "gece kaşıntısı",
        "cildim kaşınıyor durmuyor", "alerjik kaşıntı",
        "iç çamaşırı kaşındırıyor", "kafa derisi kaşınıyor",
        # Döküntü & isilik
        "döküntü çıktı", "vücudumda döküntü var", "kızarık döküntü",
        "isilik var", "ürtiker çıktı", "kurdeşen var",
        "ciltte kabarcıklar oluştu", "su toplayan döküntü",
        "alerjik döküntü geçirdim", "ilaç döküntüsü oldu",
        # Egzama & psoriasis
        "egzama var", "egzema dermatiti", "atopik dermatit",
        "kontakt dermatit", "sedef hastalığı var", "psoriasis var",
        "pullanma var cildimde", "sedef lekesi genişliyor",
        "sedef krizi geçiriyorum",
        # Alerji & reaksiyon
        "alerjik reaksiyon geçirdim", "alerjim var ciltsel",
        "besin alerjisi cilde yansıdı", "lateks alerjisi",
        "güneşe alerjim var", "güneş çarptı ciltten reaksiyon",
        "böcek ısırığı reaksiyonu", "temas alerjisi",
        # Kuruluk & soyulma
        "cildim çok kuru", "ciltte pullanma ve kuruluk",
        "ihtiyoz var cildim", "cildim çatlıyor kuruyor",
        "dudaklarım sürekli çatlıyor", "topuklarım çatlıyor",
        "el içlerim kuruyor çatlıyor", "vücudum soyuluyor",
        # Leke & pigmentasyon
        "cildimde lekeler var", "güneş lekeleri",
        "melazma var yüzümde", "hiperpigmentasyon",
        "beyaz lekeler oluştu", "vitiligo olabilir mi",
        "doğum lekesi var kontrol ettirmek istiyorum",
        "cildimde renk değişimi var",
        # Saç sorunları
        "saç dökülmesi var", "yoğun saç dökülmesi",
        "alopesi var", "saç bölgeleri açıldı",
        "saçlarım inceliyor", "beyaz saç erken çıkıyor",
        "kepek problemi var", "yağlı kafa derisi",
        "kaşıntılı kafa derisi", "saç derisinde döküntü",
        "folikülit var saç köklerinde",
        # Tırnak sorunları
        "tırnaklarım bozuk", "tırnakta mantar var",
        "tırnak rengi değişti", "tırnak kırılıyor döküyor",
        "tırnak içine gömüldü", "tırnak kalınlaştı",
        "tırnakta leke var", "tırnak çizgilendi",
        # Mantar & enfeksiyon
        "cildimde mantar var", "cilt mantarı tedavisi gerekiyor",
        "kasıkta mantar var", "ayak parmak arası mantar",
        "yüzük mantarı var", "koku var enfeksiyon olabilir",
        "impetigo oldu", "cilt enfeksiyonu geçirdim",
        "herpes labialis var dudağımda",
        "zona geçiriyorum", "su çiçeği izleri var",
        # Ben & mole & lezyonlar
        "benlerimi kontrol ettirmek istiyorum",
        "benim büyüdüğünü fark ettim", "bende renk değişimi",
        "şüpheli ben var", "cilt kanseri riski için kontrol",
        "yeni lezyon oluştu cildimde",
        "cildimde kabuk olmayan yara var",
        # Yara & iz
        "yara izi var tedavi etmek istiyorum",
        "ameliyat izi düzeltme", "akne izi var",
        "keloid oluştu", "strach mark var gerilme çizgileri",
        # Bölge özel
        "yüzümde şişlik var", "gözaltlarım şişiyor",
        "dudaklarım şişiyor anjioödem",
        "boyunda cilt altı kitle var",
        "koltuk altında şişlik var",
        "kasıkta sivciller var",
        # Diğer
        "cilt bakımı için dermatolog görmek istiyorum",
        "dermatoloji kontrolü yaptırmak istiyorum",
        "botox veya dolgu için dermatolog",
        "lazer epilasyon kontrolü",
    ],

    # ════════════════════════════════════════════════════════════════
    "Laboratory": [
        # Kan tahlili genel
        "kan tahlili yaptırmak istiyorum", "tam kan sayımı yaptırmak istiyorum",
        "hemogram yaptırmak istiyorum", "kan değerlerime baktırmak istiyorum",
        "CBC testi istiyorum", "kan sonuçlarıma bakmak istiyorum",
        # Şeker & diyabet testleri
        "şeker testi yaptırmak istiyorum", "açlık kan şekeri ölçtürmek istiyorum",
        "HbA1c testi", "glukoz tolerans testi", "insülin direnci testi",
        "diyabet testi yaptırmak istiyorum",
        # Kolesterol & lipid paneli
        "kolesterol testi yaptırmak istiyorum", "LDL HDL kolesterol",
        "trigliserit testi", "lipid paneli", "kalp riskimi ölçmek istiyorum",
        # Karaciğer testleri
        "karaciğer testleri yaptırmak istiyorum", "ALT AST baktırmak istiyorum",
        "hepatit B testi", "hepatit C testi", "hepatit kontrolü",
        "karaciğer enzimleri yüksek dendi",
        # Böbrek testleri
        "böbrek testleri yaptırmak istiyorum", "kreatinin baktırmak istiyorum",
        "üre testi", "idrar tahlili yaptırmak istiyorum",
        "idrar kültürü gerekiyor", "böbrek yetmezliği kontrolü",
        # Tiroid testleri
        "tiroid testi yaptırmak istiyorum", "TSH testi", "T3 T4 baktırmak istiyorum",
        "tiroid ultrasonu gerekiyor mu",
        # Hormon testleri
        "hormon testi yaptırmak istiyorum", "östrojen testi",
        "progesteron testi", "testosteron testi", "FSH LH testi",
        "kortizol testi", "prolaktin baktırmak istiyorum",
        "AMH testi", "menopoz testi yaptırmak istiyorum",
        # Vitamin & mineral
        "vitamin testi yaptırmak istiyorum", "D vitamini testi",
        "B12 vitamini testi", "demir eksikliği testi",
        "ferritin baktırmak istiyorum", "folat testi",
        "çinko magnezyum testi", "kalsiyum baktırmak istiyorum",
        # Enfeksiyon & mikrobiyoloji
        "PCR testi yaptırmak istiyorum", "koronavirüs testi",
        "strep testi", "boğaz kültürü", "idrar kültürü",
        "kan kültürü gerekiyor", "apse kültürü",
        "cinsel yolla bulaşan enfeksiyon testi", "HIV testi",
        "sifiliz testi", "klamidya testi",
        # Alerji testleri
        "alerji testi yaptırmak istiyorum", "besin alerjisi testi",
        "solunum alerjisi testi", "İgE testi",
        # Kan grubu & bağışıklık
        "kan grubumu öğrenmek istiyorum", "rh faktörüm ne",
        "bağışıklık testi yaptırmak istiyorum", "antikor testi",
        "otoimmün hastalık paneli",
        # İnflamasyon testleri
        "CRP testi yaptırmak istiyorum", "sedimantasyon testi",
        "inflamasyon belirteçleri", "romatizma testi",
        "romatoid faktör testi",
        # Kanser tarama
        "PSA testi erkek kanser tarama", "CA-125 testi",
        "CEA testi kanser belirteci", "AFP testi",
        "tümör belirteci testi yaptırmak istiyorum",
        # Koagülasyon & pıhtılaşma
        "pıhtılaşma testi", "INR PTT testi", "D-dimer testi",
        "pıhtılaşma bozukluğu kontrolü",
        # Sonuç & yorumlama
        "tetkik sonuçlarımı yorumlatmak istiyorum", "testi sonuçları ne anlama geliyor",
        "kan değerlerim normal mi", "hangi testlerin anormal çıktığını anlamak istiyorum",
        "sonuçlarıma baktırmak istiyorum", "test sonuçlarını açıklayın",
        # Pratik & lojistik
        "aç karnına mı gitmem gerekiyor test için",
        "kaç saat aç kalmalıyım", "hızlı test yaptırabilir miyim",
        "hızlı sonuç veren test var mı", "sonuçlar ne zaman çıkar",
        "laboratuvar randevusu almak istiyorum", "labaratuvarınıza nasıl gelirim",
        "evde test kiti almanın yolu var mı",
        "online sonuç görüntüleme nasıl yapılıyor",
        "check-up paket testleri nelerdir",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# ANAHTAR KELİME HARİTASI (token → department)
# ─────────────────────────────────────────────────────────────────────────────

KEYWORD_MAP: dict[str, str] = {
    # ── Internal Medicine ──────────────────────────────────────────
    "yorgun": "Internal Medicine",
    "halsiz": "Internal Medicine",
    "bitkin": "Internal Medicine",
    "uyku hali": "Internal Medicine",
    "kırgınlık": "Internal Medicine",
    "iştahsız": "Internal Medicine",
    "kilo kaybetti": "Internal Medicine",
    "kilo aldım": "Internal Medicine",
    "kilo verdim": "Internal Medicine",
    "bağışıklık": "Internal Medicine",
    "check-up": "Internal Medicine",
    "checkup": "Internal Medicine",
    "genel kontrol": "Internal Medicine",
    "iç hastalık": "Internal Medicine",
    "dahiliye": "Internal Medicine",
    "susuzluk": "Internal Medicine",
    "gece terlemesi": "Internal Medicine",
    "ateş": "Internal Medicine",
    "vitamin eksikliği": "Internal Medicine",
    "tiroid": "Internal Medicine",
    "guatr": "Internal Medicine",
    "diyabet": "Internal Medicine",
    "şeker hastalığı": "Internal Medicine",
    "insülin": "Internal Medicine",
    "hipoglisemi": "Internal Medicine",
    "kan şekeri": "Internal Medicine",
    "demir eksikliği": "Internal Medicine",
    "b12 eksikliği": "Internal Medicine",
    "d vitamini": "Internal Medicine",
    "anemi": "Internal Medicine",
    "kansızlık": "Internal Medicine",
    "mide yanması": "Internal Medicine",
    "reflü": "Internal Medicine",
    "hazımsızlık": "Internal Medicine",
    "ishal": "Internal Medicine",
    "kabızlık": "Internal Medicine",
    "karın ağrısı": "Internal Medicine",
    "böbrek taşı": "Internal Medicine",
    "sarılık": "Internal Medicine",
    "hepatit": "Internal Medicine",
    "zatürre": "Internal Medicine",
    "bronşit": "Internal Medicine",
    "astım": "Internal Medicine",
    "romatizma": "Internal Medicine",
    "fibromiyalji": "Internal Medicine",
    "uyuyamıyorum": "Internal Medicine",
    "uykusuzluk": "Internal Medicine",
    "insomnia": "Internal Medicine",
    "grip": "Internal Medicine",
    "soğuk algınlığı": "Internal Medicine",
    "nezle": "Internal Medicine",
    "enfeksiyon": "Internal Medicine",
    "migren": "Internal Medicine",
    "baş ağrısı": "Internal Medicine",
    "baş dönmesi": "Internal Medicine",
    "sersemlik": "Internal Medicine",
    "karıncalanma": "Internal Medicine",
    "kas ağrısı": "Internal Medicine",
    "sırt ağrısı": "Internal Medicine",
    "bel ağrısı": "Internal Medicine",
    "boyun ağrısı": "Internal Medicine",

    # ── Cardiology ─────────────────────────────────────────────────
    "çarpıntı": "Cardiology",
    "kalp çarpıntısı": "Cardiology",
    "kalp": "Cardiology",
    "nabız": "Cardiology",
    "ritim bozukluğu": "Cardiology",
    "aritmi": "Cardiology",
    "atriyal fibrilasyon": "Cardiology",
    "göğüs ağrısı": "Cardiology",
    "göğüs baskısı": "Cardiology",
    "göğüs sıkışması": "Cardiology",
    "sol kol ağrısı": "Cardiology",
    "tansiyon": "Cardiology",
    "hipertansiyon": "Cardiology",
    "hipotansiyon": "Cardiology",
    "ekg": "Cardiology",
    "elektrokardiyografi": "Cardiology",
    "ekokardiyografi": "Cardiology",
    "holter": "Cardiology",
    "efor testi": "Cardiology",
    "kalp yetmezliği": "Cardiology",
    "kalp krizi": "Cardiology",
    "infarktüs": "Cardiology",
    "anjina": "Cardiology",
    "stent": "Cardiology",
    "bypass": "Cardiology",
    "pacemaker": "Cardiology",
    "kapak": "Cardiology",
    "kardiyoloji": "Cardiology",
    "damar sertliği": "Cardiology",
    "ateroskleroz": "Cardiology",
    "ödem": "Cardiology",
    "ayak şişmesi": "Cardiology",
    "bacak şişmesi": "Cardiology",
    "bayılma": "Cardiology",
    "senkop": "Cardiology",
    "nefes darlığı": "Cardiology",
    "nefes alamıyorum": "Cardiology",
    "kolesterol": "Cardiology",
    "trigliserit": "Cardiology",

    # ── Dermatology ────────────────────────────────────────────────
    "sivilce": "Dermatology",
    "akne": "Dermatology",
    "kızarıklık": "Dermatology",
    "kaşıntı": "Dermatology",
    "döküntü": "Dermatology",
    "egzama": "Dermatology",
    "egzema": "Dermatology",
    "atopik": "Dermatology",
    "dermatit": "Dermatology",
    "sedef": "Dermatology",
    "psoriasis": "Dermatology",
    "kurdeşen": "Dermatology",
    "ürtiker": "Dermatology",
    "cilt": "Dermatology",
    "deri": "Dermatology",
    "saç dökülmesi": "Dermatology",
    "alopesi": "Dermatology",
    "kepek": "Dermatology",
    "leke": "Dermatology",
    "melazma": "Dermatology",
    "vitiligo": "Dermatology",
    "hiperpigmentasyon": "Dermatology",
    "güneş lekesi": "Dermatology",
    "ben": "Dermatology",
    "mole": "Dermatology",
    "cilt kanseri": "Dermatology",
    "keloid": "Dermatology",
    "yara izi": "Dermatology",
    "tırnak": "Dermatology",
    "tırnak mantarı": "Dermatology",
    "cilt mantarı": "Dermatology",
    "mantar": "Dermatology",
    "rosacea": "Dermatology",
    "zona": "Dermatology",
    "herpes": "Dermatology",
    "isilik": "Dermatology",
    "kabarcık": "Dermatology",
    "kuruluk": "Dermatology",
    "pullanma": "Dermatology",
    "soyulma": "Dermatology",
    "dermatoloji": "Dermatology",
    "dermatolog": "Dermatology",
    "anjioödem": "Dermatology",
    "folikülit": "Dermatology",
    "impetigo": "Dermatology",
    "alerji cilt": "Dermatology",

    # ── Laboratory ─────────────────────────────────────────────────
    "tahlil": "Laboratory",
    "laboratuvar": "Laboratory",
    "laborotuvar": "Laboratory",
    "lab ": "Laboratory",
    "kan testi": "Laboratory",
    "kan değerleri": "Laboratory",
    "hemogram": "Laboratory",
    "tam kan": "Laboratory",
    "şeker testi": "Laboratory",
    "glukoz": "Laboratory",
    "hba1c": "Laboratory",
    "lipid paneli": "Laboratory",
    "alt ast": "Laboratory",
    "karaciğer enzimi": "Laboratory",
    "kreatinin": "Laboratory",
    "idrar tahlili": "Laboratory",
    "idrar testi": "Laboratory",
    "idrar kültürü": "Laboratory",
    "tsh": "Laboratory",
    "t3 t4": "Laboratory",
    "hormon testi": "Laboratory",
    "östrojen": "Laboratory",
    "testosteron": "Laboratory",
    "fsH lh": "Laboratory",
    "prolaktin": "Laboratory",
    "kortizol": "Laboratory",
    "pcr testi": "Laboratory",
    "kültür testi": "Laboratory",
    "alerji testi": "Laboratory",
    "ige testi": "Laboratory",
    "crp": "Laboratory",
    "sedimantasyon": "Laboratory",
    "romatoid faktör": "Laboratory",
    "psa testi": "Laboratory",
    "tümör belirteci": "Laboratory",
    "d-dimer": "Laboratory",
    "inr": "Laboratory",
    "kan grubu": "Laboratory",
    "test sonucu": "Laboratory",
    "tahlil sonucu": "Laboratory",
    "tetkik sonucu": "Laboratory",
    "ferritin": "Laboratory",
    "folat": "Laboratory",
    "çinko": "Laboratory",
    "magnezyum": "Laboratory",
    "kalsiyum": "Laboratory",
    "vitamin testi": "Laboratory",
    "hiv testi": "Laboratory",
    "hepatit testi": "Laboratory",
    "kan grubumu": "Laboratory",
}


# ─────────────────────────────────────────────────────────────────────────────
# LLM İÇİN ZENGİN BAĞLAM
# ─────────────────────────────────────────────────────────────────────────────

TRIAGE_CONTEXT = """
Klinik bölüm triaj kılavuzu. Kullanıcının şikayetine en uygun bölümü belirle:

## Internal Medicine (Dahiliye)
Yorgunluk, halsizlik, bitkinlik, düşük enerji, genel check-up, iştahsızlık,
sebepsiz kilo değişimi, bağışıklık sorunları, ateş, gece terlemesi, susuzluk,
vitamin/mineral eksikliğı, diyabet/şeker kontrolü, tiroid/guatr sorunları,
mide–bağırsak problemleri (reflü, mide ağrısı, ishal, kabızlık), böbrek sorunları,
karaciğer kontrolü, solunum enfeksiyonları (grip, bronşit, zatürre),
genel eklem ve kas ağrıları, romatizma, fibromiyalji, anemi/kansızlık,
uyku sorunları, sık hastalanma, genel sistemik şikayetler.

## Cardiology (Kardiyoloji)
Kalp çarpıntısı, hızlı/yavaş/düzensiz nabız, aritmi, atriyal fibrilasyon,
göğüs ağrısı/baskı/sıkışma, sol kola vuran ağrı, nefes darlığı,
egzersizde yorulma/nefes kesme, tansiyon yüksekliği/düşüklüğü,
ayak–bacak ödemi, bayılma atakları, EKG/ekokardiyografi/holter isteği,
kalp krizi riski, stent/bypass sonrası kontrol, kapak sorunları, pacemaker.

## Dermatology (Dermatoloji)
Sivilce/akne, yüz/sırt döküntüleri, cilt kızarıklığı, kaşıntı, kurdeşen/ürtiker,
egzama/atopik dermatit, kontakt dermatit, sedef/psoriasis, rosacea, vitiligo,
melazma/güneş lekeleri, hiperpigmentasyon, saç dökülmesi/alopesi, kepek,
tırnak mantarı/bozukluğu, cilt mantarı, herpes/zona, ben/mole kontrolü,
cilt kanseri riski, yara izi/keloid, akne izleri, anjioödem, folikülit.

## Laboratory (Laboratuvar)
Kan tahlili, hemogram/tam kan sayımı, açlık kan şekeri, HbA1c,
kolesterol/lipid paneli, karaciğer enzimleri (ALT/AST), böbrek testleri (kreatinin/üre),
idrar tahlili/kültürü, tiroid testleri (TSH/T3/T4), hormon testleri,
vitamin/mineral testleri (B12/D/demir/ferritin), PCR/kültür testleri,
alerji testleri, CRP/sedimantasyon, kan grubu, tümör belirteçleri,
koagülasyon/pıhtılaşma testleri, sonuç yorumlama, check-up paketleri.
"""
