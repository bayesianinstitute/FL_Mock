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
    minimum_number_of_computers = models.IntegerField()


    def __str__(self):
        return f"{self.model_name} - {self.dataset_name} - {self.optimizer}"
    class Meta:
        verbose_name_plural="Training Information"
    
class TrainingResult(models.Model):
    training_info = models.ForeignKey(TrainingInformation, on_delete=models.CASCADE, related_name='training_results',null=True, blank=True)
    training_accuracy = models.FloatField()
    validation_accuracy = models.FloatField()
    loss = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.training_info.model_name} - {self.training_info.dataset_name} - {self.training_info.optimizer} - {self.timestamp}"
   
    class Meta:
        verbose_name_plural="Training Result"
    
    
class Logs(models.Model):
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp}"
    
    class Meta:
        verbose_name_plural="Logs"