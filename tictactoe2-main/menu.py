import pygame
import pygame
import request_handler
import os
import sys
import webbrowser

class MENUID:
    menu = 0
    local = 1
    login = 2
    stats = 3

class Menu:
    _main_instance = None
    _menu_instance = None
    localmenu = None
    mainmenu = None
    loginmenu = None
    statsmenu = None
    token = None
    @staticmethod
    def get_instance(screen = None, main_instance = None):
        if not Menu._menu_instance:
            Menu._menu_instance = Menu(screen, main_instance)
            Menu.localmenu = LocalMenu(screen, main_instance)
            Menu.mainmenu = MainMenu(screen, main_instance)
            Menu.loginmenu = LoginMenu(screen, main_instance)
            Menu.statsmenu = StatsMenu(screen, main_instance)
        return Menu._menu_instance

    def first_update():
        Menu.mainmenu.create_ui()

    
    def __init__(self, screen, main_instance) -> None:
        self.menu = MENUID.menu
        self.screen = screen
        Menu._main_instance = main_instance
        self.create_ui()

    def create_ui(self):
        self.buttons = []
        
    def render(self):   
        match self.menu:
            case MENUID.menu:
                self.mainmenu.render()
            case MENUID.local:
                self.localmenu.render()
            case MENUID.login:
                self.loginmenu.render()
            case MENUID.stats:
                self.statsmenu.render()

        pygame.display.update()


    def click(self, x, y) -> None: #check if mouse clicked
        match self.menu:
            case MENUID.menu:
                self.mainmenu.click(x, y)
            case MENUID.local:
                self.localmenu.click(x, y)
            case MENUID.login:
                self.loginmenu.click(x, y)
            case MENUID.stats:
                self.statsmenu.click(x, y)

    def handle_keydown(self, key):
        match self.menu:
            case MENUID.login:
                self.loginmenu.type(key)

    def change_text(self, text):
        self.buttons[0].text = text
        self.render()

    def change_menu(self, button, menu):
        self.menu = menu
        self.render()

class MainMenu(Menu):
    def __init__(self, screen, main_instance) -> None:
        super().__init__(screen, main_instance)
        self.create_ui()

    def create_ui(self):
        super().create_ui()
        self.font1 = pygame.font.SysFont('hightowertext', 90)
        self.text = self.font1.render("TIC TAC TOE", True, 0)
        self.text_rect = self.text.get_rect(center=(self.screen.get_width()/2, self.screen.get_height()/7))
        
        self.font2 = pygame.font.SysFont('hightowertext', self.screen.get_width() // 20)
        self.welcome_text = self.font2.render(f"Welcome, {Menu._main_instance.username}!" if Menu._main_instance.username else "Welcome!", True, 0)
        self.welcome_text_rect = self.welcome_text.get_rect(center=(self.screen.get_width()/2, self.screen.get_height()/6 + 50))

        if Menu._main_instance.username and not Menu._main_instance.ws:
            self.buttons.append(Button(self.screen, "logout",
                                        self.screen.get_width()/5, 
                                        self.screen.get_height()/6 + 130, 200, 50, 
                                        (0, 0, 0), "LOGOUT", (255, 255, 255), 0, action=self.logout))
            
            self.buttons.append(Button(self.screen, "stats",
                                        self.screen.get_width()/5 * 4, 
                                        self.screen.get_height()/6 + 130, 200, 50, 
                                        (0, 0, 0), "STATS", (255, 255, 255), 0, action=Menu.get_instance().change_menu, args=[MENUID.stats]))
        
        self.buttons.append(Button(self.screen, "rules",
                                    self.screen.get_width()/2, 
                                    self.screen.get_height()/6 + 130, 200, 50, 
                                    (0, 0, 0), "RULES", (255, 255, 255), 0, action=self.open_rules))

        if not Menu._main_instance.ws:
            self.buttons.append(Button(self.screen, "local",
                                    self.screen.get_width()/2, 
                                    self.screen.get_height() * 2/3 - 200, 500, 150, 
                                    (0, 0, 0), "LOCAL 1v1", (255, 255, 255), -10, action=Menu.get_instance().change_menu, args=[MENUID.local]))
        
        if self._main_instance.token:
            self.buttons.append(Button(self.screen, "multi",
                                self.screen.get_width()/2, 
                                self.screen.get_height() * 2/3, 500, 150, 
                                (0, 0, 0), "CONNECT" if not Menu._main_instance.ws else "WAITING FOR PLAYER 2", (255, 255, 255), -10, action=connect_button))
        else:
            self.buttons.append(Button(self.screen, "login",
                                self.screen.get_width()/2, 
                                self.screen.get_height() * 2/3, 500, 150, 
                                (0, 0, 0), "LOGIN", (255, 255, 255), 30, action=Menu.get_instance().change_menu, args=[MENUID.login]))
        
        self.buttons.append(Button(self.screen, "quit", 
                       self.screen.get_width()/2, 
                       self.screen.get_height() * 2/3 + 200, 500, 150, 
                       (0, 0, 0), "QUIT", (255, 255, 255), 30, action=sys.exit))

    def render(self):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.text, self.text_rect)
        self.screen.blit(self.welcome_text, self.welcome_text_rect)
        for button in self.buttons:
            button.render()

        self.create_ui()

    def click(self, x, y) -> None: #check if mouse is clicked on self.text2
        for button in self.buttons:
            button.click(x, y)

    def logout(self):
        if os.path.exists("token.txt"):
            os.remove("token.txt")
        Menu._main_instance.token = None
        Menu._main_instance.username = ""
        Menu.mainmenu.create_ui()

    def open_rules(self):
        webbrowser.open("https://mathwithbaddrawings.com/2013/06/16/ultimate-tic-tac-toe/")

