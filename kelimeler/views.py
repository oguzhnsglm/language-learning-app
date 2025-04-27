from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import RegisterForm
from .models import User, Word, ExamResult
from django.contrib import messages
from django.contrib.sessions.models import Session
import base64, time, os
from django.conf import settings
from django.utils import timezone
import random
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()

def add_word(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "Kullanıcı oturumu bulunamadı.")
            return redirect('login')

        current_user = User.objects.get(id=user_id)

        eng = request.POST.get('eng_word').strip()
        tur = request.POST.get('tur_word').strip()
        word_type = request.POST.get('word_type', 'other')
        samples = request.POST.getlist('samples')
        samples_clean = [s.strip() for s in samples if s.strip()]

        if not eng or not tur or len(samples_clean) == 0:
            messages.error(request, "Tüm alanlar (örnek cümle dahil) doldurulmalı.")
            return redirect('add_word')

        if Word.objects.filter(eng_word__iexact=eng, user=current_user).exists():
            messages.error(request, "Bu kelime zaten eklenmiş.")
            return redirect('add_word')

        pic = request.FILES.get('picture')
        picture_path = pic if pic else None

        audio_blob = request.POST.get('audio_blob')
        audio_file = None
        if audio_blob:
            try:
                header, encoded = audio_blob.split(',', 1)
                audio_data = base64.b64decode(encoded)
                audio_name = f"audio_{int(time.time())}.wav"
                audio_path = os.path.join(settings.MEDIA_ROOT, 'audios', audio_name)
                os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                with open(audio_path, 'wb') as f:
                    f.write(audio_data)
                audio_file = f"audios/{audio_name}"
            except:
                messages.warning(request, "Ses kaydedilemedi.")

        Word.objects.create(
            user=current_user,
            eng_word=eng,
            tur_word=tur,
            picture=picture_path,
            audio=audio_file,
            samples='|'.join(samples_clean),
            word_type=word_type
        )

        messages.success(request, "Kelime başarıyla eklendi!")
        return redirect('add_word')

    return render(request, 'add_word.html')



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Bu kullanıcı adı zaten var.')
            else:
                form.save()
                messages.success(request, 'Kayıt başarılı! Giriş yapabilirsiniz.')
                return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def anasayfa(request):
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            if user.password == password:
                # ✅ Hem username hem user_id kaydediliyor
                request.session['username'] = user.username
                request.session['user_id'] = user.id  # burası eklendi
                messages.success(request, 'Giriş başarılı!')
                return redirect('menu')
            else:
                messages.error(request, 'Şifre hatalı.')
        except User.DoesNotExist:
            messages.error(request, 'Böyle bir kullanıcı bulunamadı.')

    return render(request, 'login.html')

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')

        try:
            user = User.objects.get(username=username)
            user.password = new_password
            user.save()
            messages.success(request, 'Şifre başarıyla güncellendi.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Böyle bir kullanıcı bulunamadı.')

    return render(request, 'forgot_password.html')

def menu(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')
    return render(request, 'menu.html', {'username': username})

def logout_view(request):
    request.session.flush()
    return redirect('login')


from .models import Word  # emin olalım

from datetime import date
from django.db.models import Q
from .models import Word

def quiz_view(request):
    if request.method == 'POST':
        question_limit = int(request.POST.get("question_limit", 10))
        request.session["quiz_question_limit"] = question_limit
        today = date.today()

        # ✅ Oturumdan kullanıcıyı al
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "Oturum bilgisi bulunamadı.")
            return redirect('login')

        # 1️⃣ Öncelik: Doğru bilinen ama tekrar zamanı gelen kelimeler (sadece o kullanıcıya ait)
        priority_words = list(Word.objects.filter(
            user_id=user_id,
            is_correct=True,
            next_show_date__lte=today
        ).order_by('?')[:question_limit])

        # 2️⃣ Eksik kalan sayıyı yanlış bilinenlerden doldur
        needed = question_limit - len(priority_words)
        if needed > 0:
            fallback_words = Word.objects.filter(
                user_id=user_id,
                is_correct=False
            ).order_by('?')[:needed]
            priority_words += list(fallback_words)

        if not priority_words:
            messages.warning(request, "Bu sınav için yeterli uygun kelime bulunamadı.")
            return redirect('menu')

        # ✅ Seçilen kelime ID’lerini session’a yaz
        request.session['quiz_ids'] = [w.id for w in priority_words]
        request.session['quiz_index'] = 0

        return redirect('quiz_question')

    return render(request, 'quiz.html')



def quiz_question(request):
    ids = request.session.get('quiz_ids', [])
    index = request.session.get('quiz_index', 0)

    if index >= len(ids):
        return redirect('quiz_result')

    word_id = ids[index]
    word = Word.objects.get(id=word_id)
    
    return render(request, 'quiz_question.html', {
        'word': word,
        'index': index + 1,
        'total': len(ids)
    })


