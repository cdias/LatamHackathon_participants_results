<script lang="ts">
	import { DollarSign, Ticket, Calendar } from 'lucide-svelte';

	interface TrendPoint {
		date: string;
		revenue: number;
		bookings: number;
		flights: number;
	}

	interface Props {
		data: TrendPoint[];
	}

	let { data }: Props = $props();

	let activeMetric = $state<'revenue' | 'bookings'>('revenue');
	let hoveredIndex = $state<number | null>(null);

	const width = 800;
	const height = 280;
	const padding = { top: 20, right: 30, bottom: 40, left: 60 };

	const chartWidth = width - padding.left - padding.right;
	const chartHeight = height - padding.top - padding.bottom;

	const values = $derived(
		data.map((d) => (activeMetric === 'revenue' ? d.revenue : d.bookings))
	);

	const maxValue = $derived(Math.max(...values, 100));
	const minValue = $derived(0);

	const points = $derived(
		data.map((d, i) => {
			const x = padding.left + (i / Math.max(data.length - 1, 1)) * chartWidth;
			const val = activeMetric === 'revenue' ? d.revenue : d.bookings;
			const y = padding.top + chartHeight - ((val - minValue) / (maxValue - minValue)) * chartHeight;
			return { x, y, data: d, val };
		})
	);

	const linePath = $derived(
		points.length > 0
			? points.reduce((acc, p, i) => `${acc} ${i === 0 ? 'M' : 'L'} ${p.x},${p.y}`, '')
			: ''
	);

	const areaPath = $derived(
		points.length > 0
			? `${linePath} L ${points[points.length - 1].x},${padding.top + chartHeight} L ${points[0].x},${padding.top + chartHeight} Z`
			: ''
	);

	function formatCurrency(num: number): string {
		return new Intl.NumberFormat('pt-BR', {
			style: 'currency',
			currency: 'USD',
			maximumFractionDigits: 0
		}).format(num);
	}

	function formatDate(str: string): string {
		if (!str) return '';
		const parts = str.split('-');
		if (parts.length === 3) {
			return `${parts[2]}/${parts[1]}`;
		}
		return str;
	}
</script>

