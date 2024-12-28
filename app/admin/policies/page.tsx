"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/DataTable";
import { Plus } from "lucide-react";

const policyColumns = [
  { accessorKey: "policy_id", header: "Policy ID" },
  { accessorKey: "policy_name", header: "Name" },
  {
    accessorKey: "policy_text",
    header: "Content",
    cell: ({ row }: { row: any }) => {
      const text = row.getValue("policy_text") as string;
      return (
        <div className="max-w-[500px] truncate" title={text}>
          {text}
        </div>
      );
    },
  },
  {
    accessorKey: "actions",
    header: "Actions",
    cell: () => {
      return (
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            Edit
          </Button>
          <Button variant="outline" size="sm" className="text-red-500">
            Delete
          </Button>
        </div>
      );
    },
  },
];

export default function PolicyDocuments() {
  const [policies] = useState([
    {
      policy_id: "P1001",
      policy_name: "HSA Eligibility Policy",
      policy_text: "To be eligible for an HSA, an employee must: 1. Be covered under a High Deductible Health Plan (HDHP)...",
    },
    {
      policy_id: "P1002",
      policy_name: "FSA Eligibility Policy",
      policy_text: "FSA (Flexible Spending Account) allows employees to set aside pre-tax dollars for eligible medical expenses...",
    },
    {
      policy_id: "P1003",
      policy_name: "COBRA Eligibility Policy",
      policy_text: "COBRA allows terminated employees to keep their current health insurance...",
    },
  ]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold">Policy Documents</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add Policy
        </Button>
      </div>

      <Card>
        <DataTable
          columns={policyColumns}
          data={policies}
          searchKey="policy_name"
        />
      </Card>
    </div>
  );
} 