from datetime import date
from django.shortcuts import redirect
from .models import Word, User

def quiz_submit(request):
    if request.method == 'POST':
        quiz_ids = request.session.get('quiz_ids', [])
        index = request.session.get('quiz_index', 0)

        if index >= len(quiz_ids):
            return redirect('quiz_result')

        word_id = quiz_ids[index]
        word = Word.objects.get(id=word_id)
        user_input = request.POST.get(f"word_{word_id}", "").strip().lower()
        correct_answer = word.tur_word.strip().lower()
        is_correct = (user_input == correct_answer)

        # ✅ Eğer doğruysa word modelinde güncelleme yap
        if is_correct:
            word.update_correct()

        # ✅ Cevapları liste halinde sakla
        answers = request.session.get('quiz_answers', [])

        answers.append({
            'eng_word': word.eng_word,
            'tur_word': word.tur_word,
            'user_input': user_input,
            'is_correct': is_correct
        })

        request.session['quiz_answers'] = answers
        request.session['quiz_index'] = index + 1

        if request.session['quiz_index'] >= len(quiz_ids):
            return redirect('quiz_result')
        else:
            return redirect('quiz_question')


def quiz_result(request):
    results = request.session.get('quiz_answers', [])
    username = request.session.get('username')
    user = User.objects.get(username=username)

    # Genel sayaçlar
    total_questions = len(results)
    total_correct = 0

    verb_total = verb_correct = 0
    noun_total = noun_correct = 0
    adjective_total = adjective_correct = 0
    adverb_total = adverb_correct = 0
    other_total = other_correct = 0

    for item in results:
        is_correct = item['is_correct']
        word_obj = Word.objects.get(eng_word=item['eng_word'])

        word_type = word_obj.word_type

        if is_correct:
            total_correct += 1

        if word_type == 'verb':
            verb_total += 1
            if is_correct:
                verb_correct += 1
        elif word_type == 'noun':
            noun_total += 1
            if is_correct:
                noun_correct += 1
        elif word_type == 'adjective':
            adjective_total += 1
            if is_correct:
                adjective_correct += 1
        elif word_type == 'adverb':
            adverb_total += 1
            if is_correct:
                adverb_correct += 1
        else:
            other_total += 1
            if is_correct:
                other_correct += 1

    total_wrong = total_questions - total_correct

    # ✅ Veritabanına sınav sonucunu kaydet
    ExamResult.objects.create(
        user=user,
        total_questions=total_questions,
        total_correct=total_correct,
        total_wrong=total_wrong,
        verb_total=verb_total,
        verb_correct=verb_correct,
        noun_total=noun_total,
        noun_correct=noun_correct,
        adjective_total=adjective_total,
        adjective_correct=adjective_correct,
        adverb_total=adverb_total,
        adverb_correct=adverb_correct,
        other_total=other_total,
        other_correct=other_correct
    )

    # Session temizliği
    for key in ['quiz_ids', 'quiz_index', 'quiz_answers']:
        request.session.pop(key, None)

    return render(request, 'quiz_result.html', {'results': results})

import matplotlib.pyplot as plt
from io import BytesIO
from django.db.models import Sum
import base64
from django.http import HttpResponse
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from io import BytesIO
import matplotlib.pyplot as plt
from django.db.models import Sum
from .models import ExamResult
import base64

