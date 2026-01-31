from app.main import app

# Vercel requires a handler, but FastAPI works with the ASGI app directly
# if configured correctly or using an adapter.
# However, for @vercel/python, we usually expose 'app'.
