from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .models import Bill,Client,Delivery_In,Delivery_Out, Viewer
from django.db import models
from django.utils import timezone
import dateutil
import datetime
import os
import PIL.Image as Image
from dateutil.relativedelta import relativedelta
from django.urls import reverse
import math
from .forms import LoginForm,ViewDeliveryOutForm, Delivery_OutForm,ViewClientForm, ViewDeliveryInForm, ClientForm, Delivery_InForm, BillForm
from datetime import date as DATE
from django.shortcuts import render
from django.shortcuts import get_object_or_404
import json
from django.http import HttpResponse
from django.views.generic.edit import UpdateView, DeleteView
import xlwt
from django.db.models import Q
import arabic_reshaper
from bidi.algorithm import get_display
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
def index(request, category='None', year=0, month=0, day=0, phone='0'):
	if request.method=='POST':

		if request.is_ajax():
			if request.POST.get("operation") == "done":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Bill_Id=bill_id)
				bill.Done=True
				bill.Date_Done=datetime.datetime.now()
				bill.save()
				block=bill.Bill_Id+"_notdone"
				remove1 = bill.Bill_Id+"_donebutton"
				remove2 = bill.Bill_Id+"_postponebutton"
				ctx = {'content_id':bill.Bill_Id, 'block':block, 'rem1':remove1, 'rem2':remove2}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "sent":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Bill_Id=bill_id)
				if (bill.Status == "pending"):
					bill.Status="sent"
					bill.Hidden_Status="sent"
					bill.Date_Sent = datetime.datetime.now()
					bill.delivery_out=Delivery_Out.objects.get(pk = request.POST.get("deliveryout",None))
					bill.save()
					Id=bill.Bill_Id+"_sentbutton"
					statusid = bill.Bill_Id+"_status"
					billid=bill.Bill_Id
					newId=bill.Bill_Id+"_paidbutton"
					ctx = {'content_id':bill.Bill_Id, 'Id':Id, 'newId':newId,'statusid':statusid, 'billid':billid}
					v = HttpResponse(json.dumps(ctx),content_type='application/json')
				else:
					v = HttpResponse(json.dumps({}),content_type='application/json')
				return v
			elif request.POST.get("operation") == "paid":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Bill_Id=bill_id)
				bill.Status="paid"
				bill.Date_Paid=datetime.datetime.now()
				bill.Hidden_Status="paid"
				bill.Date_Paid=datetime.datetime.now()
				bill.save()
				Id=bill.Bill_Id+"_paidbutton"
				statusid = bill.Bill_Id+"_status"
				billid=bill.Bill_Id
				ctx = {'content_id':bill.Bill_Id, 'Id':Id,'statusid':statusid, 'billid':billid}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v

		if(len(request.POST.get('requested_date',""))==0):
			datelist=[0,0,0]
		else:
			datelist=request.POST['requested_date'].split('-')

		if datelist[0]!=0 and year==0:
			year=int(datelist[0])
			month=int(datelist[1])
			day=int(datelist[2])

		phone=request.POST.get('requested_phone',"0")
		if phone == "All Phone Numbers":
			phone = "0"

	if year!=0:
		date=datetime.date(int(year),int(month),int(day))
	else:
		date='0-0-0'

	if date !='0-0-0':
	    pre_date = datetime.datetime(int(year),int(month),int(day),0,0,0)
	    post_date = datetime.datetime(int(year),int(month),int(day),23,59,55)
	    if category in ["paid","pending","sent"]:
	        lst = Bill.objects.filter( Q( Date_In__lt = post_date) & Q( Date_In__gt = pre_date) & Q(Status=category) )
	    else:
	        lst = Bill.objects.filter( Q( Date_In__lt = post_date) & Q( Date_In__gt = pre_date) )
	else:
	    if category == "paid":
	        lst = Bill.objects.all().filter(Status="paid")
	    elif category =="pending":
	        lst = Bill.objects.all().filter(Status="pending")
	    elif category == "sent":
	        lst = Bill.objects.all().filter(Status="sent")
	    elif category == "all":
	        lst = Bill.objects.all()
	    else:
	        lst = Bill.objects.filter(
	          (
	           Q(Done = False) & Q(Done_Refunding = False) ) | ( Q(Done=True) & Q(Status = 'sent') )
	            )





	if phone!='0':

		lst = lst.filter(endClientNumber__regex=rf'^[a-zA-Z0-9_]*{phone}+[a-zA-Z0-9]*')
	req_id = request.POST.get("requested_id","nothing")
	result = "nothing"
	if req_id != "nothing":
	    try:
	        #lst = [Bill.objects.get(Bill_Id = req_id)]
	        lst = Bill.objects.filter(Bill_Id__regex=rf'^[a-zA-Z0-9_]*{req_id}+[a-zA-Z0-9]*')
	        if len(lst) > 0:
	        	result = "Bill Found"
	        else:
	        	result = "Bill Not Found"
	    except:
	        lst=list()
	        result="Bill Not Found"
	user_list = lst
	page = request.POST.get('page', 1)
	paginator = Paginator(user_list, 55)
	try:
		users = paginator.page(page)
	except PageNotAnInteger:
		users = paginator.page(1)
	except EmptyPage:
		users = paginator.page(paginator.num_pages)

	return render(request, 'index.html', {'result':result, 'total':len(Bill.objects.all()),'bills':users,'pages':math.ceil(len(user_list)/55.0) ,'date':date, 'category':category, 'phone':phone, 'deliveryouts':Delivery_Out.objects.all()})



