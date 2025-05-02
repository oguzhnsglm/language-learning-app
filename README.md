# 🧠 Language Learning App — Kelime Ezberleme & Wordle Tabanlı Öğrenme Sistemi

Bu Django projesi, kullanıcıların İngilizce kelimeleri **örnek cümle + görsel + ses** desteğiyle öğrenmesini sağlar. İçinde sınav (quiz) modu, ayrıntılı analiz & PDF çıktısı ve Wordle‑benzeri bulmaca mevcuttur.

---

## 🎯 Amaç  
- Görsel / işitsel öğelerle kelime ezberini kolaylaştırmak  
- Öğrenme sürecini kaydedip istatistiklemek  
- Sınavlarla beceriyi ölçmek, Wordle oyunuyla pekiştirmek

---

## 🚀 Özellikler  
- ✅ Kullanıcı kayıt / giriş  
- 📤 Kelime ekleme (resim, ses, örnek cümle)  
- 🎯 Quiz modülü, doğru/yanlış takibi  
- 📈 Tür bazlı istatistik ve başarı grafikleri  
- 📄 PDF raporu (xhtml2pdf)  
- 🧩 Wordle oyunu (`is_correct=True` kelimelerle)  
- 🔐 Ortam değişkeniyle SECRET_KEY yönetimi  

---

## 🧩 Teknolojiler  
`Python 3.9+`, `Django 4.2`, `xhtml2pdf`, `matplotlib`, `Pillow`, `SQLite3`, Vanilla JS + CSS

---

## ⚙️ Kurulum  
```bash
git clone https://github.com/kullanici-adi/language-learning-app.git
cd language-learning-app
python -m venv venv            # isteğe bağlı sanal ortam
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

```
---

## 🔐 Ortam Değişkenleri

export DJANGO_SECRET_KEY=my-super-secret-key
export DJANGO_DEBUG=True
export DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
python manage.py runserver

---


## 🛠 Geliştirici Talimatları

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

---

## 🧪 Özelliklerin Kullanımı
1. Kelime Ekleme
  Giriş yaptıktan sonra kelime ekleyebilir,

  Kelimeye örnek cümle, ses ve resim ekleyebilirsiniz.

2. Quiz Modülü
  Daha önce öğrenilen kelimelerden sınav oluşturulur.

  Her sınav sonucunda doğru/yanlış analizi sunulur.

3. Analiz Sayfası
  Genel başarı tablosu

  Kelime türlerine göre (verb, noun, vb.) başarı yüzdesi

  PDF olarak çıktısı alınabilir

4. PDF Raporlama
  Analiz sayfasından 📄 PDF Olarak İndir butonu ile kullanıcıya özel analiz raporu alınabilir.

  Pie chart ve bar chart görselleri dahil olur.

5. Wordle Modülü
  Wordle Bulmaca oyununda yalnızca kullanıcının doğru bildiği kelimeler kullanılır.

  Her seferinde rastgele kelime seçilir.

  Harf uzunluğu sınırlı değildir (dinamik yapıdadır).

  Renkli geri bildirimlerle harf tahmini yapılır.

---

## 📁 Proje Yapısı

language-learning-app/
├─ kelimeler/          # Django app
│  ├─ models.py
│  ├─ views.py
│  └─ templates/
├─ ezberleme/          # Proje ayarları
│  └─ settings.py
├─ media/              # Yüklenen dosyalar
├─ static/             # CSS / JS
├─ requirements.txt
└─ README.md

---

## 🛡 Güvenlik
SECRET_KEY kod dışında, .env veya ortam değişkeniyle tutulur.

Production’da DEBUG=False + güvenli HOST ayarları önerilir.

---
