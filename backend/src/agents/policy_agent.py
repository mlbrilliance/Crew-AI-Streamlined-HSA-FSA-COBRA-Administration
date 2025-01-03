"""
Policy Agent Module

Responsible for managing and retrieving policy information related to benefits.
"""

from typing import List, Dict, Any
from datetime import datetime

class PolicyAgent:
    """Agent responsible for managing and retrieving policy information."""
    
    def __init__(self):
        """Initialize the PolicyAgent."""
        self.policies = {
            "HSA Benefits": [
                "HSA funds never expire and remain with the employee even after leaving the company",
                "2024 HSA contribution limits: $4,150 for individual coverage, $8,300 for family coverage",
                "Additional $1,000 catch-up contribution allowed for age 55+",
                "Must be enrolled in a qualifying high-deductible health plan (HDHP)",
                "Triple tax advantage: tax-deductible contributions, tax-free growth, tax-free withdrawals for qualified expenses"
            ],
            "FSA Benefits": [
                "FSA funds must be used within the plan year with limited exceptions",
                "2024 FSA contribution limit: $3,200",
                "Use-it-or-lose-it rule applies with possible grace period or $610 rollover",
                "No HDHP requirement, but cannot be combined with HSA unless limited to dental/vision",
                "Immediate access to full annual election amount"
            ],
            "COBRA Benefits": [
                "COBRA continuation coverage available for up to 18 months after qualifying event",
                "Must be offered to qualified beneficiaries who lose coverage due to qualifying events",
                "Premium cannot exceed 102% of the full cost of coverage",
                "60-day election period from loss of coverage or notification, whichever is later",
                "Coverage is retroactive if elected, but premiums must be paid retroactively"
            ],
            "FSA Reimbursement Process": [
                "Submit claims with receipts showing date, service, provider, and amount",
                "Claims must be for expenses incurred during the plan year",
                "Many FSA cards provide automatic payment at qualified merchants",
                "Keep all receipts for tax purposes and verification if requested"
            ],
            "HSA Contribution Limits": [
                "2024 individual coverage limit: $4,150",
                "2024 family coverage limit: $8,300",
                "Age 55+ catch-up contribution: additional $1,000 allowed",
                "Employer contributions count toward annual limits",
                "Pro-rated limits apply if starting mid-year"
            ],
            "FSA Contribution Changes": [
                "Elections generally locked for plan year unless qualifying life event occurs",
                "Qualifying events include: marriage, divorce, birth/adoption, employment change",
                "Changes must be consistent with the qualifying event",
                "30-day window to request changes after qualifying event"
            ],
            "General Benefits": [
                "Benefits elections typically made during annual open enrollment",
                "Mid-year changes allowed only with qualifying life events",
                "Review benefits guide for detailed coverage information",
                "Contact HR for specific questions about your benefits package"
            ]
        }
    
    def get_relevant_policies(self, query_type: str) -> List[str]:
        """
        Retrieve relevant policies based on the query type.
        
        Args:
            query_type: The type of query to get policies for.
            
        Returns:
            List[str]: List of relevant policy statements.
        """
        # Get policies and ensure they are strings
        policies = self.policies.get(query_type, self.policies["General Benefits"])
        return [str(p) for p in policies] 