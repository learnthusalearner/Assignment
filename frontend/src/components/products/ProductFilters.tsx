
import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { FilterOptions } from "@/types";
import { Search, X } from "lucide-react";

interface ProductFiltersProps {
  categories: string[];
  initialFilters: FilterOptions;
  onFilterChange: (filters: FilterOptions) => void;
}

const ProductFilters: React.FC<ProductFiltersProps> = ({
  categories,
  initialFilters,
  onFilterChange
}) => {
  const [filters, setFilters] = useState<FilterOptions>(initialFilters);
  const [priceRange, setPriceRange] = useState<number[]>([
    filters.minPrice || 0,
    filters.maxPrice || 2000
  ]);

  // Helper to update filters and trigger parent callback
  const updateFilters = (newFilters: Partial<FilterOptions>) => {
    const updatedFilters = { ...filters, ...newFilters };
    setFilters(updatedFilters);
    onFilterChange(updatedFilters);
  };

  // Handle search input
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateFilters({ search: e.target.value });
  };

  // Handle category selection
  const handleCategoryChange = (value: string) => {
    updateFilters({ category: value === "all" ? null : value });
  };

  // Handle price range changes
  const handlePriceRangeChange = (value: number[]) => {
    setPriceRange(value);
  };

  const handlePriceRangeCommit = () => {
    updateFilters({ minPrice: priceRange[0], maxPrice: priceRange[1] });
  };

  // Handle rating filter
  const handleRatingChange = (value: number[]) => {
    updateFilters({ minRating: value[0] });
  };

  // Clear all filters
  const handleClearFilters = () => {
    const clearedFilters: FilterOptions = {
      category: null,
      minPrice: null,
      maxPrice: null,
      minRating: null,
      search: ""
    };
    setFilters(clearedFilters);
    setPriceRange([0, 2000]);
    onFilterChange(clearedFilters);
  };

  return (
    <Card>
      <CardContent className="p-4 space-y-5">
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search products..."
            value={filters.search}
            onChange={handleSearchChange}
            className="pl-8"
          />
        </div>

        <div className="space-y-2">
          <Label>Category</Label>
          <Select
            value={filters.category || "all"}
            onValueChange={handleCategoryChange}
          >
            <SelectTrigger>
              <SelectValue placeholder="All categories" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All categories</SelectItem>
              {categories.map((category) => (
                <SelectItem key={category} value={category}>
                  {category}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between">
            <Label>Price Range</Label>
            <span className="text-sm text-muted-foreground">
              ${priceRange[0]} - ${priceRange[1]}
            </span>
          </div>
          <Slider
            min={0}
            max={2000}
            step={10}
            value={priceRange}
            onValueChange={handlePriceRangeChange}
            onValueCommit={handlePriceRangeCommit}
            className="my-4"
          />
        </div>

        <div className="space-y-2">
          <div className="flex justify-between">
            <Label>Minimum Rating</Label>
            <span className="text-sm text-muted-foreground">
              {filters.minRating || 0}+
            </span>
          </div>
          <Slider
            min={0}
            max={5}
            step={0.5}
            value={[filters.minRating || 0]}
            onValueChange={handleRatingChange}
          />
        </div>

        <Button
          variant="outline"
          size="sm"
          className="w-full mt-2 flex items-center justify-center"
          onClick={handleClearFilters}
        >
          <X className="h-4 w-4 mr-2" /> Clear filters
        </Button>
      </CardContent>
    </Card>
  );
};

export default ProductFilters;
