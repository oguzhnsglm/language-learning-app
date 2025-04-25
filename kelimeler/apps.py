from django.apps import AppConfig

class KelimelerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kelimeler'  # 👈 bu çok önemli, küçük harf ve birebir klasörle aynı olmalı
    