
#!/usr/bin/env python3
"""
Minimal Alteryx .yxmd Reader

This is the simplest possible example of reading an Alteryx .yxmd file.
"""

import xml.etree.ElementTree as ET

def read_yxmd_basic(file_path):
    """Basic .yxmd file reader - extracts essential information"""
    
    # Parse the XML
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    print(f"File: {file_path}")
    print(f"Alteryx Version: {root.get('yxmdVer')}")
    
    # Count tools
    nodes = root.find('Nodes')
    tool_count = len(nodes.findall('Node')) if nodes is not None else 0
    print(f"Number of Tools: {tool_count}")
    
    # Count connections
    connections = root.find('Connections')
    conn_count = len(connections.findall('Connection')) if connections is not None else 0
    print(f"Number of Connections: {conn_count}")
    
    # List tools with their types
    print("\nTools in workflow:")
    if nodes is not None:
        for i, node in enumerate(nodes.findall('Node'), 1):
            tool_id = node.get('ToolID')
            gui_settings = node.find('GuiSettings')
            plugin = gui_settings.get('Plugin') if gui_settings is not None else 'Unknown'
            tool_type = plugin.split('.')[-1] if plugin else 'Unknown'
            print(f"  {i}. Tool {tool_id}: {tool_type}")

# Example usage
if __name__ == "__main__":
    read_yxmd_basic("/workspace/sample_workflow.yxmd")
