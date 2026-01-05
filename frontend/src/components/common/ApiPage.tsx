import { useState, useEffect } from "react";
import { api } from "../../services/api";
import type { Customer, Vehicle, Workshop } from "../../services/api";

export default function ApiPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [workshops, setWorkshops] = useState<Workshop[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [text, setText] = useState("");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [customersRes, vehiclesRes, workshopsRes] = await Promise.all([
        api.customers.getAll(),
        api.vehicles.getAll(),
        api.workshops.getAll(),
      ]);
      setCustomers(customersRes.data);
      setVehicles(vehiclesRes.data);
      setWorkshops(workshopsRes.data);
    } catch (error) {
      console.error("Error loading data:", error);
    }
  };

  return (
    <div>
      <h1>Vehicle Service</h1>

      <h2>Customers</h2>
      <ul>
        {customers.map((customer) => (
          <li key={customer.id}>
            {(customer.firstName || "").trim()} {(customer.lastName || "").trim()} - {customer.email}
          </li>
        ))}
      </ul>

      <h2>Vehicles</h2>
      <ul>
        {vehicles.map((vehicle) => (
          <li key={vehicle.id}>
            {vehicle.brand} {vehicle.model} ({vehicle.year})
          </li>
        ))}
      </ul>
      <h2>Workshops</h2>
      <ul>
        {workshops.map((w) => (
          <li key={w.id}>
            {w.name} {w.address} {w.postcode} {w.city}
          </li>
        ))}
      </ul>

      <div className="text">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type something..."
        />
        <p>You typed: {text}</p>
      </div>
    </div>
  );
}
