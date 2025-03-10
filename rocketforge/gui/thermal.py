import tkinter as tk
import customtkinter as ctk
from tkinter.messagebox import showwarning
from customtkinter import CTkEntry, CTkButton, CTkFrame, CTkLabel, CTkCheckBox, CTkOptionMenu
import rocketforge.thermal.config as config
import rocketforge.performance.config as pconf
from rocketforge.thermal.regenerative import Regen
from rocketforge.utils.conversions import mdot_uom, temperature_uom, pressure_uom, length_uom
from rocketforge.utils.resources import resource_path
from rocketforge.utils.helpers import update_entry
import warnings


class ThermalFrame(ctk.CTkFrame):
    def __init__(self, master=None, **kw):
        super(ThermalFrame, self).__init__(master, **kw)
        warnings.filterwarnings("error")
        self.topframe = CTkFrame(self, border_width=0, height=28, width=590)
        CTkLabel(self.topframe, text="Thermal Analysis").place(anchor="center", relx=0.5, rely=0.5, x=0, y=0) 
        self.topframe.place(anchor="n", relx=0.5, rely=0.01, x=0, y=0)

        self.regenframe = CTkFrame(self, border_width=0, height=28, width=590)
        CTkLabel(self.regenframe, text="Regenerative cooling").place(anchor="center", relx=0.5, rely=0.5, x=0, y=0)
        self.regenframe.place(anchor="center", relx=0.5, rely=0.11, x=0, y=0)
        self.regen = None
        
        self.regenvar = ctk.BooleanVar(value=False)
        CTkCheckBox(
            self,
            text="Enable regenerative cooling",
            variable=self.regenvar,
            command=self.toggle_regen_cooling
        ).place(anchor="w", relx=0.02, rely=0.18)

        CTkLabel(self, text="Coolant").place(anchor="w", relx=0.52, rely=0.18)
        self.coolant = tk.StringVar(value="Methane")
        CTkOptionMenu(
            self,
            values=[
                "A50",
                "CLF5",
                "Ethane",
                "Ethanol",
                "F2",
                "IRFNA",
                "LOX",
                "Methane",
                "Methanol",
                "MHF3",
                "MMH",
                "MON10",
                "MON25",
                "MON30",
                "N2H4",
                "N2O4",
                "N2O",
                "NH3",
                "PH2",
                "Propane",
                "RP1",
                "UDMH",
                "Water",
            ],
            variable=self.coolant, width=118
        ).place(anchor="e", relx=0.98, rely=0.18, x=0, y=0)

        CTkLabel(self, text="Coolant mass flow rate").place(anchor="w", relx=0.02, rely=0.25)
        self.mdotcentry = CTkEntry(self, width=59)
        self.mdotcentry.place(anchor="e", relx=229/600, rely=0.25)
        self.mdotcuom = tk.StringVar(value="kg/s")
        CTkOptionMenu(
            self,
            values=["kg/s", "g/s", "lb/s"],
            variable=self.mdotcuom, width=59
        ).place(anchor="e", relx=0.48, rely=0.25, x=0, y=0)

        CTkButton(
            self, text="Fuel mass flow rate", command=self.load_mdot_fuel, width=135
        ).place(anchor="w", relx=0.49, rely=0.25)
        CTkButton(
            self, text="Oxidizer mass flow rate", command=self.load_mdot_ox, width=135
        ).place(anchor="e", relx=0.95, rely=0.25)

        CTkLabel(self, text="Coolant inlet temperature").place(anchor="w", relx=0.02, rely=0.32)
        self.tcientry = CTkEntry(self, width=59)
        self.tcientry.place(anchor="e", relx=229/600, rely=0.32)
        self.tciuom = tk.StringVar(value="K")
        CTkOptionMenu(
            self,
            values=["K", "C", "F", "R"],
            variable=self.tciuom, width=59
        ).place(anchor="e", relx=0.48, rely=0.32, x=0, y=0)

        self.dp = ctk.BooleanVar(value=True)
        ctk.CTkRadioButton(
            self, text="Coolant inlet pressure", variable=self.dp, value=False
        ).place(anchor="w", relx=0.52, rely=0.32)
        self.pcientry = CTkEntry(self, width=59)
        self.pcientry.place(anchor="e", relx=529/600, rely=0.32)
        self.pciuom = tk.StringVar(value="bar")
        CTkOptionMenu(
            self,
            values=["MPa", "bar", "Pa", "psia", "atm"],
            variable=self.pciuom, width=59
        ).place(anchor="e", relx=0.98, rely=0.32, x=0, y=0)

        ctk.CTkRadioButton(
            self, text="Compute pressure drops", variable=self.dp, value=True
        ).place(anchor="w", relx=0.52, rely=0.39)

        CTkLabel(self, text="Inner wall thickness").place(anchor="w", relx=0.02, rely=0.39)
        self.tentry = CTkEntry(self, width=59)
        self.tentry.place(anchor="e", relx=229/600, rely=0.39)
        self.tuom = tk.StringVar(value="mm")
        CTkOptionMenu(
            self,
            values=["m", "cm", "mm", "in", "ft"],
            variable=self.tuom, width=59
        ).place(anchor="e", relx=0.48, rely=0.39, x=0, y=0)

        CTkLabel(self, text="Wall conductivity").place(anchor="w", relx=0.02, rely=0.46)
        self.kentry = CTkEntry(self, width=59)
        self.kentry.place(anchor="e", relx=229/600, rely=0.46)
        self.kuom = tk.StringVar(value="W/mK")
        CTkOptionMenu(
            self,
            values=[],
            variable=self.kuom, width=59
        ).place(anchor="e", relx=0.48, rely=0.46, x=0, y=0)

        CTkButton(
            self, text="Channels geometry...", command=self.channels_window, width=135
        ).place(anchor="center", relx=0.62, rely=0.46)
        self.channelswindow = None
        CTkButton(
            self, text="Advanced settings...", command=self.advanced_window, width=135
        ).place(anchor="center", relx=0.86, rely=0.46)
        self.advancedwindow = None

        self.filmframe = CTkFrame(self, border_width=0, height=28, width=590)
        CTkLabel(self.filmframe, text="Radiation cooling").place(anchor="center", relx=0.5, rely=0.5, x=0, y=0)
        self.filmframe.place(anchor="center", relx=0.5, rely=0.53, x=0, y=0)

        self.radvar = ctk.BooleanVar(value=False)
        CTkCheckBox(
            self,
            text="Enable radiation cooling",
            variable=self.radvar,
            command=self.toggle_rad_cooling
        ).place(anchor="w", relx=0.02, rely=0.60)

        CTkLabel(self, text="Wall emissivity").place(anchor="w", relx=0.52, rely=0.60)
        self.radepsentry = CTkEntry(self, width=118)
        self.radepsentry.place(anchor="e", relx=0.98, rely=0.60)
        self.radepsentry.insert("0", "0.8")

        self.filmframe = CTkFrame(self, border_width=0, height=28, width=590)
        CTkLabel(self.filmframe, text="Film cooling").place(anchor="center", relx=0.5, rely=0.5, x=0, y=0)
        self.filmframe.place(anchor="center", relx=0.5, rely=0.67, x=0, y=0)

        self.filmvar = ctk.BooleanVar(value=False)
        CTkCheckBox(
            self,
            text="Enable film cooling along injector head (thermal model still in development)",
            variable=self.filmvar,
            command=self.toggle_film_cooling
        ).place(anchor="w", relx=0.02, rely=0.74)

        CTkLabel(self, text="Fuel film cooling percentage").place(anchor="w", relx=0.02, rely=0.81)
        CTkLabel(self, text="%").place(anchor="e", relx=0.48, rely=0.81)
        self.fuelfilm = CTkEntry(self, width=80)
        self.fuelfilm.place(anchor="e", relx=0.46, rely=0.81)
        self.fuelfilm.insert("0", "0.0")

        CTkLabel(self, text="Oxidizer film cooling percentage").place(anchor="w", relx=0.52, rely=0.81)
        CTkLabel(self, text="%").place(anchor="e", relx=0.98, rely=0.81)
        self.oxfilm = CTkEntry(self, width=80)
        self.oxfilm.place(anchor="e", relx=0.96, rely=0.81)
        self.oxfilm.insert("0", "0.0")

        CTkButton(
            self, text="Plot temperatures", command=self.plot_T, width=135
        ).place(anchor="center", relx=0.14, rely=0.92)
        CTkButton(
            self, text="Plot wall heat flux", command=self.plot_q, width=135
        ).place(anchor="center", relx=0.38, rely=0.92)
        CTkButton(
            self, text="Coolant pressure", command=self.plot_p, width=135
        ).place(anchor="center", relx=0.62, rely=0.92)
        CTkButton(
            self, text="Details", command=self.details, width=135
        ).place(anchor="center", relx=0.86, rely=0.92)

        self.configure(border_width=1, corner_radius=0, height=480, width=600)

    def run(self):
        if config.regen:
            try:
                self.regen = Regen()
                self.regen.run()
            except RuntimeWarning:
                raise Exception

    def plot_p(self):
        try:
            self.regen.plot_p()
        except Exception:
            showwarning(title="Warning", message="Coolant pressure unavailable")

    def plot_T(self):
        if self.regen != None:
            self.regen.plot_T()
        else:
            showwarning(title="Warning", message="Temperatures unavailable")

    def plot_q(self):
        if self.regen != None:
            self.regen.plot_q()
        else:
            showwarning(title="Warning", message="Wall heat flux unavailable")

    def plot_g(self):
        if self.regen != None:
            self.set_channels(destroy=False)
            self.regen.plot_g()
        else:
            showwarning(title="Warning", message="Channels geometry unavailable")

    def print_g(self):
        if self.regen != None:
            self.set_channels(destroy=False)
            self.regen.print_g()
        else:
            showwarning(title="Warning", message="Channels geometry unavailable")

    def plot_3D(self):
        if self.regen != None:
            self.set_channels(destroy=False)
            self.channelswindow.update()
            self.regen.plot_3D()
        else:
            showwarning(title="Warning", message="Channels geometry unavailable")

    def details(self):
        if self.regen != None:
            self.regen.details()
        else:
            showwarning(title="Warning", message="Details unavailable")

    def load_mdot_ox(self):
        try:
            update_entry(self.mdotcentry, pconf.m_ox_d / mdot_uom(self.mdotcuom.get()))
        except Exception:
            showwarning(title="Warning", message="Mass flow rate unavailable")

    def load_mdot_fuel(self):
        try:
            update_entry(self.mdotcentry, pconf.m_f_d / mdot_uom(self.mdotcuom.get()))
        except Exception:
            showwarning(title="Warning", message="Mass flow rate unavailable")

    def channels_window(self):
        if self.channelswindow is None or not self.channelswindow.winfo_exists():
            self.channelswindow = ctk.CTkToplevel()
            self.channelswindow.title("Channels geometry")
            self.channelswindow.configure(width=420, height=260)
            self.channelswindow.resizable(False, False)
            self.channelswindow.after(
                201,
                lambda: self.channelswindow.iconphoto(
                    False, tk.PhotoImage(file=resource_path("rocketforge/resources/icon.png"))
                ),
            )

            self.channels_frame = CTkFrame(
                self.channelswindow, border_width=3, corner_radius=0, width=420, height=340,
            )
            self.channels_frame.grid(column=0, row=0)

            try:
                if config.cmode == 0:
                    self.regen.set_delta()
                else:
                    self.regen.set_a()
            except Exception:
                pass

            CTkLabel(self.channels_frame, text="Number of channels").place(anchor="w", relx=0.05, rely=1.3/17)
            self.ncentry = CTkEntry(self.channels_frame, placeholder_text="0", width=118)
            self.ncentry.place(anchor="w", relx=0.35, rely=1.3/17)
            update_entry(self.ncentry, config.NC)

            CTkLabel(self.channels_frame, text="Chamber").place(anchor="center", relx=0.42, rely=2.8/17)
            CTkLabel(self.channels_frame, text="Throat").place(anchor="center", relx=0.57, rely=2.8/17)
            CTkLabel(self.channels_frame, text="Exit").place(anchor="center", relx=0.72, rely=2.8/17)

            CTkLabel(self.channels_frame, text="Channels height").place(anchor="w", relx=0.05, rely=4/17)
            self.b1 = CTkEntry(self.channels_frame, placeholder_text="0", width=59)
            self.b1.place(anchor="w", relx=0.35, rely=4/17)
            self.b2 = CTkEntry(self.channels_frame, placeholder_text="0", width=59)
            self.b2.place(anchor="w", relx=0.5, rely=4/17)
            self.b3 = CTkEntry(self.channels_frame, placeholder_text="0", width=59)
            self.b3.place(anchor="w", relx=0.65, rely=4/17)
            self.buom = tk.StringVar(value="mm")
            CTkOptionMenu(
                self.channels_frame,
                values=["m", "cm", "mm", "in", "ft"],
                variable=self.buom, width=59
            ).place(anchor="e", relx=0.95, rely=4/17)
            update_entry(self.b1, config.b1 / length_uom(self.buom.get()))
            update_entry(self.b2, config.b2 / length_uom(self.buom.get()))
            update_entry(self.b3, config.b3 / length_uom(self.buom.get()))

            self.channelsmode = ctk.IntVar(value=config.cmode)

            ctk.CTkRadioButton(
                self.channels_frame, text="Channels width", variable=self.channelsmode, value=0,
            ).place(anchor="w", relx=0.05, rely=6/17)
            self.a1 = CTkEntry(self.channels_frame, placeholder_text="0", width=59)
            self.a1.place(anchor="w", relx=0.35, rely=6/17)
            self.a2 = CTkEntry(self.channels_frame, placeholder_text="0", width=59)
            self.a2.place(anchor="w", relx=0.5, rely=6/17)
            self.a3 = CTkEntry(self.channels_frame, placeholder_text="0", width=59)
            self.a3.place(anchor="w", relx=0.65, rely=6/17)
            self.auom = tk.StringVar(value="mm")
            CTkOptionMenu(
                self.channels_frame,
                values=["m", "cm", "mm", "in", "ft"],
                variable=self.auom, width=59
            ).place(anchor="e", relx=0.95, rely=6/17)
            update_entry(self.a1, config.a1 / length_uom(self.auom.get()))
            update_entry(self.a2, config.a2 / length_uom(self.auom.get()))
            update_entry(self.a3, config.a3 / length_uom(self.auom.get()))

            ctk.CTkRadioButton(
                self.channels_frame, text="Rib width", variable=self.channelsmode, value=1,
            ).place(anchor="w", relx=0.05, rely=8/17)
            self.d1 = CTkEntry(self.channels_frame, placeholder_text="0", width=59)
            self.d1.place(anchor="w", relx=0.35, rely=8/17)
            self.d2 = CTkEntry(self.channels_frame, placeholder_text="0", width=59)
            self.d2.place(anchor="w", relx=0.5, rely=8/17)
            self.d3 = CTkEntry(self.channels_frame, placeholder_text="0", width=59)
            self.d3.place(anchor="w", relx=0.65, rely=8/17)
            self.duom = tk.StringVar(value="mm")
            CTkOptionMenu(
                self.channels_frame,
                values=["m", "cm", "mm", "in", "ft"],
                variable=self.duom, width=59
            ).place(anchor="e", relx=0.95, rely=8/17)
            update_entry(self.d1, config.d1 / length_uom(self.duom.get()))
            update_entry(self.d2, config.d2 / length_uom(self.duom.get()))
            update_entry(self.d3, config.d3 / length_uom(self.duom.get()))

            CTkLabel(self.channels_frame, text="Aspect Ratio").place(anchor="w", relx=0.05, rely=10/17)
            self.ar1 = CTkEntry(self.channels_frame, placeholder_text="0", width=59)
            self.ar1.place(anchor="w", relx=0.35, rely=10/17)
            self.ar2 = CTkEntry(self.channels_frame, placeholder_text="0", width=59)
            self.ar2.place(anchor="w", relx=0.5, rely=10/17)
            self.ar3 = CTkEntry(self.channels_frame, placeholder_text="0", width=59)
            self.ar3.place(anchor="w", relx=0.65, rely=10/17)
            update_entry(self.ar1, config.b1 / config.a1, True)
            update_entry(self.ar2, config.b2 / config.a2, True)
            update_entry(self.ar3, config.b3 / config.a3, True)

            CTkLabel(self.channels_frame, text="Filling Ratio").place(anchor="w", relx=0.05, rely=12/17)
            self.fr1 = CTkEntry(self.channels_frame, placeholder_text="0", width=59)
            self.fr1.place(anchor="w", relx=0.35, rely=12/17)
            self.fr2 = CTkEntry(self.channels_frame, placeholder_text="0", width=59)
            self.fr2.place(anchor="w", relx=0.5, rely=12/17)
            self.fr3 = CTkEntry(self.channels_frame, placeholder_text="0", width=59)
            self.fr3.place(anchor="w", relx=0.65, rely=12/17)
            update_entry(self.fr1, config.a1 / (config.a1 + config.d1), True)
            update_entry(self.fr2, config.a2 / (config.a2 + config.d2), True)
            update_entry(self.fr3, config.a3 / (config.a3 + config.d3), True)

            CTkButton(
                self.channels_frame, text="Plot...", command=self.plot_g, width=110
            ).place(anchor="center", relx=0.2, rely=14/17)

            CTkButton(
                self.channels_frame, text="Plot 3D...", command=self.plot_3D, width=110
            ).place(anchor="center", relx=0.5, rely=14/17)

            CTkButton(
                self.channels_frame, text="Print...", command=self.print_g, width=110
            ).place(anchor="center", relx=0.8, rely=14/17)

            CTkButton(
                self.channels_frame, text="Set", command=self.set_channels, width=150
            ).place(anchor="center", relx=0.5, rely=16/17)

            self.channelswindow.after(50, self.channelswindow.lift)
            self.channelswindow.after(50, self.channelswindow.focus)

        else:
            self.channelswindow.lift()
            self.channelswindow.focus()

    def set_channels(self, destroy=True):
        try:
            config.NC = int(float(self.ncentry.get()))
            config.b1 = float(self.b1.get()) * length_uom(self.buom.get())
            config.b2 = float(self.b2.get()) * length_uom(self.buom.get())
            config.b3 = float(self.b3.get()) * length_uom(self.buom.get())
            config.cmode = self.channelsmode.get()
            if config.cmode == 0:
                config.a1 = float(self.a1.get()) * length_uom(self.auom.get())
                config.a2 = float(self.a2.get()) * length_uom(self.auom.get())
                config.a3 = float(self.a3.get()) * length_uom(self.auom.get())
                self.regen.set_delta()
                update_entry(self.d1, config.d1 / length_uom(self.duom.get()))
                update_entry(self.d2, config.d2 / length_uom(self.duom.get()))
                update_entry(self.d3, config.d3 / length_uom(self.duom.get()))
            else:
                config.d1 = float(self.d1.get()) * length_uom(self.duom.get())
                config.d2 = float(self.d2.get()) * length_uom(self.duom.get())
                config.d3 = float(self.d3.get()) * length_uom(self.duom.get())
                self.regen.set_a()
                update_entry(self.a1, config.a1 / length_uom(self.auom.get()))
                update_entry(self.a2, config.a2 / length_uom(self.auom.get()))
                update_entry(self.a3, config.a3 / length_uom(self.auom.get()))

            self.regen.set_channels()

            if destroy:
                self.channelswindow.destroy()
            else:
                update_entry(self.ar1, config.b1 / config.a1, True)
                update_entry(self.ar2, config.b2 / config.a2, True)
                update_entry(self.ar3, config.b3 / config.a3, True)
                update_entry(self.fr1, config.a1 / (config.a1 + config.d1), True)
                update_entry(self.fr2, config.a2 / (config.a2 + config.d2), True)
                update_entry(self.fr3, config.a3 / (config.a3 + config.d3), True)
        except Exception:
            pass

    def advanced_window(self):
        if self.advancedwindow is None or not self.advancedwindow.winfo_exists():
            self.advancedwindow = ctk.CTkToplevel()
            self.advancedwindow.title("Advanced settings")
            self.advancedwindow.resizable(False, False)
            self.advancedwindow.after(
                201,
                lambda: self.advancedwindow.iconphoto(
                    False, tk.PhotoImage(file=resource_path("rocketforge/resources/icon.png"))
                ),
            )

            self.advanced_frame = CTkFrame(
                self.advancedwindow, border_width=3, corner_radius=0
            )
            self.advanced_frame.pack()

            CTkLabel(self.advanced_frame, text="pInjectors/pChamber").grid(column=0, row=0, padx=7, pady=7)
            self.pcoOvpcentry = CTkEntry(self.advanced_frame, placeholder_text="0", width=125)
            self.pcoOvpcentry.grid(column=1, row=0, padx=7, pady=7)
            update_entry(self.pcoOvpcentry, config.pcoOvpc)

            CTkLabel(self.advanced_frame, text="Number of stations").grid(column=0, row=1, padx=7, pady=7)
            self.nsentry = CTkEntry(self.advanced_frame, placeholder_text="0", width=125)
            self.nsentry.grid(column=1, row=1, padx=7, pady=7)
            update_entry(self.nsentry, config.n_stations)

            CTkLabel(self.advanced_frame, text="Maximum iterations").grid(column=0, row=2, padx=7, pady=7)
            self.maxiterentry = CTkEntry(self.advanced_frame, placeholder_text="0", width=125)
            self.maxiterentry.grid(column=1, row=2, padx=7, pady=7)
            update_entry(self.maxiterentry, config.max_iter)

            CTkLabel(self.advanced_frame, text="Tuning coefficient").grid(column=0, row=3, padx=7, pady=7)
            self.tuningentry = CTkEntry(self.advanced_frame, placeholder_text="0", width=125)
            self.tuningentry.grid(column=1, row=3, padx=7, pady=7)
            update_entry(self.tuningentry, config.tuning_factor)

            CTkLabel(self.advanced_frame, text="Stability coefficient").grid(column=0, row=4, padx=7, pady=7)
            self.stabentry = CTkEntry(self.advanced_frame, placeholder_text="0", width=125)
            self.stabentry.grid(column=1, row=4, padx=7, pady=7)
            update_entry(self.stabentry, config.stability)

            CTkLabel(self.advanced_frame, text="Absolute roughness [mm]").grid(column=0, row=5, padx=7, pady=7)
            self.roughentry = CTkEntry(self.advanced_frame, placeholder_text="0", width=125)
            self.roughentry.grid(column=1, row=5, padx=7, pady=7)
            update_entry(self.roughentry, config.absolute_roughness * 1000)

            CTkLabel(self.advanced_frame, text="Outer to inner wall ratio").grid(column=0, row=6, padx=7, pady=7)
            self.t_eOvt_wentry = CTkEntry(self.advanced_frame, placeholder_text="0", width=125)
            self.t_eOvt_wentry.grid(column=1, row=6, padx=7, pady=7)
            update_entry(self.t_eOvt_wentry, config.t_eOvt_w)

            CTkLabel(self.advanced_frame, text="Friction factor relation").grid(column=0, row=7, padx=7, pady=7)
            if config.dp_method == 0:
                self.dp_method = ctk.StringVar(value="Tkachenko")
            elif config.dp_method == 1:
                self.dp_method = ctk.StringVar(value="Moody")
            elif config.dp_method == 2:
                self.dp_method = ctk.StringVar(value="Colebrook-White")
            self.dp_methodoptmenu = CTkOptionMenu(
                self.advanced_frame,
                values=["Tkachenko", "Moody", "Colebrook-White"],
                variable=self.dp_method,
                width=125
            )
            self.dp_methodoptmenu.grid(column=1, row=7, padx=7, pady=7)

            CTkButton(
                self.advanced_frame, text="Reset", command=self.reset_advanced, width=90
            ). grid(column=0, row=8, padx=7, pady=7)

            CTkButton(
                self.advanced_frame, text="Set", command=self.set_advanced, width=90
            ).grid(column=1, row=8, padx=7, pady=7)

            self.advancedwindow.after(50, self.advancedwindow.lift)
            self.advancedwindow.after(50, self.advancedwindow.focus)

        else:
            self.advancedwindow.lift()
            self.advancedwindow.focus()

    def set_advanced(self):
        try:
            config.pcoOvpc = float(self.pcoOvpcentry.get())
            config.n_stations = int(float(self.nsentry.get()))
            config.max_iter = int(float(self.maxiterentry.get()))
            config.tuning_factor = float(self.tuningentry.get())
            config.stability = float(self.stabentry.get())
            config.absolute_roughness = float(self.roughentry.get()) / 1000
            config.t_eOvt_w = float(self.t_eOvt_wentry.get())
            if self.dp_method.get() == "Tkachenko":
                config.dp_method = 0
            elif self.dp_method.get() == "Moody":
                config.dp_method = 1
            elif self.dp_method.get() == "Colebrook-White":
                config.dp_method = 2
            self.advancedwindow.destroy()
        except Exception:
            pass
    
    def reset_advanced(self):
        config.pcoOvpc = 1.2
        config.n_stations = 200
        config.max_iter = 200
        config.tuning_factor = 1.0
        config.stability = 0.5
        config.absolute_roughness = 0.00025
        config.dp_method = 0
        config.t_eOvt_w = 4.0
        self.advancedwindow.destroy()

    def toggle_regen_cooling(self):
        config.regen = self.regenvar.get()

    def toggle_rad_cooling(self):
        config.rad = self.radvar.get()

    def toggle_film_cooling(self):
        config.film = self.filmvar.get()

    def load_regen_cooling(self):
        config.regen = self.regenvar.get()
        config.coolant = self.coolant.get()
        config.m_dot_c = float(self.mdotcentry.get()) * mdot_uom(self.mdotcuom.get())
        config.T_ci = temperature_uom(float(self.tcientry.get()), self.tciuom.get())
        config.enable_dp = self.dp.get()
        if config.enable_dp:
            config.p_ci = pconf.pc * config.pcoOvpc
        else:
            config.p_ci = float(self.pcientry.get()) * pressure_uom(self.pciuom.get())
        config.t_w = float(self.tentry.get()) * length_uom(self.tuom.get())
        config.lambda_w = float(self.kentry.get())
    
    def load_rad_cooling(self):
        config.rad = self.radvar.get()
        config.eps_w = float(self.radepsentry.get())

    def load_film_cooling(self):
        config.film = self.filmvar.get()
        config.oxfilm = 0.0 if self.oxfilm.get() == "" else float(self.oxfilm.get())
        config.fuelfilm = 0.0 if self.fuelfilm.get() == "" else float(self.fuelfilm.get())