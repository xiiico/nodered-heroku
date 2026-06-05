# Registro de Decisões de Arquitetura

> Mantenha este arquivo atualizado. É a memória de longo prazo do projeto.
> Formato: adicione novas entradas no topo.

---

## Template para Nova Decisão

```
### [DATA] — [Título da decisão]
**Contexto:** Por que esta decisão foi necessária
**Decisão:** O que foi decidido
**Alternativas consideradas:** O que foi descartado e por quê
**Consequências:** O que muda com esta decisão
**Revisitar quando:** Condição que tornaria esta decisão obsoleta
```

---

## Decisões Registradas

### 2026-06-05 — Setup do Framework de Trabalho com IA

**Contexto:** Necessidade de padronizar como trabalhar com Claude Code neste projeto para manter consistência entre sessões e não perder contexto.

**Decisão:** Implementar um framework baseado em:
- `CLAUDE.md` como inteligência central do projeto
- `.claude/memory/` para persistência de contexto entre sessões
- `.claude/skills/prompt-master/` para geração de prompts otimizados
- `docs/templates/` para padronizar como tarefas são definidas

**Alternativas consideradas:**
- Manter contexto só na memória do desenvolvedor → descartado (não escala, não persiste)
- Usar um documento externo (Notion, etc.) → descartado (não integrado ao fluxo de trabalho)

**Consequências:** 
- Cada sessão deve começar lendo o `CLAUDE.md` e o `session-log.md`
- Cada sessão deve terminar atualizando o `session-log.md`

**Revisitar quando:** Mudar de ferramenta de IA ou de repositório principal.

---

### 2026-06-05 — Plataforma: Node-RED no Heroku

**Contexto:** Necessidade de um ambiente de automação visual e integrações rápidas em nuvem.

**Decisão:** Node-RED no Heroku com MongoDB como banco principal.

**Alternativas consideradas:**
- n8n (mais corporativo, mais pesado)
- Zapier/Make (pago por operações, limitado para lógica customizada)

**Consequências:** Deploy via `git push heroku main`. Runtime sempre na versão Node.js 14.x.

**Revisitar quando:** Node-RED lançar breaking changes na API ou Heroku mudar pricing model.