<div class="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-6 backdrop-blur-xl">
	<!-- Header & Metric Selector -->
	<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
		<div>
			<div class="flex items-center gap-2">
				<div class="h-2.5 w-2.5 rounded-full bg-indigo-500 animate-pulse"></div>
				<h3 class="text-base font-semibold text-white">Evolução de Receita e Reservas</h3>
			</div>
			<p class="mt-1 text-xs text-zinc-400">Desempenho diário consolidado de todas as companhias aéreas</p>
		</div>

		<div class="flex items-center gap-2 rounded-xl border border-zinc-800 bg-zinc-950/60 p-1">
			<button
				onclick={() => (activeMetric = 'revenue')}
				class="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-all {activeMetric ===
				'revenue'
					? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
					: 'text-zinc-400 hover:text-white'}"
			>
				<DollarSign class="h-3.5 w-3.5" />
				<span>Receita Bruta</span>
			</button>
			<button
				onclick={() => (activeMetric = 'bookings')}
				class="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-all {activeMetric ===
				'bookings'
					? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
					: 'text-zinc-400 hover:text-white'}"
			>
				<Ticket class="h-3.5 w-3.5" />
				<span>Volume de Reservas</span>
			</button>
		</div>
	</div>

	<!-- SVG Chart Area -->
	<div class="relative mt-6 w-full">
		<svg viewBox="0 0 {width} {height}" class="w-full h-auto overflow-visible select-none" role="img" aria-label="Gráfico de tendência de receitas e reservas de voos">
			<defs>
				<linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
					<stop offset="0%" stop-color="#6366f1" stop-opacity="0.35" />
					<stop offset="100%" stop-color="#6366f1" stop-opacity="0.0" />
				</linearGradient>
			</defs>

			<!-- Horizontal Grid Lines -->
			{#each [0, 0.25, 0.5, 0.75, 1] as tick}
				{@const y = padding.top + chartHeight * (1 - tick)}
				{@const labelVal = minValue + (maxValue - minValue) * tick}
				<line
					x1={padding.left}
					y1={y}
					x2={width - padding.right}
					y2={y}
					stroke="#27272a"
					stroke-width="1"
					stroke-dasharray="4,4"
				/>
				<text
					x={padding.left - 10}
					y={y + 4}
					fill="#71717a"
					font-size="10"
					text-anchor="end"
				>
					{activeMetric === 'revenue' ? `$${(labelVal / 1000).toFixed(0)}k` : labelVal.toFixed(0)}
				</text>
			{/each}

			<!-- Area & Line -->
			<path d={areaPath} fill="url(#chartGradient)" />
			<path
				d={linePath}
				fill="none"
				stroke="#6366f1"
				stroke-width="3"
				stroke-linecap="round"
				stroke-linejoin="round"
			/>

			<!-- Data Points and Interactive Zones -->
			{#each points as p, i}
				<!-- Vertical Guideline when hovered -->
				{#if hoveredIndex === i}
					<line
						x1={p.x}
						y1={padding.top}
						x2={p.x}
						y2={padding.top + chartHeight}
						stroke="#818cf8"
						stroke-width="1"
						stroke-dasharray="2,2"
					/>
				{/if}

				<!-- Data circle -->
				<circle
					cx={p.x}
					cy={p.y}
					r={hoveredIndex === i ? 6 : 4}
					class="transition-all duration-150 {hoveredIndex === i
						? 'fill-indigo-400 stroke-white stroke-2'
						: 'fill-indigo-500 stroke-zinc-950 stroke-2'}"
				/>

				<!-- X-Axis Labels -->
				<text
					x={p.x}
					y={height - 15}
					fill={hoveredIndex === i ? '#ffffff' : '#71717a'}
					font-size="10"
					text-anchor="middle"
					class="transition-colors"
				>
					{formatDate(p.data.date)}
				</text>

				<!-- Focusable Hit Area for Hover -->
				<rect
					x={p.x - chartWidth / (data.length * 2)}
					y={padding.top}
					width={chartWidth / data.length}
					height={chartHeight}
					fill="transparent"
					tabindex="0"
					role="button"
					aria-label={`Ponto em ${p.data.date}`}
					class="cursor-pointer focus:outline-none"
					onmouseenter={() => (hoveredIndex = i)}
					onmouseleave={() => (hoveredIndex = null)}
					onfocus={() => (hoveredIndex = i)}
					onblur={() => (hoveredIndex = null)}
				/>
			{/each}
		</svg>

		<!-- Tooltip Display -->
		{#if hoveredIndex !== null && points[hoveredIndex]}
			{@const p = points[hoveredIndex]}
			<div
				class="pointer-events-none absolute -top-4 rounded-xl border border-indigo-500/30 bg-zinc-950/90 p-3 text-xs shadow-2xl backdrop-blur-md transition-all duration-150"
				style="left: calc({(p.x / width) * 100}% - 80px); width: 160px;"
			>
				<div class="flex items-center gap-1.5 font-semibold text-indigo-300">
					<Calendar class="h-3.5 w-3.5" />
					<span>{formatDate(p.data.date)}</span>
				</div>
				<div class="mt-2 flex justify-between text-zinc-300">
					<span>Receita:</span>
					<span class="font-bold text-white">{formatCurrency(p.data.revenue)}</span>
				</div>
				<div class="mt-1 flex justify-between text-zinc-300">
					<span>Reservas:</span>
					<span class="font-bold text-emerald-400">{p.data.bookings} assentos</span>
				</div>
				<div class="mt-1 flex justify-between text-zinc-300">
					<span>Voos:</span>
					<span class="font-bold text-sky-400">{p.data.flights} operados</span>
				</div>
			</div>
		{/if}
	</div>
</div>
