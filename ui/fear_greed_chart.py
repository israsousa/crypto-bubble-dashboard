"""
Perfected Fear & Greed Index Chart
Enhanced with better fonts, corrected loading order, improved fills, and centered layout
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

def get_perfected_fear_greed_color(value):
    """Get perfected color progression with smooth transitions - FIXED for left-to-right"""
    # Clamp value between 0 and 100
    value = max(0, min(100, value))
    
    # CORRECTED: Now 0=red (left), 100=green (right)
    if value <= 25:
        # 0-25: Deep Red to Red-Orange (Extreme Fear to Fear)
        t = value / 25
        return (
            int(200 + t * 55),  # 200 → 255 (deeper to brighter red)
            int(40 + t * 70),   # 40 → 110 (add orange component)
            int(40 + t * 10)    # 40 → 50 (slight blue)
        )
    
    elif value <= 50:
        # 25-50: Red-Orange to Yellow (Fear to Neutral)
        t = (value - 25) / 25
        return (
            int(255),               # Keep red at max
            int(110 + t * 145),     # 110 → 255 (orange to yellow)
            int(50 + t * 20)        # 50 → 70 (slight blue increase)
        )
    
    elif value <= 75:
        # 50-75: Yellow to Light Green (Neutral to Greed)
        t = (value - 50) / 25
        return (
            int(255 - t * 175),     # 255 → 80 (reduce red significantly)
            int(255),               # Keep green at max
            int(70 + t * 30)        # 70 → 100 (slight blue increase)
        )
    
    else:
        # 75-100: Light Green to Deep Green (Greed to Extreme Greed)
        t = (value - 75) / 25
        return (
            int(80 - t * 20),       # 80 → 60 (less red)
            int(255 - t * 35),      # 255 → 220 (slightly deeper green)
            int(100 - t * 20)       # 100 → 80 (less blue for purer green)
        )

def create_enhanced_gauge_fill(center_x, center_y, radius, value):
    """Create enhanced gauge fill with CONSISTENT color-value alignment"""
    # Create surface for the gradient fill
    size = radius * 2 + 40
    fill_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Calculate the angle for the current value
    target_angle = math.pi * (value / 100)
    
    # CONSISTENT: Color gradient should match the logical value progression
    # Left side (π) = 0 = Red (Fear), Right side (0) = 100 = Green (Greed)
    segments = 100  # High resolution for smooth gradient
    
    for i in range(segments):
        # Calculate angles for this segment
        segment_progress = i / segments
        segment_angle = segment_progress * target_angle
        segment_end_angle = ((i + 1) / segments) * target_angle
        
        # CONSISTENT: Map segment position to value correctly
        # segment_angle goes from 0 to target_angle
        # We want this to map from current_value down to 0 (since we draw left to right)
        if target_angle > 0:
            # For the gradient: early segments (small angles) should have current value
            # later segments (larger angles) should approach 0
            angle_ratio = segment_angle / target_angle  # 0 to 1
            segment_value = value * (1 - angle_ratio)  # value down to 0
        else:
            segment_value = 0
        
        segment_color = get_perfected_fear_greed_color(segment_value)
        
        # Draw multiple layers for each segment for smooth appearance
        for thickness in range(12, 0, -2):
            alpha = int(255 * (13 - thickness) / 12 * 0.8)
            layer_color = (*segment_color, alpha)
            
            try:
                arc_rect = pygame.Rect(20, 20, radius * 2, radius * 2)
                pygame.draw.arc(fill_surface, layer_color[:3], arc_rect,
                               segment_angle, segment_end_angle, thickness)
            except:
                pass
    
    return fill_surface

def draw_fear_greed_chart(surface, fear_greed_data):
    """Draw perfected Fear & Greed Index chart with enhanced design"""
    surface.fill(COLORS['panel_bg'])
    width, height = surface.get_size()
    
    value = fear_greed_data['value']
    label = fear_greed_data['label']
    timestamp = fear_greed_data['timestamp']
    yesterday_data = fear_greed_data['yesterday']
    last_week_data = fear_greed_data['last_week']
    last_month_data = fear_greed_data['last_month']
    last_updated = fear_greed_data.get('last_updated', None)
    
    # Professional title section - CENTERED
    title_font = pygame.font.SysFont("Segoe UI", 18, bold=True)
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
    
    status_font = pygame.font.SysFont("Segoe UI", 14, bold=True)
    status_surface = status_font.render(status_text, True, status_color)
    
    # Center title perfectly
    title_x = (width - title_surface.get_width()) // 2
    title_y = 12
    surface.blit(title_surface, (title_x, title_y))
    surface.blit(status_surface, (title_x + title_surface.get_width() + 10, title_y + 1))
    
    # Chart positioning - BETTER CENTERED
    chart_center_x = int(width * 0.40)  # Slightly more centered
    chart_center_y = int(height * 0.48)  # Better vertical centering
    chart_radius = min(width // 4.5, height // 3.5)
    chart_radius = max(chart_radius, 60)
    
    # Enhanced gauge background with better appearance
    def render_perfected_gauge_background():
        """Render perfected gauge background"""
        bg_surface = pygame.Surface((chart_radius * 2 + 40, chart_radius * 2 + 40), pygame.SRCALPHA)
        
        # Multiple layers for depth and smoothness
        for layer in range(15):
            layer_radius = chart_radius - layer
            if layer_radius <= 0:
                break
                
            layer_alpha = max(12, 90 - layer * 5)
            layer_color = (45, 55, 70, layer_alpha)
            
            # Smooth arc background
            try:
                arc_rect = pygame.Rect(
                    20 + layer, 20 + layer,
                    2 * layer_radius, 2 * layer_radius
                )
                
                arc_surface = pygame.Surface((2 * layer_radius + 4, 2 * layer_radius + 4), pygame.SRCALPHA)
                pygame.draw.arc(arc_surface, layer_color[:3], 
                               (2, 2, 2 * layer_radius, 2 * layer_radius),
                               0, math.pi, max(1, 8 - layer // 2))
                
                bg_surface.blit(arc_surface, (20 + layer - 2, 20 + layer - 2))
            except:
                pass
        
        return bg_surface
    
    # Render enhanced gauge background
    gauge_bg = render_perfected_gauge_background()
    surface.blit(gauge_bg, (chart_center_x - chart_radius - 20, chart_center_y - chart_radius - 20))
    
    # PERFECTED value arc with smooth gradient fill (Red → Green)
    value_fill = create_enhanced_gauge_fill(chart_center_x, chart_center_y, chart_radius, value)
    surface.blit(value_fill, (chart_center_x - chart_radius - 20, chart_center_y - chart_radius - 20))
    
    # Professional center value display
    value_font = pygame.font.SysFont("Segoe UI", 28, bold=True)
    value_surface = value_font.render(str(value), True, (255, 255, 255))
    value_rect = value_surface.get_rect(center=(chart_center_x, chart_center_y - 5))
    
    # Enhanced shadow for depth
    shadow_surface = value_font.render(str(value), True, (25, 35, 50))
    shadow_rect = shadow_surface.get_rect(center=(chart_center_x + 2, chart_center_y - 3))
    surface.blit(shadow_surface, shadow_rect)
    surface.blit(value_surface, value_rect)
    
    # Professional label with perfected color
    label_font = pygame.font.SysFont("Segoe UI", 14, bold=True)
    label_color = get_perfected_fear_greed_color(value)
    label_surface = label_font.render(label, True, label_color)
    label_rect = label_surface.get_rect(center=(chart_center_x, chart_center_y + 25))
    surface.blit(label_surface, label_rect)
    
    # Enhanced historical data panel - BETTER POSITIONED
    hist_x = chart_center_x + chart_radius + 35
    hist_start_y = chart_center_y - 50
    
    hist_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
    small_font = pygame.font.SysFont("Segoe UI", 11)
    line_height = 26
    
    def draw_perfected_historical_line(y_pos, period_label, period_value, period_label_text, change_value):
        """Draw historical data line with perfected styling"""
        if period_value is None:
            return y_pos
            
        # Change indicator with enhanced colors
        if change_value > 0:
            change_color = (70, 220, 110)
            change_symbol = "↑"
            change_text = f"+{change_value}"
        elif change_value < 0:
            change_color = (230, 70, 70)
            change_symbol = "↓"
            change_text = f"{change_value}"
        else:
            change_color = (160, 180, 200)
            change_symbol = "→"
            change_text = "0"
        
        # Period label
        period_surface = small_font.render(f"{period_label}:", True, (150, 170, 190))
        surface.blit(period_surface, (hist_x, y_pos))
        
        # Value with perfected color
        value_color = get_perfected_fear_greed_color(period_value)
        value_text = f"{period_value}"
        value_surface = hist_font.render(value_text, True, value_color)
        value_x = hist_x + period_surface.get_width() + 8
        surface.blit(value_surface, (value_x, y_pos - 1))
        
        # Change indicator
        change_full_text = f" {change_symbol}{change_text}"
        change_surface = small_font.render(change_full_text, True, change_color)
        change_x = value_x + value_surface.get_width() + 5
        
        if change_x + change_surface.get_width() <= width - 10:
            surface.blit(change_surface, (change_x, y_pos))
        
        return y_pos + line_height
    
    # Render historical data with perfected styling
    current_y = hist_start_y
    
    if yesterday_data['value'] is not None:
        yesterday_label = yesterday_data['label'] if yesterday_data['label'] else get_fear_greed_label(yesterday_data['value'])
        current_y = draw_perfected_historical_line(current_y, "Yesterday", yesterday_data['value'], 
                                                 yesterday_label, yesterday_data.get('change', 0))
    
    if last_week_data['value'] is not None:
        last_week_label = last_week_data['label'] if last_week_data['label'] else get_fear_greed_label(last_week_data['value'])
        current_y = draw_perfected_historical_line(current_y, "Last Week", last_week_data['value'], 
                                                 last_week_label, last_week_data.get('change', 0))
    
    if last_month_data['value'] is not None:
        last_month_label = last_month_data['label'] if last_month_data['label'] else get_fear_greed_label(last_month_data['value'])
        current_y = draw_perfected_historical_line(current_y, "Last Month", last_month_data['value'], 
                                                 last_month_label, last_month_data.get('change', 0))
    
    # FIXED: Thin straight indicators BETWEEN center value and gauge
    scale_font = pygame.font.SysFont("Segoe UI", 11, bold=True)
    desc_font = pygame.font.SysFont("Segoe UI", 10, bold=True)
    
    # Scale points with exact colors
    scale_points = [
        (0, "0", "Extreme Fear", (200, 40, 40)),
        (25, "25", "Fear", (255, 110, 50)),
        (50, "50", "Neutral", (255, 255, 70)),
        (75, "75", "Greed", (80, 255, 100)),
        (100, "100", "Extreme Greed", (60, 220, 80))
    ]
    
    # Draw THIN STRAIGHT indicators between center and gauge
    for scale_value, scale_text, scale_desc, scale_color in scale_points:
        # Position indicators along the arc
        scale_angle = math.pi * (1 - scale_value / 100)
        
        # FIXED: Thin straight lines positioned BETWEEN center value and gauge
        indicator_start_radius = chart_radius * 0.6  # Start closer to center
        indicator_end_radius = chart_radius * 0.8    # End before gauge
        
        start_x = chart_center_x + int(indicator_start_radius * math.cos(scale_angle))
        start_y = chart_center_y - int(indicator_start_radius * math.sin(scale_angle))
        end_x = chart_center_x + int(indicator_end_radius * math.cos(scale_angle))
        end_y = chart_center_y - int(indicator_end_radius * math.sin(scale_angle))
        
        # Draw thin straight line (thickness = 2)
        pygame.draw.line(surface, scale_color, (start_x, start_y), (end_x, end_y), 2)
        
        # Optional: Small arrow at the end pointing towards gauge
        # Calculate arrow tip
        arrow_length = 4
        arrow_tip_x = end_x + int(arrow_length * math.cos(scale_angle))
        arrow_tip_y = end_y - int(arrow_length * math.sin(scale_angle))
        
        # Draw small arrow
        pygame.draw.line(surface, scale_color, (end_x, end_y), (arrow_tip_x, arrow_tip_y), 2)
    
    # Scale labels positioned below the gauge
    scale_y = chart_center_y + chart_radius + 30
    scale_descriptions = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]
    scale_numbers = ["0", "25", "50", "75", "100"]
    scale_colors = [(200, 40, 40), (255, 110, 50), (255, 255, 70), (80, 255, 100), (60, 220, 80)]
    
    # Calculate spacing to fit all labels properly
    available_width = chart_radius * 2
    label_spacing = available_width / 4  # 4 intervals for 5 labels
    start_x = chart_center_x - chart_radius
    
    # Draw horizontal layout with proper spacing
    for i in range(5):
        x_pos = start_x + (i * label_spacing)
        
        # Number with color
        num_surface = scale_font.render(scale_numbers[i], True, scale_colors[i])
        num_rect = num_surface.get_rect(center=(x_pos, scale_y))
        surface.blit(num_surface, num_rect)
        
        # Description below number
        desc_surface = desc_font.render(scale_descriptions[i], True, (170, 190, 210))
        desc_rect = desc_surface.get_rect(center=(x_pos, scale_y + 18))
        surface.blit(desc_surface, desc_rect)
    
    # REPOSITIONED legend and timestamp with better spacing
    legend_start_y = scale_y + 45
    
    # Professional timestamp positioned properly
    if timestamp:
        try:
            current_time = datetime.datetime.fromtimestamp(int(timestamp))
            time_text = f"Updated: {current_time.strftime('%b %d, %H:%M UTC')}"
            time_font = pygame.font.SysFont("Segoe UI", 9)
            time_surface = time_font.render(time_text, True, (120, 140, 160))
            
            time_x = (width - time_surface.get_width()) // 2
            time_y = legend_start_y
            if time_y + 15 < height - 5:  # Only show if fits
                surface.blit(time_surface, (time_x, time_y))
                legend_start_y += 20
        except:
            pass
    
    # Compact legend - only show if there's space
    if legend_start_y + 15 < height - 5:
        legend_font = pygame.font.SysFont("Segoe UI", 9)
        legend_text = "Market sentiment: Red (Fear) → Yellow (Neutral) → Green (Greed)"
        legend_surface = legend_font.render(legend_text, True, (130, 150, 170))
        legend_rect = legend_surface.get_rect(center=(width // 2, legend_start_y))
        surface.blit(legend_surface, legend_rect)