def bill_details(request, bill_id=0, status=0,date='0-0-0', category='all'):

	if request.method == "GET" and request.GET.get('id'):
		bill_id = request.GET.get('id')

		if not Bill.objects.filter(Bill_Id=bill_id).exists():
			return render(request,'thanks.html',{'Message': "Bill With Id "+bill_id+" Doesn't Exist :("})
	bill = Bill.objects.get(Bill_Id=bill_id)
	if bill.Hidden_Status == "refunded" and bill.Status!="refunded":
		bill.Done_Refunding=False
	if bill.Status != "refunded":
		bill.Done_Refunding = False
	if bill.Hidden_Status != "sent" and bill.Status=="sent":
		bill.Date_Sent = datetime.datetime.now()
	if bill.Hidden_Status != "paid" and bill.Status=="paid":
		bill.Date_Paid=datetime.datetime.now()
	if bill.Hidden_Status == 'paid' and bill.Status !="paid":
		bill.Extracted_For_DelOut = False
	if bill.Status == "pending":
		bill.Date_Sent = None
		bill.Done = False
		bill.Extracted_For_DelOut = False
		bill.delivery_out=Delivery_Out.objects.get(Name='Default')
	if bill.Status != "paid":
		#bill.Done=False
		#bill.Date_Done=None
		bill.Date_Paid = None
	if not bill.Done:
		bill.Date_Done = None
	if bill.Done and not bill.Date_Done:
		bill.Date_Done = datetime.datetime.now()
	#if bill.Hidden_Status == "paid" and bill.Status != "paid":
		#bill.Done=False
		#bill.Date_Done=None
	if bill.Hidden_Id != bill.Bill_Id:
	    Bill.objects.filter(Bill_Id=bill.Hidden_Id).delete()
	    bill.Hidden_Id=bill.Bill_Id
	bill.Hidden_Status=bill.Status
	bill.save()
	return render(request, 'bill_details.html', {'bill':bill})





def add_deliveryout(request):
	if request.method=='POST':
		form = Delivery_OutForm(request.POST)
		if form.is_valid():
			data=form.cleaned_data
			delivery_out=Delivery_Out()
			delivery_out.Name=data['Name']
			#delivery_out.Location=data['Location']
			delivery_out.Phone=data['Phone'].replace(" ","")
			delivery_out.save()
			return render(request,'thanks.html',{'Message': "Driver Out Added Successfully"})
	else:
		form=Delivery_OutForm()
	return render(request,'add_deliveryout.html',{'form':form})

def add_client(request):
	if request.method=='POST':
		form = ClientForm(request.POST)
		if form.is_valid():
			data=form.cleaned_data
			client=Client()
			#client.Name=data['Name']
			client.Location=data['Location']
			client.Phone=data['Phone'].replace(" ","")
			client.Company=data['Company'].replace("'","")
			try:
				client.save()
			except Exception as e:

				return render(request,'add_client.html',{'form':form, 'message':'Supplier Name Already Exists, choose another name.'})

			return render(request,'thanks.html',{'Message': "Client Added Successfully"})
	else:
		form=ClientForm()
	return render(request,'add_client.html',{'form':form, 'message':'nothing'})

def add_deliveryin(request):
	if request.method=='POST':
		form=Delivery_InForm(request.POST)
		if form.is_valid():
			data=form.cleaned_data
			deliveryin=Delivery_In()
			deliveryin.Name=data['Name']
			#deliveryin.Location=data['Location']
			deliveryin.Phone=data['Phone'].replace(" ","")
			#deliveryin.client=Client.objects.get(pk=data['client'])
			deliveryin.save()
			return render(request,'thanks.html',{'Message': "Delivery In Added Successfully"})
	else:
		form=Delivery_InForm()
	return render(request,'add_deliveryin.html',{'form':form})


def add_bill(request):
    message=""
    if request.method=='POST':
	    try:
	        bill=Bill()
	        bill.Bill_Id=str(request.POST['Id'])
	        bill.Date=datetime.datetime.now()
	        bill.Date_In=datetime.datetime.now()
	        bill.address=request.POST['address']
	        bill.delivery_in=Delivery_In.objects.get(Name='Default')
	        bill.delivery_out=Delivery_Out.objects.get(Name='Default')
	        bill.endClientName=request.POST['endClientName']
	        bill.endClientNumber=request.POST['endClientNumber'].replace(" ","")
	        bill.client=Client.objects.get(pk=request.POST['client'])
	        bill.Product_cost=request.POST['Product_cost']
	        bill.Delivery_cost=request.POST['Delivery_cost']
	        bill.status="pending"
	        bill.Currency = request.POST['Currency']
	        bill.Hidden_Status="pending"
	        print("beqlfvhwelbfwhlbfhwejbfhblwBHFOBFHWBHFLBWEHFBHL")

	        if (Bill.objects.filter(Bill_Id=request.POST['Id']).exists()):
	            return HttpResponse("<h1> A bill with <u><i><b>IDENTICAL ID </u></i></b> exists already in the database </h1>")
	        bill.save()
	        return render(request,'thanks.html',{'Message': "Bill Added Successfully"})
	    except:
	        message = "Some fields were missing or incorrectly filled, fill the form again"

    deliveryins = Delivery_In.objects.all()
    clients = Client.objects.all()
    return render(request,'add_bill.html',{'deliveryins':deliveryins,'clients':clients, 'message':message})



