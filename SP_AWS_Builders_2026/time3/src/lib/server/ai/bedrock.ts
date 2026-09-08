import {
	BedrockRuntimeClient,
	InvokeModelCommand
} from '@aws-sdk/client-bedrock-runtime';
import { env } from '$env/dynamic/private';

let client: BedrockRuntimeClient | null = null;

function getBedrockClient(): BedrockRuntimeClient | null {
	if (client) return client;

	const region = env.AWS_REGION || 'us-east-1';
	const accessKeyId = env.AWS_ACCESS_KEY_ID;
	const secretAccessKey = env.AWS_SECRET_ACCESS_KEY;

	if (!accessKeyId || !secretAccessKey) {
		return null;
	}

	client = new BedrockRuntimeClient({
		region,
		credentials: {
			accessKeyId,
			secretAccessKey,
			sessionToken: env.AWS_SESSION_TOKEN
		}
	});

	return client;
}

export const DEFAULT_MODEL_ID =
	env.BEDROCK_MODEL_ID || 'anthropic.claude-3-5-haiku-20241022-v1:0';

export interface BedrockResponse {
	text: string;
	modelId: string;
	isFallback?: boolean;
}

/**
 * Invoke Amazon Bedrock model with Claude Messages API format
 */
export async function invokeBedrock(
	prompt: string,
	systemPrompt?: string,
	modelId: string = DEFAULT_MODEL_ID
): Promise<BedrockResponse> {
	const bedrock = getBedrockClient();

	if (!bedrock) {
		console.warn('AWS credentials not configured in .env, using local AI fallback response.');
		return {
			text: getLocalFallbackResponse(prompt),
			modelId: 'local-fallback',
			isFallback: true
		};
	}

	try {
		const payload = {
			anthropic_version: 'bedrock-2023-05-31',
			max_tokens: 1500,
			temperature: 0.2,
			system: systemPrompt || 'You are an expert aviation intelligence AI copilot.',
			messages: [
				{
					role: 'user',
					content: [{ type: 'text', text: prompt }]
				}
			]
		};

		const command = new InvokeModelCommand({
			modelId,
			contentType: 'application/json',
			accept: 'application/json',
			body: JSON.stringify(payload)
		});

		const response = await bedrock.send(command);
		const responseBody = JSON.parse(new TextDecoder().decode(response.body));

		const text =
			responseBody.content?.[0]?.text ||
			responseBody.completion ||
			JSON.stringify(responseBody);

		return {
			text,
			modelId,
			isFallback: false
		};
	} catch (error) {
		console.error('Bedrock invocation failed, falling back to local heuristic response:', error);
		return {
			text: getLocalFallbackResponse(prompt),
			modelId: 'local-fallback-error',
			isFallback: true
		};
	}
}

/**
 * Invoke Bedrock and parse JSON response
 */
export async function invokeBedrockJson<T>(
	prompt: string,
	systemPrompt?: string,
	modelId: string = DEFAULT_MODEL_ID
): Promise<{ data: T; isFallback?: boolean }> {
	const res = await invokeBedrock(
		`${prompt}\n\nIMPORTANT: Respond ONLY with valid JSON inside \`\`\`json ... \`\`\` code block without any conversational filler.`,
		systemPrompt,
		modelId
	);

	try {
		const jsonMatch = res.text.match(/```(?:json)?\s*([\s\S]*?)\s*```/) || [null, res.text];
		const parsed = JSON.parse(jsonMatch[1].trim()) as T;
		return { data: parsed, isFallback: res.isFallback };
	} catch (err) {
		console.warn('Could not parse JSON from Bedrock response, returning default structure:', err);
		throw new Error('Invalid JSON received from AI model');
	}
}

function getLocalFallbackResponse(prompt: string): string {
	const p = prompt.toLowerCase();
	if (p.includes('weather') || p.includes('clima') || p.includes('tempestade') || p.includes('rain')) {
		return 'Analysis indicates moderate thunderstorm risk at GRU (São Paulo) with 35kt wind gusts. Recommended action: allocate 45 minutes extra fuel buffer and monitor runway visibility.';
	}
	if (p.includes('passenger') || p.includes('passageiro') || p.includes('loyalty') || p.includes('rebook')) {
		return 'Recommended re-booking offer: Complementary upgrade to Premium Economy on flight LA-8014 departing 2 hours later, plus 5,000 bonus frequent flyer points.';
	}
	return 'Analysis completed: Flight operations are operating within normal parameters with an average load factor of 83.4%. Highest yielding route is GRU → SCL ($1.74M revenue).';
}