class LocalMenu(Menu):
    def __init__(self, screen, main_instance) -> None:
        super().__init__(screen, main_instance)
        self.font1 = pygame.font.SysFont('hightowertext', 70)
        self.font2 = pygame.font.SysFont('hightowertext', screen.get_width() // 20)
        self.text = self.font1.render("CHOOSE GAMEMODE", True, 0)
    def create_ui(self):
        super().create_ui()

        self.buttons.append(Button(self.screen, "ai",
                                self.screen.get_width()/2, 
                                self.screen.get_height() * 2/3-200, 500, 150, 
                                (0, 0, 0), "VS. AI", (255, 255, 255), 0, self._main_instance.start_local_game_vs_ai))
        
        self.buttons.append(Button(self.screen, "localmulti",
                                self.screen.get_width()/2, 
                                self.screen.get_height() * 2/3, 500, 150, 
                                (0, 0, 0), "Local Multiplayer", (255, 255, 255), -30, self._main_instance.start_local_game))
        
        self.buttons.append(Button(self.screen, "back",
                                self.screen.get_width()/2,
                                self.screen.get_height() * 2/3 + 200, 300, 100, 
                                (0, 0, 0), "BACK", (255, 255, 255), 30, action=Menu.get_instance().change_menu, args=[MENUID.menu]))

    def render(self):
        self.screen.fill((255, 255, 255))
        self.text_rect = self.text.get_rect(center=(self.screen.get_width()/2, self.screen.get_height()/6))
        self.screen.blit(self.text, self.text_rect)
        for button in self.buttons:
            button.render()
    
    def click(self, x, y) -> None: #check if mouse is clicked on self.text2
        for button in self.buttons:
            button.click(x, y)
            
class LoginMenu(Menu):
    def __init__(self, screen, main_instance) -> None:
        super().__init__(screen, main_instance)
        self.font1 = pygame.font.SysFont('hightowertext', 70)
        self.font2 = pygame.font.SysFont('hightowertext', 45)
        self.text = self.font1.render("LOGIN", True, 0)
        self.status = ""
        self.focused = None
    def create_ui(self):
        super().create_ui()
        self.textboxes = []
        self.textboxes.append(TextBox(self.screen, 
                                self.screen.get_width()/2, 
                                self.screen.get_height()/2 - 100, 500, 100, 
                                (0, 0, 0), "Enter Username", (255, 255, 255), 0))

        self.textboxes.append(TextBox(self.screen,
                                self.screen.get_width()/2, 
                                self.screen.get_height()/2 + 50, 500, 100, 
                                (0, 0, 0), "Enter Password", (255, 255, 255), 0, hide=True))   

        self.buttons.append(Button(self.screen, "login",
                                self.screen.get_width()/4, 
                                self.screen.get_height()/3 + 400, 300, 100, 
                                (0, 0, 0), "LOGIN", (255, 255, 255), 20, action=self.login))

        self.buttons.append(Button(self.screen, "register",
                                self.screen.get_width()/4+self.screen.get_width()/2, 
                                self.screen.get_height()/3 + 400, 300, 100, 
                                (0, 0, 0), "REGISTER", (255, 255, 255), -15, action=self.register))    

        self.buttons.append(Button(self.screen, "back",
                                self.screen.get_width()/2, 
                                self.screen.get_height()/3 + 550, 300, 100, 
                                (0, 0, 0), "BACK", (255, 255, 255), 30, action=Menu.get_instance().change_menu, args=[MENUID.menu]))      

    def render(self):
        self.screen.fill((255, 255, 255))
        self.text_rect = self.text.get_rect(center=(self.screen.get_width()/2, self.screen.get_height()/6))
        self.status_text = self.font2.render(self.status, True, 0)
        self.text_rect_under = self.status_text.get_rect(center=(self.screen.get_width()/2, self.screen.get_height()/6 + 100))
        self.screen.blit(self.text, self.text_rect)
        self.screen.blit(self.status_text, self.text_rect_under)
        for button in self.buttons:
            button.render()
        for textbox in self.textboxes:
            textbox.render()
    
    def click(self, x, y) -> None: #check if mouse is clicked on self.text2
        for textbox in self.textboxes:
            if textbox.rect.collidepoint(pygame.mouse.get_pos()):
                self.focused = textbox
        for button in self.buttons:
            button.click(x, y)

    def type(self, key):
        if self.focused:
            if key.key == 8:
                self.focused.remove_text()
            else:
                if key.unicode.isalnum():
                    self.focused.append_text(key.unicode)
            self.render()

    def login(self):
        username = self.textboxes[0].get_text()
        password = self.textboxes[1].get_text()
        if username == "" or password == "":
            self.status = "Please fill in all fields!"
            return
        r = request_handler.login(username, password)
        if r:
            Menu._main_instance.token = r
            Menu._main_instance.username = username
            if os.path.exists("token.txt"):
                os.remove("token.txt")
            with open("token.txt", "w") as f:
                f.write(r)
            Menu.mainmenu.create_ui()
            Menu.get_instance().change_menu(None, MENUID.menu)
        else:
            self.status = "Incorrect username or password!"


    def register(self):
        username = self.textboxes[0].get_text()
        password = self.textboxes[1].get_text()
        if username == "" or password == "":
            self.status = "Please fill in all fields!"
            return
        if request_handler.register(self.textboxes[0].get_text(), self.textboxes[1].get_text()):
            self.status = "Successfully registered! You can now login."
        else:
            self.status = "Username already exists!"

class StatsMenu(Menu):
    def __init__(self, screen, main_instance) -> None:
        super().__init__(screen, main_instance)
        self.font1 = pygame.font.SysFont('hightowertext', 70)
        self.font2 = pygame.font.SysFont('hightowertext', 45)
        self.text = self.font1.render("STATS", True, 0)
          
    def create_ui(self):
        super().create_ui()
        self.buttons.append(Button(self.screen, "back",
                                self.screen.get_width()/2, 
                                self.screen.get_height() * 2/3 + 200, 300, 100, 
                                (0, 0, 0), "BACK", (255, 255, 255), 30, action=Menu.get_instance().change_menu, args=[MENUID.menu]))
        
        
    def get_stats(self):
        self.stats = request_handler.get_stats()
        self.last_stats_time = pygame.time.get_ticks()
    def render(self):
        if not hasattr(self, "stats") or pygame.time.get_ticks() - self.last_stats_time > 5000:
            self.get_stats()
        self.screen.fill((255, 255, 255))
        self.text_rect = self.text.get_rect(center=(self.screen.get_width()/2, self.screen.get_height()/6))
        stats = self.stats
        wins = self.font2.render(f"Wins: {stats['wins']}", True, 0)
        wins_rect = wins.get_rect(center=(self.screen.get_width()/2, self.screen.get_height()/6 + 100))

        losses = self.font2.render(f"Losses: {stats['losses']}", True, 0)
        losses_rect = losses.get_rect(center=(self.screen.get_width()/2, self.screen.get_height()/6 + 150))

        ties = self.font2.render(f"Ties: {stats['ties']}", True, 0)
        ties_rect = ties.get_rect(center=(self.screen.get_width()/2, self.screen.get_height()/6 + 200))

        games = self.font2.render(f"Games Played: {stats['games']}", True, 0)
        games_rect = games.get_rect(center=(self.screen.get_width()/2, self.screen.get_height()/6 + 250))

        elo = self.font2.render(f"Elo: {stats['elo']}", True, 0)
        elo_rect = elo.get_rect(center=(self.screen.get_width()/2, self.screen.get_height()/6 + 300))
        
        self.screen.blit(self.text, self.text_rect)
        self.screen.blit(wins, wins_rect)
        self.screen.blit(losses, losses_rect)
        self.screen.blit(ties, ties_rect)
        self.screen.blit(games, games_rect)
        self.screen.blit(elo, elo_rect)
        for button in self.buttons:
            button.render()

    def click(self, x, y) -> None: #check if mouse clicked on self.text2
        for button in self.buttons:
            button.click(x, y)

class Button():
    def __init__(self, screen, id, x, y, width, height, bg_color, text, text_color, font_size_mod, action=None, args = ()) -> None:
        self.id = id
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text_default = text
        self.font_size_mod = font_size_mod
        self.bg_color = bg_color
        self.hover_color = (bg_color[0] + 50, bg_color[1] + 50, bg_color[2] + 50)
        self.text_color = text_color
        self.text = text
        self.action = action
        self.args = args
        self.rect = pygame.Rect(self.x-self.width/2, self.y-self.height/2, self.width, self.height)
    
    def render(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(self.screen, self.hover_color, self.rect, 0, 20)
        else:
            pygame.draw.rect(self.screen, self.bg_color, self.rect, 0, 20)
        font_size = min((self.width // len(self.text)) - self.font_size_mod, self.height)
        font = pygame.font.SysFont('Times New Roman', font_size)
        text = font.render(self.text, True, self.text_color)
        self.text_rect = text.get_rect(center=(self.x, self.y))  # Calculate the position of the text based on the center of the button
        self.screen.blit(text, self.text_rect)
        
    def click(self, x, y):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if self.action:
                if self.id == "multi":
                    self.action(self)
                    return True
                if len(self.args) == 0:
                    self.action()
                else:
                    self.action(self, *self.args)
            return True
        
class TextBox():
    def __init__(self, screen, x, y, width, height, bg_color, text, text_color, font_size_mod, hide=False) -> None:
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text_default = text
        self.text = ""
        self.font_size_mod = font_size_mod
        self.bg_color = bg_color
        self.hover_color = (bg_color[0] + 50, bg_color[1] + 50, bg_color[2] + 50)
        self.text_color = text_color
        self.rect = pygame.Rect(self.x-self.width/2, self.y-self.height/2, self.width, self.height)
        self.hide = hide
    
    def render(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(self.screen, self.hover_color, self.rect, 0, 20)
        else:
            pygame.draw.rect(self.screen, self.bg_color, self.rect, 0, 20)
        font_size = min((self.width // len(self.text_default)) - self.font_size_mod, self.height)
        font = pygame.font.SysFont('Times New Roman', font_size)
        txt = self.text_default if self.text == "" else self.text if not self.hide else "*" * len(self.text)
        text = font.render(txt, True, self.text_color)
        self.text_rect = text.get_rect(center=(self.x, self.y))
        self.screen.blit(text, self.text_rect)
    
    def click(self, x, y):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        
    def get_text(self):
        return self.text
    
    def append_text(self, text):
        self.text += text
    
    def remove_text(self):
        self.text = self.text[:-1]
        
def connect_button(button):
    if not Menu._main_instance.ws:
        button.text = "CONNECTING..."
        button.render()
        pygame.display.update()
        pygame.time.wait(500)
        Menu._main_instance.open_websocket()
        button.text = "WAITING FOR PLAYER 2"
        Menu.mainmenu.create_ui()
        return
    else:
        Menu._main_instance.close_websocket()
        button.text = "CONNECT"
    
    