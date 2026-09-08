import { json, type RequestHandler } from '@sveltejs/kit';
import { askAviationCopilot } from '$lib/server/ai/copilot';

export const POST: RequestHandler = async ({ request }) => {
	try {
		const { question } = await request.json();
		if (!question || typeof question !== 'string') {
			return json({ error: 'Question string is required' }, { status: 400 });
		}

		const result = await askAviationCopilot(question);
		return json(result);
	} catch (error) {
		console.error('API copilot error:', error);
		return json({ error: 'Failed to process AI copilot query' }, { status: 500 });
	}
};
