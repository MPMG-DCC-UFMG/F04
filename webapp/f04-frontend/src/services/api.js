import axios from "axios";
import { getToken } from "./auth";
import eventBus from "../services/eventBus";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:8082/",
});

api.interceptors.request.use(async (config) => {
  const token = getToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response.status === 401) {
      eventBus.dispatch("unauth", {});
    }
    return Promise.reject(error);
  }
);

export default api;
