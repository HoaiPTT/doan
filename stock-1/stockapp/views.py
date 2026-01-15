from django.http import JsonResponse

from stock import settings
import requests
from .pages.user_pages import *
from .pages.admin_pages import *

from .features.tasks_with_cassandra import *
from .features.admin_with_cassandra import *
    
@authenticate_token
def check_token_acc(request):
    return JsonResponse({'success':True, 'message': 'Bạn đã xác thực thành công!', 'user': request.user}, status=200)

