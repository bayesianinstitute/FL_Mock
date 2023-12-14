from rest_framework import serializers
from .models import TrainingInformation,TrainingResult,Logs,Track,NodeStatus,Admin,GlobalModelHash,TrainingResultAdmin

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
        fields = '__all__'
        
class NodeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeStatus
        fields = '__all__'
        
class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'
        
class GlobalModelHashSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalModelHash
        fields = ['global_model_hash']

class TrainingResultAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingResultAdmin
        fields = '__all__'

    def get_data(self, obj):
        return [obj.accuracy, obj.validation_accuracy, obj.loss]  # Add more fields if needed
    
class LogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logs
        fields = ['message']
        
class UpdateOperationStatusSerializer(serializers.Serializer):
    node_id = serializers.CharField(max_length=100)
    operation_status = serializers.ChoiceField(choices=Admin.OPERATION_CHOICES)

class OperationStatusRequestSerializer(serializers.Serializer):
    node_id = serializers.IntegerField()

class OperationStatusResponseSerializer(serializers.Serializer):
    operation_status = serializers.CharField(max_length=20)

    def to_representation(self, instance):
        return {
            'operation_status': instance.operation_status,
        }

class TrainingUniqueInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingInformation
        fields = ['training_name']


class AdminModelHashSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['model_hash']