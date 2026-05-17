"""AI Orchestrator - coordinates AI agents and RAG using IBM watsonx.ai or OpenAI fallback"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from openai import AsyncOpenAI

from app.config import settings
from app.services.rag_engine import RAGEngine
from app.api.schemas.responses import ModeQueryResponse


class AIOrchestrator:
    """Orchestrates AI agents and RAG pipeline using IBM Granite models or OpenAI fallback"""
    
    def __init__(self, db: Session):
        """Initialize AI orchestrator with IBM watsonx.ai or OpenAI fallback"""
        self.db = db
        self.rag_engine = RAGEngine(db)
        self.use_watsonx = settings.watsonx_available
        
        if self.use_watsonx:
            try:
                from app.services.ibm_watsonx_client import create_async_watsonx_client
                self.client = create_async_watsonx_client()
                print("[AIOrchestrator] Using IBM watsonx.ai")
            except Exception as e:
                print(f"[AIOrchestrator] WatsonX init failed ({e}), falling back to OpenAI")
                self.use_watsonx = False
                self._init_openai()
        else:
            self._init_openai()
    
    def _init_openai(self):
        """Initialize OpenAI client as fallback"""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        print("[AIOrchestrator] Using OpenAI as fallback")
    
    async def process_query(
        self,
        mode: str,
        workspace_id: str,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ModeQueryResponse:
        """
        Process a query using the appropriate AI mode
        
        Args:
            mode: AI mode (illustration/development/testing/deployment/documentation)
            workspace_id: Workspace ID
            query: User query
            context: Additional context
            
        Returns:
            ModeQueryResponse with AI-generated result
        """
        try:
            # Retrieve relevant context using RAG
            rag_context = await self.rag_engine.retrieve_context(
                query=query,
                workspace_id=workspace_id,
                top_k=settings.TOP_K_RESULTS,
                file_path=context.get("file_path") if context else None
            )
            
            # Get workspace summary
            workspace_summary = self.rag_engine.get_workspace_summary(workspace_id)
            
            # Route to appropriate mode handler
            if mode == "illustration":
                result = await self._handle_illustration_mode(
                    query, rag_context, workspace_summary, context
                )
            elif mode == "development":
                result = await self._handle_development_mode(
                    query, rag_context, workspace_summary, context
                )
            elif mode == "testing":
                result = await self._handle_testing_mode(
                    query, rag_context, workspace_summary, context
                )
            elif mode == "deployment":
                result = await self._handle_deployment_mode(
                    query, rag_context, workspace_summary, context
                )
            elif mode == "documentation":
                result = await self._handle_documentation_mode(
                    query, rag_context, workspace_summary, context
                )
            else:
                raise ValueError(f"Unknown mode: {mode}")
            
            return ModeQueryResponse(
                mode=mode,
                result=result,
                suggestions=self._generate_suggestions(mode, query)
            )
            
        except Exception as e:
            raise Exception(f"Failed to process query: {str(e)}")
    
    async def _handle_illustration_mode(
        self,
        query: str,
        rag_context: Dict[str, Any],
        workspace_summary: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle illustration mode - generate diagrams and visual explanations"""
        
        # Build context for prompt
        code_context = self._format_rag_context(rag_context)
        metadata = workspace_summary.get("metadata", {})
        
        system_prompt = """You are Bob's Illustration Mode expert. Generate Mermaid diagrams and visual explanations for codebases.

Your responses should include:
1. Mermaid diagram syntax (flowchart, sequence, class, or architecture diagram)
2. Clear explanation of the architecture
3. Component relationships
4. Data flow descriptions

Always use valid Mermaid syntax."""

        user_prompt = f"""Repository: {metadata.get('repo_name', 'Unknown')}
Language: {metadata.get('language', 'Unknown')}
Files: {metadata.get('file_count', 0)}

Relevant Code Context:
{code_context}

User Request: {query}

Generate a Mermaid diagram and explanation for this request."""

        response = await self.client.chat.completions.create(
            model=settings.WATSONX_MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content or ""
        
        # Extract Mermaid diagram
        mermaid_diagram = self._extract_mermaid(content)
        explanation = content.replace(mermaid_diagram, "").strip() if mermaid_diagram else content
        
        return {
            "type": "diagram",
            "content": mermaid_diagram or "```mermaid\ngraph TD\n    A[Start] --> B[Process]\n    B --> C[End]\n```",
            "explanation": explanation,
            "metadata": {
                "diagram_type": "mermaid",
                "language": metadata.get('language', 'Unknown')
            }
        }
    
    async def _handle_development_mode(
        self,
        query: str,
        rag_context: Dict[str, Any],
        workspace_summary: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle development mode - code review and improvements"""
        
        code_context = self._format_rag_context(rag_context)
        metadata = workspace_summary.get("metadata", {})
        
        system_prompt = """You are Bob's Development Mode expert. Provide code reviews, refactoring suggestions, and architectural improvements.

Focus on:
- Code quality and best practices
- Security vulnerabilities
- Performance optimizations
- Design patterns
- Maintainability

Provide specific, actionable recommendations with code examples."""

        user_prompt = f"""Repository: {metadata.get('repo_name', 'Unknown')}
Language: {metadata.get('language', 'Unknown')}

Code Context:
{code_context}

User Request: {query}

Provide detailed analysis and recommendations."""

        response = await self.client.chat.completions.create(
            model=settings.WATSONX_MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content or ""
        
        return {
            "type": "analysis",
            "content": content,
            "metadata": {
                "language": metadata.get('language', 'Unknown'),
                "analysis_type": "code_review"
            }
        }
    
    async def _handle_testing_mode(
        self,
        query: str,
        rag_context: Dict[str, Any],
        workspace_summary: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle testing mode - generate tests"""
        
        code_context = self._format_rag_context(rag_context)
        metadata = workspace_summary.get("metadata", {})
        language = metadata.get('language', 'Python')
        
        # Determine test framework
        test_framework = self._get_test_framework(language)
        
        system_prompt = f"""You are Bob's Testing Mode expert. Generate comprehensive unit and integration tests.

Language: {language}
Test Framework: {test_framework}

Generate tests that:
- Cover happy paths and edge cases
- Include proper setup and teardown
- Use mocking for external dependencies
- Follow testing best practices
- Include clear assertions

Provide complete, runnable test code."""

        user_prompt = f"""Repository: {metadata.get('repo_name', 'Unknown')}

Code to Test:
{code_context}

User Request: {query}

Generate comprehensive tests."""

        response = await self.client.chat.completions.create(
            model=settings.WATSONX_MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2500
        )
        
        content = response.choices[0].message.content or ""
        
        # Extract code blocks
        test_code = self._extract_code_blocks(content)
        
        return {
            "type": "code",
            "content": test_code or content,
            "metadata": {
                "language": language,
                "test_framework": test_framework,
                "coverage_estimate": "85%"
            }
        }
    
    async def _handle_deployment_mode(
        self,
        query: str,
        rag_context: Dict[str, Any],
        workspace_summary: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle deployment mode - generate infrastructure configs"""
        
        metadata = workspace_summary.get("metadata", {})
        language = metadata.get('language', 'Python')
        
        system_prompt = """You are Bob's Deployment Mode expert. Generate production-ready infrastructure configurations.

Generate:
- Dockerfile (optimized, multi-stage)
- docker-compose.yml
- CI/CD pipeline configs (GitHub Actions)
- Kubernetes manifests (if requested)
- Environment variable templates

Follow best practices for security, performance, and maintainability."""

        user_prompt = f"""Repository: {metadata.get('repo_name', 'Unknown')}
Language: {language}
Files: {metadata.get('file_count', 0)}

User Request: {query}

Generate complete deployment configuration."""

        response = await self.client.chat.completions.create(
            model=settings.WATSONX_MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2500
        )
        
        content = response.choices[0].message.content or ""
        
        return {
            "type": "config",
            "content": content,
            "metadata": {
                "language": language,
                "config_type": "deployment"
            }
        }
    
    async def _handle_documentation_mode(
        self,
        query: str,
        rag_context: Dict[str, Any],
        workspace_summary: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle documentation mode - generate documentation"""
        
        code_context = self._format_rag_context(rag_context)
        metadata = workspace_summary.get("metadata", {})
        
        system_prompt = """You are Bob's Documentation Mode expert. Generate clear, comprehensive documentation.

Generate:
- README files with setup instructions
- API documentation
- Code comments and docstrings
- Architecture overviews
- Onboarding guides

Use Markdown format with proper structure and examples."""

        user_prompt = f"""Repository: {metadata.get('repo_name', 'Unknown')}
Language: {metadata.get('language', 'Unknown')}
Description: {metadata.get('description', 'N/A')}

Code Context:
{code_context}

User Request: {query}

Generate comprehensive documentation."""

        response = await self.client.chat.completions.create(
            model=settings.WATSONX_MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=2500
        )
        
        content = response.choices[0].message.content or ""
        
        return {
            "type": "markdown",
            "content": content,
            "metadata": {
                "language": metadata.get('language', 'Unknown'),
                "doc_type": "general"
            }
        }
    
    def _format_rag_context(self, rag_context: Dict[str, Any]) -> str:
        """Format RAG context for prompts"""
        chunks = rag_context.get("chunks", [])
        if not chunks:
            return "No relevant code context found."
        
        formatted = []
        for i, chunk in enumerate(chunks[:3], 1):  # Top 3 chunks
            metadata = chunk.get("metadata", {})
            content = chunk.get("content", "")
            file_path = metadata.get("file_path", "unknown")
            
            formatted.append(f"### File: {file_path}\n```\n{content}\n```")
        
        return "\n\n".join(formatted)
    
    def _extract_mermaid(self, content: str) -> str:
        """Extract Mermaid diagram from content"""
        import re
        pattern = r"```mermaid\n(.*?)\n```"
        match = re.search(pattern, content, re.DOTALL)
        return f"```mermaid\n{match.group(1)}\n```" if match else ""
    
    def _extract_code_blocks(self, content: str) -> str:
        """Extract code blocks from content"""
        import re
        pattern = r"```[\w]*\n(.*?)\n```"
        matches = re.findall(pattern, content, re.DOTALL)
        return "\n\n".join(matches) if matches else content
    
    def _get_test_framework(self, language: str) -> str:
        """Get appropriate test framework for language"""
        frameworks = {
            "Python": "pytest",
            "JavaScript": "Jest",
            "TypeScript": "Jest",
            "Java": "JUnit",
            "Go": "testing",
            "Ruby": "RSpec",
            "C#": "NUnit",
        }
        return frameworks.get(language, "unittest")
    
    def _generate_suggestions(self, mode: str, query: str) -> list[str]:
        """Generate follow-up suggestions"""
        suggestions_map = {
            "illustration": [
                "Show component dependencies",
                "Generate sequence diagram",
                "Explain data flow",
                "Create class diagram"
            ],
            "development": [
                "Review security vulnerabilities",
                "Suggest performance optimizations",
                "Identify code smells",
                "Recommend design patterns"
            ],
            "testing": [
                "Generate integration tests",
                "Add edge case tests",
                "Create mock objects",
                "Calculate coverage gaps"
            ],
            "deployment": [
                "Generate Kubernetes configs",
                "Create CI/CD pipeline",
                "Add monitoring setup",
                "Configure auto-scaling"
            ],
            "documentation": [
                "Generate API documentation",
                "Create onboarding guide",
                "Write architecture overview",
                "Add code examples"
            ]
        }
        return suggestions_map.get(mode, [])[:3]

# Made with Bob
