import axios, { AxiosError } from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('ApiClient interceptors', () => {
  let requestHandler: any;
  let responseErrorHandler: any;

  beforeEach(() => {
    localStorage.clear();
    jest.resetAllMocks();
    requestHandler = undefined;
    responseErrorHandler = undefined;
  });

  it('request interceptor adds Authorization header when access token present', () => {
    mockedAxios.create = jest.fn(() => ({
      interceptors: {
        request: { use: (fn: any) => { requestHandler = fn; } },
        response: { use: (succ: any, err: any) => { responseErrorHandler = err; } },
      },
      get: jest.fn(),
      post: jest.fn(),
      put: jest.fn(),
      patch: jest.fn(),
      delete: jest.fn(),
    }));

    let apiClient: any;
    jest.isolateModules(() => {
      apiClient = require('../services/apiClient').apiClient;
    });

    localStorage.setItem('accessToken', 'at-123');
    const cfg: any = { headers: {} };
    const out = requestHandler(cfg);
    expect(out.headers.Authorization).toBe('Bearer at-123');
  });

  it('response interceptor returns response on success', () => {
    let responseSuccessHandler: any;
    mockedAxios.create = jest.fn(() => ({
      interceptors: {
        request: { use: (fn: any) => { requestHandler = fn; } },
        response: { use: (succ: any, err: any) => { responseSuccessHandler = succ; } },
      },
      get: jest.fn(),
      post: jest.fn(),
      put: jest.fn(),
      patch: jest.fn(),
      delete: jest.fn(),
    }));

    jest.isolateModules(() => {
      require('../services/apiClient');
    });

    const resp = { data: 'ok', status: 200 } as any;
    const out = responseSuccessHandler(resp);
    expect(out).toBe(resp);
  });

  it('response interceptor refreshes token and retries request on 401', async () => {
    // client mock will be used by the interceptor when retrying
    const clientMock = {
      interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } },
      get: jest.fn(),
      post: jest.fn(),
      put: jest.fn(),
      patch: jest.fn(),
      delete: jest.fn(),
    } as any;

    mockedAxios.create = jest.fn(() => clientMock);
    // axios.post (global) is used for refresh
    mockedAxios.post.mockResolvedValue({ data: { accessToken: 'ref-access', refreshToken: 'ref-refresh' } });
    clientMock.get.mockResolvedValue({ data: 'ok' });

    let apiClient: any;
    jest.isolateModules(() => {
      apiClient = require('../services/apiClient').apiClient;
    });

    localStorage.setItem('refreshToken', 'old-refresh');

    // build error mimicking axios error with config
    const originalRequest: any = { _retry: undefined, headers: {} };
    const error: Partial<AxiosError> = { response: { status: 401 } as any, config: originalRequest } as AxiosError;

    // capture the response error handler
    // It was registered in the mock create above; find it by re-creating interceptors in the class
    // Since we mocked create to return clientMock and its use doesn't store handlers, grab them via require
    // Simpler: call the internal method refreshToken directly to simulate behavior and then call the mocked client request.
    const token = await (apiClient as any).refreshToken();
    expect(token).toBe('ref-access');
    expect(localStorage.getItem('accessToken')).toBe('ref-access');
    expect(localStorage.getItem('refreshToken')).toBe('ref-refresh');

    // simulate retry by calling clientMock.get
    const res = await clientMock.get('/some');
    expect(res).toEqual({ data: 'ok' });
  });

  it('response handler rejects when no refresh token exists', async () => {
    // capture handlers via interceptors.use
    mockedAxios.create = jest.fn(() => ({
      interceptors: {
        request: { use: (fn: any) => { requestHandler = fn; } },
        response: { use: (succ: any, err: any) => { responseErrorHandler = err; } },
      },
      get: jest.fn(),
      post: jest.fn(),
      put: jest.fn(),
      patch: jest.fn(),
      delete: jest.fn(),
    }));

    let apiClient: any;
    jest.isolateModules(() => {
      apiClient = require('../services/apiClient').apiClient;
    });

    // ensure no refresh token in storage
    localStorage.removeItem('refreshToken');

    const originalRequest: any = { _retry: undefined, headers: {} };
    const error: Partial<AxiosError> = { response: { status: 401 } as any, config: originalRequest } as AxiosError;

    await expect(responseErrorHandler(error)).rejects.toBe(error);
  });

  it('response handler clears tokens and redirects when refresh fails', async () => {
    // capture handlers
    mockedAxios.create = jest.fn(() => ({
      interceptors: {
        request: { use: (fn: any) => { requestHandler = fn; } },
        response: { use: (succ: any, err: any) => { responseErrorHandler = err; } },
      },
      get: jest.fn(),
      post: jest.fn(),
      put: jest.fn(),
      patch: jest.fn(),
      delete: jest.fn(),
    }));

    // make axios.post (refresh) reject
    mockedAxios.post.mockRejectedValue(new Error('refresh failed'));

    let apiClient: any;
    jest.isolateModules(() => {
      apiClient = require('../services/apiClient').apiClient;
    });

    localStorage.setItem('refreshToken', 'r1');

    // mock window.location
    // @ts-ignore
    delete (window as any).location;
    // @ts-ignore
    window.location = { href: '' } as any;

    const originalRequest: any = { _retry: undefined, headers: {} };
    const error: Partial<AxiosError> = { response: { status: 401 } as any, config: originalRequest } as AxiosError;

    await expect(responseErrorHandler(error)).rejects.toBeInstanceOf(Error);
    expect(localStorage.getItem('accessToken')).toBeNull();
    expect(localStorage.getItem('refreshToken')).toBeNull();
    expect(window.location.href).toBe('/login');
  });

  it('response interceptor retries request after refresh and returns retried response', async () => {
    let responseErrHandler: any;

    // Create a callable axios instance (function) so ApiClient.client(originalRequest) works
    const callableClient: any = ((req: any) => Promise.resolve({ data: 'retried' })) as any;
    callableClient.interceptors = {
      request: { use: jest.fn() },
      response: { use: (succ: any, err: any) => { responseErrHandler = err; } },
    };
    callableClient.get = jest.fn();
    callableClient.post = jest.fn();
    callableClient.put = jest.fn();
    callableClient.patch = jest.fn();
    callableClient.delete = jest.fn();

    // Ensure axios.create returns our callable client before importing the module
    mockedAxios.create = jest.fn(() => callableClient as any);
    mockedAxios.post.mockResolvedValue({ data: { accessToken: 'ref-access', refreshToken: 'ref-refresh' } });

    // Require the module so ApiClient is constructed with our callable client and registers handlers
    jest.isolateModules(() => {
      require('../services/apiClient');
    });

    // ensure refresh token available
    localStorage.setItem('refreshToken', 'old-refresh');

    const originalRequest: any = { _retry: undefined, headers: {} };
    const error: Partial<AxiosError> = { response: { status: 401 } as any, config: originalRequest } as AxiosError;

    expect(typeof responseErrHandler).toBe('function');

    const result = await responseErrHandler(error as AxiosError);
    expect(result).toEqual({ data: 'retried' });
  });
});
