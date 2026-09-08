<script lang="ts">
	import { Building2, TrendingUp } from 'lucide-svelte';

	export interface AirlineItem {
		airlineId: number;
		name: string;
		iata: string;
		totalFlights: number;
		totalRevenue: number;
		totalBookings: number;
		avgTicketPrice: number;
	}

	interface Props {
		airlines: AirlineItem[];
	}

	let { airlines = [] }: Props = $props();

	const maxRevenue = $derived(
		Math.max(...airlines.map((a) => a.totalRevenue), 1)
	);

	function formatCurrency(num: number): string {
		return new Intl.NumberFormat('pt-BR', {
			style: 'currency',
			currency: 'USD',
			maximumFractionDigits: 0
		}).format(num);
	}
</script>

<div class="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-6 backdrop-blur-xl">
	<div class="flex items-center justify-between">
		<div class="flex items-center gap-2">
			<Building2 class="h-5 w-5 text-indigo-400" />
			<h3 class="text-base font-semibold text-white">Participação de Mercado e Receita</h3>
		</div>
		<span class="text-xs text-zinc-400">Total: {airlines.length} companhias</span>
	</div>
	<p class="mt-1 text-xs text-zinc-400">Distribuição de faturamento por operador aéreo</p>

	<div class="mt-6 space-y-4">
		{#each airlines as item}
			{@const pct = (item.totalRevenue / maxRevenue) * 100}
			<div class="group rounded-xl border border-zinc-800/80 bg-zinc-950/40 p-3.5 transition-all hover:border-zinc-700">
				<div class="flex items-center justify-between text-xs">
					<div class="flex items-center gap-2">
						<span class="rounded bg-indigo-500/20 px-1.5 py-0.5 font-mono text-[10px] font-bold text-indigo-300">
							{item.iata}
						</span>
						<span class="font-semibold text-white">{item.name}</span>
					</div>
					<div class="flex items-center gap-3">
						<span class="text-zinc-400">{item.totalFlights} voos</span>
						<span class="font-bold text-emerald-400">{formatCurrency(item.totalRevenue)}</span>
					</div>
				</div>

				<!-- Progress bar -->
				<div class="mt-2.5 h-2 w-full overflow-hidden rounded-full bg-zinc-800">
					<div
						class="h-full rounded-full bg-gradient-to-r from-indigo-500 to-emerald-400 transition-all duration-700"
						style="width: {pct}%"
					></div>
				</div>

				<!-- Subtext row -->
				<div class="mt-2 flex justify-between text-[11px] text-zinc-500">
					<span>{item.totalBookings.toLocaleString('pt-BR')} reservas</span>
					<span>Tarifa Média: {formatCurrency(item.avgTicketPrice)}</span>
				</div>
			</div>
		{/each}
	</div>
</div>
