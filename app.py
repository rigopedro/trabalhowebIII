from flask import Flask, render_template, redirect, request
import mysql.connector
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def connector():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="alakazam_db"
    )

def enviar_sql(nome, email, telefone, data_nascimento, instagram):
    conn = connector()
    cursor = conn.cursor()
    sql = "INSERT INTO inscricoes (nome, email, telefone, data_nascimento, instagram) VALUES (%s, %s, %s, %s, %s)"
    val = (nome, email, telefone, data_nascimento, instagram)
    cursor.execute(sql, val)
    conn.commit()
    cursor.close()
    conn.close()

def enviar_email(nome, email, telefone, data_nascimento, instagram):
    msg = EmailMessage()
    msg['Subject'] = 'Nova inscrição recebida'
    msg['From'] = os.getenv('EMAIL_USER')
    msg['To'] = os.getenv('EMAIL_DESTINO')

    msg.set_content(f"""
Nova inscrição recebida:
Nome: {nome}
Email: {email}
Telefone: {telefone}
Data de Nascimento: {data_nascimento}
Instagram: {instagram}
""")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(os.getenv('EMAIL_USER'), os.getenv('SENHA_EMAIL'))
            smtp.send_message(msg)
    except Exception as e:
        app.logger.error(f"Erro ao enviar email: {e}")

@app.route('/')
def home():
    caminho_pasta = os.path.join(app.static_folder, 'frontend/images/carrossel')

    imagens = []
    if os.path.exists(caminho_pasta):
        imagens = [
            f'frontend/images/carrossel/{arquivo}' 
            for arquivo in os.listdir(caminho_pasta) 
            if arquivo.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
        ]

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
    instagram = request.form['instagram']

    # remover caracteres desnecessarios do numero de telefone inserido
    telefone = telefone.strip().translate({ord(i): None for i in ' +-.()[]'})

    # checagem dos dados inseridos
    if nome == '' or len(nome) < 2:
        return render_template('formulario.html', resultado="Nome Inválido, por favor insira novamente")
    if email == '' or '@' not in email:
        return render_template('formulario.html', resultado="E-mail inválido, por favor insira novamente")
    if len(telefone) != 11 or not telefone.isnumeric():
        return render_template('formulario.html', resultado="Numero de telefone invalido. Não esqueça de incluir o DDD, por exemplo: (21) 91234-5678")

    app.logger.info(nome, email, telefone, data_nascimento)

    try:
        enviar_sql(nome, email, telefone, data_nascimento, instagram)
        enviar_email(nome, email, telefone, data_nascimento, instagram)
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
