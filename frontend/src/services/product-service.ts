import { Product, ProductFormData } from "@/types";

const mockProducts: Product[] = [
  {
    id: "1",
    name: "Apple MacBook Pro",
    description: "High-performance laptop for professionals",
    category: "Electronics",
    price: 1999,
    rating: 4.5,
    createdAt: "2023-01-15T08:00:00Z",
    updatedAt: "2023-01-15T08:00:00Z"
  },
  {
    id: "2",
    name: "Sony Wireless Headphones",
    description: "Noise-cancelling over-ear headphones",
    category: "Audio",
    price: 349,
    rating: 4.8,
    createdAt: "2023-02-10T10:30:00Z",
    updatedAt: "2023-02-10T10:30:00Z"
  },
  {
    id: "3",
    name: "Samsung 4K Smart TV",
    description: "65-inch QLED display with smart features",
    category: "Electronics",
    price: 1299,
    rating: 4.3,
    createdAt: "2023-03-05T14:15:00Z",
    updatedAt: "2023-03-05T14:15:00Z"
  },
  {
    id: "4",
    name: "Ergonomic Office Chair",
    description: "Adjustable chair with lumbar support",
    category: "Furniture",
    price: 299,
    rating: 4.0,
    createdAt: "2023-03-20T09:45:00Z",
    updatedAt: "2023-03-20T09:45:00Z"
  },
  {
    id: "5",
    name: "Canon DSLR Camera",
    description: "Professional camera with 24MP sensor",
    category: "Photography",
    price: 899,
    rating: 4.7,
    createdAt: "2023-04-12T11:20:00Z",
    updatedAt: "2023-04-12T11:20:00Z"
  },
  {
    id: "6",
    name: "Fitness Tracker Watch",
    description: "Waterproof smartwatch with health tracking",
    category: "Wearables",
    price: 149,
    rating: 3.9,
    createdAt: "2023-05-05T16:10:00Z",
    updatedAt: "2023-05-05T16:10:00Z"
  },
  {
    id: "7",
    name: "Professional Knife Set",
    description: "8-piece chef's knife collection",
    category: "Kitchen",
    price: 179,
    rating: 4.2,
    createdAt: "2023-06-18T13:25:00Z",
    updatedAt: "2023-06-18T13:25:00Z"
  },
  {
    id: "8",
    name: "Wireless Gaming Mouse",
    description: "High-precision mouse with programmable buttons",
    category: "Gaming",
    price: 89,
    rating: 4.6,
    createdAt: "2023-07-22T15:40:00Z",
    updatedAt: "2023-07-22T15:40:00Z"
  }
];

export const getProducts = async (): Promise<Product[]> => {
  return new Promise((resolve) => {
    setTimeout(() => resolve(mockProducts), 500);
  });
};

export const getProductById = async (id: string): Promise<Product | undefined> => {
  return new Promise((resolve) => {
    setTimeout(() => resolve(mockProducts.find(p => p.id === id)), 300);
  });
};

export const createProduct = async (productData: ProductFormData): Promise<Product> => {
  const newProduct: Product = {
    id: `${Math.floor(Math.random() * 10000)}`,
    ...productData,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  
  return new Promise((resolve) => {
    setTimeout(() => {
      mockProducts.push(newProduct);
      resolve(newProduct);
    }, 400);
  });
};

export const updateProduct = async (id: string, productData: ProductFormData): Promise<Product> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = mockProducts.findIndex(p => p.id === id);
      if (index !== -1) {
        const updatedProduct: Product = {
          ...mockProducts[index],
          ...productData,
          updatedAt: new Date().toISOString()
        };
        mockProducts[index] = updatedProduct;
        resolve(updatedProduct);
      } else {
        reject(new Error('Product not found'));
      }
    }, 400);
  });
};

export const deleteProduct = async (id: string): Promise<boolean> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = mockProducts.findIndex(p => p.id === id);
      if (index !== -1) {
        mockProducts.splice(index, 1);
        resolve(true);
      } else {
        reject(new Error('Product not found'));
      }
    }, 400);
  });
};

export const getCategories = async (): Promise<string[]> => {
  return new Promise((resolve) => {
    const categories = Array.from(new Set(mockProducts.map(p => p.category)));
    setTimeout(() => resolve(categories), 300);
  });
};
