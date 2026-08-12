# --- DI BAGIAN: Sidebar inputs (Global parameters) ---
st.sidebar.header("🚚 Fleet & Emission Parameters")
fuel_cost_per_km = st.sidebar.number_input("Fuel Cost per KM (Rp)", 0, 50000, 1500)
driver_cost_per_vehicle = st.sidebar.number_input("Driver Cost per Vehicle (Rp)", 0, 500000, 100000)
num_vehicles = st.sidebar.number_input("Number of Vehicles", 1, 15, 2)
vehicle_capacity = st.sidebar.number_input("Vehicle Capacity (kg/units)", 1, 50000, 100)

st.sidebar.header("🌱 GVRP Emission Factors")
# Parameter emisi dinamis berdasarkan berat
emission_empty = st.sidebar.number_input("Empty Vehicle Emission (kg CO2/km)", 0.0, 5.0, 0.15, step=0.01)
emission_full = st.sidebar.number_input("Full Vehicle Emission (kg CO2/km)", 0.0, 5.0, 0.30, step=0.01)

# --- DI BAGIAN: Run solver ---
    # Tambahkan parameter emisi dinamis ke dictionary data
    data = {
        # ... (parameter sebelumnya tetap sama) ...
        "time_windows": [loc["time_window"] for loc in sorted_locations], 
        "service_times": [0 if idx == 0 else 5 for idx in range(len(sorted_locations))], 
        "fuel_cost_per_km": fuel_cost_per_km,
        "driver_cost_per_vehicle": driver_cost_per_vehicle,
        "emission_empty": emission_empty,  # Tambahan baru
        "emission_full": emission_full     # Tambahan baru
    }

# --- DI BAGIAN: Display results ---
    # Perbaikan perhitungan Baseline CO2 (Asumsi baseline menggunakan rata-rata emisi atau emisi penuh)
    avg_emission = (data["emission_empty"] + data["emission_full"]) / 2
    baseline_emissions = baseline_distance * avg_emission
    
    # Ambil total emisi hasil optimasi dinamis dari solver
    optimized_emissions = sum(r.get("CO2 Emissions (kg)", 0) for r in routes)
    emission_reduction = baseline_emissions - optimized_emissions