
# Alteryx .yxmd File Parser

This repository contains Python scripts to read and parse Alteryx workflow files (.yxmd). Alteryx workflows are stored as XML files containing tool configurations, connections, and metadata.

## Overview

Alteryx is a self-service data analytics platform that uses a drag-and-drop interface to create workflows. These workflows are saved as `.yxmd` files, which are XML-based files containing:

- **Nodes**: Individual tools/components in the workflow
- **Connections**: Data flow between tools
- **Properties**: Workflow-level settings and metadata
- **Configurations**: Tool-specific settings and parameters

## Files in this Repository

### 1. `sample_workflow.yxmd`
A sample Alteryx workflow file that demonstrates a simple data processing pipeline:
- **Input Tool**: Reads data from a CSV file
- **Select Tool**: Selects and transforms fields
- **Output Tool**: Writes processed data to a CSV file

### 2. `alteryx_parser.py` (Full-Featured Parser)
A comprehensive parser class that extracts all workflow information:

**Features:**
- Complete workflow metadata extraction
- Detailed node/tool configuration parsing
- Connection mapping between tools
- JSON export functionality
- Structured data output

**Usage:**
```python
from alteryx_parser import AlteryxWorkflowParser

# Create parser instance
parser = AlteryxWorkflowParser("path/to/workflow.yxmd")

# Parse the workflow
workflow_data = parser.parse_workflow()

# Print summary
parser.print_summary()

# Save to JSON
parser.save_to_json("output.json")
```

### 3. `simple_yxmd_parser.py` (Focused Parser)
A streamlined parser that focuses on essential workflow information:

**Features:**
- Tool identification and positioning
- Connection mapping
- File path extraction for I/O tools
- Clean, readable output format

**Usage:**
```bash
python3 simple_yxmd_parser.py
```

### 4. `minimal_yxmd_reader.py` (Basic Reader)
The simplest possible example showing core XML parsing:

**Features:**
- Basic workflow statistics
- Tool counting and identification
- Minimal code for learning purposes

**Usage:**
```bash
python3 minimal_yxmd_reader.py
```

### 5. `parsed_workflow.json`
Example JSON output showing the structured data extracted from the sample workflow.

## Quick Start

1. **Run the basic reader:**
   ```bash
   python3 minimal_yxmd_reader.py
   ```

2. **Run the focused parser:**
   ```bash
   python3 simple_yxmd_parser.py
   ```

3. **Run the full parser:**
   ```bash
   python3 alteryx_parser.py
   ```

## Understanding .yxmd File Structure

Alteryx .yxmd files are XML documents with this basic structure:

```xml
<AlteryxDocument yxmdVer="2023.1">
  <Nodes>
    <Node ToolID="1">
      <GuiSettings Plugin="...">
        <Position x="54" y="162" />
      </GuiSettings>
      <Properties>
        <Configuration>
          <!-- Tool-specific settings -->
        </Configuration>
      </Properties>
    </Node>
  </Nodes>
  <Connections>
    <Connection>
      <Origin ToolID="1" Connection="Output" />
      <Destination ToolID="2" Connection="Input" />
    </Connection>
  </Connections>
  <Properties>
    <!-- Workflow-level settings -->
  </Properties>
</AlteryxDocument>
```

## Key Components Explained

### Nodes (Tools)
Each tool in the workflow is represented as a `<Node>` element containing:
- **ToolID**: Unique identifier for the tool
- **Plugin**: The specific Alteryx tool type
- **Position**: X,Y coordinates on the canvas
- **Configuration**: Tool-specific settings
- **Annotation**: User-added notes and labels

### Connections
Data flow between tools is defined by `<Connection>` elements:
- **Origin**: Source tool and output connection
- **Destination**: Target tool and input connection

### Common Tool Types
- **DbFileInput**: Read data from files (CSV, Excel, etc.)
- **DbFileOutput**: Write data to files
- **AlteryxSelect**: Select, rename, and change field types
- **Filter**: Filter records based on conditions
- **Join**: Join data from multiple sources
- **Formula**: Create calculated fields
- **Summarize**: Group and aggregate data

## Extending the Parser

To add support for specific tool configurations:

```python
def parse_specific_tool(node):
    """Parse configuration for a specific tool type"""
    config = node.find('Properties/Configuration')
    if config is not None:
        # Extract tool-specific settings
        setting = config.find('SpecificSetting')
        return setting.text if setting is not None else None
    return None
```

## Requirements

- Python 3.6+
- Standard library only (xml.etree.ElementTree, json, os)

## Sample Output

```
WORKFLOW SUMMARY
==================================================
Version: 2023.1
Tools: 3
Connections: 2

TOOLS:
  1. [1] DbFileInput at (54, 162) -> C:\Users\sample\data.csv
  2. [2] AlteryxSelect at (186, 162)
  3. [3] DbFileOutput at (318, 162) -> C:\Users\sample\output.csv

CONNECTIONS:
  1. Tool 1 (Output) -> Tool 2 (Input)
  2. Tool 2 (Output) -> Tool 3 (Input)
```

## Use Cases

- **Workflow Documentation**: Generate documentation from existing workflows
- **Migration Analysis**: Understand workflow dependencies before migration
- **Audit and Compliance**: Extract data lineage and processing steps
- **Automation**: Programmatically analyze and modify workflows
- **Integration**: Connect Alteryx workflows with other systems

## References

- [Alteryx Documentation](https://help.alteryx.com/?lang=en)
- [Alteryx File Types](https://help.alteryx.com/current/en/designer/file-types-support/alteryx-file-types.html)
- [XML Processing in Python](https://docs.python.org/3/library/xml.etree.elementtree.html)

## License

This code is provided as-is for educational and demonstration purposes.

