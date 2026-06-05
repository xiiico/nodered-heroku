# Template: Início de Sessão

> Use este template no início de cada sessão com Claude Code.
> Cole o bloco preenchido como primeira mensagem.

---

## Quando usar

- Ao iniciar qualquer sessão que tenha histórico de trabalho anterior
- Ao retomar uma tarefa depois de pausa
- Ao começar uma subtarefa de um trabalho maior

---

## Session Start Block

```
## Contexto da Sessão Anterior
- Data da última sessão: [DATA]
- O que foi feito: [resumo de 2-3 linhas]
- Branch: [nome do branch]
- Decisões que devem persistir:
  - [decisão 1]
  - [decisão 2]

## Tarefa desta Sessão
[Descrição clara do que precisa ser feito hoje]

## Estado Atual do Projeto
- Branch ativo: [nome do branch]
- Arquivos relevantes:
  - [arquivo 1] — [estado atual]
  - [arquivo 2] — [estado atual]

## Critério de Pronto
- [ ] [condição 1]
- [ ] [condição 2]
- [ ] session-log.md atualizado
- [ ] Mudanças commitadas no branch correto

## Não toque em
- [arquivo ou componente 1]
- [arquivo ou componente 2]
```

---

## Checklist de Início de Sessão

Antes de colar o bloco acima, verifique:

- [ ] Li o `CLAUDE.md` (o Claude Code faz isso automaticamente)
- [ ] Li o `.claude/memory/session-log.md` — entendo o que foi feito antes
- [ ] Li o `.claude/memory/decisions.md` — conheço as decisões ativas
- [ ] A tarefa desta sessão é **uma só** — não misturo múltiplos objetivos
- [ ] Defini o critério de pronto de forma **binária** (sim/não, não "melhor")
- [ ] Listei o que **não pode ser tocado**

---

## Checklist de Fim de Sessão

Antes de encerrar, verifique:

- [ ] `session-log.md` atualizado com o que foi feito
- [ ] `decisions.md` atualizado se alguma decisão foi tomada
- [ ] `CLAUDE.md` — seção "Contexto Atual" atualizada
- [ ] Mudanças commitadas com mensagem no formato correto
- [ ] Push feito para o branch correto
- [ ] Próximo passo registrado claramente
