from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import login, get_user_model
from .forms import EmailForm
from .models import CustomUser, Test
from allauth.account.views import LoginView, PasswordResetView
from django.contrib import messages
from allauth.account.models import EmailAddress
from django.core.paginator import Paginator


# главная страница со списком тестов и пагинацией
@login_required
def index(request):
    tests = Test.objects.all()
    paginator = Paginator(tests, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'test/index.html', {'page_obj': page_obj})


# тесты, вопросы, результаты
@login_required
def test_view(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = test.questions.all()

    if request.method == 'POST':
        current_question_id = int(request.POST.get('current_question_id', 0))
        selected_answer_ids = list(map(int, request.POST.getlist('answers')))
        if not selected_answer_ids:
            return render(request, 'test/question.html', {
                'test': test,
                'question': questions[current_question_id],
                'answers': questions[current_question_id].answers.all(),
                'current_question_index': current_question_id,
                'error': 'Пожалуйста, выберите хотя бы один ответ перед переходом к следующему вопросу.'
            })
        # сохранение ответов в сессии
        request.session[f'answers_{questions[current_question_id].id}'] = selected_answer_ids
        
        # Переход к следующему вопросу
        next_question_id = current_question_id + 1
        if next_question_id < len(questions):
            request.session['current_question_index'] = next_question_id
            return redirect(reverse('tests:test_question', args=[test_id, next_question_id]))
        else:
            return redirect(reverse('tests:test_results', args=[test_id]))
        
    
    # сохранение индекса текущего вопроса в сессии для предотвращения перескакивания вопросов
    request.session['current_question_index'] = 0 
    # Отображение первого вопроса
    return redirect(reverse('tests:test_question', args=[test_id, 0]))


@login_required
def test_question_view(request, test_id, question_index):
    test = get_object_or_404(Test, id=test_id)
    questions = test.questions.all()

    # Проверка на соответствие текущего индекса вопроса и индекса в сессии
    current_question_index = request.session.get('current_question_index', 0)
    if question_index != current_question_index:
        return redirect(reverse('tests:test_question', args=[test_id, current_question_index]))

    if question_index >= len(questions):
        return redirect(reverse('tests:test_results', args=[test_id]))
    
    question = questions[question_index]
    answers = question.answers.all()
    
    return render(request, 'test/question.html', {
        'test': test,
        'question': question,
        'answers': answers,
        'current_question_index': question_index,
    })


# результаты теста
@login_required
def test_results_view(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = test.questions.all()

    total_questions = len(questions)
    correct_answers = 0

    # подсчёт правильных ответов
    for question in questions:
        selected_answer_ids = request.session.get(f'answers_{question.id}', [])
        correct_answer_ids = question.answers.filter(is_correct=True).values_list('id', flat=True)

        if set(selected_answer_ids) == set(correct_answer_ids):
            correct_answers += 1
    incorrect_answers = total_questions - correct_answers
    percentage_correct = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

    return render(request, 'test/results.html', {
        'test': test,
        'correct_answers': correct_answers,
        'incorrect_answers': incorrect_answers,
        'percentage_correct': percentage_correct,
    })


# AUTH
def first_page_login(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid(): 
            email = form.cleaned_data['email']
            User = get_user_model()  # Получаем модель пользователя

            try:
                user = User.objects.get(email=email)
                # Проверяем, зарегистрирован ли пользователь через социальную сеть
                if user.social_auth.exists():
                    email_address = EmailAddress.objects.filter(user=user, email=email, verified=True).first()
                    if email_address:
                        return redirect(f"{reverse('account_login')}?email={email}")
                    else:
                        return redirect('password_reset_notification')
                return redirect(f"{reverse('account_login')}?email={email}")
            
            except User.DoesNotExist:
                error_message = 'Пользователь с таким email не найден'
                form.add_error('email', error_message)
    else:
        form = EmailForm()

    return render(request, 'account/first_page_login.html', {'form': form})


def password_reset_notification(request):
    return render(request, 'account/password_reset_notification.html')


class CustomLoginView(LoginView): # email сохраняется в форме даже при ошибке
    def get(self, request, *args, **kwargs):
        email = request.GET.get('email', '')
        context = self.get_context_data()
        context['email'] = email
        return self.render_to_response(context)
    
    def form_invalid(self, form):
        email = self.request.POST.get('login', '')
        return self.render_to_response(self.get_context_data(form=form, email=email))
    
    def form_valid(self, form):
        email = form.cleaned_data.get('login') 
        user = CustomUser.objects.filter(email=email).first()

        if user is None:
            messages.error(self.request, "Пользователь с указанным email не найден.")
            return self.form_invalid(form)
        
        email_address = EmailAddress.objects.filter(email=email, verified=True).first()
        
        if email_address is None:
            messages.error(self.request, "Ваш email еще не подтвержден. Проверьте вашу почту.")
            return redirect('account_email_verification_sent')

        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return super().form_valid(form)

class CustomPasswordResetView(PasswordResetView): # email сохраняется в форме даже при ошибке
    def get(self, request, *args, **kwargs):
        email = request.GET.get('email', '')
        context = self.get_context_data()
        context['email'] = email
        return self.render_to_response(context)

    def form_invalid(self, form):
        email = self.request.POST.get('email', '')
        return self.render_to_response(self.get_context_data(form=form, email=email))
    
