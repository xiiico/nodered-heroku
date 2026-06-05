# CLAUDE.md — Inteligência do Projeto

> Este arquivo é lido automaticamente pelo Claude Code no início de cada sessão.
> Mantenha-o atualizado. É a sua memória persistente com a IA.

---

## Projeto

**Nome:** nodered-heroku  
**Descrição:** Node-RED hospedado na nuvem (Heroku) com integrações via MQTT, MongoDB, PostgreSQL, Redis e Telegram.  
**Repositório:** xiiico/nodered-heroku  
**Owner:** Francisco Silva (eng.franciscohgsilva@gmail.com)

---

## Stack Tecnológica

| Camada | Tecnologia |
|--------|------------|
| Runtime | Node.js 14.x |
| Plataforma de fluxos | Node-RED (latest) |
| Deploy | Heroku (Procfile: `web: npm start`) |
| Banco relacional | PostgreSQL (`node-red-contrib-postgresql`) |
| Banco de documentos | MongoDB (`node-red-contrib-mongodb4`, `node-red-contrib-mongoql`) |
| Cache/Filas | Redis 3.0.2 |
| Mensageria MQTT | Aedes broker (`node-red-contrib-aedes`) |
| Bot | Telegram (`node-red-contrib-telegrambot-home`) |
| UI | Node-RED Dashboard (`node-red-dashboard`) |
| Scheduling | cron-plus, ui-time-scheduler |

---

## Estrutura de Diretórios

```
nodered-heroku/
├── CLAUDE.md                    # Este arquivo — leia sempre primeiro
├── flows.json                   # Fluxos Node-RED (exportados)
├── flows_cred.json              # Credenciais dos fluxos (NÃO commitar valores reais)
├── settings.js                  # Configuração do runtime Node-RED
├── Procfile                     # Comando de start para Heroku
├── package.json                 # Dependências
├── nodes/                       # Nós customizados
├── utils/                       # Scripts utilitários
│   ├── file-explorer-flow.json  # Fluxo utilitário: explorador de arquivos
│   └── save-all-changes-flow.json # Fluxo utilitário: salvar mudanças
├── public/                      # Assets estáticos servidos pelo Node-RED
├── docs/
│   └── templates/               # Templates de tarefas e sessões
│       ├── task-brief.md        # Como definir uma tarefa para a IA
│       └── session-start.md     # Como iniciar uma sessão produtiva
└── .claude/
    ├── settings.json            # Configuração do Claude Code (permissões, hooks)
    ├── memory/
    │   ├── decisions.md         # Decisões de arquitetura e por quê foram tomadas
    │   └── session-log.md       # Log de sessões — o que foi feito e decidido
    └── skills/
        └── prompt-master/       # Skill: geração de prompts otimizados para qualquer IA
```

---

## Convenções do Projeto

### Flows Node-RED
- Cada flow deve ter um comentário de cabeçalho com: nome, propósito, data de criação
- Nomes de nós em `kebab-case` descritivo (ex: `mqtt-receive-sensor-data`)
- Variáveis de ambiente via `process.env.VAR_NAME` — NUNCA hardcoded
- Credenciais em `Config Vars` no Heroku Dashboard, não no código

### Commits
- Formato: `tipo: descrição curta em português`
- Tipos: `feat`, `fix`, `refactor`, `docs`, `config`
- Exemplo: `feat: adicionar agendador de relatórios diários`

### Segurança
- NUNCA commitar valores reais em `flows_cred.json`
- NUNCA incluir tokens, senhas ou connection strings no código
- Variáveis sensíveis somente via Heroku Config Vars

---

## Framework de Trabalho com IA

### Regras de Sessão (leia antes de cada sessão)

1. **Uma tarefa por sessão** — foco em um entregável concreto
2. **Frente-carregar contexto** — forneça tudo na primeira mensagem: objetivo, arquivos relevantes, restrições, critério de pronto
3. **Memory Block** — em tarefas com histórico, use o template em `docs/templates/session-start.md`
4. **Stop conditions** — sempre defina quando a IA deve parar e pedir aprovação
5. **Não toque em** — liste explicitamente o que NÃO pode ser alterado

### Critério de "Pronto"
Uma tarefa está completa quando:
- O fluxo foi testado e está funcional
- O `CLAUDE.md` foi atualizado com decisões novas
- O `session-log.md` foi atualizado com o que foi feito
- As mudanças foram commitadas com mensagem clara

### Skill Disponível
- `/prompt-master` — gera prompts otimizados para qualquer ferramenta de IA (Claude, GPT, Midjourney, Cursor, etc.)

---

## Decisões de Arquitetura

> Ver detalhes completos em `.claude/memory/decisions.md`

| # | Decisão | Motivo |
|---|---------|--------|
| 1 | Node-RED como plataforma de fluxos | Visual, rápido para prototipagem, rico em integrações |
| 2 | Heroku como deploy | Simplicidade de deploy via git, dyno on-demand |
| 3 | MongoDB como principal banco de dados | Flexibilidade para payloads variáveis de IoT/sensores |
| 4 | Redis para filas e cache | Baixa latência para dados em tempo real |
| 5 | Aedes (MQTT broker embedded) | Elimina dependência de broker externo |

---

## Contexto Atual

> Atualize esta seção a cada sessão

**Branch ativo:** `claude/standardized-work-setup-ai-GtIhp`  
**Último trabalho:** Setup inicial do framework de trabalho padronizado com IA  
**Próximo passo:** Definir e implementar primeiro fluxo de produção usando o framework  

---

## Como Iniciar uma Nova Sessão

1. Leia este `CLAUDE.md` (o Claude Code faz isso automaticamente)
2. Leia `.claude/memory/session-log.md` para contexto da última sessão
3. Copie o template `docs/templates/session-start.md` e preencha
4. Cole o Memory Block no início da sua primeira mensagem
