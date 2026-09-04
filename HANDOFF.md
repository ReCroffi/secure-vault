<!-- Nota temporária de handoff entre sessões/máquinas. Pode apagar quando não precisar mais. -->

# Handoff — onde paramos

Recado pra próxima sessão do Claude Code (outra máquina ou sessão nova).

## Antes de fazer qualquer coisa

Leia `feedback-teaching-style.md` na memória (`~/.claude/projects/.../memory/`), se existir nesta máquina. Se não existir, **recrie a partir do resumo abaixo** — foi o que aconteceu na sessão do desktop, a memória não estava lá.

- **Nunca escreva código de aplicação por conta própria.** Explique o conceito, dê a assinatura da função e o que ela precisa fazer, e deixe o usuário escrever. Revise e aponte erros com precisão, sem reescrever por ele.
- **Exceção:** infra/config (`.gitignore`, `docker-compose.yml`, `.vscode/settings.json`, `pyproject.toml`, README, este arquivo) e **docstrings** — o usuário já delegou docstrings explicitamente e várias vezes.
- **Comandos de git e comandos de CLI que são o ponto da lição são o usuário quem roda** — a menos que ele delegue ("faz isso pra mim", "faz pra mim"), o que acontece com alguma frequência.
- **Passos pequenos, ritmo de confirmação:** explica um pedaço → usuário escreve → Claude revisa → repete.
- O usuário é disléxico — feedback com mais de um ponto vai **numerado e separado**, nunca numa frase corrida.
- Ele pede a mensagem de commit pronta ("sou ruim pra msg"). Padrão do repo: conventional commits, português sem acento, `feat(vault):` / `fix(...)` / `docs:`.

## Ambiente nesta máquina (desktop) — já resolvido

- `.env` criado a partir do `.env.example` (senha local em `.env`, gitignored — não repetir aqui).
- Postgres de pé via `docker compose up -d` (container `secure-vault-db`, volume `vault_pgdata`).
- Migrations aplicadas (`alembic upgrade head`).
- Senha mestra de teste: definida localmente ao rodar `init`, não versionar aqui.
- Banco tem 2 credenciais de teste, ambas `github` (`renan` id=1, `renan-trabalho` id=2). A senha da id=1 foi trocada várias vezes em teste.
- `.vscode/settings.json` (gitignored, local): Error Lens desligado, ghost text de IA desligado, ruff com format + fixAll + organizeImports no `Ctrl+S`, interpretador apontando pro `.venv`.
- Copilot **não está instalado** nesta máquina; quem dá ghost text é a extensão `openai.chatgpt`.

**Numa máquina nova, repetir:** `cp .env.example .env` (preencher a senha nos 2 lugares) → `docker compose up -d` → `uv run alembic upgrade head` → `uv run secure-vault init`.

## Estado do projeto

Branch: `feature/05-crud-credenciais`. Fases 0-4 mergeadas em `develop`.

**Fase 5 (CRUD de credenciais) — quase fechada.** Comandos prontos, testados ponta a ponta:

| comando | estado |
|---|---|
| `init`, `add` | ok (o `add` agora autentica antes de pedir a senha do serviço) |
| `get <service_name>` | ok — decifra e mostra; sai com 1 se não achar |
| `list` | ok — mostra id, serviço e login, **sem senha**; sai com 0 se o vault estiver vazio |
| `delete <id>` | ok — mostra serviço/login na confirmação antes de apagar |
| `update <id>` | funciona, **mas falta o pedaço C** (ver abaixo) |

Funções em `src/vault/db/credentials.py`: `save_credential`, `get_credentials_by_service`, `get_all_credentials`, `delete_credential`, `update_credential_password`, `get_credential_by_id`. Todas com docstring.

### PRÓXIMO PASSO — pedaço C da tarefa 3

O `update` ainda pede a senha nova **sem dizer de quem ela é**. Se errar o id, troca a senha da credencial errada.

Falta, no `update_credential` (em `src/vault/cli/__init__.py`), entre o `key = _get_key()` e o prompt da senha nova:

1. buscar com `get_credential_by_id(credential_id)`;
2. se `None` → `typer.echo("Não encontrado")` + `raise typer.Exit(code=1)`;
3. se achou → `typer.echo` mostrando serviço e login;
4. só então pedir a senha nova. O resto fica igual.

O `delete` já foi ajustado assim e serve de modelo. **Sem `typer.confirm` aqui** — no `update` o usuário ainda digita a senha nova duas vezes, o que já confirma a intenção; confirmação demais vira ruído e ensina a ignorar a do `delete`, que importa.

### Depois disso

Fase 5 fechada → **primeiro merge pra `main`** (é o marco previsto no roteiro).

Ideias já levantadas, nenhuma bloqueante:
- `pyperclip` (já está nas dependências) pra copiar a senha no `get` em vez de imprimir na tela.
- `[tool.ruff]` no `pyproject.toml` — hoje o ruff roda só com as regras padrão.
- `src/vault/db/engine.py` tem um `I001` pré-existente (falta linha em branco entre os grupos de import). Abrir o arquivo e dar `Ctrl+S` resolve.
- **Multi-usuário (fora do roteiro das 11 fases, ideia futura):** hoje o vault é single-user — `vault_config` tem uma linha só (`scalar_one()` quebraria com mais de uma) e `credentials` não tem FK pra dono nenhum. Se dois usuários do mesmo PC usassem o app, os dois decifrariam as mesmas credenciais com a mesma senha mestra, sem isolamento. Pra suportar isso: tabela de usuários, cada um com seu próprio `salt`/hash (chave de cifragem derivada por usuário), e `credentials` ganhando `user_id` como FK — toda query passaria a filtrar por ele. É migration nova, não é ajuste pequeno.

## Roteiro e decisões de design

- Roteiro completo (11 fases): https://claude.ai/code/artifact/85e9fb4e-3d11-4b18-9f6e-9c5e23152295
- **Fase 4:** HKDF trocado por Argon2id em modo raw (`hash_secret_raw`) — HKDF não tem custo por tentativa, o que anularia a proteção contra força bruta na chave de cifragem.
- **Fase 5:** busca por serviço devolve `list[Credential]`, não um objeto — `service_name` não tem constraint de unicidade, o mesmo serviço pode ter vários logins.
- **Fase 5:** `delete` e `update` identificam por `id`, não por `service_name` — apagar por nome levaria todos os logins do serviço junto.
- **Fase 5:** `get` consulta o banco **antes** de pedir a senha mestra (não autentica à toa se o serviço não existe). `list`, `delete` e `update` autenticam **antes** de consultar, porque a saída deles é informação sensível.
- **Fase 5:** as buscas têm `ORDER BY` (`id`, e `service_name, id` no `get_all_credentials`) — sem isso o Postgres reembaralha a listagem a cada `UPDATE`.

## Conceitos que já foram explicados (não precisa repetir do zero)

`select`/`where` com coluna à esquerda e valor à direita · `.scalars().all()` · `session.get(Classe, pk)` · unit of work (atribuir ao atributo + `commit` gera o `UPDATE`) · `raise typer.Exit(code=1)` (a classe sozinha não faz nada) · `@app.command("nome")` pra separar o nome do comando do nome da função · guard clause.

**Ponto que ainda escorrega:** confundir o **argumento** de uma função com o seu **retorno** (apareceu 3x — `session.get`, `get_credential_by_id`). Quando acontecer, ler a assinatura separando pela seta: "recebe X → devolve Y".