def client_details(request, pk ,year=0, month=0, day=0,year_2=0,month_2=0,day_2=0,bill_id=-1, operation='no operation'):	
	client = Client.objects.get(pk=pk)
	company = client.Company
	if request.method == 'POST':
		if request.is_ajax():
			if request.POST.get("operation") == "postpone":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				bill.Date += datetime.timedelta(days=1)
				bill.save()
				dt = str(bill.Date.date())
				block=bill.Bill_Id+"_item"
				if year!=0:
					remove=True
				else:
					remove=False
				ctx = {'content_id':bill.Bill_Id, 'new_date':dt, 'id':bill.Bill_Id+"_date", 'remove':remove, 'block':block}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "done":

				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Bill_Id=bill_id)
				bill.Date_Done=datetime.datetime.now()
				bill.Done=True

				bill.save()
				block=bill.Bill_Id+"_notdone"
				remove1 = bill.Bill_Id+"_donebutton"
				remove2 = bill.Bill_Id+"_postponebutton"
				ctx = {'content_id':bill.Bill_Id, 'block':block, 'rem1':remove1, 'rem2':remove2}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "done_refunding":

				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Bill_Id=bill_id)
				bill.Done_Refunding = True
				bill.Date_Sent = None
				bill.save()
				Id=bill.Bill_Id+"_donerefundingbutton"
				statusid = bill.Bill_Id+"_notdonerefunding"
				billid=bill.Bill_Id
				ctx = {'content_id':bill.Bill_Id, 'Id':Id,'statusid':statusid, 'billid':billid}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "sent":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Bill_Id=bill_id)
				if (bill.Status == "pending"):
					bill.Status="sent"
					bill.Hidden_Status="sent"
					bill.Date_Sent = datetime.datetime.now()
					bill.delivery_out=Delivery_Out.objects.get(pk = request.POST.get("deliveryout",None))
					bill.save()
					Id=bill.Bill_Id+"_sentbutton"
					statusid = bill.Bill_Id+"_status"
					billid=bill.Bill_Id
					newId=bill.Bill_Id+"_paidbutton"
					ctx = {'content_id':bill.Bill_Id, 'Id':Id, 'newId':newId,'statusid':statusid, 'billid':billid}
					v = HttpResponse(json.dumps(ctx),content_type='application/json')
				else:
					v = HttpResponse(json.dumps({}),content_type='application/json')
				return v
			elif request.POST.get("operation") == "paid":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Bill_Id=bill_id)
				bill.Status="paid"
				bill.Date_Paid=datetime.datetime.now()
				bill.Hidden_Status="paid"
				bill.save()
				Id=bill.Bill_Id+"_paidbutton"
				statusid = bill.Bill_Id+"_status"
				billid=bill.Bill_Id
				ctx = {'content_id':bill.Bill_Id, 'Id':Id,'statusid':statusid, 'billid':billid}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
	if bill_id!=-1:
		bill=Bill.objects.get(pk=bill_id)
		if operation == 'make sent':
			bill.Status='sent'
			bill.Hidden_Status='sent'
		elif operation == 'make paid':
			bill.Status='paid'
			bill.Date_Paid=datetime.datetime.now()
			bill.Hidden_Status='paid'
		elif operation == 'make done':
			bill.Done=True
			bill.Date_Done=datetime.datetime.now()
		elif operation == 'postpone':
			bill.Date += datetime.timedelta(days=1)
		bill.save()
		return HttpResponseRedirect(reverse('client_details', args=(company,year,month,day)))
	elif request.method=='POST':
		if( not request.POST.get('requested_date')):
			datelist=[0,0,0]
		else:
			datelist=request.POST['requested_date'].split('-')
		if datelist[0]!=0 and year==0:
			year=int(datelist[0])
			month=int(datelist[1])
			day=int(datelist[2])
		if (not request.POST.get('requested_date_2')):
			datelist_2 = [0,0,0]
		else:
			datelist_2 = request.POST['requested_date_2'].split('-')
		if datelist_2[0]!=0 and year_2==0:
			year_2=int(datelist_2[0])
			month_2=int(datelist_2[1])
			day_2=int(datelist_2[2])





	if year!=0:
		date=datetime.date(int(year),int(month),int(day))
	else:
		date='0-0-0'

	if year_2 !=0:
		date_2 = datetime.date(int(year_2), int(month_2), int(day_2))
	else:
		date_2 = '0-0-0'
	ids = request.POST.get('IDS',"")
	if len(str(ids)) > 0:
	    ids = ids.split('-')
	    client = Client.objects.get(pk=pk)
	    date = str(datetime.datetime.now()).split(' ')[0]
	    paid_rows=[]
	    for billid in ids:
	        temp = str(billid)
	        paid_rows.append(Bill.objects.get(Bill_Id = temp))
	    return generic_excel(company,client.Location, date,paid_rows, [] , 'Immediate Supplier Report')

	    
	lst = []
	if date == '0-0-0' and date_2 == '0-0-0':
		lst = Bill.objects.filter( Q(client = pk) & Q(Done = False) & Q(Done_Refunding = False) )
	elif date != '0-0-0' and date_2 != '0-0-0':
		pre_date = datetime.datetime(int(year), int(month), int(day), 23, 59, 56)
		post_date = datetime.datetime(int(year_2), int(month_2), int(day_2), 0, 0, 1)
		post_date += datetime.timedelta(days=1)
		pre_date += datetime.timedelta(days=-1)
		lst=Bill.objects.filter( Q( client = pk) & Q( Date_In__range = [pre_date, post_date] ) ) 
	elif date != '0-0-0':
	    pre_date = datetime.datetime(int(year), int(month), int(day), 23, 59, 56)
	    pre_date += datetime.timedelta(days=-1)
	    
	    lst=Bill.objects.filter( Q(client = pk) &  Q( Date_In__gt = pre_date) )
	else:
		post_date = datetime.datetime(int(year_2), int(month_2), int(day_2), 0, 0, 1)
		post_date += datetime.timedelta(days=1)
		lst=Bill.objects.filter( Q(client = pk) & Q( Date_In__lt = post_date ) )

	    

	lst_size = len(lst)
	client = Client.objects.get(Company = company)
	return render(request, 'client_details.html', {'size':lst_size,'client':client,'bills':lst, 'date':date,'date_2':date_2,  'company':company, 'deliveryouts':Delivery_Out.objects.all() })

