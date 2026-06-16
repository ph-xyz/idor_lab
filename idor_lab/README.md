# 🎯 Lab IDOR — SecureBank v2

## Como rodar

```bash
python app.py
```

Acesse: http://localhost:5000

---

## Seu login

```
usuário: pedro
senha:   pedro123
```

---

## Missão

Você é o Pedro. Sua conta é a **#1** com saldo de R$ 1.500,00.

O sistema tem mais 3 contas cadastradas. Consegue ver o saldo e o extrato delas?
Você **não deveria** ter acesso. Mas consegue.

---

## Spoiler

<details>
<summary>Ver solução</summary>

Na tela de dashboard tem um campo "Buscar conta por ID".

O endpoint `/conta?id=1` retorna sua conta.

Tente:
- `/conta?id=2`
- `/conta?id=3`
- `/conta?id=4`

O servidor **não verifica** se a conta pertence a você.
Só recebe o ID, busca no banco e devolve — qualquer conta, de qualquer usuário.

Isso é IDOR: você controla o ID diretamente e o servidor confia sem validar.

**Em um sistema real:** você veria saldo, extrato, e-mail e nome de qualquer cliente do banco.

</details>
