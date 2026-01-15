from datetime import datetime, timedelta, timezone as dt_timezone
import hashlib
import hmac
import json
import time
import traceback
import uuid
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
import pandas as pd
import requests
from vnstock import Company, Listing, Quote
from stock import settings
from stockapp.authentication import authenticate_token, check_role
from stockapp.forms.forms_cassandra import RegisterForm, UserInfoForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from stockapp.models.cassandra_db import StockDetail, StockInfo, Users, News, Watchlist,Subscription
from stockapp.models.crud_operations import get_session
from stockapp.models.crud_operations import create_record, delete_record, read_record, update_record
from stockapp.utils import check_token_validity, generate_jwt_token
from django.utils import timezone
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

from vnstock import Vnstock

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            hashed_password = make_password(password)
            role = "client"
            token = generate_jwt_token(email, role)

            user_data = {
                'email': email,
                'password': hashed_password,
                'role': 'client',
                'user_token': token,
                'created_at': datetime.now()
            }
            create_record(Users, **user_data)
            sub_data = {
                'id': int(datetime.now().timestamp()),  # hoặc dùng UUID
                'user_email': email,
                'plan': 'basic',
                'start_date': datetime.now(),
                'end_date': None,
                'status': 'active',
                'amount': 0,
                'transaction_id': None
            }
            create_record(Subscription, **sub_data)
            messages.success(request, "Account registered successfully!")
            request.session['email'] = email
            return redirect('userinfo')
    else:
        form = RegisterForm()
    
    return render(request, 'user/register.html', {'form': form})