def delivery_in_details(request, delivery_in_id ,year=0, month=0, day=0,bill_id=-1, operation='no operation'):
	if request.method == 'POST':
		if request.is_ajax():
			if request.POST.get("operation") == "postpone":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				bill.Date += datetime.timedelta(days=1)
				bill.save()
				dt = str(bill.Date.date())
				block=bill.Bill_Id+"_item"
				if year!=0:
					remove=True
				else:
					remove=False
				ctx = {'content_id':bill.Bill_Id, 'new_date':dt, 'id':bill.Bill_Id+"_date", 'remove':remove, 'block':block}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "done":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				bill.Date_Done=datetime.datetime.now()
				bill.Done=True
				bill.save()
				block=bill.Bill_Id+"_notdone"
				remove1 = bill.Bill_Id+"_donebutton"
				remove2 = bill.Bill_Id+"_postponebutton"
				ctx = {'content_id':bill.Bill_Id, 'block':block, 'rem1':remove1, 'rem2':remove2}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "done_refunding":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				bill.Done_Refunding = True
				bill.Date_Sent = None
				bill.save()
				Id=bill.Bill_Id+"_donerefundingbutton"
				statusid = bill.Bill_Id+"_notdonerefunding"
				billid=bill.Bill_Id
				ctx = {'content_id':bill.Bill_Id, 'Id':Id,'statusid':statusid, 'billid':billid}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "sent":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				if (bill.Status == "pending"):
					bill.Status="sent"
					bill.Hidden_Status="sent"
					bill.Date_Sent = datetime.datetime.now()
					bill.delivery_out=Delivery_Out.objects.get(pk = request.POST.get("deliveryout",None))
					bill.save()
					Id=bill.Bill_Id+"_sentbutton"
					statusid = bill.Bill_Id+"_status"
					billid=bill.Bill_Id
					newId=bill.Bill_Id+"_paidbutton"
					ctx = {'content_id':bill.Bill_Id, 'Id':Id, 'newId':newId,'statusid':statusid, 'billid':billid}
					v = HttpResponse(json.dumps(ctx),content_type='application/json')
				else:
					v = HttpResponse(json.dumps({}),content_type='application/json')
				return v
			elif request.POST.get("operation") == "paid":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				bill.Status="paid"
				bill.Date_Paid=datetime.datetime.now()
				bill.Hidden_Status="paid"
				bill.save()
				Id=bill.Bill_Id+"_paidbutton"
				statusid = bill.Bill_Id+"_status"
				billid=bill.Bill_Id
				ctx = {'content_id':bill.Bill_Id, 'Id':Id,'statusid':statusid, 'billid':billid}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
	if bill_id!=-1:
		bill=Bill.objects.get(pk=bill_id)
		if operation == 'make sent':
			bill.Status='sent'
			bill.Hidden_Status="sent"
		elif operation == 'make paid':
			bill.Status='paid'
			bill.Date_Paid=datetime.datetime.now()
			bill.Hidden_Status="paid"
		elif operation == 'make done':
			bill.Date_Done=datetime.datetime.now()
			bill.Done=True
		elif operation == 'postpone':
			bill.Date += datetime.timedelta(days=1)
		bill.save()
		return HttpResponseRedirect(reverse('delivery_in_details', args=(delivery_in_id,year,month,day)))
	elif request.method=='POST':
		if(not request.POST.get('requested_date')):
			datelist=[0,0,0]
		else:
			datelist=request.POST['requested_date'].split('-')
		if datelist[0]!="No Date Specified":
			year=int(datelist[0])
			month=int(datelist[1])
			day=int(datelist[2])
	lst = Bill.objects.all().filter(delivery_in=delivery_in_id)
	if year!=0:
		date=datetime.date(int(year),int(month),int(day))
	else:
		date='0-0-0'
	monthly_info=""
	ids = request.POST.get('IDS',"")
	if len(str(ids)) > 0:
	    ids = ids.split('-')
	    deliveryin = Delivery_In.objects.get(pk=delivery_in_id)
	    date = str(datetime.datetime.now()).split(' ')[0]
	    response = HttpResponse(content_type='application/ms-excel')
	    response['Content-Disposition'] = 'attachment; filename='+deliveryin.Name+"_immediate_"+str(date)+'.xls'
	    if '.xls' not in response['Content-Disposition']:
	        response['Content-Disposition'] = 'attachment; filename='+str(date)+'_immediate.xls'
	    wb = xlwt.Workbook(encoding='utf-8')
	    ws = wb.add_sheet('Immediate Delivery_In Report')
	    row_num = 0
	    font_style = xlwt.easyxf('font: bold on, color black;\
	    borders: top_color black, bottom_color black, right_color black, left_color black,\
	    left thin, right thin, top thin, bottom thin;\
	    pattern: pattern solid, fore_color white;align: horiz center;')
	    ws.write(0,2,'FST Delivery',font_style)
	    ws.write(1,2,'Driver In:',font_style)
	    ws.write(2,2,'Immediate Report Date:',font_style)
	    ws.write(1,3,deliveryin.Name)
	    ws.write(2,3,str(date))
	    columns = ['Id','Client', 'Region', 'EndClient','Phone Number', 'Product Cost', 'Delivery Cost', 'Status']
	    for col_num in range(len(columns)):
	        ws.write(4, col_num+1, columns[col_num], font_style)
	    paid_rows = []
	    for billid in ids:
	        temp = str(billid)
	        paid_rows.append(Bill.objects.get(Id = temp))

	    font_style = xlwt.XFStyle()
	    row_num=4
	    totalprodUSD=0
	    totalprodLBP=0
	    totaldel=0
	    font_style=xlwt.easyxf("pattern: pattern solid, fore_color white; font: color black; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,left thin, right thin, top thin, bottom thin;")
	    for row in paid_rows:
	        row_num += 1
	        if row.Currency == 'usd':
	        	totalprodUSD+=max(row.Product_cost,0)
	        else:
	        	totalprodLBP+=max(row.Product_cost,0)
	        totaldel+=row.Delivery_cost
	        ws.write(row_num,1,row.Id,font_style)
	        ws.write(row_num,2,row.client.Company,font_style)
	        ws.write(row_num,3,row.address,font_style)
	        ws.write(row_num,4,row.endClientName, font_style)
	        ws.write(row_num,5,row.endClientNumber,font_style)
	        if row.Currency == 'usd':
	        	ws.write(row_num,6,str(max(0,row.Product_cost)) + " $",font_style)
	        else:
	        	ws.write(row_num,6,str(max(0,row.Product_cost)) + " LL",font_style)
	        ws.write(row_num,7,str(row.Delivery_cost) + " LL",font_style)
	        state =""
	        if row.Status == 'refunded':
	            state = 'Refunded'
	        elif row.Status == 'paid':
	            state = 'Received'
	        elif row.Status == 'pending':
	            state = 'Pending'
	        elif row.Status == 'sent':
	            state = 'Sent'
	        ws.write(row_num,8,state,font_style)
	    font_style = xlwt.easyxf('font: bold on, color black;\
	    borders: top_color black, bottom_color black, right_color black, left_color black,\
	    left thin, right thin, top thin, bottom thin;\
	    pattern: pattern solid, fore_color yellow;align: horiz center;')
	    row_num+=1
	    ws.write(row_num,7,'Total Product Cost:',font_style)
	    ws.write(row_num,8,str(totalprodLBP)+' L.L + '+ str(totalprodUSD)+ " $", font_style)
	    row_num+=1
	    ws.write(row_num,7,'Total Delivery Cost:',font_style)
	    ws.write(row_num,8,str(totaldel)+' L.L', font_style)
	    row_num+=1
	    ws.write(row_num,7,'Total Combined Cost:',font_style)
	    ws.write(row_num,8,str(totalprodLBP+totaldel)+' L.L + '+ str(totalprodUSD)+ " $", font_style)
	    wb.save(response)
	    return(response)
	if date != '0-0-0':
	    pre_date = datetime.datetime(int(year), int(month), 1, 0, 0, 1)
	    post_date = datetime.datetime(int(year), int(month), 1, 0, 0, 1)
	    post_date += relativedelta(months=1)
	    monthly_info = len(Bill.objects.filter( Q(delivery_in = delivery_in_id) & Q( Date_In__lt = post_date ) & Q( Date_In__gt = pre_date) ) )
	delivery_in=Delivery_In.objects.get(pk=delivery_in_id)
	return render(request, 'delivery_in_details.html', {'monthly_info':monthly_info, 'bills':lst, 'date':date, 'delivery_in':delivery_in, 'deliveryouts':Delivery_Out.objects.all()})


