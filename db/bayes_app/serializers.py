from rest_framework import serializers
from .models import TrainingInformation,TrainingResult,Logs

class TrainingInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingInformation
        fields = '__all__'
        
class TrainingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingResult
        fields = '__all__'
        
class LogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logs
        fields = '__all__'