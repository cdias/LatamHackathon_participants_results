<script lang="ts">
	import { CalendarDays } from 'lucide-svelte';

	interface DayStat {
		day: string;
		count: number;
	}

	interface Props {
		schedule: DayStat[];
	}

	let { schedule = [] }: Props = $props();

	const maxCount = $derived(
		Math.max(...schedule.map((s) => s.count), 1)
	);
</script>

<div class="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-6 backdrop-blur-xl">
	<div class="flex items-center justify-between">
		<div class="flex items-center gap-2">
			<CalendarDays class="h-5 w-5 text-amber-400" />
			<h3 class="text-base font-semibold text-white">Densidade de Horários Semanais</h3>
		</div>
		<span class="text-xs text-zinc-400">Frequência de Operação</span>
	</div>
	<p class="mt-1 text-xs text-zinc-400">Partidas programadas distribuídas por dia da semana</p>

	<div class="mt-6 grid grid-cols-7 gap-2">
		{#each schedule as item}
			{@const intensity = item.count / maxCount}
			<div class="flex flex-col items-center gap-2">
				<div class="flex h-24 w-full flex-col items-center justify-end rounded-xl border border-zinc-800 bg-zinc-950/60 p-2">
					<div
						class="w-full rounded-lg bg-gradient-to-t from-amber-500 to-amber-300 transition-all duration-500"
						style="height: {Math.max(12, Math.round(intensity * 100))}%; opacity: {Math.max(0.4, intensity)};"
					></div>
				</div>
				<span class="text-xs font-bold text-zinc-300">{item.day}</span>
				<span class="text-[10px] text-zinc-500">{item.count} voos</span>
			</div>
		{/each}
	</div>
</div>
