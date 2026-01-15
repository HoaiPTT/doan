from datetime import datetime, timedelta
import json
from django.contrib import admin
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render
import pytz
import requests
from stock import settings
from stockapp.authentication import authenticate_token, check_role
from stockapp.models.cassandra_db import News, StockDetail, StockInfo, Users, Subscription
from stockapp.models.crud_operations import create_record, delete_record, read_record, update_record
from stockapp.utils import check_token_validity, generate_jwt_token
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from stockapp.models.crud_operations import session


@csrf_exempt
def admin_login_page(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return JsonResponse({'success': False, 'error': 'Email and password are required'}, status=400)

        user_records = read_record(Users, email=email)
        if not user_records:
            return JsonResponse({'success': False, 'error': 'Account does not exist'}, status=404)

        user = user_records[0]
        role_user = getattr(user, 'role', None)

        if not role_user:
            return JsonResponse({'success': False, 'error': 'Role not found'}, status=404)

        if role_user == 'admin':
            if user.password == password:
                if user.user_token and check_token_validity(user.user_token):
                    messages.success(request, "Token is valid.")
                    return JsonResponse({'success': True, 'message': 'Login admin page successful!', 'token': user.user_token}, status=200)
                else:
                    access_token = generate_jwt_token(user.email, role_user)
                    update_record(Users, {'user_token': access_token}, email=user.email)
                    return JsonResponse({'success': True, 'message': 'Login admin page successful!', 'token': access_token}, status=200)
            else:
                return JsonResponse({'success': False, 'error': 'Password invalid'}, status=400)
        else:
            return JsonResponse({'success': False, 'error': 'Account unauthorized'}, status=403)

@authenticate_token
@check_role(allowed_roles=['admin'])
def get_list_users(request):
    search_query = request.GET.get('search', '').strip()
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 5))

    users = read_record(Users, role='client')

    if search_query:
        users = [
            u for u in users 
            if search_query.lower() in (u.email or '').lower() 
            or search_query.lower() in (u.name or '').lower()
        ]

    if not users:
        return JsonResponse({
            'success': True,
            'total_pages': 1,
            'current_page': page,
            'list_user': []
        }, status=200)

    total_pages = (len(users) + limit - 1) // limit
    start = (page - 1) * limit
    end = start + limit
    users_page = users[start:end]

    list_user = []
    for u in users_page:
        # Lấy subscription của user này
        subs = read_record(Subscription, user_email=u.email)

        # Nếu có nhiều, chọn gói mới nhất theo start_date
        sub_info = None
        if subs:
            subs = sorted(subs, key=lambda s: s.start_date, reverse=True)
            sub_info = subs[0]

        list_user.append({
            'email': u.email,
            'name': u.name,
            'role': u.role,
            'plan': sub_info.plan if sub_info else None,
            'start_date': sub_info.start_date if sub_info else None,
            'end_date': sub_info.end_date if sub_info else None,
            'status': sub_info.status if sub_info else None,
        })

    return JsonResponse({
        'success': True,
        'total_pages': total_pages,
        'current_page': page,
        'list_user': list_user
    }, status=200)


@authenticate_token
@check_role(allowed_roles=['admin'])   
def get_list_companys(request):
    search_query = request.GET.get('search', '').strip()
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 5))

    companies = read_record(StockInfo)
    if search_query:
        companies = [c for c in companies if search_query.lower() in (c.company_name or '').lower() or search_query.lower() in (c.symbol or '').lower()]

    if not companies:
        return JsonResponse({'success': True, 'total_pages': 1, 'current_page': page, 'list_company': []}, status=200)

    total_pages = (len(companies) + limit - 1) // limit
    start = (page - 1) * limit
    end = start + limit
    companies_page = companies[start:end]

    company_data = [
        {
            "symbol": c.symbol,
            "company_name": c.company_name,
            "industry": c.industry,
            "exchange": c.exchange,
            "profile": c.profile,
        }
        for c in companies_page
    ]

    return JsonResponse({'success': True, 'total_pages': total_pages, 'current_page': page, 'list_company': company_data}, status=200)
