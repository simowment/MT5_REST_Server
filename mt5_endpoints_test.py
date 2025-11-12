import requests
import time

BASE = "http://localhost:5000/api"

def call(name, params=None):
    url = f"{BASE}/{name}"
    try:
        r = requests.post(url, json=params, timeout=1)
    except Exception as e:
        print(f"{name}: EXC {e}")
        return
    try:
        data = r.json()
    except Exception:
        print(f"{name}: HTTP {r.status_code}, NON-JSON: {r.text[:200]}")
        return
    has_error = "error" in data
    if r.status_code != 200 or has_error:
        status = "ERR"
    else:
        result = data.get("result", data)
        if result in (None, [], {}):
            status = "WARN"
        else:
            status = "OK"
    print(f"{name}: {status} | HTTP {r.status_code} | {str(data)[:200]}")

def test_basic():
    call("version")
    call("terminal_info")
    call("account_info")
    call("symbols_total")
    call("symbols_get", {"start": 0, "count": 10})

def test_symbols():
    sym = "EURUSD"
    call("symbol_info", [sym])
    call("symbol_info_tick", [sym])
    call("symbol_select", [sym, True])

def test_market_data():
    now = int(time.time())
    call("copy_ticks_from", ["EURUSD", now - 60, 100, 1])
    call("copy_ticks_range", ["EURUSD", now - 120, now, 1])
    call("copy_rates_from", ["EURUSD", 1, now - 60 * 60, 10])
    call("copy_rates_range", ["EURUSD", 1, now - 60 * 60, now])

def test_orders_positions():
    call("orders_total")
    call("orders_get")
    call("positions_total")
    call("positions_get")

def test_history():
    now = int(time.time())
    frm = now - 7 * 24 * 60 * 60
    call("history_orders_total", [frm, now])
    call("history_orders_get", [frm, now])
    call("history_deals_total", [frm, now])
    call("history_deals_get", [frm, now])

def test_calcs():
    sym = "EURUSD"
    call("order_calc_margin", [0, sym, 0.1, 1.0])
    call("order_calc_profit", [0, sym, 0.1, 1.0, 1.001])
    call("order_check", {
        "action": 0,
        "symbol": sym,
        "volume": 0.1,
        "type": 0,
        "price": 1.0,
        "sl": 0.0,
        "tp": 0.0,
        "deviation": 10,
        "magic": 0,
        "comment": "test",
        "type_time": 0,
        "type_filling": 0,
    })

def test_orders_flow():
    sym = "EURUSD"
    order = {
        "action": 2,
        "symbol": sym,
        "volume": 0.1,
        "type": 2,
        "price": 0.5,
        "sl": 0.0,
        "tp": 0.0,
        "deviation": 10,
        "magic": 123456,
        "comment": "rest_smoke_test",
        "type_time": 0,
        "type_filling": 0,
    }

    print("\n[ORDERS FLOW] /api/order_send then /api/orders_get ...")
    resp = requests.post(f"{BASE}/order_send", json=order, timeout=5)
    try:
        data = resp.json()
    except Exception:
        print("order_send: ERR | HTTP", resp.status_code, "| NON-JSON:", resp.text[:200])
        return

    print("order_send response:", str(data)[:200])
    call("orders_total")
    call("orders_get")

def test_misc():
    sym = "EURUSD"
    call("last_error")
    call("market_book_add", [sym])
    call("market_book_get", [sym])
    call("market_book_release", [sym])

def test_session():
    call("initialize")
    call("login")
    call("shutdown")

def test_all_documented():
    print("=== BASIC ===")
    test_basic()
    print("\n=== SYMBOLS ===")
    test_symbols()
    print("\n=== MARKET DATA ===")
    test_market_data()
    print("\n=== ORDERS/POSITIONS (lecture simple) ===")
    test_orders_positions()
    print("\n=== HISTORY ===")
    test_history()
    print("\n=== CALCS ===")
    test_calcs()
    print("\n=== ORDER FLOW (order_send + orders_get) ===")
    test_orders_flow()
    print("\n=== MISC ===")
    test_misc()
    print("\n=== SESSION/LIFECYCLE ===")
    test_session()
    
test_all_documented()