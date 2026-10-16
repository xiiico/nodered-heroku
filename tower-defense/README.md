# Rota de Defesa

Tower defense original no estilo *mazing*. As torres bloqueiam o caminho, e os inimigos recalculam a rota mais curta a cada construção. Feito em HTML5 Canvas puro, sem dependências em runtime, e empacotado como APK Android com Capacitor.

> Este projeto é temporário dentro de `nodered-heroku`. Mova a pasta `tower-defense/` (e o workflow `.github/workflows/tower-defense-apk.yml`) para um repositório próprio.

## Jogabilidade

- **Mapas:** Campo Aberto (25 ondas), Vale das Pedras (30 ondas, com rochas) e Cruzamento (25 ondas, duas rotas). Cada mapa é liberado ao vencer o anterior.
- **Torres (3 níveis cada):**
  - Metralhadora: barata e rápida, acerta alvos no chão e no ar.
  - Gosma: deixa os inimigos lentos (só no chão).
  - Míssil: dano em área, acerta chão e ar.
  - Tesla: raio em cadeia que ignora armadura (só no chão).
- **Inimigos:**
  - Soldado
  - Corredor (rápido)
  - Blindado (com armadura)
  - Helicóptero (voa por cima do labirinto)
  - Colosso (chefe a cada 10 ondas, tira 5 vidas)
- **Regras:**
  - Não é permitido fechar o caminho por completo.
  - Chamar a próxima onda antes do tempo dá dinheiro extra.
  - Antes da primeira onda, vender uma torre devolve 100% do valor; depois, 70%.
- **Interface:** pausa, velocidade 1x/2x/3x e estrelas por desempenho. O progresso fica salvo no aparelho.

## Rodar no navegador

```bash
cd tower-defense
npm start         # http://localhost:8080
```

## Gerar o APK

**Pelo GitHub Actions (não precisa instalar nada):** cada push que altera `tower-defense/` dispara o workflow **"Rota de Defesa — APK"**. Para baixar o APK:

1. Abra a aba **Actions** do repositório.
2. Entre na execução mais recente do workflow.
3. Em **Artifacts**, baixe `rota-de-defesa-apk`.
4. Descompacte o arquivo, copie `app-debug.apk` para o celular e instale. Será preciso permitir a instalação de "fontes desconhecidas".

**Localmente** (requer JDK 17 e Android SDK):

```bash
cd tower-defense
npm ci
npx cap add android
npx cap sync android
cd android && ./gradlew assembleDebug
# APK: android/app/build/outputs/apk/debug/app-debug.apk
```

## Estrutura

```
tower-defense/
├── www/index.html        # página única (canvas)
├── www/game.js           # todo o jogo: mapas, pathfinding, torres, ondas, UI
├── capacitor.config.json # appId com.xiiico.rotadedefesa
└── package.json
```
