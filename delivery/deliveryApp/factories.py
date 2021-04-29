import factory
from factory.django import DjangoModelFactory
from models import Client, Delivery_In, Delivery_Out, Manager

class ClientFactory(DjangoModelFactory):
	class Meta:
		model = Client

	Company= factory.Faker("name")
	Phone = factory.Faker("phone_number")
	Location = factory.Faker("location")

for i in range(10):
	c = ClientFactory()
	c.Name
	c.Phone
	c.Location
	print(c.Name)