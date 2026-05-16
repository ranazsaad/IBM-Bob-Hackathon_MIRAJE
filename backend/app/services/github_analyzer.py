"""GitHub repository analyzer service"""

import re
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from github import Github
import uuid

from app.config import settings
from app.database.models import Workspace, File
from app.database.vector_store import vector_store
from app.services.embedding_service import embedding_service
from app.api.schemas.responses import GitHubAnalyzeResponse


class GitHubAnalyzer:
    """Service for analyzing GitHub repositories"""
    
    def __init__(self, db: Session):
        """Initialize GitHub analyzer"""
        self.db = db
        # Only use token if it's not the placeholder value
        if settings.GITHUB_TOKEN and settings.GITHUB_TOKEN != "your_github_token_here":
            self.github = Github(settings.GITHUB_TOKEN)
        else:
            # Use unauthenticated access (60 requests/hour limit)
            self.github = Github()
    
    def _extract_repo_info(self, repo_url: str) -> tuple[str, str]:
        """Extract owner and repo name from URL"""
        pattern = r"github\.com/([^/]+)/([^/]+)"
        match = re.search(pattern, repo_url)
        if not match:
            raise ValueError("Invalid GitHub URL")
        return match.group(1), match.group(2).replace(".git", "")
    
    async def analyze(
        self,
        repo_url: str,
        branch: str = "main",
        depth: str = "shallow"
    ) -> GitHubAnalyzeResponse:
        """
        Analyze a GitHub repository
        
        For hackathon: Use GitHub API to get metadata and file structure
        without cloning the entire repository
        """
        try:
            # Extract repo info
            owner, repo_name = self._extract_repo_info(repo_url)
            
            # Get repository from GitHub API
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            
            # Create workspace
            workspace_id = str(uuid.uuid4())
            
            # Get repository contents
            contents = repo.get_contents("", ref=branch)
            files_data = []
            total_lines = 0
            languages = {}
            
            # Process files (increased limits for better file tree)
            file_count = 0
            max_files = 500 if depth == "shallow" else 2000
            
            while contents and file_count < max_files:
                file_content = contents.pop(0)
                
                if file_content.type == "dir":
                    # Add directory contents
                    try:
                        contents.extend(repo.get_contents(file_content.path, ref=branch))
                    except Exception as e:
                        # Handle rate limits and other errors gracefully
                        if "rate limit" in str(e).lower():
                            print(f"[GitHub] Rate limit hit, stopping at {file_count} files")
                            break
                        # Skip directories that can't be accessed
                        pass
                else:
                    # Process file
                    file_path = file_content.path
                    file_size = file_content.size
                    
                    # Detect language from extension
                    ext = file_path.split('.')[-1] if '.' in file_path else 'unknown'
                    language = self._detect_language(ext)
                    
                    if language:
                        languages[language] = languages.get(language, 0) + 1
                    
                    # Estimate lines (rough estimate: 50 chars per line)
                    estimated_lines = max(1, file_size // 50)
                    total_lines += estimated_lines
                    
                    # Store file metadata
                    file_data = File(
                        workspace_id=workspace_id,
                        file_path=file_path,
                        language=language,
                        lines=estimated_lines,
                        indexed=False
                    )
                    files_data.append(file_data)
                    file_count += 1
            
            # Determine primary language
            primary_language = max(languages.items(), key=lambda x: x[1])[0] if languages else "Unknown"
            
            # Create workspace metadata
            metadata = {
                "repo_name": repo_name,
                "owner": owner,
                "language": primary_language,
                "file_count": file_count,
                "total_lines": total_lines,
                "structure": {
                    "languages": languages,
                    "directories": list(set([f.file_path.split('/')[0] for f in files_data if '/' in f.file_path]))
                },
                "key_files": [f.file_path for f in files_data[:10]],
                "repo_url": repo_url,
                "branch": branch,
                "stars": repo.stargazers_count,
                "description": repo.description
            }
            
            # Create workspace
            workspace = Workspace(
                id=workspace_id,
                type="github",
                workspace_metadata=metadata,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow()
            )
            
            self.db.add(workspace)
            self.db.add_all(files_data)
            self.db.commit()
            
            # Index key files in vector store (async task in production)
            await self._index_key_files(workspace_id, files_data[:10], repo, branch)
            
            return GitHubAnalyzeResponse(
                workspace_id=workspace_id,
                status="completed",
                metadata=metadata,
                indexed_at=datetime.utcnow()
            )
            
        except Exception as e:
            raise Exception(f"Failed to analyze repository: {str(e)}")
    
    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension"""
        lang_map = {
            'py': 'Python',
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'jsx': 'React',
            'tsx': 'React',
            'java': 'Java',
            'cpp': 'C++',
            'c': 'C',
            'go': 'Go',
            'rs': 'Rust',
            'rb': 'Ruby',
            'php': 'PHP',
            'swift': 'Swift',
            'kt': 'Kotlin',
            'cs': 'C#',
            'html': 'HTML',
            'css': 'CSS',
            'scss': 'SCSS',
            'md': 'Markdown',
            'json': 'JSON',
            'yaml': 'YAML',
            'yml': 'YAML',
            'sql': 'SQL',
            'sh': 'Shell',
        }
        return lang_map.get(extension.lower(), None)
    
    async def _index_key_files(
        self,
        workspace_id: str,
        files: List[File],
        repo: Any,
        branch: str
    ):
        """Index key files in vector store"""
        try:
            documents = []
            embeddings_list = []
            metadatas = []
            ids = []
            
            for idx, file in enumerate(files):
                try:
                    # Get file content
                    content = repo.get_contents(file.file_path, ref=branch)
                    if content.size > 100000:  # Skip large files
                        continue
                    
                    file_content = content.decoded_content.decode('utf-8')
                    
                    # Chunk content (simple chunking for demo)
                    chunks = self._chunk_content(file_content)
                    
                    for chunk_idx, chunk in enumerate(chunks[:5]):  # Limit chunks per file
                        documents.append(chunk)
                        metadatas.append({
                            "workspace_id": workspace_id,
                            "file_path": file.file_path,
                            "language": file.language or "unknown",
                            "chunk_index": chunk_idx
                        })
                        ids.append(f"{workspace_id}:{file.file_path}:{chunk_idx}")
                
                except Exception as e:
                    print(f"Error indexing file {file.file_path}: {e}")
                    continue
            
            if documents:
                # Generate embeddings
                embeddings_list = await embedding_service.generate_embeddings(documents)
                
                # Store in vector database
                vector_store.add_documents(
                    documents=documents,
                    embeddings=embeddings_list,
                    metadatas=metadatas,
                    ids=ids
                )
                
                # Mark files as indexed
                for file in files:
                    file.indexed = True
                self.db.commit()
        
        except Exception as e:
            print(f"Error indexing files: {e}")
    
    def _chunk_content(self, content: str, chunk_size: int = 500) -> List[str]:
        """Simple content chunking"""
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line)
            if current_size + line_size > chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks

# Made with Bob
