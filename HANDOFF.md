<!-- Nota temporária de handoff entre sessões/máquinas. Pode apagar quando não precisar mais. -->

# Handoff — onde paramos

Recado pra próxima sessão do Claude Code (outra máquina ou sessão nova). Atualizado em 05/09/2026, no desktop.

## Antes de fazer qualquer coisa

Leia `feedback-teaching-style.md` e `projeto-secure-vault.md` na memória (`~/.claude/projects/.../memory/`), se existirem nesta máquina — a memória é local por máquina. Se não existir, recrie a partir do resumo abaixo.

- **Nunca escreva código de aplicação por conta própria.** Explique o conceito, dê a assinatura da função e o que ela precisa fazer, e deixe o usuário escrever. Revise e aponte erros com precisão, sem reescrever por ele.
- **Exceção:** infra/config (`.gitignore`, `docker-compose.yml`, `.github/workflows/*`, `.vscode/settings.json`, `pyproject.toml`, README, este arquivo) e **docstrings** — o usuário já delegou docstrings explicitamente e várias vezes.
- **Comandos de git, GitHub (PR/merge) e CLI que são o ponto da lição são o usuário quem roda** — a menos que ele delegue explicitamente ("faz isso pra mim", "faz você"). Cuidado com falsa delegação: "vamo fazer o commit"/"vamos de PR e merge" **não é** pedir pra rodar o comando, é só concordância de que chegou a hora — prepare o comando/mensagem e devolva pra ele rodar.
- **Passos pequenos, ritmo de confirmação:** explica um pedaço → usuário escreve → Claude revisa → repete.
- O usuário é disléxico — feedback com mais de um ponto vai **numerado e separado**, nunca numa frase corrida.
- Ele pede a mensagem de commit e o título/descrição de PR prontos ("sou ruim pra msg"). Padrão do repo: conventional commits, português sem acento, `feat(vault):` / `fix(...)` / `test(vault):` / `docs:`.
- Ele esquece com frequência: o comando de rodar a suite de testes, e o de rodar o app. Relembrar proativamente sem esperar ele perguntar. Ambos estão também na "Cola do Terminal" (ver abaixo).

## Ambiente numa máquina nova

1. `cp .env.example .env`, preencher `DATABASE_URL` (usuário/senha reais do Postgres local).
2. `docker compose up -d` (sobe o Postgres, container `secure-vault-db`).
3. `uv sync`, `uv run alembic upgrade head` (aplica migrations no banco de dev).
4. `uv run secure-vault init` (cria o vault, define a senha mestra).
5. Pra rodar a suite de testes, precisa **também** de um banco `vault_test`:
   ```
   docker exec secure-vault-db psql -U <usuario> -d postgres -c "CREATE DATABASE vault_test;"
   ```
   Preencher `TEST_DATABASE_URL` no `.env` (mesmo usuário/senha, banco `vault_test`), depois:
   ```
   DATABASE_URL=<TEST_DATABASE_URL do .env> uv run alembic upgrade head
   uv run pytest tests/ -v
   ```

Referência rápida (comandos, pegadinhas de terminal, conceitos que já escorregaram): **Cola do Terminal** — https://claude.ai/code/artifact/37b1ceed-2da7-493e-a34f-a567d0223dfb

## Estado do projeto

