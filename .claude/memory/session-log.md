# Log de Sessões

> Registro cronológico do que foi feito em cada sessão. Entradas mais recentes no topo.
> Leia sempre antes de começar uma nova sessão.

---

## Template para Nova Sessão

```
### [DATA] — [Título da tarefa]
**Objetivo:** O que foi pedido
**O que foi feito:**
- item 1
- item 2
**Arquivos alterados:** lista de arquivos
**Decisões tomadas:** decisões que devem persistir
**Pendências / próximo passo:** o que ficou para depois
**Branch:** nome do branch usado
```

---

## Sessões

### 2026-10-16 — Novo projeto: tower defense "Rota de Defesa" (APK Android)
**Objetivo:** Jogo no estilo Fieldrunners 2 jogável no celular via APK.

**O que foi feito:**
- Recusada a engenharia reversa do Fieldrunners 2 (direitos autorais). Criado um jogo original com a mesma mecânica de mazing.
- `tower-defense/`: jogo em HTML5 Canvas (3 mapas, 4 torres com 3 níveis, 5 inimigos, pathfinding Dijkstra em 8 direções).
- Empacotamento com Capacitor 6 e workflow `.github/workflows/tower-defense-apk.yml` que gera o APK debug como artifact.
- Balanceamento validado por simulação headless (IA gulosa venceu os 3 mapas).

**Decisões tomadas:**
- Repositório próprio não pôde ser criado (integração sem permissão). Projeto fica temporariamente neste repo.
- Sem frameworks de jogo, para não ter dependências em runtime e funcionar offline no WebView.

**Pendências / próximo passo:** Mover para repositório próprio; testar no celular; lista de melhorias do usuário.

**Branch:** `ccr-086a19af-55cmp1`

---

### 2026-06-05 — Setup do Framework de Trabalho Padronizado com IA

**Objetivo:** Criar um setup completo e padronizado de trabalho com Claude Code, incluindo memória persistente, templates, skill de prompts e configurações.

**O que foi feito:**
- Criado `CLAUDE.md` com inteligência completa do projeto
- Criado `.claude/settings.json` com permissões para comandos comuns
- Criado `.claude/memory/decisions.md` para registro de decisões de arquitetura
- Criado `.claude/memory/session-log.md` (este arquivo)
- Instalado skill `prompt-master` em `.claude/skills/prompt-master/`
- Criado `docs/templates/task-brief.md` para definição padronizada de tarefas
- Criado `docs/templates/session-start.md` para início padronizado de sessões

**Arquivos alterados:**
- `CLAUDE.md` (criado)
- `.claude/settings.json` (criado)
- `.claude/memory/decisions.md` (criado)
- `.claude/memory/session-log.md` (criado)
- `.claude/skills/prompt-master/SKILL.md` (instalado)
- `.claude/skills/prompt-master/references/templates.md` (instalado)
- `.claude/skills/prompt-master/references/patterns.md` (instalado)
- `docs/templates/task-brief.md` (criado)
- `docs/templates/session-start.md` (criado)

**Decisões tomadas:**
- Framework baseado em CLAUDE.md + memory/ + skills/ + templates/
- Skill prompt-master instalada localmente no projeto

**Pendências / próximo passo:** Definir e implementar primeiro fluxo de produção usando o framework.

**Branch:** `claude/standardized-work-setup-ai-GtIhp`
