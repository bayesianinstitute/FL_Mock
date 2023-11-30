from django.urls import path
from .views import dfluser,dfladmin,create_training_information,create_training_result,get_training_results,get_logs

urlpatterns = [

    path('dfluser/', dfluser, name='dfluser'),
    path('dfladmin/', dfladmin, name='dfladmin'),
    path('api/v1/create-training-information/', create_training_information, name='create-training-information'),
    path('api/v1/create_training_result/', create_training_result, name='create_training_result'),
    path('api/v1/get-training-results/', get_training_results, name='get-training-results'),
    path('api/v1/get-logs/', get_logs, name='get-logs'),
]
