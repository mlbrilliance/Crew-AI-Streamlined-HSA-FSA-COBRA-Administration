import { supabase } from '../supabase';

export type ChatMessage = {
  id: string;
  text: string;
  sender: "user" | "assistant";
  timestamp: Date;
  details?: {
    source?: string;
    analysis_type?: string;
    processing_flow?: string;
    recommendations?: string[];
    action_items?: string[];
  };
  suggestions?: string[];
};

export interface ChatHistory {
  employee_id: string;
  messages: ChatMessage[];
  timestamp: Date;
}

export interface Employee {
  employee_id: string;
  name: string;
  dob: string;
  email: string;
  hsa_eligible: boolean;
  fsa_eligible: boolean;
  cobra_status: string;
  created_at?: string;
  updated_at?: string;
}

export const chatService = {
  async saveHistory(history: ChatHistory) {
    try {
      const { error } = await supabase
        .from('mock_chat_history')
        .upsert({
          employee_id: history.employee_id,
          chat_history: JSON.stringify(history.messages),
          timestamp: history.timestamp.toISOString()
        }, {
          onConflict: 'employee_id'
        });

      if (error) {
        console.error('Error saving chat history:', error);
        return false;
      }
      return true;
    } catch (error) {
      console.error('Error saving chat history:', error);
      return false;
    }
  },

  async getHistory(employeeId: string) {
    try {
      const { data, error } = await supabase
        .from('mock_chat_history')
        .select('chat_history')
        .eq('employee_id', employeeId)
        .maybeSingle();

      if (error) {
        console.error('Error fetching chat history:', error);
        return [];
      }
      
      if (!data) return [];
      
      try {
        return JSON.parse(data.chat_history) as ChatMessage[];
      } catch (parseError) {
        console.error('Error parsing chat history:', parseError);
        return [];
      }
    } catch (error) {
      console.error('Error fetching chat history:', error);
      return [];
    }
  },

  async validateEmployee(employeeId: string): Promise<Employee | null> {
    try {
      console.log('Validating employee:', employeeId);

      // Get the employee with all fields
      const { data, error } = await supabase
        .from('mock_employees')
        .select('*')
        .eq('employee_id', employeeId)
        .maybeSingle();

      if (error) {
        console.error('Error fetching employee:', error);
        return null;
      }

      if (!data) {
        console.log('No employee found with ID:', employeeId);
        return null;
      }

      console.log('Employee found:', data);
      return data as Employee;
    } catch (error: any) {
      console.error('Error validating employee:', error);
      return null;
    }
  }
}; 