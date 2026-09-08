<script lang="ts">
	import type { PageData } from './$types';
	import {
		CloudLightning,
		Wind,
		Thermometer,
		Droplets,
		Gauge,
		AlertTriangle,
		ShieldAlert,
		RefreshCw,
		Plane,
		CheckCircle2,
		Bot,
		ArrowRight
	} from 'lucide-svelte';

	let { data }: { data: PageData } = $props();

	let liveData = $state<{
		stations: typeof data.stations;
		flights: typeof data.flights;
		briefing: typeof data.briefing;
	} | null>(null);

	const stations = $derived(liveData?.stations ?? data.stations);
	const flights = $derived(liveData?.flights ?? data.flights);
	const briefing = $derived(liveData?.briefing ?? data.briefing);

	let loading = $state(false);

	async function refreshBriefing() {
		loading = true;
		try {
			const res = await fetch('/api/ai/weather-risk');
			if (res.ok) {
				const json = await res.json();
				liveData = json;
			}
		} catch (err) {
			console.error('Falha ao atualizar briefing meteorológico:', err);
		} finally {
			loading = false;
		}
	}

	const riskBadgeStyles = {
		CRITICAL: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
		HIGH: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
		MEDIUM: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
		LOW: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
	};

	const riskLabels = {
		CRITICAL: 'CRÍTICO',
		HIGH: 'ALTO',
		MEDIUM: 'MÉDIO',
		LOW: 'BAIXO'
	};
</script>

