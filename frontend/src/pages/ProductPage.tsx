
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import ProductTable from "@/components/products/ProductTable";
import ProductGrid from "@/components/products/ProductGrid";
import ProductFilters from "@/components/products/ProductFilters";
import ProductForm from "@/components/products/ProductForm";
import Header from "@/components/layout/Header";
import { FilterOptions, Product, ProductFormData } from "@/types";
import { Plus, Grid, List, AlertTriangle } from "lucide-react";
import {
  getProducts,
  getCategories,
  createProduct,
  updateProduct,
  deleteProduct,
} from "@/services/product-service";
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { toast } from "sonner";

const ProductPage: React.FC = () => {
  // State for products and filtering
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [filters, setFilters] = useState<FilterOptions>({
    category: null,
    minPrice: null,
    maxPrice: null,
    minRating: null,
    search: "",
  });
  
  // UI state
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");
  const [isLoading, setIsLoading] = useState(true);
  
  // Form and dialog state
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [currentProduct, setCurrentProduct] = useState<Product | undefined>(undefined);
  const [productToDelete, setProductToDelete] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const navigate = useNavigate();

  // Load products and categories
  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoading(true);
        const [productsData, categoriesData] = await Promise.all([
          getProducts(),
          getCategories()
        ]);
        setProducts(productsData);
        setFilteredProducts(productsData);
        setCategories(categoriesData);
      } catch (error) {
        console.error("Error loading data:", error);
        toast.error("Failed to load products");
      } finally {
        setIsLoading(false);
      }
    };
    
    loadData();
  }, []);

  // Apply filters whenever they change or products change
  useEffect(() => {
    let result = [...products];
    
    // Filter by category
    if (filters.category) {
      result = result.filter(product => product.category === filters.category);
    }
    
    // Filter by price range
    if (filters.minPrice !== null) {
      result = result.filter(product => product.price >= (filters.minPrice || 0));
    }
    if (filters.maxPrice !== null) {
      result = result.filter(product => product.price <= (filters.maxPrice || Infinity));
    }
    
    // Filter by minimum rating
    if (filters.minRating !== null) {
      result = result.filter(product => product.rating >= (filters.minRating || 0));
    }
    
    // Filter by search term
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      result = result.filter(
        product =>
          product.name.toLowerCase().includes(searchTerm) ||
          product.description.toLowerCase().includes(searchTerm)
      );
    }
    
    setFilteredProducts(result);
  }, [filters, products]);

  // Handle filter changes
  const handleFilterChange = (newFilters: FilterOptions) => {
    setFilters(newFilters);
  };

  // Toggle view mode
  const toggleViewMode = () => {
    setViewMode(prevMode => (prevMode === "grid" ? "table" : "grid"));
  };

  // Open product form for creation
  const handleAddProduct = () => {
    setCurrentProduct(undefined);
    setIsFormOpen(true);
  };

  // Open product form for editing
  const handleEditProduct = (product: Product) => {
    setCurrentProduct(product);
    setIsFormOpen(true);
  };

  // Handle product form submission (create or update)
  const handleProductSubmit = async (data: ProductFormData) => {
    try {
      setIsSubmitting(true);
      let updatedProduct: Product;
      
      if (currentProduct) {
        // Update existing product
        updatedProduct = await updateProduct(currentProduct.id, data);
        setProducts(prevProducts =>
          prevProducts.map(p => (p.id === currentProduct.id ? updatedProduct : p))
        );
        toast.success("Product updated successfully");
      } else {
        // Create new product
        updatedProduct = await createProduct(data);
        setProducts(prevProducts => [...prevProducts, updatedProduct]);
        toast.success("Product created successfully");
      }
      
      setIsFormOpen(false);
    } catch (error) {
      console.error("Error saving product:", error);
      toast.error(currentProduct ? "Failed to update product" : "Failed to create product");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Open delete confirmation dialog
  const handleDeleteClick = (productId: string) => {
    setProductToDelete(productId);
    setIsDeleteDialogOpen(true);
  };

  // Confirm product deletion
  const confirmDelete = async () => {
    if (!productToDelete) return;
    
    try {
      await deleteProduct(productToDelete);
      setProducts(prevProducts => prevProducts.filter(p => p.id !== productToDelete));
      toast.success("Product deleted successfully");
    } catch (error) {
      console.error("Error deleting product:", error);
      toast.error("Failed to delete product");
    } finally {
      setIsDeleteDialogOpen(false);
      setProductToDelete(null);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header />
      
      <main className="flex-1 container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row gap-6">
          {/* Sidebar filters */}
          <div className="w-full md:w-64 lg:w-80 space-y-4">
            <ProductFilters
              categories={categories}
              initialFilters={filters}
              onFilterChange={handleFilterChange}
            />
          </div>
          
          {/* Main content */}
          <div className="flex-1 space-y-4">
            {/* Actions header */}
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold">Products</h1>
              <div className="flex space-x-2">
                <Button size="sm" variant="outline" onClick={toggleViewMode}>
                  {viewMode === "grid" ? (
                    <>
                      <List className="h-4 w-4 mr-2" /> Table
                    </>
                  ) : (
                    <>
                      <Grid className="h-4 w-4 mr-2" /> Grid
                    </>
                  )}
                </Button>
                <Button size="sm" onClick={handleAddProduct}>
                  <Plus className="h-4 w-4 mr-2" /> Add Product
                </Button>
              </div>
            </div>
            
            {/* Products display */}
            {isLoading ? (
              <div className="text-center py-8">Loading products...</div>
            ) : (
              viewMode === "grid" ? (
                <ProductGrid
                  products={filteredProducts}
                  onEdit={handleEditProduct}
                  onDelete={handleDeleteClick}
                />
              ) : (
                <ProductTable
                  products={filteredProducts}
                  onEdit={handleEditProduct}
                  onDelete={handleDeleteClick}
                />
              )
            )}
          </div>
        </div>
      </main>
      
      {/* Product form dialog */}
      <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{currentProduct ? "Edit Product" : "Create Product"}</DialogTitle>
            <DialogDescription>
              {currentProduct
                ? "Make changes to the product."
                : "Add a new product to your inventory."}
            </DialogDescription>
          </DialogHeader>
          <ProductForm
            product={currentProduct}
            categories={categories}
            onSubmit={handleProductSubmit}
            onCancel={() => setIsFormOpen(false)}
            isLoading={isSubmitting}
          />
        </DialogContent>
      </Dialog>
      
      {/* Delete confirmation dialog */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the
              selected product from your inventory.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete} className="bg-destructive text-destructive-foreground">
              <AlertTriangle className="h-4 w-4 mr-2" />
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default ProductPage;
