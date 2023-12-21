from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TrainingInformation,TrainingResult,Logs,Track,NodeStatus,Admin,GlobalModelHash,TrainingResultAdmin
from .serializers import AdminModelHashSerializer,TrainingInformationSerializer,TrainingUniqueInformationSerializer,TrainingResultSerializer,LogsSerializer,TrackSerializer,NodeStatusSerializer,AdminSerializer,GlobalModelHashSerializer,TrainingResultAdminSerializer,UpdateOperationStatusSerializer,OperationStatusResponseSerializer,OperationStatusRequestSerializer
from django.shortcuts import render
import random
from itertools import groupby
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from rest_framework import status as drf_status
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.db import IntegrityError



def dfl(request):
    return render(request, 'dfl/index.html')
def dfladmin(request):
    return render(request, 'dfl/config.html')

def mlflow(request):
    # Get the current request's host (including the dynamic IP address)
    current_host = request.get_host()
    
    # Construct the new URL with the desired port (e.g., 5000)
    new_url = f'http://{current_host.replace(":8000", ":5000")}/'

    return redirect(new_url)


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
        # Extract training_info_name from the request data
        training_info_name = request.data.get('training_info_name')

        # Retrieve the TrainingInformation instance based on the name
        try:
            training_info = TrainingInformation.objects.get(training_name=training_info_name)
        except TrainingInformation.DoesNotExist:
            return Response({'error': f'TrainingInformation with name {training_info_name} does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        # Update the request data with the TrainingInformation instance
        request.data['training_info'] = training_info.id

        # Use the serializer to validate and save the data
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
        node_id = request.data.get('node_id')
        admin_instance, created = Admin.objects.get_or_create(node_id=node_id)

        training_info_name = request.data.get('training_info')

        # Query TrainingInformation model to get the instance based on training_name
        try:
            training_info = TrainingInformation.objects.get(training_name=training_info_name)
        except TrainingInformation.DoesNotExist:
            return Response({'error': f"TrainingInformation with training_name '{training_info_name}' does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Update the serializer data with the obtained training_info instance
        request.data['training_info'] = training_info.id  # Assuming 'id' is the primary key of TrainingInformation

        serializer = AdminSerializer(admin_instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Admin.DoesNotExist:
        return Response({'error': f"Admin with node_id '{node_id}' does not exist."},
                        status=status.HTTP_400_BAD_REQUEST)

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
    data = request.data
    try:
        training_info = TrainingInformation.objects.get(training_name=data.get('training_info'))
    except TrainingInformation.DoesNotExist:
        return Response({'error': f'Training name "{data.get("training_info")}" not available.'}, status=status.HTTP_400_BAD_REQUEST)
    data.pop('training_info', None)
    try:
        global_model_hash = GlobalModelHash.objects.create(training_info=training_info, **data)
        return Response({'global_model_hash': global_model_hash.global_model_hash}, status=status.HTTP_201_CREATED)
    except IntegrityError as e:
        return Response({'error': f'Error creating GlobalModelHash: {str(e)}'}, status=status.HTTP_409_CONFLICT)
    
    
@api_view(['GET'])
def get_global_model_hash(request):
    try:
        latest_hash = GlobalModelHash.objects.latest('timestamp')
        serializer = GlobalModelHashSerializer(latest_hash)
        return Response(serializer.data)
    except GlobalModelHash.DoesNotExist:
        return Response({"error": "No global model hash found"}, status=404)
    
@api_view(['GET'])
def get_track_role(request):
    try:
        latest_track_instance = Track.objects.latest('id')
        role = latest_track_instance.role
        return Response({'role': role})
    except Track.DoesNotExist:
        return Response({'error': 'Track data not found'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def get_all_users_metrics(request, metric_name):
    try:
        allowed_metrics = ['accuracy', 'loss']
        if metric_name not in allowed_metrics:
            return Response({'error': f"Invalid metric parameter. Allowed values: {', '.join(allowed_metrics)}"}, status=400)

        training_name = request.data.get('training_name')
        if not training_name:
            return Response({'error': 'Missing training_name in the request body'}, status=400)

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
    # Extract data from the request payload
    training_name = request.data.get('training_info')  # Use the string 'training_info'
    node_id_char = request.data.get('node_id')
    accuracy = request.data.get('accuracy')
    loss = request.data.get('loss')

    # Check if node_id_char is present in Admin table
    try:
        admin_instance = Admin.objects.get(node_id=node_id_char)
    except Admin.DoesNotExist:
        return Response({'error': f"Admin with node_id '{node_id_char}' does not exist."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Query TrainingInformation model to get the instance based on training_name
    try:
        training_info = TrainingInformation.objects.get(training_name=training_name)
    except TrainingInformation.DoesNotExist:
        return Response({'error': f"TrainingInformation with training_name '{training_name}' does not exist."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Create a dictionary with the extracted data and the obtained training_info and admin_instance
    data = {
        'training_info': training_info.id,  # Assuming 'id' is the primary key of TrainingInformation
        'node_id': admin_instance.id,  # Use the primary key of the Admin instance
        'accuracy': accuracy,
        'loss': loss,
    }

    # Use the serializer with the extracted data
    serializer = TrainingResultAdminSerializer(data=data)

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
        new_log_message = request.data.get('logs', '')
        training_info_name = request.data.get('training_info', '')

        # Check if TrainingInformation with the given name exists
        try:
            training_info = TrainingInformation.objects.get(training_name=training_info_name)
        except TrainingInformation.DoesNotExist:
            return JsonResponse({'error': f'Training name "{training_info_name}" not available.'}, status=400)

        # Retrieve the latest log entry for the provided training_info
        log_entry = Logs.objects.filter(training_info=training_info).first()

        if log_entry is not None:
            # Update the existing log entry
            log_entry.message = f"{new_log_message}\n{log_entry.message}"
        else:
            # Create a new log entry
            log_entry = Logs.objects.create(
                message=new_log_message,
                training_info=training_info
            )

        log_entry.save()
        serializer = LogsSerializer(log_entry)

        return Response({'logs': serializer.data['message']})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@api_view(['GET'])
def get_latest_global_model_hash(request):
    try:
        latest_hash = GlobalModelHash.objects.latest('timestamp')
        serializer = GlobalModelHashSerializer(latest_hash)
        return Response(serializer.data)
    except GlobalModelHash.DoesNotExist:
        return Response({"error": "No global model hash found"}, status=404)
    
    
@api_view(['PUT'])
def update_node_status(request, status, new_status):
    # Validate the input status
    valid_statuses = ['operation', 'network']
    if status not in valid_statuses:
        return Response({'error': f'Invalid status type: {status}'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate the new_status
    valid_operation_statuses = [choice[0] for choice in NodeStatus.OPERATION_CHOICES]
    valid_network_statuses = [choice[0] for choice in NodeStatus.NETWORK_STATUS_CHOICES]

    if status == 'operation' and new_status not in valid_operation_statuses:
        return Response({'error': f'Invalid operation status: {new_status}'}, status=status.HTTP_400_BAD_REQUEST)
    elif status == 'network' and new_status not in valid_network_statuses:
        return Response({'error': f'Invalid network status: {new_status}'}, status=status.HTTP_400_BAD_REQUEST)

    # Try to get an existing NodeStatus instance
    node_status, created = NodeStatus.objects.get_or_create()

    # Update the appropriate status field
    if status == 'operation':
        node_status.operation_status = new_status
    elif status == 'network':
        node_status.network_status = new_status

    # Save the changes
    node_status.save()

    # Return a response
    return Response({'message': f'Successfully updated {status} status to {new_status}'}, status=drf_status.HTTP_200_OK)


@api_view(['PUT'])
def update_model_hash(request):
    try:
        # Extract training_info from request data
        training_info_name = request.data.get('training_info')

        # Check if TrainingInformation with the given name exists
        try:
            training_info = TrainingInformation.objects.get(training_name=training_info_name)
        except TrainingInformation.DoesNotExist:
            return Response({'error': f'Training name "{training_info_name}" not available.'}, status=status.HTTP_400_BAD_REQUEST)

        node_status = NodeStatus.objects.first()

        # Update data dictionary with the primary key of training_info
        request.data['training_info'] = training_info.pk

        serializer = NodeStatusSerializer(node_status, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except NodeStatus.DoesNotExist:
        # Create a new NodeStatus instance
        serializer = NodeStatusSerializer(data=request.data)
        if serializer.is_valid():
            # Check if TrainingInformation with the given name exists
            try:
                training_info = TrainingInformation.objects.get(training_name=training_info_name)
            except TrainingInformation.DoesNotExist:
                return Response({'error': f'Training name "{training_info_name}" not available.'}, status=status.HTTP_400_BAD_REQUEST)

            # Assign the primary key of training_info to the serializer data
            serializer.validated_data['training_info'] = training_info.pk

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except IntegrityError as e:
        return Response({'error': f'Error updating NodeStatus: {str(e)}'}, status=status.HTTP_409_CONFLICT)

@api_view(['GET'])
def get_training_information_by_name(request, training_name):
    try:
        training_info = TrainingInformation.objects.get(training_name=training_name)
        serializer = TrainingInformationSerializer(training_info)
        return Response(serializer.data)
    except TrainingInformation.DoesNotExist:
        return Response({"detail": "Training information not found"}, status=404)