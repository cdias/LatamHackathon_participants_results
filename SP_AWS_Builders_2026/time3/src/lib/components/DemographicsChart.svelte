<script lang="ts">
	import { Users, Globe } from 'lucide-svelte';

	interface CountryStat {
		country: string;
		count: number;
	}

	interface GenderStat {
		gender: string;
		count: number;
	}

	interface Props {
		countries: CountryStat[];
		genders: GenderStat[];
	}

	let { countries = [], genders = [] }: Props = $props();

	const totalPassengerCount = $derived(
		countries.reduce((acc, c) => acc + c.count, 0)
	);

	const totalGenderCount = $derived(
		genders.reduce((acc, g) => acc + g.count, 0)
	);
</script>

<div class="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-6 backdrop-blur-xl">
	<div class="flex items-center gap-2">
		<Users class="h-5 w-5 text-violet-400" />
		<h3 class="text-base font-semibold text-white">Demografia e Geografia dos Passageiros</h3>
	</div>
	<p class="mt-1 text-xs text-zinc-400">Distribuição de país de origem e perfil dos viajantes</p>

	<div class="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
		<!-- Countries Breakdown -->
		<div>
			<h4 class="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-zinc-400">
				<Globe class="h-3.5 w-3.5 text-indigo-400" />
				<span>Principais Países de Origem</span>
			</h4>

			<div class="mt-4 space-y-3">
				{#each countries as item}
					{@const pct = totalPassengerCount > 0 ? Math.round((item.count / totalPassengerCount) * 100) : 0}
					<div>
						<div class="flex justify-between text-xs">
							<span class="font-medium text-zinc-200">{item.country}</span>
							<span class="text-zinc-400">{item.count.toLocaleString('pt-BR')} ({pct}%)</span>
						</div>
						<div class="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-zinc-800">
							<div
								class="h-full rounded-full bg-indigo-500 transition-all duration-500"
								style="width: {pct}%"
							></div>
						</div>
					</div>
				{/each}
			</div>
		</div>

		<!-- Gender Breakdown -->
		<div>
			<h4 class="text-xs font-semibold uppercase tracking-wider text-zinc-400">
				Distribuição por Gênero
			</h4>

			<div class="mt-4 space-y-3">
				{#each genders as item}
					{@const pct = totalGenderCount > 0 ? Math.round((item.count / totalGenderCount) * 100) : 0}
					<div>
						<div class="flex justify-between text-xs">
							<span class="font-medium text-zinc-200">{item.gender}</span>
							<span class="text-zinc-400">{item.count.toLocaleString('pt-BR')} ({pct}%)</span>
						</div>
						<div class="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-zinc-800">
							<div
								class="h-full rounded-full {item.gender === 'Feminino' ? 'bg-violet-400' : 'bg-sky-400'} transition-all duration-500"
								style="width: {pct}%"
							></div>
						</div>
					</div>
				{/each}
			</div>
		</div>
	</div>
</div>
