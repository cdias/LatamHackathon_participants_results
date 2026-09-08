<script lang="ts">
	import { Filter, RefreshCw, Plane, Building2 } from 'lucide-svelte';

	interface AirportOption {
		id: number;
		code: string;
		name: string;
	}

	interface AirlineOption {
		id: number;
		code: string;
		name: string;
	}

	interface Props {
		airports: AirportOption[];
		airlines: AirlineOption[];
		selectedAirlineId: number | null;
		selectedAirportId: number | null;
		loading: boolean;
		onfilterchange: (filters: { airlineId: number | null; airportId: number | null }) => void;
		onreset: () => void;
	}

	let {
		airports = [],
		airlines = [],
		selectedAirlineId = $bindable(null),
		selectedAirportId = $bindable(null),
		loading = false,
		onfilterchange,
		onreset
	}: Props = $props();

	function handleAirlineChange(e: Event) {
		const val = (e.target as HTMLSelectElement).value;
		selectedAirlineId = val ? Number(val) : null;
		onfilterchange({ airlineId: selectedAirlineId, airportId: selectedAirportId });
	}

	function handleAirportChange(e: Event) {
		const val = (e.target as HTMLSelectElement).value;
		selectedAirportId = val ? Number(val) : null;
		onfilterchange({ airlineId: selectedAirlineId, airportId: selectedAirportId });
	}
</script>

<div class="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-zinc-800 bg-zinc-900/60 p-4 backdrop-blur-xl">
	<div class="flex flex-wrap items-center gap-3">
		<div class="flex items-center gap-2 text-xs font-semibold text-zinc-300">
			<Filter class="h-4 w-4 text-indigo-400" />
			<span>Filtrar Dados:</span>
		</div>

		<!-- Airline Selector -->
		<div class="relative">
			<select
				value={selectedAirlineId ?? ''}
				onchange={handleAirlineChange}
				class="rounded-xl border border-zinc-800 bg-zinc-950/80 py-1.5 pl-3 pr-8 text-xs text-zinc-200 transition-colors focus:border-indigo-500 focus:outline-none"
			>
				<option value="">Todas as Companhias</option>
				{#each airlines as a}
					<option value={a.id}>{a.code} - {a.name}</option>
				{/each}
			</select>
		</div>

		<!-- Airport Selector -->
		<div class="relative">
			<select
				value={selectedAirportId ?? ''}
				onchange={handleAirportChange}
				class="rounded-xl border border-zinc-800 bg-zinc-950/80 py-1.5 pl-3 pr-8 text-xs text-zinc-200 transition-colors focus:border-indigo-500 focus:outline-none"
			>
				<option value="">Todos os Aeroportos de Origem</option>
				{#each airports as ap}
					<option value={ap.id}>{ap.code} - {ap.name}</option>
				{/each}
			</select>
		</div>
	</div>

	<!-- Reset / Refresh Button -->
	<div class="flex items-center gap-2">
		{#if selectedAirlineId || selectedAirportId}
			<button
				onclick={onreset}
				class="rounded-xl border border-zinc-800 bg-zinc-800/50 px-3 py-1.5 text-xs text-zinc-300 transition-colors hover:bg-zinc-800 hover:text-white"
			>
				Limpar Filtros
			</button>
		{/if}

		<div class="flex items-center gap-1 text-[11px] text-zinc-500">
			{#if loading}
				<RefreshCw class="h-3 w-3 animate-spin text-indigo-400" />
				<span>Atualizando métricas...</span>
			{:else}
				<span class="inline-block h-2 w-2 rounded-full bg-emerald-500"></span>
				<span>TiDB em Tempo Real</span>
			{/if}
		</div>
	</div>
</div>
