from django.contrib import admin
from .models import Test, Question, Answer
from django.utils.html import format_html
from django.core.exceptions import ValidationError


class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 0
    fields = ('text', 'is_correct')

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0
    fields = ('text',)

    def edit_link(self, obj):
        return format_html('<a href="{}">Редактировать ответы</a>', obj.get_absolute_url())
    
    edit_link.short_description = 'Действия'


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    list_filter = ('title',)
    ordering = ('title',)
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'test')
    search_fields = ('text',)
    list_filter = ('test',)
    raw_id_fields = ('test',)
    ordering = ('test', 'text')
    inlines = [AnswerInline]  

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        question = form.instance

        # Проверка, что у вопроса есть ответы и что это не первый ответ
        if question.answers.count() > 1:
            # Проверка, что есть хотя бы один правильный ответ
            if not question.answers.filter(is_correct=True).exists():
                raise ValidationError('Должен быть хотя бы один правильный ответ.')

            # Проверка, что не все ответы являются правильными
            if question.answers.filter(is_correct=True).count() == question.answers.count():
                raise ValidationError('Не все ответы могут быть правильными.')

            # Проверка, что есть хотя бы один неправильный ответ
            if not question.answers.filter(is_correct=False).exists():
                raise ValidationError('Должен быть хотя бы один неправильный ответ.')
            
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    search_fields = ('text', 'question__text',)
    list_filter = ('is_correct',)
    ordering = ('question', 'text')
    raw_id_fields = ('question',)
