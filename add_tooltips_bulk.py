#!/usr/bin/env python3
"""
Bulk tooltip addition script for enhanced dashboard
This script will add data source tooltips to all remaining charts in the enhanced dashboard.
"""

import re

def add_tooltip_to_chart(content, chart_pattern, data_source):
    """Add tooltip annotation to a chart pattern."""
    
    # Pattern to find fig.update_layout calls without annotations
    layout_pattern = r'(fig\.update_layout\([^)]*?height=\d+)(\))'
    
    def replacement(match):
        layout_call = match.group(1)
        # Check if annotations already exist
        if 'annotations=' in layout_call:
            return match.group(0)  # Already has annotations
        
        # Add annotations parameter
        annotation_text = f"""                        annotations=[
                            dict(
                                text=self.get_data_source_tooltip('{data_source}'),
                                showarrow=False,
                                xref="paper", yref="paper",
                                x=0.02, y=0.98,
                                xanchor="left", yanchor="top",
                                bgcolor="rgba(255,255,255,0.8)",
                                bordercolor="gray",
                                borderwidth=1,
                                font=dict(size=10)
                            )
                        ]"""
        
        return layout_call + ',\n' + annotation_text + '\n                    )'
    
    return re.sub(layout_pattern, replacement, content)

def add_hover_templates(content):
    """Add hover templates to charts without them."""
    
    # Common hover template patterns for different chart types
    hover_patterns = [
        # Bar charts
        (r'(fig = px\.bar\([^)]+\))', 'bar'),
        # Line charts  
        (r'(fig = px\.line\([^)]+\))', 'line'),
        # Scatter plots
        (r'(fig = px\.scatter\([^)]+\))', 'scatter'),
        # Pie charts
        (r'(fig = px\.pie\([^)]+\))', 'pie'),
    ]
    
    for pattern, chart_type in hover_patterns:
        def add_hover(match):
            chart_call = match.group(1)
            # Add appropriate hover template based on chart type
            if chart_type == 'pie':
                hover_template = '''
                fig.update_traces(
                    hovertemplate="<b>Category:</b> %{label}<br>" +
                                  "<b>Value:</b> %{value:,.2f}<br>" +
                                  "<b>Percentage:</b> %{percent}<br>" +
                                  "<b>Data Source:</b> Stock Records<br>" +
                                  "<extra></extra>"
                )'''
            else:
                hover_template = '''
                fig.update_traces(
                    hovertemplate="<b>Value:</b> %{y:,.2f}<br>" +
                                  "<b>Data Source:</b> Stock Records<br>" +
                                  "<extra></extra>"
                )'''
            
            return chart_call + hover_template
        
        content = re.sub(pattern, add_hover, content)
    
    return content

def main():
    """Main function to add tooltips to all charts."""
    
    # Read the enhanced dashboard file
    with open('enhanced_dashboard.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Adding data source tooltips to charts...")
    
    # Chart mappings with their data sources
    chart_mappings = [
        ('create_supplier_analytics', ['hr995_grn.csv', 'suppliers.csv']),
        ('create_operational_analytics', ['hr995_grn.csv', 'hr995_issue.csv']),
        ('create_volume_anomalies', ['hr995_grn.csv', 'hr995_issue.csv']),
        ('create_time_anomalies', ['hr995_grn.csv', 'hr995_issue.csv']),
        ('create_pattern_anomalies', ['hr995_grn.csv', 'hr995_issue.csv']),
        ('create_turnover_analysis', ['hr995_grn.csv', 'hr995_issue.csv']),
        ('create_stock_alerts', ['stock_adjustments.csv', 'all_stock_data.csv']),
    ]
    
    # Add tooltips to different chart sections
    for section, sources in chart_mappings:
        if len(sources) == 1:
            source_text = f"'{sources[0]}'"
        else:
            source_text = str(sources)
        content = add_tooltip_to_chart(content, section, source_text)
    
    # Add hover templates
    content = add_hover_templates(content)
    
    # Write back the updated content
    with open('enhanced_dashboard.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Successfully added tooltips to enhanced dashboard!")
    print("📊 Charts now include:")
    print("   • Data source annotations")
    print("   • Enhanced hover information")
    print("   • Source file references")

if __name__ == "__main__":
    main()
