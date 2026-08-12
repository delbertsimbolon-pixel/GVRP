# --- DI BAGIAN: Sidebar inputs (Global parameters) ---
st.sidebar.header("⚙️ Operational Scenarios")
scenario = st.sidebar.selectbox("Select Scenario", ["Normal distribution day", "Peak distribution day", "Delayed departure"])

st.sidebar.header("🚚 Fleet & Emission Parameters")
fuel_cost_per_km = st.sidebar.number_input("Fuel Cost per KM (Rp)", 0, 50000, 1500)
driver_cost_per_vehicle = st.sidebar.number_input("Driver Cost per Vehicle (Rp)", 0, 500000, 100000)
num_vehicles = st.sidebar.number_input("Number of Vehicles", 1, 15, 2)
vehicle_capacity = st.sidebar.number_input("Vehicle Capacity (kg)", 1, 50000, 100)

st.sidebar.header("🌱 GVRP Emission Factors")
# Parameter emisi dinamis berdasarkan berat kendaraan
emission_empty = st.sidebar.number_input("Empty Vehicle Emission (kg CO2/km)", 0.0, 5.0, 0.15, step=0.01)
emission_full = st.sidebar.number_input("Full Vehicle Emission (kg CO2/km)", 0.0, 5.0, 0.30, step=0.01)

# ... (Biarkan bagian Input Data Manual / Excel tetap seperti aslinya) ...

# -------------------------------
# Run solver
# -------------------------------
if st.button("🚀 Run Route Optimization"):
    if not user_locations:
        st.error("Validation Error: No location configurations found. Please setup manual forms or upload your template data.")
        st.stop()
        
    if not depot_indices:
        st.error("Validation Error: Please configure at least one location type as 'depot'.")
        st.stop()

    primary_depot_idx = depot_indices[0]
    sorted_locations = [user_locations[primary_depot_idx]] + [
        loc for idx, loc in enumerate(user_locations) if idx != primary_depot_idx
    ]

    multiplier = 1.0
    if scenario == "Peak distribution day":
        multiplier = 1.25

    final_demands = [math.ceil(loc["demand"] * multiplier) if idx != 0 else 0 for idx, loc in enumerate(sorted_locations)]

    # PASTIKAN POSISI 'data' SEJAJAR (4 spasi dari kiri) SEPERTI INI:
    data = {
        "address_list": [loc["name"] for loc in sorted_locations],
        "raw_coords": [loc["coords"] for loc in sorted_locations],
        "demands": final_demands,
        "vehicle_capacities": [vehicle_capacity] * num_vehicles,
        "num_vehicles": num_vehicles,
        "depot": 0,
        "depot_start": 0,              
        "time_windows": [loc["time_window"] for loc in sorted_locations], 
        "service_times": [0 if idx == 0 else 5 for idx in range(len(sorted_locations))], 
        "fuel_cost_per_km": fuel_cost_per_km,
        "driver_cost_per_vehicle": driver_cost_per_vehicle,
        "emission_empty": emission_empty,
        "emission_full": emission_full
    }

    if any(lat == 0.0 or lon == 0.0 for lat, lon in data["raw_coords"]):
        st.error("Validation Error: Ensure all mapped coordinates are valid (cannot be 0.0/0.0).")
        st.stop()

    with st.spinner("Fetching matrix configurations and solving..."):
        try:
            data = get_osrm_matrices(data)
            # Pastikan nama fungsi di bawah ini sesuai dengan yang kamu buat di solver.py
            result = solve_gvrp(data) 
        except Exception as e:
            st.error(f"Mapping error from OSRM engine: {e}")
            st.stop()
