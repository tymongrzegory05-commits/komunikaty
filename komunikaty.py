#!/usr/bin/env python3
"""
Program do puszczania komunikatów dźwiękowych.
Odtwarza pliki dźwiękowe co godzinę o ustalonych minutach.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import threading
import time
from datetime import datetime
import os


class SoundSlot:
    """Klasa reprezentująca pojedynczy slot na komunikat dźwiękowy."""
    
    def __init__(self, parent, slot_id, on_remove_callback):
        self.slot_id = slot_id
        self.file_path = None
        self.file_name = "Nie wybrano pliku"
        self.minute = 0
        self.on_remove_callback = on_remove_callback
        
        # Ramka dla slotu
        self.frame = tk.Frame(parent, relief=tk.RIDGE, borderwidth=2, padx=5, pady=5)
        
        # Numer slotu
        tk.Label(self.frame, text=f"Slot {slot_id + 1}", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=3, sticky="w")
        
        # Przycisk wyboru pliku
        self.file_button = tk.Button(self.frame, text="Wybierz plik", command=self.choose_file, width=12)
        self.file_button.grid(row=1, column=0, padx=2)
        
        # Etykieta nazwy pliku
        self.file_label = tk.Label(self.frame, text=self.file_name, width=30, anchor="w", fg="gray")
        self.file_label.grid(row=1, column=1, padx=2)
        
        # Wybór minuty
        tk.Label(self.frame, text="Minuta:").grid(row=2, column=0, sticky="w", padx=2)
        self.minute_var = tk.StringVar(value="0")
        self.minute_spinbox = tk.Spinbox(self.frame, from_=0, to=59, textvariable=self.minute_var, width=5)
        self.minute_spinbox.grid(row=2, column=1, sticky="w", padx=2)
        
        # Przycisk usuwania
        self.remove_button = tk.Button(self.frame, text="Usuń", command=self.remove, width=8, bg="#ffcccc")
        self.remove_button.grid(row=2, column=2, padx=2)
        
        # Wskaźnik aktywności
        self.status_label = tk.Label(self.frame, text="●", fg="gray", font=("Arial", 14))
        self.status_label.grid(row=0, column=3, padx=5)
    
    def choose_file(self):
        """Wybiera plik dźwiękowy."""
        file_path = filedialog.askopenfilename(
            title="Wybierz plik dźwiękowy",
            filetypes=[
                ("Pliki dźwiękowe", "*.mp3 *.wav *.ogg *.flac"),
                ("Wszystkie pliki", "*.*")
            ]
        )
        if file_path:
            self.file_path = file_path
            self.file_name = os.path.basename(file_path)
            self.file_label.config(text=self.file_name, fg="black")
            self.minute = int(self.minute_var.get())
    
    def remove(self):
        """Usuwa slot."""
        self.on_remove_callback(self.slot_id)
    
    def get_config(self):
        """Zwraca konfigurację slotu."""
        return {
            'file_path': self.file_path,
            'minute': int(self.minute_var.get())
        }
    
    def set_status(self, playing):
        """Ustawia wskaźnik aktywności."""
        if playing:
            self.status_label.config(text="▶", fg="green")
        else:
            self.status_label.config(text="●", fg="gray")


class SoundSchedulerApp:
    """Główna aplikacja do zarządzania komunikatami."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Komunikaty Dźwiękowe")
        self.root.geometry("600x700")
        
        # Inicjalizacja pygame do odtwarzania dźwięku
        pygame.mixer.init()
        
        self.slots = []
        self.running = False
        self.scheduler_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Tworzy interfejs użytkownika."""
        # Główny kontener
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tytuł
        tk.Label(main_frame, text="Harmonogram Komunikatów Dźwiękowych", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Przycisk dodawania slotu
        self.add_button = tk.Button(main_frame, text="+ Dodaj slot", command=self.add_slot, 
                                   font=("Arial", 10), height=2)
        self.add_button.pack(pady=5, fill=tk.X)
        
        # Kontener na sloty
        self.slots_frame = tk.Frame(main_frame)
        self.slots_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Przyciski sterowania
        control_frame = tk.Frame(main_frame)
        control_frame.pack(pady=10, fill=tk.X)
        
        self.start_button = tk.Button(control_frame, text="▶ Start", command=self.start_scheduler,
                                     font=("Arial", 10), bg="#ccffcc", width=15)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(control_frame, text="⏹ Stop", command=self.stop_scheduler,
                                    font=("Arial", 10), bg="#ffcccc", width=15, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = tk.Label(main_frame, text="Status: Zatrzymano", font=("Arial", 10))
        self.status_label.pack(pady=5)
        
        # Informacja o czasie
        self.time_label = tk.Label(main_frame, text="", font=("Arial", 12))
        self.time_label.pack(pady=5)
        
        # Dodaj początkowe sloty
        for _ in range(3):
            self.add_slot()
        
        # Aktualizacja zegara
        self.update_clock()
    
    def add_slot(self):
        """Dodaje nowy slot."""
        if len(self.slots) >= 10:
            messagebox.showwarning("Ostrzeżenie", "Maksymalna liczba slotów to 10")
            return
        
        slot = SoundSlot(self.slots_frame, len(self.slots), self.remove_slot)
        slot.frame.pack(fill=tk.X, pady=5)
        self.slots.append(slot)
    
    def remove_slot(self, slot_id):
        """Usuwa slot o podanym ID."""
        if slot_id < len(self.slots):
            slot = self.slots[slot_id]
            slot.frame.destroy()
            self.slots.pop(slot_id)
            
            # Przeindeksuj pozostałe sloty
            for i, s in enumerate(self.slots):
                s.slot_id = i
                s.frame.children['!label'].config(text=f"Slot {i + 1}")
    
    def start_scheduler(self):
        """Uruchamia harmonogram."""
        if not self.slots:
            messagebox.showwarning("Ostrzeżenie", "Brak skonfigurowanych slotów")
            return
        
        # Sprawdź czy wszystkie sloty mają pliki
        for slot in self.slots:
            if not slot.file_path:
                messagebox.showwarning("Ostrzeżenie", f"Slot {slot.slot_id + 1} nie ma wybranego pliku")
                return
        
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.add_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Uruchomiony", fg="green")
        
        # Uruchom wątek harmonogramu
        self.scheduler_thread = threading.Thread(target=self.scheduler_loop, daemon=True)
        self.scheduler_thread.start()
    
    def stop_scheduler(self):
        """Zatrzymuje harmonogram."""
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.add_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Zatrzymano", fg="black")
        
        # Zresetuj wskaźniki
        for slot in self.slots:
            slot.set_status(False)
    
    def scheduler_loop(self):
        """Główna pętla harmonogramu."""
        last_minute = -1
        
        while self.running:
            now = datetime.now()
            current_minute = now.minute
            
            # Sprawdź czy minuta się zmieniła
            if current_minute != last_minute:
                last_minute = current_minute
                
                # Sprawdź każdy slot
                for slot in self.slots:
                    slot_minute = int(slot.minute_var.get())
                    if slot_minute == current_minute and slot.file_path:
                        # Odtwórz dźwięk
                        self.play_sound(slot)
            
            time.sleep(1)
    
    def play_sound(self, slot):
        """Odtwarza dźwięk z podanego slotu."""
        try:
            # Zaktualizuj wskaźnik w głównym wątku
            self.root.after(0, lambda: slot.set_status(True))
            
            # Odtwórz dźwięk
            pygame.mixer.music.load(slot.file_path)
            pygame.mixer.music.play()
            
            # Czekaj na zakończenie odtwarzania
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # Zaktualizuj wskaźnik
            self.root.after(0, lambda: slot.set_status(False))
            
        except Exception as e:
            print(f"Błąd odtwarzania: {e}")
            self.root.after(0, lambda: slot.set_status(False))
    
    def update_clock(self):
        """Aktualizuje wyświetlany czas."""
        now = datetime.now()
        self.time_label.config(text=f"Aktualny czas: {now.strftime('%H:%M:%S')}")
        self.root.after(1000, self.update_clock)
    
    def on_closing(self):
        """Obsługa zamknięcia aplikacji."""
        self.running = False
        pygame.mixer.quit()
        self.root.destroy()


def main():
    """Funkcja główna."""
    root = tk.Tk()
    app = SoundSchedulerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
