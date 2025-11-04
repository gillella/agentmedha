"""
Admin Setup Agent
Conversational agent to help admins configure databases and data sources.
"""

from typing import Any, Dict, List, Optional
from enum import Enum

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import logger


class Intent(str, Enum):
    """Admin setup intents"""
    
    GREETING = "greeting"
    SETUP_DATABASE = "setup_database"
    CONNECT_DATABASE = "connect_database"
    SELECT_DATABASE_TYPE = "select_database_type"
    PROVIDE_CONNECTION_DETAILS = "provide_connection_details"
    TEST_CONNECTION = "test_connection"
    CREATE_DATABASE = "create_database"
    CREATE_TABLE = "create_table"
    LOAD_DATA = "load_data"
    VIEW_SCHEMA = "view_schema"
    HELP = "help"
    UNKNOWN = "unknown"


class UIComponent(str, Enum):
    """UI components to display in dynamic panel"""
    
    NONE = "none"
    DATABASE_SELECTOR = "database_selector"
    CONNECTION_FORM = "connection_form"
    CONNECTION_TEST = "connection_test"
    DATABASE_CREATOR = "database_creator"
    TABLE_BUILDER = "table_builder"
    DATA_UPLOADER = "data_uploader"
    SCHEMA_VIEWER = "schema_viewer"
    SUCCESS_FEEDBACK = "success_feedback"


class ConversationState(str, Enum):
    """Conversation states"""
    
    START = "start"
    SELECTING_DATABASE_TYPE = "selecting_database_type"
    COLLECTING_CONNECTION_DETAILS = "collecting_connection_details"
    TESTING_CONNECTION = "testing_connection"
    CONNECTED = "connected"
    CREATING_DATABASE = "creating_database"
    CREATING_TABLE = "creating_table"
    LOADING_DATA = "loading_data"


