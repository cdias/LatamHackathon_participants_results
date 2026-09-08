import { describe, it, expect, beforeEach } from 'vitest';
import { memoryCache } from './cache';

describe('MemoryCache', () => {
	beforeEach(() => {
		memoryCache.invalidate();
	});

	it('should set and get values within TTL', () => {
		memoryCache.set('test-key', { value: 42 }, 1000);
		const cached = memoryCache.get<{ value: number }>('test-key');
		expect(cached).toEqual({ value: 42 });
	});

	it('should return undefined for non-existent keys', () => {
		const cached = memoryCache.get('non-existent');
		expect(cached).toBeUndefined();
	});

	it('should wrap async functions and avoid redundant calls', async () => {
		let callCount = 0;
		const fetchMock = async () => {
			callCount++;
			return { revenue: 1000 };
		};

		const res1 = await memoryCache.wrap('analytics:kpi', 5000, fetchMock);
		const res2 = await memoryCache.wrap('analytics:kpi', 5000, fetchMock);

		expect(res1).toEqual({ revenue: 1000 });
		expect(res2).toEqual({ revenue: 1000 });
		expect(callCount).toBe(1); // Second call should hit the cache
	});

	it('should invalidate keys matching prefix', () => {
		memoryCache.set('analytics:kpi:1', 'data1');
		memoryCache.set('analytics:kpi:2', 'data2');
		memoryCache.set('other:data', 'data3');

		memoryCache.invalidate('analytics:kpi');

		expect(memoryCache.get('analytics:kpi:1')).toBeUndefined();
		expect(memoryCache.get('analytics:kpi:2')).toBeUndefined();
		expect(memoryCache.get('other:data')).toBe('data3');
	});
});
