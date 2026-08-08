"""
Centralized Configuration Management for Visualizers.

This module provides centralized configuration management for all visualizer classes,
eliminating scattered hardcoded constants and providing consistent display parameters
across different visualizer types.
"""


class VisualizerConfig:
    """Centralized configuration management for visualizer display parameters."""
    
    # Node Display Configuration
    DEFAULT_NODE_SIZES = {
        'selected': 3500,
        'connected': 2000,
        'unconnected': 1000,
        'lexical_unit': 1000,
        'frame_element': 800
    }
    
    # Interaction Thresholds
    INTERACTION_THRESHOLDS = {
        'hover_threshold': 0.05,  # Percentage of axis range
        'click_threshold': 0.05   # Percentage of axis range
    }
    
    # Color Schemes by Visualizer Type
    COLOR_SCHEMES = {
        'default': {
            'unconnected': 'lightgray',
            'edge_highlight': 'red',
            'edge_normal': 'black',
            'edge_greyed': 'lightgray'
        },
        'framenet': {
            'unconnected': 'lightgray',
            'edge_highlight': 'red',
            'edge_normal': 'black',
            'edge_greyed': 'lightgray'
        },
        'verbnet': {
            'unconnected': 'lightgray',
            'edge_highlight': 'red',
            'edge_normal': 'black',
            'edge_greyed': 'lightgray'
        },
        'wordnet': {
            'unconnected': 'lightgray',
            'edge_highlight': 'red', 
            'edge_normal': 'black',
            'edge_greyed': 'lightgray'
        }
    }
    
    # Alpha Values
    ALPHA_VALUES = {
        'connected_nodes': 1.0,
        'unconnected_nodes': 0.3,
        'highlight_edges': 0.8,
        'greyed_edges': 0.2
    }
    
    # Edge Styling
    EDGE_STYLES = {
        'highlight_width': 3,
        'normal_width': 1.5,
        'greyed_width': 0.5,
        'arrow_size': 20
    }
    
    # Font Configuration
    FONT_STYLES = {
        'connected_size': 10,
        'unconnected_size': 6,
        'selected_weight': 'bold',
        'normal_weight': 'normal'
    }
    
    # Tooltip Configuration
    TOOLTIP_STYLES = {
        'default': {
            'offset': (20, 20),
            'bbox': {'boxstyle': 'round,pad=0.5', 'fc': 'wheat', 'alpha': 0.8},
            'arrowprops': {'arrowstyle': '->', 'connectionstyle': 'arc3,rad=0'},
            'fontsize': 9,
            'fontweight': 'normal'
        },
        'combined': {
            'offset': (20, 20),
            'bbox': {'boxstyle': 'round,pad=0.5', 'fc': 'yellow', 'alpha': 0.8},
            'arrowprops': {'arrowstyle': '->', 'connectionstyle': 'arc3,rad=0'},
            'fontsize': 9,
            'fontweight': 'normal'
        }
    }
    
    # Legend Configuration
    LEGEND_CONFIG = {
        'location': 'upper left',
        'fontsize': 10,
        'title_fontsize': 12,
        'title_fontweight': 'bold'
    }
    
    @classmethod
    def get_node_sizes(cls, visualizer_type='default'):
        """Get node size configuration for a specific visualizer type."""
        return cls.DEFAULT_NODE_SIZES.copy()
    
    @classmethod
    def get_color_scheme(cls, visualizer_type='default'):
        """Get color scheme for a specific visualizer type."""
        return cls.COLOR_SCHEMES.get(visualizer_type, cls.COLOR_SCHEMES['default']).copy()
    
    @classmethod
    def get_interaction_thresholds(cls):
        """Get interaction threshold configuration."""
        return cls.INTERACTION_THRESHOLDS.copy()
    
    @classmethod
    def get_alpha_values(cls):
        """Get alpha value configuration."""
        return cls.ALPHA_VALUES.copy()
    
    @classmethod
    def get_edge_styles(cls):
        """Get edge styling configuration."""
        return cls.EDGE_STYLES.copy()
    
    @classmethod
    def get_font_styles(cls):
        """Get font styling configuration."""
        return cls.FONT_STYLES.copy()
    
    @classmethod
    def get_tooltip_style(cls, tooltip_type='default'):
        """Get tooltip styling configuration."""
        return cls.TOOLTIP_STYLES.get(tooltip_type, cls.TOOLTIP_STYLES['default']).copy()
    
    @classmethod
    def get_legend_config(cls):
        """Get legend configuration."""
        return cls.LEGEND_CONFIG.copy()
    
    @classmethod
    def get_highlight_styling(cls, visualizer_type='default', custom_overrides=None):
        """
        Get complete highlighting styling configuration.
        
        Args:
            visualizer_type: Type of visualizer ('default', 'framenet', 'verbnet', 'wordnet')
            custom_overrides: Dict of custom styling overrides
            
        Returns:
            Dict containing all styling parameters for highlighting
        """
        node_sizes = cls.get_node_sizes(visualizer_type)
        colors = cls.get_color_scheme(visualizer_type)
        alphas = cls.get_alpha_values()
        edges = cls.get_edge_styles()
        fonts = cls.get_font_styles()
        
        styling = {
            # Node styling
            'unconnected_color': colors['unconnected'],
            'unconnected_size': node_sizes['unconnected'],
            'unconnected_alpha': alphas['unconnected_nodes'],
            'connected_size': node_sizes['connected'],
            'selected_size': node_sizes['selected'],
            'connected_alpha': alphas['connected_nodes'],
            
            # Edge styling
            'edge_highlight_color': colors['edge_highlight'],
            'edge_normal_color': colors['edge_normal'],
            'edge_greyed_color': colors['edge_greyed'],
            'edge_highlight_width': edges['highlight_width'],
            'edge_normal_width': edges['normal_width'],
            'edge_greyed_width': edges['greyed_width'],
            'edge_highlight_alpha': alphas['highlight_edges'],
            'edge_greyed_alpha': alphas['greyed_edges'],
            
            # Font styling
            'font_size_connected': fonts['connected_size'],
            'font_size_unconnected': fonts['unconnected_size'],
            'font_weight_selected': fonts['selected_weight'],
            'font_weight_normal': fonts['normal_weight']
        }
        
        if custom_overrides:
            styling.update(custom_overrides)
            
        return styling
    
    @classmethod
    def create_visualizer_config(cls, visualizer_type, custom_config=None):
        """
        Create a complete configuration for a specific visualizer type.
        
        Args:
            visualizer_type: Type of visualizer
            custom_config: Dict of custom configuration overrides
            
        Returns:
            Dict containing complete visualizer configuration
        """
        config = {
            'node_sizes': cls.get_node_sizes(visualizer_type),
            'colors': cls.get_color_scheme(visualizer_type),
            'interaction_thresholds': cls.get_interaction_thresholds(),
            'alpha_values': cls.get_alpha_values(),
            'edge_styles': cls.get_edge_styles(),
            'font_styles': cls.get_font_styles(),
            'tooltip_style': cls.get_tooltip_style('combined' if 'combined' in visualizer_type.lower() else 'default'),
            'legend_config': cls.get_legend_config()
        }
        
        if custom_config:
            # Deep merge custom configuration
            for section, values in custom_config.items():
                if section in config and isinstance(config[section], dict):
                    config[section].update(values)
                else:
                    config[section] = values
        
        return config