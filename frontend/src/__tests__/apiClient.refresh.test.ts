import axios from "axios";

jest.mock("axios");
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe("ApiClient refreshToken", () => {
  beforeEach(() => {
    localStorage.clear();
    jest.resetAllMocks();
  });

  it("refreshes tokens and stores them", () => {
    localStorage.setItem("refreshToken", "old-refresh");
    mockedAxios.post.mockResolvedValue({
      data: { accessToken: "new-access", refreshToken: "new-refresh" },
    });

    // ensure axios.create returns an object with interceptors used by ApiClient
    mockedAxios.create = jest.fn(
      () =>
        ({
          interceptors: {
            request: { use: jest.fn() },
            response: { use: jest.fn() },
          },
          get: jest.fn(),
          post: jest.fn(),
          put: jest.fn(),
          patch: jest.fn(),
          delete: jest.fn(),
        }) as unknown as import("axios").AxiosInstance,
    );

    let apiClient: any;
    jest.isolateModules(() => {
      apiClient = require("../services/apiClient").apiClient;
    });

    return (apiClient as any).refreshToken().then((token: any) => {
      expect(token).toBe("new-access");
      expect(localStorage.getItem("accessToken")).toBe("new-access");
      expect(localStorage.getItem("refreshToken")).toBe("new-refresh");
      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining("/auth/refresh"),
        { refreshToken: "old-refresh" },
      );
    });
  });

  it("returns null when no refresh token exists", () => {
    mockedAxios.create = jest.fn(
      () =>
        ({
          interceptors: {
            request: { use: jest.fn() },
            response: { use: jest.fn() },
          },
          get: jest.fn(),
          post: jest.fn(),
          put: jest.fn(),
          patch: jest.fn(),
          delete: jest.fn(),
        }) as unknown as import("axios").AxiosInstance,
    );

    let apiClient: any;
    jest.isolateModules(() => {
      apiClient = require("../services/apiClient").apiClient;
    });

    return (apiClient as any).refreshToken().then((token: any) => {
      expect(token).toBeNull();
      expect(mockedAxios.post).not.toHaveBeenCalled();
    });
  });
});
