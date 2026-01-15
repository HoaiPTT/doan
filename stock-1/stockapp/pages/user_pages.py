from django.shortcuts import render, redirect

def login(request):
    return render(request, 'user/login.html')

def home(request):
    return render(request, 'user/home.html')

def stock_detail(request):
    symbol = request.GET.get('symbol')  
    return render(request, 'user/stock_detail.html', {"symbol": symbol})


def personal(request):
    return render(request, 'user/personal.html')

def news(request):
    return render(request, 'user/news.html')

def register(request):
    return render(request, 'user/register.html')

def company(request):
    return render(request, 'user/company.html')

def stocks(request):
    return render(request, 'user/stocks.html')

def subscription(request):
    return render(request, 'user/subscription.html')