def delivery_out_details(request, delivery_out_id ,year=0, month=0, day=0,bill_id=-1, operation='no operation'):
	if request.method == 'POST':
		if request.is_ajax():
			print("REACHED")
			if request.POST.get("operation") == "done_refunding":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Bill_Id=bill_id)
				bill.Done_Refunding = True
				bill.Date_Sent = None
				bill.save()
				Id=bill.Bill_Id+"_donerefundingbutton"
				statusid = bill.Bill_Id+"_notdonerefunding"
				billid=bill.Bill_Id
				ctx = {'content_id':bill.Bill_Id, 'Id':Id,'statusid':statusid, 'billid':billid}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "done":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Bill_Id=bill_id)
				bill.Date_Done=datetime.datetime.now()
				bill.Done=True
				bill.save()
				block=bill.Bill_Id+"_notdone"
				remove1 = bill.Bill_Id+"_donebutton"
				remove2 = bill.Bill_Id+"_postponebutton"
				ctx = {'content_id':bill.Bill_Id, 'block':block, 'rem1':remove1, 'rem2':remove2}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "sent":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Bill_Id=bill_id)
				if (bill.Status == "pending"):
					bill.Status="sent"
					bill.Hidden_Status="sent"
					bill.Date_Sent = datetime.datetime.now()
					bill.delivery_out=Delivery_Out.objects.get(pk = request.POST.get("deliveryout",None))
					bill.save()
					Id=bill.Bill_Id+"_sentbutton"
					statusid = bill.Bill_Id+"_status"
					billid=bill.Bill_Id
					newId=bill.Bill_Id+"_paidbutton"
					ctx = {'content_id':bill.Bill_Id, 'Id':Id, 'newId':newId,'statusid':statusid, 'billid':billid}
					v = HttpResponse(json.dumps(ctx),content_type='application/json')
				else:
					v = HttpResponse(json.dumps({}),content_type='application/json')
				return v
			elif request.POST.get("operation") == "paid":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Bill_Id=bill_id)
				bill.Status="paid"
				bill.Date_Paid=datetime.datetime.now()
				bill.Hidden_Status="paid"
				bill.save()
				Id=bill.Bill_Id+"_paidbutton"
				statusid = bill.Bill_Id+"_status"
				billid=bill.Bill_Id
				ctx = {'content_id':bill.Bill_Id, 'Id':Id,'statusid':statusid, 'billid':billid}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
	if bill_id!=-1:
		bill=Bill.objects.get(pk=bill_id)
		if operation == 'make sent':
			bill.Status='sent'
			bill.Hidden_Status='sent'
		elif operation == 'make paid':
			bill.Status='paid'
			bill.Date_Paid=datetime.datetime.now()
			bill.Hidden_Status='paid'
		elif operation == 'make done':
			bill.Done=True
			bill.Date_Done=datetime.datetime.now()
		elif operation == 'postpone':
			bill.Date += datetime.timedelta(days=1)
		bill.save()
		return HttpResponseRedirect(reverse('delivery_out_details', args=(delivery_out_id,year,month,day)))
	elif request.method=='POST':
		if( not request.POST.get('requested_date')):
			datelist=[0,0,0]
		else:
			datelist=request.POST['requested_date'].split('-')
		if datelist[0]!=0 and year==0:
			year=int(datelist[0])
			month=int(datelist[1])
			day=int(datelist[2])





	if year!=0:
		date=datetime.date(int(year),int(month),int(day))
	else:
		date='0-0-0'
	monthly_info=""
	ids = request.POST.get('IDS',"")
	if len(str(ids)) > 0:
	    ids = ids.split('-')
	    deliveryout = Delivery_Out.objects.get(pk=delivery_out_id)
	    date = str(datetime.datetime.now()).split(' ')[0]
	    paid_rows = []
	    for billid in ids:
	        temp = str(billid)
	        paid_rows.append(Bill.objects.get(Bill_Id = temp))

	    return generic_excel(deliveryout.Name, "---", date, paid_rows, [] , 'Immediate Driver Out Report')

	lst = list()
	if date != '0-0-0':
	    pre_date = datetime.datetime(int(year), int(month), 1, 0, 0, 1)
	    post_date = datetime.datetime(int(year), int(month), 1, 0, 0, 1)
	    post_date += relativedelta(months=1)
	    monthly_info = len(Bill.objects.filter( Q(delivery_out = delivery_out_id) & Q( Date_Sent__lt = post_date ) & Q( Date_Sent__gt = pre_date) ) )
	    pre_date = datetime.datetime(int(year), int(month),int(day),23,59,55)
	    post_date = datetime.datetime(int(year), int(month),int(day),0,0,1)
	    pre_date += datetime.timedelta(days=-1)
	    post_date += datetime.timedelta(days=1)
	    lst = Bill.objects.filter(
	        Q(delivery_out = delivery_out_id) & Q(Date_Sent__lt = post_date) & Q(Date_Sent__gt = pre_date)
	        )
	else:
	    	lst = Bill.objects.filter(Q(delivery_out=delivery_out_id) & ~Q(Extracted_For_DelOut = True))
