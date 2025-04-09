
import React from "react";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Product } from "@/types";
import { Edit, Trash2 } from "lucide-react";

interface ProductGridProps {
  products: Product[];
  onEdit: (product: Product) => void;
  onDelete: (productId: string) => void;
}

const ProductGrid: React.FC<ProductGridProps> = ({ products, onEdit, onDelete }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {products.length === 0 ? (
        <div className="col-span-full text-center py-8 text-muted-foreground">
          No products found
        </div>
      ) : (
        products.map((product) => (
          <Card key={product.id} className="product-card-grid">
            <CardHeader>
              <CardTitle className="line-clamp-1">{product.name}</CardTitle>
              <div className="text-sm text-muted-foreground">{product.category}</div>
            </CardHeader>
            <CardContent>
              <div className="flex justify-between items-center mb-2">
                <div className="text-xl font-bold">${product.price.toFixed(2)}</div>
                <div className="flex items-center">
                  <div className="flex text-yellow-500">
                    {[...Array(5)].map((_, i) => (
                      <span key={i} className={i < Math.floor(product.rating) ? "text-yellow-500" : "text-gray-300"}>
                        ★
                      </span>
                    ))}
                  </div>
                  <span className="ml-1 text-sm text-muted-foreground">{product.rating}</span>
                </div>
              </div>
              <p className="text-muted-foreground line-clamp-2">{product.description}</p>
            </CardContent>
            <CardFooter className="flex justify-end space-x-2 pt-2">
              <Button size="sm" variant="outline" onClick={() => onEdit(product)}>
                <Edit className="h-4 w-4 mr-1" /> Edit
              </Button>
              <Button size="sm" variant="outline" className="text-destructive" onClick={() => onDelete(product.id)}>
                <Trash2 className="h-4 w-4 mr-1" /> Delete
              </Button>
            </CardFooter>
          </Card>
        ))
      )}
    </div>
  );
};

export default ProductGrid;
