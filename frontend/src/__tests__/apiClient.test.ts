import { apiClient as realApiClient } from '../services/apiClient';

describe('apiClient (integration small)', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  it('sets, gets and clears tokens in localStorage', () => {
    realApiClient.setAccessToken('a1');
    realApiClient.setRefreshToken('r1');
    expect(localStorage.getItem('accessToken')).toBe('a1');
    expect(localStorage.getItem('refreshToken')).toBe('r1');

    realApiClient.clearTokens();
    expect(localStorage.getItem('accessToken')).toBeNull();
    expect(localStorage.getItem('refreshToken')).toBeNull();
  });

  it('forwards GET to underlying client', async () => {
    // Spy on the internal client.get
    // @ts-ignore
    const client = (realApiClient as any).client;
    expect(client).toBeDefined();
    client.get = jest.fn().mockResolvedValue({ data: { ok: true } });

    const res = await realApiClient.get('/ping');
    expect(client.get).toHaveBeenCalledWith('/ping', undefined);
    expect(res).toEqual({ data: { ok: true } });
  });
});