class AdminSetupAgent:
    """
    Conversational agent for admin database setup.
    
    This agent:
    1. Understands admin's intent through natural language
    2. Maintains conversation context
    3. Recommends appropriate UI components
    4. Guides admin through setup process
    5. Provides helpful responses
    
    Principle #1: Single-Purpose Agent - focused on admin setup only
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.temperature = 0.7  # Slightly higher for more conversational responses

    async def process_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process admin's message and return response with UI recommendations.
        
        Args:
            message: Admin's message
            context: Current conversation context
            
        Returns:
            {
                "message": "Agent's response",
                "intent": "detected_intent",
                "ui_component": "component_to_show",
                "data": {...},  # Additional data for UI
                "next_state": "conversation_state"
            }
        """
        logger.info(
            "admin_setup_agent.processing_message",
            message_preview=message[:50],
            current_state=context.get("state") if context else None,
        )

        # Initialize context if not provided
        if context is None:
            context = {
                "state": ConversationState.START,
                "database_type": None,
                "connection_details": {},
                "conversation_history": [],
            }
        
        # Ensure conversation_history exists
        if "conversation_history" not in context:
            context["conversation_history"] = []

        # Add message to history
        context["conversation_history"].append({
            "role": "user",
            "content": message,
        })

        # Detect intent
        intent = await self._detect_intent(message, context)
        
        # Process based on intent and state
        response = await self._process_intent(intent, message, context)
        
        # Add response to history
        context["conversation_history"].append({
            "role": "assistant",
            "content": response["message"],
        })
        
        logger.info(
            "admin_setup_agent.message_processed",
            intent=intent,
            ui_component=response.get("ui_component"),
            next_state=response.get("next_state"),
        )
        
        return response

    async def _detect_intent(
        self,
        message: str,
        context: Dict[str, Any],
    ) -> Intent:
        """
        Detect user intent using LLM.
        
        Args:
            message: User's message
            context: Current conversation context
            
        Returns:
            Detected intent
        """
        current_state = context.get("state", ConversationState.START)
        
        # Context-aware intent detection
        system_prompt = f"""You are an intent classifier for an admin database setup assistant.
        
Current conversation state: {current_state}
Database type selected: {context.get('database_type', 'None')}

Classify the user's message into one of these intents:
- greeting: User is greeting or starting conversation
- setup_database: User wants to set up a new database
- connect_database: User wants to connect to existing database
- select_database_type: User is selecting a database type (PostgreSQL, MySQL, etc.)
- provide_connection_details: User is providing connection details
- test_connection: User wants to test the connection
- create_database: User wants to create a new database
- create_table: User wants to create tables
- load_data: User wants to load data
- view_schema: User wants to view schema
- help: User needs help
- unknown: Cannot determine intent

Respond with ONLY the intent name, nothing else."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
                temperature=0.3,
                max_tokens=50,
            )
            
            intent_str = response.choices[0].message.content.strip().lower()
            
            # Map to Intent enum
            try:
                return Intent(intent_str)
            except ValueError:
                return Intent.UNKNOWN
                
        except Exception as e:
            logger.error("admin_setup_agent.intent_detection_failed", error=str(e))
            return Intent.UNKNOWN

    async def _process_intent(
        self,
        intent: Intent,
        message: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Process intent and generate appropriate response.
        
        Args:
            intent: Detected intent
            message: User's message
            context: Current conversation context
            
        Returns:
            Response dictionary
        """
        handlers = {
            Intent.GREETING: self._handle_greeting,
            Intent.SETUP_DATABASE: self._handle_setup_database,
            Intent.CONNECT_DATABASE: self._handle_setup_database,  # Same flow
            Intent.SELECT_DATABASE_TYPE: self._handle_select_database_type,
            Intent.HELP: self._handle_help,
            Intent.UNKNOWN: self._handle_unknown,
        }
        
        handler = handlers.get(intent, self._handle_unknown)
        return await handler(message, context)

    async def _handle_greeting(
        self,
        message: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle greeting intent"""
        return {
            "message": (
                "👋 Hi! I'm your **Admin Setup Assistant**.\n\n"
                "I can help you:\n"
                "• Connect to databases\n"
                "• Set up new data sources\n"
                "• Create tables and load data\n"
                "• Configure access controls\n\n"
                "What would you like to do today?"
            ),
            "intent": Intent.GREETING.value,
            "ui_component": UIComponent.NONE.value,
            "next_state": ConversationState.START.value,
        }

    async def _handle_setup_database(
        self,
        message: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle setup database intent"""
        return {
            "message": (
                "Great! Let's set up a database connection.\n\n"
                "**Which database system would you like to use?**\n\n"
                "I support:\n"
                "• **PostgreSQL** - Popular open-source database\n"
                "• **MySQL** - Widely used relational database\n"
                "• **Supabase** - PostgreSQL with built-in APIs\n"
                "• **Snowflake** - Cloud data warehouse\n\n"
                "Click on a database type on the right, or tell me your choice!"
            ),
            "intent": Intent.SETUP_DATABASE.value,
            "ui_component": UIComponent.DATABASE_SELECTOR.value,
            "data": {
                "database_types": [
                    {
                        "id": "postgresql",
                        "name": "PostgreSQL",
                        "description": "Open-source relational database",
                        "icon": "database",
                        "popular": True,
                    },
                    {
                        "id": "mysql",
                        "name": "MySQL",
                        "description": "World's most popular open-source database",
                        "icon": "database",
                        "popular": True,
                    },
                    {
                        "id": "supabase",
                        "name": "Supabase",
                        "description": "PostgreSQL with built-in APIs and auth",
                        "icon": "cloud",
                        "popular": False,
                    },
                    {
                        "id": "snowflake",
                        "name": "Snowflake",
                        "description": "Cloud data warehouse platform",
                        "icon": "cloud",
                        "popular": False,
                    },
                ],
            },
            "next_state": ConversationState.SELECTING_DATABASE_TYPE.value,
        }

    async def _handle_select_database_type(
        self,
        message: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle database type selection"""
        # Extract database type from message (PostgreSQL, MySQL, etc.)
        message_lower = message.lower()
        
        db_type_mapping = {
            "postgresql": "postgresql",
            "postgres": "postgresql",
            "mysql": "mysql",
            "supabase": "supabase",
            "snowflake": "snowflake",
        }
        
        selected_type = None
        for key, value in db_type_mapping.items():
            if key in message_lower:
                selected_type = value
                break
        
        if not selected_type:
            return {
                "message": (
                    "I didn't catch which database you selected. "
                    "Could you click on one of the database cards or tell me: "
                    "PostgreSQL, MySQL, Supabase, or Snowflake?"
                ),
                "intent": Intent.SELECT_DATABASE_TYPE.value,
                "ui_component": UIComponent.DATABASE_SELECTOR.value,
                "next_state": ConversationState.SELECTING_DATABASE_TYPE.value,
            }
        
        # Update context
        context["database_type"] = selected_type
        
        # Get connection form fields for this database type
        form_fields = self._get_connection_form_fields(selected_type)
        
        db_name_display = selected_type.title()
        
        return {
            "message": (
                f"Perfect! You've selected **{db_name_display}**.\n\n"
                f"To connect, I'll need some information:\n"
                f"{self._format_required_fields(form_fields)}\n\n"
                f"Please fill in the connection form on the right, or you can tell me the details in the chat!"
            ),
            "intent": Intent.SELECT_DATABASE_TYPE.value,
            "ui_component": UIComponent.CONNECTION_FORM.value,
            "data": {
                "database_type": selected_type,
                "form_fields": form_fields,
            },
            "next_state": ConversationState.COLLECTING_CONNECTION_DETAILS.value,
        }

    async def _handle_help(
        self,
        message: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle help request"""
        current_state = context.get("state", ConversationState.START)
        
        if current_state == ConversationState.SELECTING_DATABASE_TYPE:
            help_message = (
                "**Choosing a database:**\n\n"
                "• **PostgreSQL** - Best for most use cases, open-source, reliable\n"
                "• **MySQL** - Great for web applications, widely supported\n"
                "• **Supabase** - PostgreSQL with instant APIs, perfect for rapid development\n"
                "• **Snowflake** - Enterprise data warehouse for analytics\n\n"
                "Just click on a card or tell me which one you prefer!"
            )
        elif current_state == ConversationState.COLLECTING_CONNECTION_DETAILS:
            help_message = (
                "**Connection details:**\n\n"
                "You can either:\n"
                "1. Fill in the form on the right\n"
                "2. Tell me the details in the chat\n\n"
                "Example: 'Host is localhost, port 5432, username is admin, password is secret, database name is mydb'\n\n"
                "Don't worry, all credentials are encrypted!"
            )
        else:
            help_message = (
                "**What I can help with:**\n\n"
                "• Connect to databases\n"
                "• Set up new data sources\n"
                "• Test connections\n"
                "• Create databases and tables\n"
                "• Load data from CSV or JSON\n\n"
                "Just tell me what you'd like to do!"
            )
        
        return {
            "message": help_message,
            "intent": Intent.HELP.value,
            "ui_component": context.get("ui_component", UIComponent.NONE.value),
            "next_state": current_state,
        }

    async def _handle_unknown(
        self,
        message: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle unknown intent"""
        return {
            "message": (
                "I'm not sure I understood that. Could you rephrase?\n\n"
                "You can:\n"
                "• Say 'help' for guidance\n"
                "• Tell me 'set up a database'\n"
                "• Ask me questions about database setup"
            ),
            "intent": Intent.UNKNOWN.value,
            "ui_component": context.get("ui_component", UIComponent.NONE.value),
            "next_state": context.get("state", ConversationState.START.value),
        }

    def _get_connection_form_fields(self, database_type: str) -> List[Dict[str, Any]]:
        """
        Get connection form fields for a specific database type.
        
        Args:
            database_type: Database type (postgresql, mysql, etc.)
            
        Returns:
            List of form field definitions
        """
        fields_map = {
            "postgresql": [
                {"name": "host", "label": "Host", "type": "text", "placeholder": "localhost", "required": True},
                {"name": "port", "label": "Port", "type": "number", "placeholder": "5432", "required": True},
                {"name": "username", "label": "Username", "type": "text", "placeholder": "postgres", "required": True},
                {"name": "password", "label": "Password", "type": "password", "placeholder": "••••••••", "required": True},
                {"name": "database", "label": "Database Name", "type": "text", "placeholder": "mydb", "required": True},
            ],
            "mysql": [
                {"name": "host", "label": "Host", "type": "text", "placeholder": "localhost", "required": True},
                {"name": "port", "label": "Port", "type": "number", "placeholder": "3306", "required": True},
                {"name": "username", "label": "Username", "type": "text", "placeholder": "root", "required": True},
                {"name": "password", "label": "Password", "type": "password", "placeholder": "••••••••", "required": True},
                {"name": "database", "label": "Database Name", "type": "text", "placeholder": "mydb", "required": True},
            ],
            "supabase": [
                {"name": "project_url", "label": "Project URL", "type": "text", "placeholder": "https://xxx.supabase.co", "required": True},
                {"name": "api_key", "label": "API Key", "type": "password", "placeholder": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "required": True},
                {"name": "database", "label": "Database Name", "type": "text", "placeholder": "postgres", "required": False},
            ],
            "snowflake": [
                {"name": "account", "label": "Account", "type": "text", "placeholder": "xy12345", "required": True},
                {"name": "username", "label": "Username", "type": "text", "placeholder": "admin", "required": True},
                {"name": "password", "label": "Password", "type": "password", "placeholder": "••••••••", "required": True},
                {"name": "warehouse", "label": "Warehouse", "type": "text", "placeholder": "COMPUTE_WH", "required": True},
                {"name": "database", "label": "Database", "type": "text", "placeholder": "MYDB", "required": True},
                {"name": "schema", "label": "Schema", "type": "text", "placeholder": "PUBLIC", "required": True},
            ],
        }
        
        return fields_map.get(database_type, [])

    def _format_required_fields(self, fields: List[Dict[str, Any]]) -> str:
        """Format required fields for display in message"""
        required = [f"• **{f['label']}**" for f in fields if f.get("required")]
        return "\n".join(required)


# Global instance
admin_setup_agent = AdminSetupAgent()

