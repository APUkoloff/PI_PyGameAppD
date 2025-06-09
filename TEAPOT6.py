import pygame
import random
import sys
import os

# --- Constants ---

# Button icons
BUTTON_ICONS = {
    "next_turn": "next.png",
    "view_market": "market.png",
    "win_progress": "progress.png",
    "help": "help.png",
    "exit": "exit.png"
}

# Button dimensions (square)
BUTTON_SIZE_PCT = 0.09  # Increased from 0.06 to 0.09 (1.5x larger)
BUTTON_TOP_MARGIN_PCT = 0.01  # Reduced from 0.02 to 0.01 (closer to top)
BUTTON_SPACING_PCT = 0.01  # Reduced from 0.02 to 0.01 (closer together)
BUTTON_RIGHT_MARGIN_PCT = -0.00  # Reduced from 0.02 to 0.01 (closer to right edge)

# Percentages for UI elements (as decimals)
REGION_WIDTH_PCT = 0.15  # 15% of screen width
REGION_HEIGHT_PCT = 0.25  # 25% of screen height
REGION_BUTTON_WIDTH_PCT = 0.15  # Width of region buttons
REGION_BUTTON_HEIGHT_PCT = 0.085  # Increased from 0.08 to 0.09
REGION_BUTTON_TOP_MARGIN_PCT = 0.14
REGION_BUTTON_LEFT_MARGIN_PCT = 0.0  # 2% from left
REGION_ICON_SIZE_PCT = 0.08  # 8% of screen height (square)

# Resources window
RESOURCES_HEIGHT_PCT = 0.14  # Reduced from default to 15% of screen height

# Progress window
PROGRESS_WIDTH_PCT = 0.25  # 25% of screen width
PROGRESS_HEIGHT_PCT = 0.27  # 30% of screen height
PROGRESS_RIGHT_MARGIN_PCT = -0.00  # 1% from right
PROGRESS_TOP_MARGIN_PCT = 0.15  # 15% from top

# Game Log dimensions
GAME_LOG_WIDTH_PCT = 0.25  # 25% of screen width
GAME_LOG_HEIGHT_PCT = 0.25  # 25% of screen height
GAME_LOG_MARGIN_PCT = -0.00  # 1% margin from edges

# Region info window dimensions
REGION_INFO_WIDTH_PCT = 0.25  # 25% of screen width
REGION_INFO_HEIGHT_PCT = 0.6  # 60% of screen height

FONT_LARGE = 36
FONT_MEDIUM = 24
FONT_SMALL = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
YELLOW = (255, 255, 0)

# Region Information
REGIONS = {
    "Индонезия": {"tea_leaves_cost": 5.0, "labor_cost": 250, "tax_rate": 0.1, "potential_tea": 500, "icon": "indonesia.png"},
    "Индия": {"tea_leaves_cost": 6.0, "labor_cost": 300, "tax_rate": 0.12, "potential_tea": 600, "icon": "india.png"},
    "Китай": {"tea_leaves_cost": 7.5, "labor_cost": 325, "tax_rate": 0.15, "potential_tea": 700, "icon": "china.png"},
    "Турция": {"tea_leaves_cost": 6.5, "labor_cost": 310, "tax_rate": 0.13, "potential_tea": 550, "icon": "turkey.png"},
    "Кения": {"tea_leaves_cost": 4.0, "labor_cost": 200, "tax_rate": 0.08, "potential_tea": 450, "icon": "kenya.png"},
    "Германия": {"tea_leaves_cost": 10.0, "labor_cost": 400, "tax_rate": 0.20, "potential_tea": 800, "icon": "germany.png"},
    "Россия": {"tea_leaves_cost": 8.5, "labor_cost": 380, "tax_rate": 0.17, "potential_tea": 750, "icon": "russia.png"},
    "США": {"tea_leaves_cost": 12.5, "labor_cost": 450, "tax_rate": 0.25, "potential_tea": 700, "icon": "usa.png"},
    "Аргентина": {"tea_leaves_cost": 5.5, "labor_cost": 275, "tax_rate": 0.11, "potential_tea": 650, "icon": "argentina.png"},
    "Австралия": {"tea_leaves_cost": 9.0, "labor_cost": 425, "tax_rate": 0.18, "potential_tea": 850, "icon": "australia.png"},
}

# --- Classes ---
class Player:
    def __init__(self):
        self.name = "Player"
        self.money = 5000
        self.tea_leaves = 0
        self.processed_tea = 0
        self.equipment_multiplier = 1.0
        self.owned_tea_percentage = 0

    def hire_worker(self, region):
        if self.money >= region.labor_cost:
            self.money -= region.labor_cost
            region.update_worker_count(self.name, 1)
            return True
        return False

    def fire_worker(self, region):
        if region.get_worker_count(self.name) > 0:
            region.update_worker_count(self.name, -1)
            return True
        return False

    def get_total_tea(self):
        return self.tea_leaves + self.processed_tea

class Company:
    def __init__(self, name, money_multiplier=1.0, tea_multiplier=1.0):
        self.name = name
        # Increased starting resources based on multipliers
        self.money = random.randint(5000, 15000) * money_multiplier
        self.influence = {} # Region : Influence
        self.tea_leaves = random.randint(100, 300) * tea_multiplier
        self.processed_tea = random.randint(50, 150) * tea_multiplier
        self.workers = {}  # region: number_of_workers
        self.equipment_multiplier = random.uniform(1.2, 1.5)  # Companies start with better equipment
        self.owned_tea_percentage = 0
        self.aggressive_factor = random.uniform(1.5, 3.0)  # Companies are more aggressive in trading

    def add_influence(self, region, amount):
        if region not in self.influence:
            self.influence[region] = 0
        self.influence[region] = max(0, self.influence.get(region, 0) + amount)  # Ensure influence doesn't go below 0

    def get_total_tea(self):
        return self.processed_tea

    def hire_worker(self, region):
        """Hire a worker in the specified region."""
        # Companies are willing to spend more on workers
        if self.money >= region.labor_cost * 0.8:  # 20% discount on labor costs
            self.money -= region.labor_cost
            region.update_worker_count(self.name, 1)
            return True
        return False

    def fire_worker(self, region):
        """Fire a worker in the specified region."""
        if region.get_worker_count(self.name) > 0:
            region.update_worker_count(self.name, -1)
            return True
        return False


