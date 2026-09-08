<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { page } from '$app/state';
	import {
		Plane,
		Database,
		BarChart3,
		CloudLightning,
		Crown,
		Activity,
		Sparkles
	} from 'lucide-svelte';
	import AICopilotDrawer from '$lib/components/ai/AICopilotDrawer.svelte';

	let { children } = $props();

	const currentPath = $derived(page.url.pathname);
</script>

<svelte:head>
	<title>TiDB LATAM Hackathon - Inteligência de Aviação e Reservas</title>
	<meta
		name="description"
		content="Painel de operações aéreas, gestão de receita e análise de reservas alimentado por TiDB, SvelteKit e Amazon Bedrock"
	/>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="min-h-screen bg-zinc-950 font-sans text-zinc-100 antialiased selection:bg-indigo-500 selection:text-white">
	<!-- Ambient Background Glows -->
	<div class="pointer-events-none fixed inset-0 overflow-hidden">
		<div class="absolute -left-40 -top-40 h-96 w-96 rounded-full bg-indigo-600/10 blur-[128px]"></div>
		<div class="absolute -right-40 top-1/4 h-96 w-96 rounded-full bg-purple-600/10 blur-[128px]"></div>
		<div class="absolute bottom-10 left-1/3 h-96 w-96 rounded-full bg-sky-600/10 blur-[128px]"></div>
	</div>

	<!-- Top Navigation Bar -->
	<header class="sticky top-0 z-40 border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-xl">
		<div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-3.5 sm:px-6 lg:px-8">
			<!-- Brand Logo -->
			<a href="/" class="flex items-center gap-3 transition-opacity hover:opacity-90">
				<div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-sky-400 shadow-lg shadow-indigo-500/20">
					<Plane class="h-5 w-5 text-white" />
				</div>
				<div>
					<div class="flex items-center gap-2">
						<span class="text-base font-bold tracking-tight text-white">AeroInsights</span>
						<span class="rounded-md border border-indigo-500/30 bg-indigo-500/10 px-1.5 py-0.5 text-[10px] font-semibold text-indigo-300">
							TiDB + Bedrock
						</span>
					</div>
					<p class="text-[11px] text-zinc-400">Plataforma de Inteligência em Aviação</p>
				</div>
			</a>

			<!-- Center Nav Links -->
			<nav class="hidden md:flex items-center gap-1 rounded-2xl border border-zinc-800/80 bg-zinc-900/60 p-1 backdrop-blur-md">
				<a
					href="/"
					class="flex items-center gap-2 rounded-xl px-3.5 py-1.5 text-xs font-semibold transition-all {currentPath === '/'
						? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
						: 'text-zinc-400 hover:text-white'}"
				>
					<BarChart3 class="h-3.5 w-3.5" />
					<span>Painel Principal</span>
				</a>
				<a
					href="/weather-risk"
					class="flex items-center gap-2 rounded-xl px-3.5 py-1.5 text-xs font-semibold transition-all {currentPath === '/weather-risk'
						? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
						: 'text-zinc-400 hover:text-white'}"
				>
					<CloudLightning class="h-3.5 w-3.5" />
					<span>Risco Meteorológico</span>
				</a>
				<a
					href="/passenger-loyalty"
					class="flex items-center gap-2 rounded-xl px-3.5 py-1.5 text-xs font-semibold transition-all {currentPath === '/passenger-loyalty'
						? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
						: 'text-zinc-400 hover:text-white'}"
				>
					<Crown class="h-3.5 w-3.5" />
					<span>Fidelidade e Reacomodação</span>
				</a>
			</nav>

			<!-- Status Badges -->
			<div class="flex items-center gap-3">
				<div class="hidden items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900/60 px-3 py-1 text-xs text-zinc-300 sm:flex">
					<Database class="h-3.5 w-3.5 text-emerald-400" />
					<span class="text-zinc-400">Banco:</span>
					<span class="font-mono text-emerald-300">TiDB Cloud</span>
				</div>

				<div class="flex items-center gap-1.5 rounded-full border border-purple-500/30 bg-purple-500/10 px-2.5 py-1 text-xs font-medium text-purple-300">
					<Sparkles class="h-3 w-3 text-purple-400" />
					<span>Claude 3.5</span>
				</div>
			</div>
		</div>
	</header>

	<!-- Main Content Container -->
	<main class="relative mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
		{@render children()}
	</main>

	<!-- Global Floating AI Copilot Drawer -->
	<AICopilotDrawer />

	<!-- Footer -->
	<footer class="mt-16 border-t border-zinc-900 bg-zinc-950 py-8 text-center text-xs text-zinc-600">
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
			<p>Desenvolvido para o TiDB LATAM Hackathon 2026 • Alimentado por SvelteKit 5, Amazon Bedrock e TiDB</p>
		</div>
	</footer>
</div>
