from flask import Flask, request, jsonify, redirect
import MetaTrader5 as mt5
import inspect
from datetime import datetime

app = Flask(__name__)

if not mt5.initialize():
    raise RuntimeError("MetaTrader5 initialization failed")


def to_jsonable(x):
    if x is None or isinstance(x, (bool, int, float, str)):
        return x
    if hasattr(x, "_asdict"):
        return {k: to_jsonable(v) for k, v in x._asdict().items()}
    if isinstance(x, (list, tuple, range)):
        return [to_jsonable(v) for v in x]
    if isinstance(x, dict):
        return {k: to_jsonable(v) for k, v in x.items()}
    if hasattr(x, "tolist"):
        return to_jsonable(x.tolist())
    if isinstance(x, datetime):
        return x.isoformat()
    if hasattr(x, "__dict__"):
        return to_jsonable(vars(x))
    return str(x)


def call_mt5_function(func_name, params):
    func = getattr(mt5, func_name, None)
    
    if not func or not callable(func):
        return {"error": f"Function '{func_name}' not found"}

    try:
        if isinstance(params, dict):
            try:
                result = func(**params)
            except TypeError:
                try:
                    sig = inspect.signature(func)
                    param_names = list(sig.parameters.keys())
                    args = [params.get(p) for p in param_names if p in params]
                    result = func(*args)
                except Exception as e:
                    return {"error": f"Invalid arguments: {str(e)}"}
                    
        elif isinstance(params, (list, tuple)):
            result = func(*params)
        else:
            result = func() if not params else func(params)
        
        return {"result": to_jsonable(result)}
        
    except Exception as e:
        return {"error": str(e)}


@app.route("/api/<func_name>", methods=["POST"])
def mt5_proxy(func_name):
    params = request.get_json(force=True, silent=True) or {}
    return jsonify(call_mt5_function(func_name, params))


@app.route("/")
def root():
    return redirect("/api/docs")


@app.route("/api/docs")
def docs():
    """
    Discovery endpoint.
    For more info see: https://www.mql5.com/en/docs/python_metatrader5
    Returns:
        {
            "endpoints": ["version", "account_info", ...]
        }
    Only lists available MetaTrader5 function names exposed via:
        POST /api/<function_name>
    """
    funcs = [
        name
        for name, _ in inspect.getmembers(mt5, inspect.isbuiltin)
        if not name.startswith("__")
    ]
    return jsonify({"endpoints": funcs})


app.run(host="0.0.0.0", port=5000)