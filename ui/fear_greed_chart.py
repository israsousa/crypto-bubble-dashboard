"""
Improved Fear & Greed Index Chart
Professional rendering with corrected color order and smooth fills
"""

import pygame
import math
import datetime
from config.settings import COLORS

def get_fear_greed_label(value):
    """Get label for Fear & Greed Index value"""
    if value <= 25:
        return "Extreme Fear"
    elif value <= 45:
        return "Fear"
    elif value <= 55:
        return "Neutral"
    elif value <= 75:
        return "Greed"
    else:
        return "Extreme Greed"

def draw_fear_greed_chart(surface, fear_greed_data):
    """Draw professional Fear & Greed Index chart with improved colors and rendering"""
    surface.fill(COLORS['panel_bg'])
    width, height = surface.get_size()
    
    value = fear_greed_data['value']
    label = fear_greed_data['label']
    timestamp = fear_greed_data['timestamp']
    yesterday_data = fear_greed_data['yesterday']
    last_week_data = fear_greed_data['last_week']
    last_month_data = fear_greed_data['last_month']
    last_updated = fear_greed_data.get('last_updated', None)
    
    # CORRECTED COLOR MAPPING (Green to Red instead of Red to Green)
    if value < 25:
        value_color = (220, 80, 80)      # Red - Extreme Fear
        gauge_color = (200, 60, 60)
    elif value < 45:
        value_color = (255, 140, 80)     # Orange - Fear
        gauge_color = (235, 120, 60)
    elif value < 55:
        value_color = (255, 220, 80)     # Yellow - Neutral
        gauge_color = (235, 200, 60)
    elif value < 75:
        value_color = (160, 220, 80)     # Light Green - Greed
        gauge_color = (140, 200, 60)
    else:
        value_color = (80, 200, 80)      # Green - Extreme Greed
        gauge_color = (60, 180, 60)
    
    # Professional title
    title_font = pygame.font.SysFont("Segoe UI", 16, bold=True)
    title_surface = title_font.render("Fear & Greed Index", True, (220, 230, 250))
    
    # Status indicator
    if last_updated:
        import time
        time_since_update = time.time() - last_updated
        if time_since_update < 3600:
            status_color = (80, 200, 120)
            status_text = "●"
        else:
            status_color = (255, 200, 100)
            status_text = "◐"
    else:
        status_color = (140, 160, 180)
        status_text = "○"
    
    status_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
    status_surface = status_font.render(status_text, True, status_color)
    
    # Center title
    title_x = (width - title_surface.get_width()) // 2
    title_y = 8
    surface.blit(title_surface, (title_x, title_y))
    surface.blit(status_surface, (title_x + title_surface.get_width() + 8, title_y + 2))
    
    # Chart positioning
    chart_center_x = int(width * 0.38)
    chart_center_y = height // 2 + 10
    chart_radius = min(width // 5, height // 4)
    chart_radius = max(chart_radius, 50)
    
    # IMPROVED GAUGE RENDERING - Smooth gradient fill
    def render_smooth_gauge_background():
        """Render smooth gauge background"""
        background_surface = pygame.Surface((chart_radius * 2 + 20, chart_radius * 2 + 20), pygame.SRCALPHA)
        
        # Multiple layers for smooth appearance
        for layer in range(15):
            layer_radius = chart_radius - layer
            if layer_radius <= 0:
                break
                
            layer_alpha = max(20, 100 - layer * 6)
            layer_color = (60, 70, 85, layer_alpha)
            
            # Draw arc background
            arc_rect = pygame.Rect(
                10 + layer, 10 + layer,
                2 * layer_radius, 2 * layer_radius
            )
            
            # Create arc surface for smooth rendering
            arc_surface = pygame.Surface((2 * layer_radius + 4, 2 * layer_radius + 4), pygame.SRCALPHA)
            pygame.draw.arc(arc_surface, layer_color[:3], 
                           (2, 2, 2 * layer_radius, 2 * layer_radius),
                           0, math.pi, max(1, 4 - layer // 3))
            
            background_surface.blit(arc_surface, (10 + layer - 2, 10 + layer - 2))
        
        return background_surface
    
    # Render gauge background
    gauge_bg = render_smooth_gauge_background()
    surface.blit(gauge_bg, (chart_center_x - chart_radius - 10, chart_center_y - chart_radius - 10))
    
    # IMPROVED VALUE ARC RENDERING - Anti-aliased and smooth
    def render_smooth_value_arc():
        """Render smooth value arc with anti-aliasing"""
        angle = math.pi * (value / 100)
        
        # Create high-resolution surface for smooth rendering
        arc_size = chart_radius * 2 + 40
        arc_surface = pygame.Surface((arc_size, arc_size), pygame.SRCALPHA)
        
        # Multiple layers for smooth gradient effect
        for layer in range(12):
            layer_radius = chart_radius - layer
            if layer_radius <= 0:
                break
                
            # Gradient from full color to transparent
            layer_intensity = 1.0 - (layer / 12)
            layer_alpha = int(255 * layer_intensity * 0.9)
            
            # Color with gradient
            layer_color = tuple(int(c * layer_intensity) for c in gauge_color) + (layer_alpha,)
            
            # Draw smooth arc
            arc_rect = pygame.Rect(
                20 + layer, 20 + layer,
                2 * layer_radius, 2 * layer_radius
            )
            
            if layer_radius > 0:
                # Use multiple thin arcs for smoothness
                for i in range(max(1, 6 - layer // 2)):
                    pygame.draw.arc(arc_surface, layer_color[:3], arc_rect,
                                   0, angle, max(1, 6 - layer))
        
        return arc_surface
    
    # Render value arc
    value_arc = render_smooth_value_arc()
    surface.blit(value_arc, (chart_center_x - chart_radius - 20, chart_center_y - chart_radius - 20))
    
    # Professional center value display
    value_font = pygame.font.SysFont("Segoe UI", 24, bold=True)
    value_surface = value_font.render(str(value), True, (255, 255, 255))
    value_rect = value_surface.get_rect(center=(chart_center_x, chart_center_y - 5))
    
    # Subtle shadow for depth
    shadow_surface = value_font.render(str(value), True, (40, 50, 65))
    shadow_rect = shadow_surface.get_rect(center=(chart_center_x + 1, chart_center_y - 4))
    surface.blit(shadow_surface, shadow_rect)
    surface.blit(value_surface, value_rect)
    
    # Professional label
    label_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
    label_surface = label_font.render(label, True, value_color)
    label_rect = label_surface.get_rect(center=(chart_center_x, chart_center_y + 20))
    surface.blit(label_surface, label_rect)
    
    # Historical data panel
    hist_x = chart_center_x + chart_radius + 25
    hist_start_y = chart_center_y - 40
    
    hist_font = pygame.font.SysFont("Segoe UI", 11, bold=True)
    small_font = pygame.font.SysFont("Segoe UI", 10)
    line_height = 22
    
    def draw_professional_historical_line(y_pos, period_label, period_value, period_label_text, change_value):
        """Draw professional historical data line"""
        if period_value is None:
            return y_pos
            
        # Change indicator with professional colors
        if change_value > 0:
            change_color = (80, 200, 120)
            change_symbol = "↑"
            change_text = f"+{change_value}"
        elif change_value < 0:
            change_color = (220, 80, 80)
            change_symbol = "↓"
            change_text = f"{change_value}"
        else:
            change_color = (160, 180, 200)
            change_symbol = "→"
            change_text = "0"
        
        # Period label
        period_surface = small_font.render(f"{period_label}:", True, (140, 160, 180))
        surface.blit(period_surface, (hist_x, y_pos))
        
        # Value
        value_text = f"{period_value}"
        value_surface = hist_font.render(value_text, True, (200, 220, 255))
        value_x = hist_x + period_surface.get_width() + 5
        surface.blit(value_surface, (value_x, y_pos - 1))
        
        # Change indicator
        change_full_text = f" {change_symbol}{change_text}"
        change_surface = small_font.render(change_full_text, True, change_color)
        change_x = value_x + value_surface.get_width() + 3
        
        if change_x + change_surface.get_width() <= width - 10:
            surface.blit(change_surface, (change_x, y_pos))
        
        return y_pos + line_height
    
    # Render historical data
    current_y = hist_start_y
    
    if yesterday_data['value'] is not None:
        yesterday_label = yesterday_data['label'] if yesterday_data['label'] else get_fear_greed_label(yesterday_data['value'])
        current_y = draw_professional_historical_line(current_y, "Yesterday", yesterday_data['value'], 
                                                    yesterday_label, yesterday_data.get('change', 0))
    
    if last_week_data['value'] is not None:
        last_week_label = last_week_data['label'] if last_week_data['label'] else get_fear_greed_label(last_week_data['value'])
        current_y = draw_professional_historical_line(current_y, "Last Week", last_week_data['value'], 
                                                    last_week_label, last_week_data.get('change', 0))
    
    if last_month_data['value'] is not None:
        last_month_label = last_month_data['label'] if last_month_data['label'] else get_fear_greed_label(last_month_data['value'])
        current_y = draw_professional_historical_line(current_y, "Last Month", last_month_data['value'], 
                                                    last_month_label, last_month_data.get('change', 0))
    
    # IMPROVED SCALE INDICATORS - Better positioning and colors
    scale_y = chart_center_y + chart_radius + 35
    scale_font = pygame.font.SysFont("Segoe UI", 9, bold=True)
    desc_font = pygame.font.SysFont("Segoe UI", 8)
    
    # Corrected scale points (Green to Red progression)
    scale_points = [
        (0, "0", "Extreme Fear", (220, 80, 80)),      # Red
        (25, "25", "Fear", (255, 140, 80)),           # Orange  
        (50, "50", "Neutral", (255, 220, 80)),        # Yellow
        (75, "75", "Greed", (160, 220, 80)),          # Light Green
        (100, "100", "Extreme Greed", (80, 200, 80))  # Green
    ]
    
    for scale_value, scale_text, scale_desc, scale_color in scale_points:
        # Position indicators along the arc
        scale_angle = math.pi * (1 - scale_value / 100)
        
        # Marker position
        marker_radius = chart_radius - 5
        scale_x = chart_center_x + int(marker_radius * math.cos(scale_angle))
        scale_marker_y = chart_center_y - int(marker_radius * math.sin(scale_angle))
        
        # Enhanced marker with glow effect
        pygame.draw.circle(surface, (255, 255, 255), (scale_x, scale_marker_y), 4)
        pygame.draw.circle(surface, scale_color, (scale_x, scale_marker_y), 3)
        
        # Scale labels below the gauge
        label_spacing = (2 * chart_radius) / 4
        text_x = chart_center_x - chart_radius + int((label_spacing * scale_value) / 25)
        
        # Number label
        scale_surface = scale_font.render(scale_text, True, scale_color)
        number_rect = scale_surface.get_rect(center=(text_x, scale_y))
        surface.blit(scale_surface, number_rect)
        
        # Description label
        desc_surface = desc_font.render(scale_desc, True, (160, 180, 200))
        desc_rect = desc_surface.get_rect(center=(text_x, scale_y + 14))
        surface.blit(desc_surface, desc_rect)
    
    # Professional legend
    legend_y = scale_y + 40
    legend_font = pygame.font.SysFont("Segoe UI", 9)
    legend_items = [
        "Market sentiment based on volatility, momentum,", 
        "safe haven demand, and social media analysis"
    ]
    
    for i, legend_text in enumerate(legend_items):
        if legend_y + (i * 12) < height - 20:
            legend_surface = legend_font.render(legend_text, True, (120, 140, 160))
            legend_rect = legend_surface.get_rect(center=(chart_center_x, legend_y + (i * 12)))
            surface.blit(legend_surface, legend_rect)
    
    # Professional timestamp
    if timestamp:
        try:
            current_time = datetime.datetime.fromtimestamp(int(timestamp))
            time_text = f"Updated: {current_time.strftime('%b %d, %H:%M UTC')}"
            time_font = pygame.font.SysFont("Segoe UI", 9)
            time_surface = time_font.render(time_text, True, (120, 140, 160))
            time_x = (width - time_surface.get_width()) // 2
            time_y = height - 15
            surface.blit(time_surface, (time_x, time_y))
        except:
            pass