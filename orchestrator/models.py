from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField


class TestRequest(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    ENV_CHOICES = (
        ('DT', 'DocTest'),
        ('UT', 'Unittest'),
    )
    environment = models.CharField(max_length=100, choices=ENV_CHOICES)
    
    INTF_CHOICES = tuple((str(i), i) for i in range(1, 101))
    interface = models.CharField(max_length=100, choices=INTF_CHOICES,)
    
    template = models.CharField(max_length=20, default="Web Application")
    file = models.FileField(upload_to='files/')
    file_names = ArrayField(models.CharField(max_length=100))
    state = models.CharField(max_length=10, default='Running')
    request_date = models.DateTimeField(default=timezone.now)
    failures = ArrayField(models.TextField(), null=True)
    description = models.CharField(max_length=10, null=True)
    errors = ArrayField(models.TextField(), null=True)
    
    def add(self, **kwargs):
        self.request_date = timezone.now()
        self.environment = kwargs['environment']
        self.interface = kwargs['interface']
        self.user = kwargs['user']
        self.file_names = kwargs['file_names']
        self.save()

    def update_state(self, **kwargs):
        self.state = kwargs['new_state']
        self.errors = kwargs['errors']
        self.description = kwargs['desc']
        self.failures = kwargs['failures']
        self.save()
