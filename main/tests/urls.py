from django.urls import path
from . import views
from .views import test_view, test_question_view, test_results_view

app_name = 'tests'

urlpatterns = [
    path('', views.index, name='index'),
    path('test/<int:test_id>/', test_view, name='test_view'),
    path('test/<int:test_id>/question/<int:question_index>/', test_question_view, name='test_question'),
    path('test/<int:test_id>/results/', test_results_view, name='test_results'),
]
