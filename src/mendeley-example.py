from flask import Flask, redirect, render_template, request, session
import yaml
import json
#import os

from mendeley import Mendeley
from mendeley.session import MendeleySession

filemendeley = "c:/Users/edevp/source/repos/MendeleyToNotion/MendeleyToNotion/secrets/secrets_mendeley.json"
# if not os.path.exists(filemendeley):
#     print("No existe la ruta")

with open(filemendeley) as f:
    config = json.load(f)

print(config)

REDIRECT_URI = 'http://localhost:5000/oauth'

app = Flask(__name__)
app.debug = True
app.secret_key = config['clientSecret']

mendeley = Mendeley(config['clientId'], config['clientSecret'], REDIRECT_URI)


@app.route('/')
def home():
    if 'token' in session:
        return redirect('/listDocuments')

    auth = mendeley.start_authorization_code_flow()
    session['state'] = auth.state

    return render_template('home.html', login_url=(auth.get_login_url()))


@app.route('/oauth')
def auth_return():
    #code = session['code']
    #print(code)
    #request.args.get('nombre')
    auth = mendeley.start_authorization_code_flow(state=request.args.get('state'))
    mendeley_session = auth.authenticate(request.url)

    session.clear()
    session['token'] = mendeley_session.token
    print(mendeley_session.token)
    with open(filemendeley, "r+") as archivo:
    # Leer el contenido del archivo
        datos_existentes = json.load(archivo)
        # Actualizar el nodo "ciudad"
        datos_existentes["token"] = mendeley_session.token
        # Rebobinar el archivo
        archivo.seek(0)
        # Volver a escribir el archivo con la información actualizada
        json.dump(datos_existentes, archivo, indent=4)


    return redirect('/listDocuments')


@app.route('/listDocuments')
def list_documents():
    if 'token' not in session:
        return redirect('/')

    mendeley_session = get_session_from_cookies()

    name = mendeley_session.profiles.me.display_name
    docs = mendeley_session.documents.list(view='client').items

    return render_template('library.html', name=name, docs=docs)


@app.route('/document')
def get_document():
    if 'token' not in session:
        return redirect('/')

    mendeley_session = get_session_from_cookies()

    document_id = request.args.get('document_id')
    doc = mendeley_session.documents.get(document_id)

    return render_template('metadata.html', doc=doc)


@app.route('/metadataLookup')
def metadata_lookup():
    if 'token' not in session:
        return redirect('/')

    mendeley_session = get_session_from_cookies()

    doi = request.args.get('doi')
    doc = mendeley_session.catalog.by_identifier(doi=doi)

    return render_template('metadata.html', doc=doc)


@app.route('/download')
def download():
    if 'token' not in session:
        return redirect('/')

    mendeley_session = get_session_from_cookies()

    document_id = request.args.get('document_id')
    doc = mendeley_session.documents.get(document_id)
    doc_file = doc.files.list().items[0]

    return redirect(doc_file.download_url)


@app.route('/logout')
def logout():
    session.pop('token', None)
    return redirect('/')


def get_session_from_cookies():
    return MendeleySession(mendeley, session['token'])


if __name__ == '__main__':
    app.run()