class Region:
    def __init__(self, name, data):
        self.name = name
        self.base_tea_leaves_cost = data["tea_leaves_cost"]
        self.base_labor_cost = data["labor_cost"]
        self.tax_rate = data["tax_rate"]
        self.potential_tea = data["potential_tea"]
        self.workers = {}  # company/player name : # workers
        self.current_tea_price = 7  # Initial price
        
        # Economic factors
        self.economic_stability = random.uniform(0.5, 1.5)  # Economic stability multiplier
        self.labor_market_pressure = random.uniform(0.5, 1.5)  # Labor market pressure
        self.agricultural_conditions = random.uniform(0.8, 1.2)  # Agricultural conditions
        self.market_development = random.uniform(0.8, 1.2)  # Market development level
        
        # Current costs (will be updated each turn)
        self.tea_leaves_cost = self.base_tea_leaves_cost * random.uniform(0.8, 1.2)
        self.labor_cost = self.base_labor_cost * random.uniform(0.8, 1.2)
        
        # Price ranges based on region's economic factors
        self.min_price = self.tea_leaves_cost * 5  # Minimum price is 5x the tea leaves cost
        self.max_price = self.tea_leaves_cost * 15  # Maximum price is 15x the tea leaves cost
        
    def update_economic_factors(self):
        """Update economic factors each turn."""
        # Randomly adjust economic factors with small variations
        self.economic_stability *= random.uniform(0.95, 1.05)  # ±5% change
        self.labor_market_pressure *= random.uniform(0.93, 1.07)  # ±7% change
        self.agricultural_conditions *= random.uniform(0.9, 1.1)  # ±10% change
        self.market_development *= random.uniform(0.95, 1.05)  # ±5% change
        
        # Keep factors within reasonable bounds
        self.economic_stability = max(0.6, min(1.4, self.economic_stability))
        self.labor_market_pressure = max(0.7, min(1.3, self.labor_market_pressure))
        self.agricultural_conditions = max(0.5, min(1.5, self.agricultural_conditions))
        self.market_development = max(0.8, min(1.2, self.market_development))
        
        # Update costs based on economic factors
        self.update_costs()
        
    def update_costs(self):
        """Update tea leaves and labor costs based on economic factors."""
        # Tea leaves cost affected by agricultural conditions and economic stability
        tea_leaves_multiplier = (self.agricultural_conditions * 0.7 + self.economic_stability * 0.3)
        self.tea_leaves_cost = self.base_tea_leaves_cost * tea_leaves_multiplier
        
        # Labor cost affected by labor market pressure and economic stability
        labor_multiplier = (self.labor_market_pressure * 0.6 + self.economic_stability * 0.4)
        self.labor_cost = int(self.base_labor_cost * labor_multiplier)
        
        # Update price ranges
        self.min_price = self.tea_leaves_cost * 5
        self.max_price = self.tea_leaves_cost * 15
        
    def randomize_price(self):
        """Randomize the tea price within region-specific range."""
        # Base random price
        base_random = random.uniform(self.min_price, self.max_price)
        
        # Apply economic factors
        economic_modifier = (
            self.economic_stability * 0.3 +  # 30% influence from economic stability
            self.market_development * 0.4 +  # 40% influence from market development
            self.agricultural_conditions * 0.3  # 30% influence from agricultural conditions
        ) / 3  # Normalize to a reasonable range
        
        # Add some market volatility (±20%)
        volatility = random.uniform(-0.2, 0.2)
        
        # Calculate final price
        final_price = base_random * economic_modifier * (1 + volatility)
        
        # Ensure price stays within bounds
        self.current_tea_price = max(self.min_price, min(self.max_price, final_price))
        return self.current_tea_price

    def get_worker_count(self, company_name):
        return self.workers.get(company_name, 0)

    def update_worker_count(self, company_name, count):
        if company_name not in self.workers:
             self.workers[company_name] = 0
        self.workers[company_name] += count

    def get_current_tea_price(self):
        return self.current_tea_price

    def harvest_tea(self, company, equipment_multiplier):
        """Calculate the amount of raw tea harvested."""
        worker_count = self.get_worker_count(company.name)
        if worker_count is None or worker_count <= 0:
            return 0

        base_output = worker_count * 100  # Base output per harvester
        return int(base_output * equipment_multiplier)  # Adjust by equipment multiplier

    def pack_tea(self, company, raw_tea, equipment_multiplier):
        """Calculate the amount of packed tea produced."""
        worker_count = self.get_worker_count(company.name)
        if worker_count is None or worker_count <= 0:
            return 0

        base_output = worker_count * 75  # Base output per packer
        packed_tea = min(raw_tea, int(base_output * equipment_multiplier))  # Limit to available raw tea
        return packed_tea

