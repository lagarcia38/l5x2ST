"""
Structured Text (ST) to L5X Converter

This module converts Structured Text code back to L5X XML format,
enabling round-trip conversion between L5X and ST.
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Optional, Set
import re
import logging

logger = logging.getLogger(__name__)


class ST2L5XConverter:
    """Converts Structured Text to L5X XML format."""
    
    def __init__(self):
        self.variables: Dict[str, Dict] = {}  # Variable declarations
        self.program_logic: List[str] = []  # ST statements
        self.function_blocks: Dict[str, Dict] = {}  # Function block instances
        self.data_types: Dict[str, str] = {}  # Data type mappings
        
    def parse_st_code(self, st_code: str) -> ET.Element:
        """Parse ST code and convert to L5X XML structure."""
        try:
            # Clear previous data
            self.variables.clear()
            self.program_logic.clear()
            self.function_blocks.clear()
            
            # Parse ST code
            self._parse_variable_declarations(st_code)
            self._parse_program_logic(st_code)
            
            # Generate L5X XML
            return self._generate_l5x_xml()
            
        except Exception as e:
            logger.error(f"Error parsing ST code: {e}")
            return self._create_error_xml(f"Failed to parse ST code - {e}")
    
    def _parse_variable_declarations(self, st_code: str):
        """Parse variable declarations from ST code (IEC 61131-3 compliant)."""
        self.user_types = set()
        var_match = re.search(r'VAR\s*(.*?)END_VAR', st_code, re.DOTALL | re.IGNORECASE)
        if not var_match:
            logger.warning("No VAR section found in ST code")
            return
        var_section = var_match.group(1)
        var_lines = var_section.split('\n')
        for line in var_lines:
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('(*'):
                continue
            # IEC 61131-3: identifier : type [ := initial_value ];
            # Array: identifier : ARRAY [lower..upper] OF type [ := initial_value ];
            array_match = re.match(r'(\w+)\s*:\s*ARRAY\s*\[(.*?)\]\s*OF\s*(\w+)\s*(?::=\s*([^;]+))?;', line, re.IGNORECASE)
            if array_match:
                var_name = array_match.group(1)
                array_range = array_match.group(2)
                base_type = array_match.group(3)
                initial_value = array_match.group(4)
                self.variables[var_name] = {
                    'name': var_name,
                    'type': base_type,
                    'array_range': array_range,
                    'scope': 'Local',
                    'initial_value': initial_value.strip() if initial_value else None,
                    'is_array': True
                }
                if base_type not in self._basic_types():
                    self.user_types.add(base_type)
                continue
            # Regular variable: identifier : type [ := initial_value ];
            var_match = re.match(r'(\w+)\s*:\s*([\w\[\]\.]+)\s*(?::=\s*([^;]+))?;', line)
            if var_match:
                var_name = var_match.group(1)
                var_type = var_match.group(2)
                initial_value = var_match.group(3)
                self.variables[var_name] = {
                    'name': var_name,
                    'type': var_type,
                    'scope': 'Local',
                    'initial_value': initial_value.strip() if initial_value else None,
                    'is_array': False
                }
                if var_type not in self._basic_types():
                    self.user_types.add(var_type)
                continue
            # Could add STRUCT, user-defined, etc. here
            logger.debug(f"Unparsed VAR line: {line}")
    
    def _parse_program_logic(self, st_code: str):
        """Parse program logic statements from ST code (IEC 61131-3 compliant)."""
        lines = []
        for line in st_code.split('\n'):
            # Remove single-line and multi-line comments
            line = re.sub(r'//.*$', '', line)
            line = re.sub(r'\(\*.*?\*\)', '', line, flags=re.DOTALL)
            line = line.strip()
            if line:
                lines.append(line)
        in_var_section = False
        for line in lines:
            if re.match(r'VAR\b', line, re.IGNORECASE):
                in_var_section = True
                continue
            elif re.match(r'END_VAR\b', line, re.IGNORECASE):
                in_var_section = False
                continue
            if not in_var_section and line and not line.startswith('//'):
                # Assignment: identifier := expression;
                assign_match = re.match(r'(\w+(?:\[.*?\])?)\s*:=\s*(.+);', line)
                if assign_match:
                    self.program_logic.append(line)
                    continue
                # Function/FB call: FBName(param1 := value1, ...);
                fb_call_match = re.match(r'(\w+)\s*\((.*)\);', line)
                if fb_call_match:
                    self.program_logic.append(line)
                    continue
                # Control structures (IF, FOR, WHILE, etc.)
                ctrl_match = re.match(r'(IF|ELSIF|ELSE|END_IF|FOR|END_FOR|WHILE|END_WHILE|CASE|END_CASE|REPEAT|END_REPEAT|EXIT|RETURN|CONTINUE|THEN|DO|TO|BY|OF|UNTIL|AND|OR|NOT|TRUE|FALSE)', line, re.IGNORECASE)
                if ctrl_match:
                    self.program_logic.append(line)
                    continue
                # Otherwise, just add the line
                self.program_logic.append(line)
    
    def _split_variables(self):
        """Split variables into controller-level and program-level tags by naming convention."""
        controller_tags = {}
        program_tags = {}
        for var_name, var_info in self.variables.items():
            # Simple convention: names starting with 'HMI_', 'Global_', or all uppercase are controller tags
            if var_name.startswith('HMI_') or var_name.startswith('Global_') or var_name.isupper():
                controller_tags[var_name] = var_info
            else:
                program_tags[var_name] = var_info
        return controller_tags, program_tags

    def _generate_l5x_xml(self) -> ET.Element:
        """Generate L5X XML structure from parsed ST code."""
        root = ET.Element('RSLogix5000Content')
        root.set('SchemaRevision', '1.0')
        root.set('SoftwareRevision', '20.01')
        root.set('TargetName', 'Generated_Controller')
        root.set('TargetType', 'Controller')
        root.set('ContainsContext', 'true')
        controller = ET.SubElement(root, 'Controller')
        controller.set('Name', 'Generated_Controller')
        controller.set('ProcessorType', '1756-L71')
        controller.set('MajorRev', '20')
        controller.set('MinorRev', '11')
        controller.set('TimeSlice', '20')
        controller.set('ShareUnusedTimeSlice', '1')
        controller.set('ProjectCreationDate', '2024-01-01T00:00:00')
        controller.set('LastModifiedDate', '2024-01-01T00:00:00')
        controller.set('SFCExecutionControl', 'CurrentActive')
        controller.set('SFCRestartPosition', 'MostRecent')
        controller.set('SFCLastScan', 'DontScan')
        controller.set('ProjectSN', '16#0000_0000')
        data_types = ET.SubElement(controller, 'DataTypes')
        self._add_basic_data_types(data_types)
        controller_tags, program_tags = self._split_variables()
        tags_elem = ET.SubElement(controller, 'Tags')
        for var_name, var_info in controller_tags.items():
            tag = ET.SubElement(tags_elem, 'Tag')
            tag.set('Name', var_name)
            tag.set('TagType', 'Base')
            tag.set('DataType', var_info['type'])
            tag.set('Scope', 'Controller')
            if var_info.get('is_array'):
                tag.set('Dimension', var_info['array_range'])
            desc = ET.SubElement(tag, 'Description')
            desc.text = 'Generated from ST conversion'
            # Add empty Data element to prevent "Decoded data content not found" errors
            data = ET.SubElement(tag, 'Data')
            data.set('Format', 'Decorated')
            data.set('Use', 'Context')
            value = ET.SubElement(data, 'Value')
            value.set('DataType', var_info['type'])
            if var_info.get('is_array'):
                value.set('Radix', 'Decimal')
                value.text = '0'
            else:
                value.set('Radix', 'Decimal')
                value.text = '0'
        programs = ET.SubElement(controller, 'Programs')
        main_program = self._create_main_program(program_tags)
        programs.append(main_program)
        tasks = ET.SubElement(controller, 'Tasks')
        main_task = self._create_main_task()
        tasks.append(main_task)
        return root
    
    def _add_basic_data_types(self, data_types_elem: ET.Element):
        """Add basic IEC data types to the L5X."""
        basic_types = [
            ('BOOL', 'BOOL'),
            ('SINT', 'SINT'),
            ('INT', 'INT'),
            ('DINT', 'DINT'),
            ('LINT', 'LINT'),
            ('USINT', 'USINT'),
            ('UINT', 'UINT'),
            ('UDINT', 'UDINT'),
            ('ULINT', 'ULINT'),
            ('REAL', 'REAL'),
            ('LREAL', 'LREAL'),
            ('TIME', 'TIME'),
            ('DATE', 'DATE'),
            ('TOD', 'TOD'),
            ('DT', 'DT'),
            ('STRING', 'STRING')
        ]
        for type_name, base_type in basic_types:
            data_type = ET.SubElement(data_types_elem, 'DataType')
            data_type.set('Name', type_name)
            data_type.set('Family', 'NoFamily')
            data_type.set('Class', 'User')
            base = ET.SubElement(data_type, 'Base')
            base.text = base_type
        # Add user-defined types as simple aliases (could be expanded)
        for user_type in getattr(self, 'user_types', set()):
            data_type = ET.SubElement(data_types_elem, 'DataType')
            data_type.set('Name', user_type)
            data_type.set('Family', 'NoFamily')
            data_type.set('Class', 'User')
            base = ET.SubElement(data_type, 'Base')
            base.text = 'DINT'  # Default base, could be improved
    
    def _create_main_program(self, program_tags) -> ET.Element:
        """Create the main program element with ST routine and program-level tags."""
        program = ET.Element('Program')
        program.set('Name', 'MainProgram')
        program.set('TestEdits', 'false')
        program.set('MainRoutineName', 'MainRoutine')
        program.set('TaskName', 'MainTask')
        program.set('ScheduledPrograms', '')
        program.set('UseAsFolder', 'false')
        program.set('ProgramNumber', '0')
        tags_elem = ET.SubElement(program, 'Tags')
        for var_name, var_info in program_tags.items():
            tag = ET.SubElement(tags_elem, 'Tag')
            tag.set('Name', var_name)
            tag.set('TagType', 'Base')
            tag.set('DataType', var_info['type'])
            tag.set('Scope', 'Program')
            if var_info.get('is_array'):
                tag.set('Dimension', var_info['array_range'])
            desc = ET.SubElement(tag, 'Description')
            desc.text = 'Generated from ST conversion'
            # Add empty Data element to prevent "Decoded data content not found" errors
            data = ET.SubElement(tag, 'Data')
            data.set('Format', 'Decorated')
            data.set('Use', 'Context')
            value = ET.SubElement(data, 'Value')
            value.set('DataType', var_info['type'])
            if var_info.get('is_array'):
                value.set('Radix', 'Decimal')
                value.text = '0'
            else:
                value.set('Radix', 'Decimal')
                value.text = '0'
        routines = ET.SubElement(program, 'Routines')
        main_routine = self._create_st_routine('MainRoutine')
        routines.append(main_routine)
        return program
    
    def _create_st_routine(self, routine_name: str) -> ET.Element:
        """Create an ST routine element."""
        routine = ET.Element('Routine')
        routine.set('Name', routine_name)
        routine.set('Type', 'ST')
        routine.set('TestEdits', 'false')
        routine.set('UseAsFolder', 'false')
        
        # Add ST content
        st_content = ET.SubElement(routine, 'STContent')
        st_content.set('Use', 'Context')
        
        # Add the ST code
        st_text = ET.SubElement(st_content, 'Text')
        st_text.text = self._format_st_code()
        
        return routine
    
    def _format_st_code(self) -> str:
        """Format the program logic as ST code."""
        if not self.program_logic:
            return "// No program logic found"
        
        # Join statements with proper formatting
        formatted_code = []
        for statement in self.program_logic:
            # Clean up the statement
            statement = statement.strip()
            if statement:
                # Ensure statements end with semicolon
                if not statement.endswith(';'):
                    statement += ';'
                formatted_code.append(statement)
        
        return '\n'.join(formatted_code)
    
    def _create_main_task(self) -> ET.Element:
        """Create the main task element."""
        task = ET.Element('Task')
        task.set('Name', 'MainTask')
        task.set('Type', 'CONTINUOUS')
        task.set('Priority', '10')
        task.set('Watchdog', '500')
        task.set('DisableUpdateOutputs', 'false')
        task.set('InhibitTask', 'false')
        
        # Add scheduled programs
        scheduled_programs = ET.SubElement(task, 'ScheduledPrograms')
        scheduled_program = ET.SubElement(scheduled_programs, 'ScheduledProgram')
        scheduled_program.set('Name', 'MainProgram')
        
        return task
    
    def _create_error_xml(self, error_message: str) -> ET.Element:
        """Create an error XML structure."""
        root = ET.Element('RSLogix5000Content')
        error_elem = ET.SubElement(root, 'Error')
        error_elem.text = error_message
        return root

    def convert_st_to_l5x(self, variables: str, program_logic: str) -> str:
        """Convert ST variables and program logic to L5X XML string."""
        # Combine variables and program logic
        st_code = f"{variables}\n\n{program_logic}"
        
        # Parse and convert
        xml_elem = self.parse_st_code(st_code)
        return ET.tostring(xml_elem, encoding='unicode', method='xml')

    def _basic_types(self):
        return {
            'BOOL', 'SINT', 'INT', 'DINT', 'LINT', 'USINT', 'UINT', 'UDINT', 'ULINT',
            'REAL', 'LREAL', 'TIME', 'DATE', 'TOD', 'DT', 'STRING'
        }


def convert_st_to_l5x(st_code: str) -> ET.Element:
    """Main function to convert ST code to L5X XML."""
    converter = ST2L5XConverter()
    return converter.parse_st_code(st_code)


def convert_st_to_l5x_string(st_code: str) -> str:
    """Convert ST code to L5X XML string."""
    xml_elem = convert_st_to_l5x(st_code)
    return ET.tostring(xml_elem, encoding='unicode', method='xml') 