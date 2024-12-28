"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Users,
  FileText,
  AlertCircle,
  MessageSquare,
} from "lucide-react";
import { supabase } from "@/lib/supabase";

interface DashboardStats {
  activeChatSessions: number;
  totalEmployees: number;
  totalPolicies: number;
  pendingInterventions: number;
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    activeChatSessions: 0,
    totalEmployees: 5,
    totalPolicies: 5,
    pendingInterventions: 0,
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        console.log('Fetching chat sessions...');
        // Fetch active chat sessions
        const { data: chatSessions, error: chatError } = await supabase
          .from('mock_chat_sessions')
          .select('*')
          .eq('status', 'active');

        if (chatError) {
          console.error('Error fetching chat sessions:', chatError);
          throw chatError;
        }

        console.log('Chat sessions data:', chatSessions);

        // Update stats
        setStats(prev => {
          const newStats = {
            ...prev,
            activeChatSessions: chatSessions?.length || 0
          };
          console.log('Updating stats:', newStats);
          return newStats;
        });

      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
      }
    };

    // Initial fetch
    fetchStats();

    // Set up real-time subscription for chat sessions
    console.log('Setting up real-time subscription...');
    const subscription = supabase
      .channel('mock_chat_sessions')
      .on('postgres_changes', { 
        event: '*', 
        schema: 'public', 
        table: 'mock_chat_sessions' 
      }, (payload) => {
        console.log('Received real-time update:', payload);
        fetchStats();
      })
      .subscribe((status) => {
        console.log('Subscription status:', status);
      });

    // Cleanup subscription
    return () => {
      console.log('Cleaning up subscription...');
      subscription.unsubscribe();
    };
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Employees</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalEmployees}</div>
            <p className="text-xs text-muted-foreground">
              Active in the system
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Chat Sessions</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeChatSessions}</div>
            <p className="text-xs text-muted-foreground">
              Active conversations
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Policy Documents</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalPolicies}</div>
            <p className="text-xs text-muted-foreground">
              Total documents
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Interventions</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pendingInterventions}</div>
            <p className="text-xs text-muted-foreground">
              Requiring attention
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              No recent activity to display.
            </p>
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm font-medium">CrewAI Status</p>
                  <p className="text-xs text-muted-foreground">
                    All agents operational
                  </p>
                </div>
                <div className="flex h-2 w-2">
                  <div className="animate-pulse h-2 w-2 rounded-full bg-green-500" />
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm font-medium">Supabase Connection</p>
                  <p className="text-xs text-muted-foreground">
                    Connected and synced
                  </p>
                </div>
                <div className="flex h-2 w-2">
                  <div className="animate-pulse h-2 w-2 rounded-full bg-green-500" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 