from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TrainingInformation,TrainingResult,Logs,Track,NodeStatus,Admin,GlobalModelHash,TrainingResultAdmin
from .serializers import TrainingInformationSerializer,TrainingResultSerializer,LogsSerializer,TrackSerializer,NodeStatusSerializer,AdminSerializer,GlobalModelHashSerializer,TrainingResultAdminSerializer
from django.shortcuts import render
import random
from itertools import groupby

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
        # Assuming you want the latest admin data (based on timestamp)
        admin_instance = Admin.objects.latest('timestamp')
        serializer = AdminSerializer(admin_instance)
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
def get_all_users_accuracy(request, training_name):
    try:
        accuracy_records = TrainingResultAdmin.objects.filter(
            training_info__training_name=training_name
        ).order_by('node_id')  # Ensure records are ordered by node_id

        grouped_data = []
        for node_id, records in groupby(accuracy_records, key=lambda x: x.node_id):
            # Convert the group of records into a list of accuracy values
            data = [record.accuracy for record in records]

            # Append the data to the result list
            grouped_data.append({
                'node_id': node_id,
                'data': data
            })

        return Response(grouped_data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def get_accuracy_by_training_name_and_node_id(request, training_name, node_id):
    try:
        accuracy_records = TrainingResultAdmin.objects.filter(
            training_info__training_name=training_name, 
            node_id=node_id
        ).order_by('timestamp')  # Ensure records are ordered by timestamp
        serializer = TrainingResultAdminSerializer(accuracy_records, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)