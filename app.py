from flask import Flask, render_template, redirect, request, session, url_for, g
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

app = Flask(__name__)

app.secret_key = os.getenv('CHAVE_SECRETA')

# gerenciar conexao com bd
def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="alakazam_db"
    )
    return g.db

#fecha conexao com bd no final da req
@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario' in session:
        return redirect(url_for('admin'))
    erro = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        sql = "SELECT * FROM admins WHERE usuario = %s"
        cursor.execute(sql, (usuario,))
        admin = cursor.fetchone()

        cursor.close()

        if admin and check_password_hash(admin['senha'], senha):
            session['usuario'] = admin['usuario']
            return redirect(url_for('admin'))
        else:
            erro = "Usuário ou senha incorretos."

    return render_template('login.html', erro=erro)

def enviar_sql(nome, email, telefone, data_nascimento, instagram):
    conn = get_db()
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
            smtp.sendmail(os.getenv('EMAIL_USER'), os.getenv('EMAIL_DESTINO'), msg.as_string())
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

    app.logger.info(f"{nome}, {email}, {telefone}, {data_nascimento}, {instagram}")

    try:
        enviar_sql(nome, email, telefone, data_nascimento,  instagram)
    except Exception as e:
        app.logger.error(e)
        return render_template('formulario.html', resultado="Erro na conexão com o nosso banco de dados, tente novamente mais tarde!")

    try:
        enviar_email(nome, email, telefone, data_nascimento,  instagram)
    except Exception as e:
        app.logger.error(e)

    return render_template('formulario.html', resultado="Inscrição enviada com sucesso!")

@app.route('/admin')
def admin():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inscricoes ORDER BY data_envio DESC")
    inscritos = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin.html', inscritos=inscritos)

if __name__ == '__main__':
    app.run(debug=True)

