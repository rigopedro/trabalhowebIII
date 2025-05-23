from flask import Flask, render_template, redirect, request
import mysql.connector
import os

app = Flask(__name__)

def connector():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="alakazam_db"
    )

def enviar_sql(nome, email, telefone, data_nascimento):
    conn = connector()
    cursor = conn.cursor()
    sql = "INSERT INTO candidatos (nome, email, telefone, data_nascimento) VALUES (%s, %s, %s, %s)"
    val = (nome, email, telefone, data_nascimento)
    cursor.execute(sql, val)
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
def home():
    caminho_pasta = os.path.join(app.static_folder, 'frontend/images/carrossel')

    imagens = []
    if os.path.exists(caminho_pasta):
        imagens = [
            f'images/carrossel/{arquivo}' 
            for arquivo in os.listdir(caminho_pasta) 
            if arquivo.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
    ]

    app.logger.info(imagens)

    return render_template('index.html', imagens_carrossel=imagens)

@app.route('/inscricao')
def formulario():
    return render_template('formulario.html')

@app.route('/enviar', methods=['POST'])
def enviar():
    nome = request.form['nome']
    email = request.form['email']
    telefone = request.form['telefone']
    data_nascimento = request.form['data_nascimento']

    # remover caracteres desnecessarios do numero de telefone inserido

    telefone = telefone.strip().translate({ord(i): None for i in ' +-.()[]'})

    # checagem dos dados inseridos

    if nome == '' or len(nome) < 2:
        return render_template('formulario.html', resultado="Nome Inválido, por favor insira novamente")
    if email == '' or '@' not in email:
        return render_template('formulario.html', resultado="E-mail inválido, por favor insira novamente")
    if len(telefone) != 11 or telefone.isnumber():
        return render_template('formulario.html', resultado="Numero de telefone invalido. Não esqueça de incluir o DDD, por exemplo: (21) 91234-5678")

    app.logger.info(nome, email, telefone, data_nascimento)

    try:
        enviar_sql(nome, email, telefone, data_nascimento)
    except Exception as e:
        app.logger.error(e)
        return render_template('formulario.html', resultado="Erro na conexão com o nosso banco de dados, tente novamente mais tarde!")

    return render_template('formulario.html', resultado="Inscrição enviada com sucesso!")

@app.route('/admin')
def admin():
    conn = connector()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inscricoes ORDER BY data_envio DESC")
    inscritos = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin.html', inscritos=inscritos)

if __name__ == '__main__':
    app.run(debug=True)
