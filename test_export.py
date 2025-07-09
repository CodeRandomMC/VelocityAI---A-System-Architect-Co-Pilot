"""
Test script for export functionality.
"""

import os
import json
from export_utils import ExportManager

def test_export_functionality():
    """Test basic export functionality with a sample architecture analysis."""
    print("Testing export functionality...")
    
    # Create sample analysis data
    sample_analysis = {
        "summaryOfReviewerObservations": "This is a sample architecture review for testing exports.",
        "planSummary": "A simple test system with frontend, backend, and database components.",
        "strengths": [
            {
                "dimension": "Scalability",
                "point": "Stateless design allows horizontal scaling",
                "reason": "Services can be replicated across multiple instances without shared state."
            },
            {
                "dimension": "Security",
                "point": "API authentication using OAuth 2.0",
                "reason": "Industry standard protocol for secure authorization."
            }
        ],
        "areasForImprovement": [
            {
                "area": "Database Design",
                "concern": "Single database instance is a potential bottleneck",
                "suggestion": "Consider database sharding or read replicas",
                "severity": "MEDIUM",
                "impact": "As user base grows, database performance will degrade",
                "tradeOffsConsidered": "Increased complexity vs. performance benefits"
            }
        ],
        "strategicRecommendations": [
            {
                "recommendation": "Consider adopting event-driven architecture",
                "rationale": "Better scalability and decoupling of services",
                "potentialImplications": "Requires learning curve and messaging infrastructure"
            }
        ],
        "nextStepsAndConsiderations": [
            "Conduct load testing to verify database capacity",
            "Document API versioning strategy",
            "Implement automated infrastructure as code"
        ]
    }
    
    # Sample markdown plan
    sample_markdown_plan = """
# Test System Architecture

## Components
- Frontend: React SPA
- Backend: Node.js API
- Database: PostgreSQL

## Communication
- REST APIs between frontend and backend
- SQL queries to database
"""
    
    # Create export manager
    export_manager = ExportManager()
    
    # Test each export format
    for format_name in ["PDF", "HTML", "Markdown"]:
        try:
            output_path = export_manager.export_analysis(
                analysis_data=sample_analysis,
                markdown_plan=sample_markdown_plan,
                model_used="test-model",
                export_format=format_name
            )
            
            if os.path.exists(output_path):
                print(f"✓ {format_name} export successful: {output_path}")
            else:
                print(f"✗ {format_name} export failed: File not created")
                
        except Exception as e:
            print(f"✗ {format_name} export error: {str(e)}")
    
    print("\nExport testing complete!")


if __name__ == "__main__":
    test_export_functionality()
