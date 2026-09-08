/**
 * In-Memory LRU/TTL Cache for Database Queries
 */

interface CacheEntry<T> {
	data: T;
	expiresAt: number;
	createdAt: number;
}

class MemoryCache {
	private store = new Map<string, CacheEntry<unknown>>();
	private hits = 0;
	private misses = 0;
	private defaultTTL = 60 * 1000; // 60 seconds default TTL

	/**
	 * Retrieve a cached value if not expired
	 */
	get<T>(key: string): T | undefined {
		const entry = this.store.get(key) as CacheEntry<T> | undefined;
		if (!entry) {
			this.misses++;
			return undefined;
		}

		if (Date.now() > entry.expiresAt) {
			this.store.delete(key);
			this.misses++;
			return undefined;
		}

		this.hits++;
		return entry.data;
	}

	/**
	 * Store a value in cache with a TTL (in milliseconds)
	 */
	set<T>(key: string, data: T, ttlMs = this.defaultTTL): void {
		// Prune cache if it grows too large
		if (this.store.size > 500) {
			this.pruneExpired();
		}

		this.store.set(key, {
			data,
			expiresAt: Date.now() + ttlMs,
			createdAt: Date.now()
		});
	}

	/**
	 * Wrap an asynchronous data fetching function with caching
	 */
	async wrap<T>(key: string, ttlMs: number, fetchFn: () => Promise<T>): Promise<T> {
		const cached = this.get<T>(key);
		if (cached !== undefined) {
			return cached;
		}

		const freshData = await fetchFn();
		this.set<T>(key, freshData, ttlMs);
		return freshData;
	}

	/**
	 * Invalidate a specific key or keys matching a prefix
	 */
	invalidate(prefixOrKey?: string): void {
		if (!prefixOrKey) {
			this.store.clear();
			return;
		}

		for (const key of this.store.keys()) {
			if (key === prefixOrKey || key.startsWith(prefixOrKey)) {
				this.store.delete(key);
			}
		}
	}

	/**
	 * Prune expired entries
	 */
	private pruneExpired(): void {
		const now = Date.now();
		for (const [key, entry] of this.store.entries()) {
			if (now > entry.expiresAt) {
				this.store.delete(key);
			}
		}
	}

	/**
	 * Cache statistics
	 */
	getStats() {
		return {
			size: this.store.size,
			hits: this.hits,
			misses: this.misses,
			hitRatio: this.hits + this.misses > 0 ? (this.hits / (this.hits + this.misses)).toFixed(2) : '0'
		};
	}
}

export const memoryCache = new MemoryCache();
