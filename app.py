from flask import Flask, render_template, request
import osmnx as ox
import networkx as nx
import folium
from geopy.distance import geodesic
from shapely import wkt
import pandas as pd
import heapq

app = Flask(__name__)

# Load data from CSV files
hospital_file = 'pune_hospitals.csv'
highways_file = 'pune_highways.csv'

# Load hospital data and filter emergency hospitals
hospital_data = pd.read_csv(hospital_file)
hospital_data['geometry'] = hospital_data['geometry'].apply(wkt.loads)
emergency_hospitals = hospital_data[hospital_data['emergency'] == 'yes'].copy()

# Extract latitude and longitude from geometry
emergency_hospitals['lat'] = emergency_hospitals['geometry'].apply(lambda x: x.centroid.y if x.geom_type == 'Polygon' else x.y)
emergency_hospitals['lon'] = emergency_hospitals['geometry'].apply(lambda x: x.centroid.x if x.geom_type == 'Polygon' else x.x)

# Predefined locations in Pune
def get_user_locations():
    locations = {
         1: ('Shivajinagar', (18.5300, 73.8476)),
2: ('Hadapsar', (18.5089, 73.9259)),
3: ('Kothrud', (18.5074, 73.8077)),
4: ('Aundh', (18.5590, 73.8078)),
5: ('Viman Nagar', (18.5679, 73.9143)),
6: ('Baner', (18.5603, 73.7890)),
7: ('Wakad', (18.5971, 73.7707)),
8: ('Magarpatta', (18.5139, 73.9317)),
9: ('Pimpri', (18.6298, 73.7997)),
10: ('Chinchwad', (18.6446, 73.7639)),
11: ('Nigdi', (18.6510, 73.7629)),
12: ('Bhosari', (18.6193, 73.8440)),
13: ('Swargate', (18.5018, 73.8580)),
14: ('Deccan', (18.5167, 73.8417)),
15: ('Kalyani Nagar', (18.5524, 73.9020)),
16: ('Pimple Saudagar', (18.5970, 73.8069)),
17: ('Kharadi', (18.5512, 73.9357)),
18: ('Hinjewadi', (18.5907, 73.7408)),
19: ('Dhanori', (18.5940, 73.8857)),
20: ('Bavdhan', (18.5233, 73.7723)),
21: ('Warje', (18.4829, 73.8079)),
22: ('Balewadi', (18.5679, 73.7727)),
23: ('Pashan', (18.5403, 73.7961)),
24: ('Kondhwa', (18.4635, 73.8916)),
25: ('Camp', (18.5120, 73.8833)),
26: ('Erandwane', (18.5140, 73.8381)),
27: ('Bopodi', (18.5636, 73.8453)),
28: ('Karve Nagar', (18.4862, 73.8270)),
29: ('Narhe', (18.4473, 73.8103)),
30: ('Vadgaon Budruk', (18.4635, 73.8239)),
31: ('Parvati', (18.4892, 73.8580)),
32: ('Sinhagad Road', (18.4727, 73.8297)),
33: ('Dhayari', (18.4498, 73.8158)),
34: ('Wagholi', (18.5675, 74.0090)),
35: ('Undri', (18.4572, 73.9049)),
36: ('Lohegaon', (18.6191, 73.9120)),
37: ('Mundhwa', (18.5414, 73.9235)),
38: ('NIBM', (18.4724, 73.8945)),
39: ('Wanowrie', (18.4859, 73.8997)),
40: ('Kasarwadi', (18.6020, 73.8169)),
41: ('Thergaon', (18.6197, 73.7642)),
42: ('Pimple Gurav', (18.5933, 73.8324)),
43: ('Ravet', (18.6492, 73.7432)),
44: ('Talegaon Dabhade', (18.7355, 73.6755)),
45: ('Moshi', (18.6707, 73.8524)),
46: ('Charholi Budruk', (18.6395, 73.8742)),
47: ('Tathawade', (18.6148, 73.7428)),
48: ('Akurdi', (18.6407, 73.7727)),
49: ('Chakan', (18.7607, 73.8586)),
50: ('Wakadewadi', (18.5437, 73.8395)),
51: ('Bibwewadi', (18.4773, 73.8677)),
52: ('Fursungi', (18.5025, 73.9864)),
53: ('Manjari Budruk', (18.5056, 73.9679)),
54: ('Ghorpadi', (18.5213, 73.9023)),
55: ('Yerawada', (18.5606, 73.8897)),
56: ('Bavdhan Khurd', (18.5140, 73.7623)),
57: ('Gokhale Nagar', (18.5305, 73.8371)),
58: ('Model Colony', (18.5302, 73.8443)),
59: ('Prabhat Road', (18.5106, 73.8359)),
60: ('Law College Road', (18.5143, 73.8344)),
61: ('Sadashiv Peth', (18.5141, 73.8496)),
62: ('Navi Peth', (18.5177, 73.8494)),
63: ('Rasta Peth', (18.5214, 73.8667)),
64: ('Budhwar Peth', (18.5155, 73.8532)),
65: ('Somwar Peth', (18.5209, 73.8727)),
66: ('Bhavani Peth', (18.5147, 73.8760)),
67: ('Narayan Peth', (18.5173, 73.8482)),
68: ('Ganesh Peth', (18.5184, 73.8624)),
69: ('Mangalwar Peth', (18.5187, 73.8675)),
70: ('Guruwar Peth', (18.5141, 73.8543)),
71: ('Salisbury Park', (18.4999, 73.8753)),
72: ('Pune Station', (18.5289, 73.8744)),
73: ('Shaniwar Peth', (18.5167, 73.8466)),
74: ('Kasba Peth', (18.5186, 73.8507)),
75: ('Katraj', (18.4456, 73.8662)),
76: ('Ambegaon Pathar', (18.4498, 73.8612)),
77: ('Narhegaon', (18.4493, 73.8097)),
78: ('Vadgaon Sheri', (18.5533, 73.9085)),
79: ('Bhugaon', (18.5046, 73.7464)),
80: ('Ambegaon BK', (18.4487, 73.8619)),
81: ('Balaji Nagar', (18.4782, 73.8614)),
82: ('Santosh Nagar', (18.4827, 73.8604)),
83: ('Saswad', (18.3484, 74.0274)),
84: ('Khed Shivapur', (18.4200, 73.8382)),
85: ('Shivane', (18.4934, 73.7861)),
86: ('Pune Cantonment', (18.5159, 73.8923)),
87: ('Vishrantwadi', (18.5836, 73.8803)),
88: ('Tadiwala Road', (18.5285, 73.8790)),
89: ('Chandan Nagar', (18.5640, 73.9190)),
90: ('Dighi', (18.6101, 73.8744)),
91: ('Talawade', (18.6630, 73.7745)),
92: ('Moshi Pradhikaran', (18.6627, 73.8611)),
93: ('Manik Baug', (18.4842, 73.8200)),
94: ('Chinchwad Gaon', (18.6347, 73.7915)),
95: ('Sus Gaon', (18.5547, 73.7525)),
96: ('Bhavdhan Budruk', (18.5235, 73.7802)),
97: ('Mulshi', (18.5276, 73.5506)),
98: ('Pirangut', (18.5310, 73.6750)),
99: ('Shivapur', (18.4186, 73.8347)),
100: ('Jambhulwadi', (18.4264, 73.8287)),
101: ('Kirkatwadi', (18.4492, 73.7890))

        
    }
    return locations

