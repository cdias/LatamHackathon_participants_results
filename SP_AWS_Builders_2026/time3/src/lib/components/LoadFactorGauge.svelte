<script lang="ts">
	import { Users, AlertCircle, CheckCircle2 } from 'lucide-svelte';

	interface Props {
		loadFactor: number;
		title?: string;
		subtitle?: string;
		target?: number;
	}

	let {
		loadFactor = 0,
		title = 'Taxa Média de Ocupação',
		subtitle = 'Proporção de assentos ocupados em todos os voos programados',
		target = 80
	}: Props = $props();

	const safeLoadFactor = $derived(Math.min(100, Math.max(0, loadFactor)));
	const radius = 64;
	const circumference = 2 * Math.PI * radius;
	const strokeDashoffset = $derived(circumference - (safeLoadFactor / 100) * circumference);

	const statusColor = $derived(
		safeLoadFactor >= target
			? 'text-emerald-400 stroke-emerald-500'
			: safeLoadFactor >= 65
				? 'text-amber-400 stroke-amber-500'
				: 'text-rose-400 stroke-rose-500'
	);
</script>

<div class="flex flex-col justify-between rounded-2xl border border-zinc-800 bg-zinc-900/70 p-6 backdrop-blur-xl">
	<div>
		<div class="flex items-center justify-between">
			<span class="text-xs font-semibold uppercase tracking-wider text-zinc-400">{title}</span>
			<span class="flex items-center gap-1 rounded-full border border-zinc-800 bg-zinc-950/80 px-2 py-0.5 text-xs text-zinc-300">
				Meta: {target}%
			</span>
		</div>
		<p class="mt-1 text-xs text-zinc-500">{subtitle}</p>
	</div>

	<!-- Radial Progress Gauge -->
	<div class="my-6 flex items-center justify-center">
		<div class="relative flex items-center justify-center">
			<svg class="h-36 w-36 -rotate-90 transform overflow-visible" viewBox="0 0 160 160">
				<!-- Background Track -->
				<circle
					cx="80"
					cy="80"
					r={radius}
					class="stroke-zinc-800"
					stroke-width="12"
					fill="transparent"
				/>
				<!-- Active Fill Track -->
				<circle
					cx="80"
					cy="80"
					r={radius}
					class="transition-all duration-1000 ease-out {statusColor}"
					stroke-width="12"
					stroke-linecap="round"
					stroke-dasharray={circumference}
					stroke-dashoffset={strokeDashoffset}
					fill="transparent"
				/>
			</svg>
			<div class="absolute flex flex-col items-center">
				<span class="text-3xl font-black text-white">{safeLoadFactor}%</span>
				<span class="text-[10px] font-semibold uppercase tracking-wider text-zinc-400">Ocupação</span>
			</div>
		</div>
	</div>

	<!-- Bottom Benchmark Note -->
	<div class="rounded-xl border border-zinc-800/80 bg-zinc-950/50 p-3 text-xs">
		{#if safeLoadFactor >= target}
			<div class="flex items-center gap-2 text-emerald-400">
				<CheckCircle2 class="h-4 w-4 shrink-0" />
				<span>Superando a meta de eficiência operacional (+{(safeLoadFactor - target).toFixed(1)}%)</span>
			</div>
		{:else}
			<div class="flex items-center gap-2 text-amber-400">
				<AlertCircle class="h-4 w-4 shrink-0" />
				<span>Abaixo da meta ideal. Oportunidade para incentivos tarifários dinâmicos.</span>
			</div>
		{/if}
	</div>
</div>
