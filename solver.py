# Di dalam fungsi def solve_gvrp(data):
# ... (Kode inisialisasi model dari OR-Tools tetap sama hingga masuk ke dalam loop ekstraksi rute) ...

    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)

        route_distance = 0
        route_load = 0
        
        # 1. Lakukan pre-looping untuk mendapatkan total beban awal (sebelum berangkat dari depot)
        temp_index = index
        while not routing.IsEnd(temp_index):
            node_idx = manager.IndexToNode(temp_index)
            route_load += int(data["demands"][node_idx])
            temp_index = solution.Value(routing.NextVar(temp_index))

        current_vehicle_load = route_load  # Beban maksimal saat berangkat
        max_capacity = data["vehicle_capacities"][vehicle_id]
        route_co2_emission = 0.0 # Akumulasi emisi rute ini

        route_nodes = []
        route_schedule = []
        route_node_indices = []
        temporary_stop_results = []

        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            arrival_time = solution.Min(time_dimension.CumulVar(index))
            
            # Kurangi beban kendaraan saat barang diturunkan di titik ini
            demand_at_node = int(data["demands"][node_index])
            current_vehicle_load -= demand_at_node 

            route_nodes.append(data["address_list"][node_index])
            route_node_indices.append(node_index)

            absolute_arrival = arrival_time + depot_start
            absolute_deadline = data["time_windows"][node_index][1]

            route_schedule.append({
                "Location": data["address_list"][node_index],
                "Time": f"{absolute_arrival // 60:02d}:{absolute_arrival % 60:02d}",
                "Demand": demand_at_node,
                "Current Load": current_vehicle_load, # Menyimpan histori beban
                "Latitude": data["raw_coords"][node_index][0],
                "Longitude": data["raw_coords"][node_index][1],
                "Stop Type": "Depot" if node_index == depot else "Delivery"
            })

            # ... (Simpan status keterlambatan jika perlu, seperti kode sebelumnya) ...

            previous_index = index
            index = solution.Value(routing.NextVar(index))

            # 2. Kalkulasi Emisi Dinamis per Segmen Jalan
            segment_distance_m = routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            segment_distance_km = segment_distance_m / 1000.0
            route_distance += segment_distance_m
            
            # Aplikasi Model Matematika GVRP untuk emisi
            load_ratio = current_vehicle_load / max_capacity if max_capacity > 0 else 0
            emission_rate = data["emission_empty"] + (load_ratio * (data["emission_full"] - data["emission_empty"]))
            segment_emission = segment_distance_km * emission_rate
            
            route_co2_emission += segment_emission

        # ... (Kode penanganan end_node dan depot kembali tetap sama) ...

        if route_load > 0:
            active_vehicles += 1
            display_vehicle_id += 1
            total_distance += route_distance
            
            distance_km = route_distance / 1000
            fuel_cost = distance_km * data["fuel_cost_per_km"]
            total_cost = fuel_cost + data["driver_cost_per_vehicle"]
            
            route_results.append({
                "Vehicle": display_vehicle_id,
                "Distance (km)": round(distance_km, 2),
                "Delivered Packages": route_load,
                "Utilization (%)": round(route_load / max_capacity * 100, 2),
                "Total Cost": round(total_cost, 2),
                "CO2 Emissions (kg)": round(route_co2_emission, 3), # Menggunakan hasil kalkulasi dinamis
                "Schedule": route_schedule,
                "Coordinates": [data["raw_coords"][i] for i in route_node_indices]
            })
            
    # Return hasil