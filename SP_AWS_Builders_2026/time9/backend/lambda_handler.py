"""Entrypoint AWS Lambda (deploy serverless alternativo, documentado).
Uso: apontar o handler da função para `lambda_handler.handler`."""
from mangum import Mangum
from app.main import app

handler = Mangum(app)
