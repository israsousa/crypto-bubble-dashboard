"""
News panel component
"""

import pygame
import datetime
from config.settings import COLORS, FONT_SIZES

def draw_news_panel(surface, news_data):
    """Draw enhanced news panel"""
    surface.fill(COLORS['panel_bg'])
    width, height = surface.get_size()
    
    # Title
    title_font = pygame.font.SysFont("Arial", 18, bold=True)
    title_surface = title_font.render("Latest Crypto News", True, COLORS['text_primary'])
    surface.blit(title_surface, (10, 10))
    
    if not news_data:
        no_news_font = pygame.font.SysFont("Arial", 14)
        no_news_surface = no_news_font.render("Loading news...", True, COLORS['neutral'])
        surface.blit(no_news_surface, (10, 50))
        return
    
    # Calculate items
    available_height = height - 60
    min_item_height = 120
    max_items = max(2, min(5, available_height // min_item_height))
    
    y_offset = 50
    item_height = available_height // max_items
    
    for i, news in enumerate(news_data[:max_items]):
        if y_offset + item_height > height:
            break
        
        # Background for news item
        item_rect = pygame.Rect(5, y_offset, width - 10, item_height - 5)
        pygame.draw.rect(surface, (30, 30, 35), item_rect, border_radius=8)
        
        # Title
        title = news.get('title', 'No Title')
        if len(title) > 70:
            title = title[:70] + "..."
        
        title_font = pygame.font.SysFont("Arial", 12, bold=True)
        
        # Word wrap for title
        padding = 10
        text_width = width - 30
        words = title.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if title_font.size(test_line)[0] < text_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        # Draw title lines
        title_y = y_offset + padding
        for line in lines[:2]:
            line_surface = title_font.render(line, True, (240, 240, 240))
            surface.blit(line_surface, (15, title_y))
            title_y += 16
        
        # Body text
        body = news.get('body', '')
        if not body:
            body = news.get('description', '')
        
        if body and item_height > 80:
            body = body[:150] + "..." if len(body) > 150 else body
            body_font = pygame.font.SysFont("Arial", 10)
            
            # Simple word wrap for body
            body_words = body.split()
            body_lines = []
            current_line = ""
            
            for word in body_words:
                test_line = current_line + word + " "
                if body_font.size(test_line)[0] < text_width:
                    current_line = test_line
                else:
                    if current_line:
                        body_lines.append(current_line.strip())
                    current_line = word + " "
            
            if current_line:
                body_lines.append(current_line.strip())
            
            # Draw body lines
            max_body_lines = min(2, (item_height - title_y + y_offset - 40) // 12)
            for line in body_lines[:max_body_lines]:
                line_surface = body_font.render(line, True, (190, 190, 190))
                surface.blit(line_surface, (15, title_y))
                title_y += 12
        
        # Source info
        source_info = news.get('source_info', {})
        source_name = source_info.get('name', 'Unknown Source')
        
        # Time formatting
        published_on = news.get('published_on', 0)
        if published_on:
            try:
                pub_time = datetime.datetime.fromtimestamp(published_on)
                time_str = pub_time.strftime("%H:%M")
                date_str = pub_time.strftime("%m/%d")
                time_info = f"{date_str} at {time_str}"
            except:
                time_info = "Recently"
        else:
            time_info = "Recently"
        
        # Source line
        source_font = pygame.font.SysFont("Arial", 11, bold=True)
        source_text = f"Source: {source_name}"
        source_surface = source_font.render(source_text, True, (150, 200, 255))
        surface.blit(source_surface, (15, y_offset + item_height - 35))
        
        # Time line
        time_font = pygame.font.SysFont("Arial", 11)
        time_text = f"Time: {time_info}"
        time_surface = time_font.render(time_text, True, COLORS['neutral'])
        surface.blit(time_surface, (15, y_offset + item_height - 20))
        
        y_offset += item_height