"""
MCP Server Connectors

Implements connectors for different MCP server types.
Each connector provides connection testing and resource discovery.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import structlog
import psycopg2
import sqlite3
import httpx
from pathlib import Path
import os

logger = structlog.get_logger()


class MCPConnector(ABC):
    """Base class for MCP connectors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to the server.
        
        Returns:
            Dict with 'success' (bool), 'message' (str), and optionally 'error' (str)
        """
        pass
    
    @abstractmethod
    def discover_resources(self) -> List[Dict[str, Any]]:
        """
        Discover available resources from the server.
        
        Returns:
            List of resource dictionaries with:
            - resource_uri: str
            - resource_type: str
            - name: str
            - description: Optional[str]
            - metadata: Dict[str, Any]
        """
        pass


class PostgreSQLConnector(MCPConnector):
    """PostgreSQL MCP connector"""
    
    def test_connection(self) -> Dict[str, Any]:
        """Test PostgreSQL connection"""
        try:
            conn = psycopg2.connect(
                host=self.config.get('host'),
                port=self.config.get('port', 5432),
                database=self.config.get('database'),
                user=self.config.get('username'),
                password=self.config.get('password')
            )
            
            # Test query
            cursor = conn.cursor()
            cursor.execute('SELECT version()')
            version = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            logger.info("postgres.connection_test_success", 
                       host=self.config.get('host'),
                       database=self.config.get('database'))
            
            return {
                'success': True,
                'message': f'Connected successfully. {version[:50]}...'
            }
            
        except Exception as e:
            logger.error("postgres.connection_test_failed", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to connect to PostgreSQL'
            }
    
    def discover_resources(self) -> List[Dict[str, Any]]:
        """Discover tables and views from PostgreSQL"""
        try:
            conn = psycopg2.connect(
                host=self.config.get('host'),
                port=self.config.get('port', 5432),
                database=self.config.get('database'),
                user=self.config.get('username'),
                password=self.config.get('password')
            )
            
            cursor = conn.cursor()
            schema_filter = self.config.get('schema')
            
            # Discover tables from all non-system schemas if no specific schema specified
            if schema_filter:
                # Discover from specific schema
                cursor.execute("""
                    SELECT 
                        table_schema,
                        table_name,
                        table_type
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    ORDER BY table_name
                """, (schema_filter,))
            else:
                # Discover from all user schemas (excluding system schemas)
                cursor.execute("""
                    SELECT 
                        table_schema,
                        table_name,
                        table_type
                    FROM information_schema.tables
                    WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                    ORDER BY table_schema, table_name
                """)
            
            resources = []
            for row in cursor.fetchall():
                schema_name, table_name, table_type = row
                
                # Get column count
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                """, (schema_name, table_name))
                column_count = cursor.fetchone()[0]
                
                # Use schema.table format for clarity
                full_table_name = f"{schema_name}.{table_name}"
                
                resources.append({
                    'resource_uri': f'postgres://{schema_name}/{table_name}',
                    'resource_type': 'table' if table_type == 'BASE TABLE' else 'view',
                    'name': full_table_name,  # Include schema in name
                    'description': f'{table_type} with {column_count} columns',
                    'metadata': {
                        'schema': schema_name,
                        'table_name': table_name,
                        'table_type': table_type,
                        'column_count': column_count
                    }
                })
            
            cursor.close()
            conn.close()
            
            logger.info("postgres.resources_discovered", count=len(resources))
            return resources
            
        except Exception as e:
            logger.error("postgres.resource_discovery_failed", error=str(e))
            return []


