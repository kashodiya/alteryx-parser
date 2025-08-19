#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced Alteryx parser capabilities
"""

from alteryx_parser import AlteryxWorkflowParser
import json
import os

def test_parser_with_file(file_path, description):
    """Test the parser with a specific file"""
    print(f"\n{'='*60}")
    print(f"TESTING: {description}")
    print(f"File: {file_path}")
    print('='*60)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None
    
    parser = AlteryxWorkflowParser(file_path)
    workflow_data = parser.parse_workflow()
    
    if not workflow_data:
        print("❌ Failed to parse workflow")
        return None
    
    print("✅ Successfully parsed workflow")
    
    # Print enhanced workflow info
    info = workflow_data['workflow_info']
    print(f"\n📋 Workflow Information:")
    for key, value in info.items():
        if value is not None and value != '':
            print(f"  {key}: {value}")
    
    # Print node statistics
    nodes = workflow_data['nodes']
    print(f"\n🔧 Node Statistics:")
    print(f"  Total nodes: {len(nodes)}")
    
    # Engine type distribution
    engine_types = {}
    plugin_types = {}
    
    for node in nodes:
        # Count engine types
        engine_type = node['engine_settings'].get('type', 'Unknown')
        engine_types[engine_type] = engine_types.get(engine_type, 0) + 1
        
        # Count plugin types
        plugin = node.get('plugin', 'Unknown')
        if plugin.startswith('AlteryxBasePluginsGui'):
            plugin_category = 'Standard Alteryx'
        elif plugin.startswith('AlteryxGuiToolkit'):
            plugin_category = 'GUI Toolkit'
        elif plugin.startswith('AlteryxConnectorGui'):
            plugin_category = 'Connector'
        else:
            plugin_category = 'Custom/Third-party'
        
        plugin_types[plugin_category] = plugin_types.get(plugin_category, 0) + 1
    
    print(f"  Engine types:")
    for engine_type, count in engine_types.items():
        print(f"    {engine_type}: {count}")
    
    print(f"  Plugin categories:")
    for plugin_category, count in plugin_types.items():
        print(f"    {plugin_category}: {count}")
    
    # Print connections
    connections = workflow_data['connections']
    print(f"\n🔗 Connections: {len(connections)}")
    
    return workflow_data

def main():
    """Main test function"""
    print("🚀 Enhanced Alteryx Parser Test Suite")
    print("="*60)
    
    # Test files
    test_files = [
        ("/workspace/alteryx-parser/sample_workflow.yxmd", "Original Sample Workflow"),
        ("/tmp/sftp-tools/Examples/SFTP Tools Examples - Download.yxmd", "SFTP Tools Example")
    ]
    
    results = []
    
    for file_path, description in test_files:
        result = test_parser_with_file(file_path, description)
        if result:
            results.append((description, result))
    
    # Summary comparison
    if len(results) >= 2:
        print(f"\n{'='*60}")
        print("📊 COMPARISON SUMMARY")
        print('='*60)
        
        for desc, data in results:
            print(f"\n{desc}:")
            print(f"  Version: {data['workflow_info'].get('version', 'N/A')}")
            print(f"  Nodes: {len(data['nodes'])}")
            print(f"  Connections: {len(data['connections'])}")
            
            # Count custom tools
            custom_tools = sum(1 for node in data['nodes'] 
                             if not any(prefix in node.get('plugin', '') 
                                      for prefix in ['AlteryxBasePluginsGui', 'AlteryxGuiToolkit', 'AlteryxConnectorGui']))
            print(f"  Custom tools: {custom_tools}")
    
    print(f"\n✅ Test completed successfully!")

if __name__ == "__main__":
    main()
