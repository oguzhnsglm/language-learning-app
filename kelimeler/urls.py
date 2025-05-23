from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.anasayfa, name='anasayfa'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('menu/', views.menu, name='menu'),
    path('logout/', views.logout_view, name='logout'),
    path('add-word/', views.add_word, name='add_word'),
    path('quiz/', views.quiz_view, name='quiz'),  # hem ayar hem başlangıç sayfası
    path('quiz-submit/', views.quiz_submit, name='quiz_submit'),
    path('quiz-question/', views.quiz_question, name='quiz_question'),
    path('quiz-result/', views.quiz_result, name='quiz_result'),
    path('analysis/', views.exam_analysis, name='exam_analysis'),
    path('analysis/pdf/', views.exam_analysis_pdf, name='exam_analysis_pdf'),
    path('wordle/', views.wordle_game, name='wordle_game'),
]

# Geliştirme ortamında statik ve medya dosyalarını servis et
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATICFILES_DIRS[0]
    )