@authenticate_token
def edit_company(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=400)

    try:
         
        data = json.loads(request.body)
        symbol = data.get('symbol')
        company_name = data.get('company_name')
        industry = data.get('industry')
        exchange = data.get('exchange')
        profile = data.get('profile')

        if not symbol:
            return JsonResponse({'success': False, 'message': 'Symbol is required'}, status=400)

        # Cập nhật công ty trong Cassandra
        update_record(
            StockInfo,
            update_values={
                'company_name': company_name,
                'industry': industry,
                'exchange': exchange,
                'profile': profile
            },
            symbol=symbol  # điều kiện WHERE
        )

        return JsonResponse({'success': True, 'message': 'Company updated successfully'}, status=200)

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@authenticate_token
@check_role(allowed_roles=['admin'])
def add_company(request):
   
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=400)

    try:
        
        data = json.loads(request.body)
        symbol = data.get('symbol')
        company_name = data.get('company_name')
        industry = data.get('industry')
        exchange = data.get('exchange')
        profile = data.get('profile')

        if not symbol or not company_name:
            return JsonResponse({'success': False, 'message': 'Symbol and Company Name are required'}, status=400)

        # Kiểm tra trùng symbol
        existing = read_record(StockInfo, symbol=symbol)
        if existing:
            return JsonResponse({'success': False, 'message': 'Symbol already exists'}, status=400)

        # Thêm bản ghi mới
        create_record(
            StockInfo,
            symbol=symbol,
            company_name=company_name,
            industry=industry,
            exchange=exchange,
            profile=profile,
        )

        return JsonResponse({'success': True, 'message': 'Company added successfully'}, status=200)

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
def delete_company(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=400)

    try:
        data = json.loads(request.body.decode('utf-8'))
        symbol = data.get('symbol', '').strip()

        if not symbol:
            return JsonResponse({'success': False, 'message': 'Missing symbol'}, status=400)

        # ⚡ Nếu bạn có helper delete_record:
        delete_record(StockInfo, symbol=symbol)

        return JsonResponse({'success': True, 'message': f'Company "{symbol}" deleted successfully'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@authenticate_token
@check_role(allowed_roles=['admin'])   
def get_list_stock(request):
    try:
        search_query = request.GET.get('search', '').strip()
        from_date = request.GET.get('from_date', '').strip()
        to_date = request.GET.get('to_date', '').strip()
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 8))

        all_stocks = read_record(StockDetail)  # lấy tất cả
            # Chuyển sang list dict
        stock_info = [
            {key: round(value, 2) if isinstance(value, float) else value for key, value in row._asdict().items()}
            for row in all_stocks
        ]
        # Lọc theo search_query
        if search_query:
                stock_info = [s for s in stock_info if search_query.lower() in s['symbol'].lower()]

        # Lọc theo ngày
        if from_date and to_date:
                from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
                to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()

                stock_info = [
                    s for s in stock_info
                    if isinstance(s['date'], str) and from_date_obj <= datetime.strptime(s['date'], "%Y-%m-%d").date() <= to_date_obj
                ]
            # Sắp xếp giảm dần theo ngày
        stock_info = sorted(stock_info, key=lambda x: x['date'], reverse=True)

        # Phân trang
        paginator = Paginator(stock_info, limit)
        stock_page = paginator.get_page(page)

        return JsonResponse({
                'success': True,
                'total_pages': paginator.num_pages,
                'current_page': page,
                'stock_data': list(stock_page),
                'stock_info': stock_info,
            }, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@authenticate_token
@check_role(allowed_roles=['admin'])   
def clean_data(request):
    try:
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now_vn = datetime.now(vn_tz)
        cutoff_date = now_vn - timedelta(days=90)
        print(cutoff_date)
        stock_records = read_record(StockDetail)

        to_delete = []
        for record in stock_records:
            try:
                record_date = record.date
                if isinstance(record_date, str):
                    record_date = datetime.strptime(record_date, "%Y-%m-%d")
                    record_date = vn_tz.localize(record_date)
                    print(record_date)
                if record_date < cutoff_date:
                    to_delete.append((record.symbol, record.date))
            except Exception:
                continue

        deleted_count = 0
        for symbol, date in to_delete:
            delete_record(StockDetail, symbol=symbol, date=date)
            deleted_count += 1

        return JsonResponse({'success': True, 'message': f'Deleted {deleted_count} old records.'}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
@authenticate_token
@check_role(allowed_roles=['admin', 'user'])   
def get_list_news(request):
    try:
        search_query = request.GET.get('search', '').strip()
        from_date = request.GET.get('from_date', '').strip()
        to_date = request.GET.get('to_date', '').strip()
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 5))
        category_filter = request.GET.get('category', 'all')
        # Lấy toàn bộ tin tức từ Cassandra
        news = read_record(News)  # Trả về list Row object
        news_list = [n._asdict() for n in news]

        # Lọc theo từ khóa
        if search_query:
            news_list = [n for n in news_list if search_query.lower() in (n.get('title') or '').lower()]

        # Lọc theo ngày
        if from_date and to_date:
            from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()

            news_list = [
                n for n in news_list
                if isinstance(n['updated_at'], datetime) and from_date_obj <= n['updated_at'].date() <= to_date_obj
            ]

        
        # Filter theo category nếu có
        if category_filter != 'all':
            news_list = [n for n in news_list if (n.get('category') or 'other') == category_filter]

        # Sắp xếp giảm dần theo updated_at
        news_list = sorted(news_list, key=lambda x: x['updated_at'], reverse=True)

        # Phân trang
        paginator = Paginator(news_list, limit)
        news_page = paginator.get_page(page)

        return JsonResponse({
            'success': True,
            'total_pages': paginator.num_pages,
            'current_page': news_page.number,
            'news_data': list(news_page.object_list)
        }, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@authenticate_token
@check_role(allowed_roles=['admin'])
def clean_news(request):
    try:
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now_vn = datetime.now(vn_tz)
        cutoff_date = now_vn - timedelta(days=90)

        all_records = read_record(News)
        deleted_count = 0

        for record in all_records:
            try:
                if isinstance(record.updated_at, datetime) and record.updated_at < cutoff_date:
                    delete_record(News, url_news=record.url_news)
                    deleted_count += 1
            except:
                continue

        return JsonResponse({'success': True, 'message': f'Deleted {deleted_count} records older than 3 months.'}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz, uuid
from django.http import JsonResponse

@authenticate_token
@check_role(allowed_roles=['admin'])
def add_news(request):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now_vn = datetime.now(vn_tz)

        # Các nguồn + category
        sources = [
            # Vietstock
            ("https://vietstock.vn/chung-khoan.htm", "stocks", "Vietstock"),
            ("https://vietstock.vn/thi-truong.htm", "economy", "Vietstock"),
            # VnExpress
            ("https://vnexpress.net/kinh-doanh/chung-khoan", "stocks", "VnExpress"),
            ("https://vnexpress.net/kinh-doanh/bat-dong-san", "real_estate", "VnExpress"),
            ("https://vnexpress.net/kinh-doanh/ngan-hang", "banking", "VnExpress"),
        ]

        total_added = 0

        for url, category, source_name in sources:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    print(f"❌ Không lấy được {url}")
                    continue

                soup = BeautifulSoup(response.text, "html.parser")

                # Chọn selector theo nguồn
                if source_name == "Vietstock":
                    articles = soup.select(".list-news .item")
                elif source_name == "VnExpress":
                    articles = soup.select("article.item-news")
                else:
                    articles = []

                added_count = 0

                for item in articles:
                    try:
                        if source_name == "Vietstock":
                            link_tag = item.select_one("a")
                            title = link_tag.get("title") or link_tag.get_text(strip=True)
                            url_news = "https://vietstock.vn" + link_tag["href"]
                            desc_tag = item.select_one(".content")
                            description = desc_tag.get_text(strip=True) if desc_tag else ""
                            img_tag = item.select_one("img")
                            image_url = img_tag["src"] if img_tag else ""
                        elif source_name == "VnExpress":
                            link_tag = item.select_one("a[href]")
                            url_news = link_tag["href"]
                            title = link_tag.get("title") or link_tag.get_text(strip=True)
                            desc_tag = item.select_one("p.description")
                            description = desc_tag.get_text(strip=True) if desc_tag else ""
                            img_tag = item.select_one("img")
                            image_url = img_tag["src"] if img_tag else ""
                        else:
                            continue

                        # Kiểm tra đã tồn tại trong DB chưa
                        existing = read_record(News, url_news=url_news)
                        if existing:
                            continue

                        create_record(
                            News,
                            id=uuid.uuid4(),
                            url_news=url_news,
                            updated_at=now_vn,
                            title=title,
                            description=description,
                            image_news=image_url,
                            source=source_name,
                            category=category
                        )
                        added_count += 1
                        total_added += 1

                        if added_count >= 20:  # Giới hạn 20 bài mỗi nguồn
                            break

                    except Exception as e:
                        print(f"❌ Lỗi xử lý bài ({source_name}):", e)
                        continue

                print(f"✅ Thêm {added_count} bài từ {source_name} ({category})")

            except Exception as e:
                print(f"❌ Lỗi khi cào {url}: {e}")

        return JsonResponse({'success': True, 'message': f'Đã thêm tổng cộng {total_added} tin tức mới'}, status=200)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
def get_subscription_report(request):

    try:
        query = "SELECT start_date, amount FROM subscriptions"
        rows = session.execute(query)

        monthly_data = {}
        for row in rows:
            if not row.start_date:
                continue
            month_key = row.start_date.strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = {"revenue": 0, "count": 0}
            monthly_data[month_key]["revenue"] += row.amount or 0
            monthly_data[month_key]["count"] += 1

        # Sắp xếp theo tháng (từ cũ → mới)
        sorted_months = sorted(monthly_data.keys())  

        data = {
            "labels": sorted_months,
            "revenues": [monthly_data[m]["revenue"] for m in sorted_months],
            "counts": [monthly_data[m]["count"] for m in sorted_months],
        }

        return JsonResponse(data)

    except Exception as e:
        print("❌ Lỗi khi lấy dữ liệu báo cáo:", e)
        return JsonResponse({"error": str(e)}, status=500)

def admin_home(request):
    

    # Tổng công ty
    stock_rows = list(session.execute("SELECT symbol FROM stock;"))
    total_companies = len(stock_rows)

    # Tổng user role=client
    user_rows = list(session.execute("SELECT email, role, name FROM users;"))
    client_users = [r for r in user_rows if r.role and r.role.lower() == "client"]
    total_users = len(client_users)

    # Tổng gói active
    sub_rows = list(session.execute("SELECT user_email, plan, status, start_date FROM subscriptions;"))
    active_subs = [r for r in sub_rows if r.plan and r.status == "active"]

    total_premium = sum(1 for r in active_subs if "premium" in r.plan.lower())
    total_professional = sum(1 for r in active_subs if "professional" in r.plan.lower())

    # 5 subscription active gần nhất
    recent_subs = sorted(
        [r for r in sub_rows if r.status == "active" and r.start_date],
        key=lambda r: r.start_date,
        reverse=True
    )[:5]

    recent_subs_data = []
    for r in recent_subs:
        # Lấy user theo email
        user = next((u for u in user_rows if u.email == r.user_email), None)
        recent_subs_data.append({
            "name": user.name if user and user.name else r.user_email,
            "plan": r.plan,
            "time": r.start_date.strftime("%d/%m/%Y %H:%M")
        })


    dashboard = {
        "total_companies": total_companies,
        "total_users": total_users,
        "total_premium": total_premium,
        "total_professional": total_professional
    }

    return render(
        request,
        "admin/home-admin.html",
        {
            "dashboard": dashboard,
            "recent_subs": recent_subs_data
        }
    )
