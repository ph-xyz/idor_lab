from flask import Flask, request, render_template_string, session, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "segredo123"
DB_PATH = "banco.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT,
        email TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS contas (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        saldo REAL,
        tipo TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY,
        conta_id INTEGER,
        descricao TEXT,
        valor REAL
    )''')
    c.execute("DELETE FROM users")
    c.execute("DELETE FROM contas")
    c.execute("DELETE FROM transacoes")

    # Usuários
    c.execute("INSERT INTO users VALUES (1, 'pedro',  'pedro123',  'pedro@email.com')")
    c.execute("INSERT INTO users VALUES (2, 'admin',  'admin123',  'admin@securebank.com')")
    c.execute("INSERT INTO users VALUES (3, 'julia',  'julia123',  'julia@email.com')")
    c.execute("INSERT INTO users VALUES (4, 'marcos', 'marcos123', 'marcos@email.com')")

    # Contas bancárias
    c.execute("INSERT INTO contas VALUES (1, 1, 1500.00,  'Corrente')")   # pedro
    c.execute("INSERT INTO contas VALUES (2, 2, 99999.99, 'Corrente')")   # admin
    c.execute("INSERT INTO contas VALUES (3, 3, 3200.50,  'Poupança')")   # julia
    c.execute("INSERT INTO contas VALUES (4, 4, 850.00,   'Corrente')")   # marcos

    # Transações
    c.execute("INSERT INTO transacoes VALUES (1, 1, 'Salário',         3000.00)")
    c.execute("INSERT INTO transacoes VALUES (2, 1, 'Aluguel',        -1200.00)")
    c.execute("INSERT INTO transacoes VALUES (3, 1, 'Supermercado',    -300.00)")
    c.execute("INSERT INTO transacoes VALUES (4, 2, 'Transferência recebida', 50000.00)")
    c.execute("INSERT INTO transacoes VALUES (5, 2, 'Investimento',   49999.99)")
    c.execute("INSERT INTO transacoes VALUES (6, 3, 'Freelance',       1500.00)")
    c.execute("INSERT INTO transacoes VALUES (7, 3, 'Netflix',           -45.90)")
    c.execute("INSERT INTO transacoes VALUES (8, 4, 'Venda produto',    900.00)")
    c.execute("INSERT INTO transacoes VALUES (9, 4, 'Uber',             -50.00)")

    conn.commit()
    conn.close()

# ─────────────────────────────────────────────
#  TEMPLATES
# ─────────────────────────────────────────────

BASE_STYLE = """
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', sans-serif; background: #0f0f1a; color: #e0e0e0; }
  a { color: #00c8ff; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .navbar {
    background: #1a1a2e;
    border-bottom: 1px solid #2a2a4a;
    padding: 14px 30px;
    display: flex; justify-content: space-between; align-items: center;
  }
  .navbar h2 { color: #00c8ff; font-size: 1.1rem; }
  .navbar span { font-size: 0.85rem; color: #aaa; }
  .container { max-width: 800px; margin: 40px auto; padding: 0 20px; }
  .card {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 12px;
    padding: 28px;
    margin-bottom: 20px;
  }
  .card h3 { color: #00c8ff; margin-bottom: 16px; font-size: 1rem; }
  .saldo { font-size: 2rem; font-weight: bold; color: #00ff88; margin: 8px 0; }
  .tipo { font-size: 0.8rem; color: #666; }
  table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
  th { text-align: left; color: #666; font-weight: 500; padding: 8px 0; border-bottom: 1px solid #2a2a4a; }
  td { padding: 10px 0; border-bottom: 1px solid #1a1a2e; }
  .pos { color: #00ff88; }
  .neg { color: #ff4444; }
  .btn {
    display: inline-block;
    padding: 8px 18px;
    background: #00c8ff;
    color: #0f0f1a;
    font-weight: bold;
    border-radius: 8px;
    font-size: 0.85rem;
    border: none;
    cursor: pointer;
  }
  .btn-ghost {
    background: transparent;
    border: 1px solid #2a2a4a;
    color: #aaa;
  }
  .error {
    background: #2a1a1a; border: 1px solid #ff4444;
    color: #ff6666; padding: 10px 14px;
    border-radius: 8px; font-size: 0.85rem; margin-bottom: 16px;
  }
  input[type=text], input[type=password] {
    width: 100%; padding: 10px 14px;
    background: #0f0f1a; border: 1px solid #2a2a4a;
    border-radius: 8px; color: #e0e0e0;
    font-size: 0.95rem; margin-bottom: 16px; outline: none;
  }
  input:focus { border-color: #00c8ff; }
  label { display: block; font-size: 0.85rem; color: #aaa; margin-bottom: 6px; }
  .hint { color: #444; font-size: 0.75rem; margin-top: 20px; text-align: center; }
</style>
"""

LOGIN_TEMPLATE = """
<!DOCTYPE html><html><head><title>SecureBank</title>""" + BASE_STYLE + """</head><body>
<div style="display:flex;justify-content:center;align-items:center;height:100vh;">
  <div class="card" style="width:360px;">
    <div style="text-align:center;margin-bottom:28px;">
      <h1 style="color:#00c8ff;font-size:1.6rem;">🏦 SecureBank</h1>
      <p style="color:#666;font-size:0.8rem;margin-top:4px;">Internet Banking</p>
    </div>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <label>Usuário</label>
      <input type="text" name="username" placeholder="seu usuário" autocomplete="off">
      <label>Senha</label>
      <input type="password" name="password" placeholder="••••••••">
      <button class="btn" style="width:100%;padding:12px;">Entrar</button>
    </form>
    <p class="hint">Use: pedro / pedro123</p>
  </div>
</div>
</body></html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html><html><head><title>SecureBank — Dashboard</title>""" + BASE_STYLE + """</head><body>
<div class="navbar">
  <h2>🏦 SecureBank</h2>
  <span>Olá, {{ username }} &nbsp;|&nbsp; <a href="/logout">Sair</a></span>
</div>
<div class="container">
  <div class="card">
    <h3>💳 Minha Conta</h3>
    <p class="tipo">{{ conta.tipo }}</p>
    <p class="saldo">R$ {{ "%.2f"|format(conta.saldo) }}</p>
    <p style="font-size:0.8rem;color:#555;margin-top:8px;">Conta #{{ conta.id }}</p>
  </div>

  <div class="card">
    <h3>📋 Últimas Transações</h3>
    <table>
      <tr><th>Descrição</th><th style="text-align:right;">Valor</th></tr>
      {% for t in transacoes %}
      <tr>
        <td>{{ t.descricao }}</td>
        <td style="text-align:right;" class="{{ 'pos' if t.valor > 0 else 'neg' }}">
          R$ {{ "%.2f"|format(t.valor) }}
        </td>
      </tr>
      {% endfor %}
    </table>
  </div>

  <div class="card">
    <h3>🔍 Buscar conta por ID</h3>
    <p style="color:#666;font-size:0.85rem;margin-bottom:16px;">
      Consulte informações de qualquer conta pelo número.
    </p>
    <form method="GET" action="/conta">
      <label>ID da Conta</label>
      <input type="text" name="id" placeholder="ex: 1" style="width:200px;display:inline-block;margin-bottom:0;margin-right:10px;">
      <button class="btn">Buscar</button>
    </form>
  </div>
</div>
</body></html>
"""

CONTA_TEMPLATE = """
<!DOCTYPE html><html><head><title>SecureBank — Conta</title>""" + BASE_STYLE + """</head><body>
<div class="navbar">
  <h2>🏦 SecureBank</h2>
  <span>Olá, {{ session_user }} &nbsp;|&nbsp; <a href="/logout">Sair</a></span>
</div>
<div class="container">
  {% if error %}
  <div class="error">{{ error }}</div>
  {% else %}
  <div class="card">
    <h3>💳 Dados da Conta #{{ conta.id }}</h3>
    <table>
      <tr><th>Campo</th><th>Valor</th></tr>
      <tr><td>Titular</td><td><strong>{{ dono.username }}</strong></td></tr>
      <tr><td>Email</td><td>{{ dono.email }}</td></tr>
      <tr><td>Tipo</td><td>{{ conta.tipo }}</td></tr>
      <tr><td>Saldo</td><td class="{{ 'pos' if conta.saldo > 0 else 'neg' }}"><strong>R$ {{ "%.2f"|format(conta.saldo) }}</strong></td></tr>
    </table>
  </div>

  <div class="card">
    <h3>📋 Extrato</h3>
    <table>
      <tr><th>Descrição</th><th style="text-align:right;">Valor</th></tr>
      {% for t in transacoes %}
      <tr>
        <td>{{ t.descricao }}</td>
        <td style="text-align:right;" class="{{ 'pos' if t.valor > 0 else 'neg' }}">
          R$ {{ "%.2f"|format(t.valor) }}
        </td>
      </tr>
      {% endfor %}
    </table>
  </div>
  {% endif %}
  <p><a href="/dashboard">← Voltar</a></p>
</div>
</body></html>
"""

# ─────────────────────────────────────────────
#  ROTAS
# ─────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session["user_id"]  = user[0]
            session["username"] = user[1]
            return redirect("/dashboard")
        return render_template_string(LOGIN_TEMPLATE, error="Usuário ou senha incorretos.")
    return render_template_string(LOGIN_TEMPLATE, error=None)

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM contas WHERE user_id=?", (session["user_id"],))
    conta = c.fetchone()
    c.execute("SELECT * FROM transacoes WHERE conta_id=?", (conta[0],))
    rows = c.fetchall()
    conn.close()
    transacoes = [{"descricao": r[2], "valor": r[3]} for r in rows]
    conta_obj  = {"id": conta[0], "saldo": conta[2], "tipo": conta[3]}
    return render_template_string(DASHBOARD_TEMPLATE,
        username=session["username"],
        conta=conta_obj,
        transacoes=transacoes)

@app.route("/conta")
def ver_conta():
    if "user_id" not in session:
        return redirect("/")

    conta_id = request.args.get("id", "")

    # ⚠️ VULNERABILIDADE INTENCIONAL: IDOR
    # Não verifica se a conta pertence ao usuário logado.
    # Qualquer usuário autenticado pode ver qualquer conta só passando o ID.

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM contas WHERE id=?", (conta_id,))
    conta = c.fetchone()

    if not conta:
        conn.close()
        return render_template_string(CONTA_TEMPLATE,
            session_user=session["username"], error="Conta não encontrada.", conta=None, dono=None, transacoes=[])

    c.execute("SELECT * FROM users WHERE id=?", (conta[1],))
    dono = c.fetchone()
    c.execute("SELECT * FROM transacoes WHERE conta_id=?", (conta[0],))
    rows = c.fetchall()
    conn.close()

    transacoes = [{"descricao": r[2], "valor": r[3]} for r in rows]
    conta_obj  = {"id": conta[0], "saldo": conta[2], "tipo": conta[3]}
    dono_obj   = {"username": dono[1], "email": dono[3]}

    return render_template_string(CONTA_TEMPLATE,
        session_user=session["username"],
        conta=conta_obj,
        dono=dono_obj,
        transacoes=transacoes,
        error=None)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    print("\n" + "="*50)
    print("  🎯 LAB IDOR — SecureBank v2")
    print("="*50)
    print("  Acesse: http://localhost:5000")
    print("  Login:  pedro / pedro123")
    print("="*50 + "\n")
    app.run(debug=False, port=5000)
