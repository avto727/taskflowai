#!/usr/bin/env python3
"""
Test script for Todoist MCP tools
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.todoist_tools import TodoistMCP

load_dotenv()


def test_todoist_mcp():
    """Test Todoist MCP functions"""
    
    api_token = os.getenv("TODOIST_API_TOKEN")
    if not api_token:
        print("Error: TODOIST_API_TOKEN not found in .env")
        return
    
    print("Testing Todoist MCP...")
    todoist = TodoistMCP(api_token)
    
    # Test 1: Get projects
    print("\n1. Getting projects...")
    projects_result = todoist.get_projects()
    if projects_result["success"]:
        print(f"Found {projects_result['count']} projects:")
        for project in projects_result["projects"][:3]:
            print(f"  - {project['name']} (ID: {project['id']})")
    else:
        print(f"Error: {projects_result['error']}")
        return
    
    # Test 2: Get tasks
    print("\n2. Getting tasks...")
    tasks_result = todoist.get_tasks()
    if tasks_result["success"]:
        print(f"Found {tasks_result['count']} tasks:")
        for task in tasks_result["tasks"][:3]:
            print(f"  - {task['content']} (ID: {task['id']})")
    else:
        print(f"Error: {tasks_result['error']}")
    
    # Test 3: Create test task
    print("\n3. Creating test task...")
    create_result = todoist.create_task(
        content="MCP Test Task",
        due_string="today"
    )
    if create_result["success"]:
        task_id = create_result["task"]["id"]
        print(f"Created task: {create_result['task']['content']}")
        print(f"Task ID: {task_id}")
        
        # Test 4: Complete the test task
        print("\n4. Completing test task...")
        complete_result = todoist.complete_task(task_id)
        if complete_result["success"]:
            print("Task completed successfully!")
        else:
            print(f"Error completing task: {complete_result['error']}")
    else:
        print(f"Error creating task: {create_result['error']}")
    
    print("\nMCP tests completed!")


if __name__ == "__main__":
    test_todoist_mcp()