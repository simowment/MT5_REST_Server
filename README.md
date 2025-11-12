# MT5 REST Server

Very simple REST server exposing the Python MetaTrader5 API over HTTP.
It dynamically maps most `MetaTrader5` functions to HTTP endpoints.

Application: [`MT5_Rest_Server.py`](MT5_Rest_Server.py:1)
Example tests: [`mt5_endpoints_test.py`](mt5_endpoints_test.py:1)

---

## 1. Server startup

Prerequisites:
- Python 3.x
- MetaTrader 5 installed with a configured terminal
- Packages:
  - `MetaTrader5`
  - `Flask`
  - `requests` (for client-side testing)

Minimal installation (example):

```bash
pip install MetaTrader5 Flask requests
```

Start the server:

```bash
python MT5_Rest_Server.py
```

By default, the server listens on:

- Host: `0.0.0.0`
- Port: `5000`

---

## 2. General endpoint principle

All main endpoints are exposed as:

- Method: `POST`
- URL: `/api/<function_name>`
- Body: JSON (arguments for the corresponding MetaTrader5 function)
- Response: JSON:
  - `{"result": ...}` on success
  - `{"error": "message"}` on error

Implementation: [`mt5_proxy()`](MT5_Rest_Server.py:60)

The server:
- Dynamically resolves `function_name` to `MetaTrader5.<function_name>`
- Accepts:
  - a JSON object (`{...}`) interpreted as named arguments
  - a JSON array (`[...]`) interpreted as positional arguments
  - or an empty body for functions without arguments
- Automatically serializes results (structures, lists, datetime, etc.) to JSON.

---

## 3. API Docs endpoint

- `GET /api/docs`
  Returns a JSON object with:
  - `endpoints`: list of exposed `MetaTrader5` function names.

Implementation: [`docs()`](MT5_Rest_Server.py:71)

Example response (truncated):

```json
{
  "endpoints": [
    "version",
    "terminal_info",
    "account_info",
    "symbols_total",
    "symbol_info",
    "symbol_info_tick",
    "... etc ..."
  ]
}
```

This endpoint is only meant to:
- discover which function names are available via `POST /api/<function_name>`.

---

## 4. Root redirect

- `GET /`
  Redirects to `/api/docs`.

Implementation: [`root()`](MT5_Rest_Server.py:66)

---

## 5. Available endpoints

The exact list depends on the installed `MetaTrader5` version.
Here are some typical endpoints, all in the format:

- `POST /api/<mt5_function_name>`

1) General information:
- `POST /api/version`
- `POST /api/terminal_info`
- `POST /api/account_info`

2) Symbols:
- `POST /api/symbols_total`
- `POST /api/symbols_get`
  - Body example: `{"start": 0, "count": 10}`
- `POST /api/symbol_info`
  - Body example: `["EURUSD"]`
- `POST /api/symbol_info_tick`
  - Body example: `["EURUSD"]`
- `POST /api/symbol_select`
  - Body example: `["EURUSD", true]`

3) Market data / history:
- `POST /api/copy_ticks_from`
  - Body example: `["EURUSD", 1700000000, 100, 1]`
- `POST /api/copy_ticks_range`
- `POST /api/copy_rates_from`
- `POST /api/copy_rates_range`

4) Orders / positions:
- `POST /api/orders_total`
- `POST /api/orders_get`
- `POST /api/positions_total`
- `POST /api/positions_get`

5) History:
- `POST /api/history_orders_total`
- `POST /api/history_orders_get`
- `POST /api/history_deals_total`
- `POST /api/history_deals_get`

6) Calculations:
- `POST /api/order_calc_margin`
- `POST /api/order_calc_profit`
- `POST /api/order_check`

7) Trading / order flow:
- `POST /api/order_send`
  - Body: same structure as native `MetaTrader5.order_send`

8) Miscellaneous / session:
- `POST /api/last_error`
- `POST /api/market_book_add`
- `POST /api/market_book_get`
- `POST /api/market_book_release`
- `POST /api/initialize`
- `POST /api/login`
- `POST /api/shutdown`

To get the exact list on your environment, always query `/api/docs`.

---

## 6. Request examples

Base URL (default):

```text
http://localhost:5000/api
```

- Get account info:

```bash
curl -X POST http://localhost:5000/api/account_info
```

- Get symbol info:

```bash
curl -X POST http://localhost:5000/api/symbol_info \
  -H "Content-Type: application/json" \
  -d "[\"EURUSD\"]"
```

- Recent ticks:

```bash
curl -X POST http://localhost:5000/api/copy_ticks_from \
  -H "Content-Type: application/json" \
  -d "[\"EURUSD\", 1700000000, 100, 1]"
```

- Send order (simplified example):

```bash
curl -X POST http://localhost:5000/api/order_send \
  -H "Content-Type: application/json" \
  -d "{
    \"action\": 2,
    \"symbol\": \"EURUSD\",
    \"volume\": 0.1,
    \"type\": 2,
    \"price\": 1.0,
    \"sl\": 0.0,
    \"tp\": 0.0,
    \"deviation\": 10,
    \"magic\": 123456,
    \"comment\": \"rest_example\",
    \"type_time\": 0,
    \"type_filling\": 0
  }"
```

---

## 7. Provided test script

The file [`mt5_endpoints_test.py`](mt5_endpoints_test.py:1) contains a test suite that:

- Calls many endpoints (`version`, `account_info`, `symbols_*`, `copy_*`, `orders_*`, etc.)
- Displays for each:
  - the HTTP status
  - a status `OK` / `WARN` / `ERR`
  - an excerpt of the JSON response

Usage (with the server running):

```bash
python mt5_endpoints_test.py
```

---

## 8. Notes and security

- This server is a direct proxy to the available `MetaTrader5` functions.
- No authentication, authorization, or advanced validation is implemented by default.
- Only expose it:
  - on a trusted network, and/or
  - behind a secure reverse proxy (auth, TLS, IP allowlist, etc.).
- Some functions may:
  - place real orders on your trading account,
  - alter the session or terminal state.

Use with caution in any production or live trading environment.

yeah.
