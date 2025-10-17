#!/usr/bin/env python3
"""
Sync roadmap to Trello board
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from tools.trello.trello_client import TaskFlowTrello


def sync_roadmap():
    """Sync roadmap tasks to Trello"""
    try:
        trello = TaskFlowTrello()
        
        # Test connection
        boards = trello.get_boards()
        print(f"Connected to Trello. Found {len(boards)} boards:")
        for board in boards:
            print(f"  - {board.name}")
        
        # TODO: Add roadmap.csv parsing and card creation
        print("\nRoadmap sync functionality - coming soon!")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    sync_roadmap()