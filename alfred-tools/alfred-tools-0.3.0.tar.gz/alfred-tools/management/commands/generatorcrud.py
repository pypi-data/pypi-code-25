from django.core.management.base import BaseCommand, CommandError
from django.apps import apps

class Command(BaseCommand):
	help = 'Generator Crud'

	def add_arguments(self, parser):
		parser.add_argument('model', nargs='+', type=str)

	def handle(self, *args, **options):
		model = options['model'][0]
		VAR = input("Input New Model Crud: ")
		f = open("apps/" + model + '/views.py', 'a')
		VAR0 = VAR.upper()
		VAR1 = VAR.capitalize()
		VAR2 = VAR.lower()
		 
		func1 = ('''
#####################################
##  VIEWS MODULE VAR0              ## 
#####################################   
@login_required(login_url='loginView')
def listVAR1Dashboard(request):
	list_VAR2 = VAR1.objects.all()
	data = {
		"list_VAR2":list_VAR2,
	}
	return render(request,'listVAR1Dashboard.html',data)
		''').replace("VAR1",VAR1).replace("VAR2",VAR2).replace("VAR0",VAR0)


		func2 = (''' 

@login_required(login_url='loginView')
def createVAR1Dashboard(request):
	if request.POST:
		form = createVAR1Form(request.POST,request.FILES)
		if form.is_valid():
			f= form.save(commit=False)
			f.save()
			return redirect('listVAR1Dashboard')
		else:
			form = createVAR1Form()
			data = {        
			"form":form,
			}
			return render(request,"createVAR1Dashboard.html",data)
	else:
		form = createVAR1Form()
		data = {
		"form":form,
		}
		return render(request,"createVAR1Dashboard.html",data)
		''').replace("VAR1",VAR1).replace("VAR2",VAR2)


		func3 = ('''

@login_required(login_url='loginView')
def updateVAR1Dashboard(request,pk):
	VAR2_to_update = VAR1.objects.get(pk=pk)
	if request.POST:
		form = updateVAR1Form(request.POST,request.FILES,instance=VAR2_to_update)
		if form.is_valid():
			form.save()
			return redirect('listVAR1Dashboard')
		else:
			form = updateVAR1Form(instance=VAR2_to_update)
			data = {            
				"form":form,
			}
			return render(request,"updateVAR1Dashboard.html",data)
	else:
		form = updateVAR1Form(instance=VAR2_to_update)
		data = {         
		"form":form,
		}
		return render(request,"updateVAR1Dashboard.html",data)

		''').replace("VAR1",VAR1).replace("VAR2",VAR2)


		func4 = ('''

@login_required(login_url='loginView')
def deleteVAR1Dashboard(request,pk):
	delete_to_VAR2 = VAR1.objects.get(pk=pk)
	delete_to_VAR2.delete()
	return redirect('listVAR1Dashboard')
		 
		''').replace("VAR1",VAR1).replace("VAR2",VAR2)


		func5 = (''' 

@login_required(login_url='loginView')
def viewVAR1Dashboard(request,pk):
	VAR2 = VAR1.objects.get(pk=pk)
	data = { 
		"VAR2":VAR2,
	}
	return render(request,'viewVAR1Dashboard.html',data)
		''').replace("VAR1",VAR1).replace("VAR2",VAR2)

		f.write(func1)
		f.write(func2)
		f.write(func3)
		f.write(func4)
		f.write(func5)
		f.close()

		w1 = ("apps/" + model + "/templates/listVAR1Dashboard.html").replace("VAR1",VAR1)
		w2 = ("apps/" + model + "/templates/createVAR1Dashboard.html").replace("VAR1",VAR1)
		w3 = ("apps/" + model + "/templates/updateVAR1Dashboard.html").replace("VAR1",VAR1)
		w4 = ("apps/" + model + "/templates/viewVAR1Dashboard.html").replace("VAR1",VAR1)

		f1 = open(w1,"w+")
		f2 = open(w2,"w+")
		f3 = open(w3,"w+")
		f4 = open(w4,"w+")