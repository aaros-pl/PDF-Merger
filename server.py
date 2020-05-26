# import bibliotek do obsługi servera api
from flask import Flask, make_response, send_file
from flask_restful import Resource, Api, reqparse
# import bibliotek do obsługi plików i pdfów
from werkzeug import datastructures
from PyPDF4 import PdfFileMerger
# import bibliotek do obsługi virtualnego pliku i base64
import io
import base64

app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response('<!doctype html><title>PDF Merge API - Framework</title><h1>PDF Merge Framework</h1>', 200, headers)


class PDFUpload(Resource):
    def __init__(self):
        # inicjalizacja argumentów postowania
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('pdf1', type=datastructures.FileStorage, required=True, location='files')
        self.reqparse.add_argument('pdf2', type=datastructures.FileStorage, required=True, location='files')
        self.reqparse.add_argument('type', type=str, required=False)
        super(PDFUpload, self).__init__()

    # metoda GET
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response('<!doctype html><title>PDF Merge API</title><h1>PDF Merge API</h1>', 200, headers)

    # metoda POST
    def post(self):
        data = self.reqparse.parse_args()

        # dodatkowe sprawdzenie czy zostały zapostowane pliki
        if data['pdf1'] == "" or data['pdf2'] == "":
            return {
                'status': 'error',
                'message': 'No files found'
            }

        # inicjalizacja "virtualnego" pliku wyjściowego i mergera PDF
        output = io.BytesIO()
        merger = PdfFileMerger(output)

        # inicjalizacja inputów i przypisanie do nich zawartości postowanych plików
        input1 = data["pdf1"]
        input2 = data["pdf2"]

        # Próbujemy mergować pliki
        try:
            # łączenie, zapisywanie i zamykanie wirtualnego pliku
            merger.append(input1)
            merger.append(input2)
            merger.write(output)
            merger.close()
            # przeniesienie kursora na początek wirtualnego pliku
            output.seek(0)
            print("Successfully merged")
            # jeśli output ma być w json i base64 to konwertujemy pdf na base64
            if data['type'] == "64":
                output64 = base64.b64encode(output.getvalue()).decode()
                # zwracamy pdf jako base64
                return {
                    'status': 'success',
                    'message': output64
                }
            # w przeciwnym razie wywołujemy efekt kliknięcia przycisku "Download" i otworzenie przeglądarkowego okienka zapisu pliku
            else:
                return make_response(send_file(output, mimetype="application/pdf"), 200)

        # jeśli try się nie powiodło to wywalamy błąd
        except Exception as e:
            print(e)


# montujemy api handler
api.add_resource(HelloWorld, '/')
api.add_resource(PDFUpload, '/merge')

if __name__ == '__main__':
    app.run(debug=True, threaded=False, host="0.0.0.0", port="5003")
