from django.db import models


# Create your models here.
class TrainingInformation(models.Model):
    model_name_choices = [
        ('ANN', 'Artificial Neural Network'),
        ('CNN', 'Convolutional Neural Network'),
    ]

    dataset_name_choices = [
        ('Mnist', 'MNIST'),
        ('FashionMNIST', 'FashionMNIST'),
    ]

    optimizer_choices = [
        ('Adam', 'Adam'),
        ('Sgd', 'Stochastic Gradient Descent'),
    ]
    model_name = models.CharField(max_length=50, choices=model_name_choices)
    dataset_name = models.CharField(max_length=50, choices=dataset_name_choices)
    optimizer = models.CharField(max_length=50, choices=optimizer_choices)
    training_name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return f"{self.training_name}"
    class Meta:
        verbose_name_plural="Training Information"
    
class TrainingResult(models.Model):
    training_info = models.ForeignKey(TrainingInformation, on_delete=models.CASCADE, related_name='training_results',null=True, blank=True)
    accuracy = models.FloatField()
    validation_accuracy = models.FloatField()
    loss = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.training_info.model_name} - {self.training_info.dataset_name} - {self.training_info.optimizer} - {self.timestamp}"
   
    class Meta:
        verbose_name_plural="Training Result"
    
class TrainingResultAdmin(models.Model):
    training_info = models.ForeignKey(
        TrainingInformation,
        on_delete=models.CASCADE,
        related_name='admin_training_results',  # Provide a unique related_name
        null=True,
        blank=True
    )
    node_id = models.IntegerField()
    accuracy = models.FloatField()
    validation_accuracy = models.FloatField()
    loss = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.training_info.model_name} - {self.training_info.dataset_name} - {self.training_info.optimizer} - {self.timestamp}"
   
    class Meta:
        verbose_name_plural = "Admin Training Result"

    
class Logs(models.Model):
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp}"
    
    class Meta:
        verbose_name_plural="Logs"
        
class Admin(models.Model):
    
    TRAINING_STATUS_CHOICES = [
        ('in_progress', 'Training In Progress'),
        ('not_in_progress', 'Training Not In Progress'),
    ]

    NETWORK_STATUS_CHOICES = [
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('idle', 'Idle'),
    ]
    ROLE_CHOICES = [
        ('User', 'User'),
        ('Admin', 'Admin'),
        ('BackupAdmin', 'BackupAdmin'),
    ]

    training_status = models.CharField(
        max_length=20,
        choices=TRAINING_STATUS_CHOICES,
        default='not_in_progress'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='User'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    node_id = models.IntegerField()
    model_hash = models.CharField(max_length=255, blank=True, null=True) 
    network_status = models.CharField(
        max_length=15,
        choices=NETWORK_STATUS_CHOICES,
        default='idle'
    )
    def __str__(self):
        return f"{self.node_id}"
    
    
    class Meta:
        verbose_name_plural="Admin"
    
class NodeStatusManager(models.Manager):
    def get_or_create_single_instance(self):
        # Attempt to get the single instance, create if not found
        instance, created = self.get_or_create(pk=1)
        return instance
    
class NodeStatus(models.Model):
    TRAINING_STATUS_CHOICES = [
        ('in_progress', 'Training In Progress'),
        ('not_in_progress', 'Training Not In Progress'),
    ]

    NETWORK_STATUS_CHOICES = [
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('idle', 'Idle'),
    ]
    

    training_status = models.CharField(
        max_length=20,
        choices=TRAINING_STATUS_CHOICES,
        default='not_in_progress'
    )
    network_status = models.CharField(
        max_length=15,
        choices=NETWORK_STATUS_CHOICES,
        default='idle'
    )    
    
    objects = NodeStatusManager()
    class Meta:
        verbose_name_plural="Node Status"
    
class GlobalModelHash(models.Model):
    global_model_hash = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True) 
    class Meta:
        verbose_name_plural="GlobalModelHash"
 
class TrackManager(models.Manager):
    def get_or_create_single_instance(self):
        # Attempt to get the single instance, create if not found
        instance, created = self.get_or_create(pk=1)
        return instance
       
class Track(models.Model):
    ROLE_CHOICES = [
        ('User', 'User'),
        ('Admin', 'Admin'),
        ('BackupAdmin', 'BackupAdmin'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='User'
    )
    objects = TrackManager()
    class Meta:
        verbose_name_plural="Track"
        