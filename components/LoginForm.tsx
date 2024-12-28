"use client";

import { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";

interface LoginFormProps {
  onLogin: (employeeId: string) => Promise<boolean>;
}

export const LoginForm = ({ onLogin }: LoginFormProps) => {
  const [employeeId, setEmployeeId] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    
    if (!employeeId.trim()) {
      setError("Employee ID is required");
      return;
    }

    try {
      setIsLoading(true);
      const success = await onLogin(employeeId);
      
      if (!success) {
        setError("Invalid employee ID. Please try again.");
      }
    } catch (err) {
      setError("Login failed. Please try again.");
      console.error("Login error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 w-full max-w-sm p-4">
      <div className="space-y-2">
        <Label htmlFor="employeeId">Employee ID</Label>
        <Input
          id="employeeId"
          type="text"
          placeholder="Enter your employee ID"
          value={employeeId}
          onChange={(e) => {
            setEmployeeId(e.target.value);
            setError("");
          }}
          disabled={isLoading}
        />
        {error && <p className="text-sm text-red-500">{error}</p>}
      </div>
      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? "Logging in..." : "Login"}
      </Button>
      <p className="text-sm text-muted-foreground text-center">
        Try these employee IDs: 12345, 67890, 13579
      </p>
    </form>
  );
}; 