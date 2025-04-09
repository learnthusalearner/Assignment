export type User = {
  id: string;
  email: string;
};

export type Product = {
  id: string;
  name: string;
  description: string;
  category: string;
  price: number;
  rating: number;
  createdAt: string;
  updatedAt: string;
};

export type LoginCredentials = {
  email: string;
  password: string;
};

export type SignupCredentials = {
  email: string;
  password: string;
  confirmPassword: string;
};

export type ProductFormData = {
  name: string;
  description: string;
  category: string;
  price: number;
  rating: number;
};

export type FilterOptions = {
  category: string | null;
  minPrice: number | null;
  maxPrice: number | null;
  minRating: number | null;
  search: string;
};
