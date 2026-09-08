<script setup>
import { ref, reactive } from 'vue'
import { api, setToken } from './api.js'

const auth = reactive({ logged: false, airline: '', airlineId: null })
const login = reactive({ username: 'airline82', password: 'airrevenue2026', error: '' })
const state = reactive({ loading: false, tab: 'reco' })
// flags de loading por ação (feedback visual nos botões)
const busy = reactive({ login: false, targets: false, copy: false, save: false, search: false })

const flights = ref([])
const selected = ref(null)
const targets = ref([])
const copy = reactive({ body: '', source: '', discount: 15, priceOld: 0, priceNew: 0 })
const campaigns = ref([])
const search = reactive({ q: '', results: [] })

// evita exibir "null" quando um código/cidade vier vazio
function safe(v) { return v && v !== 'null' ? v : '—' }

async function doLogin() {
  login.error = ''; busy.login = true
  try {
    const r = await api.login(login.username, login.password)
    setToken(r.access_token)
    auth.logged = true; auth.airline = r.airline_name; auth.airlineId = r.airline_id
    await loadReco(); await loadCampaigns()
  } catch (e) { login.error = e.message } finally { busy.login = false }
}

async function loadReco() {
  state.loading = true
  try { flights.value = (await api.recommendations()).flights } finally { state.loading = false }
}
async function loadCampaigns() { campaigns.value = (await api.campaigns()).campaigns }

async function pickFlight(f) {
  selected.value = f; targets.value = []; copy.body = ''; busy.targets = true
  try { targets.value = (await api.targets(f.flight_id)).targets } finally { busy.targets = false }
}

async function genCopy() {
  busy.copy = true
  try {
    const route = `${safe(selected.value.from_iata)}->${safe(selected.value.to_iata)}`
    const r = await api.generateCopy({ flight_id: selected.value.flight_id, route, discount_pct: copy.discount, context: '' })
    copy.body = r.body; copy.source = r.source; copy.priceOld = r.price_old; copy.priceNew = r.price_new
  } finally { busy.copy = false }
}

async function saveCampaign() {
  busy.save = true
  try {
    const f = selected.value
    await api.createCampaign({
      flight_id: f.flight_id,
      title: `Promo ${safe(f.from_iata)}-${safe(f.to_iata)} (${copy.discount}% off)`,
      body: copy.body || `Promoção ${copy.discount}% off`,
      discount_pct: copy.discount,
      target_passenger_ids: targets.value.map(t => t.passenger_id),
    })
    await loadCampaigns(); state.tab = 'camp'
  } finally { busy.save = false }
}

async function doSearch() {
  busy.search = true
  try { search.results = (await api.search(search.q)).results } finally { busy.search = false }
}
</script>

