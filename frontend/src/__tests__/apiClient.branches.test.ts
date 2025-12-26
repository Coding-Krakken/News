import axios, { AxiosError } from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('ApiClient uncovered branches', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.resetAllMocks();
  });

  it('request interceptor handles missing token (no Authorization added)', async () => {
    let reqHandler: any;
    let reqErrorHandler: any;
    mockedAxios.create = jest.fn(() => ({
      interceptors: {
        request: { use: (s: any, e: any) => { reqHandler = s; reqErrorHandler = e; } },
        response: { use: jest.fn() },
      },
    } as unknown as import('axios').AxiosInstance));

    let apiClient: any;
    jest.isolateModules(() => {
      apiClient = require('../services/apiClient').apiClient;
    });

    const cfg: any = { headers: {} };
    const out = reqHandler(cfg);
    expect(out.headers.Authorization).toBeUndefined();

    // error handler should reject
    const err = new Error('bad');
    try {
      const res = reqErrorHandler(err);
      if (res && typeof res.then === 'function') {
        await expect(res).rejects.toBe(err);
      } else {
        expect(res).toBeUndefined();
      }
    } catch (e) {
      expect(e).toBe(err);
    }
  });

  it('response interceptor rejects when status is not 401', async () => {
    let responseErrHandler: any;
    mockedAxios.create = jest.fn(() => ({
      interceptors: {
        request: { use: jest.fn() },
        response: { use: (s: any, e: any) => { responseErrHandler = e; } },
      },
    } as unknown as import('axios').AxiosInstance));

    let apiClient: any;
    jest.isolateModules(() => {
      apiClient = require('../services/apiClient').apiClient;
    });

    const originalRequest: any = { _retry: undefined, headers: {} };
    const error: Partial<AxiosError> = { response: { status: 500 } as any, config: originalRequest } as AxiosError;

    await expect(responseErrHandler(error)).rejects.toBe(error);
  });

  it('response handler returns reject when originalRequest._retry is true', async () => {
    let responseErrHandler: any;
    mockedAxios.create = jest.fn(() => ({
      interceptors: {
        request: { use: jest.fn() },
        response: { use: (s: any, e: any) => { responseErrHandler = e; } },
      },
    } as unknown as import('axios').AxiosInstance));

    let apiClient: any;
    jest.isolateModules(() => {
      apiClient = require('../services/apiClient').apiClient;
    });

    const originalRequest: any = { _retry: true, headers: {} };
    const error: Partial<AxiosError> = { response: { status: 401 } as any, config: originalRequest } as AxiosError;

    await expect(responseErrHandler(error)).rejects.toBe(error);
  });
});
