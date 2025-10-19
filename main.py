from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime

app = FastAPI(title="Currency Converter API - Vercel")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Externa - Gratuita y sin límites de tasa
PRIMARY_API = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1"
FALLBACK_API = "https://latest.currency-api.pages.dev/v1"

@app.get("/")
async def root():
    return JSONResponse(
        content={
            "status_code": 200,
            "message": "Currency Converter API",
            "developer": "El Impaciente",
            "telegram_channel": "https://t.me/Apisimpacientes",
            "version": "1.0.0",
            "endpoints": {
                "/currencies": "Get list of all available currencies",
                "/convert": "Convert currency - Use: /convert?amount=100&from=USD&to=EUR",
                "/rates": "Get all rates for a currency - Use: /rates?currency=USD",
                "/health": "Check API health status"
            },
            "features": [
                "200+ currencies including cryptocurrencies",
                "Real-time exchange rates",
                "No rate limits",
                "Daily updated"
            ]
        },
        status_code=200
    )

@app.get("/currencies")
async def get_currencies():
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(f"{PRIMARY_API}/currencies.json")
                if response.status_code == 200:
                    currencies_data = response.json()
                else:
                    response = await client.get(f"{FALLBACK_API}/currencies.json")
                    currencies_data = response.json()
            except:
                response = await client.get(f"{FALLBACK_API}/currencies.json")
                currencies_data = response.json()
            
            return JSONResponse(
                content={
                    "status_code": 200,
                    "total_currencies": len(currencies_data),
                    "currencies": currencies_data,
                    "developer": "El Impaciente",
                    "telegram_channel": "https://t.me/Apisimpacientes"
                },
                status_code=200
            )
            
    except httpx.TimeoutException:
        return JSONResponse(
            content={
                "status_code": 408,
                "message": "Request timeout. The external API took too long to respond",
                "developer": "El Impaciente",
                "telegram_channel": "https://t.me/Apisimpacientes"
            },
            status_code=408
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "message": "Error fetching currencies list",
                "error": str(e),
                "developer": "El Impaciente",
                "telegram_channel": "https://t.me/Apisimpacientes"
            },
            status_code=500
        )

@app.get("/rates")
async def get_rates(currency: str = Query(default="", description="Base currency code (e.g., USD, EUR, BTC)")):
    if not currency or currency.strip() == "":
        return JSONResponse(
            content={
                "status_code": 400,
                "message": "Parameter 'currency' is required",
                "developer": "El Impaciente",
                "telegram_channel": "https://t.me/Apisimpacientes",
                "example": "/rates?currency=USD"
            },
            status_code=400
        )
    
    currency = currency.lower().strip()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(f"{PRIMARY_API}/currencies/{currency}.json")
                if response.status_code == 200:
                    rates_data = response.json()
                else:
                    response = await client.get(f"{FALLBACK_API}/currencies/{currency}.json")
                    rates_data = response.json()
            except:
                response = await client.get(f"{FALLBACK_API}/currencies/{currency}.json")
                rates_data = response.json()
            
            if response.status_code != 200:
                return JSONResponse(
                    content={
                        "status_code": 400,
                        "message": f"Currency '{currency.upper()}' not found or invalid",
                        "developer": "El Impaciente",
                        "telegram_channel": "https://t.me/Apisimpacientes"
                    },
                    status_code=400
                )
            
            base_currency = rates_data.get(currency, {})
            date = rates_data.get("date", "unknown")
            
            return JSONResponse(
                content={
                    "status_code": 200,
                    "base_currency": currency.upper(),
                    "date": date,
                    "rates": base_currency,
                    "total_rates": len(base_currency),
                    "developer": "El Impaciente",
                    "telegram_channel": "https://t.me/Apisimpacientes"
                },
                status_code=200
            )
            
    except httpx.TimeoutException:
        return JSONResponse(
            content={
                "status_code": 408,
                "message": "Request timeout. The external API took too long to respond",
                "developer": "El Impaciente",
                "telegram_channel": "https://t.me/Apisimpacientes"
            },
            status_code=408
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "message": "Error fetching exchange rates",
                "error": str(e),
                "developer": "El Impaciente",
                "telegram_channel": "https://t.me/Apisimpacientes"
            },
            status_code=500
        )

