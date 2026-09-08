<script lang="ts">
	import { TrendingUp, TrendingDown } from 'lucide-svelte';

	interface Props {
		title: string;
		value: string | number;
		subtext?: string;
		change?: number;
		icon?: any;
		color?: 'indigo' | 'emerald' | 'amber' | 'sky' | 'violet' | 'rose';
	}

	let {
		title,
		value,
		subtext = '',
		change,
		icon: Icon,
		color = 'indigo'
	}: Props = $props();

	const colorStyles = {
		indigo: 'from-indigo-500/10 to-indigo-500/5 text-indigo-400 border-indigo-500/20 group-hover:border-indigo-500/40',
		emerald: 'from-emerald-500/10 to-emerald-500/5 text-emerald-400 border-emerald-500/20 group-hover:border-emerald-500/40',
		amber: 'from-amber-500/10 to-amber-500/5 text-amber-400 border-amber-500/20 group-hover:border-amber-500/40',
		sky: 'from-sky-500/10 to-sky-500/5 text-sky-400 border-sky-500/20 group-hover:border-sky-500/40',
		violet: 'from-violet-500/10 to-violet-500/5 text-violet-400 border-violet-500/20 group-hover:border-violet-500/40',
		rose: 'from-rose-500/10 to-rose-500/5 text-rose-400 border-rose-500/20 group-hover:border-rose-500/40'
	};

	const iconBgStyles = {
		indigo: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
		emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
		amber: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
		sky: 'bg-sky-500/10 text-sky-400 border-sky-500/30',
		violet: 'bg-violet-500/10 text-violet-400 border-violet-500/30',
		rose: 'bg-rose-500/10 text-rose-400 border-rose-500/30'
	};
</script>

<div
	class="group relative overflow-hidden rounded-2xl border bg-gradient-to-br p-6 transition-all duration-300 hover:shadow-xl hover:shadow-black/40 {colorStyles[color]}"
>
	<!-- Top Row: Title and Icon -->
	<div class="flex items-center justify-between">
		<span class="text-xs font-semibold uppercase tracking-wider text-zinc-400">{title}</span>
		{#if Icon}
			<div class="flex h-10 w-10 items-center justify-center rounded-xl border p-2 {iconBgStyles[color]}">
				<Icon class="h-5 w-5" />
			</div>
		{/if}
	</div>

	<!-- Main Value -->
	<div class="mt-4 flex items-baseline gap-2">
		<span class="text-3xl font-extrabold tracking-tight text-white">{value}</span>
	</div>

	<!-- Bottom Row: Subtext & Trend -->
	<div class="mt-3 flex items-center justify-between text-xs text-zinc-400">
		<span>{subtext}</span>

		{#if change !== undefined}
			<div
				class="flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium {change >= 0
					? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
					: 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}"
			>
				{#if change >= 0}
					<TrendingUp class="h-3 w-3" />
					<span>+{change}%</span>
				{:else}
					<TrendingDown class="h-3 w-3" />
					<span>{change}%</span>
				{/if}
			</div>
		{/if}
	</div>
</div>