#	return HttpResponse(len(lst))
	delivery_out=Delivery_Out.objects.get(pk=delivery_out_id)
	return render(request, 'delivery_out_details.html', {'monthly_info':monthly_info,'bills':lst, 'date':date, 'delivery_out':delivery_out, 'deliveryouts':Delivery_Out.objects.all()})



def get_bill_format(bill):
	n="<br>"
	h="<hr>"
	if bill.Status == "refunded":
		string = "Bill Id: " + bill.Bill_Id +n+"End-Client Name: "+bill.endClientName+n+"End-Client Phone Number: "+bill.endClientNumber +n + "Address: " + bill.address+n+"Status: "+bill.Status+n+"Done Refunding: "
		if bill.Done_Refunding:
			string = string + "Yes" + n
		else:
			string = string + "No" + n
		"Date Done: "+str(bill.Date).split(' ')[0]+n+"Date In: "+str(bill.Date_In).split(' ')[0]+n
		string = string +"Product Cost: "+str(bill.Product_cost)+n+h
		return str(string)
	string = "Bill Id: " + bill.Bill_Id +n+"End-Client Name: "+bill.endClientName+n+"End-Client Phone Number: "+bill.endClientNumber +n + "Address: " + bill.address+n+"Status: "+bill.Status+n+"Date Done: "+str(bill.Date).split(' ')[0]+n+"Date In: "+str(bill.Date_In).split(' ')[0]+n
	string = string +"Product Cost: "+str(bill.Product_cost)+n+h
	return str(string)

def extract_client_report(request,pk):
	client = Client.objects.get(pk=pk)
	company=client.Company
	date = str(datetime.datetime.now()).split(' ')[0]
	paid_rows = Bill.objects.filter(
		Q(client = pk) &  ~Q(Done = True) & Q(Status = 'paid'))
	for row in paid_rows:
		row.Date_Done=datetime.datetime.now()
		row.Done=True
	temp_paid_rows = paid_rows
	paid_rows = Bill.objects.filter(
		Q(client = pk) &  ~Q(Done_Refunding = True) & Q(Status = 'refunded'))
	for row in paid_rows:
		row.Done_Refunding=True
	try:
		result = generic_excel(company, client.Location, date, temp_paid_rows, paid_rows, 'Supplier Report')
	except Exception as e:
		return HttpResponse("An error occured: " + str(e))
	for elem in temp_paid_rows:
		elem.save()
	for elem in paid_rows:
		elem.save()
	return result

		




def extract_delivery_out_report(request,id):
	deliveryout = Delivery_Out.objects.get(pk=id)
	date = str(datetime.datetime.now()).split(' ')[0]
	paid_rows = Bill.objects.filter(
		Q( delivery_out = id) & Q(Status = 'paid') & Q(Extracted_For_DelOut = False) )

	
	for row in paid_rows:
		row.Extracted_For_DelOut=True
	
	try:
		response = generic_excel(deliveryout.Name,"---", date, paid_rows,[],'Driver Out Report')
	except Exception as e:
		return HttpResponse("An error has occured "+str(e))
	for row in paid_rows:
		row.save()
	return(response)


