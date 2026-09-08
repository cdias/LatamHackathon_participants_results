<script lang="ts">
	import type { PageData } from './$types';
	import {
		Crown,
		UserCheck,
		Gift,
		Sparkles,
		Plane,
		ArrowRight,
		RefreshCw,
		MessageSquare,
		Send,
		ShieldCheck,
		DollarSign,
		Ticket
	} from 'lucide-svelte';

	let { data }: { data: PageData } = $props();

	let customProposal = $state<typeof data.initialProposal | null>(null);
	let selectedPassengerIndex = $state(0);
	let selectedLanguage = $state<'pt' | 'es' | 'en'>('pt');
	let loading = $state(false);

	const passengers = $derived(data.passengers);
	const selectedPassenger = $derived(passengers[selectedPassengerIndex] || passengers[0]);
	const proposal = $derived(customProposal ?? data.initialProposal);

	const tierBadges = {
		PLATINUM: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
		GOLD: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
		SILVER: 'bg-slate-500/10 text-slate-300 border-slate-500/30',
		STANDARD: 'bg-zinc-800 text-zinc-400 border-zinc-700'
	};

	async function generateOffer(index: number) {
		selectedPassengerIndex = index;
		const target = passengers[index] || passengers[0];

		loading = true;
		try {
			const res = await fetch('/api/ai/passenger-loyalty', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					passengerId: target.passengerId,
					language: selectedLanguage
				})
			});

			if (res.ok) {
				const json = await res.json();
				customProposal = json.proposal;
			}
		} catch (err) {
			console.error('Falha ao gerar proposta de reacomodação:', err);
		} finally {
			loading = false;
		}
	}
</script>

