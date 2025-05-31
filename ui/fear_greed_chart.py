"""
Fear & Greed Index chart component
"""

import pygame
import math
import datetime
from config.settings import COLORS

def get_fear_greed_label(value):
    """Get the label for a Fear & Greed Index value"""
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
    """Enhanced Fear & Greed Index chart"""
    surface.fill(COLORS['panel_bg'])
    width, height = surface.get_size()
    
    value = fear_greed_data['value']
    label = fear_greed_data['label']
    timestamp = fear_greed_data['timestamp']
    yesterday_data = fear_greed_data['yesterday']
    last_week_data = fear_greed_data['last_week']
    last_month_data = fear_greed_data['last_month']
    last_updated = fear_greed_data.get('last_updated', None)
    
    # Enhanced color mapping
    if value < 25:
        value_color = (255, 60, 60)
        gauge_color = (255, 40, 40)
    elif value < 45:
        value_color = (255, 140, 60)
        gauge_color = (255, 120, 40)
    elif value < 55:
        value_color = (255, 220, 60)
        gauge_color = (255, 200, 40)
    elif value < 75:
        value_color = (140, 255, 60)
        gauge_color = (120, 255, 40)
    else:
        value_color = (60, 255, 60)
        gauge_color = (40, 255, 40)
    
    # Title section
    title_font = pygame.font.SysFont("Arial", 16, bold=True)
    title_surface = title_font.render("Fear & Greed Index", True, COLORS['text_primary'])
    
    # Update status indicator
    if last_updated:
        import time
        time_since_update = time.time() - last_updated
        if time_since_update < 3600:
            status_color = COLORS['positive']
            status_text = "●"
        else:
            status_color = (255, 200, 100)
            status_text = "◐"
    else:
        status_color = COLORS['neutral']
        status_text = "○"
    
    status_font = pygame.font.SysFont("Arial", 12, bold=True)
    status_surface = status_font.render(status_text, True, status_color)
    
    # Center title at top
    title_x = (width - title_surface.get_width()) // 2
    title_y = 8
    surface.blit(title_surface, (title_x, title_y))
    surface.blit(status_surface, (title_x + title_surface.get_width() + 6, title_y + 2))
    
    # Chart section
    chart_center_x = int(width * 0.38)
    chart_center_y = height // 2 + 5
    chart_radius = min(width // 5, height // 4)
    chart_radius = max(chart_radius, 45)
    
    # Draw gauge background
    background_thickness = 10
    for i in range(background_thickness):
        bg_radius = chart_radius - i
        if bg_radius > 0:
            alpha = 120 - (i * 8)
            bg_color = (80, 80, 90, max(30, alpha))
            
            bg_surface = pygame.Surface((2 * chart_radius, 2 * chart_radius), pygame.SRCALPHA)
            pygame.draw.arc(bg_surface, bg_color,
                           (i, i, 2 * bg_radius, 2 * bg_radius),
                           0, math.pi, 3)
            surface.blit(bg_surface, (chart_center_x - chart_radius, chart_center_y - chart_radius))
    
    # Draw value arc
    angle = math.pi * (value / 100)
    arc_thickness = 12
    
    for i in range(arc_thickness):
        arc_radius = chart_radius - i
        if arc_radius > 0:
            intensity = 1.0 - (i / arc_thickness)
            alpha = int(255 * intensity * 0.9)
            
            current_color = tuple(int(c * intensity) for c in gauge_color) + (alpha,)
            
            arc_surface = pygame.Surface((2 * chart_radius, 2 * chart_radius), pygame.SRCALPHA)
            pygame.draw.arc(arc_surface, current_color,
                           (i, i, 2 * arc_radius, 2 * arc_radius),
                           0, angle, 4)
            surface.blit(arc_surface, (chart_center_x - chart_radius, chart_center_y - chart_radius))
    
    # Center value display
    value_font = pygame.font.SysFont("Arial", 22, bold=True)
    value_surface = value_font.render(str(value), True, COLORS['text_primary'])
    value_rect = value_surface.get_rect(center=(chart_center_x, chart_center_y))
    
    # Shadow effect
    shadow_surface = value_font.render(str(value), True, (50, 50, 50))
    shadow_rect = shadow_surface.get_rect(center=(chart_center_x + 1, chart_center_y + 1))
    surface.blit(shadow_surface, shadow_rect)
    surface.blit(value_surface, value_rect)
    
    # Label below value
    label_font = pygame.font.SysFont("Arial", 14, bold=True)
    label_surface = label_font.render(label, True, value_color)
    label_rect = label_surface.get_rect(center=(chart_center_x, chart_center_y + 25))
    surface.blit(label_surface, label_rect)
    
    # Historical data section
    hist_x = chart_center_x + chart_radius + 20
    hist_start_y = chart_center_y - 35
    
    hist_font = pygame.font.SysFont("Arial", 12, bold=True)
    line_height = 20
    
    def draw_historical_line(y_pos, period_label, period_value, period_label_text, change_value):
        if period_value is None:
            return y_pos
            
        if change_value > 0:
            change_color = COLORS['positive']
            change_symbol = "↑"
            change_text = f"+{change_value}"
        elif change_value < 0:
            change_color = COLORS['negative']
            change_symbol = "↓"
            change_text = f"{change_value}"
        else:
            change_color = COLORS['neutral']
            change_symbol = "→"
            change_text = "0"
        
        line_text = f"{period_label}: {period_value} ({period_label_text})"
        line_surface = hist_font.render(line_text, True, (220, 220, 220))
        surface.blit(line_surface, (hist_x, y_pos))
        
        change_full_text = f" {change_symbol}{change_text}"
        change_surface = hist_font.render(change_full_text, True, change_color)
        change_x = hist_x + line_surface.get_width() + 5
        
        if change_x + change_surface.get_width() <= width - 10:
            surface.blit(change_surface, (change_x, y_pos))
        
        return y_pos + line_height
    
    # Draw historical data
    current_y = hist_start_y
    
    if yesterday_data['value'] is not None:
        yesterday_label = yesterday_data['label'] if yesterday_data['label'] else get_fear_greed_label(yesterday_data['value'])
        current_y = draw_historical_line(current_y, "Yesterday", yesterday_data['value'], 
                                        yesterday_label, yesterday_data.get('change', 0))
    
    if last_week_data['value'] is not None:
        last_week_label = last_week_data['label'] if last_week_data['label'] else get_fear_greed_label(last_week_data['value'])
        current_y = draw_historical_line(current_y, "Last Week", last_week_data['value'], 
                                        last_week_label, last_week_data.get('change', 0))
    
    if last_month_data['value'] is not None:
        last_month_label = last_month_data['label'] if last_month_data['label'] else get_fear_greed_label(last_month_data['value'])
        current_y = draw_historical_line(current_y, "Last Month", last_month_data['value'], 
                                        last_month_label, last_month_data.get('change', 0))
    
    # Scale indicators
    scale_y = chart_center_y + chart_radius + 30
    scale_font = pygame.font.SysFont("Arial", 9, bold=True)
    desc_font = pygame.font.SysFont("Arial", 8)
    
    scale_points = [
        (0, "0", "Extreme Fear", (255, 60, 60)),
        (25, "25", "Fear", (255, 140, 60)),
        (50, "50", "Neutral", (255, 220, 60)),
        (75, "75", "Greed", (140, 255, 60)),
        (100, "100", "Extreme Greed", (60, 255, 60))
    ]
    
    for scale_value, scale_text, scale_desc, scale_color in scale_points:
        scale_angle = math.pi * (1 - scale_value / 100)
        
        scale_x = chart_center_x + int((chart_radius - 8) * math.cos(scale_angle))
        scale_marker_y = chart_center_y - int((chart_radius - 8) * math.sin(scale_angle))
        
        pygame.draw.circle(surface, scale_color, (scale_x, scale_marker_y), 3)
        
        text_x = chart_center_x - chart_radius + int((2 * chart_radius * scale_value) / 100)
        
        scale_surface = scale_font.render(scale_text, True, scale_color)
        number_rect = scale_surface.get_rect(center=(text_x, scale_y))
        surface.blit(scale_surface, number_rect)
        
        desc_surface = desc_font.render(scale_desc, True, (180, 180, 180))
        desc_rect = desc_surface.get_rect(center=(text_x, scale_y + 12))
        surface.blit(desc_surface, desc_rect)
    
    # Legend
    legend_y = scale_y + 35
    legend_font = pygame.font.SysFont("Arial", 9)
    legend_items = [
        "Market sentiment indicator based on volatility, momentum,", 
        "safe haven demand, junk bond demand, and social media sentiment"
    ]
    
    for i, legend_text in enumerate(legend_items):
        if legend_y + (i * 11) < height - 25:
            legend_surface = legend_font.render(legend_text, True, (120, 120, 120))
            legend_rect = legend_surface.get_rect(center=(chart_center_x, legend_y + (i * 11)))
            surface.blit(legend_surface, legend_rect)
    
    # Timestamp
    if timestamp:
        try:
            current_time = datetime.datetime.fromtimestamp(int(timestamp))
            time_text = f"Updated: {current_time.strftime('%b %d, %H:%M UTC')}"
            time_font = pygame.font.SysFont("Arial", 9)
            time_surface = time_font.render(time_text, True, (120, 120, 120))
            time_x = (width - time_surface.get_width()) // 2
            time_y = height - 12
            surface.blit(time_surface, (time_x, time_y))
        except:
            pass