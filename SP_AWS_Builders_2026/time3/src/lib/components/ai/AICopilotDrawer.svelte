<script lang="ts">
	import {
		Bot,
		Send,
		Sparkles,
		X,
		Database,
		ChevronRight,
		Loader2,
		MessageSquare,
		Terminal,
		CheckCircle2
	} from 'lucide-svelte';

	interface Message {
		role: 'user' | 'assistant';
		content: string;
		query?: string;
		data?: unknown[];
		isFallback?: boolean;
		timestamp: string;
	}

	let isOpen = $state(false);
	let inputQuery = $state('');
	let loading = $state(false);
	let messages = $state<Message[]>([
		{
			role: 'assistant',
			content:
				'Olá! Sou seu copiloto de inteligência de aviação com Amazon Bedrock e TiDB. Como posso ajudar com análise de rotas, receitas ou ocupação de voos?',
			timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
		}
	]);

	const samplePrompts = [
		'Quais rotas geraram maior receita total?',
		'Quais voos têm ocupação abaixo de 80%?',
		'Compare o faturamento da LATAM vs Avianca',
		'Mostre a distribuição de passageiros por país'
	];

	async function handleSend(queryToSend?: string) {
		const q = (queryToSend || inputQuery).trim();
		if (!q || loading) return;

		inputQuery = '';
		const timeStr = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

		messages.push({
			role: 'user',
			content: q,
			timestamp: timeStr
		});

		loading = true;

		try {
			const res = await fetch('/api/ai/copilot', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ question: q })
			});

			if (res.ok) {
				const json = await res.json();
				messages.push({
					role: 'assistant',
					content: json.answer || 'Nenhuma resposta gerada.',
					query: json.query,
					data: json.data,
					isFallback: json.isFallback,
					timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
				});
			} else {
				messages.push({
					role: 'assistant',
					content: 'Desculpe, ocorreu um erro ao consultar o Bedrock AI. Tente novamente.',
					timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
				});
			}
		} catch (err) {
			console.error('Erro de conexão com Copiloto IA:', err);
			messages.push({
				role: 'assistant',
				content: 'Erro de conexão com o servidor de IA.',
				timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
			});
		} finally {
			loading = false;
		}
	}
</script>

<!-- Floating Toggle Button -->
<div class="fixed bottom-6 right-6 z-40">
	{#if !isOpen}
		<button
			onclick={() => (isOpen = true)}
			class="group flex items-center gap-2.5 rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 px-4 py-3 text-sm font-bold text-white shadow-2xl shadow-indigo-500/40 transition-all duration-300 hover:scale-105 hover:shadow-indigo-500/60"
		>
			<Sparkles class="h-5 w-5 animate-pulse text-amber-300" />
			<span>Copiloto Bedrock</span>
			<span class="rounded-full bg-white/20 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider">IA</span>
		</button>
	{/if}
</div>

<!-- AI Copilot Drawer -->
{#if isOpen}
	<div
		class="fixed bottom-6 right-6 z-50 flex h-[620px] w-[92vw] max-w-[480px] flex-col overflow-hidden rounded-3xl border border-indigo-500/30 bg-zinc-950/95 shadow-2xl shadow-indigo-950/80 backdrop-blur-2xl transition-all duration-300"
	>
		<!-- Header -->
		<div class="flex items-center justify-between border-b border-zinc-800/80 bg-zinc-900/60 px-5 py-4">
			<div class="flex items-center gap-3">
				<div class="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-500 shadow-md shadow-indigo-500/30">
					<Bot class="h-5 w-5 text-white" />
				</div>
				<div>
					<div class="flex items-center gap-2">
						<span class="text-sm font-bold text-white">Copiloto AeroInsights</span>
						<span class="rounded bg-indigo-500/20 px-1.5 py-0.5 text-[10px] font-semibold text-indigo-300">
							Bedrock Claude
						</span>
					</div>
					<p class="text-[11px] text-zinc-400">Consultas em Linguagem Natural no TiDB</p>
				</div>
			</div>

			<button
				onclick={() => (isOpen = false)}
				class="rounded-lg p-1.5 text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-white"
			>
				<X class="h-5 w-5" />
			</button>
		</div>

		<!-- Chat Body -->
		<div class="flex-1 space-y-4 overflow-y-auto p-4 text-xs">
			{#each messages as msg}
				<div class="flex flex-col {msg.role === 'user' ? 'items-end' : 'items-start'}">
					<div
						class="max-w-[88%] rounded-2xl p-3.5 leading-relaxed shadow-md {msg.role === 'user'
							? 'bg-indigo-600 text-white rounded-br-sm'
							: 'bg-zinc-900/90 text-zinc-200 border border-zinc-800 rounded-bl-sm'}"
					>
						<div class="whitespace-pre-wrap">{msg.content}</div>

						<!-- SQL Query Box if available -->
						{#if msg.query}
							<div class="mt-3 rounded-xl border border-zinc-800 bg-zinc-950 p-2.5 font-mono text-[11px] text-emerald-400">
								<div class="mb-1 flex items-center gap-1 text-[10px] text-zinc-400 font-sans font-semibold uppercase">
									<Terminal class="h-3 w-3 text-indigo-400" />
									<span>Consulta TiDB SQL Gerada:</span>
								</div>
								<pre class="overflow-x-auto whitespace-pre-wrap">{msg.query}</pre>
							</div>
						{/if}
					</div>
					<span class="mt-1 px-1 text-[10px] text-zinc-500">{msg.timestamp}</span>
				</div>
			{/each}

			{#if loading}
				<div class="flex items-center gap-2 rounded-2xl border border-zinc-800 bg-zinc-900/60 p-3.5 text-zinc-400">
					<Loader2 class="h-4 w-4 animate-spin text-indigo-400" />
					<span>Bedrock está analisando os dados do TiDB...</span>
				</div>
			{/if}
		</div>

		<!-- Quick Suggestion Chips -->
		<div class="border-t border-zinc-800/60 bg-zinc-950/60 px-4 py-2">
			<div class="flex gap-1.5 overflow-x-auto pb-1">
				{#each samplePrompts as sample}
					<button
						onclick={() => handleSend(sample)}
						class="shrink-0 rounded-full border border-zinc-800 bg-zinc-900/80 px-2.5 py-1 text-[11px] text-zinc-300 transition-colors hover:border-indigo-500 hover:text-white"
					>
						{sample}
					</button>
				{/each}
			</div>
		</div>

		<!-- Input Footer -->
		<div class="border-t border-zinc-800/80 bg-zinc-900/40 p-3">
			<form
				onsubmit={(e) => {
					e.preventDefault();
					handleSend();
				}}
				class="flex items-center gap-2"
			>
				<input
					type="text"
					placeholder="Pergunte sobre voos, receitas ou ocupação..."
					bind:value={inputQuery}
					class="w-full rounded-xl border border-zinc-800 bg-zinc-950/90 py-2.5 pl-3.5 pr-3 text-xs text-white placeholder-zinc-500 transition-all focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
				/>
				<button
					type="submit"
					disabled={loading || !inputQuery.trim()}
					class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-md shadow-indigo-600/30 transition-all hover:bg-indigo-500 disabled:opacity-40"
				>
					<Send class="h-4 w-4" />
				</button>
			</form>
		</div>
	</div>
{/if}
