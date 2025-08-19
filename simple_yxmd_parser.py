#!/usr/bin/env python3
"""
Simple Alteryx .yxmd File Parser

A focused example showing how to read and parse key elements from an Alteryx workflow file.
"""

import xml.etree.ElementTree as ET
import sys


def parse_yxmd_file(file_path):
    """
    Parse an Alteryx .yxmd file and extract key information
    
    Args:
        file_path (str): Path to the .yxmd file
    
    Returns:
        dict: Parsed workflow data
    """
    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        print(f"✓ Successfully loaded: {file_path}")
        print(f"✓ Document version: {root.get('yxmdVer', 'Unknown')}")
        
        # Extract workflow information
        workflow_data = {
            'version': root.get('yxmdVer'),
            'tools': [],
            'connections': []
        }
        
        # Parse nodes (tools)
        nodes = root.find('Nodes')
        if nodes is not None:
            for node in nodes.findall('Node'):
                tool_id = node.get('ToolID')
                
                # Get plugin information
                gui_settings = node.find('GuiSettings')
                plugin = gui_settings.get('Plugin') if gui_settings is not None else 'Unknown'
                
                # Get position
                position = gui_settings.find('Position') if gui_settings is not None else None
                pos_x = position.get('x') if position is not None else '0'
                pos_y = position.get('y') if position is not None else '0'
                
                # Get file paths (for input/output tools)
                file_path = None
                properties = node.find('Properties')
                if properties is not None:
                    config = properties.find('Configuration')
                    if config is not None:
                        file_elem = config.find('File')
                        if file_elem is not None:
                            file_path = file_elem.text or file_elem.get('OutputFileName', '')
                
                tool_info = {
                    'id': tool_id,
                    'type': plugin.split('.')[-1] if plugin else 'Unknown',
                    'plugin': plugin,
                    'position': {'x': pos_x, 'y': pos_y},
                    'file': file_path
                }
                
                workflow_data['tools'].append(tool_info)
        
        # Parse connections
        connections = root.find('Connections')
        if connections is not None:
            for connection in connections.findall('Connection'):
                origin = connection.find('Origin')
                destination = connection.find('Destination')
                
                if origin is not None and destination is not None:
                    conn_info = {
                        'from_tool': origin.get('ToolID'),
                        'from_output': origin.get('Connection'),
                        'to_tool': destination.get('ToolID'),
                        'to_input': destination.get('Connection')
                    }
                    workflow_data['connections'].append(conn_info)
        
        return workflow_data
        
    except ET.ParseError as e:
        print(f"✗ XML parsing error: {e}")
        return None
    except FileNotFoundError:
        print(f"✗ File not found: {file_path}")
        return None
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None


def print_workflow_summary(workflow_data):
    """Print a summary of the parsed workflow"""
    if not workflow_data:
        print("No workflow data to display")
        return
    
    print("\n" + "="*50)
    print("WORKFLOW SUMMARY")
    print("="*50)
    
    print(f"Version: {workflow_data['version']}")
    print(f"Tools: {len(workflow_data['tools'])}")
    print(f"Connections: {len(workflow_data['connections'])}")
    
    print("\nTOOLS:")
    for i, tool in enumerate(workflow_data['tools'], 1):
        file_info = f" -> {tool['file']}" if tool['file'] else ""
        print(f"  {i}. [{tool['id']}] {tool['type']} at ({tool['position']['x']}, {tool['position']['y']}){file_info}")
    
    print("\nCONNECTIONS:")
    for i, conn in enumerate(workflow_data['connections'], 1):
        print(f"  {i}. Tool {conn['from_tool']} ({conn['from_output']}) -> Tool {conn['to_tool']} ({conn['to_input']})")
    
    print("="*50)


def main():
    """Main function"""
    # Use the sample file we created
    yxmd_file = "/workspace/sample_workflow.yxmd"
    
    print("Alteryx .yxmd File Parser")
    print("-" * 30)
    
    # Parse the workflow
    workflow_data = parse_yxmd_file(yxmd_file)
    
    if workflow_data:
        # Print summary
        print_workflow_summary(workflow_data)
        
        # Example: Show detailed tool information
        print("\nDETAILED TOOL ANALYSIS:")
        print("-" * 30)
        
        for tool in workflow_data['tools']:
            print(f"\nTool ID: {tool['id']}")
            print(f"  Type: {tool['type']}")
            print(f"  Full Plugin: {tool['plugin']}")
            print(f"  Position: ({tool['position']['x']}, {tool['position']['y']})")
            if tool['file']:
                print(f"  File: {tool['file']}")
            
            # Identify tool purpose
            if 'Input' in tool['type']:
                print(f"  Purpose: Data Input Tool")
            elif 'Output' in tool['type']:
                print(f"  Purpose: Data Output Tool")
            elif 'Select' in tool['type']:
                print(f"  Purpose: Field Selection/Transformation Tool")
            else:
                print(f"  Purpose: Processing Tool")


if __name__ == "__main__":
    main()
