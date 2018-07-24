from django.shortcuts import render, redirect
import bcrypt
from .models import *
from django.contrib import messages
import requests
import datetime
now = datetime.datetime.now()

def home(request):
	if 'id' not in request.session:
		request.session['id'] = 0
	return render(request, 'home.html')

def register_page(request):

	return render(request, 'register.html', )

def register(request):
	errors = User.objects.validator(request.POST)
	if len(errors):
		for key, value in errors.items():
			messages.error(request, value)
		return redirect('/register_page/')
	else:
		hashpw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
		User.objects.create(
			nickname = request.POST['nickname'],
			email = request.POST['email'],
			password = hashpw
			)
		ID = User.objects.get(email = request.POST['email']).__dict__['id']
		request.session['id'] = ID
		print('redirect to create page')
		return redirect('/create/')


def login(request):
	errors = User.objects.login_validator(request.POST)
	if len(errors):
		print('error')
		for key, value in errors.items():
			messages.warning(request, value)
		return redirect('/')
	else:
		print('get email')
		user = User.objects.filter(email = request.POST['email'])
		if user :
			if bcrypt.checkpw(request.POST['password'].encode(), user[0].password.encode()) == False:
				print("invalid")
				messages.warning(request, "invalid Email or Password")
				return redirect('/')
			else:
				print('pass')
				request.session['id'] = user[0].id
				if User.objects.get(id = request.session['id']).has_truck == False:
					print('redirect to create page')
					return redirect('/create/')

				print('redirect to dash')
				return redirect('/dashboard/')
		else:
			messages.warning(request,"invalid Email or Password")
			return redirect('/')
	

def create(request):
	return render(request, 'create.html', {'locations': Location.objects.all()})

def create_truck(request):
	Truck.objects.create(
		name = request.POST['name'],
		owner = User.objects.get(id = request.session['id']),
		location = Location.objects.get(id=request.POST['location'])
		)
	this_user = User.objects.get(id = request.session['id'])
	this_user.has_truck = True
	this_user.save()
	return redirect('/dashboard/')

def dashboard(request):
	api_key = 'b913e1d2697f85dea1f1bd5adf0a07da'
	url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid='+ api_key
	city = 'Seattle'
	city_weather = requests.get(url.format(city)).json()
	context = {
        'city' : User.objects.get(id=request.session['id']).trucks.first().location.location_name,
        'temperature' : city_weather['main']['temp'],
        'description' : city_weather['weather'][0]['description'],
        'icon' : city_weather['weather'][0]['icon'],
		'date' : now.strftime("%Y/%m/%d")
    }
	return render(request, 'dashboard.html', context)


def logout(request):
	request.session.clear()

	return redirect('/')

def buy_menu(request):
	return render(request, 'buy.html', {'ingredients': Ingredient.objects.all(), 'user':User.objects.get(id=request.session['id'])})

def tools(request):
	return render(request, 'tools.html', {'ingredients':Ingredient.objects.all(), 'products':Product.objects.all()})

def add_ingredient(request):
	Ingredient.objects.create(ingredient_name=request.POST['ingredient_name'], ingredient_type=request.POST['ingredient_type'], description=request.POST['desc'], buy_price=request.POST['buy_price'])
	return redirect('/tools')

def add_product(request):
	target = Product(product_name=request.POST['product_name'])
	target.product_type = request.POST['product_type']
	target.description = request.POST['desc']
	target.sell_price = request.POST['sell_price']
	if request.POST['ingredient_B'] == '':
		target.ingredient_B = None
	else:
		target.ingredient_B = Ingredient.objects.get(id=int(request.POST['ingredient_B']))
	if request.POST['ingredient_C'] == '':
		target.ingredient_C = None
	else:
		target.ingredient_C = Ingredient.objects.get(id=int(request.POST['ingredient_C']))
	if request.POST['ingredient_D'] == '':
		target.ingredient_D = None
	else:
		target.ingredient_D = Ingredient.objects.get(id=int(request.POST['ingredient_D']))
	target.ingredient_A = Ingredient.objects.get(id=int(request.POST['ingredient_A']))



	target.save()
	
	return redirect('/tools')

def buy_ingredient(request):
	target = Ingredient.objects.get(id=request.POST['id'])
	user = User.objects.get(id=request.session['id'])
	if user.fund - target.buy_price > 0:
		target.stock += 1
		user.fund -= target.buy_price
		target.save()
		user.save()	
	else:
		print('not enough fund')
		messages.warning(request,"Not enough money!")

	return redirect('/shopping_list')

def cook(request):
	return render(request, 'cook.html' , {'products':Product.objects.all(), 'ingredients':Ingredient.objects.all()})

def make_food(request):
	target = Product.objects.get(id=request.POST['id'])
	target.stock += 1
	if target.ingredient_A.stock-1 == -1:
		messages.warning(request,"Not enough ingredients!")
		return redirect('/cook')
	else:
		target.ingredient_A.stock -=1
		target.ingredient_A.save()

	
	if target.ingredient_B != None:
		if target.ingredient_B.stock-1 == -1:
			messages.warning(request,"Not enough ingredients!")
			return redirect('/cook')
		else:
			target.ingredient_B.stock -=1
			target.ingredient_B.save()
	
	if target.ingredient_C != None:
		if target.ingredient_B.stock-1 == -1:
			messages.warning(request,"Not enough ingredients!")
			return redirect('/cook')
		else:
			target.ingredient_C.stock -=1
			target.ingredient_C.save()
	
	if target.ingredient_D != None:
		if target.ingredient_B.stock-1 == -1:
			messages.warning(request,"Not enough ingredients!")
			return redirect('/cook')
		else: 
			target.ingredient_D.stock -=1
			target.ingredient_D.save()
	
	target.save()
	return redirect('/cook')

def sell(request):
	revenue = 0
	targets = Product.objects.exclude(stock = 0)
	user = User.objects.get(id=request.session['id'])
	for target in targets:
		print(target.product_name)
		revenue = target.stock * target.sell_price
		target.stock = 0
		target.save()
		user.fund += revenue

	user.save()
	return redirect('/dashboard')