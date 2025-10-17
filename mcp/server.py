"""
MCP Server for Todoist integration
"""

import asyncio
import json
import os
from typing import Any, Dict, List
from mcp import ClientSession, StdioServerParameters
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    Tool,
    TextContent,
)

from .todoist_tools import TodoistMCP


class TodoistMCPServer:
    def __init__(self):
        self.server = Server("todoist-mcp")
        self.todoist = None
        self.setup_handlers()

    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            return [
                Tool(
                    name="get_tasks",
                    description="Get tasks from Todoist",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "Project ID to filter tasks"
                            },
                            "filter": {
                                "type": "string", 
                                "description": "Todoist filter expression"
                            }
                        }
                    }
                ),
                Tool(
                    name="create_task",
                    description="Create a new task in Todoist",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Task content/title"
                            },
                            "project_id": {
                                "type": "string",
                                "description": "Project ID"
                            },
                            "due_string": {
                                "type": "string",
                                "description": "Due date (e.g. 'today', 'tomorrow')"
                            },
                            "priority": {
                                "type": "integer",
                                "description": "Priority (1-4)"
                            }
                        },
                        "required": ["content"]
                    }
                ),
                Tool(
                    name="complete_task",
                    description="Mark task as completed",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to complete"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                Tool(
                    name="delete_task",
                    description="Delete task from Todoist",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to delete"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                Tool(
                    name="get_projects",
                    description="Get all projects from Todoist",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="update_task",
                    description="Update existing task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to update"
                            },
                            "content": {
                                "type": "string",
                                "description": "New task content"
                            },
                            "due_string": {
                                "type": "string",
                                "description": "New due date"
                            },
                            "priority": {
                                "type": "integer",
                                "description": "New priority (1-4)"
                            }
                        },
                        "required": ["task_id"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> CallToolResult:
            if not self.todoist:
                api_token = os.getenv("TODOIST_API_TOKEN")
                if not api_token:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text="Error: TODOIST_API_TOKEN not found"
                            )
                        ]
                    )
                self.todoist = TodoistMCP(api_token)

            try:
                if name == "get_tasks":
                    result = self.todoist.get_tasks(
                        project_id=arguments.get("project_id"),
                        filter_expr=arguments.get("filter")
                    )
                elif name == "create_task":
                    result = self.todoist.create_task(
                        content=arguments["content"],
                        project_id=arguments.get("project_id"),
                        due_string=arguments.get("due_string"),
                        priority=arguments.get("priority", 1)
                    )
                elif name == "complete_task":
                    result = self.todoist.complete_task(
                        task_id=arguments["task_id"]
                    )
                elif name == "delete_task":
                    result = self.todoist.delete_task(
                        task_id=arguments["task_id"]
                    )
                elif name == "get_projects":
                    result = self.todoist.get_projects()
                elif name == "update_task":
                    result = self.todoist.update_task(
                        task_id=arguments["task_id"],
                        content=arguments.get("content"),
                        due_string=arguments.get("due_string"),
                        priority=arguments.get("priority")
                    )
                else:
                    result = {"success": False, "error": f"Unknown tool: {name}"}

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(result, indent=2)
                        )
                    ]
                )
            except Exception as e:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error: {str(e)}"
                        )
                    ]
                )

    async def run(self):
        async with self.server.stdio_server() as streams:
            await self.server.run(
                streams[0], streams[1], InitializationOptions()
            )


async def main():
    server = TodoistMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())