from django.urls import path
from . import views

urlpatterns = [
    # ---------- USER PAGE ----------
    path('user/login/', views.login, name='login_page'),
    path('user/register/', views.register, name='register'),
    path('user/home/', views.home, name='home'),
    path('user/stocks/', views.stocks, name='stocks'),
    path('user/stock_detail/', views.stock_detail, name='stock_detail'),
    path('user/personal/', views.personal, name='personal'),
    path('user/company/', views.company, name='company'),
    path('user/news/', views.news, name='news'),
    path('user/subscription/', views.subscription, name='subscription'),

    # ---------- USER API ----------
    path('api/login/', views.api_login, name='api_login'),
    path('api/register/', views.api_register, name='api_register'),
    path('api/userinfo/', views.api_user_info, name='api_user_info'),
    path('api/company/', views.get_company_info, name='get_company_info'),
    path('api/comp/', views.insert_company, name='in-com'),
    path("api/stocks/", views.get_stock, name="get_stock"),
    path("api/stock_detail/", views.get_stock_detail, name="get_stock_detail"),
    path('api/company/', views.get_company_profile, name='get_company_profile'),
    path('get_list_news_user/', views.get_list_news_user, name='get_list_news_user'),
    path("callback/", views.callback, name="callback"),
    # Watchlist API
    path("api/watchlist/", views.get_watchlist, name="get_watchlist"),
    path("api/watchlist/add/", views.add_to_watchlist, name="add_to_watchlist"),
    path("api/watchlist/remove/", views.remove_from_watchlist, name="remove_from_watchlist"),

    path("api/payment/zalopay/", views.zalo_payment, name="zalo_payment"),
    path("api/payment/status/", views.check_payment_status, name="check_payment_status"),
    path("api/subscription/history/", views.subscription_history, name="subscription_history"),
    path("api/user/change_password/", views.change_password, name="change_password"),
    path("api/ai/chat/", views.ai_chat, name="ai_chat"),


    # ---------- ADMIN PAGE ----------
    path('ad/login/', views.login_admin, name='login_admin'),
    path('ad/home/', views.admin_home, name='admin_home'),
    path('ad/manage-user/', views.manage_user, name='manage_user'),
    path('ad/manage-company/', views.manage_company, name='manage_company'),
    path('ad/manage-stock/', views.manage_stock, name='manage_stock'),
    path('ad/manage-news/', views.manage_news, name='manage_news'),

    # ---------- ADMIN API ----------
    path('ad/api/login/', views.admin_login_page, name='admin_login_page'),
    path('ad/api/check-token/', views.check_token_acc, name='check_token_acc'),
    path('get_list_users/', views.get_list_users, name='get_list_users'),
    path('get_list_companys/', views.get_list_companys, name='get_list_companys'),
    path('ad/api/edit_company/', views.edit_company, name='edit_company'),
    path('ad/api/add_company/', views.add_company, name='add_company'),
    path('ad/api/delete_company/', views.delete_company, name='delete_company'),
    path('get_list_stock/', views.get_list_stock, name='get_list_stock'),
    path('clean_data/', views.clean_data, name='clean_data'),
    path('get_list_news/', views.get_list_news, name='get_list_news'),
    path('clean_news/', views.clean_news, name='clean_news'),
    path('add_news/', views.add_news, name='add_news'),
    path('api/subscription_report/', views.get_subscription_report, name='subscription_report'),

]
