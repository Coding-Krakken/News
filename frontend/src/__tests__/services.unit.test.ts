// Mock the apiClient module so services call the mocked methods
jest.mock('../services/apiClient', () => {
  return {
    apiClient: {
      setAccessToken: jest.fn(),
      setRefreshToken: jest.fn(),
      clearTokens: jest.fn(),
      get: jest.fn(),
      post: jest.fn(),
      put: jest.fn(),
      patch: jest.fn(),
      delete: jest.fn(),
    },
  };
});

import { authService } from '../services/authService';
import { bookmarkService } from '../services/bookmarkService';
import { filterService } from '../services/filterService';
import { userService } from '../services/userService';
import { apiClient } from '../services/apiClient';

describe('service modules (unit, mocked apiClient)', () => {
  beforeEach(() => jest.clearAllMocks());

  it('authService.login and signup set tokens', async () => {
    (apiClient.post as jest.Mock).mockResolvedValue({ data: { accessToken: 'a', refreshToken: 'r', user: { id: 1 } } });

    const login = await authService.login({ email: 'x', password: 'p' } as any);
    expect(apiClient.post).toHaveBeenCalled();
    expect(apiClient.setAccessToken).toHaveBeenCalledWith('a');
    expect(apiClient.setRefreshToken).toHaveBeenCalledWith('r');
    expect(login.accessToken).toBe('a');

    // signup flow
    (apiClient.post as jest.Mock).mockResolvedValue({ data: { accessToken: 'sa', refreshToken: 'sr', user: { id: 2 } } });
    const signup = await authService.signup({ email: 'y', password: 'q' } as any);
    expect(apiClient.post).toHaveBeenCalled();
    expect(apiClient.setAccessToken).toHaveBeenCalledWith('sa');
    expect(apiClient.setRefreshToken).toHaveBeenCalledWith('sr');
    expect(signup.accessToken).toBe('sa');
  });

  it('bookmarkService.create/list/delete calls apiClient', async () => {
    const mockBookmark = { id: 1, user_id: 1, target_type: 'story', target_id: 's1', created_at: 't' };
    (apiClient.post as jest.Mock).mockResolvedValue({ data: { bookmark: mockBookmark } });
    const created = await bookmarkService.create('story', 's1');
    expect(created).toEqual(mockBookmark);

    (apiClient.get as jest.Mock).mockResolvedValue({ data: { bookmarks: [mockBookmark] } });
    const list = await bookmarkService.list();
    expect(list).toEqual([mockBookmark]);

    (apiClient.delete as jest.Mock).mockResolvedValue({});
    await bookmarkService.delete(1);
    expect(apiClient.delete).toHaveBeenCalledWith('/bookmarks/1');
  });

  it('filterService create/list/update/delete', async () => {
    const mockFilter = { id: 1, user_id: 1, name: 'f', filter_query: {}, created_at: '', updated_at: '' };
    (apiClient.post as jest.Mock).mockResolvedValue({ data: { filter: mockFilter } });
    const created = await filterService.create('f', {});
    expect(created).toEqual(mockFilter);

    (apiClient.get as jest.Mock).mockResolvedValue({ data: { filters: [mockFilter] } });
    const list = await filterService.list();
    expect(list).toEqual([mockFilter]);

    (apiClient.put as jest.Mock).mockResolvedValue({ data: { filter: mockFilter } });
    const updated = await filterService.update(1, { name: 'x' });
    expect(updated).toEqual(mockFilter);

    (apiClient.delete as jest.Mock).mockResolvedValue({});
    await filterService.delete(1);
    expect(apiClient.delete).toHaveBeenCalledWith('/saved-filters/1');
  });

  it('userService updateProfile/getPreferences/updatePreferences', async () => {
    const mockUser = { id: 1, email: 'a', display_name: null, avatar_url: null, created_at: '', updated_at: '' };
    (apiClient.patch as jest.Mock).mockResolvedValue({ data: { user: mockUser } });
    const updated = await userService.updateProfile({ display_name: 'x' } as any);
    expect(updated).toEqual(mockUser);

    const mockPrefs = { id: 1, user_id: 1, custom_feed_config: {}, default_filters: {}, timezone: 'UTC', created_at: '', updated_at: '' };
    (apiClient.get as jest.Mock).mockResolvedValue({ data: { preferences: mockPrefs } });
    const got = await userService.getPreferences();
    expect(got).toEqual(mockPrefs);

    (apiClient.put as jest.Mock).mockResolvedValue({ data: { preferences: mockPrefs } });
    const upd = await userService.updatePreferences({ timezone: 'UTC' } as any);
    expect(upd).toEqual(mockPrefs);
  });
});
