<!-- Nota temporária de handoff entre sessões/máquinas. Pode apagar este arquivo quando não precisar mais dele. -->

# Handoff — onde paramos

Recado pra sessão do Claude Code no notebook (ou qualquer sessão nova que pegue o projeto a partir daqui).

## Antes de fazer qualquer coisa

Leia `feedback-teaching-style.md` na memória, se ela estiver disponível nesta máquina/sessão (`~/.claude/projects/.../memory/`). Se não estiver, o resumo é:

- **Nunca escreva código de aplicação por conta própria.** Explique o conceito, dê a assinatura da função e o que ela precisa fazer, e deixe o usuário escrever. Revise o que ele escrever e aponte erros com precisão, sem reescrever por ele.
- **Exceção:** arquivos de infra/config (`.gitignore`, `docker-compose.yml`, `.vscode/settings.json`, `pyproject.toml`, README, este próprio arquivo) podem ser escritos direto.
- **Comandos de git (`add`/`commit`/`push`) e comandos de CLI que são o ponto da lição (`uv add`, `alembic`, etc.) são o usuário quem roda**, não o Claude — a menos que ele delegue explicitamente (ex.: teve pressa, pediu pra fazer um commit específico).
- **Passos pequenos, ritmo de confirmação:** explica um pedaço → usuário escreve → usuário confirma → Claude revisa e dá feedback preciso → repete. Não adianta o próximo pedaço antes do atual estar confirmado certo.
- O usuário é disléxico — quando o feedback tiver mais de um ponto, separe numerado/bem distinto, não misture numa frase só corrida.

## Estado do projeto

- Branch atual: `feature/05-crud-credenciais` (a partir de uma `develop` atualizada).
- Fases 0-4 concluídas e mergeadas em `develop` (PRs #1, #2, #3, #5 — o PR #4 foi aberto errado contra `main`, fechado sem merge, ignorem).
- **Fase 5 (CRUD de credenciais) em andamento:**
  - `vault_exists()` e guarda contra `create_vault()` duplicado — feito.
  - Esqueleto da CLI com `typer` (`src/vault/cli/__init__.py`): comando `init`, helper `_get_key()` — feito.
  - `src/vault/core/crypto.py`: `encrypt_password` e `decrypt_password` (Fernet) — feito.
  - `src/vault/db/credentials.py`: `save_credential` — feito.
  - Comando `add` (junta tudo acima) — feito e testado ponta a ponta.
  - **Próximo passo: comando `get`** — buscar uma credencial salva (por `service_name`, provavelmente), decifrar com `decrypt_password` e mostrar pro usuário. Ainda não foi desenhado nem escrito.
  - Depois de `get`: `list`, `update`, `delete`. Fase 5 é o primeiro marco de merge pra `main`.
- Roteiro completo (11 fases) publicado como artefato Claude, deve abrir normal em qualquer sessão logada na mesma conta: https://claude.ai/code/artifact/85e9fb4e-3d11-4b18-9f6e-9c5e23152295
- Senha mestra de teste usada até agora: `1234` (só localmente, não é segredo real).
- Tem uma linha de teste "lixo" na tabela `credentials` (`id=1`, `service_name="teste_servico"`) com dados fake não cifrados de verdade — pode ignorar ou apagar.

## Decisões de design que fogem do roteiro original (já ajustadas no artefato)

- Fase 4 (derivação de chave): trocado HKDF por Argon2id em modo raw (`hash_secret_raw`) — HKDF não tem custo por tentativa, o que anularia a proteção do Argon2 contra força bruta na chave de cifragem.
