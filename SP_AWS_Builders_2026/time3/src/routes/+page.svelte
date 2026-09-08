<script lang="ts">
	import type { PageData } from './$types';
	import {
		DollarSign,
		Ticket,
		Plane,
		Percent,
		Users,
		BarChart3,
		Compass,
		Layers,
		UserCheck
	} from 'lucide-svelte';

	import MetricCard from '$lib/components/MetricCard.svelte';
	import RevenueChart from '$lib/components/RevenueChart.svelte';
	import LoadFactorGauge from '$lib/components/LoadFactorGauge.svelte';
	import RoutesTable from '$lib/components/RoutesTable.svelte';
	import AirlinePerformanceBar from '$lib/components/AirlinePerformanceBar.svelte';
	import FleetUtilizationCard from '$lib/components/FleetUtilizationCard.svelte';
	import DemographicsChart from '$lib/components/DemographicsChart.svelte';
	import ScheduleHeatmap from '$lib/components/ScheduleHeatmap.svelte';
	import DashboardFilters from '$lib/components/DashboardFilters.svelte';

	let { data }: { data: PageData } = $props();

	// Reactive state for active tab & dynamic filtering
	let activeTab = $state<'overview' | 'routes' | 'fleet' | 'passengers'>('overview');
	let selectedAirlineId = $state<number | null>(null);
	let selectedAirportId = $state<number | null>(null);
	let loading = $state(false);

	// Derived state with dynamic client-side override support
	let customAnalytics = $state<{
		kpis: typeof data.kpis;
		trends: typeof data.trends;
		topRoutes: typeof data.topRoutes;
		airlines: typeof data.airlines;
		fleet: typeof data.fleet;
		demographics: typeof data.demographics;
		weeklySchedule: typeof data.weeklySchedule;
	} | null>(null);

	const kpis = $derived(customAnalytics?.kpis ?? data.kpis);
	const trends = $derived(customAnalytics?.trends ?? data.trends);
	const topRoutes = $derived(customAnalytics?.topRoutes ?? data.topRoutes);
	const airlines = $derived(customAnalytics?.airlines ?? data.airlines);
	const fleet = $derived(customAnalytics?.fleet ?? data.fleet);
	const demographics = $derived(customAnalytics?.demographics ?? data.demographics);
	const weeklySchedule = $derived(customAnalytics?.weeklySchedule ?? data.weeklySchedule);

	async function handleFilterChange(filters: { airlineId: number | null; airportId: number | null }) {
		loading = true;
		try {
			const params = new URLSearchParams();
			if (filters.airlineId) params.set('airlineId', String(filters.airlineId));
			if (filters.airportId) params.set('fromAirportId', String(filters.airportId));

			const res = await fetch(`/api/analytics?${params.toString()}`);
			if (res.ok) {
				const json = await res.json();
				customAnalytics = json;
			}
		} catch (err) {
			console.error('Falha ao buscar dados filtrados:', err);
		} finally {
			loading = false;
		}
	}

	function handleResetFilters() {
		selectedAirlineId = null;
		selectedAirportId = null;
		customAnalytics = null;
	}

	function formatCurrency(val: number): string {
		return new Intl.NumberFormat('pt-BR', {
			style: 'currency',
			currency: 'USD',
			maximumFractionDigits: 0
		}).format(val);
	}
</script>

