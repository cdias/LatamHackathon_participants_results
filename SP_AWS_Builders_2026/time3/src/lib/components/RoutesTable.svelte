<script lang="ts">
	import { Plane, Search, ArrowRight, DollarSign, Users, ChevronUp, ChevronDown } from 'lucide-svelte';

	export interface RouteItem {
		flightno: string;
		fromIata: string;
		fromName: string;
		toIata: string;
		toName: string;
		airlineName: string;
		airlineIata: string;
		totalFlights: number;
		totalBookings: number;
		totalRevenue: number;
		avgPrice: number;
	}

	interface Props {
		routes: RouteItem[];
	}

	let { routes = [] }: Props = $props();

	let searchQuery = $state('');
	let sortField = $state<'revenue' | 'bookings' | 'flights' | 'price'>('revenue');
	let sortAsc = $state(false);

	const filteredRoutes = $derived(
		routes
			.filter((r) => {
				const q = searchQuery.toLowerCase();
				return (
					r.flightno.toLowerCase().includes(q) ||
					r.fromIata.toLowerCase().includes(q) ||
					r.toIata.toLowerCase().includes(q) ||
					r.fromName.toLowerCase().includes(q) ||
					r.toName.toLowerCase().includes(q) ||
					r.airlineName.toLowerCase().includes(q)
				);
			})
			.sort((a, b) => {
				let diff = 0;
				if (sortField === 'revenue') diff = a.totalRevenue - b.totalRevenue;
				if (sortField === 'bookings') diff = a.totalBookings - b.totalBookings;
				if (sortField === 'flights') diff = a.totalFlights - b.totalFlights;
				if (sortField === 'price') diff = a.avgPrice - b.avgPrice;
				return sortAsc ? diff : -diff;
			})
	);

	function toggleSort(field: 'revenue' | 'bookings' | 'flights' | 'price') {
		if (sortField === field) {
			sortAsc = !sortAsc;
		} else {
			sortField = field;
			sortAsc = false;
		}
	}

	function formatCurrency(val: number): string {
		return new Intl.NumberFormat('pt-BR', {
			style: 'currency',
			currency: 'USD',
			maximumFractionDigits: 0
		}).format(val);
	}
</script>

<div class="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-6 backdrop-blur-xl">
	<!-- Top Bar -->
	<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
		<div>
			<div class="flex items-center gap-2">
				<Plane class="h-5 w-5 text-indigo-400" />
				<h3 class="text-base font-semibold text-white">Desempenho de Rotas e Faturamento</h3>
			</div>
			<p class="mt-1 text-xs text-zinc-400">Conexões aéreas de maior rendimento ordenadas por receita de reservas</p>
		</div>

		<!-- Search Box -->
		<div class="relative w-full sm:w-64">
			<Search class="absolute left-3 top-2.5 h-4 w-4 text-zinc-500" />
			<input
				type="text"
				placeholder="Buscar rota ou aeroporto..."
				bind:value={searchQuery}
				class="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 py-2 pl-9 pr-4 text-xs text-white placeholder-zinc-500 transition-all focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
			/>
		</div>
	</div>

	<!-- Table Area -->
	<div class="mt-5 overflow-x-auto">
		<table class="w-full text-left text-xs">
			<thead>
				<tr class="border-b border-zinc-800 text-zinc-400">
					<th class="pb-3 font-medium">Rota / Nº Voo</th>
					<th class="pb-3 font-medium">Companhia</th>
					<th class="cursor-pointer pb-3 font-medium text-right hover:text-white" onclick={() => toggleSort('flights')}>
						<div class="inline-flex items-center gap-1">
							<span>Voos</span>
							{#if sortField === 'flights'}
								{#if sortAsc}<ChevronUp class="h-3.5 w-3.5 text-indigo-400" />{:else}<ChevronDown class="h-3.5 w-3.5 text-indigo-400" />{/if}
							{/if}
						</div>
					</th>
					<th class="cursor-pointer pb-3 font-medium text-right hover:text-white" onclick={() => toggleSort('bookings')}>
						<div class="inline-flex items-center gap-1">
							<span>Assentos Reservados</span>
							{#if sortField === 'bookings'}
								{#if sortAsc}<ChevronUp class="h-3.5 w-3.5 text-indigo-400" />{:else}<ChevronDown class="h-3.5 w-3.5 text-indigo-400" />{/if}
							{/if}
						</div>
					</th>
					<th class="cursor-pointer pb-3 font-medium text-right hover:text-white" onclick={() => toggleSort('price')}>
						<div class="inline-flex items-center gap-1">
							<span>Tarifa Média</span>
							{#if sortField === 'price'}
								{#if sortAsc}<ChevronUp class="h-3.5 w-3.5 text-indigo-400" />{:else}<ChevronDown class="h-3.5 w-3.5 text-indigo-400" />{/if}
							{/if}
						</div>
					</th>
					<th class="cursor-pointer pb-3 font-medium text-right hover:text-white" onclick={() => toggleSort('revenue')}>
						<div class="inline-flex items-center gap-1">
							<span>Receita Total</span>
							{#if sortField === 'revenue'}
								{#if sortAsc}<ChevronUp class="h-3.5 w-3.5 text-indigo-400" />{:else}<ChevronDown class="h-3.5 w-3.5 text-indigo-400" />{/if}
							{/if}
						</div>
					</th>
				</tr>
			</thead>
			<tbody class="divide-y divide-zinc-800/60">
				{#each filteredRoutes as route}
					<tr class="group transition-colors hover:bg-zinc-800/30">
						<!-- Route & Code -->
						<td class="py-3.5">
							<div class="flex items-center gap-2.5">
								<div class="flex items-center gap-1.5 rounded-lg border border-zinc-800 bg-zinc-950/80 px-2 py-1 font-mono text-xs font-bold text-white">
									<span class="text-indigo-400">{route.fromIata}</span>
									<ArrowRight class="h-3 w-3 text-zinc-500" />
									<span class="text-indigo-400">{route.toIata}</span>
								</div>
								<div>
									<div class="font-semibold text-zinc-200">{route.flightno}</div>
									<div class="text-[10px] text-zinc-500 truncate max-w-[150px]">{route.fromName} → {route.toName}</div>
								</div>
							</div>
						</td>

						<!-- Carrier -->
						<td class="py-3.5">
							<span class="inline-flex items-center rounded-md border border-zinc-800 bg-zinc-900 px-2 py-0.5 text-xs text-zinc-300">
								{route.airlineName}
							</span>
						</td>

						<!-- Flights -->
						<td class="py-3.5 text-right font-medium text-zinc-300">
							{route.totalFlights}
						</td>

						<!-- Bookings -->
						<td class="py-3.5 text-right font-semibold text-emerald-400">
							{route.totalBookings.toLocaleString('pt-BR')}
						</td>

						<!-- Avg Price -->
						<td class="py-3.5 text-right text-zinc-300">
							{formatCurrency(route.avgPrice)}
						</td>

						<!-- Total Revenue -->
						<td class="py-3.5 text-right font-bold text-white">
							{formatCurrency(route.totalRevenue)}
						</td>
					</tr>
				{:else}
					<tr>
						<td colspan="6" class="py-8 text-center text-zinc-500">
							Nenhuma rota encontrada para a busca realizada.
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
