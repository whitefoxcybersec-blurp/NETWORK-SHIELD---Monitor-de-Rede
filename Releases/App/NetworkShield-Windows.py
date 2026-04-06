import tkinter as tk
import psutil
import threading
import time
import json
from datetime import datetime


class NetworkShieldApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🛡️ NETWORK SHIELD v3.0")
        self.root.geometry("1100x700")
        self.root.configure(bg='#0c0c0c')
        self.root.resizable(False, False)

        self.monitoring = False
        self.traffic_history = []
        self.intrusions = 0
        self.start_time = time.time()

        self.setup_ui()

    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#1a1a2e", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        title = tk.Label(header_frame, text="🛡️ NETWORK SHIELD",
                         font=("Arial", 28, "bold"), fg="#00d4ff", bg="#1a1a2e")
        title.pack(expand=True)

        subtitle = tk.Label(header_frame, text="Monitor Profissional de Rede",
                            font=("Arial", 12), fg="#aaa", bg="#1a1a2e")
        subtitle.pack()

        # Stats
        stats_frame = tk.Frame(self.root, bg="#16213e")
        stats_frame.pack(pady=20, padx=30, fill="x")

        self.traffic_var = tk.StringVar(value="0.00 MB/s")
        self.intrusions_var = tk.StringVar(value="0")
        self.connections_var = tk.StringVar(value="0")
        self.cpu_var = tk.StringVar(value="0%")

        stats_config = [
            ("🌐 Tráfego", self.traffic_var, "#00d4ff"),
            ("🚨 Intrusões", self.intrusions_var, "#ff6b6b"),
            ("🔗 Conexões", self.connections_var, "#4ecdc4"),
            ("💻 CPU", self.cpu_var, "#ffeb3b")
        ]

        for i, (label, var, color) in enumerate(stats_config):
            card = tk.Frame(stats_frame, bg="#0f3460", relief="ridge", bd=2)
            card.grid(row=0, column=i, padx=15, pady=15, sticky="nsew")

            tk.Label(card, text=label, font=("Arial", 12, "bold"),
                     fg=color, bg="#0f3460").pack(pady=15)
            tk.Label(card, textvariable=var, font=("Arial", 24, "bold"),
                     fg=color, bg="#0f3460").pack(pady=(0, 15))

        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Controls
        ctrl_frame = tk.Frame(self.root, bg="#1a1a2e")
        ctrl_frame.pack(pady=20)

        self.start_btn = tk.Button(ctrl_frame, text="🚀 INICIAR MONITORAMENTO",
                                   command=self.start_monitoring,
                                   font=("Arial", 14, "bold"), bg="#00d4ff",
                                   fg="black", relief="flat", padx=40, pady=12)
        self.start_btn.pack(side="left", padx=15)

        self.stop_btn = tk.Button(ctrl_frame, text="⏹️ PARAR",
                                  command=self.stop_monitoring,
                                  font=("Arial", 14, "bold"), bg="#ff6b6b",
                                  fg="white", relief="flat", padx=40, pady=12,
                                  state="disabled")
        self.stop_btn.pack(side="left", padx=15)

        export_btn = tk.Button(ctrl_frame, text="📊 EXPORTAR RELATÓRIO",
                               command=self.export_data,
                               font=("Arial", 12, "bold"), bg="#4ecdc4",
                               fg="black", relief="flat", padx=30, pady=12)
        export_btn.pack(side="left", padx=15)

        # Graph
        graph_frame = tk.LabelFrame(self.root, text="📈 Tráfego em Tempo Real",
                                    font=("Arial", 12, "bold"), fg="#00d4ff", bg="#16213e")
        graph_frame.pack(pady=20, padx=30, fill="both", expand=True)

        self.canvas = tk.Canvas(graph_frame, bg="#0c0c0c", height=280, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)

        # Alerts
        alerts_frame = tk.LabelFrame(self.root, text="🚨 ALERTAS",
                                     font=("Arial", 12, "bold"), fg="#ff6b6b", bg="#1a1a2e")
        alerts_frame.pack(pady=20, padx=30, fill="x")

        self.alerts_text = tk.Text(alerts_frame, height=6, bg="#0c0c0c",
                                   fg="#ff6b6b", font=("Consolas", 11),
                                   insertbackground="white")
        scrollbar = tk.Scrollbar(alerts_frame, orient="vertical", command=self.alerts_text.yview)
        self.alerts_text.configure(yscrollcommand=scrollbar.set)

        self.alerts_text.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=20)
        scrollbar.pack(side="right", fill="y", pady=20)

    def start_monitoring(self):
        self.monitoring = True
        self.start_btn.config(state="disabled", bg="#666")
        self.stop_btn.config(state="normal")
        self.add_alert("🚀 Monitoramento iniciado!")
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        self.monitoring = False
        self.start_btn.config(state="normal", bg="#00d4ff")
        self.stop_btn.config(state="disabled")
        self.add_alert("⏹️ Monitoramento parado.")

    def monitor_loop(self):
        while self.monitoring:
            try:
                data = self.get_network_data()
                self.root.after(0, lambda: self.update_ui(data))
                time.sleep(1)
            except Exception as e:
                self.root.after(0, lambda: self.add_alert(f"❌ Erro: {str(e)}"))
                time.sleep(2)

    def get_network_data(self):
        try:
            io1 = psutil.net_io_counters(pernic=True)
            time.sleep(0.8)
            io2 = psutil.net_io_counters(pernic=True)

            total_bytes = 0
            for interface in io1:
                if not interface.startswith('lo') and 'loopback' not in interface.lower():
                    delta_recv = io2[interface].bytes_recv - io1[interface].bytes_recv
                    delta_sent = io2[interface].bytes_sent - io1[interface].bytes_sent
                    total_bytes += delta_recv + delta_sent

            traffic_mbps = (total_bytes / 1024 / 1024) * 1.25

            return {
                'traffic': max(0, traffic_mbps),
                'connections': len(psutil.net_connections()),
                'cpu': psutil.cpu_percent(interval=0.1)
            }
        except:
            return {'traffic': 0, 'connections': 0, 'cpu': 0}

    def update_ui(self, data):
        self.traffic_var.set(f"{data['traffic']:.2f} MB/s")
        self.intrusions_var.set(str(self.intrusions))
        self.connections_var.set(f"{data['connections']:,}")
        self.cpu_var.set(f"{data['cpu']:.1f}%")

        self.traffic_history.append(data['traffic'])
        if len(self.traffic_history) > 120:
            self.traffic_history.pop(0)
        self.draw_graph()

        if data['traffic'] > 20:
            if len(self.traffic_history) > 5 and all(t > 15 for t in self.traffic_history[-5:]):
                self.add_alert(f"🚨 POSSÍVEL DDoS: {data['traffic']:.2f} MB/s")
                self.intrusions += 1
        elif data['traffic'] < 0.01:
            self.add_alert("⚠️ Tráfego muito baixo")

    def draw_graph(self):
        self.canvas.delete("all")
        if len(self.traffic_history) < 2:
            return

        w, h = 1000, 220
        max_val = max(self.traffic_history[-50:] + [1]) * 1.2

        self.canvas.create_rectangle(0, 0, w, h, fill="#0c0c0c")

        for i in range(0, 101, 20):
            x = (i / 100) * w
            self.canvas.create_line(x, 0, x, h, fill="#333", width=1)

        for i in range(1, min(len(self.traffic_history), 100)):
            x1 = ((i - 1) / 100) * w
            y1 = h - (self.traffic_history[-i] / max_val * h * 0.8)
            x2 = (i / 100) * w
            y2 = h - (self.traffic_history[-i - 1] / max_val * h * 0.8)

            color = "#ff6b6b" if self.traffic_history[-i] > 20 else "#00d4ff"
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=4, smooth=True)

    def add_alert(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.alerts_text.insert("1.0", f"[{timestamp}] {message}\n")
        self.alerts_text.see("1.0")

    def export_data(self):
        data = {
            'timestamp': datetime.now().isoformat(),
            'traffic_history': self.traffic_history[-100:],
            'total_intrusions': self.intrusions,
            'uptime_seconds': int(time.time() - self.start_time)
        }
        filename = f"NetworkShield_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        self.add_alert(f"📊 Relatório salvo: {filename}")


if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkShieldApp(root)
    root.mainloop()