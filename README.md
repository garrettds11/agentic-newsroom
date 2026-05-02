# agentic-newsroom
📰 Agentic Newsroom: Journalist-Editor Loop
A hybrid, local-first multi-agent system designed for autonomous research, multi-stage fact-checking, and cloud-native archiving. This project uses a Journalist-Editor loop to ensure high-fidelity content generation while mitigating hallucinations.
🏗️ Architecture Overview
The system utilizes a Hybrid IaC (Infrastructure as Code) approach:
• Orchestration (Local): n8n running in Docker handles the agentic logic and tool hand-offs.
• Intelligence: Dual-agent personas powered by PyGPT and OpenAI/Gemini models.
• Senses: Live web access via Tavily AI or Google Search Grounding.
• Persistence (Cloud): Finalized stories are archived to AWS DynamoDB, provisioned via Terraform.
🚀 Key Features
• Collaborative Agentic Loop: Separates research from validation to maximize factual accuracy.
• Zero-Persistence Local Engine: Run the "brains" locally for privacy and cost control.
• Serverless Persistence: Cloud-scale storage using DynamoDB with a minimal cost footprint.
• Infrastructure as Code: Fully automated environment setup via Terraform and Docker Compose.
🛠️ Prerequisites
Before starting, ensure you have the following installed and configured:
• Docker Desktop
• Terraform
• AWS CLI (authenticated with appropriate IAM permissions)
• API Keys: OpenAI/Gemini, Tavily AI