# Define heuristic function using geodesic distance
def heuristic(node, goal):
    return geodesic((node[1], node[0]), (goal[1], goal[0])).meters

# A* algorithm using road network
def a_star(graph, start_node, goal_node):
    pq = []  # Priority queue
    heapq.heappush(pq, (0, start_node))  # (cost, node)
    came_from = {start_node: None}
    cost_so_far = {start_node: 0}
    
    while pq:
        current_cost, current_node = heapq.heappop(pq)
        
        if current_node == goal_node:
            break
        
        for neighbor in graph.neighbors(current_node):
            road_length = graph.edges[current_node, neighbor, 0]['length']
            new_cost = cost_so_far[current_node] + road_length
            
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic((graph.nodes[neighbor]['x'], graph.nodes[neighbor]['y']), 
                                                (graph.nodes[goal_node]['x'], graph.nodes[goal_node]['y']))
                heapq.heappush(pq, (priority, neighbor))
                came_from[neighbor] = current_node
                
    # Reconstruct path
    path = []
    current = goal_node
    while current != start_node:
        path.append(current)
        current = came_from[current]
    path.append(start_node)
    path.reverse()
    
    return path

@app.route('/')
def index():
    locations = get_user_locations()
    return render_template('index.html', locations=locations)

@app.route('/get_path', methods=['POST'])
def get_path():
    selected_location_key = int(request.form['location'])
    locations = get_user_locations()
    selected_location = locations[selected_location_key][1]

    # Fetch the road network for driving in Pune
    place_name = "Pune, India"
    graph = ox.graph_from_place(place_name, network_type='drive')

    # Find the nearest emergency hospital using geodesic distance
    emergency_hospitals['distance'] = emergency_hospitals.apply(
        lambda row: geodesic(selected_location, (row['lat'], row['lon'])).meters, axis=1
    )
    nearest_hospital = emergency_hospitals.loc[emergency_hospitals['distance'].idxmin()]
    nearest_hospital_location = (nearest_hospital['lat'], nearest_hospital['lon'])
    distance_to_hospital = nearest_hospital['distance']

    # Get the nearest nodes from the graph for both start and hospital
    start_node = ox.distance.nearest_nodes(graph, selected_location[1], selected_location[0])
    goal_node = ox.distance.nearest_nodes(graph, nearest_hospital_location[1], nearest_hospital_location[0])

    # Run A* algorithm to find the shortest path
    shortest_path = a_star(graph, start_node, goal_node)

    # Create a map
    map_pune = folium.Map(location=[selected_location[0], selected_location[1]], zoom_start=12)

    # Plot hospitals
    for _, hospital in emergency_hospitals.iterrows():
        folium.Marker([hospital['lat'], hospital['lon']],
                      popup=hospital['name'], 
                      icon=folium.Icon(color='red', icon='info-sign')).add_to(map_pune)

    # Plot the shortest path on the map
    route_coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in shortest_path]
    folium.PolyLine(route_coords, color='blue', weight=5, opacity=0.8).add_to(map_pune)

    # Convert the map to HTML
    map_html = map_pune._repr_html_()

    return render_template('index.html', 
                           locations=locations, 
                           map_html=map_html, 
                           distance=distance_to_hospital,
                           hospital_name=nearest_hospital['name'])

if __name__ == "__main__":
    app.run(debug=True)
