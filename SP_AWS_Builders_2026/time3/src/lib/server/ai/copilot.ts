import { invokeBedrock } from './bedrock';
import { db } from '../db';
import { sql } from 'drizzle-orm';

const SYSTEM_SCHEMA_PROMPT = `
Você é um analista especialista em dados de aviação e SQL para uma plataforma de gestão de companhias aéreas alimentada por TiDB / MySQL.
Aqui está o esquema do banco de dados:

Tabelas:
1. airline (airline_id INT PK, iata CHAR(2), airlinename VARCHAR(30), base_airport INT FK)
2. airplane (airplane_id INT PK, capacity INT, type_id INT FK, airline_id INT)
3. airplane_type (type_id INT PK, identifier VARCHAR(50), description TEXT)
4. airport (airport_id INT PK, iata CHAR(3), icao CHAR(4), name VARCHAR(50))
5. airport_geo (airport_id INT PK, name VARCHAR(50), city VARCHAR(50), country VARCHAR(50), latitude DECIMAL, longitude DECIMAL)
6. booking (booking_id INT PK, flight_id INT FK, seat CHAR(4), passenger_id INT FK, price DECIMAL(10,2))
7. flight (flight_id INT PK, flightno CHAR(8), \`from\` INT FK, \`to\` INT FK, departure DATETIME, arrival DATETIME, airline_id INT FK, airplane_id INT FK)
8. flightschedule (flightno CHAR(8), \`from\` INT FK, \`to\` INT FK, departure TIME, arrival TIME, airline_id INT FK, monday TINYINT ... sunday TINYINT)
9. passenger (passenger_id INT PK, passportno CHAR(9), firstname VARCHAR(100), lastname VARCHAR(100))
10. passengerdetails (passenger_id INT PK, birthdate DATE, sex CHAR(1), street VARCHAR(100), city VARCHAR(100), country VARCHAR(100), emailaddress VARCHAR(120))
11. weatherdata (log_date DATE, time TIME, station INT, temp DECIMAL, humidity DECIMAL, airpressure DECIMAL, wind DECIMAL, weather ENUM, winddirection INT)

INSTRUÇÕES:
1. Quando uma pergunta for feita, gere uma consulta MySQL/TiDB SELECT limpa e segura dentro de um bloco \`\`\`sql ... \`\`\`.
2. Gere APENAS instruções SELECT. Nunca crie INSERT, UPDATE, DELETE, ALTER, DROP.
3. Forneça uma explicação executiva clara dos insights em português brasileiro por padrão (a menos que outro idioma seja solicitado).
`;

export interface CopilotResult {
	answer: string;
	query?: string;
	data?: unknown[];
	isFallback?: boolean;
}

export async function askAviationCopilot(question: string): Promise<CopilotResult> {
	try {
		// 1. Ask Bedrock for SQL query & response
		const aiResponse = await invokeBedrock(
			`Pergunta do Usuário: ${question}\n\nGere a consulta SQL relevante e explique o insight de negócio em português.`,
			SYSTEM_SCHEMA_PROMPT
		);

		let executedData: unknown[] = [];
		let extractedSql: string | undefined;

		const sqlMatch = aiResponse.text.match(/```sql\s*([\s\S]*?)\s*```/i);
		if (sqlMatch && sqlMatch[1]) {
			const candidateQuery = sqlMatch[1].trim();

			// Security check: Only allow SELECT queries
			if (/^\s*SELECT/i.test(candidateQuery) && !/INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE/i.test(candidateQuery)) {
				extractedSql = candidateQuery;
				try {
					const [rows] = await db.execute(sql.raw(extractedSql));
					if (Array.isArray(rows)) {
						executedData = rows.slice(0, 10);
					}
				} catch (dbErr) {
					console.warn('Erro ao executar consulta SQL gerada por IA:', dbErr);
				}
			}
		}

		return {
			answer: aiResponse.text,
			query: extractedSql,
			data: executedData,
			isFallback: aiResponse.isFallback
		};
	} catch (error) {
		console.error('Falha no processamento do Copiloto:', error);
		return {
			answer: 'Não foi possível processar a pergunta no momento. Verifique as credenciais do Bedrock ou tente novamente.',
			isFallback: true
		};
	}
}