from django.shortcuts import render, redirect
from .models import ExamResult
from django.db.models import Sum
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def exam_analysis(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect('login')

    results = ExamResult.objects.filter(user_id=user_id).order_by('-date_taken')
    totals = results.aggregate(
        total_questions=Sum('total_questions'),
        total_correct=Sum('total_correct'),
        total_wrong=Sum('total_wrong'),
        verb_total=Sum('verb_total'), verb_correct=Sum('verb_correct'),
        noun_total=Sum('noun_total'), noun_correct=Sum('noun_correct'),
        adjective_total=Sum('adjective_total'), adjective_correct=Sum('adjective_correct'),
        adverb_total=Sum('adverb_total'), adverb_correct=Sum('adverb_correct'),
        other_total=Sum('other_total'), other_correct=Sum('other_correct'),
    )

    # Pie chart
    correct = totals.get('total_correct') or 0
    wrong = totals.get('total_wrong') or 0
    pie_chart_base64 = ""
    if correct + wrong > 0:
        fig1, ax1 = plt.subplots(figsize=(4, 4))
        ax1.pie([correct, wrong], labels=["Doğru", "Yanlış"], colors=["#10B981", "#EF4444"],
                autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        buffer1 = BytesIO()
        plt.savefig(buffer1, format='png', bbox_inches='tight')
        plt.close(fig1)
        pie_chart_base64 = base64.b64encode(buffer1.getvalue()).decode('utf-8')

    # Bar chart (türlere göre)
    labels = ["Verb", "Noun", "Adjective", "Adverb", "Other"]
    corrects = [totals.get(f"{l.lower()}_correct") or 0 for l in labels]
    totals_list = [totals.get(f"{l.lower()}_total") or 0 for l in labels]
    percentages = [round((c / t) * 100, 1) if t > 0 else 0 for c, t in zip(corrects, totals_list)]

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    bars = ax2.bar(labels, percentages, color=["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#6B7280"])
    for bar, pct in zip(bars, percentages):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2, f"{pct}%", ha='center', fontsize=12)
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("Başarı %")
    ax2.set_title("Kelime Türlerine Göre Başarı")
    ax2.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout()
    buffer2 = BytesIO()
    plt.savefig(buffer2, format='png')
    plt.close(fig2)
    bar_chart_base64 = base64.b64encode(buffer2.getvalue()).decode('utf-8')

    return render(request, 'exam_analysis.html', {
        'results': results,
        'totals': totals,
        'pie_chart_base64': pie_chart_base64,
        'bar_chart_base64': bar_chart_base64
    })

from django.template.loader import get_template
from django.http import HttpResponse
from django.shortcuts import redirect
from django.db.models import Sum
from xhtml2pdf import pisa
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from PIL import Image
from .models import ExamResult


def exam_analysis_pdf(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect('login')

    results = ExamResult.objects.filter(user_id=user_id).order_by('-date_taken')
    totals = results.aggregate(
        total_questions=Sum('total_questions'),
        total_correct=Sum('total_correct'),
        total_wrong=Sum('total_wrong'),
        verb_total=Sum('verb_total'), verb_correct=Sum('verb_correct'),
        noun_total=Sum('noun_total'), noun_correct=Sum('noun_correct'),
        adjective_total=Sum('adjective_total'), adjective_correct=Sum('adjective_correct'),
        adverb_total=Sum('adverb_total'), adverb_correct=Sum('adverb_correct'),
        other_total=Sum('other_total'), other_correct=Sum('other_correct'),
    )

    # 📊 Pie Chart
    correct = totals.get("total_correct") or 0
    wrong = totals.get("total_wrong") or 0
    pie_chart_base64 = ""
    if correct + wrong > 0:
        fig, ax = plt.subplots(figsize=(3.5, 3.5))
        ax.pie([correct, wrong], labels=["Doğru", "Yanlış"], colors=["#10B981", "#EF4444"], autopct='%1.1f%%', startangle=90)
        ax.axis("equal")
        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        plt.close(fig)
        pie_chart_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # 📈 Bar Chart
    labels = ["Verb", "Noun", "Adjective", "Adverb", "Other"]
    corrects = [totals.get(f"{l.lower()}_correct") or 0 for l in labels]
    totals_list = [totals.get(f"{l.lower()}_total") or 0 for l in labels]
    percentages = [round((c / t) * 100, 1) if t > 0 else 0 for c, t in zip(corrects, totals_list)]

    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    bars = ax.bar(labels, percentages, color=["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#6B7280"])
    for bar, pct in zip(bars, percentages):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{pct}%", ha="center", fontsize=9)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Başarı %")
    ax.set_title("Kelime Türlerine Göre Başarı", fontsize=11, pad=20)
    plt.tight_layout()
    buffer2 = BytesIO()
    plt.savefig(buffer2, format="png")
    plt.close(fig)
    bar_chart_base64 = base64.b64encode(buffer2.getvalue()).decode("utf-8")

    # HTML render
    template = get_template("exam_analysis_pdf.html")
    html = template.render({
        "results": results,
        "totals": totals,
        "pie_chart_base64": pie_chart_base64,
        "bar_chart_base64": bar_chart_base64
    })

    # PDF oluştur
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="analiz_raporu.pdf"'
    pisa.CreatePDF(BytesIO(html.encode("utf-8")), dest=response, encoding="utf-8")
    return response

import random
from django.shortcuts import render, redirect
from .models import Word

import random
from django.shortcuts import render, redirect
from .models import Word

def wordle_game(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    # Kullanıcının doğru bildiği kelimeleri çek
    words = list(
        Word.objects.filter(user_id=user_id, is_correct=True)
        .values_list("eng_word", flat=True)
    )

    if not words:
        return render(request, "wordle_game.html", {"error": "Henüz yeterli doğru bilinen kelimeniz yok."})

    # Her zaman rastgele bir kelime seç (her sayfa yenilendiğinde yeni kelime)
    target_word = random.choice(words).upper()

    return render(request, "wordle_game.html", {"word": target_word})
