<script lang="ts">
	import { PlaneTakeoff, Gauge } from 'lucide-svelte';

	export interface FleetItem {
		typeId: number;
		identifier: string;
		description: string;
		airplaneCount: number;
		avgCapacity: number;
		totalFlights: number;
		totalBookings: number;
		loadFactor: number;
	}

	interface Props {
		fleet: FleetItem[];
	}

	let { fleet = [] }: Props = $props();

	function truncate(str: string | null | undefined, max = 100): string {
		if (!str) return 'Aeronave Comercial de Passageiros';
		if (str.length <= max) return str;
		return str.slice(0, max) + '...';
	}
</script>

<div class="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-6 backdrop-blur-xl">
	<div class="flex items-center justify-between">
		<div class="flex items-center gap-2">
			<PlaneTakeoff class="h-5 w-5 text-sky-400" />
			<h3 class="text-base font-semibold text-white">Utilização da Frota e Aeronaves</h3>
		</div>
		<span class="text-xs text-zinc-400">Total de Modelos: {fleet.length}</span>
	</div>
	<p class="mt-1 text-xs text-zinc-400">Aproveitamento de capacidade, taxa de ocupação e voos por modelo de aeronave</p>

	<div class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
		{#each fleet as item}
			<div class="rounded-xl border border-zinc-800/80 bg-zinc-950/50 p-4 transition-all hover:border-zinc-700">
				<div class="flex items-start justify-between">
					<div class="max-w-[75%]">
						<h4 class="text-sm font-bold text-white">{item.identifier}</h4>
						<p class="mt-0.5 text-[11px] text-zinc-500 line-clamp-2" title={item.description || 'Aeronave Comercial de Passageiros'}>
							{truncate(item.description, 100)}
						</p>
					</div>
					<span class="rounded-full border border-sky-500/30 bg-sky-500/10 px-2 py-0.5 text-[10px] font-semibold text-sky-300">
						{item.airplaneCount} {item.airplaneCount === 1 ? 'aeronave' : 'aeronaves'}
					</span>
				</div>

				<div class="mt-4 grid grid-cols-3 gap-2 border-t border-zinc-800/60 pt-3 text-center text-xs">
					<div>
						<div class="text-[10px] uppercase text-zinc-500">Cap. Média</div>
						<div class="mt-0.5 font-bold text-zinc-200">{item.avgCapacity} assentos</div>
					</div>
					<div>
						<div class="text-[10px] uppercase text-zinc-500">Voos</div>
						<div class="mt-0.5 font-bold text-zinc-200">{item.totalFlights}</div>
					</div>
					<div>
						<div class="text-[10px] uppercase text-zinc-500">Ocupação</div>
						<div class="mt-0.5 font-bold {item.loadFactor >= 80 ? 'text-emerald-400' : 'text-amber-400'}">
							{item.loadFactor}%
						</div>
					</div>
				</div>

				<!-- Load factor bar -->
				<div class="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-zinc-800">
					<div
						class="h-full rounded-full transition-all duration-700 {item.loadFactor >= 80 ? 'bg-emerald-500' : 'bg-amber-500'}"
						style="width: {item.loadFactor}%"
					></div>
				</div>
			</div>
		{/each}
	</div>
</div>