<div class="space-y-8">
	<!-- Page Header -->
	<div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
		<div>
			<h1 class="text-2xl font-black tracking-tight text-white sm:text-3xl">
				Inteligência de Aviação e Análise de Reservas
			</h1>
			<p class="mt-1 text-sm text-zinc-400">
				Monitoramento em tempo real de operações aéreas, taxa de ocupação e faturamento de passageiros.
			</p>
		</div>

		<!-- Tab Navigation Buttons -->
		<div class="flex items-center gap-1.5 overflow-x-auto rounded-2xl border border-zinc-800 bg-zinc-900/80 p-1.5 backdrop-blur-md">
			<button
				onclick={() => (activeTab = 'overview')}
				class="flex items-center gap-2 rounded-xl px-3.5 py-2 text-xs font-semibold transition-all {activeTab ===
				'overview'
					? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
					: 'text-zinc-400 hover:text-white'}"
			>
				<BarChart3 class="h-4 w-4" />
				<span>Visão Geral</span>
			</button>

			<button
				onclick={() => (activeTab = 'routes')}
				class="flex items-center gap-2 rounded-xl px-3.5 py-2 text-xs font-semibold transition-all {activeTab ===
				'routes'
					? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
					: 'text-zinc-400 hover:text-white'}"
			>
				<Compass class="h-4 w-4" />
				<span>Rotas e Horários</span>
			</button>

			<button
				onclick={() => (activeTab = 'fleet')}
				class="flex items-center gap-2 rounded-xl px-3.5 py-2 text-xs font-semibold transition-all {activeTab ===
				'fleet'
					? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
					: 'text-zinc-400 hover:text-white'}"
			>
				<Layers class="h-4 w-4" />
				<span>Frota e Capacidade</span>
			</button>

			<button
				onclick={() => (activeTab = 'passengers')}
				class="flex items-center gap-2 rounded-xl px-3.5 py-2 text-xs font-semibold transition-all {activeTab ===
				'passengers'
					? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
					: 'text-zinc-400 hover:text-white'}"
			>
				<UserCheck class="h-4 w-4" />
				<span>Demografia</span>
			</button>
		</div>
	</div>

	<!-- Interactive Filter Toolbar -->
	<DashboardFilters
		airports={data.meta.airports}
		airlines={data.meta.airlines}
		bind:selectedAirlineId
		bind:selectedAirportId
		{loading}
		onfilterchange={handleFilterChange}
		onreset={handleResetFilters}
	/>

	<!-- Top KPI Cards Grid -->
	<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
		<MetricCard
			title="Receita Total"
			value={formatCurrency(kpis.totalRevenue)}
			subtext="Faturamento bruto de reservas"
			change={14.8}
			icon={DollarSign}
			color="emerald"
		/>

		<MetricCard
			title="Total de Reservas"
			value={kpis.totalBookings.toLocaleString('pt-BR')}
			subtext="Bilhetes confirmados emitidos"
			change={8.2}
			icon={Ticket}
			color="indigo"
		/>

		<MetricCard
			title="Voos Ativos"
			value={kpis.totalFlights.toLocaleString('pt-BR')}
			subtext="Rotas programadas e operadas"
			change={4.1}
			icon={Plane}
			color="sky"
		/>

		<MetricCard
			title="Tarifa Média"
			value={formatCurrency(kpis.avgTicketPrice)}
			subtext="Rendimento médio por assento"
			change={-1.5}
			icon={Percent}
			color="amber"
		/>

		<MetricCard
			title="Taxa de Ocupação"
			value={`${kpis.avgLoadFactor}%`}
			subtext="Aproveitamento médio da frota"
			change={5.3}
			icon={Users}
			color="violet"
		/>
	</div>

	<!-- Tab Content Views -->
	{#if activeTab === 'overview'}
		<div class="space-y-8">
			<!-- Chart & Gauge Row -->
			<div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
				<div class="lg:col-span-2">
					<RevenueChart data={trends} />
				</div>
				<div>
					<LoadFactorGauge loadFactor={kpis.avgLoadFactor} />
				</div>
			</div>

			<!-- Leaderboard & Airlines Row -->
			<div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
				<div class="lg:col-span-2">
					<RoutesTable routes={topRoutes} />
				</div>
				<div>
					<AirlinePerformanceBar {airlines} />
				</div>
			</div>
		</div>
	{:else if activeTab === 'routes'}
		<div class="space-y-8">
			<RoutesTable routes={topRoutes} />
			<ScheduleHeatmap schedule={weeklySchedule} />
		</div>
	{:else if activeTab === 'fleet'}
		<div class="space-y-8">
			<div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
				<div class="lg:col-span-2">
					<FleetUtilizationCard {fleet} />
				</div>
				<div>
					<LoadFactorGauge
						loadFactor={kpis.avgLoadFactor}
						title="Ocupação Média da Frota"
						subtitle="Percentual médio de assentos preenchidos em voos ativos"
					/>
				</div>
			</div>
		</div>
	{:else if activeTab === 'passengers'}
		<div class="space-y-8">
			<DemographicsChart
				countries={demographics.countries}
				genders={demographics.genders}
			/>
		</div>
	{/if}
</div>
