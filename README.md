# Secure Vault

![CI](https://github.com/ReCroffi/secure-vault/actions/workflows/ci.yml/badge.svg)

<!-- TODO: se quiser trocar o nome do projeto, troca aqui e no diretório/repo -->

> TODO: uma frase de efeito curta descrevendo o projeto (ex: "Gerenciador de senhas local, com criptografia ponta a ponta, feito para aprender segurança na prática").

## Sobre o projeto

Sistema de gerenciamento e geração de senhas seguras, desenvolvido como projeto de portfólio. Permite gerar senhas fortes, armazená-las de forma criptografada e recuperá-las mediante autenticação com uma senha mestra — sem que a senha mestra ou as senhas armazenadas jamais sejam persistidas em texto puro.

## Motivação

<!-- TODO: por que você está construindo isso? o que quer aprender/demonstrar com esse projeto? -->

## Arquitetura de segurança

Esta é a parte mais crítica do projeto — a que diferencia um "CRUD com senha" de um gerenciador de senhas de verdade.

- **Senha mestra nunca é armazenada.** Apenas um hash dela é persistido (para autenticação), gerado com uma função de derivação de chave resistente a força bruta (Argon2id).
- **Chave de criptografia é derivada em memória**, a partir da senha mestra + um salt único, e nunca é persistida em disco.
- **Toda credencial salva é criptografada simetricamente** (AES via a biblioteca `cryptography`) antes de tocar o banco de dados. Sem a senha mestra correta, os dados no Postgres são inúteis mesmo para quem tiver acesso direto ao banco.
- **Geração de senhas** usa o módulo `secrets` do Python (CSPRNG), nunca `random`.
- Cada segredo criptografado usa **salt/nonce único** — nunca reaproveitado entre registros.

> Aviso de escopo: este projeto tem fins educacionais/portfólio. Não implementa proteções contra memory dumping, side-channel attacks ou hardening de SO. Isso é declarado intencionalmente — veja a seção "Limitações conhecidas".

## Stack tecnológica

| Camada | Escolha | Motivo |
|---|---|---|
| Linguagem | Python 3.12+ (gerenciado via `uv`) | `requires-python = ">=3.12"` no `pyproject.toml` |
| Empacotamento/deps | `uv` | resolve dependências, lockfile (`uv.lock`) e venv numa ferramenta só |
| Banco de dados | PostgreSQL | Modelagem relacional, migrations, mostra domínio de SQL |
| Driver do banco | `psycopg` (v3, extra `binary`) | driver moderno, mantido ativamente, com suporte a `async` se precisar no futuro |
| ORM / migrations | SQLAlchemy + Alembic | Padrão de mercado; migrations versionadas (Alembic entra na Fase 2) |
| Config | `pydantic-settings` | leitura tipada de variáveis de ambiente (`.env`) |
| Criptografia | `cryptography` (AES / Fernet), `argon2-cffi` (hash + derivação de chave) | Bibliotecas auditadas, nunca "rolar o próprio crypto" |
| CLI | `typer` | CLI com help automático, subcomandos, boa DX |
| Força de senha | `zxcvbn` | estimativa de entropia, não só regra de tamanho |
| Interface (fase 9) | `textual` (TUI) | Visual mais rico sem sair do terminal |
| Extras (fase 10) | `pyperclip`, `pyotp` | clipboard com auto-clear, 2FA via TOTP |
| Testes / lint | `pytest`, `ruff` (dev) | Padrão do ecossistema |

## Estrutura do projeto

```
secure-vault/
├── src/vault/
│   ├── cli/        # comandos da interface de linha de comando
│   ├── core/        # regras de negócio: criptografia, geração de senha, autenticação
│   ├── db/          # models SQLAlchemy, repositórios, sessão do banco
│   └── config/      # carregamento de configuração e variáveis de ambiente
├── tests/
│   ├── unit/
│   └── integration/
├── migrations/       # Alembic
├── docs/
├── scripts/
├── .env.example
└── README.md
```

## Como rodar

Pré-requisitos: [uv](https://docs.astral.sh/uv/) instalado e um PostgreSQL acessível.

```
git clone git@github.com:ReCroffi/secure-vault.git
cd secure-vault
uv sync                    # cria o venv e instala tudo que está travado no uv.lock
cp .env.example .env       # preencher DATABASE_URL com suas credenciais locais
```

### Comandos da CLI

```
uv run secure-vault init                          # cria o vault, define a senha mestra
uv run secure-vault add <service_name> <username>  # guarda uma credencial (pede a senha do serviço)
uv run secure-vault get <service_name>             # mostra as credenciais de um serviço, com a senha decifrada
uv run secure-vault list                           # lista id, serviço e login de tudo, sem revelar senha
uv run secure-vault list --search <termo>          # lista só os serviços cujo nome contém o termo (sem diferenciar maiúscula/minúscula)
uv run secure-vault update <id>                    # troca a senha de uma credencial (mostra de quem antes)
uv run secure-vault delete <id>                    # apaga uma credencial (pede confirmação)
uv run secure-vault generate                       # gera uma senha aleatoria (nao salva nada)
```

`generate` aceita `--length` e as flags `--use-uppercase`/`--use-lowercase`/`--use-digits`/`--use-symbols` (e seus opostos `--no-use-*`), todas ligadas por padrão. Sai com código 1 se todas vierem desligadas. Ver `uv run secure-vault generate --help`.

`add` e `update` mostram a força da senha digitada (nota de 0 a 4, via `zxcvbn`) e insistem enquanto ela vier fraca (nota abaixo de 3) — a menos que você confirme explicitamente que quer usar mesmo assim.

Todo comando que acessa dados pede a senha mestra. Use `list` para descobrir o `id` de uma credencial antes de `update`/`delete`.

## Testes

Os testes rodam contra um banco isolado (`vault_test`), no mesmo Postgres do ambiente de desenvolvimento — nunca contra o banco real.

```
docker exec secure-vault-db psql -U croffiadm -d postgres -c "CREATE DATABASE vault_test;"   # só na primeira vez
# preencher TEST_DATABASE_URL no .env, apontando pro vault_test
DATABASE_URL=<TEST_DATABASE_URL do seu .env> uv run alembic upgrade head                      # só na primeira vez / após novas migrations
uv run pytest tests/ -v
```

A fixture `patch_session` (`tests/conftest.py`) troca a sessão do banco pela de teste automaticamente e limpa as tabelas depois de cada teste — não precisa fazer nada manual entre execuções. O CI (GitHub Actions) roda essa mesma suite a cada push/PR em `main`/`develop`.

## Roadmap

- [x] Fase 0 — Setup do projeto e dependências (`uv`)
- [x] Fase 1 — Conexão com Postgres e configuração via `.env`
- [x] Fase 2 — Modelagem do schema + primeira migration (Alembic)
- [x] Fase 3 — Criação do vault (senha mestra, salt, hash)
- [x] Fase 4 — Autenticação e derivação de chave em memória
- [x] Fase 5 — CRUD de credenciais criptografadas via CLI
- [x] Testes automatizados (Fases 0-5) — banco de testes isolado, cobertura de `credentials.py`, CI no GitHub Actions
- [x] Fase 6 — Gerador de senha configurável
- [x] Fase 7 — Indicador de força de senha
- [x] Fase 8 — Busca/filtro de credenciais
- [ ] Fase 9 — Interface TUI (`textual`)
- [ ] Fase 10 — Extras: timeout de sessão, clipboard com auto-clear, 2FA na senha mestra

<!-- TODO: acompanhar o progresso marcando os checkboxes conforme avança -->

## Limitações conhecidas

<!-- TODO: manter atualizado conforme o projeto evolui — é uma seção que mostra maturidade técnica para quem for avaliar o portfólio -->

## Licença

<!-- TODO: escolher uma licença (MIT é comum para portfólio) -->

## Autor

<!-- TODO: seu nome, link do LinkedIn/GitHub, contato -->