class Game:
    def __init__(self):
        pygame.init()
        
        # Get the display info and set up fullscreen
        display_info = pygame.display.Info()
        self.screen_width = display_info.current_w
        self.screen_height = display_info.current_h
        
        self.active_input_box = None  # Track which input box is active
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("Tea Empire")
        self.clock = pygame.time.Clock()
        
        # Load background image
        try:
            bg_path = os.path.join(os.path.dirname(__file__), "img", "background.jpg")
            self.background = pygame.image.load(bg_path)
            self.background = pygame.transform.scale(self.background, (self.screen_width*1.041, self.screen_height*1.041))
        except:
            print("Could not load background image")
            self.background = None

        # Initialize different font sizes
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        
        # Default font is medium size
        self.font = self.font_medium

        self.running = True
        self.current_region = None
        self.player = Player()
        # Create more aggressive competitor companies with higher starting resources
        self.companies = [
            Company(f"Компания {i+1}", 
                   money_multiplier=random.uniform(2.0, 3.0),  # 2-3x more starting money
                   tea_multiplier=random.uniform(1.5, 2.0)     # 1.5-2x more starting tea
            ) for i in range(3)
        ]
        
        self.regions = {name: Region(name, data) for name, data in REGIONS.items()}
        self.messages = []
        self.market_demand = 100000
        self.global_tea_supply = 0
        self.global_tea_demand = 0

        # Load button icons
        self.button_icons = {}
        img_dir = os.path.join(os.path.dirname(__file__), "img")
        for button_name, icon_file in BUTTON_ICONS.items():
            try:
                icon_path = os.path.join(img_dir, icon_file)
                icon = pygame.image.load(icon_path)
                button_size = int(BUTTON_SIZE_PCT * self.screen_height)
                self.button_icons[button_name] = pygame.transform.scale(icon, (button_size, button_size))
            except:
                print(f"Could not load icon for {button_name}")
                self.button_icons[button_name] = None

        # Initialize UI elements with percentage-based positions
        button_size = int(BUTTON_SIZE_PCT * self.screen_height)
        button_spacing = int(BUTTON_SPACING_PCT * self.screen_width)
        button_top = int(BUTTON_TOP_MARGIN_PCT * self.screen_height)
        button_right = self.screen_width - int(BUTTON_RIGHT_MARGIN_PCT * self.screen_width)

        # Create button rectangles in order from right to left
        self.exit_button_rect = pygame.Rect(button_right - button_size, button_top, button_size, button_size)
        self.help_button_rect = pygame.Rect(button_right - (button_size + button_spacing) * 2, button_top, button_size, button_size)
        self.win_conditions_button_rect = pygame.Rect(button_right - (button_size + button_spacing) * 3, button_top, button_size, button_size)
        self.view_market_button_rect = pygame.Rect(button_right - (button_size + button_spacing) * 4, button_top, button_size, button_size)
        self.next_turn_button_rect = pygame.Rect(button_right - (button_size + button_spacing) * 5, button_top, button_size, button_size)

        # Store button hover state
        self.hovered_button = None

        self.game_over = False
        self.winner = None
        self.target_money = 500000  # Increased from 100,000 to 300,000
        self.monopoly_threshold = 0.6  # 60% market share requirement
        self.turn_count = 0  # Track number of turns played

        # Set up initial market prices
        self.update_market_prices()

        # Flags to show popup windows
        self.showing_help = True
        self.showing_win_conditions = False

        # Help text placeholder
        self.help_text_lines = [
            "Справка",
            "",
            "1. Для действий с регионами используйте мышь или клавиши UP/DOWN",
            "2. Для производства чая наймите рабочих",
            "3. Или купите листья для переработки их в чай",
            "4. Продайте имеющийся чай",
            "5. Итоговая прибыль может оказаться меньше (см. налоговую ставку)",
            "6. Нажмите кнопку следующий ход",
            "",
            "Критерии победы:",
            "- Достаточно достигнуть одного из них:",
            f"  ${self.target_money:,} или Контроль над {int(self.monopoly_threshold * 100)}% рынка",
            "- Победа возможна после 7 ходов при условии,",
            " что общее предложение больше общего спроса",
            "",
            "Нажмите, чтобы закрыть"
        ]

        # Load region icons
        self.region_icons = {}
        img_dir = os.path.join(os.path.dirname(__file__), "img")
        for region_name, region_data in REGIONS.items():
            icon_path = os.path.join(img_dir, region_data["icon"])
            try:
                icon = pygame.image.load(icon_path)
                icon_size = int(REGION_ICON_SIZE_PCT * self.screen_height)
                self.region_icons[region_name] = pygame.transform.scale(icon, (icon_size, icon_size))
            except:
                print(f"Could not load icon for {region_name}")
                self.region_icons[region_name] = None

        # Calculate region button positions
        self.region_buttons = {}
        button_height = self.screen_height * REGION_BUTTON_HEIGHT_PCT
        total_buttons = len(REGIONS)
        start_y = self.screen_height * REGION_BUTTON_TOP_MARGIN_PCT
        
        for i, region_name in enumerate(REGIONS.keys()):
            y_pos = start_y + (i * button_height)
            self.region_buttons[region_name] = pygame.Rect(
                self.screen_width * REGION_BUTTON_LEFT_MARGIN_PCT,
                y_pos,
                self.screen_width * REGION_BUTTON_WIDTH_PCT,
                button_height
            )

        # Progress window position
        self.progress_rect = pygame.Rect(
            self.screen_width * (1 - PROGRESS_WIDTH_PCT - PROGRESS_RIGHT_MARGIN_PCT),
            self.screen_height * PROGRESS_TOP_MARGIN_PCT,
            self.screen_width * PROGRESS_WIDTH_PCT,
            self.screen_height * PROGRESS_HEIGHT_PCT
        )

        # Initialize current region index for keyboard navigation
        self.current_region_index = 0
        self.region_names = list(REGIONS.keys())

        # Game log properties
        self.message_scroll_offset = 0  # How many messages to skip from bottom
        self.max_visible_messages = 10  # Maximum number of visible messages
        self.game_log_rect = pygame.Rect(
            self.screen_width * (1 - GAME_LOG_WIDTH_PCT - GAME_LOG_MARGIN_PCT),  # X position
            self.screen_height * (1 - GAME_LOG_HEIGHT_PCT - GAME_LOG_MARGIN_PCT),  # Y position
            self.screen_width * GAME_LOG_WIDTH_PCT,  # Width
            self.screen_height * GAME_LOG_HEIGHT_PCT  # Height
        )
        self.scroll_up_rect = pygame.Rect(
            self.game_log_rect.right - 30,  # X position
            self.game_log_rect.top + 5,  # Y position
            25,  # Width
            25   # Height
        )
        self.scroll_down_rect = pygame.Rect(
            self.game_log_rect.right - 30,  # X position
            self.game_log_rect.bottom - 30,  # Y position
            25,  # Width
            25   # Height
        )

    def check_win_condition(self):
        """Check if victory conditions are met."""
        # Must meet EITHER conditions to win
        money_condition = self.player.money >= self.target_money
        
        # Calculate market share
        total_tea = self.player.get_total_tea()
        for company in self.companies:
            total_tea += company.get_total_tea()

        if total_tea > 0: # only calculate if tea exists
            self.player.owned_tea_percentage = self.player.get_total_tea() / total_tea
            for company in self.companies:
                company.owned_tea_percentage = company.get_total_tea() / total_tea

            market_share_condition = self.player.owned_tea_percentage >= self.monopoly_threshold
            
            # Only win if BOTH conditions are met and at least 3 turns have passed
            if self.turn_count >= 7:
                if money_condition or market_share_condition:
                    self.game_over = True
                    self.winner = self.player.name

        return self.game_over

    def check_lose_condition(self):
        if self.player.money <= 0:
            self.game_over = True
            self.winner = "Оставшиеся" # loose by money

        # check if competitor wins
        for company in self.companies:
            if company.money >= self.target_money or company.owned_tea_percentage >= self.monopoly_threshold:
                self.game_over = True
                self.winner = company.name # loose by competitor
        return self.game_over

    def update_market_prices(self):
        # Calculate total supply and demand
        total_supply = self.player.get_total_tea()
        for company in self.companies:
            total_supply += company.get_total_tea()
        self.global_tea_supply = total_supply

        if total_supply == 0:
            self.global_tea_supply = 1  # avoid division by zero
            self.global_tea_demand = self.market_demand  # initial demand
        else:
            self.global_tea_demand = self.market_demand

        # Calculate global market pressure (affects volatility)
        market_pressure = self.global_tea_demand / self.global_tea_supply if self.global_tea_supply > 0 else 2.0
        
        # Update each region's price independently
        for region in self.regions.values():
            # Randomize base price
            base_price = region.randomize_price()
            
            # Apply market pressure (±30% effect)
            pressure_effect = (market_pressure - 1.0) * 0.3
            final_price = base_price * (1 + pressure_effect)
            
            # Ensure price stays within region's bounds
            region.current_tea_price = max(region.min_price, min(region.max_price, final_price))
            
        # Add message about price changes
        #self.add_message("Tea prices have been updated in all regions!")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False  # Exit on ESC
                elif event.key == pygame.K_UP:
                    # Navigate to previous region
                    self.current_region_index = (self.current_region_index - 1) % len(self.region_names)
                    self.current_region = self.region_names[self.current_region_index]
                elif event.key == pygame.K_DOWN:
                    # Navigate to next region
                    self.current_region_index = (self.current_region_index + 1) % len(self.region_names)
                    self.current_region = self.region_names[self.current_region_index]
            elif event.type == pygame.VIDEORESIZE:
                if not (self.screen.get_flags() & pygame.FULLSCREEN):
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.screen_width = event.w
                    self.screen_height = event.h
                    self.update_ui_elements()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                # Handle game log scrolling
                if len(self.messages) > self.max_visible_messages:
                    if self.scroll_up_rect.collidepoint(mouse_pos):
                        if self.message_scroll_offset < len(self.messages) - self.max_visible_messages:
                            self.message_scroll_offset += 1
                    elif self.scroll_down_rect.collidepoint(mouse_pos):
                        if self.message_scroll_offset > 0:
                            self.message_scroll_offset -= 1
                    elif self.game_log_rect.collidepoint(mouse_pos):
                        # Scroll with mouse wheel in log area
                        if event.button == 4:  # Mouse wheel up
                            if self.message_scroll_offset < len(self.messages) - self.max_visible_messages:
                                self.message_scroll_offset += 1
                        elif event.button == 5:  # Mouse wheel down
                            if self.message_scroll_offset > 0:
                                self.message_scroll_offset -= 1
                
                # Handle region clicks
                self.handle_region_clicks(mouse_pos)
                
                # Handle button clicks
                if self.next_turn_button_rect.collidepoint(mouse_pos):
                    self.next_turn()
                elif self.exit_button_rect.collidepoint(mouse_pos):
                    self.running = False
                elif self.view_market_button_rect.collidepoint(mouse_pos):
                    self.show_market_information()
                elif self.help_button_rect.collidepoint(mouse_pos):
                    self.showing_help = True
                elif self.win_conditions_button_rect.collidepoint(mouse_pos):
                    self.showing_win_conditions = True
                # Handle other clicks
                elif self.showing_help:
                    self.showing_help = False
                elif self.showing_win_conditions:
                    self.showing_win_conditions = False
                else:
                    self.handle_region_clicks(mouse_pos)

                # Check if input box is clicked
                if self.active_input_box and self.active_input_box.collidepoint(mouse_pos):
                    self.active_input_box = self.active_input_box  # Keep it active
                else:
                    self.active_input_box = None  # Deactivate if clicked outside

            # Handle keyboard events for the input box
            if self.active_input_box and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.active_input_box = None  # Deactivate on enter
                elif event.key == pygame.K_BACKSPACE:
                    # Logic to remove last character from input
                    if self.current_region:
                        self.regions[self.current_region].bribes = self.regions[self.current_region].bribes // 10  # Simple way to remove last digit
                elif event.unicode.isdigit():  # Only numbers
                    if self.current_region:
                        self.regions[self.current_region].bribes = self.regions[self.current_region].bribes * 10 + int(event.unicode)  # Update bribe amount

    def update_ui_elements(self):
        """Update all UI elements based on current screen dimensions"""
        button_size = int(BUTTON_SIZE_PCT * self.screen_height)
        button_spacing = int(BUTTON_SPACING_PCT * self.screen_width)
        button_top = int(BUTTON_TOP_MARGIN_PCT * self.screen_height)
        button_right = self.screen_width - int(BUTTON_RIGHT_MARGIN_PCT * self.screen_width)

        # Update button positions and sizes
        self.exit_button_rect = pygame.Rect(button_right - button_size, button_top, button_size, button_size)
        self.help_button_rect = pygame.Rect(button_right - (button_size + button_spacing) * 2, button_top, button_size, button_size)
        self.win_conditions_button_rect = pygame.Rect(button_right - (button_size + button_spacing) * 3, button_top, button_size, button_size)
        self.view_market_button_rect = pygame.Rect(button_right - (button_size + button_spacing) * 4, button_top, button_size, button_size)
        self.next_turn_button_rect = pygame.Rect(button_right - (button_size + button_spacing) * 5, button_top, button_size, button_size)
        
        # Update font size
        self.font = self.font_medium

    def handle_region_clicks(self, mouse_pos):
        for i, (region_name, button_rect) in enumerate(self.region_buttons.items()):
            if button_rect.collidepoint(mouse_pos):
                self.current_region = region_name
                self.current_region_index = i
                break

    def draw(self):
        # Draw background
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(WHITE)

        self.update_button_hover()  # Update hover state
        self.draw_resources()
        self.draw_map()
        self.draw_game_log()
        self.draw_progress_window()
        
        # Draw all buttons
        self.draw_next_turn_button()
        self.draw_view_market_button()
        self.draw_win_conditions_button()
        self.draw_help_button()
        self.draw_exit_button()
        
        # Draw hover text last so it appears on top
        self.draw_button_hover_text()

        if self.current_region:
            self.draw_region_window(self.current_region)

        if self.showing_help:
            self.show_help()

        if self.showing_win_conditions:
            self.show_win_conditions()

        if self.game_over:
            self.draw_game_over_screen()

        pygame.display.flip()

    def draw_next_turn_button(self):
        #pygame.draw.rect(self.screen, WHITE, self.next_turn_button_rect)
        #pygame.draw.rect(self.screen, GRAY, self.next_turn_button_rect, 2)
        if self.button_icons["next_turn"]:
            self.screen.blit(self.button_icons["next_turn"], self.next_turn_button_rect)

    def draw_exit_button(self):
        #pygame.draw.rect(self.screen, WHITE, self.exit_button_rect)
        #pygame.draw.rect(self.screen, GRAY, self.exit_button_rect, 2)
        if self.button_icons["exit"]:
            self.screen.blit(self.button_icons["exit"], self.exit_button_rect)

    def draw_view_market_button(self):
        #pygame.draw.rect(self.screen, WHITE, self.view_market_button_rect)
        #pygame.draw.rect(self.screen, GRAY, self.view_market_button_rect, 2)
        if self.button_icons["view_market"]:
            self.screen.blit(self.button_icons["view_market"], self.view_market_button_rect)

    def draw_help_button(self):
        #pygame.draw.rect(self.screen, WHITE, self.help_button_rect)
        #pygame.draw.rect(self.screen, GRAY, self.help_button_rect, 2)
        if self.button_icons["help"]:
            self.screen.blit(self.button_icons["help"], self.help_button_rect)

    def draw_win_conditions_button(self):
        #pygame.draw.rect(self.screen, WHITE, self.win_conditions_button_rect)
        #pygame.draw.rect(self.screen, GRAY, self.win_conditions_button_rect, 2)
        if self.button_icons["win_progress"]:
            self.screen.blit(self.button_icons["win_progress"], self.win_conditions_button_rect)

    def draw_button_hover_text(self):
        if self.hovered_button:
            mouse_pos = pygame.mouse.get_pos()
            hover_texts = {
                "next_turn": "Следующий ход",
                "view_market": "Рынок",
                "win_progress": "Прогресс",
                "help": "Справка",
                "exit": "Выход"
            }
            text = self.font_large.render(hover_texts[self.hovered_button], True, BLACK)
            text_rect = text.get_rect()
            # Position text above the cursor
            text_rect.midbottom = (mouse_pos[0], mouse_pos[1] - 10)
            # Ensure text stays within screen bounds
            if text_rect.left < 0:
                text_rect.left = 0
            if text_rect.right > self.screen_width:
                text_rect.right = self.screen_width
            if text_rect.top < 0:
                text_rect.top = 0
            # Draw text with white background for better visibility
            padding = 5
            bg_rect = text_rect.inflate(padding * 2, padding * 2)
            pygame.draw.rect(self.screen, WHITE, bg_rect)
            pygame.draw.rect(self.screen, GRAY, bg_rect, 1)
            self.screen.blit(text, text_rect)

    def update_button_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        # Check each button in order
        if self.next_turn_button_rect.collidepoint(mouse_pos):
            self.hovered_button = "next_turn"
        elif self.view_market_button_rect.collidepoint(mouse_pos):
            self.hovered_button = "view_market"
        elif self.win_conditions_button_rect.collidepoint(mouse_pos):
            self.hovered_button = "win_progress"
        elif self.help_button_rect.collidepoint(mouse_pos):
            self.hovered_button = "help"
        elif self.exit_button_rect.collidepoint(mouse_pos):
            self.hovered_button = "exit"
        else:
            self.hovered_button = None

    def show_help(self):
        # Semi-transparent overlay covering the entire screen
        overlay = pygame.Surface((self.screen_width+80, self.screen_height+50))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # Help window dimensions - make it taller
        width = int(0.55 * self.screen_width)
        height = int(0.8 * self.screen_height)  # Increased from 0.7 to 0.85
        x = (self.screen_width - width) // 2
        y = (self.screen_height - height) // 2
        pygame.draw.rect(self.screen, WHITE, (x, y, width, height))
        pygame.draw.rect(self.screen, BLACK, (x, y, width, height), 3)

        # Render help text lines with more spacing
        text_y = y + 40  # Increased initial padding
        title = self.font_large.render("Справка", True, BLACK)
        title_x = x + (width - title.get_width()) // 2  # Center the title
        self.screen.blit(title, (title_x, text_y))
        text_y += 60  # More space after title

        for line in self.help_text_lines[2:]:  # Skip the first two lines as we handled the title
            if line == "":  # Add more spacing for empty lines
                text_y += 20
                continue
            text_surface = self.font_medium.render(line, True, BLACK)
            # Center shorter lines, left-align longer ones
            if len(line) < 20:  # Adjust this threshold as needed
                text_x = x + (width - text_surface.get_width()) // 2
            else:
                text_x = x + 40  # Left margin for longer lines
            self.screen.blit(text_surface, (text_x, text_y))
            text_y += 35  # Increased line spacing

    def show_win_conditions(self):
        # Semi-transparent overlay covering the entire screen
        overlay = pygame.Surface((self.screen_width+80, self.screen_height+50))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # Win conditions window - wider
        width = int(0.4 * self.screen_width)
        height = int(0.8 * self.screen_height)
        x = (self.screen_width - width) // 2
        y = (self.screen_height - height) // 2
        pygame.draw.rect(self.screen, WHITE, (x, y, width, height))
        pygame.draw.rect(self.screen, BLACK, (x, y, width, height), 3)

        text_y = y + 40
        title = self.font_large.render("Прогресс", True, BLACK)
        title_x = x + (width - title.get_width()) // 2  # Center the title
        self.screen.blit(title, (title_x, text_y))
        text_y += 60

        # Show current turn
        turn_text = self.font_medium.render(f"Ход: {self.turn_count}", True, BLACK)
        self.screen.blit(turn_text, (x + 40, text_y))
        text_y += 40

        # Show player money progress
        player_money_text = self.font_medium.render(f"Деньги игрока: ${self.player.money:,.2f} / ${self.target_money:,.2f}", True, BLACK)
        self.screen.blit(player_money_text, (x + 40, text_y))
        text_y += 40

        # Show player monopoly progress
        player_monopoly = self.player.owned_tea_percentage * 100
        monopoly_text = self.font_medium.render(f"Доля игрока: {player_monopoly:.2f}% / {self.monopoly_threshold*100}%", True, BLACK)
        self.screen.blit(monopoly_text, (x + 40, text_y))
        text_y += 60

        # Competitors progress
        title = self.font_medium.render("Прогресс конкурентов:", True, BLACK)
        self.screen.blit(title, (x + 40, text_y))
        text_y += 40

        for company in self.companies:
            money_text = self.font_medium.render(f"Деньги {company.name}: ${company.money:,.2f} / ${self.target_money:,.2f}", True, BLACK)
            self.screen.blit(money_text, (x + 60, text_y))
            text_y += 35
            share = company.owned_tea_percentage * 100
            share_text = self.font_medium.render(f"Доля {company.name}: {share:.2f}% / {self.monopoly_threshold*100}%", True, BLACK)
            self.screen.blit(share_text, (x + 60, text_y))
            text_y += 50

    def show_market_information(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width+80, self.screen_height+50))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # Market information window
        width = int(0.5 * self.screen_width)
        height = int(0.9 * self.screen_height)
        x = (self.screen_width - width) // 2
        y = (self.screen_height - height) // 2
        
        # Semi-transparent window background
        window_bg = pygame.Surface((width, height))
        window_bg.fill((255, 255, 255, 255))
        self.screen.blit(window_bg, (x, y))

        text_y = y + 40
        title = self.font_large.render("Информация о рынке", True, BLACK)
        title_x = x + (width - title.get_width()) // 2
        self.screen.blit(title, (title_x, text_y))
        text_y += 60

        # Global market information
        text_x = x + 40
        
        # Total Tea Supply
        total_supply_text = self.font_medium.render(f"Общее предложение чая: {self.global_tea_supply:.2f}", True, BLACK)
        self.screen.blit(total_supply_text, (text_x, text_y))
        text_y += 40

        # Market Demand
        market_demand_text = self.font_medium.render(f"Общий спрос на чай: {self.global_tea_demand}", True, BLACK)
        self.screen.blit(market_demand_text, (text_x, text_y))
        text_y += 60

        # Table headers
        col_width_region = int(width * 0.4)  # 40% for region names
        col_width_price = int(width * 0.15)  # 15% for each price column
        header_x = text_x

        # Draw table headers
        headers = ["Регионы", "Сырье", "Рабочие", "Чай"]
        col_widths = [col_width_region, col_width_price, col_width_price, col_width_price]
        
        for header, col_width in zip(headers, col_widths):
            header_text = self.font_medium.render(header, True, BLACK)
            self.screen.blit(header_text, (header_x, text_y))
            header_x += col_width
        text_y += 40

        # Draw horizontal line under headers
        pygame.draw.line(self.screen, BLACK, (text_x, text_y), (text_x + sum(col_widths), text_y), 2)
        text_y += 20

        # Table content
        for region_name, region in self.regions.items():
            col_x = text_x
            
            # Region name (left-aligned)
            region_text = self.font_medium.render(region_name, True, BLACK)
            self.screen.blit(region_text, (col_x, text_y))
            col_x += col_width_region
            
            # Leaves cost
            leaves_cost_text = self.font_medium.render(f"${region.tea_leaves_cost:.2f}", True, BLACK)
            self.screen.blit(leaves_cost_text, (col_x, text_y))
            col_x += col_width_price
            
            # Worker cost
            worker_cost_text = self.font_medium.render(f"${region.labor_cost:.2f}", True, BLACK)
            self.screen.blit(worker_cost_text, (col_x, text_y))
            col_x += col_width_price
            
            # Tea price
            price_text = self.font_medium.render(f"${region.current_tea_price:.2f}", True, BLACK)
            self.screen.blit(price_text, (col_x, text_y))
            
            text_y += 35

        # Close instruction at the bottom
        close_text = self.font_medium.render("Нажмите, чтобы закрыть", True, BLACK)
        close_x = x + (width - close_text.get_width()) // 2
        close_y = y + height - 60
        self.screen.blit(close_text, (close_x, close_y))

        pygame.display.flip()

        # Wait for click or key to close
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False

    def draw_game_over_screen(self):
        """Draws the game over screen with the winner."""
        overlay = pygame.Surface((self.screen_width+80, self.screen_height+50), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, int(0.048 * self.screen_height))
        if self.winner:
            text = font.render(f"Победитель - {self.winner}!", True, WHITE)
        else:
             text = font.render(f"Игра окончена!", True, WHITE)
        text_rect = text.get_rect(center=(int(0.5 * self.screen_width), int(0.5 * self.screen_height)))
        self.screen.blit(text, text_rect)

        restart_text = font.render("Нажмите любую клавишу для выхода", True, WHITE)
        restart_rect = restart_text.get_rect(center=(int(0.5 * self.screen_width), int(0.5 * self.screen_height + 50)))
        self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                    self.running = False

    def next_turn(self):
        if not self.game_over:
            self.turn_count += 1  # Increment turn count
            self.process_turn()
            self.update_market_prices()
            self.messages.append(f"--- Ход {self.turn_count} ---")
            
            # Check win/lose conditions after each turn
            if self.check_win_condition():
                self.showing_win_conditions = True
                self.messages.append(f"{self.winner} выиграл игру!")
            elif self.check_lose_condition():
                self.showing_win_conditions = True
                self.messages.append(f"Игра окончена! Победитель: {self.winner}!")
            else:
                # Show progress towards victory conditions
                money_progress = (self.player.money / self.target_money) * 100
                market_share = (self.player.owned_tea_percentage * 100)
                #self.messages.append(f"Прогресс - Деньги: {money_progress:.1f}%, Доля на рынке: {market_share:.1f}%")
                self.showing_win_conditions = True

    def draw_resources(self):
        # Create a background rectangle for resources with reduced height
        padding = 20
        col_spacing = 20
        
        # Calculate dimensions for the two columns
        left_col_width = 0
        right_col_width = 0
        
        # Left column labels
        money_label = "Деньги:"
        leaves_label = "Чайные листья:"
        tea_label = "Чай:"
        
        # Calculate maximum width needed for labels
        label_surfaces = [
            self.font_medium.render(label, True, BLACK)
            for label in [money_label, leaves_label, tea_label]
        ]
        left_col_width = max(surface.get_width() for surface in label_surfaces)
        
        # Calculate values for right column
        money_text = f"${self.player.money:,.2f}"
        leaves_text = str(self.player.tea_leaves)
        tea_text = str(self.player.processed_tea)
        
        # Calculate maximum width needed for values
        value_surfaces = [
            self.font_medium.render(text, True, BLACK)
            for text in [money_text, leaves_text, tea_text]
        ]
        right_col_width = max(surface.get_width() for surface in value_surfaces)
        
        # Calculate total width and height
        total_width = left_col_width + col_spacing + right_col_width + padding * 2
        total_height = int(self.screen_height * RESOURCES_HEIGHT_PCT)

        # Create semi-transparent background
        bg_surface = self.create_semi_transparent_surface(total_width, total_height)
        self.screen.blit(bg_surface, (0, 0))
        pygame.draw.rect(self.screen, GRAY, (0, 0, total_width, total_height), 2)
        
        # Draw text
        y = padding
        for label, value in [
            (money_label, money_text),
            (leaves_label, leaves_text),
            (tea_label, tea_text)
        ]:
            label_surface = self.font_medium.render(label, True, BLACK)
            value_surface = self.font_medium.render(value, True, BLACK)
            self.screen.blit(label_surface, (padding, y))
            self.screen.blit(value_surface, (padding + left_col_width + col_spacing, y))
            y += self.font_medium.get_height() + 5

    def draw_map(self):
        for region_name, button_rect in self.region_buttons.items():
            # Draw semi-transparent white button background
            bg_surface = self.create_semi_transparent_surface(button_rect.width, button_rect.height)
            self.screen.blit(bg_surface, button_rect)
            pygame.draw.rect(self.screen, GRAY, button_rect, 2)
            
            # Draw region name (left-aligned) with medium font
            region_text = self.font_medium.render(region_name, True, BLACK)
            text_x = button_rect.x + 10
            text_y = button_rect.centery - region_text.get_height() // 2
            self.screen.blit(region_text, (text_x, text_y))
            
            # Draw region icon if available
            if self.region_icons[region_name]:
                icon_size = int(REGION_ICON_SIZE_PCT * self.screen_height)
                icon_x = button_rect.right - icon_size - 10
                icon_y = button_rect.centery - icon_size // 2
                self.screen.blit(self.region_icons[region_name], (icon_x, icon_y))

    def draw_region_window(self, region_name):
        region = self.regions[region_name]
        mouse_pos = pygame.mouse.get_pos()
        
        # Center the window in the middle of the screen
        window_width = int(REGION_INFO_WIDTH_PCT * self.screen_width)
        window_height = int(REGION_INFO_HEIGHT_PCT * self.screen_height)
        x = (self.screen_width - window_width) // 2
        y = (self.screen_height - window_height) // 2
        
        # Draw white background with border
        bg_surface = self.create_semi_transparent_surface(window_width, window_height)
        self.screen.blit(bg_surface, (x, y))
        #pygame.draw.rect(self.screen, WHITE, (x, y, window_width, window_height))
        #pygame.draw.rect(self.screen, GRAY, (x, y, window_width, window_height), 2)

        text_color = BLACK
        text_x = x + window_width * 0.05  # 5% margin from left
        text_y = y + window_height * 0.05  # 5% margin from top

        # Region Name - Large font
        region_name_text = self.font_large.render(f"Регион: {region_name}", True, text_color)
        self.screen.blit(region_name_text, (text_x, text_y))
        text_y += 50  # Larger spacing after title

        # Stats - Medium font with increased spacing
        tea_cost_text = self.font_medium.render(f"Цена сырья: ${region.tea_leaves_cost:,.2f}", True, text_color)
        self.screen.blit(tea_cost_text, (text_x, text_y))
        text_y += 40

        labor_cost_text = self.font_medium.render(f"Заработная плата: ${region.labor_cost:,.2f}", True, text_color)
        self.screen.blit(labor_cost_text, (text_x, text_y))
        text_y += 40

        current_price_text = self.font_medium.render(f"Цена чая: ${region.current_tea_price:,.2f}", True, text_color)
        self.screen.blit(current_price_text, (text_x, text_y))
        text_y += 40

        # Workers info - Small font with appropriate spacing
        player_workers_text = self.font_small.render(f"Рабочие игрока: {region.get_worker_count(self.player.name)}", True, text_color)
        self.screen.blit(player_workers_text, (text_x, text_y))
        text_y += 30

        for company in self.companies:
            company_workers_text = self.font_small.render(f"Рабочие {company.name}: {region.get_worker_count(company.name)}", True, text_color)
            self.screen.blit(company_workers_text, (text_x, text_y))
            text_y += 30

        # Tax Rate
        tax_rate = region.tax_rate
        tax_rate_text = self.font_medium.render(f"Налоговая ставка: {tax_rate:.2f}", True, text_color)
        self.screen.blit(tax_rate_text, (text_x, text_y))
        text_y += 40

        # Buttons section at the bottom of the window
        button_section_y = y + window_height - window_height * 0.25  # Start buttons 25% from bottom
        button_width = int(window_width * 0.2)  # 20% of window width
        button_height = int(window_height * 0.08)  # 8% of window height
        button_margin = 20

        # Hire/Fire Buttons
        hire_button_rect = pygame.Rect(text_x, button_section_y, button_width*2, button_height)
        fire_button_rect = pygame.Rect(text_x + button_width*2 + button_margin, button_section_y, button_width*2, button_height)

        pygame.draw.rect(self.screen, BLUE, hire_button_rect)
        pygame.draw.rect(self.screen, BLUE, fire_button_rect)

        hire_text = self.font_medium.render("Hire Worker", True, WHITE)
        fire_text = self.font_medium.render("Fire Worker", True, WHITE)
        self.screen.blit(hire_text, (hire_button_rect.centerx - hire_text.get_width()//2, hire_button_rect.centery - hire_text.get_height()//2))
        self.screen.blit(fire_text, (fire_button_rect.centerx - fire_text.get_width()//2, fire_button_rect.centery - fire_text.get_height()//2))

        # Buy/Sell buttons
        button_section_y += button_height + button_margin
        buy_leaves_button_rect = pygame.Rect(text_x, button_section_y, button_width * 2, button_height)
        sell_tea_button_rect = pygame.Rect(text_x + button_width * 2 + button_margin, button_section_y, button_width * 2, button_height)

        pygame.draw.rect(self.screen, BLUE, buy_leaves_button_rect)
        pygame.draw.rect(self.screen, BLUE, sell_tea_button_rect)

        buy_text = self.font_medium.render("Купить сырье", True, WHITE)
        sell_text = self.font_medium.render("Продать чай", True, WHITE)
        self.screen.blit(buy_text, (buy_leaves_button_rect.centerx - buy_text.get_width()//2, buy_leaves_button_rect.centery - buy_text.get_height()//2))
        self.screen.blit(sell_text, (sell_tea_button_rect.centerx - sell_text.get_width()//2, sell_tea_button_rect.centery - sell_text.get_height()//2))

        # Check for button clicks inside the region window
        if self.current_region:
            if buy_leaves_button_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                self.buy_tea_leaves(region_name)
            if sell_tea_button_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                self.sell_tea(region_name)
            if hire_button_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                self.hire_worker(region_name)
            if fire_button_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                self.fire_worker(region_name)

    def buy_tea_leaves(self, region_name):
        region = self.regions[region_name]
        buy_amount = 100 # simplified, buying only 100 leaves
        cost = region.tea_leaves_cost * buy_amount
        if self.player.money >= cost:
            self.player.money -= cost
            self.player.tea_leaves += buy_amount  # Assuming green tea for simplicity
            #self.add_message(f"Куплено {buy_amount} чайных листьев в {region_name} за ${cost:,.2f}")
        #else:
            #self.add_message("Недостаточно средств для покупки.")

    def sell_tea(self, region_name):
        region = self.regions[region_name]
        sell_amount = 100  # simplified, selling only 100 tea
        if self.player.processed_tea >= sell_amount:
            self.player.processed_tea -= sell_amount
            revenue = region.current_tea_price * sell_amount * (1 - region.tax_rate)
            self.player.money += revenue
            #self.add_message(f"Продано {sell_amount} чая в {region_name} за ${revenue:,.2f} (Налог: {region.tax_rate:.2f})")
        #else:
            #self.add_message("Недостаточно чая для продажи.")

    def hire_worker(self, region_name):
        region = self.regions[region_name]
        self.player.hire_worker(region)
            #self.add_message(f"Наняли рабочего в {region_name}.")
        #else:
            #self.add_message("Недостаточно средств для найма рабочих.")

    def fire_worker(self, region_name):
        region = self.regions[region_name]
        self.player.fire_worker(region)
            #self.add_message(f"Уволили рабочего в {region_name}.")
        #else:
            #self.add_message("Некого увольнять.")

    def process_turn(self):
        # 1. Update economic conditions in all regions
        for region in self.regions.values():
            region.update_economic_factors()
        
        # 2. Collect payments (workers' salaries)
        for region_name, region in self.regions.items():
            worker_cost = region.get_worker_count(self.player.name) * region.labor_cost
            if self.player.money >= worker_cost:
                self.player.money -= worker_cost
                #self.add_message(f"Выплачено ${worker_cost:,.2f} рабочим в {region_name}")
            else:
                self.player.money = 0
                self.add_message(f"Недостаточно средств на зарплаты в {region_name}! {region.get_worker_count(self.player.name)} уволились")
                region.update_worker_count(self.player.name, 0)  # if can't pay, workers leave.
                continue  # Skip further processing for this region

        # 3. Harvesting
        for region_name, region in self.regions.items():
            raw_tea = region.harvest_tea(self.player, self.player.equipment_multiplier)
            self.player.tea_leaves += raw_tea  # Assuming green tea for simplicity
            #self.add_message(f"Harvested {raw_tea} raw Tea in {region_name}")

        # 4. Packing
        for region_name, region in self.regions.items():
            packed_tea = region.pack_tea(self.player, self.player.tea_leaves, self.player.equipment_multiplier)
            self.player.processed_tea += packed_tea
            self.player.tea_leaves -= packed_tea  # Reduce raw tea by the amount packed
            #self.add_message(f"Packed {packed_tea} Tea in {region_name}")
        # 5. Taxes cut out
        # 6. Random Events
        self.trigger_random_event()

        # 7. Competitor Actions (very basic)
        self.competitor_turn()

    def competitor_turn(self):
        """Simulates actions for competitor companies."""
        for company in self.companies:
            # Companies now evaluate all regions and act in multiple regions per turn
            profitable_regions = []
            for region_name, region in self.regions.items():
                # Calculate potential profit
                profit = (region.current_tea_price - region.tea_leaves_cost) * 100 * company.aggressive_factor
                if profit > 0:
                    profitable_regions.append((profit, region))
    
            # Sort regions by profitability
            #profitable_regions.sort(reverse=True)
            profitable_regions.sort(key=lambda x: x[0], reverse=True)
            # Act in top 3 most profitable regions
            for _, region in profitable_regions:
                # Harvesting with improved efficiency
                raw_tea = region.harvest_tea(company, company.equipment_multiplier)
                company.tea_leaves += raw_tea
                # Packing with improved efficiency
                packed_tea = region.pack_tea(company, company.tea_leaves, company.equipment_multiplier)
                company.processed_tea += packed_tea
                company.tea_leaves -= packed_tea

            for _, region in profitable_regions[:3]:
                # More aggressive selling
                sell_amount = min(100 * int(company.aggressive_factor), company.processed_tea)
                if sell_amount > 0:
                    tax_rate = region.tax_rate
                    revenue = region.current_tea_price * sell_amount * (1 - tax_rate)
                company.money += revenue
                company.processed_tea -= sell_amount

            # Companies now evaluate all regions and act in multiple regions per turn
            harvest_regions = []
            for region_name, region in self.regions.items():
                # Calculate potential benfit
                hire = region.labor_cost * company.aggressive_factor
                if hire > 0:
                    harvest_regions.append((hire, region))
            
            #harvest_regions.sort()
            harvest_regions.sort(key=lambda x: x[0], reverse=False)
            # Hire workers in top 3 most profitable regions
            for _, region in harvest_regions[:3]:
                # Companies hire more aggressively
                workers_to_hire = random.randint(1, 3)*2*int(company.aggressive_factor)  # Hire multiple workers at once
                for _ in range(workers_to_hire):
                    if company.hire_worker(region):
                        continue
                    else:
                        break  # Stop if can't afford more workers

            # Companies might upgrade their equipment (dummied out)
            #if company.money > 5000 and random.random() < 0.2:  # 20% chance to upgrade if can afford
            #    upgrade_cost = 5000
            #    company.money -= upgrade_cost
            #    company.equipment_multiplier *= 1.2  # 20% improvement

    def trigger_random_event(self):
        event_chance = random.random()
        if event_chance < 0.1:  # 10% chance
            event_type = random.randint(1, 5)
            self.random_event(event_type)

    def random_event(self, event_type):
        if event_type == 1:  # Loss of tea due to spoilage
            loss_percentage = random.uniform(0.1, 0.3)  # 10-30% loss
            loss_amount = int(self.player.processed_tea * loss_percentage)
            self.player.processed_tea -= loss_amount
            self.add_message(f"Порча товара. Потеряно {loss_amount} чая.")

            # Apply similar loss to competitors
            for company in self.companies:
                loss_amount_comp = int(company.processed_tea * loss_percentage)
                company.processed_tea -= loss_amount_comp
                self.add_message(f"Порча товара. {company.name} потеряла {loss_amount_comp} чая.")

        elif event_type == 2:  # Labor strike
            region_name = random.choice(list(self.regions.keys()))
            region = self.regions[region_name]
            workers_affected = int(region.get_worker_count(self.player.name) * 0.5)  # 50% of workers on strike
            region.update_worker_count(self.player.name, -workers_affected)
            self.add_message(f"Забастовка в {region.name}! {workers_affected} человек бастуют.")

        elif event_type == 3:  # Market crash reduces company funds
            loss_percentage = random.uniform(0.2, 0.6)  # 20-60% loss
            loss_amount = int(self.player.money * loss_percentage)
            self.player.money -= loss_amount
            self.add_message(f"Обвал акций на фондовом рынке! Потеряно ${loss_amount:,.2f}.")

            # Apply similar loss to competitors
            for company in self.companies:
                loss_amount_comp = int(company.money * loss_percentage)
                company.money -= loss_amount_comp
                self.add_message(f"{company.name} потеряла ${loss_amount_comp:,.2f} из-за обвала на фондовом рынке.")

        elif event_type == 4:  # Unexpected demand increases tea prices
            price_increase = random.uniform(1.1, 1.5)  # Random price increase factor
            for region in self.regions.values():
                region.current_tea_price *= price_increase
            self.add_message("Неожиданный рост спроса на чай. Цены увеличились!")

        elif event_type == 5:  # Pest outbreak reduces tea production
            region_name = random.choice(list(self.regions.keys()))
            region = self.regions[region_name]
            production_loss = int(region.get_worker_count(self.player.name) * 0.3)  # 30% production loss
            self.player.tea_leaves -= production_loss # lost tea leaves because of outbreak
            self.add_message(f"Вредителями съедено {production_loss} чайных листьев.")

    def add_message(self, message):
        """Add a message to the message log."""
        self.messages.append(message)
        if len(self.messages) > 10:  # Limit the number of messages
            self.messages.pop(0)

    def draw_game_log(self):
        # Draw semi-transparent background
        bg_surface = self.create_semi_transparent_surface(self.game_log_rect.width, self.game_log_rect.height)
        self.screen.blit(bg_surface, self.game_log_rect)
        pygame.draw.rect(self.screen, BLACK, self.game_log_rect, 2)

        # Draw title
        title = self.font_medium.render("Game Log", True, BLACK)
        title_x = self.game_log_rect.centerx - title.get_width() // 2
        title_y = self.game_log_rect.top + 5
        self.screen.blit(title, (title_x, title_y))

        # Draw scroll buttons if there are more messages than can be displayed
        if len(self.messages) > self.max_visible_messages:
            # Up arrow
            pygame.draw.rect(self.screen, GRAY if self.message_scroll_offset < len(self.messages) - self.max_visible_messages else WHITE, self.scroll_up_rect)
            pygame.draw.rect(self.screen, BLACK, self.scroll_up_rect, 2)
            up_arrow = self.font_medium.render("↑", True, BLACK)
            self.screen.blit(up_arrow, (self.scroll_up_rect.centerx - up_arrow.get_width() // 2, 
                                      self.scroll_up_rect.centery - up_arrow.get_height() // 2))

            # Down arrow
            pygame.draw.rect(self.screen, GRAY if self.message_scroll_offset > 0 else WHITE, self.scroll_down_rect)
            pygame.draw.rect(self.screen, BLACK, self.scroll_down_rect, 2)
            down_arrow = self.font_medium.render("↓", True, BLACK)
            self.screen.blit(down_arrow, (self.scroll_down_rect.centerx - down_arrow.get_width() // 2,
                                        self.scroll_down_rect.centery - down_arrow.get_height() // 2))

        # Calculate visible messages
        start_y = self.game_log_rect.top + 40  # Space for title
        message_height = 25  # Height per message
        visible_messages = self.messages[-self.max_visible_messages - self.message_scroll_offset:] if self.message_scroll_offset > 0 else self.messages[-self.max_visible_messages:]
        
        # Draw messages
        for i, message in enumerate(visible_messages):
            message_surface = self.font_small.render(message, True, BLACK)
            message_x = self.game_log_rect.left + 10
            message_y = start_y + (i * message_height)
            
            # Only draw if within bounds
            if message_y + message_height <= self.game_log_rect.bottom - 5:
                self.screen.blit(message_surface, (message_x, message_y))

    def draw_progress_window(self):
        # Draw semi-transparent background
        bg_surface = self.create_semi_transparent_surface(self.progress_rect.width, self.progress_rect.height)
        self.screen.blit(bg_surface, self.progress_rect)
        pygame.draw.rect(self.screen, BLACK, self.progress_rect, 2)

        # Draw title
        title = self.font_medium.render("Progress to Victory", True, BLACK)
        title_x = self.progress_rect.centerx - title.get_width() // 2
        text_y = self.progress_rect.top + 20
        self.screen.blit(title, (title_x, text_y))
        text_y += 40

        # Calculate progress percentages
        money_progress = (self.player.money / self.target_money) * 100
        market_share = self.player.owned_tea_percentage * 100 if self.global_tea_supply > 0 else 0

        # Draw money progress
        money_text = self.font_medium.render(f"Деньги: ${self.player.money:,.0f} / ${self.target_money:,.0f}", True, BLACK)
        self.screen.blit(money_text, (self.progress_rect.left + 20, text_y))
        text_y += 25

        # Money progress bar
        bar_width = self.progress_rect.width - 40
        bar_height = 20
        pygame.draw.rect(self.screen, GRAY, (self.progress_rect.left + 20, text_y, bar_width, bar_height))
        progress_width = min(money_progress / 100 * bar_width, bar_width)
        pygame.draw.rect(self.screen, GREEN, (self.progress_rect.left + 20, text_y, progress_width, bar_height))
        text_y += 40

        # Draw market share progress
        share_text = self.font_medium.render(f"Доля на рынке: {market_share:.1f}% / {self.monopoly_threshold*100}%", True, BLACK)
        self.screen.blit(share_text, (self.progress_rect.left + 20, text_y))
        text_y += 25

        # Market share progress bar
        share_progress = (market_share / (self.monopoly_threshold * 100)) * 100
        progress_width = min(share_progress / 100 * bar_width, bar_width)
        pygame.draw.rect(self.screen, GRAY, (self.progress_rect.left + 20, text_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, BLUE, (self.progress_rect.left + 20, text_y, progress_width, bar_height))
        text_y += 40

        # Draw turn count
        turn_text = self.font_medium.render(f"Ход: {self.turn_count}", True, BLACK)
        self.screen.blit(turn_text, (self.progress_rect.left + 20, text_y))
        text_y += 30

        # Draw supply/demand info
        #supply_text = self.font_small.render(f"Предложение: {self.global_tea_supply:.2f}", True, BLACK)
        #demand_text = self.font_small.render(f"Спрос: {self.global_tea_demand}", True, BLACK)
        #self.screen.blit(supply_text, (self.progress_rect.left + 20, text_y))
        #self.screen.blit(demand_text, (self.progress_rect.left + 20, text_y + 20))

    def create_semi_transparent_surface(self, width, height, alpha=150):
        """Creates a semi-transparent white surface."""
        surface = pygame.Surface((width, height))
        surface.fill(WHITE)
        surface.set_alpha(alpha)
        return surface

    def run(self):
        while self.running:
            self.handle_events()  # Process events
            self.draw()           # Draw everything
            self.clock.tick(60)   # Maintain 60 FPS
        pygame.quit()
        sys.exit()

# --- Main Execution ---
if __name__ == "__main__":
    game = Game()
    game.run()
