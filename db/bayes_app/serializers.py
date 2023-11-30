from rest_framework import serializers
from .models import TrainingInformation,TrainingResult,Logs,Track,NodeStatus,Admin

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
        
class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['role']
        
class NodeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeStatus
        fields = ['network_status','training_status']
        
class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'