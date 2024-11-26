from django.db import models
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Поле email должно быть заполнено")
        
        email = self.normalize_email(email)
        
        existing_user = self.model.objects.filter(email=email).first()
        if existing_user:
            for key, value in extra_fields.items():
                setattr(existing_user, key, value)
            existing_user.save(using=self._db)
            return existing_user
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, verbose_name='именем', unique=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.email
    
    
# тест
class Test(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название')

    def count_questions(self):
        return self.questions.count()
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Тест'  
        verbose_name_plural = 'Тесты'
        ordering = ['title']


# вопрос
class Question(models.Model):
    text = models.CharField(max_length=255, verbose_name='Вопрос')
    test = models.ForeignKey(Test, related_name='questions',
                              on_delete=models.CASCADE, verbose_name='Тест')
    
    class Meta:
        verbose_name = 'Вопрос'  
        verbose_name_plural = 'Вопросы'
        indexes = [
            models.Index(fields=['test']),
        ]
    
    def __str__(self):
        return self.text
    
    def get_absolute_url(self):
        return reverse('admin:tests_app_question_change', args=[self.pk])
    
        
# ответ         
class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE,
                                  verbose_name='Вопрос')
    text = models.CharField(max_length=255, verbose_name='ответ')
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
    
    class Meta:
        verbose_name = 'Ответ'  
        verbose_name_plural = 'Ответы'
        indexes = [
            models.Index(fields=['question']),
        ]
