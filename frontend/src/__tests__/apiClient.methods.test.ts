import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('ApiClient methods and token helpers', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.resetAllMocks();
  });

  it('get/post/put/patch/delete delegate to underlying client', async () => {
    const clientMock = {
      interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } },
      get: jest.fn().mockResolvedValue({ data: 'g' }),
      post: jest.fn().mockResolvedValue({ data: 'p' }),
      put: jest.fn().mockResolvedValue({ data: 'u' }),
      patch: jest.fn().mockResolvedValue({ data: 'pa' }),
      delete: jest.fn().mockResolvedValue({ data: 'd' }),
    } as unknown as import('axios').AxiosInstance;

    mockedAxios.create = jest.fn(() => clientMock as unknown as import('axios').AxiosInstance);

    let apiClient: any;
    jest.isolateModules(() => {
      apiClient = require('../services/apiClient').apiClient;
    });

    await expect(apiClient.get('/g')).resolves.toEqual({ data: 'g' });
    await expect(apiClient.post('/p', { foo: 1 })).resolves.toEqual({ data: 'p' });
    await expect(apiClient.put('/u', { foo: 2 })).resolves.toEqual({ data: 'u' });
    await expect(apiClient.patch('/pa', { foo: 3 })).resolves.toEqual({ data: 'pa' });
    await expect(apiClient.delete('/d')).resolves.toEqual({ data: 'd' });

    expect(clientMock.get).toHaveBeenCalledWith('/g', undefined);
    expect(clientMock.post).toHaveBeenCalledWith('/p', { foo: 1 }, undefined);
  });

  it('setAccessToken, setRefreshToken and clearTokens operate on localStorage', () => {
    mockedAxios.create = jest.fn(() => ({ interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } } } as unknown as import('axios').AxiosInstance));
    let apiClient: any;
    jest.isolateModules(() => {
      apiClient = require('../services/apiClient').apiClient;
    });

    apiClient.setAccessToken('a1');
    apiClient.setRefreshToken('r1');
    expect(localStorage.getItem('accessToken')).toBe('a1');
    expect(localStorage.getItem('refreshToken')).toBe('r1');

    apiClient.clearTokens();
    expect(localStorage.getItem('accessToken')).toBeNull();
    expect(localStorage.getItem('refreshToken')).toBeNull();
  });

  it('concurrent refreshToken calls reuse the same promise', async () => {
    mockedAxios.create = jest.fn(() => ({ interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } } } as unknown as import('axios').AxiosInstance));
    mockedAxios.post.mockImplementation(() => new Promise((res) => setTimeout(() => res({ data: { accessToken: 'acc', refreshToken: 'ref' } }), 10)));

    let apiClient: any;
    jest.isolateModules(() => {
      apiClient = require('../services/apiClient').apiClient;
    });

    localStorage.setItem('refreshToken', 'old');

    const p1 = (apiClient as any).refreshToken();
    const p2 = (apiClient as any).refreshToken();

    const [r1, r2] = await Promise.all([p1, p2]);
    expect(r1).toBe('acc');
    expect(r2).toBe('acc');
    expect(mockedAxios.post).toHaveBeenCalledTimes(1);
  });
});
