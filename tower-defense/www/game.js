'use strict';
// Rota de Defesa — tower defense original no estilo "mazing":
// as torres bloqueiam o caminho e os inimigos recalculam a rota a cada construção.
(() => {
  const COLS = 16, ROWS = 10, HUD = 0.9, START_LIVES = 20;
  const canvas = document.getElementById('game');
  const ctx = canvas.getContext('2d');
  let W = 0, H = 0, CELL = 40, OX = 0, OY = 0;

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth; H = window.innerHeight;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    CELL = Math.max(8, Math.floor(Math.min(W / COLS, H / (ROWS + HUD))));
    OX = Math.floor((W - CELL * COLS) / 2);
    OY = Math.floor((H - CELL * (ROWS + HUD)) / 2 + CELL * HUD);
  }
  window.addEventListener('resize', resize);
  resize();

  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* sem armazenamento */ } },
  };

  // ---------- Mapas ----------
  const OUT = { L: [-1, 0], R: [1, 0], T: [0, -1], B: [0, 1] };
  function sideCells(side, a, b) {
    const r = [];
    for (let i = a; i <= b; i++) {
      if (side === 'L') r.push([0, i]);
      else if (side === 'R') r.push([COLS - 1, i]);
      else if (side === 'T') r.push([i, 0]);
      else r.push([i, ROWS - 1]);
    }
    return r;
  }
  function route(inSide, a, b, outSide, c, d) {
    return { inSide, outSide, entrances: sideCells(inSide, a, b), exits: sideCells(outSide, c, d) };
  }

  const MAPS = [
    { name: 'Campo Aberto', desc: 'Uma entrada, uma saída. Aprenda a montar o labirinto.',
      routes: [route('L', 3, 6, 'R', 3, 6)], rocks: [], money: 80, waves: 25 },
    { name: 'Vale das Pedras', desc: 'Rochas limitam onde você pode construir.',
      routes: [route('L', 1, 3, 'R', 6, 8)],
      rocks: [[4, 4], [4, 5], [5, 5], [8, 1], [8, 2], [9, 7], [9, 8], [12, 4], [12, 5], [11, 4], [6, 8], [13, 1]],
      money: 90, waves: 30 },
    { name: 'Cruzamento', desc: 'Duas rotas se cruzam no meio do campo.',
      routes: [route('L', 4, 5, 'R', 4, 5), route('T', 7, 8, 'B', 7, 8)],
      rocks: [[3, 1], [12, 8], [3, 8], [12, 1]], money: 160, waves: 25 },
  ];

  // ---------- Definições ----------
  const TOWERS = {
    gat: { name: 'Metralhadora', color: '#e0b04a', cost: [12, 15, 25], range: [2.4, 2.7, 3.0], dmg: [3, 5, 8],
      cd: [0.2, 0.17, 0.14], air: true, ground: true },
    goo: { name: 'Gosma', color: '#74c94a', cost: [18, 20, 30], range: [2.2, 2.4, 2.7], dmg: [1, 2, 3],
      cd: [0.9, 0.8, 0.7], slow: [0.5, 0.42, 0.34], slowT: [2, 2.5, 3], air: false, ground: true },
    msl: { name: 'Míssil', color: '#d0584f', cost: [30, 35, 50], range: [3.4, 3.8, 4.2], dmg: [18, 30, 48],
      cd: [1.6, 1.5, 1.4], splash: [0.9, 1.0, 1.2], air: true, ground: true },
    tes: { name: 'Tesla', color: '#55aef0', cost: [40, 45, 65], range: [2.3, 2.5, 2.8], dmg: [14, 22, 36],
      cd: [1.3, 1.2, 1.1], chain: [3, 4, 5], air: false, ground: true },
  };
  const TOWER_ORDER = ['gat', 'goo', 'msl', 'tes'];

  const ENEMIES = {
    sol: { hp: 20, spd: 1.0, armor: 0, reward: 2, r: 0.22, color: '#e8d6a0', lives: 1 },
    run: { hp: 12, spd: 1.8, armor: 0, reward: 2, r: 0.18, color: '#f0a030', lives: 1 },
    tank: { hp: 75, spd: 0.6, armor: 3, reward: 5, r: 0.32, color: '#7d8c5a', lives: 1 },
    heli: { hp: 30, spd: 1.15, armor: 0, reward: 4, r: 0.28, color: '#8a9ab2', lives: 1, fly: true },
    boss: { hp: 450, spd: 0.45, armor: 5, reward: 30, r: 0.42, color: '#a8466a', lives: 5 },
  };

  function waveGroups(n) {
    const g = [];
    g.push({ t: 'sol', c: 6 + n, i: 0.7 });
    if (n >= 3 && n % 2 === 1) g.push({ t: 'run', c: 4 + n, i: 0.45 });
    if (n >= 5 && n % 3 === 2) g.push({ t: 'tank', c: 2 + Math.floor(n / 2), i: 1.2 });
    if (n >= 4 && n % 4 === 0) g.push({ t: 'heli', c: 3 + Math.floor(n / 2), i: 0.9 });
    if (n % 10 === 0) g.push({ t: 'boss', c: n / 10, i: 3 });
    return g;
  }
  const hpMul = (w) => 1 + 0.16 * (w - 1) + 0.012 * (w - 1) * (w - 1);

  // ---------- Pathfinding (Dijkstra, 8 direções, sem cortar quinas) ----------
  const DIRS = [[1, 0, 1], [-1, 0, 1], [0, 1, 1], [0, -1, 1],
    [1, 1, Math.SQRT2], [1, -1, Math.SQRT2], [-1, 1, Math.SQRT2], [-1, -1, Math.SQRT2]];
  function passable(grid, x, y) { return x >= 0 && y >= 0 && x < COLS && y < ROWS && grid[y * COLS + x] === 0; }
  function canStep(grid, x, y, dx, dy) {
    if (!passable(grid, x + dx, y + dy)) return false;
    if (dx && dy) return passable(grid, x + dx, y) && passable(grid, x, y + dy);
    return true;
  }
  function computeField(exits, grid) {
    const N = COLS * ROWS, d = new Float64Array(N).fill(Infinity), done = new Uint8Array(N);
    for (const [x, y] of exits) if (grid[y * COLS + x] === 0) d[y * COLS + x] = 0;
    for (;;) {
      let bi = -1, bd = Infinity;
      for (let i = 0; i < N; i++) if (!done[i] && d[i] < bd) { bd = d[i]; bi = i; }
      if (bi < 0) break;
      done[bi] = 1;
      const x = bi % COLS, y = (bi / COLS) | 0;
      for (const [dx, dy, c] of DIRS) {
        if (!canStep(grid, x, y, dx, dy)) continue;
        const j = (y + dy) * COLS + x + dx;
        if (bd + c < d[j]) d[j] = bd + c;
      }
    }
    return d;
  }
  function nextCell(field, grid, x, y) {
    let best = null, bd = field[y * COLS + x];
    for (const [dx, dy] of DIRS) {
      if (!canStep(grid, x, y, dx, dy)) continue;
      const v = field[(y + dy) * COLS + x + dx];
      if (v < bd - 1e-9) { bd = v; best = [x + dx, y + dy]; }
    }
    return best;
  }

  // ---------- Estado ----------
  let screen = 'menu';
  let G = null;
  let progress = store.get('rd_progress', { unlocked: 1, stars: [] });

  function newGame(mi) {
    const m = MAPS[mi];
    const grid = new Uint8Array(COLS * ROWS), noBuild = new Uint8Array(COLS * ROWS);
    for (const [x, y] of m.rocks) grid[y * COLS + x] = 2;
    for (const r of m.routes) for (const [x, y] of r.entrances.concat(r.exits)) noBuild[y * COLS + x] = 1;
    G = {
      mi, map: m, grid, noBuild, towers: [], towerAt: new Array(COLS * ROWS).fill(null),
      enemies: [], shots: [], fx: [], texts: [], money: m.money, lives: START_LIVES, wave: 0,
      queue: [], spawnT: 0, nextT: -1, started: false, paused: false, speed: 1, sel: null, over: null, time: 0, kills: 0,
    };
    G.fields = m.routes.map((r) => computeField(r.exits, grid));
    screen = 'play';
  }

  // ---------- Inimigos ----------
  function spawnEnemy(type, ri, w) {
    const def = ENEMIES[type], r = G.map.routes[ri];
    const [ex, ey] = r.entrances[(Math.random() * r.entrances.length) | 0];
    const o = OUT[r.inSide], hp = def.hp * hpMul(w);
    const e = { type, def, route: ri, x: ex + 0.5 + o[0] * 1.2, y: ey + 0.5 + o[1] * 1.2, tx: ex, ty: ey,
      hp, maxHp: hp, slowT: 0, slowF: 1, alive: true, leaving: false, ang: Math.atan2(-o[1], -o[0]),
      fly: !!def.fly, rem: 0, hitT: 0, wob: Math.random() * 6 };
    if (e.fly) {
      const xs = r.exits[(Math.random() * r.exits.length) | 0], oo = OUT[r.outSide];
      e.gx = xs[0] + 0.5 + oo[0] * 1.2; e.gy = xs[1] + 0.5 + oo[1] * 1.2;
    }
    G.enemies.push(e);
  }

  function leak(e) {
    e.alive = false;
    G.lives = Math.max(0, G.lives - e.def.lives);
    addText('-' + e.def.lives + '♥', Math.min(Math.max(e.x, 0.5), COLS - 0.5), Math.min(Math.max(e.y, 0.5), ROWS - 0.5), '#ff6b6b');
    if (G.lives <= 0 && !G.over) G.over = 'lose';
  }

  function updEnemy(e, dt) {
    if (e.slowT > 0) { e.slowT -= dt; if (e.slowT <= 0) e.slowF = 1; }
    e.hitT = Math.max(0, e.hitT - dt);
    let step = e.def.spd * e.slowF * dt;
    if (e.fly) {
      const dx = e.gx - e.x, dy = e.gy - e.y, L = Math.hypot(dx, dy);
      e.ang = Math.atan2(dy, dx); e.rem = L;
      if (L <= step) { leak(e); return; }
      e.x += dx / L * step; e.y += dy / L * step;
      return;
    }
    const f = G.fields[e.route];
    while (step > 0 && e.alive) {
      const gx = e.leaving ? e.lx : e.tx + 0.5, gy = e.leaving ? e.ly : e.ty + 0.5;
      const dx = gx - e.x, dy = gy - e.y, L = Math.hypot(dx, dy);
      if (L > 1e-6) e.ang = Math.atan2(dy, dx);
      if (L > step) { e.x += dx / L * step; e.y += dy / L * step; break; }
      e.x = gx; e.y = gy; step -= L;
      if (e.leaving) { leak(e); return; }
      if (f[e.ty * COLS + e.tx] === 0) {
        const o = OUT[G.map.routes[e.route].outSide];
        e.leaving = true; e.lx = e.tx + 0.5 + o[0] * 1.2; e.ly = e.ty + 0.5 + o[1] * 1.2;
        continue;
      }
      const n = nextCell(f, G.grid, e.tx, e.ty);
      if (!n) break;
      e.tx = n[0]; e.ty = n[1];
    }
    e.rem = e.leaving ? Math.hypot(e.lx - e.x, e.ly - e.y) * 0.01
      : f[e.ty * COLS + e.tx] + Math.hypot(e.tx + 0.5 - e.x, e.ty + 0.5 - e.y);
  }

  function hurt(e, dmg, pierce) {
    if (!e.alive) return;
    const a = pierce ? dmg : Math.max(dmg * 0.25, dmg - e.def.armor);
    e.hp -= a; e.hitT = 0.08;
    if (e.hp <= 0) {
      e.alive = false;
      G.money += e.def.reward; G.kills++;
      addText('+' + e.def.reward, e.x, e.y, '#ffd84a');
      boom(e.x, e.y, e.def.r * 1.8, e.fly ? '#ffcf70' : '#ffb040');
    }
  }

  // ---------- Torres ----------
  const stat = (t, k) => t.def[k][t.lvl];

  function tryPlace(cx, cy) {
    const i = cy * COLS + cx;
    if (G.grid[i] !== 0 || G.noBuild[i]) return null;
    for (const e of G.enemies) {
      if (!e.alive || e.fly) continue;
      if (e.tx === cx && e.ty === cy) return null;
      if (Math.floor(e.x) === cx && Math.floor(e.y) === cy) return null;
    }
    G.grid[i] = 1;
    const fields = G.map.routes.map((r) => computeField(r.exits, G.grid));
    let ok = true;
    G.map.routes.forEach((r, ri) => {
      for (const [x, y] of r.entrances) if (!isFinite(fields[ri][y * COLS + x])) ok = false;
    });
    if (ok) for (const e of G.enemies) {
      if (!e.alive || e.fly || e.leaving) continue;
      if (!isFinite(fields[e.route][e.ty * COLS + e.tx])) ok = false;
    }
    G.grid[i] = 0;
    return ok ? fields : null;
  }

  function build(type, cx, cy) {
    const def = TOWERS[type];
    if (G.money < def.cost[0]) { flashMsg('Dinheiro insuficiente'); return false; }
    const fields = tryPlace(cx, cy);
    if (!fields) { flashMsg('Não pode bloquear o caminho!'); return false; }
    const t = { type, def, lvl: 0, x: cx, y: cy, cd: 0, ang: -Math.PI / 2, spent: def.cost[0], flash: 0, built: 0.25 };
    G.money -= def.cost[0];
    G.grid[cy * COLS + cx] = 1; G.towerAt[cy * COLS + cx] = t; G.towers.push(t);
    G.fields = fields;
    return true;
  }

  function upgrade(t) {
    if (t.lvl >= 2) return;
    const c = t.def.cost[t.lvl + 1];
    if (G.money < c) { flashMsg('Dinheiro insuficiente'); return; }
    G.money -= c; t.spent += c; t.lvl++; t.built = 0.25;
  }

  function sellValue(t) { return G.started ? Math.floor(t.spent * 0.7) : t.spent; }

  function sell(t) {
    G.money += sellValue(t);
    const i = t.y * COLS + t.x;
    G.grid[i] = 0; G.towerAt[i] = null;
    G.towers.splice(G.towers.indexOf(t), 1);
    G.fields = G.map.routes.map((r) => computeField(r.exits, G.grid));
    addText('+' + sellValue(t), t.x + 0.5, t.y + 0.5, '#ffd84a');
  }

  function updTower(t, dt) {
    t.cd -= dt; t.flash = Math.max(0, t.flash - dt); t.built = Math.max(0, t.built - dt);
    const cx = t.x + 0.5, cy = t.y + 0.5, R = stat(t, 'range');
    let best = null, bs = Infinity;
    for (const e of G.enemies) {
      if (!e.alive) continue;
      if (e.fly ? !t.def.air : !t.def.ground) continue;
      if (Math.hypot(e.x - cx, e.y - cy) > R) continue;
      const s = e.rem + (t.type === 'goo' && e.slowT > 0.3 ? 1000 : 0);
      if (s < bs) { bs = s; best = e; }
    }
    if (!best) return;
    t.ang = Math.atan2(best.y - cy, best.x - cx);
    if (t.cd > 0) return;
    t.cd = stat(t, 'cd'); t.flash = 0.07;
    const mx = cx + Math.cos(t.ang) * 0.38, my = cy + Math.sin(t.ang) * 0.38;
    if (t.type === 'gat') {
      hurt(best, stat(t, 'dmg'));
      G.fx.push({ k: 'line', pts: [[mx, my], [best.x, best.y]], t: 0.06, m: 0.06, c: '#fff2a8', w: 0.05 });
    } else if (t.type === 'goo') {
      G.shots.push({ k: 'goo', x: mx, y: my, tg: best, lx: best.x, ly: best.y, spd: 6, dmg: stat(t, 'dmg'),
        slow: stat(t, 'slow'), slowT: stat(t, 'slowT') });
    } else if (t.type === 'msl') {
      G.shots.push({ k: 'msl', x: mx, y: my, tg: best, lx: best.x, ly: best.y, spd: 4.5, dmg: stat(t, 'dmg'),
        splash: stat(t, 'splash'), ang: t.ang });
    } else if (t.type === 'tes') {
      const hit = [best]; let cur = best;
      for (let k = 1; k < stat(t, 'chain'); k++) {
        let nb = null, nd = 1.7;
        for (const e of G.enemies) {
          if (!e.alive || e.fly || hit.includes(e)) continue;
          const d = Math.hypot(e.x - cur.x, e.y - cur.y);
          if (d < nd) { nd = d; nb = e; }
        }
        if (!nb) break;
        hit.push(nb); cur = nb;
      }
      const pts = [[cx, cy - 0.15]];
      hit.forEach((e, k) => { pts.push([e.x, e.y]); hurt(e, stat(t, 'dmg') * Math.pow(0.85, k), true); });
      G.fx.push({ k: 'bolt', pts, t: 0.16, m: 0.16, c: '#bfe6ff', w: 0.06 });
    }
  }

  function updShot(s, dt) {
    if (s.tg.alive) { s.lx = s.tg.x; s.ly = s.tg.y; }
    const dx = s.lx - s.x, dy = s.ly - s.y, L = Math.hypot(dx, dy), step = s.spd * dt;
    if (s.k === 'msl') {
      s.ang = Math.atan2(dy, dx);
      if (Math.random() < 0.6) G.fx.push({ k: 'puff', x: s.x, y: s.y, r: 0.08, t: 0.35, m: 0.35, c: '#cfcfcf' });
    }
    if (L > step + 0.05) { s.x += dx / L * step; s.y += dy / L * step; return true; }
    if (s.k === 'goo') {
      if (s.tg.alive) {
        hurt(s.tg, s.dmg, true);
        if (s.tg.slowF > s.slow || s.tg.slowT < s.slowT) { s.tg.slowF = Math.min(s.tg.slowF, s.slow); s.tg.slowT = s.slowT; }
      }
      G.fx.push({ k: 'ring', x: s.lx, y: s.ly, r: 0.3, t: 0.25, m: 0.25, c: '#8be05a' });
    } else {
      for (const e of G.enemies) if (e.alive && Math.hypot(e.x - s.lx, e.y - s.ly) <= s.splash) hurt(e, s.dmg);
      boom(s.lx, s.ly, s.splash, '#ff8a3a');
    }
    return false;
  }

  // ---------- Ondas ----------
  function callWave() {
    if (!G || G.wave >= G.map.waves) return;
    const bonus = G.started && G.nextT > 0 ? Math.ceil(G.nextT) : 0;
    G.wave++; G.started = true; G.nextT = -1;
    if (bonus) { G.money += bonus; flashMsg('Bônus por antecipar: +$' + bonus); }
    const wasEmpty = G.queue.length === 0, nr = G.map.routes.length;
    let k = 0;
    for (const g of waveGroups(G.wave)) {
      for (let i = 0; i < g.c; i++) G.queue.push({ t: g.t, w: G.wave, route: (k++) % nr, delay: i === 0 ? 1.5 : g.i });
    }
    if (wasEmpty) G.spawnT = 0.5;
  }

  // ---------- Efeitos ----------
  function boom(x, y, r, c) { G.fx.push({ k: 'boom', x, y, r, t: 0.35, m: 0.35, c }); }
  function addText(s, x, y, c) { G.texts.push({ s, x, y, c, t: 0.9 }); }
  let msg = null;
  function flashMsg(s) { msg = { s, t: 1.6 }; }

  // ---------- Atualização ----------
  function update(dt) {
    if (msg) { msg.t -= dt; if (msg.t <= 0) msg = null; }
    if (screen !== 'play' || G.paused || G.over) return;
    G.time += dt;
    if (G.queue.length) {
      G.spawnT -= dt;
      while (G.queue.length && G.spawnT <= 0) {
        const q = G.queue.shift();
        spawnEnemy(q.t, q.route, q.w);
        if (G.queue.length) G.spawnT += G.queue[0].delay;
      }
    } else if (G.started && G.wave < G.map.waves) {
      if (G.nextT < 0) G.nextT = 12;
      G.nextT -= dt;
      if (G.nextT <= 0) { G.nextT = 0; callWave(); }
    }
    for (const e of G.enemies) if (e.alive) updEnemy(e, dt);
    for (const t of G.towers) updTower(t, dt);
    G.shots = G.shots.filter((s) => updShot(s, dt));
    G.enemies = G.enemies.filter((e) => e.alive);
    for (const f of G.fx) f.t -= dt;
    G.fx = G.fx.filter((f) => f.t > 0);
    for (const t of G.texts) { t.t -= dt; t.y -= dt * 0.8; }
    G.texts = G.texts.filter((t) => t.t > 0);
    if (G.sel && G.sel.kind === 'tower' && !G.towers.includes(G.sel.t)) G.sel = null;

    if (!G.over && G.wave >= G.map.waves && !G.queue.length && !G.enemies.length) G.over = 'win';
    if (G.over) onGameOver();
  }

  function onGameOver() {
    G.sel = null;
    if (G.over === 'win') {
      const stars = G.lives >= START_LIVES ? 3 : G.lives >= START_LIVES / 2 ? 2 : 1;
      progress.stars[G.mi] = Math.max(progress.stars[G.mi] || 0, stars);
      progress.unlocked = Math.max(progress.unlocked, Math.min(MAPS.length, G.mi + 2));
      store.set('rd_progress', progress);
      G.starsWon = stars;
    }
  }

  // ---------- Desenho: utilidades ----------
  let UI = [];
  const sx = (x) => OX + x * CELL, sy = (y) => OY + y * CELL;
  function rr(x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
  }
  function circle(x, y, r, fill) { ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fillStyle = fill; ctx.fill(); }
  function font(px, w) { ctx.font = (w || 700) + ' ' + Math.max(9, Math.round(px)) + 'px system-ui, -apple-system, Segoe UI, Roboto, sans-serif'; }
  function text(s, x, y, px, c, align, w) {
    font(px, w); ctx.textAlign = align || 'center'; ctx.textBaseline = 'middle';
    ctx.lineWidth = Math.max(2, px / 5); ctx.strokeStyle = 'rgba(0,0,0,0.55)'; ctx.strokeText(s, x, y);
    ctx.fillStyle = c || '#fff'; ctx.fillText(s, x, y);
  }
  function button(x, y, w, h, label, fn, opt) {
    opt = opt || {};
    rr(x, y, w, h, Math.min(h * 0.3, 12));
    ctx.fillStyle = opt.disabled ? '#4b4b42' : (opt.bg || '#3e6b2a'); ctx.fill();
    ctx.lineWidth = 2; ctx.strokeStyle = opt.disabled ? '#2e2e28' : 'rgba(0,0,0,0.45)'; ctx.stroke();
    if (label) text(label, x + w / 2, y + h / 2 + 1, opt.px || h * 0.42, opt.disabled ? '#9a9a90' : (opt.fg || '#fff'));
    UI.push({ x, y, w, h, fn, disabled: !!opt.disabled });
  }

  // ---------- Desenho: jogo ----------
  function drawBoard() {
    ctx.fillStyle = '#1d2b16'; ctx.fillRect(0, 0, W, H);
    // estradas de entrada/saída fora do tabuleiro
    for (const r of G.map.routes) {
      for (const [cells, side] of [[r.entrances, r.inSide], [r.exits, r.outSide]]) {
        const o = OUT[side];
        for (const [x, y] of cells) {
          ctx.fillStyle = '#8a6a43';
          ctx.fillRect(sx(x + o[0]), sy(y + o[1]), CELL, CELL);
        }
      }
    }
    for (let y = 0; y < ROWS; y++) for (let x = 0; x < COLS; x++) {
      ctx.fillStyle = (x + y) % 2 ? '#5b8f3b' : '#629944';
      if (G.noBuild[y * COLS + x]) ctx.fillStyle = (x + y) % 2 ? '#977550' : '#9d7b55';
      ctx.fillRect(sx(x), sy(y), CELL + 0.5, CELL + 0.5);
    }
    // setas de entrada
    for (const r of G.map.routes) {
      const o = OUT[r.inSide];
      for (const [x, y] of r.entrances) arrow(sx(x + 0.5 + o[0]), sy(y + 0.5 + o[1]), Math.atan2(-o[1], -o[0]), '#f4e1a0');
      const p = OUT[r.outSide];
      for (const [x, y] of r.exits) arrow(sx(x + 0.5 + p[0]), sy(y + 0.5 + p[1]), Math.atan2(p[1], p[0]), '#ff9b8a');
    }
    for (const [x, y] of G.map.rocks) drawRock(x, y);
    // prévia do caminho (pontinhos) antes de iniciar ou com algo selecionado
    if (!G.started || G.sel) drawPathPreview();
  }

  function drawPathPreview() {
    ctx.fillStyle = 'rgba(255,255,255,0.28)';
    G.map.routes.forEach((r, ri) => {
      const f = G.fields[ri];
      let [x, y] = r.entrances[Math.floor(r.entrances.length / 2)];
      for (let n = 0; n < 200 && f[y * COLS + x] > 0; n++) {
        const nc = nextCell(f, G.grid, x, y); if (!nc) break;
        const mx = (x + nc[0]) / 2 + 0.5, my = (y + nc[1]) / 2 + 0.5;
        ctx.beginPath(); ctx.arc(sx(mx), sy(my), CELL * 0.06, 0, 7); ctx.fill();
        [x, y] = nc;
      }
    });
  }

  function arrow(x, y, a, c) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(a);
    ctx.beginPath(); ctx.moveTo(CELL * 0.25, 0); ctx.lineTo(-CELL * 0.15, -CELL * 0.18); ctx.lineTo(-CELL * 0.15, CELL * 0.18); ctx.closePath();
    ctx.fillStyle = c; ctx.globalAlpha = 0.7; ctx.fill(); ctx.restore();
  }

  function drawRock(x, y) {
    const cx = sx(x + 0.5), cy = sy(y + 0.5);
    circle(cx + CELL * 0.05, cy + CELL * 0.08, CELL * 0.4, 'rgba(0,0,0,0.25)');
    circle(cx, cy, CELL * 0.4, '#8b8b85');
    circle(cx - CELL * 0.1, cy - CELL * 0.1, CELL * 0.22, '#a6a69f');
    circle(cx + CELL * 0.15, cy + CELL * 0.12, CELL * 0.12, '#74746e');
  }

  function drawTowerIcon(type, cx, cy, s, ang, lvl, flash) {
    const def = TOWERS[type];
    ctx.save(); ctx.translate(cx, cy);
    rr(-s * 0.44, -s * 0.44, s * 0.88, s * 0.88, s * 0.14);
    ctx.fillStyle = '#4a4f55'; ctx.fill(); ctx.lineWidth = Math.max(1, s * 0.04); ctx.strokeStyle = '#2b2f33'; ctx.stroke();
    rr(-s * 0.36, -s * 0.36, s * 0.72, s * 0.72, s * 0.1); ctx.fillStyle = '#5d636a'; ctx.fill();
    ctx.rotate(ang);
    if (type === 'gat') {
      ctx.fillStyle = '#2a2a2a';
      ctx.fillRect(0, -s * 0.12, s * 0.42, s * 0.08); ctx.fillRect(0, s * 0.04, s * 0.42, s * 0.08);
      circle(0, 0, s * 0.22, def.color);
      circle(-s * 0.05, -s * 0.05, s * 0.09, '#f7d98a');
      if (flash > 0) circle(s * 0.48, 0, s * 0.12, '#fff6b0');
    } else if (type === 'goo') {
      ctx.fillStyle = '#2f5a1f'; ctx.fillRect(0, -s * 0.08, s * 0.38, s * 0.16);
      circle(0, 0, s * 0.25, def.color);
      circle(-s * 0.07, -s * 0.08, s * 0.08, '#c7f2a6');
      circle(s * 0.08, s * 0.06, s * 0.05, '#c7f2a6');
    } else if (type === 'msl') {
      rr(-s * 0.24, -s * 0.24, s * 0.48, s * 0.48, s * 0.06); ctx.fillStyle = def.color; ctx.fill();
      ctx.fillStyle = '#3a1d1a'; ctx.fillRect(s * 0.05, -s * 0.17, s * 0.28, s * 0.12); ctx.fillRect(s * 0.05, s * 0.05, s * 0.28, s * 0.12);
      if (flash > 0) circle(s * 0.36, 0, s * 0.1, '#ffd29a');
    } else if (type === 'tes') {
      ctx.rotate(-ang);
      circle(0, 0, s * 0.24, '#2d4b66');
      ctx.strokeStyle = def.color; ctx.lineWidth = s * 0.06;
      for (let k = 0; k < 3; k++) { ctx.beginPath(); ctx.arc(0, 0, s * (0.08 + k * 0.07), 0, Math.PI * 2); ctx.stroke(); }
      circle(0, 0, s * 0.08, flash > 0 ? '#ffffff' : '#bfe6ff');
    }
    ctx.restore();
    if (lvl != null) for (let i = 0; i <= lvl; i++) circle(cx - s * 0.3 + i * s * 0.14, cy + s * 0.34, s * 0.05, '#ffd84a');
  }

  function drawEnemy(e) {
    const cx = sx(e.x), cy = sy(e.y), r = e.def.r * CELL;
    const bob = Math.sin(G.time * 10 + e.wob) * r * 0.08;
    if (e.fly) {
      ctx.fillStyle = 'rgba(0,0,0,0.25)';
      ctx.beginPath(); ctx.ellipse(cx + CELL * 0.25, cy + CELL * 0.35, r, r * 0.6, 0, 0, 7); ctx.fill();
    } else {
      ctx.fillStyle = 'rgba(0,0,0,0.25)';
      ctx.beginPath(); ctx.ellipse(cx, cy + r * 0.6, r, r * 0.5, 0, 0, 7); ctx.fill();
    }
    ctx.save(); ctx.translate(cx, cy + (e.fly ? 0 : bob)); ctx.rotate(e.ang);
    const body = e.hitT > 0 ? '#ffffff' : e.slowF < 1 ? '#a8e07a' : e.def.color;
    if (e.type === 'tank') {
      rr(-r, -r * 0.75, r * 2, r * 1.5, r * 0.25); ctx.fillStyle = '#3b3b33'; ctx.fill();
      rr(-r * 0.85, -r * 0.6, r * 1.7, r * 1.2, r * 0.2); ctx.fillStyle = body; ctx.fill();
      ctx.fillStyle = '#4c5638'; ctx.fillRect(0, -r * 0.12, r * 1.1, r * 0.24);
      circle(0, 0, r * 0.4, '#5d6a43');
    } else if (e.type === 'heli') {
      rr(-r, -r * 0.45, r * 1.8, r * 0.9, r * 0.4); ctx.fillStyle = body; ctx.fill();
      ctx.fillStyle = '#5c6b80'; ctx.fillRect(-r * 1.7, -r * 0.1, r * 0.9, r * 0.2);
      circle(r * 0.45, 0, r * 0.25, '#cfe3ff');
      ctx.rotate(G.time * 25);
      ctx.strokeStyle = 'rgba(30,30,30,0.7)'; ctx.lineWidth = Math.max(1.5, r * 0.12);
      ctx.beginPath(); ctx.moveTo(-r * 1.3, 0); ctx.lineTo(r * 1.3, 0); ctx.moveTo(0, -r * 1.3); ctx.lineTo(0, r * 1.3); ctx.stroke();
    } else if (e.type === 'boss') {
      circle(0, 0, r, '#5a2338');
      circle(0, 0, r * 0.85, body);
      ctx.fillStyle = '#3a1424'; ctx.fillRect(r * 0.2, -r * 0.5, r * 0.9, r * 0.25); ctx.fillRect(r * 0.2, r * 0.25, r * 0.9, r * 0.25);
      circle(-r * 0.1, 0, r * 0.35, '#e0a0b8');
    } else {
      // soldado / corredor
      circle(0, 0, r, '#3a3022');
      circle(0, 0, r * 0.82, body);
      circle(r * 0.15, 0, r * 0.5, e.type === 'run' ? '#b76a14' : '#6f7b45');
      ctx.fillStyle = '#2a2a2a'; ctx.fillRect(r * 0.3, r * 0.35, r * 0.9, r * 0.18);
    }
    ctx.restore();
    if (e.hp < e.maxHp) {
      const w = CELL * 0.5, h = Math.max(3, CELL * 0.07), bx = cx - w / 2, by = cy - r - CELL * 0.18;
      ctx.fillStyle = '#300'; ctx.fillRect(bx, by, w, h);
      ctx.fillStyle = e.hp / e.maxHp > 0.5 ? '#5be05b' : e.hp / e.maxHp > 0.25 ? '#f0c040' : '#f05050';
      ctx.fillRect(bx, by, w * Math.max(0, e.hp / e.maxHp), h);
    }
  }

  function drawShots() {
    for (const s of G.shots) {
      const x = sx(s.x), y = sy(s.y);
      if (s.k === 'goo') { circle(x, y, CELL * 0.1, '#7fd84f'); circle(x - CELL * 0.03, y - CELL * 0.03, CELL * 0.04, '#d8ffc0'); }
      else {
        ctx.save(); ctx.translate(x, y); ctx.rotate(s.ang);
        ctx.fillStyle = '#e9e2d0'; ctx.fillRect(-CELL * 0.14, -CELL * 0.045, CELL * 0.24, CELL * 0.09);
        ctx.fillStyle = '#d0584f'; ctx.fillRect(CELL * 0.08, -CELL * 0.045, CELL * 0.06, CELL * 0.09);
        ctx.restore();
      }
    }
  }

  function drawFx() {
    for (const f of G.fx) {
      const a = Math.max(0, f.t / f.m);
      ctx.globalAlpha = a;
      if (f.k === 'boom') {
        circle(sx(f.x), sy(f.y), CELL * f.r * (1.2 - a * 0.6), f.c);
        circle(sx(f.x), sy(f.y), CELL * f.r * (0.7 - a * 0.4), '#fff0b0');
      } else if (f.k === 'puff') {
        circle(sx(f.x), sy(f.y), CELL * f.r * (2 - a), f.c);
      } else if (f.k === 'ring') {
        ctx.strokeStyle = f.c; ctx.lineWidth = CELL * 0.06;
        ctx.beginPath(); ctx.arc(sx(f.x), sy(f.y), CELL * f.r * (1.5 - a), 0, 7); ctx.stroke();
      } else if (f.k === 'line' || f.k === 'bolt') {
        ctx.strokeStyle = f.c; ctx.lineWidth = Math.max(1.5, CELL * f.w); ctx.lineCap = 'round';
        ctx.beginPath();
        f.pts.forEach(([px, py], i) => {
          if (i === 0) { ctx.moveTo(sx(px), sy(py)); return; }
          if (f.k === 'bolt') {
            const [qx, qy] = f.pts[i - 1];
            for (let s = 1; s < 4; s++) {
              const tt = s / 4;
              ctx.lineTo(sx(qx + (px - qx) * tt + (Math.random() - 0.5) * 0.25), sy(qy + (py - qy) * tt + (Math.random() - 0.5) * 0.25));
            }
          }
          ctx.lineTo(sx(px), sy(py));
        });
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
    }
    for (const t of G.texts) {
      ctx.globalAlpha = Math.min(1, t.t * 2);
      text(t.s, sx(t.x), sy(t.y), CELL * 0.32, t.c);
      ctx.globalAlpha = 1;
    }
  }

  function drawHud() {
    const h = CELL * HUD, y0 = OY - h, bh = h * 0.78, by = y0 + (h - bh) / 2;
    ctx.fillStyle = '#26381c'; ctx.fillRect(OX, y0, CELL * COLS, h);
    const px = h * 0.42;
    text('♥ ' + G.lives, OX + CELL * 0.3, y0 + h / 2, px, '#ff8080', 'left');
    text('$ ' + G.money, OX + CELL * 2.0, y0 + h / 2, px, '#ffd84a', 'left');
    text('Onda ' + G.wave + '/' + G.map.waves, OX + CELL * 4.0, y0 + h / 2, px, '#e8f0d8', 'left');
    let x = OX + CELL * COLS - CELL * 0.15;
    const bw1 = CELL * 3.2;
    x -= bw1;
    if (!G.started) button(x, by, bw1, bh, '▶ Iniciar', callWave, { bg: '#c0761e' });
    else if (G.wave < G.map.waves) {
      const label = G.nextT > 0 ? '▶ Próxima ' + Math.ceil(G.nextT) + 's' : '▶ Próxima';
      button(x, by, bw1, bh, label, callWave, { bg: '#c0761e' });
    } else button(x, by, bw1, bh, 'Última onda', null, { disabled: true });
    const bw2 = CELL * 1.3;
    x -= bw2 + CELL * 0.15;
    button(x, by, bw2, bh, G.speed + 'x', () => { G.speed = G.speed >= 3 ? 1 : G.speed + 1; });
    x -= bw2 + CELL * 0.15;
    button(x, by, bw2, bh, 'II', () => { G.paused = true; G.sel = null; });
  }

  function drawSelection() {
    const s = G.sel; if (!s) return;
    const cx = sx(s.x + 0.5), cy = sy(s.y + 0.5);
    if (s.kind === 'cell') {
      ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 2; ctx.strokeRect(sx(s.x) + 1, sy(s.y) + 1, CELL - 2, CELL - 2);
      const bw = CELL * 1.15, gap = CELL * 0.12, total = bw * 4 + gap * 3;
      let bx = Math.min(Math.max(cx - total / 2, OX), OX + CELL * COLS - total);
      const by = s.y >= 2 ? sy(s.y) - bw * 1.25 - CELL * 0.1 : sy(s.y + 1) + CELL * 0.1;
      rr(bx - gap, by - gap, total + gap * 2, bw * 1.25 + gap * 2, 10); ctx.fillStyle = 'rgba(20,26,16,0.85)'; ctx.fill();
      for (const type of TOWER_ORDER) {
        const def = TOWERS[type], ok = G.money >= def.cost[0];
        const x0 = bx;
        rr(x0, by, bw, bw * 1.25, 8); ctx.fillStyle = ok ? '#3d5a2c' : '#3a3a34'; ctx.fill();
        ctx.globalAlpha = ok ? 1 : 0.45;
        drawTowerIcon(type, x0 + bw / 2, by + bw * 0.5, bw * 0.8, -Math.PI / 2, null, 0);
        ctx.globalAlpha = 1;
        text('$' + def.cost[0], x0 + bw / 2, by + bw * 1.07, bw * 0.24, ok ? '#ffd84a' : '#9a9a90');
        UI.push({ x: x0, y: by, w: bw, h: bw * 1.25, fn: () => { if (build(type, s.x, s.y)) G.sel = null; } });
        bx += bw + gap;
      }
    } else {
      const t = s.t, R = stat(t, 'range') * CELL;
      ctx.fillStyle = 'rgba(255,255,255,0.12)'; ctx.strokeStyle = 'rgba(255,255,255,0.6)'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7); ctx.fill(); ctx.stroke();
      const bw = CELL * 1.6, bh = CELL * 0.8, gap = CELL * 0.15, total = bw * 2 + gap;
      const bx = Math.min(Math.max(cx - total / 2, OX), OX + CELL * COLS - total);
      const by = t.y >= 1 ? sy(t.y) - bh - CELL * 0.15 : sy(t.y + 1) + CELL * 0.15;
      text(t.def.name + ' Nv' + (t.lvl + 1), cx, by - CELL * 0.25, CELL * 0.3, '#fff');
      if (t.lvl < 2) {
        const c = t.def.cost[t.lvl + 1];
        button(bx, by, bw, bh, '↑ $' + c, () => upgrade(t), { bg: '#2f6fb0', disabled: G.money < c, px: bh * 0.4 });
      } else button(bx, by, bw, bh, 'MÁX', null, { disabled: true, px: bh * 0.4 });
      button(bx + bw + gap, by, bw, bh, 'Vender $' + sellValue(t), () => { sell(t); G.sel = null; }, { bg: '#9a3b2e', px: bh * 0.36 });
    }
  }

  function drawOverlay(title, sub, buttons) {
    ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.fillRect(0, 0, W, H);
    const pw = Math.min(W * 0.8, CELL * 9), ph = CELL * 5.2, px = (W - pw) / 2, py = (H - ph) / 2;
    rr(px, py, pw, ph, 16); ctx.fillStyle = '#2b3d20'; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = '#7fae53'; ctx.stroke();
    text(title, W / 2, py + CELL * 0.9, CELL * 0.7, '#ffe9a8');
    if (sub) text(sub, W / 2, py + CELL * 1.8, CELL * 0.34, '#e8f0d8', 'center', 500);
    const bw = Math.min(pw * 0.7, CELL * 5), bh = CELL * 0.8;
    buttons.forEach(([label, fn, bg], i) => button((W - bw) / 2, py + CELL * 2.4 + i * (bh + CELL * 0.2), bw, bh, label, fn, { bg }));
  }

  function drawPlay() {
    drawBoard();
    for (const t of G.towers) {
      const k = 1 + t.built * 0.6;
      drawTowerIcon(t.type, sx(t.x + 0.5), sy(t.y + 0.5), CELL * k, t.ang, t.lvl, t.flash);
    }
    for (const e of G.enemies) if (!e.fly) drawEnemy(e);
    drawShots();
    for (const e of G.enemies) if (e.fly) drawEnemy(e);
    drawFx();
    drawSelection();
    drawHud();
    if (G.paused) {
      drawOverlay('Pausado', MAPS[G.mi].name, [
        ['Continuar', () => { G.paused = false; }, '#3e6b2a'],
        ['Reiniciar', () => newGame(G.mi), '#c0761e'],
        ['Menu', () => { screen = 'menu'; }, '#555'],
      ]);
    } else if (G.over === 'win') {
      const btns = [['Jogar de novo', () => newGame(G.mi), '#3e6b2a']];
      if (G.mi + 1 < MAPS.length) btns.unshift(['Próximo mapa', () => newGame(G.mi + 1), '#c0761e']);
      btns.push(['Menu', () => { screen = 'menu'; }, '#555']);
      drawOverlay('Vitória! ' + '★'.repeat(G.starsWon) + '☆'.repeat(3 - G.starsWon), 'Vidas restantes: ' + G.lives + ' · Abates: ' + G.kills, btns);
    } else if (G.over === 'lose') {
      drawOverlay('Derrota', 'Você chegou à onda ' + G.wave + ' · Abates: ' + G.kills, [
        ['Tentar de novo', () => newGame(G.mi), '#c0761e'],
        ['Menu', () => { screen = 'menu'; }, '#555'],
      ]);
    }
  }

  // ---------- Menu ----------
  let menuHelp = false;
  function drawMenu() {
    ctx.fillStyle = '#1d2b16'; ctx.fillRect(0, 0, W, H);
    const u = Math.min(W / 16, H / 10);
    for (let y = 0; y < H / u + 1; y++) for (let x = 0; x < W / u + 1; x++) {
      ctx.fillStyle = (x + y) % 2 ? '#263a1c' : '#22341a'; ctx.fillRect(x * u, y * u, u, u);
    }
    text('ROTA DE DEFESA', W / 2, u * 1.3, u * 0.95, '#ffe9a8');
    text('Construa o labirinto. Não deixe ninguém passar.', W / 2, u * 2.2, u * 0.33, '#cfe0b8', 'center', 500);
    if (menuHelp) {
      const lines = [
        'Toque num quadrado livre para construir uma torre.',
        'As torres bloqueiam o caminho: os inimigos sempre buscam a rota mais curta.',
        'Você não pode fechar o caminho por completo.',
        'Helicópteros voam por cima do labirinto: use Metralhadora e Míssil.',
        'Gosma deixa os inimigos lentos; Tesla acerta vários em cadeia.',
        'Chamar a próxima onda antes do tempo dá dinheiro extra.',
        'Toque numa torre para melhorar (até Nv3) ou vender.',
      ];
      lines.forEach((l, i) => text('• ' + l, W / 2, u * 3.3 + i * u * 0.62, u * 0.32, '#f0f4e8', 'center', 500));
      button(W / 2 - u * 2, H - u * 1.5, u * 4, u * 0.9, 'Voltar', () => { menuHelp = false; });
      return;
    }
    const cw = Math.min(u * 4.4, (W - u * 2) / 3 - u * 0.3), ch = u * 4.6, gap = u * 0.4;
    const total = cw * 3 + gap * 2; let x = (W - total) / 2; const y = u * 2.9;
    MAPS.forEach((m, i) => {
      const locked = i >= progress.unlocked;
      rr(x, y, cw, ch, 14); ctx.fillStyle = locked ? '#33362e' : '#3b5a29'; ctx.fill();
      ctx.lineWidth = 3; ctx.strokeStyle = locked ? '#222' : '#86b65a'; ctx.stroke();
      drawMiniMap(m, x + cw * 0.1, y + u * 0.3, cw * 0.8, cw * 0.5, locked);
      text(m.name, x + cw / 2, y + cw * 0.5 + u * 0.75, u * 0.4, locked ? '#888' : '#fff');
      text(m.waves + ' ondas', x + cw / 2, y + cw * 0.5 + u * 1.3, u * 0.28, locked ? '#777' : '#cfe0b8', 'center', 500);
      const st = progress.stars[i] || 0;
      text(locked ? '🔒' : '★'.repeat(st) + '☆'.repeat(3 - st), x + cw / 2, y + ch - u * 0.6, u * 0.45, '#ffd84a');
      if (!locked) UI.push({ x, y, w: cw, h: ch, fn: () => newGame(i) });
      x += cw + gap;
    });
    button(W / 2 - u * 2, H - u * 1.4, u * 4, u * 0.9, 'Como jogar', () => { menuHelp = true; });
  }

  function drawMiniMap(m, x, y, w, h, locked) {
    const c = Math.min(w / COLS, h / ROWS), ox = x + (w - c * COLS) / 2, oy = y + (h - c * ROWS) / 2;
    ctx.fillStyle = locked ? '#444' : '#629944'; ctx.fillRect(ox, oy, c * COLS, c * ROWS);
    ctx.fillStyle = locked ? '#555' : '#9d7b55';
    for (const r of m.routes) for (const [cx, cy] of r.entrances.concat(r.exits)) ctx.fillRect(ox + cx * c, oy + cy * c, c, c);
    ctx.fillStyle = locked ? '#666' : '#8b8b85';
    for (const [cx, cy] of m.rocks) ctx.fillRect(ox + cx * c, oy + cy * c, c, c);
  }

  // ---------- Entrada ----------
  canvas.addEventListener('pointerdown', (ev) => {
    ev.preventDefault();
    const x = ev.clientX, y = ev.clientY;
    for (let i = UI.length - 1; i >= 0; i--) {
      const b = UI[i];
      if (x >= b.x && x <= b.x + b.w && y >= b.y && y <= b.y + b.h) {
        if (!b.disabled && b.fn) b.fn();
        return;
      }
    }
    if (screen !== 'play' || G.paused || G.over) return;
    const cx = Math.floor((x - OX) / CELL), cy = Math.floor((y - OY) / CELL);
    if (cx < 0 || cy < 0 || cx >= COLS || cy >= ROWS) { G.sel = null; return; }
    const t = G.towerAt[cy * COLS + cx];
    if (t) { G.sel = G.sel && G.sel.t === t ? null : { kind: 'tower', t, x: cx, y: cy }; return; }
    if (G.grid[cy * COLS + cx] === 0 && !G.noBuild[cy * COLS + cx]) {
      G.sel = G.sel && G.sel.kind === 'cell' && G.sel.x === cx && G.sel.y === cy ? null : { kind: 'cell', x: cx, y: cy };
    } else G.sel = null;
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden && G && screen === 'play' && !G.over) G.paused = true; });

  // ---------- Loop ----------
  let last = performance.now();
  function frame(now) {
    let dt = Math.min(0.05, (now - last) / 1000); last = now;
    const steps = screen === 'play' && G ? G.speed : 1;
    for (let i = 0; i < steps; i++) update(dt);
    UI = [];
    if (screen === 'menu') drawMenu(); else drawPlay();
    if (msg) {
      ctx.globalAlpha = Math.min(1, msg.t * 2);
      text(msg.s, W / 2, OY + CELL * 1.2, CELL * 0.4, '#ffe0a0');
      ctx.globalAlpha = 1;
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  // Gancho para testes automatizados
  window.__rd = { get G() { return G; }, newGame, build, upgrade, callWave, update, MAPS, TOWERS };
})();
