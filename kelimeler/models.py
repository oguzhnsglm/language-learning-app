from django.db import models
from datetime import date, timedelta
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=150)

    def __str__(self):
        return self.username

User = get_user_model()

class Word(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ✅ EKLENDİ
    eng_word = models.CharField("İngilizce Kelime", max_length=100, unique=True)
    tur_word = models.CharField("Türkçe Karşılık", max_length=100)
    picture = models.ImageField(upload_to='pictures/', null=True, blank=True)
    audio = models.FileField(upload_to='audios/', null=True, blank=True)
    samples = models.TextField("Örnek Cümleler")  # cümleler | ile ayrılacak

    # Yeni alan: Kelime türü
    WORD_TYPES = [
        ('noun', 'İsim'),
        ('verb', 'Fiil'),
        ('adj', 'Sıfat'),
        ('adv', 'Zarf'),
        ('pron', 'Zamir'),
        ('other', 'Diğer'),
    ]
    word_type = models.CharField(max_length=10, choices=WORD_TYPES, default='other')


    correct_count = models.IntegerField(default=0)
    correct_date = models.DateField(null=True, blank=True)
    next_show_date = models.DateField(null=True, blank=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.eng_word

    def update_correct(self):
        intervals = [1, 7, 30, 90, 180, 365]
        self.correct_count += 1
        self.last_correct_date = date.today()
        if self.correct_count <= len(intervals):
            self.next_show_date = self.last_correct_date + timedelta(days=intervals[self.correct_count - 1])
        else:
            self.next_show_date = None
        self.is_correct = True
        self.save()

    def reset_progress(self):
        self.correct_count = 0
        self.last_correct_date = None
        self.next_show_date = None
        self.is_correct = False
        self.save()

    @classmethod
    def filter(cls):
        today = date.today()
        return cls.objects.filter(
            models.Q(is_correct=False) | models.Q(is_correct=True, next_show_date=today)
        )

class ExamResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_taken = models.DateTimeField(auto_now_add=True)
    total_questions = models.IntegerField()

    # Türlere göre dağılım
    verb_total = models.IntegerField(default=0)
    verb_correct = models.IntegerField(default=0)

    noun_total = models.IntegerField(default=0)
    noun_correct = models.IntegerField(default=0)

    adjective_total = models.IntegerField(default=0)
    adjective_correct = models.IntegerField(default=0)

    adverb_total = models.IntegerField(default=0)
    adverb_correct = models.IntegerField(default=0)

    other_total = models.IntegerField(default=0)
    other_correct = models.IntegerField(default=0)

    total_correct = models.IntegerField()
    total_wrong = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.date_taken.strftime('%Y-%m-%d')} sınavı"
