import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("inspection_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const endpoints = {
  login: "/auth/login",
  logout: "/auth/logout",

  establishments: "/etablissements",
  inspections: "/inspections",
  uploadInspectionImage: (inspectionId) => `/inspections/${inspectionId}/images`,
  serveImage: (imageId) => `/images/${imageId}`,
  analyzeImage: (imageId) => `/images/${imageId}/analyze`,
  ragDocuments: "/rag/documents",
  ragUploadDocument: "/rag/documents/upload",
  ragAsk: "/rag/questions",
  ragAskStream: "/rag/questions/stream",
  analyzeAllImages: (inspectionId) => `/inspections/${inspectionId}/analyze-all`,
  reports: "/rapports",
  reportDetail: (reportId) => `/rapports/${reportId}`,
  reportPdf: (reportId) => `/rapports/${reportId}/pdf`,
  users: "/users",
};

export default api;
