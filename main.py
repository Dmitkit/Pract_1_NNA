import tkinter as tk
from tkinter import ttk
import math
import time
import random

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Алгоритм ближайшего соседа для задачи коммивояжёра")

        self.control_panel = tk.Frame(self.root, width=200)
        self.control_panel.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        self.clear_button = tk.Button(self.control_panel, text="Очистить", command=self.clear_all)
        self.clear_button.grid(row=4, column=0, padx=10, pady=10)

        self.time_label = tk.Label(self.control_panel, text="Затраченное время (сек): ")
        self.time_label.grid(row=5, column=0, padx=10, pady=5)

        self.time_display = tk.Entry(self.control_panel, width=25)
        self.time_display.grid(row=5, column=1, padx=10, pady=5)

        ttk.Separator(self.root, orient=tk.VERTICAL).grid(row=0, column=1, rowspan=2, sticky="ns", padx=5)

        self.calc_button = tk.Button(self.control_panel, text="Рассчитать путь", command=self.calculate_tsp)
        self.calc_button.grid(row=0, column=0, padx=10, pady=10)

        self.calc_button_mod = tk.Button(self.control_panel, text="Рассчитать путь модифицированный", command=self.calculate_tsp_improved)
        self.calc_button_mod.grid(row=5, column=0, padx=10, pady=10)

        self.default_button = tk.Button(self.control_panel, text="Пример по умолчанию", command=self.load_default_example)
        self.default_button.grid(row=1, column=0, padx=10, pady=10)

        self.path_label = tk.Label(self.control_panel, text="Путь: ")
        self.path_label.grid(row=2, column=0, padx=10, pady=5)

        self.length_label = tk.Label(self.control_panel, text="Длина пути: ")
        self.length_label.grid(row=3, column=0, padx=10, pady=5)

        self.path_display = tk.Entry(self.control_panel, width=25)
        self.path_display.grid(row=2, column=1, padx=10, pady=5)

        self.length_display = tk.Entry(self.control_panel, width=25)
        self.length_display.grid(row=3, column=1, padx=10, pady=5)

        self.canvas = tk.Canvas(self.root, width=600, height=300, bg='white')
        self.canvas.grid(row=0, column=2, padx=10, pady=10)
        tk.Label(self.root, text="Исходный граф").grid(row=0, column=2, sticky="n", pady=(0, 5))

        self.result_canvas = tk.Canvas(self.root, width=600, height=300, bg='white')
        self.result_canvas.grid(row=1, column=2, padx=10, pady=10)
        tk.Label(self.root, text="Гамильтонов цикл").grid(row=1, column=2, sticky="n", pady=(0, 5))

        ttk.Separator(self.root, orient=tk.VERTICAL).grid(row=0, column=3, rowspan=2, sticky="ns", padx=5)

        self.table_frame = tk.Frame(self.root, width=300, height=400)
        self.table_frame.grid(row=0, column=4, rowspan=2, padx=10, pady=10, sticky="n")

        self.edge_table = ttk.Treeview(self.table_frame, columns=("From", "To", "Weight"), show="headings")
        self.edge_table.heading("From", text="От", anchor="w")
        self.edge_table.heading("To", text="К", anchor="w")
        self.edge_table.heading("Weight", text="Вес", anchor="w")
        self.edge_table.column("From", width=80)
        self.edge_table.column("To", width=80)
        self.edge_table.column("Weight", width=100)
        self.edge_table.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.edge_table.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.edge_table.configure(yscrollcommand=self.scrollbar.set)

        self.edge_table.bind("<Double-1>", self.on_table_double_click)

        self.node_radius = 20
        self.nodes = []  
        self.edges = []  
        self.selected_node = None  
        self.node_positions = {}  

        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def clear_all(self):
        self.time_display.delete(0, tk.END)

        self.canvas.delete("all")
        self.result_canvas.delete("all")

        self.path_display.delete(0, tk.END)
        self.length_display.delete(0, tk.END)

        for item in self.edge_table.get_children():
            self.edge_table.delete(item)

        self.nodes.clear()
        self.edges.clear()
        self.node_positions.clear()

    def on_canvas_click(self, event):

        x, y = event.x, event.y

        node = self.get_node_at_position(x, y)
        if node:
            if self.selected_node:

                self.create_edge(self.selected_node, node)
                self.selected_node = None
            else:

                self.selected_node = node
        else:

            if self.selected_node:
                self.selected_node = None

            self.create_node(x, y)

    def create_node(self, x, y):
        node_id = len(self.nodes) + 1
        node = {'id': node_id, 'x': x, 'y': y}
        self.nodes.append(node)
        self.node_positions[node_id] = (x, y)
        self.canvas.create_oval(x - self.node_radius, y - self.node_radius, x + self.node_radius, y + self.node_radius,
                                fill="blue", tags=f"node{node_id}")
        self.canvas.create_text(x, y, text=str(node_id), fill="white")

    def create_edge(self, from_node, to_node):
        from_x, from_y = from_node['x'], from_node['y']
        to_x, to_y = to_node['x'], to_node['y']

        edge_id = len(self.edges) + 1
        self.canvas.create_line(from_x, from_y, to_x, to_y, arrow=tk.LAST, tags=f"edge{edge_id}")

        weight = self.calculate_distance(from_node, to_node)
        self.edges.append({'id': edge_id, 'from': from_node['id'], 'to': to_node['id'], 'weight': weight})
        self.edge_table.insert("", "end", values=(from_node['id'], to_node['id'], weight))

    def get_node_at_position(self, x, y):
        for node in self.nodes:
            node_x, node_y = node['x'], node['y']
            if (node_x - self.node_radius < x < node_x + self.node_radius) and (node_y - self.node_radius < y < node_y + self.node_radius):
                return node
        return None

    def calculate_distance(self, from_node, to_node):
        x1, y1 = from_node['x'], from_node['y']
        x2, y2 = to_node['x'], to_node['y']
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def on_table_double_click(self, event):

        region = self.edge_table.identify_region(event.x, event.y)
        if region == "cell":
            column = self.edge_table.identify_column(event.x)
            if column == "#3":  
                item = self.edge_table.selection()[0]
                column_box = self.edge_table.bbox(item, column)
                current_value = self.edge_table.item(item, "values")[2]

                entry = ttk.Entry(self.edge_table, width=10)
                entry.place(x=column_box[0], y=column_box[1], width=column_box[2], height=column_box[3])
                entry.insert(0, current_value)
                entry.focus_set()

                entry.bind("<FocusOut>", lambda e: self.update_edge_weight(item, entry))
                entry.bind("<Return>", lambda e: self.update_edge_weight(item, entry))

    def update_edge_weight(self, item, entry):
        if not self.edge_table.exists(item):
            entry.destroy() 
            return

        new_weight = entry.get()
        try:
            new_weight = float(new_weight)
            if new_weight < 0:
                raise ValueError("Вес не может быть отрицательным")
        except ValueError:
            tk.messagebox.showerror("Ошибка", "Введите корректное число для веса")
            return


        values = list(self.edge_table.item(item, "values"))
        values[2] = new_weight  
        self.edge_table.item(item, values=values)  


        from_node_id = int(values[0])
        to_node_id = int(values[1])
        for edge in self.edges:
            if edge['from'] == from_node_id and edge['to'] == to_node_id:
                edge['weight'] = new_weight
                break

        entry.destroy() 

    def load_default_example(self):

        self.nodes.clear()
        self.edges.clear()
        self.node_positions.clear()
        self.canvas.delete("all")
        self.result_canvas.delete("all")
        self.edge_table.delete(*self.edge_table.get_children())

        default_nodes = [
            {'id': 1, 'x': 200, 'y': 80, 'label': 'a'},
            {'id': 2, 'x': 100, 'y': 100, 'label': 'b'},
            {'id': 3, 'x': 100, 'y': 150, 'label': 'c'},
            {'id': 4, 'x': 200, 'y': 200, 'label': 'd'},
            {'id': 5, 'x': 250, 'y': 150, 'label': 'f'},
            {'id': 6, 'x': 200, 'y': 150, 'label': 'g'},
        ]
        default_edges = [
            {'from': 1, 'to': 2, 'weight': 3},
            {'from': 2, 'to': 1, 'weight': 3},
            {'from': 2, 'to': 3, 'weight': 8},
            {'from': 3, 'to': 2, 'weight': 3},
            {'from': 3, 'to': 4, 'weight': 1},
            {'from': 4, 'to': 3, 'weight': 8},
            {'from': 4, 'to': 5, 'weight': 1},
            {'from': 5, 'to': 4, 'weight': 3},
            {'from': 5, 'to': 1, 'weight': 3},
            {'from': 1, 'to': 5, 'weight': 1},
            {'from': 6, 'to': 2, 'weight': 3},
            {'from': 6, 'to': 1, 'weight': 3},
            {'from': 6, 'to': 3, 'weight': 3},
            {'from': 6, 'to': 4, 'weight': 5},
            {'from': 6, 'to': 5, 'weight': 4},
            {'from': 6, 'to': 5, 'weight': 4},
            {'from': 2, 'to': 6, 'weight': 3},
            {'from': 3, 'to': 6, 'weight': 1}
        ]
        random.seed(42)

        nodes_15 = [{'id': i, 'x': random.randint(50, 350), 'y': random.randint(50, 350)} for i in range(1, 16)]

        edges_15 = []
        for i in range(1, 16):
            for j in range(i + 1, 16):
                if random.random() < 0.7:  
                    weight = random.randint(1, 10)
                    edges_15.append({'from': i, 'to': j, 'weight': weight})
                    edges_15.append({'from': j, 'to': i, 'weight': weight})


        nodes_30 = [{'id': i, 'x': random.randint(50, 550), 'y': random.randint(50, 550)} for i in range(1, 31)]

        edges_30 = []
        for i in range(1, 31):
            for j in range(i + 1, 31):
                if random.random() < 0.9: 
                    weight = random.randint(1, 10)
                    edges_30.append({'from': i, 'to': j, 'weight': weight})
                    edges_30.append({'from': j, 'to': i, 'weight': weight})


        # default_nodes = nodes_15
        # default_edges = edges_15

        for node in default_nodes:
            self.create_node(node['x'], node['y'])

            self.canvas.create_text(node['x'], node['y'] - 25, fill="black")

        for edge in default_edges:
            from_node = next(n for n in self.nodes if n['id'] == edge['from'])
            to_node = next(n for n in self.nodes if n['id'] == edge['to'])
            self.create_edge(from_node, to_node)

        for edge in self.edges:
            for default_edge in default_edges:
                if edge['from'] == default_edge['from'] and edge['to'] == default_edge['to']:
                    edge['weight'] = default_edge['weight']

                    for item in self.edge_table.get_children():
                        values = self.edge_table.item(item, "values")
                        if int(values[0]) == edge['from'] and int(values[1]) == edge['to']:
                            self.edge_table.item(item, values=(values[0], values[1], default_edge['weight']))
                    break

    def calculate_tsp(self):
        start_time = time.time()  
        if len(self.nodes) < 2:
            end_time = time.time()  
            elapsed_time = end_time - start_time  
            self.time_display.delete(0, tk.END)
            self.time_display.insert(0, f"{elapsed_time:.4f}")  
            return  

        edges_from_node = {}
        for edge in self.edges:
            from_node = edge['from']
            if from_node not in edges_from_node:
                edges_from_node[from_node] = []
            edges_from_node[from_node].append(edge)

        start_node = self.nodes[0]
        current_node_id = start_node['id']
        path = [current_node_id]
        total_length = 0

        visited = {node['id']: False for node in self.nodes}
        visited[current_node_id] = True

        for _ in range(len(self.nodes) - 1):

            available_edges = edges_from_node.get(current_node_id, [])

            valid_edges = [edge for edge in available_edges if not visited[edge['to']]]

            if not valid_edges:

                break

            min_edge = min(valid_edges, key=lambda x: x['weight'])
            next_node_id = min_edge['to']
            path.append(next_node_id)
            total_length += min_edge['weight']
            visited[next_node_id] = True
            current_node_id = next_node_id

        return_edges = [edge for edge in edges_from_node.get(current_node_id, []) 
                       if edge['to'] == start_node['id']]

        if return_edges:

            total_length += return_edges[0]['weight']
            path.append(start_node['id'])

        self.display_path(path, total_length)
        self.draw_result_path(path)
        end_time = time.time()  
        elapsed_time = end_time - start_time  
        self.time_display.delete(0, tk.END)
        self.time_display.insert(0, f"{elapsed_time:.4f}")  

    def calculate_tsp_improved(self):
        def run_nearest_neighbor(start_node):
            edges_from_node = {}
            for edge in self.edges:
                if edge['from'] not in edges_from_node:
                    edges_from_node[edge['from']] = []
                edges_from_node[edge['from']].append(edge)

            current_node_id = start_node['id']
            path = [current_node_id]
            total_length = 0

            visited = {node['id']: False for node in self.nodes}
            visited[current_node_id] = True

            for _ in range(len(self.nodes) - 1):
                available_edges = edges_from_node.get(current_node_id, [])
                valid_edges = [edge for edge in available_edges if not visited[edge['to']]]

                if not valid_edges:
                    break

                min_edge = min(valid_edges, key=lambda x: x['weight'])
                next_node_id = min_edge['to']
                path.append(next_node_id)
                total_length += min_edge['weight']
                visited[next_node_id] = True
                current_node_id = next_node_id

            return_edges = [edge for edge in edges_from_node.get(current_node_id, []) 
                        if edge['to'] == start_node['id']]

            if return_edges:
                total_length += return_edges[0]['weight']
                path.append(start_node['id'])

            return path, total_length

        start_time = time.time()

        if len(self.nodes) < 2:
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.time_display.delete(0, tk.END)
            self.time_display.insert(0, f"{elapsed_time:.4f}")
            return

        best_path = None
        best_length = float('inf')

        for start_node in self.nodes:
            path, length = run_nearest_neighbor(start_node)
            if length < best_length:
                best_path = path
                best_length = length

        self.display_path(best_path, best_length)
        self.draw_result_path(best_path)

        end_time = time.time()
        elapsed_time = end_time - start_time
        self.time_display.delete(0, tk.END)
        self.time_display.insert(0, f"{elapsed_time:.4f}")

    def display_path(self, path, length):

        self.path_display.delete(0, tk.END)
        self.path_display.insert(0, " -> ".join(map(str, path)))
        self.length_display.delete(0, tk.END)
        self.length_display.insert(0, str(length))

    def draw_result_path(self, path):

        self.result_canvas.delete("all")
        edge_ids = {(e['from'], e['to']): e for e in self.edges}

        for i in range(len(path)-1):
            from_id, to_id = path[i], path[i+1]
            if (from_id, to_id) in edge_ids:
                edge = edge_ids[(from_id, to_id)]
                from_node = next(n for n in self.nodes if n['id'] == from_id)
                to_node = next(n for n in self.nodes if n['id'] == to_id)
                x1, y1 = from_node['x'], from_node['y']
                x2, y2 = to_node['x'], to_node['y']
                self.result_canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill="green", width=2)

        for node in self.nodes:
            x, y = node['x'], node['y']
            self.result_canvas.create_oval(x-15, y-15, x+15, y+15, fill="blue")
            self.result_canvas.create_text(x, y, text=str(node['id']), fill="white")

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.geometry("1600x800")  
    root.mainloop()