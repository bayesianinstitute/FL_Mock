from django.urls import path
from .views import dfluser,dfladmin,create_training_information,create_training_result,get_training_results,get_logs,update_admin_role,update_backup_admin_role,update_user_role,update_network_status,toggle_training_status,create_or_update_admin,get_admin_data,post_global_model_hash,get_global_model_hash,get_track_role




urlpatterns = [

    path('dfluser/', dfluser, name='dfluser'),
    path('dfladmin/', dfladmin, name='dfladmin'),
    path('api/v1/create-training-information/', create_training_information, name='create-training-information'),
    path('api/v1/create_training_result/', create_training_result, name='create_training_result'),
    path('api/v1/get-training-results/', get_training_results, name='get-training-results'),
    path('api/v1/get-logs/', get_logs, name='get-logs'),
    
    path('api/v1/update-admin/', update_admin_role, name='update_admin_role'),
    path('api/v1/update-backup-admin/', update_backup_admin_role, name='update_backup_admin_role'),
    path('api/v1/update-user/', update_user_role, name='update_user_role'),
    path('api/v1/update-network-status/<str:new_status>/', update_network_status, name='update_network_status'),
    path('api/v1/toggle-training-status/', toggle_training_status, name='toggle_training_status'),
    path('api/v1/create-or-update-admin/', create_or_update_admin, name='create_or_update_admin'),
    path('api/v1/get-admin-data/', get_admin_data, name='get_admin_data'),
    path('api/v1/post-global-model-hash/', post_global_model_hash, name='post_global_model_hash'),
    path('api/v1/get-global-model-hash/', get_global_model_hash, name='get_global_model_hash'),
    path('api/v1/get-track-role/', get_track_role, name='get_track_role'),
]
