"""
GitRecombo Desktop GUI - Modern Dark Edition
Interfaccia grafica professionale per GitRecombo usando CustomTkinter
NON modifica il backend - lo chiama via subprocess

Design: Modern dark theme con grafica ultra-professionale
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import threading
import json
import os
import sys
from pathlib import Path
import time
import re

# Modern DARK theme configuration
ctk.set_appearance_mode("dark")  # Professional dark mode
ctk.set_default_color_theme("dark-blue")  # Uniform theme without tile patterns

# Modern and readable font (Gemini-style)
MODERN_FONT = {
    "family": "Inter",  # Modern sans-serif font (uses fallback if unavailable)
    "fallback": "Segoe UI"  # Windows standard
}

def get_modern_font(size=14, weight="normal"):
    """Returns a modern and readable font"""
    try:
        # Try Inter first (modern font)
        return ctk.CTkFont(family=MODERN_FONT["family"], size=size, weight=weight)
    except:
        try:
            # Fallback to Segoe UI
            return ctk.CTkFont(family=MODERN_FONT["fallback"], size=size, weight=weight)
        except:
            # Ultimo fallback al default
            return ctk.CTkFont(size=size, weight=weight)

# Modern Dark Color Palette (ultra professionale)
MODERN_COLORS_DARK = {
    "primary_blue": "#1f6feb",
    "dark_blue": "#388bfd",
    "accent_purple": "#a371f7",
    "accent_green": "#3fb950",
    "accent_orange": "#fb8500",
    "accent_red": "#f85149",
    "bg_primary": "#0d1117",
    "bg_secondary": "#161b22",
    "bg_tertiary": "#21262d",
    "text_primary": "#e6edf3",
    "text_secondary": "#8b949e",
    "border": "#30363d",
    "success": "#3fb950",
    "warning": "#fb8500",
    "danger": "#f85149",
    "card_hover": "#21262d"
}

# Modern Light Color Palette (ultra professionale)
MODERN_COLORS_LIGHT = {
    "primary_blue": "#0969da",
    "dark_blue": "#0550ae",
    "accent_purple": "#8250df",
    "accent_green": "#238636",
    "accent_orange": "#d29922",
    "accent_red": "#da3633",
    "bg_primary": "#ffffff",
    "bg_secondary": "#f6f8fa",
    "bg_tertiary": "#f6f8fa",
    "text_primary": "#24292f",
    "text_secondary": "#656d76",
    "border": "#d0d7de",
    "success": "#238636",
    "warning": "#d29922",
    "danger": "#da3633",
    "card_hover": "#f3f4f6"
}

# Tema corrente (inizia con dark)
MODERN_COLORS = MODERN_COLORS_DARK.copy()

class GitRecomboGUI:
    def __init__(self):
        # Imposta la directory radice del progetto (2 livelli sopra questo file)
        self.project_root = Path(__file__).parent.parent
        os.chdir(str(self.project_root))  # Cambia directory di lavoro alla root
        
        self.root = ctk.CTk()
        self.root.title("GitRecombo v6.0 - AI-Powered Repository Discovery")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        
        # Imposta background GitHub-style
        self.root.configure(fg_color=MODERN_COLORS["bg_secondary"])

        # Riduce errori rumorosi da callback Tkinter su widget già distrutti
        # Alcuni widget CustomTkinter possono programmare callback "after" che
        # tentano di operare su widget già rimossi; intercettiamo eccezioni
        # specifiche per evitare che l'app stampi traceback non bloccanti.
        def _tk_callback_exception(exc_type, exc_value, exc_tb):
            try:
                # Ignora errori Tcl relativi a "bad window path name" (widget distrutti)
                if isinstance(exc_value, tk.TclError) and "bad window path name" in str(exc_value):
                    return
            except Exception:
                pass
            # For everything else, show normal traceback
            import traceback as _tb
            _tb.print_exception(exc_type, exc_value, exc_tb)

        self.root.report_callback_exception = _tk_callback_exception

        # Variabili di stato
        self.discovery_process = None
        self.is_discovering = False
        self.current_config = self.load_current_config()
        self.current_mission_data = None
        
        # Tema corrente (dark/light)
        self.current_theme = "dark"

        # Create interface
        self.create_widgets()
        
        # Aumenta velocità scroll del 20%
        self._setup_scroll_acceleration()

    def toggle_theme(self):
        """Cambia tra tema dark e light"""
        global MODERN_COLORS
        
        if self.current_theme == "dark":
            # Passa a light
            MODERN_COLORS = MODERN_COLORS_LIGHT.copy()
            self.current_theme = "light"
            ctk.set_appearance_mode("light")
        else:
            # Passa a dark
            MODERN_COLORS = MODERN_COLORS_DARK.copy()
            self.current_theme = "dark"
            ctk.set_appearance_mode("dark")
        
        # Ricarica l'interfaccia con il nuovo tema
        self._refresh_theme()

    def _refresh_theme(self):
        """Ricarica tutti i colori dell'interfaccia per il nuovo tema"""
        # Update root background
        self.root.configure(fg_color=MODERN_COLORS["bg_secondary"])
        
        # Update toggle button icon
        theme_icon = "🌙" if self.current_theme == "dark" else "☀"
        self.theme_button.configure(text=theme_icon)
        
        # Ricarica completamente l'interfaccia
        self._recreate_interface()

    def _recreate_interface(self):
        """Distrugge e ricrea l'intera interfaccia per applicare il nuovo tema"""
        # Rimuovi tutti i widget esistenti
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Recreate everything
        self.create_widgets()

    def create_widgets(self):
        """Crea tutti i widget dell'interfaccia ULTRA MODERNA"""

        # COMPACT main header
        header_frame = ctk.CTkFrame(self.root, fg_color=MODERN_COLORS["bg_primary"], 
                                   corner_radius=0, height=55)
        header_frame.pack(fill="x", pady=(0, 0))
        header_frame.pack_propagate(False)

        # Logo personalizzato (se esiste) - Tamagotchi cat neon
        logo_path = Path("gitrecombo/assets/logo.png")
        if logo_path.exists():
            try:
                from PIL import Image
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((50, 50), Image.Resampling.LANCZOS)
                logo_ctk = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(50, 50))
                logo_label = ctk.CTkLabel(header_frame, image=logo_ctk, text="")
                logo_label.pack(side="left", padx=(20, 15), pady=8)
            except Exception as e:
                # Fallback a emoji se errore
                print(f"Errore caricamento logo: {e}")
                logo_label = ctk.CTkLabel(header_frame, text="🐱",
                                        font=get_modern_font(size=32))
                logo_label.pack(side="left", padx=(25, 10), pady=10)
        else:
            # Usa emoji cat se file non esiste
            logo_label = ctk.CTkLabel(header_frame, text="🐱",
                                    font=get_modern_font(size=32))
            logo_label.pack(side="left", padx=(25, 10), pady=10)

        # Titolo compatto
        title_label = ctk.CTkLabel(header_frame, 
                                  text="GitRecombo",
                                  font=get_modern_font(size=26, weight="bold"),
                                  text_color=MODERN_COLORS["text_primary"])
        title_label.pack(side="left", pady=10)

        # Subtitle compatta
        subtitle_label = ctk.CTkLabel(header_frame,
                                     text="AI-Powered Repository Discovery",
                                     font=get_modern_font(size=14),
                                     text_color=MODERN_COLORS["text_secondary"])
        subtitle_label.pack(side="left", padx=(12, 20), pady=10)

        # Pulsante toggle tema (luna/sole)
        theme_icon = "🌙" if self.current_theme == "dark" else "☀"
        self.theme_button = ctk.CTkButton(header_frame,
                                         text=theme_icon,
                                         width=40,
                                         height=40,
                                         fg_color="transparent",
                                         hover_color=MODERN_COLORS["bg_tertiary"],
                                         command=self.toggle_theme,
                                         font=get_modern_font(size=16))
        self.theme_button.pack(side="right", padx=(0, 20), pady=8)

        # Main frame with ULTRA MODERN tabs
        self.tabview = ctk.CTkTabview(self.root, 
                                     fg_color=MODERN_COLORS["bg_primary"],
                                     segmented_button_fg_color="white",
                                     segmented_button_selected_color=MODERN_COLORS["primary_blue"],
                                     segmented_button_selected_hover_color=MODERN_COLORS["dark_blue"],
                                     segmented_button_unselected_hover_color="#f0f0f0",
                                     text_color=MODERN_COLORS["text_primary"],
                                     border_width=0)
        self.tabview.pack(pady=20, padx=30, fill="both", expand=True)

        # Create tabs with ULTRA MODERN design - graphic icons
        self.tabview.add("⚙  CONFIG")
        self.tabview.add("🚀  DISCOVERY")  
        self.tabview.add("💎  RESULTS")
        
        # Stilizza i tab buttons per renderli MODERNI (GitHub/VSCode style)
        self._modernize_tab_buttons()

        # Configura ogni tab
        self.setup_config_tab()
        self.setup_discovery_tab()
        self.setup_results_tab()

    def _modernize_tab_buttons(self):
        """Stilizza i pulsanti dei tab in stile MODERNO (Bianco/Nero, Centrato)"""
        try:
            # Accedi ai pulsanti segmentati
            segmented_button = self.tabview._segmented_button
            
            # Configurazione moderna: bianco con bordi, testo nero, centrato
            segmented_button.configure(
                corner_radius=10,
                border_width=0,
                fg_color="white",
                font=get_modern_font(size=14, weight="bold")
            )
            
            # Stilizza ogni bottone: bianco, testo nero, centrato
            for button_name in segmented_button._buttons_dict:
                button = segmented_button._buttons_dict[button_name]
                button.configure(
                    corner_radius=8,
                    height=44,
                    font=get_modern_font(size=14, weight="bold"),
                    anchor="center",
                    fg_color="white",  # Bianco
                    text_color="black",  # Nero
                    hover_color="#f0f0f0"  # Grigio chiaro hover
                )
        except Exception as e:
            print(f"Info: Stilizzazione tab non applicata: {e}")

    def setup_config_tab(self):
        """Setup del tab configurazione - DESIGN ULTRA MODERNO"""
        config_frame = self.tabview.tab("⚙  CONFIG")
        config_frame.configure(fg_color=MODERN_COLORS["bg_primary"])  # Unified background color

        # Main container with updated proportions
        main_container = ctk.CTkFrame(config_frame, fg_color="transparent", corner_radius=0)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Hero section with transparent background
        hero_frame = ctk.CTkFrame(main_container, fg_color="transparent", corner_radius=0, height=56)
        hero_frame.pack(fill="x", padx=20, pady=(10, 12))
        hero_frame.pack_propagate(False)

        # Icon container with modern styling
        icon_container = ctk.CTkFrame(hero_frame, fg_color=MODERN_COLORS["text_primary"], corner_radius=8, width=50, height=50)
        icon_container.pack(side="left", padx=(15, 10), pady=10)
        icon_container.pack_propagate(False)

        icon_label = ctk.CTkLabel(icon_container, text="⚙", font=get_modern_font(size=28), text_color=MODERN_COLORS["bg_primary"])
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # Hero text frame with compact layout
        hero_text_frame = ctk.CTkFrame(hero_frame, fg_color="transparent")
        hero_text_frame.pack(side="left", fill="both", expand=True, pady=10)

        title_label = ctk.CTkLabel(hero_text_frame, text="Discovery Configuration", font=get_modern_font(size=24, weight="bold"), text_color=MODERN_COLORS["text_primary"], anchor="w")
        title_label.pack(anchor="w")

        # Removed subtitle for cleaner layout
        # subtitle_label = ctk.CTkLabel(hero_text_frame, text="Define search parameters for AI-powered repository discovery", font=get_modern_font(size=13), text_color=MODERN_COLORS["text_secondary"], anchor="w")
        # subtitle_label.pack(anchor="w", pady=(3, 0))

        # Split container with transparent background
        split_container = ctk.CTkFrame(main_container, fg_color="transparent")
        split_container.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        # Left column with scrollable frame
        left_column = ctk.CTkScrollableFrame(split_container, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # CARD 1: Topics (con icona moderna)
        topics_card = self._create_modern_card(left_column, "🏷️", "Topics of Interest",
                                               "Comma-separated research topics")
        self.topics_entry = self._create_modern_input(topics_card,
                                                      "web3, stable, SQL, parameters")
        if self.current_config and "topics" in self.current_config:
            self.topics_entry.insert(0, ", ".join(self.current_config["topics"]))

        # CARD 2: Goal (con icona target)
        goal_card = self._create_modern_card(left_column, "🎯", "Discovery Goal",
                                            "What do you want to build or explore?")
        self.goal_textbox = self._create_modern_textbox(goal_card, height=150)
        if self.current_config and "goal" in self.current_config:
            self.goal_textbox.insert("0.0", self.current_config["goal"])

        # CARD 3: Custom Queries (con icona search)
        queries_card = self._create_modern_card(left_column, "🔍", "Custom GitHub Queries",
                                               "Advanced search filters (optional)")
        self.queries_entry = self._create_modern_input(queries_card,
                                                       "language:python stars:>100")
        if self.current_config and "custom_queries" in self.current_config:
            self.queries_entry.insert(0, ", ".join(self.current_config["custom_queries"]))

        # Separatore viola scuro tra le colonne
        separator = ctk.CTkFrame(split_container, fg_color="#6B3D99", width=2)
        separator.pack(side="left", fill="y", padx=(5, 5))
        separator.pack_propagate(False)

        # RIGHT COLUMN (1/3) - With scroll
        right_column = ctk.CTkScrollableFrame(split_container, fg_color="transparent")
        right_column.pack(side="left", fill="both", expand=True, padx=(0, 0))

        # CARD 4: Advanced Settings (modern 3-column layout)
        advanced_card = ctk.CTkFrame(right_column,
                                    fg_color=MODERN_COLORS["bg_primary"],
                                    corner_radius=12,
                                    border_width=2,
                                    border_color=MODERN_COLORS["primary_blue"])
        advanced_card.pack(fill="x", pady=(0, 15))

        # Header advanced
        adv_header = ctk.CTkFrame(advanced_card, fg_color="transparent")
        adv_header.pack(fill="x", padx=25, pady=(20, 15))

        adv_icon = ctk.CTkLabel(adv_header, text="⚙️",
                               font=get_modern_font(size=28))
        adv_icon.pack(side="left", padx=(0, 12))

        adv_title = ctk.CTkLabel(adv_header, text="Advanced Parameters",
                                font=get_modern_font(size=18, weight="bold"),
                                text_color=MODERN_COLORS["text_primary"])
        adv_title.pack(side="left")

        # Modern 3-column grid
        grid_container = ctk.CTkFrame(advanced_card, fg_color="transparent")
        grid_container.pack(fill="x", padx=25, pady=(0, 20))

        # Column 1: Days
        days_frame = ctk.CTkFrame(grid_container, fg_color=MODERN_COLORS["bg_secondary"],
                                 corner_radius=10)
        days_frame.grid(row=0, column=0, padx=(0, 12), pady=5, sticky="ew")

        ctk.CTkLabel(days_frame, text="📅",
                    font=get_modern_font(size=24)).pack(pady=(15, 5))
        ctk.CTkLabel(days_frame, text="Search Days",
                    font=get_modern_font(size=14, weight="bold"),
                    text_color=MODERN_COLORS["text_primary"]).pack()

        self.days_var = tk.StringVar(value=str(self.current_config.get("days", 7)))
        days_input = ctk.CTkEntry(days_frame, textvariable=self.days_var,
                                 width=80, height=40,
                                 justify="center",
                                 font=get_modern_font(size=18, weight="bold"),
                                 border_color=MODERN_COLORS["primary_blue"],
                                 fg_color=MODERN_COLORS["bg_primary"])
        days_input.pack(pady=(5, 15))

        # Column 2: Max Stars
        stars_frame = ctk.CTkFrame(grid_container, fg_color=MODERN_COLORS["bg_secondary"],
                                  corner_radius=10)
        stars_frame.grid(row=0, column=1, padx=(0, 12), pady=5, sticky="ew")

        ctk.CTkLabel(stars_frame, text="⭐",
                    font=get_modern_font(size=24)).pack(pady=(15, 5))
        ctk.CTkLabel(stars_frame, text="Max Stars",
                    font=get_modern_font(size=14, weight="bold"),
                    text_color=MODERN_COLORS["text_primary"]).pack()

        self.stars_var = tk.StringVar(value=str(self.current_config.get("max_stars", 100)))
        stars_input = ctk.CTkEntry(stars_frame, textvariable=self.stars_var,
                                  width=80, height=40,
                                  justify="center",
                                  font=get_modern_font(size=18, weight="bold"),
                                  border_color=MODERN_COLORS["primary_blue"],
                                  fg_color=MODERN_COLORS["bg_primary"])
        stars_input.pack(pady=(5, 15))

        # Column 3: Max Repositories
        repos_frame = ctk.CTkFrame(grid_container, fg_color=MODERN_COLORS["bg_secondary"],
                                  corner_radius=10)
        repos_frame.grid(row=0, column=2, pady=5, sticky="ew")

        ctk.CTkLabel(repos_frame, text="📚",
                    font=get_modern_font(size=24)).pack(pady=(15, 5))
        ctk.CTkLabel(repos_frame, text="Max Repos",
                    font=get_modern_font(size=14, weight="bold"),
                    text_color=MODERN_COLORS["text_primary"]).pack()

        self.max_repos_var = tk.StringVar(value=str(self.current_config.get("max", 20)))
        repos_input = ctk.CTkEntry(repos_frame, textvariable=self.max_repos_var,
                                  width=80, height=40,
                                  justify="center",
                                  font=get_modern_font(size=18, weight="bold"),
                                  border_color=MODERN_COLORS["primary_blue"],
                                  fg_color=MODERN_COLORS["bg_primary"])
        repos_input.pack(pady=(5, 15))

        # Seconda riga: Embeddings toggle
        embed_frame = ctk.CTkFrame(grid_container, fg_color=MODERN_COLORS["bg_secondary"],
                                  corner_radius=10)
        embed_frame.grid(row=1, column=0, padx=(0, 12), pady=(5, 0), sticky="ew")

        ctk.CTkLabel(embed_frame, text="🧠",
                    font=get_modern_font(size=24)).pack(pady=(15, 5))
        ctk.CTkLabel(embed_frame, text="Embeddings",
                    font=get_modern_font(size=14, weight="bold"),
                    text_color=MODERN_COLORS["text_primary"]).pack()

        self.embeddings_var = tk.BooleanVar(value=self.current_config.get("use_embeddings", True))
        embed_switch = ctk.CTkSwitch(embed_frame, text="",
                                    variable=self.embeddings_var,
                                    progress_color=MODERN_COLORS["success"],
                                    button_color=MODERN_COLORS["bg_primary"],
                                    button_hover_color=MODERN_COLORS["border"])
        embed_switch.pack(pady=(5, 15))

        grid_container.columnconfigure(0, weight=1)
        grid_container.columnconfigure(1, weight=1)
        grid_container.columnconfigure(2, weight=1)
        grid_container.rowconfigure(0, weight=1)
        grid_container.rowconfigure(1, weight=1)

        # CACHE MANAGEMENT SECTION
        cache_frame = ctk.CTkFrame(right_column, fg_color=MODERN_COLORS["bg_secondary"],
                                  corner_radius=10)
        cache_frame.pack(fill="x", padx=0, pady=(15, 15))

        cache_header = ctk.CTkFrame(cache_frame, fg_color="transparent")
        cache_header.pack(fill="x", padx=20, pady=(15, 10))

        cache_title = ctk.CTkLabel(cache_header, text="💾  Repository Cache Management",
                                  font=get_modern_font(size=14, weight="bold"),
                                  text_color=MODERN_COLORS["text_primary"])
        cache_title.pack(anchor="w")

        # Skip processed + cache count row
        cache_controls = ctk.CTkFrame(cache_frame, fg_color="transparent")
        cache_controls.pack(fill="x", padx=20, pady=(0, 15))

        # Switch to skip processed repos
        self.skip_processed_var = tk.BooleanVar(value=True)
        skip_switch = ctk.CTkSwitch(cache_controls, text="🔄 Skip Already Analyzed",
                                   variable=self.skip_processed_var,
                                   progress_color=MODERN_COLORS["success"],
                                   button_color=MODERN_COLORS["bg_primary"],
                                   button_hover_color=MODERN_COLORS["border"])
        skip_switch.pack(side="left", padx=(0, 20))

        # Cache count badge
        self.cache_count_label = ctk.CTkLabel(cache_controls, text="📊 Loading cache info...",
                                             font=get_modern_font(size=12),
                                             text_color=MODERN_COLORS["text_secondary"])
        self.cache_count_label.pack(side="left", padx=(0, 20))

        # Clear cache button
        clear_cache_btn = ctk.CTkButton(cache_controls, text="🗑️  Clear Cache",
                                       command=self.clear_repo_cache,
                                       fg_color=MODERN_COLORS["danger"],
                                       hover_color="#d73a49",
                                       text_color="white",
                                       height=32,
                                       font=get_modern_font(size=11, weight="bold"),
                                       corner_radius=6)
        clear_cache_btn.pack(side="left")

        # Load cache count
        self.update_cache_count()

        # LLM INSERTION CONTROL SECTION
        llm_frame = ctk.CTkFrame(right_column, fg_color=MODERN_COLORS["bg_secondary"],
                                corner_radius=10)
        llm_frame.pack(fill="x", padx=0, pady=(15, 15))

        llm_header = ctk.CTkFrame(llm_frame, fg_color="transparent")
        llm_header.pack(fill="x", padx=20, pady=(15, 10))

        llm_title = ctk.CTkLabel(llm_header, text="🤖 LLM Recombination Control",
                                font=get_modern_font(size=14, weight="bold"),
                                text_color=MODERN_COLORS["text_primary"])
        llm_title.pack(anchor="w")

        # Switch to skip LLM insertion
        llm_controls = ctk.CTkFrame(llm_frame, fg_color="transparent")
        llm_controls.pack(fill="x", padx=20, pady=(0, 15))

        self.skip_llm_insertion_var = tk.BooleanVar(value=False)
        skip_llm_switch = ctk.CTkSwitch(llm_controls, text="⏭️  Skip LLM Insertion",
                                       variable=self.skip_llm_insertion_var,
                                       progress_color=MODERN_COLORS["warning"],
                                       button_color=MODERN_COLORS["bg_primary"],
                                       button_hover_color=MODERN_COLORS["border"])
        skip_llm_switch.pack(side="left", padx=(0, 20))

        llm_info = ctk.CTkLabel(llm_controls, text="Disable LLM component insertion in recombination",
                               font=get_modern_font(size=11),
                               text_color=MODERN_COLORS["text_secondary"])
        llm_info.pack(side="left")

    # (Removed) Auto-save info: removed to save vertical space

        # Action buttons - Solo Reset
        buttons_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=30, pady=(5, 30))

        reset_btn = ctk.CTkButton(buttons_frame, text="🔄  Reset to Default",
                                command=self.reset_config,
                                fg_color=MODERN_COLORS["bg_secondary"],
                                hover_color=MODERN_COLORS["border"],
                                text_color=MODERN_COLORS["text_primary"],
                                border_width=2,
                                border_color=MODERN_COLORS["border"],
                                height=50,
                                font=get_modern_font(size=16, weight="bold"),
                                corner_radius=10)
        reset_btn.pack(fill="x")

    def _create_modern_card(self, parent, icon, title, subtitle):
        """Crea card moderna compatta con icona piccola su badge scuro"""
        card = ctk.CTkFrame(parent,
                           fg_color=MODERN_COLORS["bg_primary"],
                           corner_radius=10,
                           border_width=1,
                           border_color=MODERN_COLORS["border"])
        card.pack(fill="x", pady=(0, 12))

        # Header card compatto
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 8))

        # Badge scuro per icona
        icon_badge = ctk.CTkFrame(header, fg_color=MODERN_COLORS["text_primary"],
                                 corner_radius=6, width=36, height=36)
        icon_badge.pack(side="left", padx=(0, 12))
        icon_badge.pack_propagate(False)

        icon_label = ctk.CTkLabel(icon_badge, text=icon,
                                 font=get_modern_font(size=20),
                                 text_color=MODERN_COLORS["bg_primary"])
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

        text_frame = ctk.CTkFrame(header, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)

        title_label = ctk.CTkLabel(text_frame, text=title,
                                  font=get_modern_font(size=17, weight="bold"),
                                  text_color=MODERN_COLORS["text_primary"],
                                  anchor="w")
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(text_frame, text=subtitle,
                                     font=get_modern_font(size=13),
                                     text_color=MODERN_COLORS["text_secondary"],
                                     anchor="w")
        subtitle_label.pack(anchor="w", pady=(2, 0))

        return card

    def _create_modern_input(self, parent, placeholder):
        """Crea input moderno"""
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder,
                           border_color=MODERN_COLORS["border"],
                           fg_color=MODERN_COLORS["bg_secondary"],
                           font=get_modern_font(size=15),
                           height=50,
                           corner_radius=8)
        entry.pack(fill="x", padx=25, pady=(0, 20))
        return entry

    def _create_modern_textbox(self, parent, height=100):
        """Crea textbox moderno"""
        textbox = ctk.CTkTextbox(parent,
                                height=height,
                                border_color=MODERN_COLORS["border"],
                                fg_color=MODERN_COLORS["bg_secondary"],
                                font=get_modern_font(size=14),
                                wrap="word",
                                corner_radius=8)
        textbox.pack(fill="x", padx=25, pady=(0, 20))
        return textbox

    def setup_discovery_tab(self):
        """Setup del tab discovery ULTRA MODERNO"""
        discovery_frame = self.tabview.tab("🚀  DISCOVERY")
        discovery_frame.configure(fg_color=MODERN_COLORS["bg_secondary"])

        # Main 2-column container
        split_container = ctk.CTkFrame(discovery_frame, fg_color=MODERN_COLORS["bg_primary"],
                                      corner_radius=12)
        split_container.pack(fill="both", expand=True, padx=20, pady=20)

        # LEFT COLUMN (3/4) - Main content
        left_column = ctk.CTkScrollableFrame(split_container, fg_color=MODERN_COLORS["bg_primary"],
                                            corner_radius=12)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 15))

        # Header
        header_frame = ctk.CTkFrame(left_column, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(25, 15))

        title_label = ctk.CTkLabel(header_frame, text="Start Discovery",
                                 font=get_modern_font(size=26, weight="bold"),
                                 text_color=MODERN_COLORS["text_primary"])
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(header_frame,
                                     text="Run autonomous repository discovery powered by AI",
                                     font=get_modern_font(size=14),
                                     text_color=MODERN_COLORS["text_secondary"])
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # Separator
        separator = ctk.CTkFrame(left_column, height=1,
                                fg_color=MODERN_COLORS["border"])
        separator.pack(fill="x", padx=30, pady=(0, 20))

        # Status card
        status_card = ctk.CTkFrame(left_column, fg_color=MODERN_COLORS["bg_secondary"],
                                  corner_radius=8, border_width=1,
                                  border_color=MODERN_COLORS["border"])
        status_card.pack(fill="x", padx=30, pady=(0, 15))

        self.status_label = ctk.CTkLabel(status_card, text="🚀 Ready to start discovery",
                                       font=get_modern_font(size=16, weight="bold"),
                                       text_color=MODERN_COLORS["text_primary"])
        self.status_label.pack(pady=18)

        # Progress bar (GitHub-style)
        self.progress_bar = ctk.CTkProgressBar(left_column, 
                                              progress_color=MODERN_COLORS["primary_blue"],
                                              fg_color=MODERN_COLORS["bg_secondary"],
                                              height=8,
                                              corner_radius=4)
        self.progress_bar.pack(fill="x", padx=30, pady=(0, 20))
        self.progress_bar.set(0)

        # Log section
        log_header = ctk.CTkLabel(left_column, text="📝  Real-time Log Output",
                                font=get_modern_font(size=16, weight="bold"),
                                text_color=MODERN_COLORS["text_primary"])
        log_header.pack(anchor="w", padx=30, pady=(5, 8))

        # Log container with generous height, avoid ultra-compact
        log_container = ctk.CTkFrame(left_column, fg_color="transparent", height=420)
        log_container.pack(fill="x", padx=30, pady=(0, 25))
        log_container.pack_propagate(False)  # maintain container height

        # Log textbox (GitHub code block style)
        self.log_textbox = ctk.CTkTextbox(log_container, 
                                         wrap="word",
                                         border_color=MODERN_COLORS["border"],
                                         fg_color=MODERN_COLORS["bg_secondary"],
                                         font=get_modern_font(size=13),
                                         text_color=MODERN_COLORS["text_primary"])
        self.log_textbox.pack(fill="both", expand=True)

        # Adatta dinamicamente l'altezza in base alla finestra (tra 300 e 700 px)
        def _adjust_log_height(event=None):
            try:
                h = self.root.winfo_height()
                target = max(300, min(700, int(h * 0.42)))
                log_container.configure(height=target)
            except Exception:
                pass

        # Prima regolazione dopo il layout
        self.root.after(150, _adjust_log_height)
        # Update when window size changes
        self.root.bind("<Configure>", _adjust_log_height)

        # Separatore viola tra le colonne
        separator_vertical = ctk.CTkFrame(split_container, fg_color="#6B3D99", width=2)
        separator_vertical.pack(side="left", fill="y", padx=(5, 5))
        separator_vertical.pack_propagate(False)

        # RIGHT COLUMN (1/4) - Vertical icons with dark purple background
        right_column = ctk.CTkFrame(split_container, fg_color="transparent")
        right_column.pack(side="left", fill="y", padx=(0, 0))

        # Icone/bottoni verticali
        self.start_btn = ctk.CTkButton(right_column, text="🚀\nStart",
                                     command=self.start_discovery,
                                     fg_color=MODERN_COLORS["primary_blue"],
                                     hover_color=MODERN_COLORS["dark_blue"],
                                     height=80,
                                     width=120,
                                     font=get_modern_font(size=14, weight="bold"),
                                     corner_radius=8)
        self.start_btn.pack(padx=15, pady=(25, 10))

        self.stop_btn = ctk.CTkButton(right_column, text="⏹️\nStop",
                                    command=self.stop_discovery,
                                    fg_color=MODERN_COLORS["danger"],
                                    hover_color="#b31d28",
                                    height=80,
                                    width=120,
                                    font=get_modern_font(size=14, weight="bold"),
                                    corner_radius=8)
        self.stop_btn.pack(padx=15, pady=10)
        self.stop_btn.configure(state="disabled")

        clear_log_btn = ctk.CTkButton(right_column, text="🧹\nClear",
                                    command=self.clear_log,
                                    fg_color=MODERN_COLORS["bg_secondary"],
                                    hover_color=MODERN_COLORS["border"],
                                    text_color=MODERN_COLORS["text_primary"],
                                    border_width=1,
                                    border_color=MODERN_COLORS["border"],
                                    height=80,
                                    width=120,
                                    font=get_modern_font(size=14),
                                    corner_radius=8)
        clear_log_btn.pack(padx=15, pady=10)

    def setup_results_tab(self):
        """Setup del tab risultati ULTRA MODERNO"""
        results_frame = self.tabview.tab("💎  RESULTS")
        results_frame.configure(fg_color=MODERN_COLORS["bg_secondary"])

        # Main 2-column container
        split_container = ctk.CTkFrame(results_frame, fg_color=MODERN_COLORS["bg_primary"],
                                      corner_radius=12)
        split_container.pack(fill="both", expand=True, padx=20, pady=20)

        # LEFT COLUMN (3/4) - Results content
        left_column = ctk.CTkScrollableFrame(split_container, fg_color=MODERN_COLORS["bg_primary"],
                                            corner_radius=12)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 15))

        # Header con titolo
        header_frame = ctk.CTkFrame(left_column, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(25, 15))

        title_label = ctk.CTkLabel(header_frame, text="Discovery Results",
                                 font=get_modern_font(size=26, weight="bold"),
                                 text_color=MODERN_COLORS["text_primary"])
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(header_frame,
                                     text="View and analyze discovered repositories",
                                     font=get_modern_font(size=14),
                                     text_color=MODERN_COLORS["text_secondary"])
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # Separator
        separator = ctk.CTkFrame(left_column, height=1,
                                fg_color=MODERN_COLORS["border"])
        separator.pack(fill="x", padx=30, pady=(0, 20))

        # Results area: use normal Frame to avoid nested scroll
        # Scroll is handled ONLY by left_column (external CTkScrollableFrame)
        self.results_scrollable = ctk.CTkFrame(left_column,
                                               fg_color="transparent")
        self.results_scrollable.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        # Placeholder iniziale
        self._show_results_placeholder()

        # Separatore viola tra le colonne
        separator_vertical = ctk.CTkFrame(split_container, fg_color="#6B3D99", width=2)
        separator_vertical.pack(side="left", fill="y", padx=(5, 5))
        separator_vertical.pack_propagate(False)

        # RIGHT COLUMN (1/4) - Vertical icons with dark purple background
        right_column = ctk.CTkFrame(split_container, fg_color="#2D1B3D")
        right_column.pack(side="left", fill="y", padx=(0, 0))

        # Bottoni verticali
        load_btn = ctk.CTkButton(right_column, text="📂\nLoad",
                               command=self.load_mission,
                               fg_color=MODERN_COLORS["primary_blue"],
                               hover_color=MODERN_COLORS["dark_blue"],
                               height=80,
                               width=120,
                               font=get_modern_font(size=14, weight="bold"),
                               corner_radius=8)
        load_btn.pack(padx=15, pady=(25, 10))

        refresh_btn = ctk.CTkButton(right_column, text="🔄\nRefresh",
                                  command=self.refresh_results,
                                  fg_color=MODERN_COLORS["bg_secondary"],
                                  hover_color=MODERN_COLORS["border"],
                                  text_color=MODERN_COLORS["text_primary"],
                                  border_width=1,
                                  border_color=MODERN_COLORS["border"],
                                  height=80,
                                  width=120,
                                  font=get_modern_font(size=14),
                                  corner_radius=8)
        refresh_btn.pack(padx=15, pady=10)

    def _show_results_placeholder(self):
        """Mostra placeholder quando non ci sono risultati"""
        for widget in self.results_scrollable.winfo_children():
            widget.destroy()

        placeholder_frame = ctk.CTkFrame(self.results_scrollable,
                                        fg_color=MODERN_COLORS["bg_secondary"],
                                        corner_radius=12,
                                        border_width=2,
                                        border_color=MODERN_COLORS["border"])
        placeholder_frame.pack(fill="both", expand=True, pady=50, padx=20)

        icon_label = ctk.CTkLabel(placeholder_frame, text="💎",
                                 font=get_modern_font(size=60))
        icon_label.pack(pady=(40, 15))

        title_label = ctk.CTkLabel(placeholder_frame,
                                  text="No Mission Loaded",
                                  font=get_modern_font(size=24, weight="bold"),
                                  text_color=MODERN_COLORS["text_primary"])
        title_label.pack()

        subtitle_label = ctk.CTkLabel(placeholder_frame,
                                     text="Click 'Load Mission' to view discovery results",
                                     font=get_modern_font(size=15),
                                     text_color=MODERN_COLORS["text_secondary"])
        subtitle_label.pack(pady=(5, 40))

    def load_current_config(self):
        """Carica la configurazione attuale"""
        config_path = Path("config_lightweight.json")
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Errore caricamento config: {e}")
        return {}

    def save_config(self):
        """Salva la configurazione preservando i campi esistenti (con messagebox)"""
        try:
            self.save_config_internal()
            messagebox.showinfo("Successo", "✅ Configurazione salvata!")
            self.log_message("Configurazione salvata con successo")
        except Exception as e:
            messagebox.showerror("Errore", f"❌ Errore salvataggio config:\n{str(e)}")

    def save_config_internal(self):
        """Salva la configurazione senza mostrare messagebox (per auto-save)"""
        # Carica il config esistente per preservare i campi non gestiti dalla GUI
        existing_config = {}
        config_path = Path("config_lightweight.json")
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    existing_config = json.load(f)
            except:
                pass  # Se non riesce a leggere, usa config vuoto

        # Update only GUI-managed fields
        config = existing_config.copy()  # Preserva tutti i campi esistenti
        config.update({
            "topics": [t.strip() for t in self.topics_entry.get().split(",") if t.strip()],
            "goal": self.goal_textbox.get("0.0", "end").strip(),
            "custom_queries": [q.strip() for q in self.queries_entry.get().split(",") if q.strip()],
            "days": int(self.days_var.get()),
            "max": int(self.max_repos_var.get()),
            "max_stars": int(self.stars_var.get()),
            "use_embeddings": self.embeddings_var.get(),
            "exclude_processed": self.skip_processed_var.get(),
            "skip_llm_insertion": self.skip_llm_insertion_var.get()
        })

        with open("config_lightweight.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def reset_config(self):
        """Reset alla configurazione di default"""
        default_config = {
            "topics": ["web3", "stable", "SQL", "parameters"],
            "goal": "Build an innovative application combining multiple technologies",
            "custom_queries": [],
            "days": 7,
            "max": 20,
            "max_stars": 100,
            "use_embeddings": True,
            "exclude_processed": True,
            "skip_llm_insertion": False
        }

        # Update UI
        self.topics_entry.delete(0, "end")
        self.topics_entry.insert(0, ", ".join(default_config["topics"]))

        self.goal_textbox.delete("0.0", "end")
        self.goal_textbox.insert("0.0", default_config["goal"])

        self.queries_entry.delete(0, "end")

        self.days_var.set(str(default_config["days"]))
        self.max_repos_var.set(str(default_config["max"]))
        self.stars_var.set(str(default_config["max_stars"]))
        self.embeddings_var.set(default_config["use_embeddings"])
        self.skip_processed_var.set(default_config["exclude_processed"])
        self.skip_llm_insertion_var.set(default_config["skip_llm_insertion"])

        messagebox.showinfo("Reset", "🔄 Configurazione resettata ai valori di default")

    def update_cache_count(self):
        """Update repository count in cache"""
        try:
            from .repo_cache import RepoCache
            cache = RepoCache()
            count = cache.get_repo_count()
            cache.close()
            
            if count > 0:
                self.cache_count_label.configure(
                    text=f"📊 {count} repos cached",
                    text_color=MODERN_COLORS["success"]
                )
            else:
                self.cache_count_label.configure(
                    text="📊 Cache empty",
                    text_color=MODERN_COLORS["text_secondary"]
                )
        except Exception as e:
            self.cache_count_label.configure(
                text=f"⚠️ Cache error",
                text_color=MODERN_COLORS["warning"]
            )

    def clear_repo_cache(self):
        """Clear repository cache"""
        confirm = messagebox.askyesno(
            "Clear Cache",
            "⚠️ This will delete all cached repositories.\nContinue?"
        )
        
        if not confirm:
            return
        
        try:
            from .repo_cache import RepoCache
            cache = RepoCache()
            cache.clear_all()
            cache.close()
            
            messagebox.showinfo("Success", "✅ Cache cleared successfully")
            self.update_cache_count()
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error clearing cache:\n{str(e)}")

    def start_discovery(self):
        """Avvia il processo di discovery"""
        if self.is_discovering:
            return

        # AUTO-SAVE: Salva automaticamente la configurazione prima di avviare
        try:
            self.save_config_internal()  # Salva senza messagebox
            self.log_message("✅ Configurazione auto-salvata")
        except Exception as e:
            messagebox.showerror("Errore", f"❌ Impossibile salvare la configurazione:\n{str(e)}")
            return

        self.is_discovering = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.progress_bar.set(0)
        self.status_label.configure(text="🚀 Avvio discovery...")
        self.clear_log()

        # Avvia in thread separato
        discovery_thread = threading.Thread(target=self.run_discovery)
        discovery_thread.daemon = True
        discovery_thread.start()

    def run_discovery(self):
        """Esegue il discovery chiamando il backend"""
        try:
            self.log_message("🔍 Avvio GitRecombo ultra_autonomous...")
            self.log_message("Questo potrebbe richiedere 3-15 minuti...")

            cmd = [sys.executable, "ultra_autonomous.py", "--config", "config_lightweight.json"]
            
            # Aggiungi flag per escludere repository già analizzati
            if self.skip_processed_var.get():
                cmd.append("--exclude-processed")
                self.log_message("⏭️ Skipping already analyzed repositories")

            # Aggiungi flag per skip LLM insertion
            if self.skip_llm_insertion_var.get():
                cmd.append("--skip-llm-insertion")
                self.log_message("⏭️ Skipping LLM insertion in recombination")

            # Start process from project root to find module
            self.discovery_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                cwd=str(self.project_root)
            )

            # Leggi output in tempo reale
            while True:
                if self.discovery_process.poll() is not None:
                    # Process terminated, read all remaining buffer
                    remaining_output = self.discovery_process.stdout.read()
                    if remaining_output:
                        for line in remaining_output.split('\n'):
                            if line.strip():
                                self.log_message(line.strip())
                    break

                if not self.is_discovering:
                    self.discovery_process.terminate()
                    break

                # Leggi una riga
                line = self.discovery_process.stdout.readline()
                if line:
                    self.log_message(line.strip())

                    # Update progress based on phases
                    if "PHASE 1" in line:
                        self.progress_bar.set(0.2)
                        self.status_label.configure(text="🔍 Fase 1: Discovery repository...")
                    elif "PHASE 2" in line:
                        self.progress_bar.set(0.6)
                        self.status_label.configure(text="🤖 Fase 2: Analisi AI...")
                    elif "PHASE 3" in line:
                        self.progress_bar.set(0.8)
                        self.status_label.configure(text="📝 Fase 3: Arricchimento README...")

                time.sleep(0.1)

            # Controlla exit code
            exit_code = self.discovery_process.wait()

            if exit_code == 0:
                self.progress_bar.set(1.0)
                self.status_label.configure(text="✅ Discovery completed!")
                self.log_message("🎉 Success! Check 'missions/' folder for results")
                messagebox.showinfo("Completed", "🎉 Discovery completed!\n\nResults saved in missions/")
                # Update cache count after successful discovery
                self.update_cache_count()
            else:
                self.status_label.configure(text="❌ Error during discovery")
                self.log_message(f"❌ Process terminated with error (exit code: {exit_code})")
                messagebox.showerror("Errore", f"Discovery fallita (exit code: {exit_code})")

        except Exception as e:
            self.log_message(f"❌ Errore: {str(e)}")
            messagebox.showerror("Error", f"Error during discovery:\n{str(e)}")

        finally:
            self.is_discovering = False
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")

    def stop_discovery(self):
        """Ferma il processo di discovery"""
        if self.discovery_process and self.is_discovering:
            self.is_discovering = False
            self.discovery_process.terminate()
            self.status_label.configure(text="⏹️ Discovery fermata")
            self.log_message("⏹️ Discovery fermata dall'utente")

    def clear_log(self):
        """Clear the log"""
        self.log_textbox.delete("0.0", "end")

    def log_message(self, message):
        """Add a message to the log"""
        self.log_textbox.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_textbox.see("end")  # Auto-scroll to end

    def load_mission(self):
        """Load a mission from the missions/ folder"""
        missions_dir = Path("missions")
        if not missions_dir.exists():
            messagebox.showwarning("Warning", "Folder 'missions/' not found")
            return

        # List JSON files
        json_files = list(missions_dir.glob("*.json"))
        if not json_files:
            messagebox.showwarning("Warning", "No mission files found in missions/")
            return

        # Dialog to choose file
        file_path = filedialog.askopenfilename(
            title="Select Mission",
            initialdir=str(missions_dir),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            self.display_mission_results(file_path)

    def display_mission_results(self, file_path):
        """Display mission results - SINGLE BLOCK WITH MODERN ICONS"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.current_mission_data = data

            # Clear previous results
            for widget in self.results_scrollable.winfo_children():
                widget.destroy()

            # SINGLE BLOCK - Main card containing everything
            main_results_card = ctk.CTkFrame(self.results_scrollable,
                                            fg_color=MODERN_COLORS["bg_primary"],
                                            corner_radius=16,
                                            border_width=2,
                                            border_color=MODERN_COLORS["primary_blue"])
            main_results_card.pack(fill="both", expand=True)

            # Mission header (hero style)
            hero_header = ctk.CTkFrame(main_results_card,
                                      fg_color=MODERN_COLORS["primary_blue"],
                                      corner_radius=14,
                                      height=100)
            hero_header.pack(fill="x", padx=3, pady=3)
            hero_header.pack_propagate(False)

            # Icona grande
            hero_icon = ctk.CTkLabel(hero_header, text="🎯",
                                    font=get_modern_font(size=50))
            hero_icon.pack(side="left", padx=(30, 20))

            # Testo hero
            hero_text_frame = ctk.CTkFrame(hero_header, fg_color="transparent")
            hero_text_frame.pack(side="left", fill="both", expand=True, pady=15)

            mission_title = ctk.CTkLabel(hero_text_frame,
                                        text=data.get('refined_goal', 'Mission')[:120] + "...",
                                        font=get_modern_font(size=22, weight="bold"),
                                        text_color="white",
                                        wraplength=1000,
                                        anchor="w",
                                        justify="left")
            mission_title.pack(anchor="w")

            timestamp_label = ctk.CTkLabel(hero_text_frame,
                                          text=f"📅 {data.get('timestamp', 'N/A')}",
                                          font=get_modern_font(size=13),
                                          text_color="white")
            timestamp_label.pack(anchor="w", pady=(5, 0))

            # Container for all sections
            content_container = ctk.CTkFrame(main_results_card, fg_color="transparent")
            content_container.pack(fill="both", expand=True, padx=30, pady=25)

            # AI sections - show only those with real content
            ai_sections_all = [
                ("📝", "Refined Goal", data.get("refined_goal", "N/A"), "#0366d6"),
                ("🔗", "Repository Synergy", data.get("repository_synergy", "N/A"), "#6f42c1"),
                ("⚙️", "Technical Architecture", data.get("technical_architecture", "N/A"), "#d73a49"),
                ("🎯", "Expected Impact", data.get("expected_impact", "N/A"), "#28a745"),
                ("💡", "Innovation Analysis", data.get("innovation_analysis", "N/A"), "#f66a0a")
            ]

            # Filter N/A or empty strings
            ai_sections = [(i, t, c, col) for (i, t, c, col) in ai_sections_all if c and str(c).strip() and str(c).strip() != "N/A"]

            # If few sections (<=2), allow each to expand to fill vertical space
            allow_expand = len(ai_sections) <= 2

            for icon, title, content, accent_color in ai_sections:
                self._create_analysis_section_modern(content_container, icon, title, content, accent_color, expand_section=allow_expand)

            # Separator prima dei repository
            separator = ctk.CTkFrame(content_container, height=2,
                                    fg_color=MODERN_COLORS["border"],
                                    corner_radius=1)
            separator.pack(fill="x", pady=(25, 25))

            # Repository section
            if "sources" in data and data["sources"]:
                repos_header_frame = ctk.CTkFrame(content_container, fg_color="transparent")
                repos_header_frame.pack(fill="x", pady=(0, 20))

                repos_icon = ctk.CTkLabel(repos_header_frame, text="📚",
                                         font=get_modern_font(size=32))
                repos_icon.pack(side="left", padx=(0, 12))

                repos_title = ctk.CTkLabel(repos_header_frame,
                                          text="Discovered Repositories",
                                          font=get_modern_font(size=22, weight="bold"),
                                          text_color=MODERN_COLORS["text_primary"])
                repos_title.pack(side="left")

                repos_count = ctk.CTkLabel(repos_header_frame,
                                          text=f"  {len(data['sources'])} repos  ",
                                          font=get_modern_font(size=12, weight="bold"),
                                          fg_color=MODERN_COLORS["primary_blue"],
                                          text_color="white",
                                          corner_radius=12)
                repos_count.pack(side="left", padx=(12, 0))

                # Create card for each repository
                for repo in data["sources"]:
                    self._create_repository_card(content_container, repo)

        except Exception as e:
            messagebox.showerror("Error", f"Error loading mission:\n{str(e)}")

    def _create_analysis_section_modern(self, parent, icon, title, content, accent_color, expand_section: bool = False):
        """Crea sezione analisi ESPANSA - altezza basata su contenuto"""
        section_card = ctk.CTkFrame(parent,
                                   fg_color=MODERN_COLORS["bg_secondary"],
                                   corner_radius=10,
                                   border_width=3,
                                   border_color=accent_color)
        # If it is the only (or among few) sections, let it expand vertically to use all available space
        section_card.pack(fill="both", expand=bool(expand_section), pady=(0, 12))

        # Header compatto con badge scuro per icona
        header_frame = ctk.CTkFrame(section_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        # Badge scuro per icona piccola
        icon_badge = ctk.CTkFrame(header_frame, fg_color=MODERN_COLORS["text_primary"],
                                 corner_radius=6, width=36, height=36)
        icon_badge.pack(side="left", padx=(0, 12))
        icon_badge.pack_propagate(False)

        icon_label = ctk.CTkLabel(icon_badge, text=icon,
                                 font=get_modern_font(size=20),
                                 text_color=MODERN_COLORS["bg_primary"])
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # Titolo compatto
        title_label = ctk.CTkLabel(header_frame, text=title,
                                  font=get_modern_font(size=17, weight="bold"),
                                  text_color=MODERN_COLORS["text_primary"])
        title_label.pack(side="left")

        # Badge scuro word count con testo chiaro
        word_count = len(content.split())
        count_badge = ctk.CTkLabel(header_frame,
                                  text=f"  {word_count} words  ",
                                  font=get_modern_font(size=12, weight="bold"),
                                  fg_color=MODERN_COLORS["text_primary"],
                                  text_color=MODERN_COLORS["bg_primary"],
                                  corner_radius=8)
        count_badge.pack(side="right")

        # Formatted content - no internal scroll, all visible (use Label with wrap)
        formatted_content = self._format_analysis_text(content)

        # Gemini-style font: modern and readable with fallback
        try:
            gemini_font = ("Segoe UI Variable Text", 15)  # Modern Windows 11 font
        except Exception:
            gemini_font = ("Segoe UI", 15)  # Fallback Windows standard

        # Etichetta multi-linea con wrap; la pagina esterna gestisce lo scroll
        content_label = ctk.CTkLabel(section_card,
                                     text=formatted_content,
                                     fg_color=MODERN_COLORS["bg_primary"],
                                     text_color=MODERN_COLORS["text_primary"],
                                     font=gemini_font,
                                     justify="left",
                                     anchor="w",
                                     wraplength=900)
        content_label.pack(fill="x", expand=False, padx=20, pady=(0, 15))

        # Adatta il wraplength alla larghezza reale della card dopo il layout
        def _adjust_wrap():
            try:
                width = section_card.winfo_width()
                if width and width > 100:
                    content_label.configure(wraplength=max(300, width - 60))
            except Exception:
                pass
        section_card.after(120, _adjust_wrap)



    def _format_analysis_text(self, text):
        """Formatta il testo delle analisi AI per renderlo più leggibile"""
        if not text or text == "N/A":
            return text

        # Aggiungi spacing dopo i punti
        text = re.sub(r'\.\s+', '.\n\n', text)
        
        # Identifica e formatta liste (bullet points)
        text = re.sub(r'(\d+\))', r'\n\1', text)
        text = re.sub(r'([•\-]\s)', r'\n\1', text)

        # Rimuovi spazi multipli
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    def _create_repository_card(self, parent, repo):
        """Crea una card repository COMPATTA con badge scuri"""
        card = ctk.CTkFrame(parent,
                           fg_color=MODERN_COLORS["bg_primary"],
                           corner_radius=10,
                           border_width=2,
                           border_color=MODERN_COLORS["border"])
        card.pack(fill="x", pady=(0, 10))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=16)

        # Row 1: Nome repo con icona piccola + GEM score
        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 12))

        # Badge scuro per icona repo
        repo_icon_badge = ctk.CTkFrame(top_row, fg_color=MODERN_COLORS["text_primary"],
                                      corner_radius=6, width=36, height=36)
        repo_icon_badge.pack(side="left", padx=(0, 12))
        repo_icon_badge.pack_propagate(False)

        repo_icon = ctk.CTkLabel(repo_icon_badge, text="📦",
                                font=get_modern_font(size=20))
        repo_icon.place(relx=0.5, rely=0.5, anchor="center")

        # Nome repo
        repo_name_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        repo_name_frame.pack(side="left", fill="x", expand=True)

        repo_name = ctk.CTkLabel(repo_name_frame,
                                text=repo['name'],
                                font=get_modern_font(size=18, weight="bold"),
                                text_color=MODERN_COLORS["primary_blue"],
                                anchor="w")
        repo_name.pack(anchor="w")

        # Link sotto il nome
        link_label = ctk.CTkLabel(repo_name_frame,
                                 text=f"🔗 {repo.get('url', 'N/A')}",
                                 font=get_modern_font(size=12),
                                 text_color=MODERN_COLORS["text_secondary"],
                                 anchor="w",
                                 cursor="hand2")
        link_label.pack(anchor="w", pady=(2, 0))
        
        # Rendi il link cliccabile
        def open_repo_url(event, url=repo.get('url', '')):
            if url and url != 'N/A':
                import webbrowser
                webbrowser.open(url)
        
        link_label.bind("<Button-1>", open_repo_url)

        # GEM Score compatto a destra
        gem_score = repo['scores'].get('gem_score', 0)
        score_color = self._get_score_color(gem_score)

        gem_frame = ctk.CTkFrame(top_row, fg_color=score_color,
                                corner_radius=10)
        gem_frame.pack(side="right")

        gem_label_top = ctk.CTkLabel(gem_frame,
                                    text="GEM SCORE",
                                    font=get_modern_font(size=9, weight="bold"),
                                    text_color="white")
        gem_label_top.pack(padx=12, pady=(8, 2))

        gem_score_label = ctk.CTkLabel(gem_frame,
                                      text=f"{gem_score:.3f}",
                                      font=get_modern_font(size=20, weight="bold"),
                                      text_color="white")
        gem_score_label.pack(padx=12, pady=(0, 8))

        # Row 2: Metrics badges compatte con badge scuri
        metrics_row = ctk.CTkFrame(inner, fg_color="transparent")
        metrics_row.pack(fill="x", pady=(0, 10))

        scores = repo['scores']
        metrics = [
            ("🎯", "Novelty", scores.get('novelty', 0)),
            ("�", "Health", scores.get('health', 0)),
            ("🔥", "Relevance", scores.get('relevance', 0))
        ]

        for icon, metric_name, metric_value in metrics:
            metric_frame = ctk.CTkFrame(metrics_row,
                                       fg_color=MODERN_COLORS["text_primary"],
                                       corner_radius=8)
            metric_frame.pack(side="left", padx=(0, 8))

            icon_label = ctk.CTkLabel(metric_frame, text=icon,
                                     font=get_modern_font(size=16))
            icon_label.pack(side="left", padx=(10, 6), pady=6)

            text_frame = ctk.CTkFrame(metric_frame, fg_color="transparent")
            text_frame.pack(side="left", padx=(0, 10), pady=6)

            name_label = ctk.CTkLabel(text_frame, text=metric_name,
                                     font=get_modern_font(size=9),
                                     text_color=MODERN_COLORS["bg_secondary"])
            name_label.pack(anchor="w")

            value_label = ctk.CTkLabel(text_frame,
                                      text=f"{metric_value:.3f}",
                                      font=get_modern_font(size=12, weight="bold"),
                                      text_color=MODERN_COLORS["bg_primary"])
            value_label.pack(anchor="w")

        # Row 3: Language + License badges
        badges_row = ctk.CTkFrame(inner, fg_color="transparent")
        badges_row.pack(fill="x", pady=(0, 10))

        if 'language' in repo and repo['language']:
            lang_badge = ctk.CTkLabel(badges_row,
                                     text=f"  � {repo['language']}  ",
                                     font=get_modern_font(size=11, weight="bold"),
                                     fg_color=MODERN_COLORS["text_primary"],
                                     text_color=MODERN_COLORS["bg_primary"],
                                     corner_radius=8)
            lang_badge.pack(side="left", padx=(0, 8))

        if 'license' in repo and repo['license']:
            license_badge = ctk.CTkLabel(badges_row,
                                        text=f"  � {repo['license']}  ",
                                        font=get_modern_font(size=11, weight="bold"),
                                        fg_color=MODERN_COLORS["text_primary"],
                                        text_color=MODERN_COLORS["bg_primary"],
                                        corner_radius=8)
            license_badge.pack(side="left")

        # README snippet (se disponibile)
        if 'readme_snippet' in repo and repo['readme_snippet']:
            snippet_frame = ctk.CTkFrame(inner,
                                        fg_color=MODERN_COLORS["bg_secondary"],
                                        corner_radius=8,
                                        border_width=1,
                                        border_color=MODERN_COLORS["border"])
            snippet_frame.pack(fill="x", pady=(5, 0))

            snippet_header = ctk.CTkLabel(snippet_frame,
                                         text="📖  README Preview",
                                         font=get_modern_font(size=10, weight="bold"),
                                         text_color=MODERN_COLORS["text_secondary"])
            snippet_header.pack(anchor="w", padx=15, pady=(10, 4))

            snippet_text = ctk.CTkLabel(snippet_frame,
                                       text=repo['readme_snippet'][:250] + "...",
                                       font=get_modern_font(size=11),
                                       text_color=MODERN_COLORS["text_primary"],
                                       wraplength=1100,
                                       justify="left",
                                       anchor="w")
            snippet_text.pack(anchor="w", padx=15, pady=(0, 10))

    def _get_score_color(self, score):
        """Restituisce un colore basato sullo score (GitHub-style)"""
        if score >= 0.8:
            return "#2ea44f"  # Green (success)
        elif score >= 0.6:
            return "#0366d6"  # Blue (good)
        elif score >= 0.4:
            return "#bf8700"  # Orange (warning)
        else:
            return "#cf222e"  # Red (low)

    def _setup_scroll_acceleration(self):
        """Aumenta drasticamente la velocità dello scroll - METODO DIRETTO"""
        
        print("🚀 Scroll acceleration: Testing direct binding approach...")
        
        # Invece del monkey-patch globale, bindiamo direttamente gli eventi
        def ultra_fast_scroll(event):
            # Find the nearest CTkScrollableFrame
            widget = event.widget
            while widget and not isinstance(widget, ctk.CTkScrollableFrame):
                widget = widget.master
                if widget is None:
                    return
            
            if widget and hasattr(widget, '_parent_canvas'):
                # Scroll naturale: usa 1.0 invece di 6 (6x più veloce, praticamente default)
                scroll_amount = -int(event.delta / 1.0)
                widget._parent_canvas.yview_scroll(scroll_amount, "units")
                return "break"
        
        # Global bind for all CTkScrollableFrame
        self.root.bind_all("<MouseWheel>", ultra_fast_scroll)
        print("✅ Ultra-fast scroll bound to all CTkScrollableFrame instances!")

    # ...existing code... (no per-tab wheel helper)

    def refresh_results(self):
        """Update results (placeholder)"""
        messagebox.showinfo("Info", "🔄 Funzionalità di refresh da implementare")

    def run(self):
        """Avvia l'applicazione"""
        self.root.mainloop()

if __name__ == "__main__":
    app = GitRecomboGUI()
    app.run()




