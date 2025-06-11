import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Request interceptor za dodavanje tokena
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  console.log("Token koji šaljemo: ", token);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    console.log("Authorization Header:", config.headers.Authorization);  // Ovdje se loguje header
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// Response interceptor za rukovanje greškama
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      // Server je odgovorio sa statusom koji nije u 2xx opsegu
      switch (error.response.status) {
        case 401:
          // Unauthorized - možda je token istekao
          localStorage.removeItem('token');
          window.location.href = '/login';
          break;
        case 403:
          // Forbidden - korisnik nema prava
          console.error('Nemate dozvolu za ovu akciju');
          break;
        case 404:
          // Not found
          console.error('Resurs nije pronađen');
          break;
        default:
          console.error('Došlo je do greške:', error.response.data);
      }
    } else if (error.request) {
      // Zahtev je poslat ali nije bilo odgovora
      console.error('Nema odgovora sa servera');
    } else {
      // Došlo je do greške prilikom postavljanja zahteva
      console.error('Greška prilikom slanja zahteva:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;