# Template: Task Brief

> Use este template para definir qualquer tarefa antes de enviar ao Claude Code.
> Uma tarefa bem definida na primeira mensagem elimina 80% dos re-prompts.

---

## Como usar

1. Copie o bloco abaixo
2. Preencha todos os campos (não deixe nenhum em branco — se não souber, escreva "sem restrição")
3. Cole como primeira mensagem na sessão

---

## Task Brief

```
## Memory Block (contexto persistente)
- Stack: Node-RED + Node.js 14 + MongoDB + PostgreSQL + Redis + Aedes MQTT + Telegram
- Deploy: Heroku via git push
- Variáveis sensíveis: NUNCA no código, sempre em Heroku Config Vars
- [Adicione aqui decisões específicas da sessão anterior]

## Tarefa
[Descrição precisa do que deve ser feito. Use verbos concretos: criar, modificar, corrigir, refatorar, exportar.]

## Contexto
- Estado atual: [Descreva o que existe hoje — arquivos, fluxos, comportamento]
- Por que precisa mudar: [Motivo da tarefa]
- Tentativas anteriores: [O que já foi tentado e por que não funcionou — ou "nenhuma"]

## Arquivos relevantes
- [caminho/do/arquivo.json] — [o que ele faz]
- [caminho/do/outro.js] — [o que ele faz]

## Critério de pronto (binário)
- [ ] [Condição 1 — ex: flow X processa mensagem MQTT e salva no MongoDB]
- [ ] [Condição 2 — ex: Dashboard mostra dado em tempo real]
- [ ] session-log.md atualizado
- [ ] Mudanças commitadas

## Restrições
- NÃO alterar: [lista de arquivos ou fluxos que não podem ser tocados]
- NÃO instalar: [dependências proibidas]
- NÃO conectar a: [serviços externos não autorizados]

## Stop conditions (quando a IA deve parar e pedir aprovação)
- Antes de deletar qualquer arquivo
- Antes de alterar package.json ou settings.js
- Antes de qualquer operação de banco de dados
- [Adicione condições específicas da tarefa]
```

---

## Exemplo preenchido

```
## Memory Block
- Stack: Node-RED + Node.js 14 + MongoDB + Aedes MQTT
- Broker MQTT interno via Aedes, porta 1883
- Dados de sensores salvos na collection "sensor_readings" no MongoDB

## Tarefa
Criar um flow que recebe dados de temperatura via MQTT (tópico sensor/temp),
valida se o valor está entre -20 e 80 graus, e salva no MongoDB com timestamp.
Se o valor estiver fora do range, enviar alerta via Telegram.

## Contexto
- Estado atual: broker MQTT está rodando mas sem subscriber para sensor/temp
- Por que precisa mudar: sensores novos começarão a publicar dados amanhã
- Tentativas anteriores: nenhuma

## Arquivos relevantes
- flows.json — fluxos existentes (não alterar fluxos existentes)
- settings.js — config do Node-RED (não alterar)

## Critério de pronto
- [ ] Flow recebe mensagem MQTT no tópico sensor/temp
- [ ] Validação de range funcionando (-20 a 80)
- [ ] Dados salvos no MongoDB com timestamp ISO 8601
- [ ] Alerta Telegram disparado quando fora do range
- [ ] session-log.md atualizado
- [ ] Mudanças commitadas

## Restrições
- NÃO alterar flows existentes — apenas adicionar novos
- NÃO alterar settings.js

## Stop conditions
- Antes de qualquer alteração no schema do MongoDB
- Antes de instalar novas dependências
```
