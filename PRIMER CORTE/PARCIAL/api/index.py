from serverless_wsgi import handle_request
from app import app

def vercel_handler(request, context):
    return handle_request(app, request, context)