<div class="space-y-8">
	<!-- Top Title & Action Bar -->
	<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
		<div>
			<div class="flex items-center gap-2">
				<div class="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-rose-500 to-amber-500 shadow-lg shadow-rose-500/20">
					<CloudLightning class="h-5 w-5 text-white" />
				</div>
				<h1 class="text-2xl font-black tracking-tight text-white sm:text-3xl">
					Disrupção Meteorológica e Risco Operacional
				</h1>
			</div>
			<p class="mt-1 text-sm text-zinc-400">
				Telemetria meteorológica em tempo real do TiDB correlacionada com despacho de risco operacional via Amazon Bedrock.
			</p>
		</div>

		<button
			onclick={refreshBriefing}
			disabled={loading}
			class="flex items-center gap-2 rounded-xl bg-zinc-800 px-4 py-2.5 text-xs font-semibold text-white shadow-lg transition-all hover:bg-zinc-700 disabled:opacity-50"
		>
			<RefreshCw class="h-3.5 w-3.5 {loading ? 'animate-spin text-indigo-400' : ''}" />
			<span>Regenerar Briefing de IA</span>
		</button>
	</div>

	<!-- AI Executive Dispatch Briefing Banner -->
	<div class="rounded-3xl border border-rose-500/30 bg-gradient-to-br from-rose-950/30 via-zinc-900/90 to-zinc-950 p-6 backdrop-blur-2xl shadow-xl shadow-rose-950/30">
		<div class="flex items-center justify-between border-b border-rose-500/20 pb-4">
			<div class="flex items-center gap-2.5">
				<div class="flex h-8 w-8 items-center justify-center rounded-lg bg-rose-500/20 text-rose-400">
					<Bot class="h-4 w-4" />
				</div>
				<div>
					<h3 class="text-base font-bold text-white">Briefing Tático de Despacho (Bedrock AI)</h3>
					<span class="text-[11px] text-zinc-400">Síntese autônoma de risco baseada nos logs climáticos ativos do TiDB</span>
				</div>
			</div>
			<span class="rounded-full border border-rose-500/30 bg-rose-500/10 px-3 py-1 text-xs font-semibold text-rose-300">
				Nível de Alerta Alto
			</span>
		</div>

		<div class="mt-5 prose prose-invert max-w-none text-xs leading-relaxed text-zinc-300">
			<div class="whitespace-pre-wrap">{briefing}</div>
		</div>
	</div>

	<!-- Weather Stations Telemetry Grid -->
	<div class="space-y-4">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-2">
				<Wind class="h-4 w-4 text-sky-400" />
				<h3 class="text-sm font-bold uppercase tracking-wider text-zinc-300">Estações Meteorológicas nos Hubs</h3>
			</div>
			<span class="text-xs text-zinc-500">Fontes Ativas: {stations.length}</span>
		</div>

		<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
			{#each stations as s}
				<div class="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-5 backdrop-blur-xl transition-all hover:border-zinc-700">
					<div class="flex items-start justify-between">
						<div>
							<h4 class="font-bold text-white">{s.airportName || `Estação #${s.station}`}</h4>
							<span class="text-[11px] text-zinc-500">{s.logDate} • {s.time}</span>
						</div>
						<span class="rounded-lg border px-2 py-0.5 text-[10px] font-bold uppercase {riskBadgeStyles[s.riskLevel]}">
							{riskLabels[s.riskLevel] || s.riskLevel}
						</span>
					</div>

					<div class="mt-4 rounded-xl bg-zinc-950/70 p-3 font-mono text-xs">
						<div class="flex items-center justify-between text-zinc-300">
							<span class="text-zinc-500">Condição:</span>
							<span class="font-bold capitalize text-amber-300">{s.weather.replace(/-/g, ' ')}</span>
						</div>
					</div>

					<div class="mt-4 grid grid-cols-3 gap-2 border-t border-zinc-800/80 pt-3 text-center text-xs">
						<div>
							<span class="text-[10px] text-zinc-500 uppercase">Temp</span>
							<div class="mt-0.5 font-bold text-white">{s.temp}°C</div>
						</div>
						<div>
							<span class="text-[10px] text-zinc-500 uppercase">Vento</span>
							<div class="mt-0.5 font-bold text-sky-300">{s.wind} kt</div>
						</div>
						<div>
							<span class="text-[10px] text-zinc-500 uppercase">Pressão</span>
							<div class="mt-0.5 font-bold text-zinc-300">{s.airpressure} hPa</div>
						</div>
					</div>
				</div>
			{/each}
		</div>
	</div>

	<!-- High Risk Scheduled Flights Table -->
	<div class="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-6 backdrop-blur-xl">
		<div class="flex items-center gap-2">
			<Plane class="h-5 w-5 text-rose-400" />
			<h3 class="text-base font-semibold text-white">Voos Programados com Risco Operacional</h3>
		</div>
		<p class="mt-1 text-xs text-zinc-400">Partidas cruzando tempestades e corredores de baixa visibilidade</p>

		<div class="mt-5 overflow-x-auto">
			<table class="w-full text-left text-xs">
				<thead>
					<tr class="border-b border-zinc-800 text-zinc-400">
						<th class="pb-3 font-medium">Nº Voo e Rota</th>
						<th class="pb-3 font-medium">Companhia</th>
						<th class="pb-3 font-medium">Partida Prevista</th>
						<th class="pb-3 font-medium">Condição de Risco</th>
						<th class="pb-3 font-medium text-right">Índice de Risco</th>
						<th class="pb-3 font-medium">Recomendação do Despacho IA</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-zinc-800/60">
					{#each flights as f}
						<tr class="transition-colors hover:bg-zinc-800/30">
							<td class="py-3.5">
								<div class="flex items-center gap-2">
									<span class="font-bold text-white">{f.flightno}</span>
									<span class="rounded bg-zinc-800 px-1.5 py-0.5 text-[10px] font-mono text-indigo-300">
										{f.fromIata} → {f.toIata}
									</span>
								</div>
							</td>
							<td class="py-3.5 text-zinc-300">{f.airlineName}</td>
							<td class="py-3.5 text-zinc-400">{f.departure}</td>
							<td class="py-3.5">
								<span class="rounded-md border border-rose-500/20 bg-rose-500/10 px-2 py-0.5 text-[11px] font-semibold text-rose-400 capitalize">
									{f.weatherCondition.replace(/-/g, ' ')}
								</span>
							</td>
							<td class="py-3.5 text-right font-bold text-rose-400">
								{f.riskScore}%
							</td>
							<td class="py-3.5 text-zinc-300 max-w-xs truncate" title={f.recommendation}>
								{f.recommendation}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</div>
