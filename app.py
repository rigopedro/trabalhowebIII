from flask import Flask, render_template, redirect, request
import mysql.connector

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
    return render_template('index.html')

@app.route('/inscricao')
def formulario():
    return render_template('formulario.html')

@app.route('/enviar', methods=['POST'])
def enviar():
    nome = request.form['nome']
    email = request.form['email']
    telefone = request.form['telefone']
    data_nascimento = request.form['data_nascimento']

    try:
        enviar_sql(nome, email, telefone, data_nascimento)
    except Exception as e:
        app.logger.error(e)
        return render_template('formulario.html', resultado="Erro na conexão com o nosso banco de dados, tente novamente mais tarde!")

    return render_template('formulario.html', resultado="Inscrição enviada com sucesso!")

if __name__ == '__main__':
    app.run(debug=True)
