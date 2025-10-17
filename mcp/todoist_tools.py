"""
Todoist MCP Tools
"""

import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, date


class TodoistMCP:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.todoist.com/rest/v2"
        self.headers = {"Authorization": f"Bearer {api_token}"}

    def get_tasks(
        self, 
        project_id: Optional[str] = None,
        filter_expr: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get tasks from Todoist"""
        try:
            params = {}
            if project_id:
                params["project_id"] = project_id
            if filter_expr:
                params["filter"] = filter_expr

            response = requests.get(
                f"{self.base_url}/tasks",
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                tasks = response.json()
                return {
                    "success": True,
                    "tasks": tasks,
                    "count": len(tasks)
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_task(
        self,
        content: str,
        project_id: Optional[str] = None,
        due_string: Optional[str] = None,
        priority: int = 1,
        parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create new task in Todoist"""
        try:
            data = {"content": content, "priority": priority}
            
            if project_id:
                data["project_id"] = project_id
            if due_string:
                data["due_string"] = due_string
            if parent_id:
                data["parent_id"] = parent_id

            response = requests.post(
                f"{self.base_url}/tasks",
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 200:
                task = response.json()
                return {
                    "success": True,
                    "task": task,
                    "message": f"Task created: {content}"
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def complete_task(self, task_id: str) -> Dict[str, Any]:
        """Complete task in Todoist"""
        try:
            response = requests.post(
                f"{self.base_url}/tasks/{task_id}/close",
                headers=self.headers
            )
            
            if response.status_code == 204:
                return {
                    "success": True,
                    "message": f"Task {task_id} completed"
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Delete task from Todoist"""
        try:
            response = requests.delete(
                f"{self.base_url}/tasks/{task_id}",
                headers=self.headers
            )
            
            if response.status_code == 204:
                return {
                    "success": True,
                    "message": f"Task {task_id} deleted"
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_projects(self) -> Dict[str, Any]:
        """Get all projects from Todoist"""
        try:
            response = requests.get(
                f"{self.base_url}/projects",
                headers=self.headers
            )
            
            if response.status_code == 200:
                projects = response.json()
                return {
                    "success": True,
                    "projects": projects,
                    "count": len(projects)
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_task(
        self,
        task_id: str,
        content: Optional[str] = None,
        due_string: Optional[str] = None,
        priority: Optional[int] = None
    ) -> Dict[str, Any]:
        """Update existing task"""
        try:
            data = {}
            if content:
                data["content"] = content
            if due_string:
                data["due_string"] = due_string
            if priority:
                data["priority"] = priority

            response = requests.post(
                f"{self.base_url}/tasks/{task_id}",
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 200:
                task = response.json()
                return {
                    "success": True,
                    "task": task,
                    "message": f"Task {task_id} updated"
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}