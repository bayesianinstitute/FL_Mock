from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TrainingInformation,TrainingResult,Logs
from .serializers import TrainingInformationSerializer,TrainingResultSerializer,LogsSerializer
from django.shortcuts import render

def dfluser(request):
    return render(request, 'dfl/user.html')

def dfladmin(request):
    return render(request, 'dfl/admin.html')

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