def extract_all_data(request,year=0,month=0,day=0):
	pre_date = datetime.datetime(int(year), int(month), int(day), 23, 59, 59)
	post_date = datetime.datetime(int(year), int(month), int(day), 0, 0, 1)
	pre_date += datetime.timedelta(days=-1)
	post_date += datetime.timedelta(days=1)
	date  = datetime.date(int(year),int(month),int(day))
	bills1 = Bill.objects.filter(
		Q(Status = 'paid') & Q(Date_Paid__lt = post_date) & Q(Date_Paid__gt = pre_date)
		)

	bills2 = Bill.objects.filter(
		Q(Date_In__lt = post_date) & Q(Date_In__gt = pre_date)
	  )
	try:
		response = generic_excel('Daily Report', '---', date, bills1, bills2, 'Daily Report')
	except Exception as e:
		return HttpResponse("An error has occured "+str(e))
	return response

def find_client(request):
	if request.method == 'POST':
	    client=request.POST.get("client")
	    return HttpResponseRedirect(reverse('client_details',args=(client,)))
	clients = Client.objects.all()
	return render(request,'find_client.html',{'clients':clients})

def find_delivery_in(request):
	if request.method == 'POST':
	    delivery_in = request.POST.get("deliveryin")
	    return HttpResponseRedirect(reverse('delivery_in_details',args=(delivery_in,)))
	deliveryins = Delivery_In.objects.all()
	return render(request,'find_delivery_in.html',{'deliveryins':deliveryins})


def find_delivery_out(request):
	if request.method == 'POST':
		delivery_out = request.POST.get("deliveryout")
		#return HttpResponse(delivery_out)
		return HttpResponseRedirect(reverse('delivery_out_details',args=(delivery_out,)))
	else:
		deliveryouts=Delivery_Out.objects.all()
	return render(request,'find_delivery_out.html',{'deliveryouts':deliveryouts})


def request_extract_all_data(request):
	if request.method == 'POST':
		data=request.POST
		date=data['date']
		if (len(date)==0):
			date="0-0-0"
		date=date.split('-')
		year=date[0]
		month=date[1]
		day=date[2]
		return HttpResponseRedirect(reverse('extract_all_data',args=(year,month,day)))
	return render(request,'extract_all_data.html')


def request_extract_system_log(request):
	if request.method == 'POST':
		data=request.POST
		date=data['date']
		if (len(date)==0):
			date="0-0-0"
		date=date.split('-')
		year=date[0]
		month=date[1]
		day=date[2]
		return HttpResponseRedirect(reverse('extract_system_log',args=(year,month,day)))
	return render(request,'extract_system_log.html')


class BillUpdate(UpdateView):
    model = Bill
    fields = ['Bill_Id','Date_In','Date_Sent', 'Done', 'address','delivery_out','endClientName','endClientNumber','client','Currency','Product_cost','Delivery_cost','Status','Extracted_For_DelOut','Done_Refunding']
    #template_name_suffix = '_update'
    def form_valid(self, form):
        bill = form.save(commit=False)
        if bill.Bill_Id != bill.Hidden_Id and (Bill.objects.filter(Bill_Id=bill.Bill_Id).exists()):
        	return HttpResponse("<h1> A bill with <u><i><b>IDENTICAL ID "+bill.Bill_Id+" </u></i></b> exists already in the database </h1>")
        bill.save()
        return HttpResponseRedirect(reverse('bill_details',args=(str(bill.Bill_Id),bill.Status)))

class ClientUpdate(UpdateView):
    model = Client
    fields = ['Company','Phone','Location']

class Delivery_OutUpdate(UpdateView):
    model = Delivery_Out
    fields = '__all__'

class Delivery_InUpdate(UpdateView):
    model = Delivery_In
    fields = '__all__'


class BillDelete(DeleteView):
    model = Bill
    success_url ="/confirm_delete/"

def deletionComplete(request):
	return render(request, 'thanks.html', {'Message':'Deletion Performed Successfully'})

class ClientDelete(DeleteView):
    model = Client
    success_url ="/confirm_delete/"

class DeliveryInDelete(DeleteView):
    model = Delivery_In
    success_url ="/confirm_delete/"

class DeliveryOutDelete(DeleteView):
    model = Delivery_Out
    success_url ="/confirm_delete/"