<template>
  <div v-if="!auth.logged" class="login">
    <div class="card">
      <h1>✈️ AirRevenue</h1>
      <p class="muted">Copiloto de promoções para voos ociosos</p>
      <input v-model="login.username" placeholder="Usuário da companhia" />
      <input v-model="login.password" type="password" placeholder="Senha" @keyup.enter="doLogin" />
      <button @click="doLogin" :disabled="busy.login">
        <span v-if="busy.login" class="spin"></span>{{ busy.login ? 'Entrando...' : 'Entrar' }}
      </button>
      <p v-if="login.error" class="err">{{ login.error }}</p>
      <p class="hint">Demo: airline82 / airrevenue2026</p>
    </div>
  </div>

  <div v-else class="app">
    <header>
      <b>✈️ AirRevenue</b>
      <span class="badge">{{ auth.airline }} · cia {{ auth.airlineId }}</span>
      <nav>
        <a :class="{on:state.tab==='reco'}" @click="state.tab='reco'">Recomendações</a>
        <a :class="{on:state.tab==='camp'}" @click="state.tab='camp'">Campanhas ({{ campaigns.length }})</a>
        <a :class="{on:state.tab==='search'}" @click="state.tab='search'">Busca semântica</a>
      </nav>
    </header>

    <!-- RECOMENDAÇÕES -->
    <main v-show="state.tab==='reco'" class="grid">
      <section class="col">
        <h2>Voos com assentos ociosos</h2>
        <table>
          <thead><tr><th>Voo</th><th>Rota</th><th>Cap</th><th>Ocioso</th><th>Score</th></tr></thead>
          <tbody>
            <tr v-for="f in flights" :key="f.flight_id" :class="{sel:selected&&selected.flight_id===f.flight_id}" @click="pickFlight(f)">
              <td>{{ f.flightno }}</td>
              <td>{{ safe(f.origem) }} → {{ safe(f.destino) }}</td>
              <td class="num">{{ f.capacity }}</td>
              <td class="num"><b>{{ f.ociosidade_pct }}%</b></td>
              <td class="num">{{ f.score }}</td>
            </tr>
          </tbody>
        </table>
      </section>
      <section class="col" v-if="selected">
        <h2>Voo {{ selected.flightno }} — {{ safe(selected.from_iata) }}→{{ safe(selected.to_iata) }}</h2>
        <div class="box">
          <label>Desconto sugerido: <b>{{ copy.discount }}%</b></label>
          <input type="range" min="5" max="60" v-model.number="copy.discount" />
          <button @click="genCopy" :disabled="busy.copy">
            <span v-if="busy.copy" class="spin"></span>{{ busy.copy ? 'Gerando...' : 'Gerar texto com IA' }}
          </button>
          <textarea v-model="copy.body" rows="4" placeholder="Texto da promoção..."></textarea>
          <div v-if="copy.priceOld" class="prices">
            <span class="old">De US$ {{ copy.priceOld.toFixed(2) }}</span>
            <span class="new">por US$ {{ copy.priceNew.toFixed(2) }}</span>
          </div>
          <small v-if="copy.source" class="muted">origem: {{ copy.source }}</small>
          <button class="primary" @click="saveCampaign" :disabled="busy.save">
            <span v-if="busy.save" class="spin"></span>{{ busy.save ? 'Salvando...' : `Criar campanha (${targets.length} alvos)` }}
          </button>
        </div>
        <h3>Passageiros frequentes (alvos) <span v-if="busy.targets" class="spin"></span></h3>
        <table>
          <thead><tr><th>Passageiro</th><th>Voos cia</th><th>Rota</th><th>Score</th></tr></thead>
          <tbody>
            <tr v-for="t in targets" :key="t.passenger_id">
              <td>{{ t.firstname }} {{ t.lastname }}</td>
              <td class="num">{{ t.voos_na_cia }}</td>
              <td class="num">{{ t.voos_na_rota }}</td>
              <td class="num">{{ t.score }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>

    <!-- CAMPANHAS -->
    <main v-show="state.tab==='camp'">
      <h2>Campanhas da companhia</h2>
      <div v-if="!campaigns.length" class="muted">Nenhuma campanha ainda.</div>
      <div v-for="c in campaigns" :key="c.id" class="camp">
        <div><b>{{ c.title }}</b> <span class="badge">{{ c.discount_pct }}% off · {{ c.alvos }} alvos · {{ c.status }}</span></div>
        <p>{{ c.body }}</p>
      </div>
    </main>

    <!-- BUSCA -->
    <main v-show="state.tab==='search'">
      <h2>Busca semântica (vetorial no TiDB)</h2>
      <div class="box">
        <input v-model="search.q" placeholder="ex: voos noturnos para o litoral" @keyup.enter="doSearch" />
        <button @click="doSearch" :disabled="busy.search">
          <span v-if="busy.search" class="spin"></span>{{ busy.search ? 'Buscando...' : 'Buscar' }}
        </button>
      </div>
      <div v-for="(r,i) in search.results" :key="i" class="camp">
        <span class="badge">dist {{ r.distancia.toFixed(3) }}</span> {{ r.note }}
      </div>
    </main>
  </div>
</template>

<style>
*{box-sizing:border-box} body{margin:0;font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#0d1117;color:#e6edf3}
.login{min-height:100vh;display:flex;align-items:center;justify-content:center}
.card{background:#161b22;border:1px solid #30363d;padding:32px;border-radius:12px;width:340px;display:flex;flex-direction:column;gap:10px}
.card h1{margin:0}
input,textarea{background:#0d1117;border:1px solid #30363d;color:#e6edf3;padding:10px;border-radius:8px;font:inherit;width:100%}
button{background:#1f6feb;color:#fff;border:0;padding:10px 14px;border-radius:8px;cursor:pointer;font:inherit;display:inline-flex;align-items:center;justify-content:center;gap:8px}
button.primary{background:#238636}button:hover:not(:disabled){filter:brightness(1.1)}
button:disabled{opacity:.65;cursor:progress}
.spin{width:14px;height:14px;border:2px solid #ffffff55;border-top-color:#fff;border-radius:50%;display:inline-block;animation:sp .6s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}
.err{color:#f85149}.hint,.muted{color:#8b949e;font-size:13px}
header{display:flex;align-items:center;gap:16px;padding:14px 24px;border-bottom:1px solid #30363d;background:#161b22}
.badge{background:#1f6feb22;color:#58a6ff;border:1px solid #1f6feb55;border-radius:20px;padding:3px 12px;font-size:12px}
nav{margin-left:auto;display:flex;gap:14px}nav a{color:#8b949e;cursor:pointer;padding:4px 8px}nav a.on{color:#58a6ff;border-bottom:2px solid #58a6ff}
main{padding:24px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:8px;border-bottom:1px solid #21262d;text-align:left}
th{color:#58a6ff}tr:hover td{background:#1a2029;cursor:pointer}tr.sel td{background:#1f6feb22}
.num{text-align:right}.box{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:16px;display:flex;flex-direction:column;gap:10px;margin-bottom:16px}
.camp{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:14px;margin-bottom:10px}
.prices{display:flex;gap:12px;align-items:baseline}
.prices .old{color:#8b949e;text-decoration:line-through;font-size:15px}
.prices .new{color:#3fb950;font-size:22px;font-weight:700}
</style>
