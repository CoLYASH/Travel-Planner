from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import heapq

app = Flask(__name__)
CORS(app)

# Load datasets
flight_df = pd.read_csv("flight_final_with_states.csv")
train_df = pd.read_csv("train_after_with_states.csv")

# Function to construct the graph from datasets
def construct_graph(flight_df, train_df):
    graph = {}
    for _, row in flight_df.iterrows():
        src, dest, price = row['Src'], row['Dest'], row['Price']
        if src not in graph:
            graph[src] = []
        graph[src].append((price, dest, 'Flight', row['Agent'], row['TimetoTravel']))
    for _, row in train_df.iterrows():
        src, dest, price = row['source_station_name'], row['destination_station_name'], row['Base_Fare']
        if src not in graph:
            graph[src] = []
        graph[src].append((price, dest, 'Train', row['train_name'], row['timetotravel']))
    return graph

# Construct graph
graph = construct_graph(flight_df, train_df)

# Dijkstra’s algorithm to find the least-cost path
def find_least_cost_path(graph, source_city, destination_city):
    pq = [(0, source_city, [])]
    visited = set()
    while pq:
        cost, current_city, path = heapq.heappop(pq)
        if current_city in visited:
            continue
        visited.add(current_city)
        if current_city == destination_city:
            return cost, path
        for neighbor_cost, neighbor_city, transport_mode, name, travel_time in graph.get(current_city, []):
            if neighbor_city not in visited:
                heapq.heappush(pq, (cost + neighbor_cost, neighbor_city, path + [(neighbor_city, transport_mode, name, travel_time, neighbor_cost)]))
    return float('inf'), []

# API route for finding the least-cost trip
@app.route('/find_trip', methods=['POST'])
def find_trip():
    data = request.get_json()
    source = data.get('startPoint')
    destination = data.get('endPoint')
    cost, path = find_least_cost_path(graph, source, destination)
    result = {
        "cost": cost,
        "path": path
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)
