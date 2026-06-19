# API com login

API simples em Flask com cadastro, login, rota protegida e logout.

## Como instalar

No terminal, dentro desta pasta:

```powershell
py -m pip install -r requirements.txt
```

Se o comando `py` nao funcionar, instale o Python em:

https://www.python.org/downloads/

Durante a instalacao, marque a opcao `Add python.exe to PATH`.

## Como rodar

```powershell
py app.py
```

A API vai abrir em:

```text
http://127.0.0.1:5000
```

## Como colocar online no Render

1. Crie uma conta no GitHub.
2. Crie um repositorio e envie estes arquivos:
   - `app.py`
   - `requirements.txt`
   - `README.md`
3. Entre no Render:

```text
https://dashboard.render.com
```

4. Clique em `New` > `Web Service`.
5. Conecte seu repositorio do GitHub.
6. Use estas configuracoes:

```text
Language: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

Quando terminar, o Render vai gerar um link parecido com:

```text
https://seu-projeto.onrender.com
```

Suas rotas online ficarao assim:

```text
POST https://seu-projeto.onrender.com/cadastro
POST https://seu-projeto.onrender.com/login
GET  https://seu-projeto.onrender.com/perfil
POST https://seu-projeto.onrender.com/logout
```

## Rotas

### Cadastro

```http
POST /cadastro
```

Body JSON:

```json
{
  "name": "Kalleb",
  "email": "kalleb@email.com",
  "password": "123456"
}
```

### Login

```http
POST /login
```

Body JSON:

```json
{
  "email": "kalleb@email.com",
  "password": "123456"
}
```

A resposta traz um `token`. Use esse token nas rotas protegidas.

### Perfil

```http
GET /perfil
Authorization: Bearer SEU_TOKEN_AQUI
```

### Logout

```http
POST /logout
Authorization: Bearer SEU_TOKEN_AQUI
```
