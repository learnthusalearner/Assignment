
import { Navigate } from "react-router-dom";

const Index = () => {
  // This page will redirect to the products page
  return <Navigate to="/" replace />;
};

export default Index;
