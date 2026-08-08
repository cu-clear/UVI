"""
Presentation module for UVI package.

This module provides standalone presentation-layer formatting and HTML generation
functions that are used in templates but not tied to Flask or any specific web framework.
"""

import json
import random
import hashlib
from typing import Dict, List, Any, Union, Optional


class Presentation:
    """
    A standalone class for presentation-layer formatting and HTML generation
    functions that are used in templates but not tied to Flask.
    """
    
    def __init__(self):
        """
        Initialize Presentation formatter.
        """
        # Initialize any required state for presentation formatting
        self._color_cache = {}
        
    def generate_class_hierarchy_html(self, class_id: str, uvi_instance) -> str:
        """
        Generate HTML representation of class hierarchy.
        
        Args:
            class_id (str): VerbNet class ID
            uvi_instance: UVI instance for data access
            
        Returns:
            str: HTML string for class hierarchy
        """
        try:
            hierarchy = uvi_instance.get_full_class_hierarchy(class_id)
            if not hierarchy:
                return f"<div class='alert alert-warning'>No hierarchy found for class {class_id}</div>"
            
            html_parts = []
            html_parts.append("<div class='class-hierarchy'>")
            
            # Generate hierarchical HTML structure
            def render_class_level(class_data, level=0):
                indent = "  " * level
                class_name = class_data.get('class_id', 'Unknown')
                html = f"{indent}<div class='hierarchy-level-{level}'>\n"
                html += f"{indent}  <span class='class-name'>{class_name}</span>\n"
                
                # Add subclasses if they exist
                subclasses = class_data.get('subclasses', [])
                if subclasses:
                    html += f"{indent}  <div class='subclasses'>\n"
                    for subclass in subclasses:
                        html += render_class_level(subclass, level + 1)
                    html += f"{indent}  </div>\n"
                
                html += f"{indent}</div>\n"
                return html
            
            html_parts.append(render_class_level(hierarchy))
            html_parts.append("</div>")
            
            return "".join(html_parts)
            
        except Exception as e:
            return f"<div class='alert alert-danger'>Error generating hierarchy: {str(e)}</div>"
    
    def generate_sanitized_class_html(self, vn_class_id: str, uvi_instance) -> str:
        """
        Generate sanitized VerbNet class HTML.
        
        Args:
            vn_class_id (str): VerbNet class ID
            uvi_instance: UVI instance for data access
            
        Returns:
            str: Sanitized HTML representation
        """
        try:
            class_data = uvi_instance.get_verbnet_class(vn_class_id, 
                                                      include_subclasses=True, 
                                                      include_mappings=True)
            if not class_data:
                return f"<div class='alert alert-warning'>No data found for class {vn_class_id}</div>"
            
            html_parts = []
            html_parts.append(f"<div class='verbnet-class' data-class-id='{vn_class_id}'>")
            
            # Class header
            html_parts.append(f"<h3 class='class-header'>{vn_class_id}</h3>")
            
            # Members section
            members = class_data.get('members', [])
            if members:
                html_parts.append("<div class='members-section'>")
                html_parts.append("<h4>Members:</h4>")
                html_parts.append("<ul class='member-list'>")
                for member in members[:10]:  # Limit display for sanitized view
                    member_name = self._sanitize_html(str(member))
                    html_parts.append(f"<li>{member_name}</li>")
                if len(members) > 10:
                    html_parts.append(f"<li><em>... and {len(members) - 10} more</em></li>")
                html_parts.append("</ul>")
                html_parts.append("</div>")
            
            # Frames section (simplified)
            frames = class_data.get('frames', [])
            if frames:
                html_parts.append("<div class='frames-section'>")
                html_parts.append(f"<h4>Frames ({len(frames)}):</h4>")
                html_parts.append("<ul class='frame-list'>")
                for i, frame in enumerate(frames[:3]):  # Show only first 3 frames
                    frame_desc = self._sanitize_html(frame.get('description', f'Frame {i+1}'))
                    html_parts.append(f"<li>{frame_desc}</li>")
                if len(frames) > 3:
                    html_parts.append(f"<li><em>... and {len(frames) - 3} more frames</em></li>")
                html_parts.append("</ul>")
                html_parts.append("</div>")
            
            html_parts.append("</div>")
            
            return "".join(html_parts)
            
        except Exception as e:
            return f"<div class='alert alert-danger'>Error generating class HTML: {str(e)}</div>"
    
    def format_framenet_definition(self, frame: Dict, markup: str, popover: bool = False) -> str:
        """
        Format FrameNet frame definition with HTML markup.
        
        Args:
            frame (dict): FrameNet frame data
            markup (str): Definition markup
            popover (bool): Include popover functionality
            
        Returns:
            str: Formatted HTML definition
        """
        try:
            if not markup:
                return "<span class='no-definition'>No definition available</span>"
            
            # Basic HTML sanitization and formatting
            formatted_markup = self._sanitize_html(markup)
            
            # Wrap in appropriate container
            css_class = "framenet-definition"
            if popover:
                css_class += " popover-trigger"
                unique_id = self.generate_unique_id()
                formatted_markup = f"""
                <span class="{css_class}" 
                      data-toggle="popover" 
                      data-content="{self._sanitize_html(frame.get('name', 'Unknown'))}"
                      id="{unique_id}">
                    {formatted_markup}
                </span>
                """
            else:
                formatted_markup = f'<span class="{css_class}">{formatted_markup}</span>'
            
            return formatted_markup
            
        except Exception as e:
            return f"<span class='error'>Error formatting definition: {str(e)}</span>"
    
    def format_propbank_example(self, example: Dict) -> Dict:
        """
        Format PropBank example with colored arguments.
        
        Args:
            example (dict): PropBank example data
            
        Returns:
            dict: Example with colored HTML markup
        """
        try:
            if not example:
                return {"text": "No example available", "args": []}
            
            formatted_example = example.copy()
            text = example.get('text', '')
            args = example.get('args', [])
            
            # Generate colors for arguments
            arg_colors = self.generate_element_colors([f"ARG{i}" for i in range(len(args))])
            
            # Apply coloring to text
            colored_text = text
            for i, arg in enumerate(args):
                arg_label = f"ARG{i}"
                color = arg_colors.get(arg_label, "#666666")
                arg_text = arg.get('text', '')
                if arg_text and arg_text in colored_text:
                    colored_text = colored_text.replace(
                        arg_text,
                        f'<span class="propbank-arg" style="color: {color}; font-weight: bold;">{arg_text}</span>'
                    )
            
            formatted_example['colored_text'] = colored_text
            formatted_example['arg_colors'] = arg_colors
            
            return formatted_example
            
        except Exception as e:
            return {"text": f"Error formatting example: {str(e)}", "args": []}
    
    def format_themrole_display(self, themrole_data: Dict) -> str:
        """
        Format thematic role for display.
        
        Args:
            themrole_data (dict): Thematic role data
            
        Returns:
            str: Formatted display string
        """
        try:
            if not themrole_data:
                return "<span class='no-data'>No thematic role data</span>"
            
            role_name = themrole_data.get('name', 'Unknown')
            role_type = themrole_data.get('type', '')
            selectional_restrictions = themrole_data.get('selectional_restrictions', [])
            
            parts = []
            parts.append(f"<span class='themrole-name'>{self._sanitize_html(role_name)}</span>")
            
            if role_type:
                parts.append(f"<span class='themrole-type'>({self._sanitize_html(role_type)})</span>")
            
            if selectional_restrictions:
                restr_strs = [self._sanitize_html(str(r)) for r in selectional_restrictions[:3]]
                parts.append(f"<span class='themrole-restrictions'>[{', '.join(restr_strs)}]</span>")
            
            return " ".join(parts)
            
        except Exception as e:
            return f"<span class='error'>Error formatting thematic role: {str(e)}</span>"
    
    def format_predicate_display(self, predicate_data: Dict) -> str:
        """
        Format predicate for display.
        
        Args:
            predicate_data (dict): Predicate data
            
        Returns:
            str: Formatted display string
        """
        try:
            if not predicate_data:
                return "<span class='no-data'>No predicate data</span>"
            
            pred_name = predicate_data.get('name', 'Unknown')
            pred_args = predicate_data.get('args', [])
            pred_description = predicate_data.get('description', '')
            
            parts = []
            parts.append(f"<span class='predicate-name'>{self._sanitize_html(pred_name)}</span>")
            
            if pred_args:
                args_str = ", ".join([self._sanitize_html(str(arg)) for arg in pred_args])
                parts.append(f"<span class='predicate-args'>({args_str})</span>")
            
            if pred_description:
                desc_short = pred_description[:100] + "..." if len(pred_description) > 100 else pred_description
                parts.append(f"<span class='predicate-desc' title='{self._sanitize_html(pred_description)}'>{self._sanitize_html(desc_short)}</span>")
            
            return " ".join(parts)
            
        except Exception as e:
            return f"<span class='error'>Error formatting predicate: {str(e)}</span>"
    
    def format_restriction_display(self, restriction_data: Dict, restriction_type: str) -> str:
        """
        Format selectional or syntactic restriction for display.
        
        Args:
            restriction_data (dict): Restriction data
            restriction_type (str): 'selectional' or 'syntactic'
            
        Returns:
            str: Formatted display string
        """
        try:
            if not restriction_data:
                return f"<span class='no-data'>No {restriction_type} restriction data</span>"
            
            restr_value = restriction_data.get('value', 'Unknown')
            restr_logic = restriction_data.get('logic', '')
            restr_type = restriction_data.get('type', '')
            
            css_class = f"{restriction_type}-restriction"
            parts = []
            
            parts.append(f"<span class='{css_class}-value'>{self._sanitize_html(restr_value)}</span>")
            
            if restr_logic:
                parts.append(f"<span class='{css_class}-logic'>({self._sanitize_html(restr_logic)})</span>")
            
            if restr_type:
                parts.append(f"<span class='{css_class}-type'>[{self._sanitize_html(restr_type)}]</span>")
            
            return f"<span class='{css_class}'>{' '.join(parts)}</span>"
            
        except Exception as e:
            return f"<span class='error'>Error formatting {restriction_type} restriction: {str(e)}</span>"
    
    def generate_unique_id(self) -> str:
        """
        Generate unique identifier for HTML elements.
        
        Returns:
            str: Unique 16-character hex string
        """
        return hashlib.md5(str(random.random()).encode()).hexdigest()[:16]
    
    def json_to_display(self, elements: Union[List, Dict]) -> str:
        """
        Convert parsed corpus elements to display-ready JSON.
        
        Args:
            elements: Parsed corpus data list or dict
            
        Returns:
            str: JSON string for display
        """
        try:
            # Strip internal IDs and metadata for clean display
            clean_elements = self.strip_object_ids(elements)
            return json.dumps(clean_elements, indent=2, ensure_ascii=False)
        except Exception as e:
            return f'{{"error": "Failed to convert to JSON: {str(e)}"}}'
    
    def strip_object_ids(self, data: Union[Dict, List]) -> Union[Dict, List]:
        """
        Remove internal IDs and metadata from data for clean display.
        
        Args:
            data (dict/list): Data containing internal identifiers
            
        Returns:
            dict/list: Data without internal identifiers
        """
        try:
            if isinstance(data, dict):
                return {
                    key: self.strip_object_ids(value)
                    for key, value in data.items()
                    if not key.startswith('_') and key not in ['object_id', 'internal_id', 'mongodb_id']
                }
            elif isinstance(data, list):
                return [self.strip_object_ids(item) for item in data]
            else:
                return data
        except Exception:
            return data
    
    def generate_element_colors(self, elements: List[str], seed: Optional[int] = None) -> Dict[str, str]:
        """
        Generate consistent colors for elements.
        
        Args:
            elements (list): List of elements needing colors
            seed: Seed for consistent color generation
            
        Returns:
            dict: Element to color mapping
        """
        try:
            if seed is not None:
                random.seed(seed)
            
            colors = {}
            color_palette = [
                "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
                "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
                "#F8C471", "#82E0AA", "#F1948A", "#85C1E9", "#F4D03F"
            ]
            
            for i, element in enumerate(elements):
                if element not in colors:
                    colors[element] = color_palette[i % len(color_palette)]
            
            return colors
            
        except Exception:
            # Return default colors on error
            return {element: "#666666" for element in elements}
    
    def _sanitize_html(self, text: str) -> str:
        """
        Basic HTML sanitization to prevent XSS attacks.
        
        Args:
            text (str): Text to sanitize
            
        Returns:
            str: Sanitized text
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Basic HTML escaping
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&#x27;",
            ">": "&gt;",
            "<": "&lt;",
        }
        
        for char, escape in html_escape_table.items():
            text = text.replace(char, escape)
        
        return text