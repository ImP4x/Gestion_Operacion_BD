from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
import requests
from pymongo import MongoClient
import datetime

# Configuración
API_KEY = '49618108-69398494162a37c0b5866112e'
MONGO_URI = 'mongodb://localhost:27017/'
DB_NAME = 'image_db'

class SimpleHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type='text/html'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        try:
            if self.path == '/':
                self._set_headers()
                with open('index.html', 'rb') as f:
                    self.wfile.write(f.read())
            elif self.path == '/styles.css':
                self._set_headers('text/css')
                with open('styles.css', 'rb') as f:
                    self.wfile.write(f.read())
            elif self.path == '/scripts.js':
                self._set_headers('application/javascript')
                with open('scripts.js', 'rb') as f:
                    self.wfile.write(f.read())
            elif self.path == '/lupa.png':
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                with open('lupa.png', 'rb') as f:
                    self.wfile.write(f.read())
                    
            else:
                self.send_error(404)
        except Exception as e:
            self.send_error(500, str(e))

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            if self.path == '/search':
                self._handle_search(data)
            elif self.path == '/save':
                self._handle_save(data)
            else:
                self.send_error(404)
        except Exception as e:
            self._send_error_response(500, str(e))

    def _handle_search(self, data):
        search_term = data.get('query', '').strip()
        if not search_term:
            raise ValueError("Término de búsqueda vacío")

        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        # Registrar búsqueda
        db.api_requests.insert_one({
            'query': search_term,
            'date': datetime.datetime.utcnow()
        })

        # Obtener imágenes
        response = requests.get(
            'https://pixabay.com/api/',
            params={
                'key': API_KEY,
                'q': search_term,
                'image_type': 'photo',
                'per_page': 20,
                'safesearch': 'true',
                'orientation': 'horizontal'
            }
        )

        if response.status_code != 200:
            raise Exception(f"Error API: {response.status_code} - {response.text}")

        images = response.json().get('hits', [])
        self._send_json_response(images)

    def _handle_save(self, data):
        selected_images = data.get('images', [])
        if not selected_images:
            raise ValueError("No se seleccionaron imágenes")

        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]

        # Filtrar imágenes ya existentes
        existing_ids = [img['id'] for img in selected_images]
        duplicates = list(db.images.find(
            {"pixabay_id": {"$in": existing_ids}},
            {"pixabay_id": 1, "_id": 0}
        ))

        if duplicates:
            duplicate_ids = [str(doc['pixabay_id']) for doc in duplicates]
            self._send_json_response({
                'success': False,
                'message': 'Algunas imágenes ya existen',
                'duplicates': duplicate_ids
            }, status=409)
            return

        # Insertar nuevas imágenes
        documents = []
        for img in selected_images:
            documents.append({
                'pixabay_id': img['id'],
                'image_url': img['webformatURL'],
                'tags': ', '.join(img.get('tags', '').split(', ')),
                'search_query': data.get('query', ''),
                'date': datetime.datetime.utcnow(),
                'saved_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        result = db.images.insert_many(documents)
        self._send_json_response({
            'success': True,
            'inserted': len(result.inserted_ids),
            'message': 'Imágenes guardadas exitosamente'
        })

    def _send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _send_error_response(self, status, message):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            'success': False,
            'error': message,
            'message': 'Error en el servidor'
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=SimpleHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Servidor corriendo en http://localhost:{port}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo el servidor...")
    finally:
        httpd.server_close()

if __name__ == '__main__':
    run()