Branch: `develop`, sincronizada com `origin/develop` **e com `main`** — ambas em `50b17d3` (05/09/2026). O segundo merge `develop → main` (PR #15) já aconteceu, fechando o release de testes automatizados + Fases 6, 7 e 8.

**Sobre o `delete_branch_on_merge: true` do GitHub:** numa PR `develop → main`, o GitHub trata `develop` como "branch de origem" e apaga ela do remoto. Já aconteceu duas vezes (Fase 5 e agora de novo) e nas duas foi preciso recriar (`git reset --hard main` na `develop` local + `git push origin develop`). **Vai se repetir na próxima PR `develop → main`** — avisar o usuário antes, mas ele já sabe o procedimento.

Fases concluídas e já mergeadas em `develop` **e em `main`** (cada uma foi feature branch → PR → merge, branch local apagada depois):

- Fases 0-5: setup, Postgres/`.env`, schema+Alembic, criação do vault, autenticação, CRUD de credenciais.
- **Testes automatizados** (fase extra, inserida antes da 6): banco `vault_test` isolado, `Settings.test_database_url`, fixtures `db_engine`/`patch_session` (autouse, monkeypatch + limpeza) em `tests/conftest.py`, CI no GitHub Actions (`.github/workflows/ci.yml`, roda em push/PR de `main`/`develop`).
- **Fase 6** — gerador de senha configurável: `generate_password` (`src/vault/core/generator.py`, usa `secrets`), comando `secure-vault generate`.
- **Fase 7** — indicador de força de senha: `check_password_strength` (`src/vault/core/strength.py`, usa `zxcvbn`), helper `_prompt_password_with_strength_check` na CLI, usado em `add`/`update` (mostra a força, insiste se for fraca, a menos que o usuário confirme usar mesmo assim).
- **Fase 8** — busca/filtro de credenciais: `search_credentials_by_service(term: str) -> list[Credential]` (`src/vault/db/credentials.py`, `ILIKE`), comando `list --search`. Primeira vez com TDD de verdade no projeto (teste escrito antes da função).

Suite de testes atual: 18 testes, todos passando (`tests/integration/` pra tudo que toca banco, `tests/unit/` pra funções puras — gerador e força de senha).

### PRÓXIMO PASSO — Fase 9: interface TUI (`textual`)

Não começada — **nenhum brainstorm feito ainda**, diferente da Fase 8 (que já chegou com design aprovado). Antes de escrever qualquer código, fazer o brainstorm de design com o usuário: quais telas/fluxos a TUI cobre, como ela reusa (ou não) as funções de `src/vault/db/` e `src/vault/core/` que já existem, e como a autenticação da senha mestra funciona numa interface que fica aberta (sessão) em vez de um comando que roda e termina.

### Depois da Fase 9

- Fase 10 — Extras: timeout de sessão, clipboard com auto-clear (`pyperclip`, já nas dependências), 2FA na senha mestra (`pyotp`, já nas dependências).
- `pyperclip` pra copiar a senha no `get` em vez de imprimir na tela — ideia levantada, não bloqueante, pode caber em qualquer fase futura.
- `[tool.ruff]` no `pyproject.toml` — hoje o ruff roda só com regras padrão. Tem 6 erros pré-existentes (migrations do Alembic, `Union` em vez de `|`; e um `I001` em `src/vault/db/engine.py`), nenhum deles das fases recentes.
- **Multi-usuário** (fora do roteiro das 11 fases, ideia futura): hoje o vault é single-user — `vault_config` tem uma linha só e `credentials` não tem FK pra dono nenhum. Precisaria de tabela de usuários, salt/hash por usuário, e `user_id` como FK em `credentials`. Migration nova, não é ajuste pequeno.

## Roteiro e decisões de design

- Roteiro completo (11 fases): https://claude.ai/code/artifact/85e9fb4e-3d11-4b18-9f6e-9c5e23152295
- **Fase 4:** HKDF trocado por Argon2id em modo raw (`hash_secret_raw`) — HKDF não tem custo por tentativa, o que anularia a proteção contra força bruta na chave de cifragem.
- **Fase 5:** busca por serviço devolve `list[Credential]`, não um objeto — `service_name` não tem constraint de unicidade, o mesmo serviço pode ter vários logins.
- **Fase 5:** `delete` e `update` identificam por `id`, não por `service_name` — apagar por nome levaria todos os logins do serviço junto.
- **Fase 5:** `get` consulta o banco **antes** de pedir a senha mestra (não autentica à toa se o serviço não existe). `list`, `delete` e `update` autenticam **antes** de consultar, porque a saída deles é informação sensível.
- **Fase 5:** as buscas têm `ORDER BY` (`id`, e `service_name, id` no `get_all_credentials`) — sem isso o Postgres reembaralha a listagem a cada `UPDATE`.
- **Testes:** banco de teste simples — segunda database (`vault_test`) no mesmo container Postgres, não um container separado ("ainda não é um projeto profissional que precisa de todo esse isolamento" — decisão do usuário).
- **Fase 7:** o indicador de força **não bloqueia** o salvamento — só avisa e, se fraca, pede confirmação explícita antes de aceitar.
- **Fase 8:** busca casa só em `service_name`, não em `login` (`OR` no `WHERE` daria resultado surpreendente). Função nova (`search_credentials_by_service`), não parâmetro opcional em `get_all_credentials` (mentiria no nome). `%`/`_` digitados pelo usuário são coringa do `LIKE`, sem escape — aceito de propósito (YAGNI).

## Conceitos que já foram explicados (não precisa repetir do zero)

`select`/`where` com coluna à esquerda e valor à direita · `.scalars().all()` · `session.get(Classe, pk)` · unit of work (atribuir ao atributo + `commit` gera o `UPDATE`) · `raise typer.Exit(code=1)` (a classe sozinha não faz nada) · `@app.command("nome")` pra separar o nome do comando do nome da função · guard clause · fixtures de pytest (`@pytest.fixture`, `yield` pra limpeza, `autouse`) · `monkeypatch.setattr` (corrigir onde é **usado**, não onde é definido) · valor padrão de parâmetro (`= None`, `typer.Option(valor, ...)`) · `while True` com `return`/`break` como ponto de saída · `pytest.raises(..., match=...)` · `ILIKE` (LIKE case-insensitive, extensão do Postgres) · `%` como coringa do LIKE · `.ilike()` como método de coluna no SQLAlchemy.

**Ponto que já escorregou mais de uma vez:** confundir o **argumento** de uma função com o seu **retorno** (`session.get`, `get_credential_by_id`). Quando acontecer, ler a assinatura separando pela seta: "recebe X → devolve Y".