@app.get("/convert")
async def convert_currency(
    amount: float = Query(default=0, description="Amount to convert"),
    from_currency: str = Query(default="", alias="from", description="Source currency code (e.g., USD)"),
    to_currency: str = Query(default="", alias="to", description="Target currency code (e.g., EUR)")
):
    if not from_currency or from_currency.strip() == "":
        return JSONResponse(
            content={
                "status_code": 400,
                "message": "Parameter 'from' is required",
                "developer": "El Impaciente",
                "telegram_channel": "https://t.me/Apisimpacientes",
                "example": "/convert?amount=100&from=USD&to=EUR"
            },
            status_code=400
        )
    
    if not to_currency or to_currency.strip() == "":
        return JSONResponse(
            content={
                "status_code": 400,
                "message": "Parameter 'to' is required",
                "developer": "El Impaciente",
                "telegram_channel": "https://t.me/Apisimpacientes",
                "example": "/convert?amount=100&from=USD&to=EUR"
            },
            status_code=400
        )
    
    if amount <= 0:
        return JSONResponse(
            content={
                "status_code": 400,
                "message": "Parameter 'amount' must be greater than 0",
                "developer": "El Impaciente",
                "telegram_channel": "https://t.me/Apisimpacientes",
                "example": "/convert?amount=100&from=USD&to=EUR"
            },
            status_code=400
        )
    
    from_currency = from_currency.lower().strip()
    to_currency = to_currency.lower().strip()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(f"{PRIMARY_API}/currencies/{from_currency}.json")
                if response.status_code == 200:
                    rates_data = response.json()
                else:
                    response = await client.get(f"{FALLBACK_API}/currencies/{from_currency}.json")
                    rates_data = response.json()
            except:
                response = await client.get(f"{FALLBACK_API}/currencies/{from_currency}.json")
                rates_data = response.json()
            
            if response.status_code != 200:
                return JSONResponse(
                    content={
                        "status_code": 400,
                        "message": f"Source currency '{from_currency.upper()}' not found or invalid",
                        "developer": "El Impaciente",
                        "telegram_channel": "https://t.me/Apisimpacientes"
                    },
                    status_code=400
                )
            
            base_rates = rates_data.get(from_currency, {})
            
            if to_currency not in base_rates:
                return JSONResponse(
                    content={
                        "status_code": 400,
                        "message": f"Target currency '{to_currency.upper()}' not found or invalid",
                        "developer": "El Impaciente",
                        "telegram_channel": "https://t.me/Apisimpacientes"
                    },
                    status_code=400
                )
            
            exchange_rate = base_rates[to_currency]
            converted_amount = amount * exchange_rate
            date = rates_data.get("date", "unknown")
            
            return JSONResponse(
                content={
                    "status_code": 200,
                    "original": {
                        "amount": amount,
                        "currency": from_currency.upper()
                    },
                    "converted": {
                        "amount": round(converted_amount, 2),
                        "currency": to_currency.upper()
                    },
                    "exchange_rate": exchange_rate,
                    "date": date,
                    "calculation": f"{amount} {from_currency.upper()} × {exchange_rate} = {round(converted_amount, 2)} {to_currency.upper()}",
                    "developer": "El Impaciente",
                    "telegram_channel": "https://t.me/Apisimpacientes"
                },
                status_code=200
            )
            
    except httpx.TimeoutException:
        return JSONResponse(
            content={
                "status_code": 408,
                "message": "Request timeout. The external API took too long to respond",
                "developer": "El Impaciente",
                "telegram_channel": "https://t.me/Apisimpacientes"
            },
            status_code=408
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "message": "Error performing currency conversion",
                "error": str(e),
                "developer": "El Impaciente",
                "telegram_channel": "https://t.me/Apisimpacientes"
            },
            status_code=500
        )

@app.get("/health")
async def health_check():
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "Currency Converter API - Vercel",
            "timestamp": datetime.utcnow().isoformat(),
            "developer": "El Impaciente",
            "telegram_channel": "https://t.me/Apisimpacientes"
        },
        status_code=200
    )

# Handler para Vercel
app = app