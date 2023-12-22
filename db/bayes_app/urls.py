from django.urls import path
from .views import dfl,dfladmin,mlflow,changerole,get_training_information_by_name,update_model_hash,update_node_status
from .views import get_model_hashes,update_logs,training_information_choices,create_training_information,create_training_result
from .views import get_training_results,get_logs,update_admin_role,update_backup_admin_role,update_user_role,update_network_status
from .views import toggle_training_status,create_or_update_status,get_admin_data,post_global_model_hash,get_global_model_hash,get_track_role
from .views import dfl,get_all_users_metrics,get_logs,add_nodes,unique_node_id_count,add_global_model_hash,add_training_result
from .views import update_operation_status,get_operation_status,get_unique_training_names




urlpatterns = [
    path('', dfl, name='dfl'),
    path('config/', dfladmin, name='dfladmin'),
    path('mlflow/', mlflow, name='mlflow'),
    path('changerole/', changerole, name='mlflow'),


    path('api/v1/update_admin/', update_admin_role, name='update_admin_role'),
    # path('api/v1/update_backup_admin/', update_backup_admin_role, name='update_backup_admin_role'),
    path('api/v1/update_user/', update_user_role, name='update_user_role'),
    # path('api/v1/node_id_count/', unique_node_id_count, name='unique_node_id_count'),
    # path('api/v1/add_global_model_hash/', add_global_model_hash, name='add_global_model_hash'),

    # Working 
    path('api/v1/create_or_update_status/', create_or_update_status, name='create_or_update_status'),
    path('api/v1/add_training_result/', add_training_result, name='add_training_result'),
    path('api/v1/update_operation_status/', update_operation_status, name='update_operation_status'),
    path('api/v1/get_operation_status/', get_operation_status, name='get_operation_status'),
    path('api/v1/get_unique_training_names/', get_unique_training_names, name='get_unique_training_names'),
    path('api/v1/training_information_choices/', training_information_choices, name='training_information_choices'),
    path('api/v1/get_model_hashes/', get_model_hashes, name='get_model_hashes'),
    path('api/v1/logs/', get_logs, name='get_logs'),
    path('api/v1/update_logs/', update_logs, name='update_logs'),
    path('api/v1/get_global_model_hash/', get_global_model_hash, name='get_global_model_hash'),
    path('api/v1/post_global_model_hash/', post_global_model_hash, name='post_global_model_hash'),
    
    path('api/v1/update_status/<str:status>/<str:new_status>/', update_node_status, name='update_status'),
    path('api/v1/create_training_information/', create_training_information, name='create_training_information'),
    path('api/v1/create_training_result/', create_training_result, name='create_training_result'),
    path('api/v1/update_model_hash/', update_model_hash, name='update_model_hash'),
    path('api/v1/get_training_info/<str:training_name>/', get_training_information_by_name, name='get_training_info'),
    path('api/v1/get_admin_data/', get_admin_data, name='get_admin_data'),
    path('api/v1/get_track_role/', get_track_role, name='get_track_role'),
    path('api/v1/<str:metric_name>/', get_all_users_metrics, name='metrics_api_all'),
    path('api/v1/get_training_results/', get_training_results, name='get-training-results'),
    path('api/v1/update_network_status/<str:new_status>/', update_network_status, name='update_network_status'),
    path('api/v1/toggle_training_status/', toggle_training_status, name='toggle_training_status'),
    path('api/v1/add_nodes/', add_nodes, name='add_admin'),
    
    
]