class GitHubConnector(MCPConnector):
    """GitHub MCP connector using REST API"""
    
    def test_connection(self) -> Dict[str, Any]:
        """Test GitHub connection"""
        try:
            headers = {
                'Authorization': f'token {self.config.get("token")}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Test with user endpoint
            response = httpx.get('https://api.github.com/user', headers=headers, timeout=10)
            response.raise_for_status()
            
            user_data = response.json()
            logger.info("github.connection_test_success", user=user_data.get('login'))
            
            return {
                'success': True,
                'message': f'Connected as {user_data.get("login")}'
            }
            
        except httpx.HTTPStatusError as e:
            logger.error("github.connection_test_failed", status=e.response.status_code)
            return {
                'success': False,
                'error': f'HTTP {e.response.status_code}',
                'message': 'Failed to authenticate with GitHub'
            }
        except Exception as e:
            logger.error("github.connection_test_failed", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to connect to GitHub'
            }
    
    def discover_resources(self) -> List[Dict[str, Any]]:
        """Discover repositories from GitHub"""
        try:
            headers = {
                'Authorization': f'token {self.config.get("token")}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            resources = []
            
            # If owner and repo specified, get that specific repo
            owner = self.config.get('owner')
            repo = self.config.get('repo')
            
            if owner and repo:
                response = httpx.get(
                    f'https://api.github.com/repos/{owner}/{repo}',
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                repo_data = response.json()
                
                resources.append({
                    'resource_uri': f'github://{owner}/{repo}',
                    'resource_type': 'repository',
                    'name': repo_data['name'],
                    'description': repo_data.get('description', 'No description'),
                    'metadata': {
                        'owner': owner,
                        'full_name': repo_data['full_name'],
                        'private': repo_data['private'],
                        'default_branch': repo_data['default_branch'],
                        'stars': repo_data['stargazers_count'],
                        'forks': repo_data['forks_count']
                    }
                })
            else:
                # List user's repositories
                response = httpx.get(
                    'https://api.github.com/user/repos',
                    headers=headers,
                    params={'per_page': 50, 'sort': 'updated'},
                    timeout=10
                )
                response.raise_for_status()
                repos = response.json()
                
                for repo_data in repos:
                    resources.append({
                        'resource_uri': f'github://{repo_data["full_name"]}',
                        'resource_type': 'repository',
                        'name': repo_data['name'],
                        'description': repo_data.get('description', 'No description'),
                        'metadata': {
                            'owner': repo_data['owner']['login'],
                            'full_name': repo_data['full_name'],
                            'private': repo_data['private'],
                            'default_branch': repo_data['default_branch'],
                            'stars': repo_data['stargazers_count'],
                            'forks': repo_data['forks_count']
                        }
                    })
            
            logger.info("github.resources_discovered", count=len(resources))
            return resources
            
        except Exception as e:
            logger.error("github.resource_discovery_failed", error=str(e))
            return []


class FilesystemConnector(MCPConnector):
    """Filesystem MCP connector"""
    
    def test_connection(self) -> Dict[str, Any]:
        """Test filesystem access"""
        try:
            path = Path(self.config.get('path'))
            
            if not path.exists():
                return {
                    'success': False,
                    'error': 'Path does not exist',
                    'message': f'Directory {path} not found'
                }
            
            if not path.is_dir():
                return {
                    'success': False,
                    'error': 'Path is not a directory',
                    'message': f'{path} is not a directory'
                }
            
            # Test read access
            list(path.iterdir())
            
            logger.info("filesystem.connection_test_success", path=str(path))
            
            return {
                'success': True,
                'message': f'Successfully accessed {path}'
            }
            
        except PermissionError:
            return {
                'success': False,
                'error': 'Permission denied',
                'message': 'No permission to read directory'
            }
        except Exception as e:
            logger.error("filesystem.connection_test_failed", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to access filesystem'
            }
    
    def discover_resources(self) -> List[Dict[str, Any]]:
        """Discover files and directories"""
        try:
            base_path = Path(self.config.get('path'))
            allowed_extensions = self.config.get('allowed_extensions', '').split(',')
            allowed_extensions = [ext.strip() for ext in allowed_extensions if ext.strip()]
            
            resources = []
            
            # Walk directory tree
            for root, dirs, files in os.walk(base_path):
                root_path = Path(root)
                relative_root = root_path.relative_to(base_path)
                
                # Add directories
                for dir_name in dirs[:50]:  # Limit to first 50
                    dir_path = root_path / dir_name
                    resources.append({
                        'resource_uri': f'file://{dir_path}',
                        'resource_type': 'directory',
                        'name': dir_name,
                        'description': f'Directory in {relative_root}',
                        'metadata': {
                            'path': str(dir_path),
                            'parent': str(relative_root)
                        }
                    })
                
                # Add files
                for file_name in files[:100]:  # Limit to first 100
                    file_path = root_path / file_name
                    
                    # Filter by extension if specified
                    if allowed_extensions:
                        if not any(file_name.endswith(ext) for ext in allowed_extensions):
                            continue
                    
                    try:
                        stat = file_path.stat()
                        resources.append({
                            'resource_uri': f'file://{file_path}',
                            'resource_type': 'file',
                            'name': file_name,
                            'description': f'{file_path.suffix} file ({stat.st_size} bytes)',
                            'metadata': {
                                'path': str(file_path),
                                'parent': str(relative_root),
                                'size': stat.st_size,
                                'extension': file_path.suffix
                            }
                        })
                    except:
                        pass  # Skip files that can't be accessed
                
                # Only scan top level for now
                break
            
            logger.info("filesystem.resources_discovered", count=len(resources))
            return resources
            
        except Exception as e:
            logger.error("filesystem.resource_discovery_failed", error=str(e))
            return []


class SQLiteConnector(MCPConnector):
    """SQLite MCP connector"""
    
    def test_connection(self) -> Dict[str, Any]:
        """Test SQLite database"""
        try:
            db_path = self.config.get('database_path')
            
            if not os.path.exists(db_path):
                return {
                    'success': False,
                    'error': 'Database file does not exist',
                    'message': f'File {db_path} not found'
                }
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT sqlite_version()')
            version = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            logger.info("sqlite.connection_test_success", db_path=db_path)
            
            return {
                'success': True,
                'message': f'Connected successfully. SQLite version {version}'
            }
            
        except Exception as e:
            logger.error("sqlite.connection_test_failed", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to connect to SQLite database'
            }
    
    def discover_resources(self) -> List[Dict[str, Any]]:
        """Discover tables from SQLite database"""
        try:
            db_path = self.config.get('database_path')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("""
                SELECT name, type
                FROM sqlite_master
                WHERE type IN ('table', 'view')
                AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            
            resources = []
            for row in cursor.fetchall():
                table_name, table_type = row
                
                # Get column count
                cursor.execute(f'PRAGMA table_info({table_name})')
                column_count = len(cursor.fetchall())
                
                resources.append({
                    'resource_uri': f'sqlite:///{table_name}',
                    'resource_type': table_type,
                    'name': table_name,
                    'description': f'{table_type.capitalize()} with {column_count} columns',
                    'metadata': {
                        'table_type': table_type,
                        'column_count': column_count,
                        'database': db_path
                    }
                })
            
            cursor.close()
            conn.close()
            
            logger.info("sqlite.resources_discovered", count=len(resources))
            return resources
            
        except Exception as e:
            logger.error("sqlite.resource_discovery_failed", error=str(e))
            return []


class GmailConnector(MCPConnector):
    """Gmail MCP connector using Google Auth"""
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Gmail connection"""
        try:
            import sys
            from pathlib import Path
            
            # Add google-auth helper to path
            google_auth_path = Path.home() / ".local" / "bin" / "google-auth"
            if str(google_auth_path) not in sys.path:
                sys.path.insert(0, str(google_auth_path))
            
            from google_api_helper import get_credentials
            from googleapiclient.discovery import build
            
            # Get default account or first account
            default_account = self.config.get('default_account', 'arvinda.reddy@gmail.com')
            accounts = self.config.get('accounts', [default_account])
            test_account = accounts[0]
            
            # Test authentication
            creds = get_credentials(test_account)
            if not creds:
                return {
                    'success': False,
                    'error': 'Failed to get credentials',
                    'message': 'Gmail authentication failed. Check OAuth tokens.'
                }
            
            # Test API access
            service = build('gmail', 'v1', credentials=creds)
            profile = service.users().getProfile(userId='me').execute()
            
            logger.info("gmail.connection_test_success", account=test_account)
            
            return {
                'success': True,
                'message': f'Connected to Gmail as {profile.get("emailAddress", test_account)}'
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'Google Auth helper not found',
                'message': 'Gmail connector requires google-auth helper at ~/.local/bin/google-auth/'
            }
        except Exception as e:
            logger.error("gmail.connection_test_failed", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to connect to Gmail'
            }
    
    def discover_resources(self) -> List[Dict[str, Any]]:
        """Discover Gmail accounts and labels"""
        try:
            import sys
            from pathlib import Path
            
            # Add google-auth helper to path
            google_auth_path = Path.home() / ".local" / "bin" / "google-auth"
            if str(google_auth_path) not in sys.path:
                sys.path.insert(0, str(google_auth_path))
            
            from google_api_helper import get_credentials
            from googleapiclient.discovery import build
            
            resources = []
            accounts = self.config.get('accounts', [self.config.get('default_account', 'arvinda.reddy@gmail.com')])
            
            for account in accounts:
                try:
                    creds = get_credentials(account)
                    if not creds:
                        continue
                    
                    service = build('gmail', 'v1', credentials=creds)
                    
                    # Get profile
                    profile = service.users().getProfile(userId='me').execute()
                    
                    # Add account as resource
                    resources.append({
                        'resource_uri': f'gmail://{account}',
                        'resource_type': 'account',
                        'name': account,
                        'description': f'Gmail account: {profile.get("emailAddress", account)}',
                        'metadata': {
                            'account': account,
                            'email_address': profile.get('emailAddress'),
                            'messages_total': profile.get('messagesTotal', 0),
                            'threads_total': profile.get('threadsTotal', 0)
                        }
                    })
                    
                    # Get labels (common ones)
                    labels = service.users().labels().list(userId='me').execute()
                    for label in labels.get('labels', [])[:10]:  # Limit to 10 labels
                        if label['type'] == 'user':
                            resources.append({
                                'resource_uri': f'gmail://{account}/labels/{label["id"]}',
                                'resource_type': 'label',
                                'name': label['name'],
                                'description': f'Label: {label["name"]}',
                                'metadata': {
                                    'account': account,
                                    'label_id': label['id'],
                                    'label_name': label['name']
                                }
                            })
                
                except Exception as e:
                    logger.warning("gmail.account_discovery_failed", account=account, error=str(e))
                    continue
            
            logger.info("gmail.resources_discovered", count=len(resources))
            return resources
            
        except Exception as e:
            logger.error("gmail.resource_discovery_failed", error=str(e))
            return []


# Factory function
def get_connector(server_type: str, config: Dict[str, Any]) -> MCPConnector:
    """
    Get the appropriate connector for a server type.
    
    Args:
        server_type: Type of server
        config: Server configuration
        
    Returns:
        MCPConnector instance
        
    Raises:
        ValueError: If server type is unknown
    """
    connectors = {
        'postgres': PostgreSQLConnector,
        'github': GitHubConnector,
        'filesystem': FilesystemConnector,
        'sqlite': SQLiteConnector,
        'gmail': GmailConnector,
    }
    
    connector_class = connectors.get(server_type)
    if not connector_class:
        raise ValueError(f'Unknown server type: {server_type}')
    
    return connector_class(config)

