<!-- Nota temporária de handoff entre sessões/máquinas. Pode apagar quando não precisar mais. -->

# Handoff — onde paramos

Recado pra próxima sessão do Claude Code (outra máquina ou sessão nova). Atualizado em 07/09/2026.

**Projeto fechado por hora ao final da Fase 9.** App funcional (CLI + TUI), cobertura de testes completa. Fase 10 virou sugestão de melhoria futura, não é mais fase obrigatória do roteiro — ver seção própria abaixo.

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

Branch atual: `feature/09-tui`. Fase 9 concluída (CRUD completo + suite de testes da TUI) — falta abrir a PR `feature/09-tui → develop` e depois `develop → main` (o usuário roda esses comandos, ver regra acima sobre falsa delegação). `develop`/`main` continuam em `50b17d3` (05/09/2026) até essa PR — o segundo merge `develop → main` (PR #15) fechou o release de testes automatizados + Fases 6, 7 e 8.

**Sobre o `delete_branch_on_merge: true` do GitHub:** numa PR `develop → main`, o GitHub trata `develop` como "branch de origem" e apaga ela do remoto. Já aconteceu duas vezes (Fase 5 e agora de novo) e nas duas foi preciso recriar (`git reset --hard main` na `develop` local + `git push origin develop`). **Vai se repetir na próxima PR `develop → main`** — avisar o usuário antes, mas ele já sabe o procedimento.

Fases concluídas e já mergeadas em `develop` **e em `main`** (cada uma foi feature branch → PR → merge, branch local apagada depois):

- Fases 0-5: setup, Postgres/`.env`, schema+Alembic, criação do vault, autenticação, CRUD de credenciais.
- **Testes automatizados** (fase extra, inserida antes da 6): banco `vault_test` isolado, `Settings.test_database_url`, fixtures `db_engine`/`patch_session` (autouse, monkeypatch + limpeza) em `tests/conftest.py`, CI no GitHub Actions (`.github/workflows/ci.yml`, roda em push/PR de `main`/`develop`).
- **Fase 6** — gerador de senha configurável: `generate_password` (`src/vault/core/generator.py`, usa `secrets`), comando `secure-vault generate`.
- **Fase 7** — indicador de força de senha: `check_password_strength` (`src/vault/core/strength.py`, usa `zxcvbn`), helper `_prompt_password_with_strength_check` na CLI, usado em `add`/`update` (mostra a força, insiste se for fraca, a menos que o usuário confirme usar mesmo assim).
- **Fase 8** — busca/filtro de credenciais: `search_credentials_by_service(term: str) -> list[Credential]` (`src/vault/db/credentials.py`, `ILIKE`), comando `list --search`. Primeira vez com TDD de verdade no projeto (teste escrito antes da função).

Suite de testes atual: 26 testes, todos passando (`tests/integration/` pra tudo que toca banco, `tests/unit/` pra funções puras — gerador e força de senha, `tests/tui/` pra interface Textual).

### Fase 9 — interface TUI (`textual`): CONCLUÍDA (CRUD completo + testes)

Brainstorm de arquitetura já feito e aprovado: chave derivada guardada em `self.app.key` (uma vez por sessão, não recalculada por comando como na CLI), pacote `src/vault/tui/` com `app.py` + um arquivo por tela em `screens/`, entry point `secure-vault tui`. Nenhuma lógica de negócio foi duplicada — todas as telas chamam as mesmas funções de `core/`/`db/` que a CLI usa.

Telas prontas (`login.py`, `list.py`, `detail.py`, `add.py`, `confirm.py`, `edit.py`) — listar, buscar ao vivo, ver detalhe, adicionar, apagar (com modal de confirmação), editar senha, tudo reaproveitando o aviso de força de senha (`check_password_strength`) igual ao CLI. Detalhes de implementação e os dois bugs reais encontrados no caminho (erro de login mudo por causa de `print()`; crash ao apagar por causa da ordem de execução do `dismiss()` do Textual) estão registrados na memória — ver `project_secure_vault_state.md`.

**Testes da TUI concluídos** (`tests/tui/`, 8 testes): `test_login.py` (senha certa avança, senha errada não avança), `test_list.py` (popula tabela, busca ao vivo), `test_add.py`, `test_detail.py` (decifra e mostra), `test_edit.py`, `test_delete.py` (apagar com confirmação via `ConfirmScreen`). Usam o harness `Pilot`/`app.run_test()` do Textual (precisou de `pytest-asyncio`, `@pytest.mark.asyncio` em cada teste). Padrão usado pra "clicar" numa linha da `DataTable` sem mirar coordenada de pixel: pegar o widget com `query_one` e chamar `.focus()` direto nele, depois `pilot.press("enter")` (cursor já começa na primeira linha).

**Fixture reforçado:** `patch_session` (`tests/conftest.py`) agora limpa as tabelas **antes e depois** de cada teste (função `_limpar_tabelas(engine)` extraída, chamada nos dois pontos) — protege contra sujeira de um teste anterior que tenha travado antes do teardown normal rodar.

**Flakiness rara observada e investigada (não é bug de lógica):** rodando a suite de `tui/` em lote (~60 execuções), 2 falharam de forma não determinística, sempre com o dado certo já salvo no banco no momento da falha — indica corrida de tempo entre o Textual e o assert do teste (não reproduzida isolando o teste nem instrumentando a tela). Taxa baixa (~3-5%), não bloqueou o fechamento da fase. Se voltar a incomodar (especialmente no CI), o próximo passo seria trocar os `pilot.pause()` por uma espera mais robusta.

**Próximo passo real: abrir a PR.** `feature/09-tui → develop`, depois `develop → main` — o roteiro marcava a Fase 9 como "versão apresentável visualmente, bom momento pra GIF/screenshot no README"; já existe um GIF de 05/09/2026 (login+lista+busca, ver memória) — considerar gerar um novo mostrando o CRUD completo, se o usuário quiser, mas não é bloqueante.

### Fase 10 — sugestão futura (não é mais fase obrigatória do roteiro)

Decidido em 07/09/2026: o projeto foi considerado completo e fechado ao final da Fase 9. A Fase 10 saiu do roteiro obrigatório e virou backlog de melhorias, sem compromisso de retomar. Se o usuário voltar a esse projeto no futuro, os itens são:

- Timeout de sessão: expirar a chave em memória depois de N minutos de inatividade.
- Clipboard com auto-clear (`pyperclip`, já nas dependências).
- 2FA na senha mestra via TOTP (`pyotp`, já nas dependências).
- `pyperclip` pra copiar a senha no `get` em vez de imprimir na tela.
- `[tool.ruff]` no `pyproject.toml` — hoje o ruff roda só com regras padrão. Tem 6 erros pré-existentes (migrations do Alembic, `Union` em vez de `|`; e um `I001` em `src/vault/db/engine.py`), nenhum deles das fases recentes.
- **Multi-usuário** (fora do roteiro, ideia futura): hoje o vault é single-user — `vault_config` tem uma linha só e `credentials` não tem FK pra dono nenhum. Precisaria de tabela de usuários, salt/hash por usuário, e `user_id` como FK em `credentials`. Migration nova, não é ajuste pequeno.

## Roteiro e decisões de design

- Roteiro completo (10 fases obrigatórias + 1 de sugestões futuras): https://claude.ai/code/artifact/85e9fb4e-3d11-4b18-9f6e-9c5e23152295
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

Conceitos de Textual (Fase 9): `App`/`Screen`, `compose()`/`yield`, `on_mount`, `push_screen`/`switch_screen`/`pop_screen`, `query_one("#id", Tipo)`, `DataTable`, `Input.Submitted` vs `Input.Changed`, `BINDINGS`+`action_<nome>`, `self.notify(msg, severity=...)`, `on_screen_resume` (dispara quando uma tela empilhada por cima fecha e essa volta a ficar ativa — `on_mount` só roda uma vez, na primeira montagem), `ModalScreen[T]` + `self.dismiss(valor)` + `push_screen(tela, callback)`.

Conceitos de teste de Textual (Fase 9, testes): `app.run_test()` como `async with ... as pilot` (sobe a app sem terminal de verdade), `await pilot.press(...)` (aceita string desempacotada `*"texto"` pra "digitar", ou nome de tecla tipo `"enter"`), `await pilot.pause()` (dá tempo do Textual processar antes do assert — sempre dentro do `async with`, nunca depois, senão a app já foi desmontada e `pilot.app.screen` estoura `ScreenStackError`), `@pytest.mark.asyncio` (obrigatório em cada teste `async def`, senão o pytest-asyncio silenciosamente não roda a coroutine), `widget.focus()` chamado direto no objeto (sem `pilot.click`) quando só precisa de foco de teclado, não simular o clique em si, `Static.content` (não `.renderable`) pra ler o texto atual de um `Static`.

**Pontos que já escorregaram mais de uma vez:**
- Confundir o **argumento** de uma função com o seu **retorno** (`session.get`, `get_credential_by_id`). Ler a assinatura separando pela seta: "recebe X → devolve Y".
- O nome da action no `BINDINGS` (segundo item da tupla) tem que bater exatamente com o sufixo do método `action_<nome>` — divergência não dá erro, a tecla só vira no-op silencioso. Aconteceu 2x na Fase 9.
- `event.input.id` (identidade do widget, o que você escolheu no `compose`) não é o mesmo que `event.input.password` (se o campo mascara o texto) — são atributos diferentes que só coincidem por acaso quando só um campo do formulário é de senha.
- `self.app.pop_screen()` dentro de uma callback de `push_screen(tela, callback)`: a callback roda **antes** do `pop_screen()` automático da própria `dismiss()`, então um pop manual ali tira a tela errada da pilha.
