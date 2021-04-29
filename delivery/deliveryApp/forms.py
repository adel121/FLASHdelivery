from django import forms
from .models import Client, Delivery_In, Delivery_Out



class Delivery_OutForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(Delivery_OutForm, self).__init__(*args, **kwargs)
		for visible in self.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'
	Name=forms.CharField(label='Name', max_length=100)
	#Location=forms.CharField(label='Location', max_length=100)
	Phone=forms.CharField(label='Phone', max_length=100)

class ClientForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(ClientForm, self).__init__(*args, **kwargs)
		for visible in self.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'
	#Name=forms.CharField(label='Name', max_length=100)
	Company=forms.CharField(label='Company',max_length=100)
	Location=forms.CharField(label='Location', max_length=100)
	Phone=forms.CharField(label='Phone', max_length=100)


class Delivery_InForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(Delivery_InForm, self).__init__(*args, **kwargs)
		for visible in self.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'
	Name=forms.CharField(label='Name', max_length=100)
	#Location=forms.CharField(label='Location', max_length=100)
	Phone=forms.CharField(label='Phone', max_length=100)
	#client=forms.ChoiceField(choices=[(x.pk,x.Company) for x in Client.objects.all()])

class BillForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(BillForm, self).__init__(*args, **kwargs)
		for visible in self.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'
	Id = forms.CharField(label="Bill Id",max_length=20)
	#Date = forms.DateTimeField(label="Date")
	address = forms.CharField(label="Address",max_length=100000)
	delivery_in=forms.ModelChoiceField(required=True, widget=forms.Select, queryset=Delivery_In.objects.all())
	#delivery_out=forms.ModelChoiceField(required=True, widget=forms.Select, queryset=Delivery_Out.objects.all())
	endClientName=forms.CharField(label="end-client name",max_length=100000)
	endClientNumber=forms.CharField(label="end-client number", max_length=10000)
	client=forms.ModelChoiceField(required=True, widget=forms.Select, queryset=Client.objects.all())
	Product_cost=forms.DecimalField(label="Product Cost in LBP", max_digits=30, decimal_places=5)
	Delivery_cost=forms.DecimalField(label="Delivery Cost in LBP", max_digits=30, decimal_places=5)
	
class ViewClientForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(ViewClientForm, self).__init__(*args, **kwargs)
		for visible in self.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'
	client=forms.ModelChoiceField(required=True, widget=forms.Select, queryset=Client.objects.all())
	#date = forms.CharField(max_length=20)

class ViewDeliveryInForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(ViewDeliveryInForm, self).__init__(*args, **kwargs)
		for visible in self.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'
	delivery_in = forms.ModelChoiceField(required=True, widget=forms.Select, queryset=Delivery_In.objects.all())


class ViewDeliveryOutForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(ViewDeliveryOutForm, self).__init__(*args, **kwargs)
		for visible in self.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'
	delivery_out = forms.ModelChoiceField(required=True, widget=forms.Select, queryset=Delivery_Out.objects.all())




class LoginForm(forms.Form):
	def __init__(self,*args,**kwargs):
		super(LoginForm,self).__init__(*args,**kwargs)
		for visible in self.visible_fields():
			visible.field.widget.attrs['class']='form-control'
	passcode = forms.CharField(widget=forms.PasswordInput())

