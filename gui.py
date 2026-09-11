import customtkinter as ctk
from tkinter import messagebox
import converter

# Theme settings
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class ConverterGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Medizinischer Umrechner (Benzo & Opioid)")
        self.geometry("900x700")

        # Grid layout: Sidebar and Main Content
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Med-Umrechner", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_benzo = ctk.CTkButton(self.sidebar_frame, text="Benzodiazepine", command=lambda: self.show_frame("benzo"))
        self.btn_benzo.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_opioid = ctk.CTkButton(self.sidebar_frame, text="Opioide", command=lambda: self.show_frame("opioid"))
        self.btn_opioid.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_conv = ctk.CTkButton(self.sidebar_frame, text="Umstellung", command=lambda: self.show_frame("conv"))
        self.btn_conv.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_adv = ctk.CTkButton(self.sidebar_frame, text="Erweitert", command=lambda: self.show_frame("adv"))
        self.btn_adv.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.btn_hist = ctk.CTkButton(self.sidebar_frame, text="Historie", command=lambda: self.show_frame("hist"))
        self.btn_hist.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        # Theme Switcher
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                               command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=20, sticky="s")
        self.appearance_mode_optionemenu.set("System")

        # --- Main Content Area ---
        self.main_container = ctk.CTkFrame(self, corner_radius=15)
        self.main_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self.frames = {}
        self.init_frames()
        self.show_frame("benzo")

    def init_frames(self):
        # Create all frames and add them to the container
        self.frames["benzo"] = self.create_benzo_frame()
        self.frames["opioid"] = self.create_opioid_frame()
        self.frames["conv"] = self.create_conv_frame()
        self.frames["adv"] = self.create_adv_frame()
        self.frames["hist"] = self.create_hist_frame()

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def validate_float(self, value):
        try:
            return float(value.replace(",", "."))
        except ValueError:
            return None

    # --- Frame Implementations ---

    def create_benzo_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
        ctk.CTkLabel(frame, text="Benzodiazepin Umrechner", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 10))
        
        ctk.CTkLabel(frame, text=converter.DISCLAIMER, wraplength=500, text_color="red").pack(pady=10)

        # Inputs
        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(pady=20, padx=40, fill="x")

        ctk.CTkLabel(input_frame, text="Medikament:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.benzo_med_var = ctk.StringVar(value=sorted(list(converter.DISPLAY_NAMES.values()))[0])
        self.benzo_med_combo = ctk.CTkComboBox(input_frame, values=sorted(list(converter.DISPLAY_NAMES.values())), variable=self.benzo_med_var)
        self.benzo_med_combo.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(input_frame, text="Dosis (mg):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.benzo_dose_entry = ctk.CTkEntry(input_frame)
        self.benzo_dose_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.benzo_dose_entry.insert(0, "0")

        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(frame, text="Umrechnen", command=self.calc_benzo).pack(pady=20)

        self.benzo_res_label = ctk.CTkLabel(frame, text="Ergebnis: -", font=ctk.CTkFont(size=18, weight="bold"))
        self.benzo_res_label.pack(pady=10)

        # Table
        self.benzo_table_text = ctk.CTkTextbox(frame, width=500, height=200)
        self.benzo_table_text.pack(pady=20, padx=20)
        self.benzo_table_text.insert("0.0", converter.get_equivalence_markdown())
        self.benzo_table_text.configure(state="disabled")

        return frame

    def calc_benzo(self):
        try:
            med_display = self.benzo_med_var.get()
            med_key = next(k for k, v in converter.DISPLAY_NAMES.items() if v == med_display)
            dose = self.validate_float(self.benzo_dose_entry.get())
            if dose is None: raise ValueError("Ungültige Dosis")
            
            equiv, _ = converter.convert_to_diazepam(med_key, dose)
            self.benzo_res_label.configure(text=f"{dose} mg {med_display} ≈ {equiv:.2f} mg Diazepam")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def create_opioid_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
        ctk.CTkLabel(frame, text="Opioid Umrechner", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 10))

        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(pady=20, padx=40, fill="x")

        ctk.CTkLabel(input_frame, text="Opioid:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        op_names = sorted(list(set(d.capitalize() for (d, r) in converter.OPIOID_TABLE.keys())))
        self.op_med_var = ctk.StringVar(value=op_names[0])
        self.op_med_combo = ctk.CTkComboBox(input_frame, values=op_names, variable=self.op_med_var)
        self.op_med_combo.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(input_frame, text="Weg:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.op_route_var = ctk.StringVar(value="oral")
        self.op_route_combo = ctk.CTkComboBox(input_frame, values=["oral", "iv", "sc", "sl", "td"], variable=self.op_route_var)
        self.op_route_combo.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(input_frame, text="Dosis:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.op_dose_entry = ctk.CTkEntry(input_frame)
        self.op_dose_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        self.op_dose_entry.insert(0, "0")

        ctk.CTkLabel(input_frame, text="Vorherige OME (Methadon):").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.op_prev_entry = ctk.CTkEntry(input_frame)
        self.op_prev_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(input_frame, text="Abschlag (%):").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.op_discount_entry = ctk.CTkEntry(input_frame)
        self.op_discount_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
        self.op_discount_entry.insert(0, "0")

        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(frame, text="Umrechnen", command=self.calc_opioid).pack(pady=20)
        self.op_res_label = ctk.CTkLabel(frame, text="Ergebnis: -", font=ctk.CTkFont(size=18, weight="bold"))
        self.op_res_label.pack(pady=10)

        return frame

    def calc_opioid(self):
        try:
            drug = self.op_med_var.get()
            route = self.op_route_var.get()
            dose = self.validate_float(self.op_dose_entry.get())
            if dose is None: raise ValueError("Ungültige Dosis")
            
            prev_ome_str = self.op_prev_entry.get().strip()
            prev_ome = self.validate_float(prev_ome_str) if prev_ome_str else None
            
            discount = self.validate_float(self.op_discount_entry.get())
            if discount is None: discount = 0.0
            
            ome = converter.to_morphine_ome(drug, dose, route, prev_ome, discount)
            unit = "µg" if "fentanyl" in drug.lower() else "mg"
            if "fentanyl" in drug.lower() and route == "td": unit = "µg/h"
            
            self.op_res_label.configure(text=f"{dose} {unit} {drug} ({route}) ≈ {ome} mg OME")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def create_conv_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="Dosis Umstellung", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 10))
        
        ctk.CTkLabel(frame, text=converter.DISCLAIMER, wraplength=500, text_color="red").pack(pady=10)

        conv_frame = ctk.CTkFrame(frame)
        conv_frame.pack(pady=20, padx=40, fill="x")

        self.conv_type_var = ctk.StringVar(value="Benzo")
        type_frame = ctk.CTkFrame(conv_frame, fg_color="transparent")
        type_frame.pack(pady=10)
        ctk.CTkRadioButton(type_frame, text="Benzodiazepine", variable=self.conv_type_var, value="Benzo", command=self.update_conv_ui).pack(side="left", padx=10)
        ctk.CTkRadioButton(type_frame, text="Opioide", variable=self.conv_type_var, value="Opioid", command=self.update_conv_ui).pack(side="left", padx=10)

        # From
        ctk.CTkLabel(conv_frame, text="Von:").pack(anchor="w", padx=10)
        self.conv_from_var = ctk.StringVar()
        self.conv_from_combo = ctk.CTkComboBox(conv_frame, variable=self.conv_from_var)
        self.conv_from_combo.pack(fill="x", padx=10, pady=5)

        self.conv_from_route_label = ctk.CTkLabel(conv_frame, text="Weg (von):")
        self.conv_from_route_var = ctk.StringVar(value="oral")
        self.conv_from_route_combo = ctk.CTkComboBox(conv_frame, variable=self.conv_from_route_var, values=["oral", "iv", "sc", "sl", "td"])

        ctk.CTkLabel(conv_frame, text="Dosis:").pack(anchor="w", padx=10)
        self.conv_dose_entry = ctk.CTkEntry(conv_frame)
        self.conv_dose_entry.pack(fill="x", padx=10, pady=5)
        self.conv_dose_entry.insert(0, "0")

        # To
        ctk.CTkLabel(conv_frame, text="Auf:").pack(anchor="w", padx=10)
        self.conv_to_var = ctk.StringVar()
        self.conv_to_combo = ctk.CTkComboBox(conv_frame, variable=self.conv_to_var)
        self.conv_to_combo.pack(fill="x", padx=10, pady=5)

        self.conv_to_route_label = ctk.CTkLabel(conv_frame, text="Weg (auf):")
        self.conv_to_route_var = ctk.StringVar(value="oral")
        self.conv_to_route_combo = ctk.CTkComboBox(conv_frame, variable=self.conv_to_route_var, values=["oral", "iv", "sc", "sl", "td"])

        ctk.CTkButton(frame, text="Umstellen", command=self.calc_conv).pack(pady=20)
        self.conv_res_label = ctk.CTkLabel(frame, text="Ergebnis: -", font=ctk.CTkFont(size=18, weight="bold"), wraplength=500)
        self.conv_res_label.pack(pady=10)

        self.update_conv_ui()
        return frame

    def update_conv_ui(self):
        if self.conv_type_var.get() == "Benzo":
            names = sorted(list(converter.DISPLAY_NAMES.values()))
            self.conv_from_combo.configure(values=names)
            self.conv_to_combo.configure(values=names)
            self.conv_from_var.set(names[0])
            self.conv_to_var.set(names[0])
            
            self.conv_from_route_label.pack_forget()
            self.conv_from_route_combo.pack_forget()
            self.conv_to_route_label.pack_forget()
            self.conv_to_route_combo.pack_forget()
        else:
            op_names = sorted(list(set(d.capitalize() for (d, r) in converter.OPIOID_TABLE.keys() | converter.USER_OPIOID_TABLE.keys())))
            self.conv_from_combo.configure(values=op_names)
            self.conv_to_combo.configure(values=op_names)
            self.conv_from_var.set(op_names[0])
            self.conv_to_var.set(op_names[0])
            
            self.conv_from_route_label.pack(anchor="w", padx=10)
            self.conv_from_route_combo.pack(fill="x", padx=10, pady=5)
            self.conv_to_route_label.pack(anchor="w", padx=10)
            self.conv_to_route_combo.pack(fill="x", padx=10, pady=5)

    def calc_conv(self):
        try:
            dose = self.validate_float(self.conv_dose_entry.get())
            if dose is None: raise ValueError("Ungültige Dosis")
            
            if self.conv_type_var.get() == "Benzo":
                from_disp = self.conv_from_var.get()
                to_disp = self.conv_to_var.get()
                from_k = next(k for k, v in converter.DISPLAY_NAMES.items() if v == from_disp)
                to_k = next(k for k, v in converter.DISPLAY_NAMES.items() if v == to_disp)
                
                diaz_equiv, _ = converter.convert_to_diazepam(from_k, dose)
                target_dose = converter.from_diazepam(to_k, diaz_equiv)
                self.conv_res_label.configure(text=f"{dose} mg {from_disp} ≈ {target_dose:.2f} mg {to_disp}\n(entspricht {diaz_equiv:.2f} mg Diazepam)")
            else:
                from_d = self.conv_from_var.get()
                to_d = self.conv_to_var.get()
                from_r = self.conv_from_route_var.get()
                to_r = self.conv_to_route_var.get()
                
                ome = converter.to_morphine_ome(from_d, dose, from_r)
                target_dose = converter.from_morphine_ome(to_d, ome, to_r)
                self.conv_res_label.configure(text=f"{dose} mg {from_d} ({from_r}) ≈ {target_dose:.2f} mg {to_d} ({to_r})\n(entspricht {ome:.2f} mg OME)")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def create_adv_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
        # Custom Opioid
        ctk.CTkLabel(frame, text="Benutzerdefiniertes Opioid", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 10))
        
        custom_frame = ctk.CTkFrame(frame)
        custom_frame.pack(pady=10, padx=40, fill="x")
        
        ctk.CTkLabel(custom_frame, text="Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.cust_name = ctk.CTkEntry(custom_frame)
        self.cust_name.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(custom_frame, text="Weg:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.cust_route = ctk.CTkEntry(custom_frame)
        self.cust_route.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(custom_frame, text="Faktor:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.cust_fact = ctk.CTkEntry(custom_frame)
        self.cust_fact.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        custom_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(frame, text="Speichern", command=self.add_custom).pack(pady=10)

        ctk.CTkFrame(frame, height=2, fg_color="gray").pack(pady=20, fill="x", padx=40)

        # Tolerance
        ctk.CTkLabel(frame, text="Toleranz-Modell", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        tol_frame = ctk.CTkFrame(frame)
        tol_frame.pack(pady=10, padx=40, fill="x")
        
        self.tol_type_var = ctk.StringVar(value="Opioid (OME)")
        type_f = ctk.CTkFrame(tol_frame, fg_color="transparent")
        type_f.pack(pady=5)
        ctk.CTkRadioButton(type_f, text="Opioid (OME)", variable=self.tol_type_var, value="Opioid (OME)").pack(side="left", padx=10)
        ctk.CTkRadioButton(type_f, text="Benzo (Diazepam)", variable=self.tol_type_var, value="Benzo (mg Diazepam)").pack(side="left", padx=10)

        ctk.CTkLabel(tol_frame, text="Start-Dosis:").pack(anchor="w", padx=10)
        self.tol_start = ctk.CTkEntry(tol_frame)
        self.tol_start.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(tol_frame, text="Tage:").pack(anchor="w", padx=10)
        self.tol_days = ctk.CTkEntry(tol_frame)
        self.tol_days.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(tol_frame, text="Rate (z.B. 0.02):").pack(anchor="w", padx=10)
        self.tol_rate = ctk.CTkEntry(tol_frame)
        self.tol_rate.insert(0, "0.02")
        self.tol_rate.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(frame, text="Berechnen", command=self.calc_tol).pack(pady=10)
        self.tol_res_label = ctk.CTkLabel(frame, text="Ergebnis: -", font=ctk.CTkFont(size=18, weight="bold"))
        self.tol_res_label.pack(pady=10)

        return frame

    def add_custom(self):
        try:
            name = self.cust_name.get().strip()
            route = self.cust_route.get().strip()
            fact = self.validate_float(self.cust_fact.get())
            if not name or not route or fact is None: raise ValueError("Bitte alle Felder korrekt ausfüllen")
            converter.save_custom_drug(name, route, fact)
            messagebox.showinfo("Erfolg", f"{name} gespeichert")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def calc_tol(self):
        try:
            start = self.validate_float(self.tol_start.get())
            days = int(self.tol_days.get())
            rate = self.validate_float(self.tol_rate.get())
            if start is None or rate is None: raise ValueError("Ungültige Werte")
            
            res = converter.calculate_tolerance_development(start, days, rate)
            unit = "mg OME" if self.tol_type_var.get() == "Opioid (OME)" else "mg Diazepam"
            self.tol_res_label.configure(text=f"Dosis nach {days} Tagen: {res} {unit}")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def create_hist_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="Historie der Änderungen", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 10))
        
        self.hist_text = ctk.CTkTextbox(frame, width=600, height=400)
        self.hist_text.pack(pady=20, padx=20)
        
        ctk.CTkButton(frame, text="Aktualisieren", command=self.refresh_hist).pack(pady=10)
        self.refresh_hist()
        return frame

    def refresh_hist(self):
        self.hist_text.delete("0.0", "end")
        for entry in converter.get_history():
            line = f"[{entry['date']}] {entry['type']} - {entry['drug']}: {entry['change']}\n"
            self.hist_text.insert("end", line)