@csrf_exempt
def api_register(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')

        # check email đã tồn tại chưa
        if read_record(Users, email=email):
            return JsonResponse({'success': False, 'error': 'Email already exists'}, status=400)

        hashed_password = make_password(password)
        role = 'client'
        token = generate_jwt_token(email, role)

        user_data = {
            'email': email,
            'password': hashed_password,
            'role': role,
            'user_token': token,
            'name': name,
            'created_at': datetime.now()
        }
        create_record(Users, **user_data)
        
        sub_data = {
           'id': uuid.uuid4(), 
            'user_email': email,
            'plan': 'basic',
            'start_date': datetime.now(),
            'end_date': None,
            'status': 'active',
            'amount': 0,
            'transaction_id': None
        }
        create_record(Subscription, **sub_data)

        return JsonResponse({'success': True, 'message': 'Account registered successfully!'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def user_info(request):
    email = request.session.get('email')  
    if not email:
        return redirect('/user/login/')  # Nếu chưa login thì chuyển sang login

    conditions = {'email': email}
    records = read_record(Users, **conditions)

    if records:
        record = records[0]
        users = Users(
            email=record.email,
            password=record.password,
            role=record.role,
            user_token=record.user_token, 
            name=record.name,  
             
        )

    if request.method == "POST":
        form = UserInfoForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
           
            update_record(Users, {'name': name, }, **{'email': email})
            return redirect('/user/info/')
    else:
        form = UserInfoForm(initial={'email': email, 'name': record.name})

    return render(request, 'user/personal.html', {'form': form, 'user': users})

@csrf_exempt
def api_user_info(request):
    if request.method == "GET":
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JsonResponse({"success": False, "error": "No token"}, status=401)

        token = auth_header.split(" ")[1]

        # Tìm user theo token
        user_records = read_record(Users, **{"user_token": token})
        if not user_records:
            return JsonResponse({"success": False, "error": "Invalid token"}, status=401)

        user = user_records[0]

       
        sub_records = read_record(Subscription, user_email=user.email)
        sub = None
        if sub_records:
            active_subs = [s for s in sub_records if s.status == "active"]
            if active_subs:
                sub = max(active_subs, key=lambda s: s.start_date)
            else:
                sub = max(sub_records, key=lambda s: s.start_date)


        return JsonResponse({
            "success": True,
            "user": {
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "created_at": str(user.created_at),
                "subscription": {
                    "plan": sub.plan if sub else "basic",
                    "start_date": str(sub.start_date) if sub else str(user.created_at),
                    "end_date": str(sub.end_date) if sub and sub.end_date else None,
                    "status": sub.status if sub else "active",
                    "amount": sub.amount if sub else 0,
                    "transaction_id": sub.transaction_id if sub else None,
                } if sub else None
    }
}, status=200)



@csrf_exempt
def api_login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            password = data.get('password')
        except:
            return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

        records = read_record(Users, **{'email': email})
        if not records:
            return JsonResponse({'success': False, 'error': 'Account does not exist'}, status=404)

        user_record = records[0]
        if not check_password(password, user_record.password):
            return JsonResponse({'success': False, 'error': 'Invalid password'}, status=403)

        # Token
        if user_record.user_token and check_token_validity(user_record.user_token):
            token = user_record.user_token
        else:
            token = generate_jwt_token(user_record.email, user_record.role)
            update_record(Users, {'user_token': token}, **{'email': email})

        if user_record.role != 'client':
            return JsonResponse({'success': False, 'error': 'Invalid role!'}, status=403)

        return JsonResponse({
            'success': True,
            'message': 'Login successful',
            'user': {   
                'token': token,
                'email': user_record.email,
                'name': user_record.name,
                'role': user_record.role
            }
        }, status=200)


@authenticate_token
@check_role(allowed_roles=['client'])
def customer_edit_profile(request):
    email_user = request.user['email']
    userinfo_list = read_record(Users, email=email_user)
    userinfo = userinfo_list[0] if userinfo_list else None

    if not userinfo:
        return JsonResponse({'error': 'Customer personal infomation does not exist.'}, status=403)

    if request.method == 'GET':
        user_data = {
            'name': str(userinfo.name),
           
            'email': str(userinfo.email),
        }
        return JsonResponse({'success': True, 'userinfo': user_data}, status=200)

    elif request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        name = data.get('name')
      

        try:
            update_record(Users, {'name': name}, email=email_user)
            return JsonResponse({
                'success': True,
                'message': 'Customer information updated successfully!',
                'name': name
            }, status=200)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid method. Use GET to view and POST to update profile.'}, status=405)


@csrf_exempt
def get_company_info(request):
    try:
        # Lấy symbol
        if request.method == "GET":
            symbol = request.GET.get('symbol')
        else:
            data = json.loads(request.body.decode('utf-8'))
            symbol = data.get('symbol')

        if not symbol:
            return JsonResponse({'success': False, 'error': 'No symbol provided'}, status=400)

        # Lấy thông tin công ty
        company_info_list = read_record(StockInfo, symbol=symbol)
        if not company_info_list:
            return JsonResponse({'success': False, 'error': 'Company not found'}, status=404)

        company_info = company_info_list[0]._asdict()
        return JsonResponse({'success': True, 'company_info': company_info}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    

import math

 # Load danh sách cổ phiếu từ Excel
df = pd.read_excel("/Users/thuhoai/Downloads/stock-1/vn_stocks_full_info.xlsx")
companys = df[["symbol", "company_name", "exchange"]].dropna().drop_duplicates()
symbols = df['symbol'].dropna().unique().tolist()
batch_size = 5
batch_delay = 20
vn=Vnstock()
source ="VCI"

def is_trading_time():
    now = datetime.now()
   
    now = now.astimezone()  # sẽ dùng timezone hệ thống, hoặc pytz timezone Asia/Ho_Chi_Minh
    if now.hour == 9 and now.minute < 15:
        return False
    return 9 <= now.hour < 15

def adjust_price(val):
    try:
        v = float(val)
        if v < 1000:
            return v * 1000
        return v
    except:
        return val
    
from datetime import datetime, date, timedelta, timezone
import time
import traceback
import pandas as pd
import numpy as np


def insert_stock_info():
    session = get_session()  # lấy session Cassandra chuẩn
    all_data = {}

    def ensure_datetime_local(val):
        if val is None:
            return None
        if isinstance(val, pd.Timestamp):
            return val.to_pydatetime().replace(tzinfo=None)  # local naive
        if isinstance(val, np.datetime64):
            return pd.to_datetime(val).to_pydatetime().replace(tzinfo=None)
        if isinstance(val, datetime):
            return val.replace(tzinfo=None)  
        if isinstance(val, date):
            return datetime.combine(val, datetime.min.time())  # local date
        return None

    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i + batch_size]
        print(f"\n=== Xử lý batch {i // batch_size + 1}: {batch} ===")

        for sym in batch:
            print(f"--- Xử lý mã {sym} ---")
            try:
                stk = vn.stock(symbol=sym, source=source)

                # Lấy dữ liệu thực cho từng mã
                if is_trading_time():
                    board = stk.trading.price_board(symbols_list=[sym])
                    if board is not None and len(board) > 0:
                        df_board = board[[
                            ('listing', 'trading_date'),
                            ('bid_ask', 'transaction_time'),
                            ('match', 'open_price'),
                            ('match', 'highest'),
                            ('match', 'lowest'),
                            ('match', 'match_price'),
                            ('match', 'accumulated_volume'),
                            ('listing', 'ref_price')
                        ]].copy()

                        df_board.columns = [
                            "trading_date", "transaction_time", "open", "high",
                            "low", "close", "volume", "ref_price"
                        ]
                        row = df_board.iloc[-1].copy()
                        date_val = pd.to_datetime(row["trading_date"])
                        close = adjust_price(row["close"])
                        ref = adjust_price(row["ref_price"]) if row.get("ref_price") else None
                        if ref and ref != 0:
                            change_abs = close - ref
                            change_pct = (change_abs / ref) * 100
                        else:
                            change_abs = None
                            change_pct = None

                        row["change"] = change_abs
                        row["change_pct"] = change_pct
                    else:
                        row = pd.Series({
                            c: None for c in [
                                "date", "open", "high", "low",
                                "close", "volume", "ref_price",
                                "change", "change_pct"
                            ]
                        })
                        date_val = None

                else:
                    today = datetime.now().date()
                    start_hist = (today - timedelta(days=7)).strftime("%Y-%m-%d")
                    end_hist = today.strftime("%Y-%m-%d")

                    hist = stk.quote.history(start=start_hist, end=end_hist, interval="1D")
                    if len(hist) > 0:
                        today_row = hist.iloc[-1]
                        prev_row = hist.iloc[-2] if len(hist) > 1 else None
                        row = pd.Series({
                            "date": datetime.now(),
                            "open": adjust_price(today_row["open"]),
                            "high": adjust_price(today_row["high"]),
                            "low": adjust_price(today_row["low"]),
                            "close": adjust_price(today_row["close"]),
                            "volume": today_row["volume"],
                            "change_pct": (
                                (adjust_price(today_row["close"]) -
                                 adjust_price(prev_row["close"])) /
                                adjust_price(prev_row["close"]) * 100
                            ) if prev_row is not None else 0
                        })
                        date_val = row["date"]
                    else:
                        row = pd.Series({
                            c: None for c in [
                                "date", "open", "high", "low",
                                "close", "volume", "ref_price",
                                "change", "change_pct"
                            ]
                        })
                        date_val = None

                # Kiểm tra giá trị date hợp lệ
                dt_local = datetime.now()

                defaults = {
                    k: (None if pd.isna(v) else v) for k, v in {
                        "open_price": row.get("open"),
                        "high_price": row.get("high"),
                        "low_price": row.get("low"),
                        "close_price": row.get("close"),
                        "volume": row.get("volume"),
                        "change": row.get("change_pct"),
                        "market_cap": None
                    }.items()
                }

                # Lấy stock đã tồn tại trong ngày (range)
                today_dt = dt_local.date()
                start_day = datetime.combine(today_dt, datetime.min.time())  # local
                end_day = start_day + timedelta(days=1)

                existing = session.execute(
                    f"""
                    SELECT * FROM {StockDetail.__table__}
                    WHERE symbol=%s AND date >= %s AND date < %s ALLOW FILTERING
                    """,
                    (sym, start_day, end_day)
                ).all()

                updated_at = datetime.now()
                query = f"""
                    INSERT INTO {StockDetail.__table__}
                    (symbol, date, open_price, high_price, low_price,
                     close_price, volume, change, market_cap, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                if existing:
                    ex = existing[0]
                    if ex.close_price != defaults["close_price"] or ex.volume != defaults["volume"]:
                        session.execute(
                            query,
                            (
                                sym, dt_local,
                                defaults["open_price"], defaults["high_price"],
                                defaults["low_price"], defaults["close_price"],
                                defaults["volume"], defaults["change"],
                                defaults["market_cap"], updated_at
                            )
                        )
                        all_data[sym] = {"inserted": True}
                    else:
                        all_data[sym] = {
                            "inserted": False,
                            "reason": "No change in close/volume"
                        }
                else:
                    session.execute(
                        query,
                        (
                            sym, dt_local,
                            defaults["open_price"], defaults["high_price"],
                            defaults["low_price"], defaults["close_price"],
                            defaults["volume"], defaults["change"],
                            defaults["market_cap"], updated_at
                        )
                    )
                    all_data[sym] = {"inserted": True}

                time.sleep(5)

            except Exception as e:
                print(f"Lỗi xử lý mã {sym}: {e}")
                traceback.print_exc()
                all_data[sym] = {"success": False, "error": str(e)}
                continue

        print(f"Ngủ {batch_delay} giây trước batch tiếp theo...")
        time.sleep(batch_delay)

    return all_data


def get_stock(request):
    import pytz
    VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")
    try:
        all_companies = read_record(StockInfo)
        company_map = {c.symbol: c for c in all_companies}

        all_stocks = read_record(StockDetail)

        stock_map = {}  # { (symbol, date_only) : record }
        for s in all_stocks:
            if not s.date:
                continue
            vn_date = s.date.astimezone(VN_TZ)
            date_only = vn_date.date()  # chỉ lấy ngày, bỏ giờ

            key = (s.symbol, date_only)

            # Giữ bản mới nhất (date lớn hơn)
            if key not in stock_map or s.date > stock_map[key].date:
                stock_map[key] = s

        stock_list = []
        for (symbol, _), s in stock_map.items():
            company = company_map.get(s.symbol)
            stock_list.append({
                "symbol": s.symbol,
                "company_name": company.company_name if company else "",
                "exchange": company.exchange if company else "",
                "date": s.date.astimezone(VN_TZ).strftime("%Y-%m-%d %H:%M:%S"),
                "open_price": s.open_price,
                "high_price": s.high_price,
                "low_price": s.low_price,
                "close_price": s.close_price,
                "change": s.change,
                "volume": s.volume,
            })

        stock_list.sort(key=lambda x: x["date"], reverse=True)

        return JsonResponse({"success": True, "stocks": stock_list})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    

from stockapp.models.crud_operations import session
@csrf_exempt

def get_stock_detail(request):
    symbol = request.GET.get("symbol")
    if not symbol:
        return JsonResponse({"error": "Missing symbol"}, status=400)

    try:
        info = session.execute(
            "SELECT * FROM stock WHERE symbol = %s LIMIT 1", [symbol]
        ).one()

        detail = session.execute(
            "SELECT * FROM stock_detail WHERE symbol = %s LIMIT 1", [symbol]
        ).one()

        if not info or not detail:
            return JsonResponse({"error": "Stock not found"}, status=404)

        stock = {
            "symbol": info.symbol,
            "name": info.company_name,
            "exchange": info.exchange,
            "industry": info.industry,
            "profile": info.profile,
            "date": str(detail.date),
            "open_price": detail.open_price,
            "high_price": detail.high_price,
            "low_price": detail.low_price,
            "close_price": detail.close_price,
            "volume": detail.volume,
            "change": detail.change,
            "market_cap": detail.market_cap,

            "updated_at": str(detail.updated_at),
        }

        return JsonResponse({"success": True, "stock": stock})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def insert_company(request):
    try:
        symbols_list = companys['symbol'].tolist()
        for i in range(0, len(symbols_list), batch_size):
            batch_symbols = symbols_list[i:i+batch_size]
            print(f"\n=== Xử lý batch {i//batch_size + 1}: {batch_symbols} ===")

            for sym in batch_symbols:
                print(f"\n--- Xử lý mã {sym} ---")
                stk = vn.stock(symbol=sym, source=source)

                company_info = stk.company.overview().iloc[0]
                row = companys[companys['symbol'] == sym].iloc[0]
                income = stk.finance.income_statement(period="year", lang="vi", dropna=True)
                if not income.empty:
                    latest_income = income.sort_values("Năm", ascending=False).iloc[0]
                    defaults={
                        'company_name': row['company_name'],
                        'industry': company_info.get('icb_name3', ''),
                        'exchange': row['exchange'],
                        'profile': company_info.get('company_profile','')
                    }
                create_record(StockInfo, **defaults, symbol=sym)
                time.sleep(5)  

            print(f"\nNgủ {batch_delay} giây trước khi batch tiếp theo...")
            time.sleep(batch_delay)

        return JsonResponse({'success': True, 'message': 'Thêm thông tin công ty thành công'}, status=200)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
 
import random

def get_company_profile(symbol: str):
    # Lấy thông tin công ty từ DB
    company = session.execute(
        f"SELECT * FROM {StockInfo.__table__} WHERE symbol=%s", (symbol,)
    ).one()

    stock = session.execute(
        f"SELECT * FROM {StockDetail.__table__} WHERE symbol=%s ORDER BY date DESC LIMIT 1", (symbol,)
    ).one()

    if not company:
        # Nếu DB không có công ty, return lỗi
        return JsonResponse({"success": False, "message": f"Company {symbol} not found"}, status=404)

    company = dict(company._asdict())

    # Stock info
    if stock:
        stock_data = {
            "price": stock.close_price,
            "change": stock.change or 0,
            "changePercent": (stock.change or 0) / stock.close_price * 100 if stock.close_price else 0,
            "high52w": stock.high_52w or (stock.close_price * 1.2 if stock.close_price else 100),
            "low52w": stock.low_52w or (stock.close_price * 0.8 if stock.close_price else 50),
        }
    else:
        # Fake giá trị stock nhỏ nếu DB chưa có
        stock_data = {
            "price": round(random.uniform(10, 1000), 2),
            "change": round(random.uniform(-5, 5), 2),
            "changePercent": round(random.uniform(-5, 5), 2),
            "high52w": round(random.uniform(50, 1000), 2),
            "low52w": round(random.uniform(5, 50), 2),
        }

    # Financial highlights (fake nếu null)
    financials = {
        "revenue": company.get("revenue") or random.randint(1e8, 1e12),
        "netIncome": company.get("netIncome") or random.randint(1e7, 1e11),
        "grossMargin": company.get("grossMargin") or round(random.uniform(20, 80), 2),
        "operatingMargin": company.get("operatingMargin") or round(random.uniform(10, 50), 2),
        "roe": company.get("roe") or round(random.uniform(5, 25), 2),
        "roa": company.get("roa") or round(random.uniform(2, 15), 2),
        "marketCap": company.get("marketCap") or random.randint(1e9, 1e12),
        "enterpriseValue": company.get("enterpriseValue") or random.randint(1e9, 1e12),
       
    }

    # Fake một số field nhỏ nếu trống
    if not company.get("tagline"):
        company["tagline"] = f"Leading company in {company.get('sector', 'its sector')}"
    if not company.get("website"):
        company["website"] = f"https://www.{symbol.lower()}.com"

    company.update(stock_data)
    company.update(financials)

    return JsonResponse({"success": True, "company": company})

def get_list_news_user(request):
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 9))
        category_filter = request.GET.get('category', '').strip()  # có thể truyền ?category=economy

        news = read_record(News)
        news_list = [n._asdict() for n in news]

        # Lọc theo category nếu có
        if category_filter:
            news_list = [n for n in news_list if n.get('category') == category_filter]

        # sắp xếp theo updated_at
        news_list = sorted(news_list, key=lambda x: x['updated_at'], reverse=True)

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


# ✅ Helper: lấy user từ token
def get_user_from_token(request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, JsonResponse({"success": False, "error": "No token"}, status=401)

    token = auth_header.split(" ")[1]
    records = read_record(Users, user_token=token)
    if not records:
        return None, JsonResponse({"success": False, "error": "Invalid token"}, status=401)

    return records[0], None


@csrf_exempt
def add_to_watchlist(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid method"}, status=405)

    user, error = get_user_from_token(request)
    if error:
        return error

    try:
        data = json.loads(request.body)
        symbol = data.get("symbol")
        if not symbol:
            return JsonResponse({"success": False, "error": "Missing symbol"}, status=400)

        create_record(Watchlist, email=user.email, symbol=symbol)
        return JsonResponse({"success": True, "message": f"{symbol} added to watchlist"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)



def get_watchlist(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "error": "Invalid method"}, status=405)

    user, error = get_user_from_token(request)
    if error:
        return error

    # Lấy danh sách symbol từ Watchlist
    records = read_record(Watchlist, email=user.email)
    symbols = [r.symbol for r in records]

    # Lấy dữ liệu từ bảng stock_detail
    watchlist_data = []
    for symbol in symbols:
        stock_records = read_record(StockDetail, symbol=symbol)
        if stock_records:
            stock = stock_records[0]
            watchlist_data.append({
                "symbol": stock.symbol,
                "close_price": getattr(stock, "close_price", None),
                "change": getattr(stock, "change", None)
            })
        else:
            # Nếu không có dữ liệu stock_detail, vẫn trả symbol
            watchlist_data.append({
                "symbol": symbol,
                "close_price": None,
                "change": None
            })

    return JsonResponse({"success": True, "watchlist": watchlist_data})

@csrf_exempt
def remove_from_watchlist(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid method"}, status=405)

    user, error = get_user_from_token(request)
    if error:
        return error

    try:
        data = json.loads(request.body)
        symbol = data.get("symbol")
        if not symbol:
            return JsonResponse({"success": False, "error": "Missing symbol"}, status=400)

        delete_record(Watchlist, email=user.email, symbol=symbol)
        return JsonResponse({"success": True, "message": f"{symbol} removed from watchlist"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
ZALOPAY_CONFIG = {
    'app_id': '2554',
    'key1': 'sdngKKJmqEMzvh5QQcdD2A9XBSKUNaYn',
    'key2': 'trMrHtvjo6myautxDUiAcYsVtaeQ8nhf',
    'endpoint': 'https://sb-openapi.zalopay.vn/v2/create',
}
from stockapp.tasks import ngrok_url
PLAN_PRICING = {
    "Premium": 50000,
    "Professional": 100000,
}
@csrf_exempt
@authenticate_token

def zalo_payment(request):
    if request.method == 'POST':
        if not ngrok_url:
            return JsonResponse({'success': False, 'error': 'Ngrok URL not available'}, status=500)

        data = json.loads(request.body)
        email = request.user['email']
        plan = data.get('plan')

        if plan not in PLAN_PRICING:
            return JsonResponse({'success': False, 'error': 'Invalid plan'}, status=400)

        amount = PLAN_PRICING[plan]
        trans_id = random.randint(100000, 999999)
        ReturnUrl = "http://127.0.0.1:8000/user/subscription/"
        embed_data = {'redirecturl': ReturnUrl, 'plan': plan}

        order = {
            'app_id': ZALOPAY_CONFIG['app_id'],
            'app_trans_id': f"{datetime.now().strftime('%y%m%d')}{trans_id}",
            'app_user': str(email),
            'app_time': int(datetime.now().timestamp() * 1000),
            'item': json.dumps([]),
            'embed_data': json.dumps(embed_data),
            'amount': amount,
            'callback_url': f"{ngrok_url}/callback/",
            'description': f"Payment for {plan} plan - order #{trans_id}",
            'bank_code': '',
        }
        data_mac = '|'.join([
            str(order['app_id']),
            str(order['app_trans_id']),
            str(order['app_user']),
            str(order['amount']),
            str(order['app_time']),
            order['embed_data'],
            order['item']
        ])
        order['mac'] = hmac.new(ZALOPAY_CONFIG['key1'].encode(), data_mac.encode(), hashlib.sha256).hexdigest()

        try:
            response = requests.post(ZALOPAY_CONFIG['endpoint'], params=order)
            result = response.json()
            if result.get('return_code') == 1:
                return JsonResponse({'success': True, 'url': result.get('order_url')})
            else:
                return JsonResponse({'success': False, 'error': result.get('return_message')}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        

def save_subscription(email, amount, plan="", transaction_id=None):
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)

    # 1. expire gói cũ
    old_subs = read_record(Subscription, user_email=email, status="active")
    for sub in old_subs:
        update_record(
            Subscription,
            {"status": "expired"},
            user_email=sub.user_email,
            id=sub.id
        )

    # 2. insert gói mới (luôn active)
    create_record(
        Subscription,
        user_email=email,
        id=uuid.uuid4(),
        amount=int(amount),
        plan=plan,
        status="active",
        transaction_id=transaction_id,
        start_date=start_date,
        end_date=end_date,
    )

    print(f"✅ Subscription inserted for {email}, plan={plan}, amount={amount}")

@csrf_exempt
def callback(request):
    if request.method != 'POST':
        return JsonResponse({'return_code': 0, 'return_message': 'Invalid method'}, status=405)

    try:
        # Parse JSON request từ ZaloPay
        body = json.loads(request.body)
        data_str = body.get("data", "")
        req_mac = body.get("mac", "")

        # Tính lại MAC để xác thực
        mac = hmac.new(
            ZALOPAY_CONFIG['key2'].encode(),
            data_str.encode(),
            hashlib.sha256
        ).hexdigest()

        if req_mac != mac:
            return JsonResponse({'return_code': -1, 'return_message': 'MAC not equal'})

        # Parse chi tiết giao dịch
        data_json = json.loads(data_str)
        app_trans_id = data_json.get("app_trans_id")
        email = data_json.get("app_user")
        amount = data_json.get("amount", 0)

        # embed_data là chuỗi JSON => parse lại
        embed_data_raw = data_json.get("embed_data", "{}")
        embed_data = json.loads(embed_data_raw)
        plan = embed_data.get("plan", "Premium")

        # Kiểm tra trạng thái giao dịch
        status_response = check_status_order(app_trans_id)

        if status_response.get("return_code") == 1:
            # Lưu subscription thành công
            save_subscription(
                email=email,
                amount=amount,
                plan=plan,
                
                transaction_id=app_trans_id
            )
            return JsonResponse({'return_code': 1, 'return_message': 'success'})
        else:
            return JsonResponse({'return_code': 0, 'return_message': 'Payment failed or processing'})

    except Exception as e:
        return JsonResponse({'return_code': 0, 'return_message': f'Error: {str(e)}'})
    
def check_status_order(app_trans_id):
    post_data = {
        'app_id': ZALOPAY_CONFIG['app_id'],
        'app_trans_id': app_trans_id,
    }
    data_str = f"{post_data['app_id']}|{post_data['app_trans_id']}|{ZALOPAY_CONFIG['key1']}"
    post_data['mac'] = hmac.new(ZALOPAY_CONFIG['key1'].encode(), data_str.encode(), hashlib.sha256).hexdigest()

    response = requests.post('https://sb-openapi.zalopay.vn/v2/query', data=post_data)
    return response.json()

def check_payment_status(request):
    app_trans_id = request.GET.get("apptransid")
    plan = request.GET.get("plan", "Premium")
    amount = request.GET.get("amount", 0)

    post_data = {
        'app_id': ZALOPAY_CONFIG['app_id'],
        'app_trans_id': app_trans_id,
    }
    data_str = f"{post_data['app_id']}|{post_data['app_trans_id']}|{ZALOPAY_CONFIG['key1']}"
    post_data['mac'] = hmac.new(ZALOPAY_CONFIG['key1'].encode(), data_str.encode(), hashlib.sha256).hexdigest()

    response = requests.post('https://sb-openapi.zalopay.vn/v2/query', data=post_data)
    result = response.json()

    if result.get("return_code") == 1:
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)  # mặc định 1 tháng

        return JsonResponse({
            "success": True,
            "message": "Payment successful!",
            "plan": plan,
            "amount": amount,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        })
    else:
        return JsonResponse({
            "success": False,
            "message": "Payment failed!"
        })
        

def check_and_update_status(email):
    subs = read_record(Subscription, user_email=email)
    if not subs:
        return None

    now = datetime.now()   # dùng local time
    active_sub = None

    for sub in subs:
        if sub.status == "active":
            # nếu gói đã hết hạn thì expire luôn
            if sub.end_date and sub.end_date < now:
                update_record(
                    Subscription,
                    {"status": "expired"},
                    user_email=sub.user_email,
                    id=sub.id
                )
            else:
                # còn hạn thì giữ lại active mới nhất
                if (not active_sub) or (sub.start_date > active_sub.start_date):
                    active_sub = sub

    return active_sub



@csrf_exempt
def subscription_history(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "error": "Method not allowed"}, status=405)

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JsonResponse({"success": False, "error": "No token"}, status=401)

    token = auth_header.split(" ")[1]

    # Tìm user theo token
    user_records = read_record(Users, **{"user_token": token})
    if not user_records:
        return JsonResponse({"success": False, "error": "Invalid token"}, status=401)

    user = user_records[0]

    try:
        records = read_record(Subscription, user_email=user.email)
        history = []

        for record in records:
            history.append({
                "plan_name": getattr(record, "plan", None),
                "amount": getattr(record, "amount", None),
                "purchase_date": getattr(record, "start_date", None),
                "end_date": getattr(record, "end_date", None),
                "status": getattr(record, "status", None)
            })

        return JsonResponse({"success": True, "history": history})

    except Exception as e:
        print("❌ Error fetching subscription history:", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@csrf_exempt
def change_password(request):
    if request.method != "PUT":
        return JsonResponse({"success": False, "error": "Method not allowed"}, status=405)

    # Lấy token từ header
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JsonResponse({"success": False, "error": "No token provided"}, status=401)

    token = auth_header.split(" ")[1]

    # Xác thực token → tìm user tương ứng
    user_records = read_record(Users, **{"user_token": token})
    if not user_records:
        return JsonResponse({"success": False, "error": "Invalid token"}, status=401)

    user = user_records[0]

    # Đọc dữ liệu gửi lên
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    current_pw = data.get("current_password")
    new_pw = data.get("new_password")

    if not current_pw or not new_pw:
        return JsonResponse({"success": False, "error": "Missing password fields"}, status=400)

    # Kiểm tra mật khẩu cũ
    if not check_password(user.password, current_pw):
        return JsonResponse({"success": False, "error": "Current password is incorrect"}, status=401)

    # Hash mật khẩu mới
    hashed_pw = make_password(new_pw)

    try:
        # Gọi helper update_record
        update_record(Users, {"password": hashed_pw}, email=user.email)
        return JsonResponse({"success": True, "message": "Password changed successfully"})
    except Exception as e:
        print("❌ Error updating password:", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)
#####AI

def check_ai_permission(user_email):
    sub_records = read_record(Subscription, user_email=user_email)

    if not sub_records:
        return False, "BASIC"

    now = datetime.now(timezone.utc)

    active_subs = [
        s for s in sub_records
        if s.status == "active"
        and s.end_date
        and s.end_date > now
    ]

    if not active_subs:
        return False, "BASIC"

    sub = max(active_subs, key=lambda s: s.start_date)
    plan = sub.plan.upper()

    if plan in ["PROFESSIONAL", "PREMIUM"]:
        return True, plan

    return False, plan

@csrf_exempt
def ai_chat(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid method"}, status=405)

    # ===== CHECK TOKEN =====
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JsonResponse({"success": False, "error": "No token"}, status=401)

    token = auth_header.split(" ")[1]
    users = read_record(Users, user_token=token)
    if not users:
        return JsonResponse({"success": False, "error": "Invalid token"}, status=401)

    user = users[0]

    # ===== CHECK SUBSCRIPTION =====
    subs = read_record(Subscription, user_email=user.email)
    plan = "basic"

    if subs:
        active_subs = [s for s in subs if s.status == "active"]
        if active_subs:
            latest = max(active_subs, key=lambda s: s.start_date)
            plan = latest.plan

    # ===== BLOCK BASIC =====
    if plan == "basic":
        return JsonResponse({
            "success": False,
            "error": "Bạn đang dùng gói Basic. Vui lòng nâng cấp để sử dụng AI."
        }, status=403)

    # ===== GỌI AI =====
    data = json.loads(request.body)
    question = data.get("message")

    from stockapp.ai_service import call_ai_model
    answer = call_ai_model(question, plan)

    return JsonResponse({
        "success": True,
        "answer": answer,
        "plan": plan
    })
