import React from "react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Product, ProductFormData } from "@/types";

interface ProductFormProps {
  product?: Product;
  categories: string[];
  onSubmit: (data: ProductFormData) => void;
  onCancel: () => void;
  isLoading: boolean;
}

const ProductForm: React.FC<ProductFormProps> = ({
  product,
  categories,
  onSubmit,
  onCancel,
  isLoading
}) => {
  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm<ProductFormData>({
    defaultValues: product
      ? {
          name: product.name,
          description: product.description,
          category: product.category,
          price: product.price,
          rating: product.rating
        }
      : {
          name: "",
          description: "",
          category: "",
          price: 0,
          rating: 3
        }
  });

  const watchRating = watch("rating", product?.rating || 3);

  const handleCategoryChange = (value: string) => {
    setValue("category", value);
  };

  const handleRatingChange = (value: number[]) => {
    setValue("rating", value[0]);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{product ? "Edit Product" : "Create Product"}</CardTitle>
      </CardHeader>
      <form onSubmit={handleSubmit(onSubmit)}>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              {...register("name", { required: "Name is required" })}
            />
            {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              {...register("description", { required: "Description is required" })}
              rows={3}
            />
            {errors.description && <p className="text-sm text-destructive">{errors.description.message}</p>}
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="category">Category</Label>
            <Select
              onValueChange={handleCategoryChange}
              defaultValue={product?.category}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select a category" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  {categories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>
            <input type="hidden" {...register("category", { required: "Category is required" })} />
            {errors.category && <p className="text-sm text-destructive">{errors.category.message}</p>}
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="price">Price ($)</Label>
            <Input
              id="price"
              type="number"
              step="0.01"
              {...register("price", { 
                required: "Price is required",
                valueAsNumber: true,
                min: { value: 0, message: "Price must be positive" }
              })}
            />
            {errors.price && <p className="text-sm text-destructive">{errors.price.message}</p>}
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between">
              <Label htmlFor="rating">Rating</Label>
              <span>{watchRating}</span>
            </div>
            <Slider
              id="rating"
              min={0}
              max={5}
              step={0.1}
              defaultValue={[product?.rating || 3]}
              onValueChange={handleRatingChange}
            />
            <input type="hidden" {...register("rating", { valueAsNumber: true })} />
          </div>
        </CardContent>
        
        <CardFooter className="flex justify-between">
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? "Saving..." : (product ? "Update Product" : "Create Product")}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
};

export default ProductForm;
