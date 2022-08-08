export const TOKEN_KEY = "@f04-token";
export const USER_KEY = "@f04-user";

export const isAuthenticated = () => localStorage.getItem(TOKEN_KEY) !== null;
export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const login = (token) => {
  localStorage.setItem(TOKEN_KEY, token);
};

export const setUser = (user) => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

export const getUser = () => JSON.parse(localStorage.getItem(USER_KEY));

export const logout = () => {
  localStorage.removeItem(TOKEN_KEY);
};
