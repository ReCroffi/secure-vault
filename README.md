# Secure Vault

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
| Linguagem | Python 3.12+ | <!-- TODO: confirmar versão instalada --> |
| Banco de dados | PostgreSQL | Modelagem relacional, migrations, mostra domínio de SQL |
| ORM | SQLAlchemy + Alembic | Padrão de mercado; migrations versionadas |
| Criptografia | `cryptography` (AES / Fernet), Argon2 (`argon2-cffi`) | Bibliotecas auditadas, nunca "rolar o próprio crypto" |
| CLI | `typer` | CLI com help automático, subcomandos, boa DX |
| Interface (fase 2) | `textual` (TUI) | Visual mais rico sem sair do terminal |
| Testes | `pytest` | Padrão do ecossistema |

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

<!-- TODO: preencher conforme o setup for avançando (instalação de dependências, criação do banco, primeiro comando da CLI) -->

## Roadmap

- [ ] Setup do projeto, dependências e conexão com Postgres
- [ ] Modelagem do schema + primeira migration
- [ ] Criação de vault (definição de senha mestra, salt, hash)
- [ ] Autenticação e derivação de chave em memória
- [ ] CRUD de credenciais criptografadas via CLI
- [ ] Gerador de senha configurável
- [ ] Indicador de força de senha
- [ ] Busca/filtro de credenciais
- [ ] Interface TUI (`textual`)
- [ ] Extras: timeout de sessão, clipboard com auto-clear, 2FA na senha mestra

<!-- TODO: acompanhar o progresso marcando os checkboxes conforme avança -->

## Limitações conhecidas

<!-- TODO: manter atualizado conforme o projeto evolui — é uma seção que mostra maturidade técnica para quem for avaliar o portfólio -->

## Licença

<!-- TODO: escolher uma licença (MIT é comum para portfólio) -->

## Autor

<!-- TODO: seu nome, link do LinkedIn/GitHub, contato -->
