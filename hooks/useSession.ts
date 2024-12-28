"use client";

import { useState, useEffect } from "react";
import { chatService } from "@/lib/services/chatService";

interface Employee {
  employee_id: string;
  name: string;
  email: string;
  hsa_eligible: boolean;
  fsa_eligible: boolean;
  cobra_status: string;
}

interface SessionState {
  isAuthenticated: boolean;
  employee: Employee | null;
}

const STORAGE_KEY = "hsa_fsa_cobra_session";

export const useSession = () => {
  const [session, setSession] = useState<SessionState>({
    isAuthenticated: false,
    employee: null,
  });

  useEffect(() => {
    // Load session from localStorage on mount
    try {
      const storedSession = localStorage.getItem(STORAGE_KEY);
      if (storedSession) {
        const parsedSession = JSON.parse(storedSession);
        if (parsedSession?.employee?.employee_id) {
          setSession(parsedSession);
        }
      }
    } catch (error) {
      console.error("Error loading session:", error);
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const login = async (employeeId: string): Promise<boolean> => {
    try {
      console.log("Attempting login with employee ID:", employeeId);
      const employee = await chatService.validateEmployee(employeeId);
      console.log("Validation response:", employee);
      
      if (!employee) {
        console.log("Employee not found");
        return false;
      }

      const newSession = {
        isAuthenticated: true,
        employee,
      };

      // Save to localStorage
      localStorage.setItem(STORAGE_KEY, JSON.stringify(newSession));
      setSession(newSession);
      console.log("Login successful");
      return true;
    } catch (error) {
      console.error("Login failed:", error);
      return false;
    }
  };

  const logout = () => {
    try {
      localStorage.removeItem(STORAGE_KEY);
      setSession({
        isAuthenticated: false,
        employee: null,
      });
    } catch (error) {
      console.error("Error during logout:", error);
    }
  };

  return {
    isAuthenticated: session.isAuthenticated,
    employee: session.employee,
    login,
    logout,
  };
}; 