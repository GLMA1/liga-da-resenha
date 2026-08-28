from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta-liga-da-resenha-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Filtro do Jinja para ler o JSON das seleções no histórico de apostas
@app.template_filter('from_json')
def from_json_filter(value):
    try:
        return json.loads(value)
    except:
        return []

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    creditos = db.Column(db.Float, default=10.0) # Começa com 10 créditos grátis
    is_admin = db.Column(db.Boolean, default=False)
    apostas = db.relationship('Aposta', backref='user', lazy=True)

class Aposta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    selecoes = db.Column(db.Text, nullable=False) # Armazenado como string JSON
    odd_total = db.Column(db.Float, nullable=False)
    retorno = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pendente') # Pendente, Ganha, Perdida

with app.app_context():
    db.create_all()
    # Cria um administrador padrão se não existir (Usuário: admin / Senha: admin123)
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        hashed_pw = generate_password_hash('admin123')
        admin = User(username='admin', password=hashed_pw, creditos=1000.0, is_admin=True)
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    usuario = User.query.get(session['user_id'])
    return render_template('index.html', usuario=usuario, aba_ativa='partidas')

@app.route('/elencos')
def elencos():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    usuario = User.query.get(session['user_id'])
    return render_template('index.html', usuario=usuario, aba_ativa='elencos')

@app.route('/apostas')
def apostas_aba():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    usuario = User.query.get(session['user_id'])
    return render_template('index.html', usuario=usuario, aba_ativa='apostas')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        flash('Usuário ou senha incorretos!', 'error')
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        existing = User.query.filter_by(username=username).first()
        if existing:
            flash('Este nome de usuário já está em uso.', 'error')
            return redirect(url_for('cadastro'))
        
        hashed_pw = generate_password_hash(password)
        novo_usuario = User(username=username, password=hashed_pw, creditos=10.0)
        db.session.add(novo_usuario)
        db.session.commit()
        
        session['user_id'] = novo_usuario.id
        return redirect(url_for('index'))
    return render_template('cadastro.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    usuario = User.query.get(session['user_id'])
    if not usuario or not usuario.is_admin:
        flash('Acesso negado!', 'error')
        return redirect(url_for('index'))
    
    usuarios = User.query.all()
    apostas = Aposta.query.order_by(Aposta.id.desc()).all()
    return render_template('admin.html', usuarios=usuarios, apostas=apostas)

@app.route('/liquidar/<int:aposta_id>/<status>')
def liquidar_aposta(aposta_id, status):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    usuario = User.query.get(session['user_id'])
    if not usuario or not usuario.is_admin:
        return redirect(url_for('index'))
    
    aposta = Aposta.query.get(aposta_id)
    if aposta and aposta.status == 'Pendente':
        aposta.status = status
        if status == 'Ganha':
            aposta.user.creditos += aposta.retorno
        db.session.commit()
    
    return redirect(url_for('admin'))

@app.route('/fazer_aposta', methods=['POST'])
def fazer_aposta():
    if 'user_id' not in session:
        return jsonify({'status': 'erro', 'mensagem': 'Faça login primeiro.'})
    
    usuario = User.query.get(session['user_id'])
    dados = request.get_json()
    valor = float(dados.get('valor', 0))
    selecoes = dados.get('selecoes', [])
    odd_total = float(dados.get('odd_total', 1.0))
    
    if valor <= 0:
        return jsonify({'status': 'erro', 'mensagem': 'Valor de aposta inválido.'})
    
    if usuario.creditos < valor:
        return jsonify({'status': 'erro', 'mensagem': 'Saldo insuficiente!'})
    
    retorno = valor * odd_total
    usuario.creditos -= valor
    
    nova_aposta = Aposta(
        user_id=usuario.id,
        valor=valor,
        selecoes=json.dumps(selecoes),
        odd_total=odd_total,
        retorno=retorno,
        status='Pendente'
    )
    db.session.add(nova_aposta)
    db.session.commit()
    
    return jsonify({'status': 'sucesso'})

if __name__ == '__main__':
    app.run(debug=True)