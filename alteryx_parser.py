#!/usr/bin/env python3
"""
Alteryx .yxmd File Parser

This script reads and parses Alteryx workflow files (.yxmd) which are XML-based files
containing workflow definitions, tool configurations, and connections.
"""

import xml.etree.ElementTree as ET
import json
from typing import Dict, List, Any
import os


class AlteryxWorkflowParser:
    """Parser for Alteryx .yxmd workflow files"""
    
    def __init__(self, file_path: str):
        """
        Initialize the parser with a .yxmd file path
        
        Args:
            file_path (str): Path to the .yxmd file
        """
        self.file_path = file_path
        self.root = None
        self.workflow_data = {}
        
    def load_file(self):
        """Load and parse the XML file"""
        try:
            tree = ET.parse(self.file_path)
            self.root = tree.getroot()
            print(f"Successfully loaded {self.file_path}")
            return True
        except ET.ParseError as e:
            print(f"Error parsing XML file: {e}")
            return False
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """Extract basic workflow information"""
        workflow_info = {}
        
        if self.root is not None:
            # Get document version
            workflow_info['version'] = self.root.get('yxmdVer', 'Unknown')
            
            # Get metadata from Properties/MetaInfo
            meta_info = self.root.find('.//Properties/MetaInfo')
            if meta_info is not None:
                workflow_info['name'] = self._get_element_text(meta_info, 'Name')
                workflow_info['description'] = self._get_element_text(meta_info, 'Description')
                workflow_info['author'] = self._get_element_text(meta_info, 'Author')
                workflow_info['company'] = self._get_element_text(meta_info, 'Company')
                workflow_info['copyright'] = self._get_element_text(meta_info, 'Copyright')
                
                # Additional metadata fields
                workflow_info['root_tool_name'] = self._get_element_text(meta_info, 'RootToolName')
                workflow_info['tool_version'] = self._get_element_text(meta_info, 'ToolVersion')
                workflow_info['category_name'] = self._get_element_text(meta_info, 'CategoryName')
                workflow_info['search_tags'] = self._get_element_text(meta_info, 'SearchTags')
                
                # Handle attributes
                name_is_filename = meta_info.find('NameIsFileName')
                if name_is_filename is not None:
                    workflow_info['name_is_filename'] = name_is_filename.get('value')
                
                tool_in_db = meta_info.find('ToolInDb')
                if tool_in_db is not None:
                    workflow_info['tool_in_db'] = tool_in_db.get('value')
                
                # Handle DescriptionLink with attributes
                desc_link = meta_info.find('DescriptionLink')
                if desc_link is not None:
                    workflow_info['description_link'] = {
                        'actual': desc_link.get('actual', ''),
                        'displayed': desc_link.get('displayed', ''),
                        'text': desc_link.text
                    }
        
        return workflow_info
    
    def get_nodes(self) -> List[Dict[str, Any]]:
        """Extract all nodes (tools) from the workflow"""
        nodes = []
        
        nodes_element = self.root.find('Nodes')
        if nodes_element is not None:
            for node in nodes_element.findall('Node'):
                node_data = {
                    'tool_id': node.get('ToolID'),
                    'plugin': None,
                    'position': {},
                    'configuration': {},
                    'annotation': {},
                    'engine_settings': {}
                }
                
                # Get GUI settings (plugin and position)
                gui_settings = node.find('GuiSettings')
                if gui_settings is not None:
                    node_data['plugin'] = gui_settings.get('Plugin')
                    position = gui_settings.find('Position')
                    if position is not None:
                        node_data['position'] = {
                            'x': position.get('x'),
                            'y': position.get('y')
                        }
                
                # Get properties and configuration
                properties = node.find('Properties')
                if properties is not None:
                    config = properties.find('Configuration')
                    if config is not None:
                        node_data['configuration'] = self._xml_to_dict(config)
                    
                    annotation = properties.find('Annotation')
                    if annotation is not None:
                        node_data['annotation'] = self._xml_to_dict(annotation)
                
                # Get engine settings
                engine_settings = node.find('EngineSettings')
                if engine_settings is not None:
                    node_data['engine_settings'] = {
                        'dll': engine_settings.get('EngineDll'),
                        'entry_point': engine_settings.get('EngineDllEntryPoint')
                    }
                    
                    # For Python-based tools, the entry point might be a file path
                    if node_data['engine_settings']['dll'] == 'Python':
                        node_data['engine_settings']['type'] = 'Python'
                    else:
                        node_data['engine_settings']['type'] = 'DLL'
                else:
                    # Some tools (like TextBox) don't have engine settings - they're GUI-only
                    node_data['engine_settings'] = {'type': 'GUI'}
                
                nodes.append(node_data)
        
        return nodes
    
    def get_connections(self) -> List[Dict[str, Any]]:
        """Extract all connections between nodes"""
        connections = []
        
        connections_element = self.root.find('Connections')
        if connections_element is not None:
            for connection in connections_element.findall('Connection'):
                origin = connection.find('Origin')
                destination = connection.find('Destination')
                
                if origin is not None and destination is not None:
                    connection_data = {
                        'origin': {
                            'tool_id': origin.get('ToolID'),
                            'connection': origin.get('Connection')
                        },
                        'destination': {
                            'tool_id': destination.get('ToolID'),
                            'connection': destination.get('Connection')
                        }
                    }
                    connections.append(connection_data)
        
        return connections
    
    def get_workflow_properties(self) -> Dict[str, Any]:
        """Extract workflow-level properties"""
        properties = {}
        
        props_element = self.root.find('Properties')
        if props_element is not None:
            # Get various workflow settings
            memory = props_element.find('Memory')
            if memory is not None:
                properties['memory_default'] = memory.get('default')
            
            global_limit = props_element.find('GlobalRecordLimit')
            if global_limit is not None:
                properties['global_record_limit'] = global_limit.get('value')
            
            zoom_level = props_element.find('ZoomLevel')
            if zoom_level is not None:
                properties['zoom_level'] = zoom_level.get('value')
            
            layout_type = props_element.find('LayoutType')
            if layout_type is not None:
                properties['layout_type'] = layout_type.text
        
        return properties
    
    def parse_workflow(self) -> Dict[str, Any]:
        """Parse the entire workflow and return structured data"""
        if not self.load_file():
            return {}
        
        self.workflow_data = {
            'workflow_info': self.get_workflow_info(),
            'nodes': self.get_nodes(),
            'connections': self.get_connections(),
            'properties': self.get_workflow_properties()
        }
        
        return self.workflow_data
    
    def _get_element_text(self, parent, tag_name):
        """Helper method to safely get element text"""
        element = parent.find(tag_name)
        return element.text if element is not None else None
    
    def _extract_plugin_name(self, plugin_string):
        """Extract a readable plugin name from the plugin string"""
        if not plugin_string:
            return 'Unknown'
        
        # Check if this looks like a standard Alteryx plugin (has multiple dots and follows naming pattern)
        if plugin_string.count('.') >= 2 and any(prefix in plugin_string for prefix in ['AlteryxBasePluginsGui', 'AlteryxGuiToolkit', 'AlteryxConnectorGui']):
            # For standard Alteryx plugins with dots
            parts = plugin_string.split('.')
            return parts[-1]
        else:
            # For custom plugins (like SKOPOSSFTPDownload_v1.0), return the full name
            return plugin_string
    
    def _xml_to_dict(self, element):
        """Convert XML element to dictionary recursively"""
        result = {}
        
        # Add attributes
        if element.attrib:
            result.update(element.attrib)
        
        # Add text content if present
        if element.text and element.text.strip():
            if len(element) == 0:  # No child elements
                return element.text.strip()
            else:
                result['_text'] = element.text.strip()
        
        # Add child elements
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                # Handle multiple elements with same tag
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result
    
    def print_summary(self):
        """Print a summary of the parsed workflow"""
        if not self.workflow_data:
            print("No workflow data available. Please parse the workflow first.")
            return
        
        print("\n" + "="*60)
        print("ALTERYX WORKFLOW SUMMARY")
        print("="*60)
        
        # Workflow info
        info = self.workflow_data['workflow_info']
        print(f"Name: {info.get('name', 'N/A')}")
        print(f"Version: {info.get('version', 'N/A')}")
        print(f"Author: {info.get('author', 'N/A')}")
        print(f"Company: {info.get('company', 'N/A')}")
        print(f"Description: {info.get('description', 'N/A')}")
        
        # Nodes summary
        nodes = self.workflow_data['nodes']
        print(f"\nNodes: {len(nodes)} tools")
        for i, node in enumerate(nodes, 1):
            plugin_name = self._extract_plugin_name(node['plugin']) if node['plugin'] else 'Unknown'
            print(f"  {i}. Tool ID {node['tool_id']}: {plugin_name} at ({node['position'].get('x', 'N/A')}, {node['position'].get('y', 'N/A')})")
        
        # Connections summary
        connections = self.workflow_data['connections']
        print(f"\nConnections: {len(connections)} links")
        for i, conn in enumerate(connections, 1):
            print(f"  {i}. Tool {conn['origin']['tool_id']} -> Tool {conn['destination']['tool_id']}")
        
        print("="*60)
    
    def save_to_json(self, output_file: str):
        """Save parsed data to JSON file"""
        if not self.workflow_data:
            print("No workflow data to save. Please parse the workflow first.")
            return
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.workflow_data, f, indent=2, ensure_ascii=False)
            print(f"Workflow data saved to {output_file}")
        except Exception as e:
            print(f"Error saving to JSON: {e}")


def main():
    """Main function to demonstrate the parser"""
    # Example usage
    yxmd_file = "/workspace/alteryx-parser/sample_workflow.yxmd"
    
    if not os.path.exists(yxmd_file):
        print(f"File {yxmd_file} not found!")
        return
    
    # Create parser instance
    parser = AlteryxWorkflowParser(yxmd_file)
    
    # Parse the workflow
    workflow_data = parser.parse_workflow()
    
    if workflow_data:
        # Print summary
        parser.print_summary()
        
        # Save to JSON
        parser.save_to_json("/workspace/alteryx-parser/parsed_workflow.json")
        
        # Example: Access specific data
        print("\n" + "="*60)
        print("DETAILED NODE INFORMATION")
        print("="*60)
        
        for node in workflow_data['nodes']:
            print(f"\nTool ID: {node['tool_id']}")
            print(f"Plugin: {node['plugin']}")
            print(f"Position: {node['position']}")
            
            # Show configuration details for input/output tools
            if 'File' in node['configuration']:
                file_config = node['configuration']['File']
                if isinstance(file_config, dict):
                    print(f"File: {file_config.get('_text', 'N/A')}")
                else:
                    print(f"File: {file_config}")


if __name__ == "__main__":
    main()
