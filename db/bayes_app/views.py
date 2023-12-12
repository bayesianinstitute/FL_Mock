from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TrainingInformation,TrainingResult,Logs,Track,NodeStatus,Admin,GlobalModelHash,TrainingResultAdmin
from .serializers import AdminModelHashSerializer,TrainingInformationSerializer,TrainingUniqueInformationSerializer,TrainingResultSerializer,LogsSerializer,TrackSerializer,NodeStatusSerializer,AdminSerializer,GlobalModelHashSerializer,TrainingResultAdminSerializer,UpdateOperationStatusSerializer,OperationStatusResponseSerializer,OperationStatusRequestSerializer
from django.shortcuts import render
import random
from itertools import groupby
from django.db.models import F
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse

def dfl(request):
    return render(request, 'dfl/index.html')
def dfladmin(request):
    return render(request, 'dfl/config.html')

@api_view(['POST'])
def create_training_information(request):
    serializer = TrainingInformationSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def get_training_results(request):
    if request.method == 'GET':
        training_results = TrainingResult.objects.all()
        serializer = TrainingResultSerializer(training_results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def create_training_result(request):
    if request.method == 'POST':
        serializer = TrainingResultSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['GET'])
def get_logs(request):
    if request.method == 'GET':
        logs = Logs.objects.all()
        serializer = LogsSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