<div class="space-y-8">
	<!-- Page Header -->
	<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
		<div>
			<div class="flex items-center gap-2">
				<div class="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-500 shadow-lg shadow-purple-500/20">
					<Crown class="h-5 w-5 text-white" />
				</div>
				<h1 class="text-2xl font-black tracking-tight text-white sm:text-3xl">
					Programa de Fidelidade e Assistente de Reacomodação Inteligente
				</h1>
			</div>
			<p class="mt-1 text-sm text-zinc-400">
				Recuperação autônoma de clientes VIP e reacomodação personalizada gerada via Amazon Bedrock.
			</p>
		</div>

		<!-- Language Selector -->
		<div class="flex items-center gap-2 rounded-2xl border border-zinc-800 bg-zinc-900/80 p-1 backdrop-blur-md">
			<button
				onclick={() => {
					selectedLanguage = 'pt';
					generateOffer(selectedPassengerIndex);
				}}
				class="rounded-xl px-3 py-1.5 text-xs font-semibold transition-all {selectedLanguage === 'pt'
					? 'bg-indigo-600 text-white shadow-md'
					: 'text-zinc-400 hover:text-white'}"
			>
				Português
			</button>
			<button
				onclick={() => {
					selectedLanguage = 'es';
					generateOffer(selectedPassengerIndex);
				}}
				class="rounded-xl px-3 py-1.5 text-xs font-semibold transition-all {selectedLanguage === 'es'
					? 'bg-indigo-600 text-white shadow-md'
					: 'text-zinc-400 hover:text-white'}"
			>
				Español
			</button>
			<button
				onclick={() => {
					selectedLanguage = 'en';
					generateOffer(selectedPassengerIndex);
				}}
				class="rounded-xl px-3 py-1.5 text-xs font-semibold transition-all {selectedLanguage === 'en'
					? 'bg-indigo-600 text-white shadow-md'
					: 'text-zinc-400 hover:text-white'}"
			>
				English
			</button>
		</div>
	</div>

	<div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
		<!-- Left: Passenger Selection List -->
		<div class="space-y-4">
			<div class="flex items-center justify-between">
				<span class="text-xs font-bold uppercase tracking-wider text-zinc-400">Lista de Passageiros VIP</span>
				<span class="text-xs text-zinc-500">{passengers.length} passageiros</span>
			</div>

			<div class="space-y-3">
				{#each passengers as p, i}
					<button
						onclick={() => generateOffer(i)}
						class="w-full text-left rounded-2xl border p-4 transition-all duration-200 {selectedPassengerIndex ===
						i
							? 'border-indigo-500/50 bg-indigo-500/10 shadow-lg shadow-indigo-500/10'
							: 'border-zinc-800 bg-zinc-900/60 hover:border-zinc-700'}"
					>
						<div class="flex items-start justify-between">
							<div>
								<h4 class="font-bold text-white">{p.firstname} {p.lastname}</h4>
								<span class="text-[11px] text-zinc-400">{p.city}, {p.country}</span>
							</div>
							<span class="rounded-lg border px-2 py-0.5 text-[10px] font-bold uppercase {tierBadges[p.loyaltyTier]}">
								{p.loyaltyTier}
							</span>
						</div>

						<div class="mt-3 flex items-center justify-between border-t border-zinc-800/60 pt-2 text-[11px] text-zinc-400">
							<span>{p.totalBookings} voos no histórico</span>
							<span class="font-semibold text-emerald-400">${p.totalSpent.toLocaleString('pt-BR')} investidos</span>
						</div>
					</button>
				{/each}
			</div>
		</div>

		<!-- Right: AI Generated Recovery Proposal -->
		<div class="space-y-6 lg:col-span-2">
			<!-- Selected Passenger Banner -->
			<div class="rounded-3xl border border-indigo-500/30 bg-zinc-900/70 p-6 backdrop-blur-xl">
				<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-zinc-800 pb-4">
					<div class="flex items-center gap-3">
						<div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-500/20 font-bold text-indigo-400 text-lg">
							{selectedPassenger.firstname[0]}{selectedPassenger.lastname[0]}
						</div>
						<div>
							<div class="flex items-center gap-2">
								<h3 class="text-lg font-bold text-white">
									{selectedPassenger.firstname} {selectedPassenger.lastname}
								</h3>
								<span class="rounded-lg border px-2 py-0.5 text-[10px] font-bold uppercase {tierBadges[selectedPassenger.loyaltyTier]}">
									{selectedPassenger.loyaltyTier}
								</span>
							</div>
							<p class="text-xs text-zinc-400">Passaporte: {selectedPassenger.passportno} • {selectedPassenger.emailaddress}</p>
						</div>
					</div>

					<button
						onclick={() => generateOffer(selectedPassengerIndex)}
						disabled={loading}
						class="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-bold text-white shadow-md shadow-indigo-600/30 transition-all hover:bg-indigo-500 disabled:opacity-50"
					>
						<Sparkles class="h-3.5 w-3.5 {loading ? 'animate-spin' : ''}" />
						<span>Regenerar Plano de IA</span>
					</button>
				</div>

				<!-- AI Narrative Proposal -->
				<div class="mt-6">
					<div class="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-indigo-400">
						<Sparkles class="h-4 w-4" />
						<span>Estratégia Personalizada de Recuperação (Amazon Bedrock)</span>
					</div>

					{#if loading}
						<div class="my-8 flex items-center justify-center gap-2 text-xs text-zinc-400">
							<RefreshCw class="h-4 w-4 animate-spin text-indigo-400" />
							<span>Gerando opções de reacomodação e pacote de benefícios...</span>
						</div>
					{:else}
						<div class="mt-3 prose prose-invert max-w-none text-xs leading-relaxed text-zinc-300">
							<div class="whitespace-pre-wrap">{proposal.proposalSummary}</div>
						</div>
					{/if}
				</div>
			</div>

			<!-- Alternative Itineraries Cards -->
			<div class="rounded-2xl border border-zinc-800 bg-zinc-900/60 p-6 backdrop-blur-xl">
				<div class="flex items-center gap-2">
					<Plane class="h-4 w-4 text-emerald-400" />
					<h4 class="text-sm font-bold text-white">Alternativas Imediatas de Voo com Upgrade de Assento</h4>
				</div>

				<div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
					{#each proposal.alternativeFlights as flight}
						<div class="rounded-xl border border-zinc-800 bg-zinc-950/70 p-4">
							<div class="flex items-center justify-between">
								<span class="font-bold text-white">{flight.flightno}</span>
								<span class="rounded bg-emerald-500/20 px-2 py-0.5 text-[10px] font-bold text-emerald-400">
									{flight.timeDifference}
								</span>
							</div>
							<div class="mt-2 text-xs text-zinc-300">{flight.route}</div>
							<div class="mt-3 flex items-center justify-between border-t border-zinc-800/80 pt-2 text-xs">
								<span class="text-zinc-500">Assento Atribuído:</span>
								<span class="font-semibold text-indigo-400">{flight.seatUpgrade}</span>
							</div>
						</div>
					{/each}
				</div>

				<div class="mt-4 rounded-xl border border-purple-500/20 bg-purple-500/10 p-3.5 text-xs text-purple-300">
					<span class="font-bold">Compensação Aprovada:</span> {proposal.compensationPackage}
				</div>
			</div>
		</div>
	</div>
</div>
