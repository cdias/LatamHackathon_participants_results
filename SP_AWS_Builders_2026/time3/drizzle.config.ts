import { defineConfig } from 'drizzle-kit';

if (!process.env.DATABASE_URL) throw new Error('DATABASE_URL is not set');

export default defineConfig({
	schema: './src/lib/server/db/schema.ts',
	out: './src/lib/server/db',
	dialect: 'mysql',
	dbCredentials: {
		url: process.env.DATABASE_URL,
		ssl: {
			rejectUnauthorized: true
		}
	},
	verbose: true,
	strict: true
});
