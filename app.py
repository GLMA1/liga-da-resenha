from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta-liga-da-resenha-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///liga_resenha.db'
db = SQLAlchemy(app)

# Modelo de Usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    creditos = db.Column(db.Float, default=10.0) # Começa com 10 créditos!
    is_admin = db.Column(db.Boolean, default=False)

# Modelo de Aposta
class Aposta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    selecoes = db.Column(db.Text, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    odd_total = db.Column(db.Float, nullable=False)
    retorno = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pendente') # Pendente, Ganha, Perdida
    user = db.relationship('User', backref=db.backref('apostas', lazy=True))

# Criar banco e admin padrão
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            creditos=1000.0,
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('index.html', aba_ativa='partidas', usuario=user)

@app.route('/elencos')
def elencos():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('index.html', aba_ativa='elencos', usuario=user)

@app.route('/apostas')
def apostas_aba():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('index.html', aba_ativa='apostas', usuario=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos!', 'error')
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Este nome de usuário já está em uso!', 'error')
            return redirect(url_for('cadastro'))
            
        hashed_pw = generate_password_hash(password)
        novo_usuario = User(username=username, password=hashed_pw, creditos=10.0)
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Cadastro realizado! Você ganhou 10 créditos iniciais!', 'success')
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/fazer_aposta', methods=['POST'])
def fazer_aposta():
    if 'user_id' not in session:
        return {'status': 'erro', 'mensagem': 'Faça login primeiro!'}
    
    data = request.get_json()
    valor = float(data.get('valor', 0))
    selecoes = data.get('selecoes', [])
    odd_total = float(data.get('odd_total', 1))
    
    user = User.query.get(session['user_id'])
    
    if valor <= 0:
        return {'status': 'erro', 'mensagem': 'Valor de aposta inválido.'}
    if user.creditos < valor:
        return {'status': 'erro', 'mensagem': 'Créditos insuficientes!'}
    if not selecoes:
        return {'status': 'erro', 'mensagem': 'Adicione seleções ao bilhete.'}
        
    # Desconta créditos
    user.creditos -= valor
    retorno = valor * odd_total
    
    nova_aposta = Aposta(
        user_id=user.id,
        selecoes=json.dumps(selecoes),
        valor=valor,
        odd_total=odd_total,
        retorno=retorno,
        status='Pendente'
    )
    db.session.add(nova_aposta)
    db.session.commit()
    
    return {'status': 'sucesso', 'novos_creditos': user.creditos}

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acesso negado. Apenas o administrador.', 'error')
        return redirect(url_for('index'))
    
    usuarios = User.query.all()
    apostas = Aposta.query.order_by(Aposta.id.desc()).all()
    return render_template('admin.html', usuarios=usuarios, apostas=apostas)

@app.route('/admin/liquidar/<int:aposta_id>/<status>')
def liquidar_aposta(aposta_id, status):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('index'))
        
    aposta = Aposta.query.get(aposta_id)
    if aposta and aposta.status == 'Pendente':
        aposta.status = status
        if status == 'Ganha':
            aposta.user.creditos += aposta.retorno
        db.session.commit()
        
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)