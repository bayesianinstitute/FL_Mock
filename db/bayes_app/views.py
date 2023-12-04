from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TrainingInformation,TrainingResult,Logs,Track,NodeStatus,Admin,GlobalModelHash,TrainingResultAdmin
from .serializers import TrainingInformationSerializer,TrainingResultSerializer,LogsSerializer,TrackSerializer,NodeStatusSerializer,AdminSerializer,GlobalModelHashSerializer,TrainingResultAdminSerializer
from django.shortcuts import render
import random
from itertools import groupby
from django.db.models import F

def dfluser(request):
    return render(request, 'dfl/user.html')

def dfladmin(request):
    return render(request, 'dfl/admin.html')

def dfl(request):
    return render(request, 'dfl/index.html')

# Create your views here.
@api_view(['POST'])
def create_training_information(request):
    if request.method == 'POST':
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
    # Get or create the single instance
    track = Track.objects.get_or_create_single_instance()

    # Update the role to Admin
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

    # Ensure the provided status is valid
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

    # Toggle the training_status
    new_training_status = 'in_progress' if node_status.training_status != 'in_progress' else 'not_in_progress'

    serializer = NodeStatusSerializer(node_status, data={'training_status': new_training_status}, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_or_update_admin(request):
    try:
        # Attempt to get the existing Admin instance
        admin_instance = Admin.objects.get()

        # If the instance exists, update the data with the provided data
        serializer = AdminSerializer(admin_instance, data=request.data, partial=True)
    except Admin.DoesNotExist:
        # If no instance exists, create a new one with a random node_id
        random_node_id = random.randint(1, 1000)  # Adjust the range as needed
        request.data['node_id'] = random_node_id
        serializer = AdminSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_admin_data(request):
    try:
        # Fetch all entries ordered by timestamp
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
        # Ensure that the metric_name is one of the allowed metrics
        allowed_metrics = ['accuracy', 'loss', 'validation_accuracy']
        if metric_name not in allowed_metrics:
            return Response({'error': f"Invalid metric parameter. Allowed values: {', '.join(allowed_metrics)}"}, status=400)

        # Use F expressions to dynamically select the desired metric field
        metric_field = F(metric_name)

        # Query the database with the selected metric field
        metric_records = TrainingResultAdmin.objects.filter(
            training_info__training_name=training_name
        ).order_by('node_id').values('node_id', metric=metric_field)

        grouped_data = []
        for node_id, records in groupby(metric_records, key=lambda x: x['node_id']):
            # Convert the group of records into a list of metric values
            data = [record['metric'] for record in records]

            # Append the data to the result list
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
        # Fetch all logs ordered by timestamp
        logs = Logs.objects.all().order_by('-timestamp')
        
        # Serialize the logs data
        serializer = LogsSerializer(logs, many=True)
        
        # Return the serialized data as a JSON response
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)