from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configurações do Flask para lidar com upload de arquivos
app.config['UPLOAD_FOLDER'] = 'static/imagens'  # Diretório onde as fotos serão salvas
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}  # Tipos de arquivos permitidos
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite máximo de 16MB para uploads

# Função para verificar se o arquivo é uma imagem válida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Lista que simula um banco de dados com os carros cadastrados
carros_cadastrados = []

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para cadastrar um novo carro
@app.route('/cadastro', methods=['POST'])
def cadastro():
    modelo = request.form.get('modelo')
    marca = request.form.get('marca')
    ano = request.form.get('ano')
    placa = request.form.get('placa')
    cor = request.form.get('cor')

    # Verifica se o arquivo de imagem foi enviado
    foto_filename = None
    if 'foto' in request.files:
        foto = request.files['foto']
        if foto and allowed_file(foto.filename):
            foto_filename = secure_filename(foto.filename)
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))

    carro = {
        "modelo": modelo,
        "marca": marca,
        "ano": ano,
        "placa": placa,
        "cor": cor,
        "foto": foto_filename  # Armazena o nome do arquivo da foto
    }

    carros_cadastrados.append(carro)

    # Redireciona para a página de sucesso com os dados do carro
    return redirect(url_for('sucesso', modelo=modelo, marca=marca, ano=ano, placa=placa, cor=cor, foto=foto_filename))

# Rota para apagar um carro
@app.route('/apagar/<int:index>', methods=['POST'])
def apagar(index):
    if 0 <= index < len(carros_cadastrados):
        carro = carros_cadastrados.pop(index)
        # Apagar a foto do carro se existir
        if carro['foto']:
            foto_path = os.path.join(app.config['UPLOAD_FOLDER'], carro['foto'])
            if os.path.exists(foto_path):
                os.remove(foto_path)
    
    return redirect(url_for('visualizar'))

# Rota para visualizar todos os carros cadastrados
@app.route('/visualizar')
def visualizar():
    return render_template('visualizar.html', carros=carros_cadastrados)

# Rota para visualizar os detalhes de um carro
@app.route('/visualizar_detalhes/<int:index>')
def visualizar_detalhes(index):
    if 0 <= index < len(carros_cadastrados):
        carro = carros_cadastrados[index]
        return render_template('detalhes.html', carro=carro)
    return redirect(url_for('visualizar'))

# Rota para editar as informações de um carro
@app.route('/editar/<int:index>', methods=['GET', 'POST'])
def editar(index):
    if 0 <= index < len(carros_cadastrados):
        carro = carros_cadastrados[index]

        if request.method == 'POST':
            # Atualiza os dados do carro
            carro['modelo'] = request.form.get('modelo')
            carro['marca'] = request.form.get('marca')
            carro['ano'] = request.form.get('ano')
            carro['placa'] = request.form.get('placa')
            carro['cor'] = request.form.get('cor')

            # Verifica se o arquivo de imagem foi enviado
            if 'foto' in request.files:
                foto = request.files['foto']
                if foto and allowed_file(foto.filename):
                    # Apaga a foto antiga, se existir
                    if carro['foto']:
                        foto_path = os.path.join(app.config['UPLOAD_FOLDER'], carro['foto'])
                        if os.path.exists(foto_path):
                            os.remove(foto_path)
                    
                    # Salva a nova foto
                    foto_filename = secure_filename(foto.filename)
                    foto.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))
                    carro['foto'] = foto_filename

            # Redireciona para a página de visualização dos carros atualizados
            return redirect(url_for('visualizar'))

        # Exibe o formulário de edição com os dados atuais do carro
        return render_template('editar.html', carro=carro, index=index)
    
    return redirect(url_for('visualizar'))  # Caso o índice não seja válido, volta para a lista

# Rota de sucesso após o cadastro de um novo carro
@app.route('/sucesso')
def sucesso():
    modelo = request.args.get('modelo')
    marca = request.args.get('marca')
    ano = request.args.get('ano')
    placa = request.args.get('placa')
    cor = request.args.get('cor')
    foto = request.args.get('foto')  # Nome da foto, se existir

    return render_template('sucesso.html', modelo=modelo, marca=marca, ano=ano, placa=placa, cor=cor, foto=foto)

if __name__ == '__main__':
    # Garante que o diretório de imagens exista
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    app.run(debug=True)
