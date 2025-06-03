"""
Refined Fear & Greed Index Chart
Enhanced with shorter tick marks, responsive labels, and consistent color direction
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
    """Get perfected color progression with smooth transitions - CONSISTENT"""
    # Clamp value between 0 and 100
    value = max(0, min(100, value))
    
    # CONSISTENT: 0=red (fear), 100=green (greed)
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
    
    # Calculate the total angle coverage for the current value
    total_angle_coverage = math.pi * (value / 100)  # 0 to π radians
    
    # FIXED: Fill from left (π) to right (0) as value increases
    # Left side (π) = 0 = Red (Fear), Right side (0) = 100 = Green (Greed)
    segments = 100  # High resolution for smooth gradient
    
    if total_angle_coverage > 0:
        angle_per_segment = total_angle_coverage / segments
        
        for i in range(segments):
            # Calculate angles for this segment - filling from left to right
            # Start from π (left) and progress toward 0 (right)
            segment_start_angle = math.pi - (i * angle_per_segment)
            segment_end_angle = math.pi - ((i + 1) * angle_per_segment)
            
            # Map segment position to color value (left=0, right=100)
            segment_progress = i / segments  # 0 to 1
            segment_value = value * segment_progress  # 0 up to current value
        
            segment_color = get_perfected_fear_greed_color(segment_value)
            
            # Draw multiple layers for each segment for smooth appearance
            for thickness in range(12, 0, -2):
                alpha = int(255 * (13 - thickness) / 12 * 0.8)
                layer_color = (*segment_color, alpha)
                
                try:
                    arc_rect = pygame.Rect(20, 20, radius * 2, radius * 2)
                    pygame.draw.arc(fill_surface, layer_color[:3], arc_rect,
                                   segment_end_angle, segment_start_angle, thickness)
                except:
                    pass
    
    return fill_surface

def draw_fear_greed_chart(surface, fear_greed_data):
    """Draw refined Fear & Greed Index chart with enhanced design"""
    surface.fill(COLORS['panel_bg'])
    width, height = surface.get_size()
    
    value = fear_greed_data['value']
    label = fear_greed_data['label']
    timestamp = fear_greed_data['timestamp']
    yesterday_data = fear_greed_data['yesterday']
    last_week_data = fear_greed_data['last_week']
    last_month_data = fear_greed_data['last_month']
    last_updated = fear_greed_data.get('last_updated', None)
    
    # Professional title section with timestamp in top-right
    title_font = pygame.font.SysFont("Segoe UI", 18, bold=True)
    title_surface = title_font.render("Fear & Greed Index", True, (220, 230, 250))
    
    # Center title
    title_x = (width - title_surface.get_width()) // 2
    title_y = 12
    surface.blit(title_surface, (title_x, title_y))
    
    # Last updated timestamp (top-right)
    if last_updated:
        import time
        update_time = time.time()
        if hasattr(time, 'strftime'):
            try:
                formatted_time = time.strftime('%H:%M', time.localtime(last_updated))
                timestamp_text = f"Last Updated: {formatted_time}"
            except:
                timestamp_text = "Last Updated: --:--"
        else:
            timestamp_text = "Last Updated: --:--"
    else:
        timestamp_text = "Last Updated: --:--"
    
    timestamp_font = pygame.font.SysFont("Segoe UI", 10)
    timestamp_surface = timestamp_font.render(timestamp_text, True, (140, 160, 180))
    
    timestamp_x = width - timestamp_surface.get_width() - 10
    timestamp_y = 8
    surface.blit(timestamp_surface, (timestamp_x, timestamp_y))
    
    # Chart positioning - BETTER CENTERED
    chart_center_x = int(width * 0.40)
    chart_center_y = int(height * 0.48)
    chart_radius = min(width // 4.5, height // 3.5)
    chart_radius = max(chart_radius, 60)
    
    # Enhanced gauge background
    def render_perfected_gauge_background():
        """Render perfected gauge background"""
        bg_surface = pygame.Surface((chart_radius * 2 + 40, chart_radius * 2 + 40), pygame.SRCALPHA)
        
        for layer in range(15):
            layer_radius = chart_radius - layer
            if layer_radius <= 0:
                break
                
            layer_alpha = max(12, 90 - layer * 5)
            layer_color = (45, 55, 70, layer_alpha)
            
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
    
    # Value arc with smooth gradient fill
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
    
    # Enhanced historical data panel
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
    
    # Render historical data
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
    
    # REFINED: Shorter tick indicators positioned closer to center
    scale_points = [
        (0, "0", "Extreme Fear", (200, 40, 40)),
        (25, "25", "Fear", (255, 110, 50)),
        (50, "50", "Neutral", (255, 255, 70)),
        (75, "75", "Greed", (80, 255, 100)),
        (100, "100", "Extreme Greed", (60, 220, 80))
    ]
    
    # Draw SHORTER tick indicators positioned closer to center (50% shorter)
    for scale_value, scale_text, scale_desc, scale_color in scale_points:
        scale_angle = math.pi * (1 - scale_value / 100)
        
        # REFINED: Tick marks with gap from center value
        indicator_start_radius = chart_radius * 0.75  # Moved outward for gap (was 0.75)
        indicator_end_radius = chart_radius * 0.72    # Slightly adjusted end position
        
        start_x = chart_center_x + int(indicator_start_radius * math.cos(scale_angle))
        start_y = chart_center_y - int(indicator_start_radius * math.sin(scale_angle))
        end_x = chart_center_x + int(indicator_end_radius * math.cos(scale_angle))
        end_y = chart_center_y - int(indicator_end_radius * math.sin(scale_angle))
        
        # Draw shorter tick line
        pygame.draw.line(surface, scale_color, (start_x, start_y), (end_x, end_y), 2)
    
    # RESPONSIVE: Bottom labels positioned to fill available width evenly
    scale_y = chart_center_y + chart_radius + 30
    scale_descriptions = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]
    scale_numbers = ["0", "25", "50", "75", "100"]
    scale_colors = [(200, 40, 40), (255, 110, 50), (255, 255, 70), (80, 255, 100), (60, 220, 80)]
    
    # RESPONSIVE: Calculate expanded spacing to use more available width
    available_width = min(width * 0.8, chart_radius * 3)  # Use 80% of panel width or 3x radius
    labels_left = chart_center_x - available_width // 2
    
    # Font sizes for labels
    scale_font = pygame.font.SysFont("Segoe UI", 11, bold=True)
    desc_font = pygame.font.SysFont("Segoe UI", 10, bold=True)
    
    # Evenly distribute labels across expanded width
    for i in range(5):
        # Calculate position as percentage across expanded width (0%, 25%, 50%, 75%, 100%)
        position_ratio = i / 4
        x_pos = labels_left + (position_ratio * available_width)
        
        # Number with color
        num_surface = scale_font.render(scale_numbers[i], True, scale_colors[i])
        num_rect = num_surface.get_rect(center=(x_pos, scale_y))
        surface.blit(num_surface, num_rect)
        
        # Description below number
        desc_surface = desc_font.render(scale_descriptions[i], True, (170, 190, 210))
        desc_rect = desc_surface.get_rect(center=(x_pos, scale_y + 18))
        surface.blit(desc_surface, desc_rect)
    
    # Professional timestamp
    legend_start_y = scale_y + 45
    
    if timestamp:
        try:
            current_time = datetime.datetime.fromtimestamp(int(timestamp))
            time_text = f"Updated: {current_time.strftime('%b %d, %H:%M UTC')}"
            time_font = pygame.font.SysFont("Segoe UI", 9)
            time_surface = time_font.render(time_text, True, (120, 140, 160))
            
            time_x = (width - time_surface.get_width()) // 2
            time_y = legend_start_y
            if time_y + 15 < height - 5:
                surface.blit(time_surface, (time_x, time_y))
                legend_start_y += 20
        except:
            pass
    
    # Compact legend
    if legend_start_y + 15 < height - 5:
        legend_font = pygame.font.SysFont("Segoe UI", 9)
        legend_text = "Market sentiment: Red (Fear) → Yellow (Neutral) → Green (Greed)"
        legend_surface = legend_font.render(legend_text, True, (130, 150, 170))
        legend_rect = legend_surface.get_rect(center=(width // 2, legend_start_y))
        surface.blit(legend_surface, legend_rect)