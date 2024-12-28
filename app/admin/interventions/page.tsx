"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/DataTable";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, XCircle } from "lucide-react";

const interventionColumns = [
  { accessorKey: "task_id", header: "Task ID" },
  { accessorKey: "employee_id", header: "Employee ID" },
  { accessorKey: "type", header: "Type" },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }: { row: any }) => {
      const status = row.getValue("status") as string;
      return (
        <Badge
          variant={
            status === "Pending"
              ? "default"
              : status === "Approved"
              ? "success"
              : "destructive"
          }
        >
          {status}
        </Badge>
      );
    },
  },
  {
    accessorKey: "created_at",
    header: "Created At",
    cell: ({ row }: { row: any }) => {
      const date = new Date(row.getValue("created_at"));
      return date.toLocaleString();
    },
  },
  {
    accessorKey: "actions",
    header: "Actions",
    cell: ({ row }: { row: any }) => {
      const status = row.getValue("status") as string;
      if (status !== "Pending") return null;
      
      return (
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="text-green-500">
            <CheckCircle className="h-4 w-4 mr-1" />
            Approve
          </Button>
          <Button variant="outline" size="sm" className="text-red-500">
            <XCircle className="h-4 w-4 mr-1" />
            Deny
          </Button>
        </div>
      );
    },
  },
];

export default function Interventions() {
  const [interventions] = useState([
    {
      task_id: "T1001",
      employee_id: "12345",
      type: "Document Verification",
      status: "Pending",
      created_at: "2024-01-01T10:00:00",
    },
    {
      task_id: "T1002",
      employee_id: "67890",
      type: "COBRA Election",
      status: "Approved",
      created_at: "2024-01-02T11:30:00",
    },
    {
      task_id: "T1003",
      employee_id: "13579",
      type: "HSA Eligibility",
      status: "Denied",
      created_at: "2024-01-03T09:15:00",
    },
  ]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold">Intervention Tasks</h1>
        <div className="flex gap-2">
          <Badge variant="outline" className="text-orange-500">
            {interventions.filter((i) => i.status === "Pending").length} Pending
          </Badge>
          <Badge variant="outline" className="text-green-500">
            {interventions.filter((i) => i.status === "Approved").length} Approved
          </Badge>
          <Badge variant="outline" className="text-red-500">
            {interventions.filter((i) => i.status === "Denied").length} Denied
          </Badge>
        </div>
      </div>

      <Card>
        <DataTable
          columns={interventionColumns}
          data={interventions}
          searchKey="task_id"
        />
      </Card>
    </div>
  );
} 