"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import { DataTable } from "@/components/DataTable";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

// Table columns configuration
const employeeColumns = [
  { accessorKey: "employee_id", header: "Employee ID" },
  { accessorKey: "name", header: "Name" },
  { accessorKey: "email", header: "Email" },
  { accessorKey: "hsa_eligible", header: "HSA Eligible" },
  { accessorKey: "fsa_eligible", header: "FSA Eligible" },
  { accessorKey: "cobra_status", header: "COBRA Status" },
];

const claimsColumns = [
  { accessorKey: "claim_id", header: "Claim ID" },
  { accessorKey: "employee_id", header: "Employee ID" },
  { accessorKey: "date", header: "Date" },
  { accessorKey: "amount", header: "Amount" },
  { accessorKey: "type", header: "Type" },
  { accessorKey: "status", header: "Status" },
];

const lifeEventsColumns = [
  { accessorKey: "event_id", header: "Event ID" },
  { accessorKey: "employee_id", header: "Employee ID" },
  { accessorKey: "event_type", header: "Event Type" },
  { accessorKey: "event_date", header: "Event Date" },
  { accessorKey: "verification_status", header: "Status" },
];

const cobraEventsColumns = [
  { accessorKey: "employee_id", header: "Employee ID" },
  { accessorKey: "event_type", header: "Event Type" },
  { accessorKey: "event_date", header: "Event Date" },
  { accessorKey: "cobra_start_date", header: "Start Date" },
  { accessorKey: "cobra_end_date", header: "End Date" },
];

export default function DataManagement() {
  const [activeTab, setActiveTab] = useState("employees");

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold">Data Management</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add New
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="employees">Employees</TabsTrigger>
          <TabsTrigger value="claims">Claims</TabsTrigger>
          <TabsTrigger value="life-events">Life Events</TabsTrigger>
          <TabsTrigger value="cobra">COBRA Events</TabsTrigger>
        </TabsList>

        <Card className="mt-4">
          <TabsContent value="employees" className="m-0">
            <DataTable
              columns={employeeColumns}
              data={[]}
              searchKey="name"
            />
          </TabsContent>

          <TabsContent value="claims" className="m-0">
            <DataTable
              columns={claimsColumns}
              data={[]}
              searchKey="claim_id"
            />
          </TabsContent>

          <TabsContent value="life-events" className="m-0">
            <DataTable
              columns={lifeEventsColumns}
              data={[]}
              searchKey="event_id"
            />
          </TabsContent>

          <TabsContent value="cobra" className="m-0">
            <DataTable
              columns={cobraEventsColumns}
              data={[]}
              searchKey="employee_id"
            />
          </TabsContent>
        </Card>
      </Tabs>
    </div>
  );
} 