def generic_excel(name, location, date, first_list, second_list= [], sheet_name="sheet"):
	response = HttpResponse(content_type='application/ms-excel')
	response['Content-Disposition'] = 'attachment; filename='+name+"_"+str(date)+'.xls'
	if '.xls' not in response['Content-Disposition']:
		response['Content-Disposition'] = 'attachment; filename='+str(date)+'.xls'
	wb = xlwt.Workbook(encoding='utf-8')
	ws = wb.add_sheet(sheet_name)
	ws.col(0).width = 4500
	ws.row(11).height_mismatch = True
	ws.row(12).height_mismatch = True
	ws.row(13).height_mismatch = True
	ws.row(15).height_mismatch = True
	ws.row(11).height=400
	ws.row(12).height=400
	ws.row(13).height=400
	if sheet_name == 'Daily Report':
		ws.row(16).height_mismatch = True
		ws.row(16).height = 800
	else:
		ws.row(15).height=800
	ws.col(1).width=4500
	ws.col(2).width=5500
	ws.col(3).width=5000
	ws.col(4).width=5000
	ws.col(5).width=4800
	ws.col(6).width=4800
	ws.col(7).width=4800
	ws.col(8).width=3800
	row_num = 11
	font_style = xlwt.easyxf('font: bold on, color black;\
		borders: top_color black, bottom_color black, right_color black, left_color black,\
		left thick, right thick, top thick, bottom thick;\
		pattern: pattern solid, fore_color white;align: horiz center; align: vert center')
	ws.insert_bitmap(os.path.join(os.path.dirname(__file__), 'logo.bmp'),0,0,0,0,0.6,0.25)
	ws.write(11,0,'Name:',xlwt.easyxf('font:bold on, color black;'))
	ws.write(12,0,'Address:',xlwt.easyxf('font:bold on, color black;'))
	ws.write(13,0,'Date:',xlwt.easyxf('font:bold on, color black;'))
	ws.write(11,1,name,xlwt.easyxf('font:bold on, color black;'))
	ws.write(12,1,location,xlwt.easyxf('font:bold on, color black;'))
	ws.write(13,1,str(date))
	columns = ['Order #', 'Date', 'Recepient Name', 'Region', 'Phone Number', 'Order Amount', 'Delivery Charge', 'Total', 'Status']
	row_num = 15
	if sheet_name == 'Daily Report':
		ws.write(row_num,0,"Paid Orders", font_style)
		row_num+=1
	for col_num in range(len(columns)):
		ws.write(row_num, col_num, columns[col_num], font_style)
	paid_rows = first_list
	
	font_style = xlwt.XFStyle()
	row_num +=1
	total=0
	font_style=xlwt.easyxf("pattern: pattern solid, fore_color white; font: color black; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,left thin, right thin, top thin, bottom thin; align: vert center")
	for row in paid_rows:
		ws.row(row_num).height_mismatch = True
		ws.row(row_num).height=400
		ws.write(row_num,0,row.Bill_Id,font_style)
		ws.write(row_num,1,str(row.Date_In).split(' ')[0], font_style)
		ws.write(row_num,2,row.endClientName,font_style)
		ws.write(row_num,3,row.address,font_style)
		ws.write(row_num,4,row.endClientNumber, font_style)
		ws.write(row_num,5,str(row.Product_cost) + " LL",font_style)
		ws.write(row_num,6,str(row.Delivery_cost)+" LL" ,font_style)
		ws.write(row_num,7,str(row.Product_cost-row.Delivery_cost)+" LL" ,font_style)
		total += row.Product_cost-row.Delivery_cost
		state =""
		if row.Status == 'refunded':
			state = 'Refunded'
		elif row.Status == 'paid':
			state = 'Received'
		elif row.Status == 'pending':
			state = 'Pending'
		elif row.Status == 'sent':
			state = 'Sent'
		ws.write(row_num,8,state,font_style)
		row_num+=1
	row_num+=2
	font_style = xlwt.easyxf('font: bold on, color black;\
		borders: top_color black, bottom_color black, right_color black, left_color black,\
		left thick, right thick, top thick, bottom thick;\
		pattern: pattern solid, fore_color white;align: horiz center; align: vert center')

	ws.write_merge(row_num,row_num,7,8,'TOTAL '+str(total) + ' LBP',font_style)
	row_num+=3

	paid_rows = second_list

	if len(paid_rows):
		if sheet_name == 'Daily Report':
			ws.write(row_num,0,"In - Orders", font_style)
			row_num+=1
		ws.row(row_num).height_mismatch = True
		ws.row(row_num).height=800

	columns = ['Order #', 'Date', 'Recepient Name', 'Region', 'Phone Number', 'Order Amount', 'Delivery Charge', 'Total', 'Status']
	
	for col_num in range(len(columns)):
		if len(paid_rows)>0:
			ws.write(row_num, col_num, columns[col_num], font_style)
	
	
	font_style = xlwt.XFStyle()
	
	total=0
	row_num+=1
	font_style=xlwt.easyxf("pattern: pattern solid, fore_color white; font: color black; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,left thin, right thin, top thin, bottom thin; align: vert center")
	for row in paid_rows:
		ws.row(row_num).height_mismatch = True
		ws.row(row_num).height=400
		ws.write(row_num,0,row.Bill_Id,font_style)
		ws.write(row_num,1,str(row.Date_In).split(' ')[0], font_style)
		ws.write(row_num,2,row.endClientName,font_style)
		ws.write(row_num,3,row.address,font_style)
		ws.write(row_num,4,row.endClientNumber, font_style)
		ws.write(row_num,5,str(row.Product_cost) + " LL",font_style)
		ws.write(row_num,6,str(row.Delivery_cost)+" LL" ,font_style)
		ws.write(row_num,7,str(row.Product_cost-row.Delivery_cost)+" LL" ,font_style)
		total += row.Product_cost-row.Delivery_cost
		state =""
		if row.Status == 'refunded':
			state = 'Refunded'
		elif row.Status == 'paid':
			state = 'Received'
		elif row.Status == 'pending':
			state = 'Pending'
		elif row.Status == 'sent':
			state = 'Sent'
		ws.write(row_num,8,state,font_style)
		row_num+=1
	row_num+=2
	font_style = xlwt.easyxf('font: bold on, color black;\
		borders: top_color black, bottom_color black, right_color black, left_color black,\
		left thick, right thick, top thick, bottom thick;\
		pattern: pattern solid, fore_color white;align: horiz center; align: vert center')
	ws.row(4).height_mismatch = True
	ws.row(4).height = 500
	if len(paid_rows)>0:
		ws.write_merge(row_num,row_num,7,8,'TOTAL '+str(total) + ' LBP',font_style)
	ws.row(4).height_mismatch = True
	ws.row(4).height = 500
	font_style = xlwt.easyxf('font: bold 1 ; font: height 400, color black;pattern: pattern solid, fore_color white;align: horiz center; align: vert center')
	ws.write_merge(4,4,5,6, 'Statement of A/C',font_style )
	wb.save(response)
	return(response)