def update_admin_role(request):
    track = Track.objects.get_or_create_single_instance()
    
    serializer = TrackSerializer(track, data={'role': 'Admin'}, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_backup_admin_role(request):
    track = Track.objects.get_or_create_single_instance()
    serializer = TrackSerializer(track, data={'role': 'BackupAdmin'}, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_user_role(request):
    track = Track.objects.get_or_create_single_instance()
    serializer = TrackSerializer(track, data={'role': 'User'}, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_network_status(request, new_status):
    node_status = NodeStatus.objects.get_or_create_single_instance()

    if new_status not in ['connected', 'disconnected', 'idle']:
        return Response({'error': 'Invalid network status'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = NodeStatusSerializer(node_status, data={'network_status': new_status}, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def toggle_training_status(request):
    node_status = NodeStatus.objects.get_or_create_single_instance()
    
    new_training_status = 'in_progress' if node_status.training_status != 'in_progress' else 'not_in_progress'

    serializer = NodeStatusSerializer(node_status, data={'training_status': new_training_status}, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_or_update_status(request):
    try:
        admin_instance = Admin.objects.get(node_id=request.data['node_id'])
        serializer = AdminSerializer(admin_instance, data=request.data, partial=True)
    except Admin.DoesNotExist:
        serializer = AdminSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_admin_data(request):
    try:
        admin_instances = Admin.objects.order_by('-timestamp')

        if not admin_instances.exists():
            return Response({'error': 'Admin data not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AdminSerializer(admin_instances, many=True)
        return Response(serializer.data)
    except Admin.DoesNotExist:
        return Response({'error': 'Admin data not found'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def post_global_model_hash(request):
    serializer = GlobalModelHashSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
    
@api_view(['GET'])
def get_global_model_hash(request):
    try:
        global_model_hash_instance = GlobalModelHash.objects.latest('timestamp')
        serializer = GlobalModelHashSerializer(global_model_hash_instance)
        return Response(serializer.data)
    except GlobalModelHash.DoesNotExist:
        return Response({'error': 'Global Model Hash data not found'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def get_track_role(request):
    try:
        latest_track_instance = Track.objects.latest('id')
        role = latest_track_instance.role
        return Response({'role': role})
    except Track.DoesNotExist:
        return Response({'error': 'Track data not found'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def get_all_users_metrics(request, metric_name, training_name):
    try:
        allowed_metrics = ['accuracy', 'loss']
        if metric_name not in allowed_metrics:
            return Response({'error': f"Invalid metric parameter. Allowed values: {', '.join(allowed_metrics)}"}, status=400)
        metric_field = F(metric_name)

        metric_records = TrainingResultAdmin.objects.filter(
            training_info__training_name=training_name
        ).order_by('node_id').values('node_id', metric=metric_field)

        grouped_data = []
        for node_id, records in groupby(metric_records, key=lambda x: x['node_id']):
            
            data = [record['metric'] for record in records]

            grouped_data.append({
                'node_id': node_id,
                'data': data
            })

        return Response(grouped_data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_logs(request):
    try:
       
        logs = Logs.objects.all().order_by('-timestamp')
        serializer = LogsSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def add_nodes(request):
    if request.method == 'POST':
        node_id = request.data.get('node_id')
        
        if Admin.objects.filter(node_id=node_id).exists():
            return Response({'error': 'Record with the same node_id already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def unique_node_id_count(request):
    if request.method == 'GET':
        unique_node_id_count = Admin.objects.values('node_id').distinct().count()
        return Response({'count': unique_node_id_count})
    
@api_view(['POST'])
def add_global_model_hash(request):
    if request.method == 'POST':
        new_global_model_hash = request.data.get('global_model_hash')
        global_model_hash_instance = GlobalModelHash.objects.create(
            global_model_hash=new_global_model_hash
        )
        return Response({'message': 'Global model hash added successfully'})
    
@api_view(['POST'])
def add_training_result(request):
    serializer = TrainingResultAdminSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_operation_status(request):
    if request.method == 'PUT':
        serializer = UpdateOperationStatusSerializer(data=request.data)

        if serializer.is_valid():
            node_id = serializer.validated_data['node_id']
            operation_status = serializer.validated_data['operation_status']

            try:
                admin_instance = Admin.objects.get(node_id=node_id)
                previous_operation_status = admin_instance.operation_status

                admin_instance.operation_status = operation_status
                admin_instance.save()

                return Response({
                    "status": "success",
                    "message": "Operation status updated successfully",
                    "previous_operation_status": previous_operation_status,
                    "current_operation_status": operation_status
                }, status=status.HTTP_200_OK)
            except Admin.DoesNotExist:
                return Response({"status": "error", "message": "Admin with the specified node_id does not exist"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def get_operation_status(request):
    try:
        serializer = OperationStatusRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        node_id = serializer.validated_data['node_id']

        admin_instance = Admin.objects.get(node_id=node_id)
        serializer = OperationStatusResponseSerializer(admin_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Admin.DoesNotExist:
        return Response({"status": "error", "message": "Admin with the specified node_id does not exist"}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
def get_unique_training_names(request):
    if request.method == 'GET':
        unique_training_names = TrainingInformation.objects.values('training_name').distinct()
        training_names_list = [entry['training_name'] for entry in unique_training_names]
        response_data = {"data": training_names_list}
        return Response(response_data, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def training_information_choices(request):
    model_name_choices = [choice[0] for choice in TrainingInformation.model_name_choices]
    dataset_name_choices = [choice[0] for choice in TrainingInformation.dataset_name_choices]
    optimizer_choices = [choice[0] for choice in TrainingInformation.optimizer_choices]

    choices_data = {
        'model_name_choices': model_name_choices,
        'dataset_name_choices': dataset_name_choices,
        'optimizer_choices': optimizer_choices,
    }

    return Response(choices_data)


@api_view(['GET'])
def get_model_hashes(request):
    threshold_time = timezone.now() - timedelta(minutes=2)
    model_hashes = Admin.objects.filter(timestamp__gte=threshold_time).values_list('model_hash', flat=True)
    serializer = AdminModelHashSerializer({'model_hash': list(model_hashes)}, many=False)
    return Response(serializer.data)

@api_view(['PUT'])
def update_logs(request):
    try:
        # Retrieve the existing log entry (assuming you have a single log entry in this example)
        log_entry = Logs.objects.first()

        # Get the new log message from the request
        new_log_message = request.data.get('logs', '')

        if log_entry is not None:
            # If a log entry exists, append a new line to the existing message
            log_entry.message += f"\n{new_log_message}"
        else:
            # If no log entry exists, create a new log entry with the provided message
            log_entry = Logs.objects.create(message=new_log_message)

        # Save the updated or new log entry
        log_entry.save()

        # Serialize the data
        serializer = LogsSerializer(log_entry)

        return Response({'logs': serializer.data['message']})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)