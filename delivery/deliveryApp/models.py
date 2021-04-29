from django.db import models
from django.urls import reverse
# Create your models here.



class Delivery_Out(models.Model):
    def __str__(self):
        return self.Name
    def get_absolute_url(self):
        return reverse('delivery_out_details', args=[str(self.pk)])
    Name = models.CharField(max_length=50)
    #Location = models.CharField(max_length=50)
    Phone = models.CharField(max_length=20)



class Client(models.Model):
    def __str__(self):
        return self.Company
    def get_absolute_url(self):
        return reverse('client_details', args=[str(self.pk),])
    Company = models.CharField(max_length=50, unique=True)
    Location = models.CharField(max_length=50)
    Phone = models.CharField(max_length=50)
    
    

class Delivery_In(models.Model):
    def __str__(self):
        return self.Name
    def get_absolute_url(self):
        return reverse('delivery_in_details', args=[str(self.pk),])
    Name=models.CharField(max_length=50)
    Phone = models.CharField(max_length=50)



Status_Choices = ( ('paid','PAID'), ('pending','PENDING'), ('sent','SENT'), ('refunded','REFUNDED'))
Currency_Choices = ( ('lbp','LBP'), )




class Bill(models.Model):
    def __str__(self):
        return self.Bill_Id
    def get_absolute_url(self):
        return reverse('bill_details', args=[str(self.Bill_Id),self.Status])
    Bill_Id = models.CharField(max_length=10, unique=True)
    Date_In = models.DateTimeField('Date In', null=True, blank=True)
    Date_Sent = models.DateTimeField('Date Sent', null=True, blank=True,default=None)
    Date_Paid = models.DateTimeField('Date Paid', null=True, blank=True, default=None)
    Date_Done = models.DateTimeField('Date Done', null=True, blank=True, default=None)
    Done = models.BooleanField(default=False)
    address = models.CharField(max_length=100000,default="Address not found")
    directions = models.CharField(max_length=100000,default="", blank=True)
    delivery_in = models.ForeignKey(Delivery_In, on_delete=models.CASCADE)
    delivery_out = models.ForeignKey(Delivery_Out, on_delete=models.CASCADE)
    endClientName=models.CharField(max_length=100000,default="Unknown Name")
    endClientNumber=models.CharField(max_length=10000,default="03000000")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=False)
    Product_cost = models.IntegerField( default=0)
    Currency = models.CharField(max_length=10, choices=Currency_Choices, default="lbp" )
    Delivery_cost = models.IntegerField(default=0)
    Status = models.CharField(max_length=99, choices=Status_Choices, default="pending" )
    Hidden_Status =  models.CharField(max_length=99, choices=Status_Choices, default="pending" )
    Done_Refunding = models.BooleanField(default=False)
    Extracted_For_DelOut = models.BooleanField(default=False)
    Notes = models.CharField(max_length=10000,default="", blank=True)
    Hidden_Id=models.CharField(max_length=10)



class Viewer(models.Model):
    Username=models.CharField(max_length=50)
    Password = models.CharField(max_length=50)
    Company=models.CharField(max_length=67111, default="")
    delivery_in = models.ForeignKey(Delivery_In, on_delete=models.CASCADE)