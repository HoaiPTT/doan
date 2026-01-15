from django.shortcuts import render, redirect

def login_admin(request):
    return render(request, 'admin/login-admin.html')

def admin_home(request):
    return render(request, 'admin/home-admin.html')

def manage_user(request):
    return render(request, 'admin/manage_user.html')

def manage_company(request):
    return render(request, 'admin/manage_company.html')

def manage_stock(request):
    return render(request, 'admin/manage_stock.html')

def manage_news(request):
    return render(request, 'admin/manage_news.html')