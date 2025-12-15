import { useState, useEffect } from "react";
import { api } from "../../services/api";

export default function Profile() {
  const [form, setForm] = useState({
    // My Profile
    customerId: undefined as number | undefined,
    username: "",
    email: "",
    firstName: "",
    lastName: "",
    postcode: "",
    city: "",
    phone: "",
    address: "",
    // Lawyer
    lawyerId: undefined as number | undefined,
    lawyerFirstName: "",
    lawyerLastName: "",
    lawyerCompany: "",
    lawyerEmail: "",
    lawyerPostcode: "",
    lawyerCity: "",
    lawyerPhone: "",
    lawyerAddress: "",
    // Workshop
    workshopId: undefined as number | undefined,
    workshopName: "",
    workshopEmail: "",
    workshopPostcode: "",
    workshopCity: "",
    workshopPhone: "",
    workshopAddress: "",
    // Vehicle
    vehicleId: undefined as number | undefined,
    vehicleBrand: "",
    vehicleModel: "",
    vehicleYear: "",
    vehicleNumberplate: "",
    // Insurance
    insuranceId: undefined as number | undefined,
    insuranceName: "",
    insuranceNumber: "",
    insuranceEmail: "",
    insurancePhone: "",
    insurancePostcode: "",
    insuranceCity: "",
    insuranceContact: "",
    insuranceAddress: "",
  });

  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);


  // 1) Daten beim Laden holen
  useEffect(() => {
    const loadProfile = async () => {
      try {
        // 1) Customer
        const kundenRes = await api.customers.getAll();
        const firstCustomer = kundenRes.data[0];
        if (firstCustomer) {
          setForm(prev => ({
            ...prev,
            customerId: firstCustomer.id,
            firstName: firstCustomer.firstName ?? "",
            lastName: firstCustomer.lastName ?? "",
            username: firstCustomer.username ?? "",
            email: firstCustomer.email ?? "",
            phone: firstCustomer.phone ?? "",
            postcode: firstCustomer.postcode ?? "",
            city: firstCustomer.city ?? "",
            address: firstCustomer.address ?? "",
          }));
        }

        // 2) Vehicle
        const fahrzeugeRes = await api.vehicles.getAll();
        const firstVehicle = fahrzeugeRes.data[0];
        if (firstVehicle) {
          setForm(prev => ({
            ...prev,
            vehicleId: firstVehicle.id,
            vehicleBrand: firstVehicle.brand ?? "",
            vehicleModel: firstVehicle.model ?? "",
            vehicleYear: String(firstVehicle.year ?? "") ?? "",
            vehicleNumberplate: firstVehicle.numberplate ?? "",
          }));
        }

        // 3) Workshop
        const werkstattRes = await api.workshops.getAll();
        const firstWorkshop = werkstattRes.data[0];
        if (firstWorkshop) {
          setForm(prev => ({
            ...prev,
            workshopId: firstWorkshop.id,
            workshopName: firstWorkshop.name ?? "",
            workshopEmail: firstWorkshop.email ?? "",
            workshopPhone: firstWorkshop.phone ?? "",
            workshopPostcode: firstWorkshop.postcode ?? "",
            workshopCity: firstWorkshop.city ?? "",
            workshopAddress: firstWorkshop.address ?? "",
          }));
        }

        // 4) Lawyer
        const anwaltRes = await api.lawyers.getAll();
        const firstLawyer = anwaltRes.data[0];
        if (firstLawyer) {
          setForm(prev => ({
            ...prev,
            lawyerId: firstLawyer.id,
            lawyerFirstName: firstLawyer.firstName ?? "",
            lawyerLastName: firstLawyer.lastName ?? "",
            lawyerCompany: firstLawyer.company ?? "",
            lawyerEmail: firstLawyer.email ?? "",
            lawyerPhone: firstLawyer.phone ?? "",
            lawyerPostcode: firstLawyer.postcode ?? "",
            lawyerCity: firstLawyer.city ?? "",
            lawyerAddress: firstLawyer.address ?? "",
          }));
        }

        // 5) Insurance
        const versRes = await api.insurances.getAll();
        const firstInsurance = versRes.data[0];
        if (firstInsurance) {
          setForm(prev => ({
            ...prev,
            insuranceId: firstInsurance.id,
            insuranceName: firstInsurance.name ?? "",
            insuranceNumber: firstInsurance.number ?? "",
            insuranceEmail: firstInsurance.email ?? "",
            insurancePhone: firstInsurance.phone ?? "",
            insurancePostcode: firstInsurance.postcode ?? "",
            insuranceCity: firstInsurance.city ?? "",
            insuranceContact: firstInsurance.contact ?? "",
            insuranceAddress: firstInsurance.address ?? "",
          }));
        }
      } catch (err) {
        console.error("Error loading profile data", err);
      }
    };

    loadProfile();
  }, []);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    console.log("handleSubmit fired");

    try {
      // 1) Customer (My Profile)
      const customerPayload = {
        firstName: form.firstName,
        lastName: form.lastName,
        username: form.username,
        email: form.email,
        phone: form.phone,
        postcode: form.postcode,
        city: form.city,
        address: form.address,
      };

      let customerId = form.customerId;

      if (customerId) {
        await api.customers.update(customerId, customerPayload);
      } else {
        const customerRes = await api.customers.create(customerPayload);
        customerId = customerRes.data.id!;
        setForm(prev => ({ ...prev, customerId }));
      }

      // 2) Vehicle
      if (
        form.vehicleBrand ||
        form.vehicleModel ||
        form.vehicleYear ||
        form.vehicleNumberplate
      ) {
        const vehiclePayload = {
          brand: form.vehicleBrand,
          model: form.vehicleModel,
          year: Number(form.vehicleYear) || 0,
          numberplate: form.vehicleNumberplate,
        };

        if (form.vehicleId) {
          await api.vehicles.update(form.vehicleId, vehiclePayload);
        } else {
          const vRes = await api.vehicles.create(vehiclePayload);
          setForm(prev => ({ ...prev, vehicleId: vRes.data.id }));
        }
      }

      // 3) Workshop
      if (
        form.workshopName ||
        form.workshopEmail ||
        form.workshopPhone ||
        form.workshopPostcode ||
        form.workshopCity ||
        form.workshopAddress
      ) {
        const workshopPayload = {
          name: form.workshopName,
          email: form.workshopEmail,
          phone: form.workshopPhone,
          postcode: form.workshopPostcode,
          city: form.workshopCity,
          address: form.workshopAddress,
        };

        if (form.workshopId) {
          await api.workshops.update(form.workshopId, workshopPayload);
        } else {
          const wRes = await api.workshops.create(workshopPayload);
          setForm(prev => ({ ...prev, workshopId: wRes.data.id }));
        }
      }

      // 4) Lawyer
      if (
        form.lawyerFirstName ||
        form.lawyerLastName ||
        form.lawyerCompany ||
        form.lawyerEmail ||
        form.lawyerPhone ||
        form.lawyerPostcode ||
        form.lawyerCity ||
        form.lawyerAddress
      ) {
        const lawyerPayload = {
          firstName: form.lawyerFirstName,
          lastName: form.lawyerLastName,
          company: form.lawyerCompany,
          email: form.lawyerEmail,
          phone: form.lawyerPhone,
          postcode: form.lawyerPostcode,
          city: form.lawyerCity,
          address: form.lawyerAddress,
        };

        if (form.lawyerId) {
          await api.lawyers.update(form.lawyerId, lawyerPayload);
        } else {
          const lRes = await api.lawyers.create(lawyerPayload);
          setForm(prev => ({ ...prev, lawyerId: lRes.data.id }));
        }
      }

      // 5) Insurance
      if (
        form.insuranceName ||
        form.insuranceNumber ||
        form.insuranceEmail ||
        form.insurancePhone ||
        form.insurancePostcode ||
        form.insuranceCity ||
        form.insuranceContact ||
        form.insuranceAddress
      ) {
        const insurancePayload = {
          name: form.insuranceName,
          number: form.insuranceNumber,
          email: form.insuranceEmail,
          phone: form.insurancePhone,
          postcode: form.insurancePostcode,
          city: form.insuranceCity,
          contact: form.insuranceContact,
          address: form.insuranceAddress,
        };

        if (form.insuranceId) {
          await api.insurances.update(form.insuranceId, insurancePayload);
        } else {
          const iRes = await api.insurances.create(insurancePayload);
          setForm(prev => ({ ...prev, insuranceId: iRes.data.id }));
        }
      }

      console.log("Profile saved");
      setSuccess("Changes saved successfully!");
    } catch (error) {
      console.error("Error saving profile", error);
      setError("Could not save your data. Please try again.");
    }
  };

  return (
    <div className="flex flex-col items-center h-screen p-8 text-white overflow-y-auto">
      <div className="max-w-4xl w-full space-y-8">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold pt-2">
            My <span className="text-blue-400">Profile</span>
          </h1>
          <p className="text-gray-300">
            Manage your personal, vehicle and service information in one place.
          </p>
        </div>

        {success && (
          <div className="bg-green-900/40 border border-green-500/60 text-green-200 px-4 py-2 rounded">
            {success}
          </div>
        )}

        {error && (
          <div className="bg-red-900/40 border border-red-500/60 text-red-200 px-4 py-2 rounded">
            {error}
          </div>
        )}


        <form onSubmit={handleSubmit} className="space-y-8">
          {/* My Profile */}
          <section className="bg-blue-900/30 backdrop-blur-sm border border-blue-500/20 rounded-xl p-6 space-y-4">
            <h2 className="text-2xl font-semibold mb-2">My Profile</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-300 mb-1">
                  First name
                </label>
                <input
                  type="text"
                  name="firstName"
                  value={form.firstName}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">
                  Last name
                </label>
                <input
                  type="text"
                  name="lastName"
                  value={form.lastName}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Username
                </label>
                <input
                  type="text"
                  name="username"
                  value={form.username}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Phone
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={form.phone}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Address
                </label>
                <input
                  type="text"
                  name="address"
                  value={form.address}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">
                  Postcode
                </label>
                <input
                  type="text"
                  name="postcode"
                  value={form.postcode}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">
                  City
                </label>
                <input
                  type="text"
                  name="city"
                  value={form.city}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
            </div>
          </section>

          {/* Insurance */}
          <section className="bg-blue-900/30 backdrop-blur-sm border border-blue-500/20 rounded-xl p-6 space-y-4">
            <h2 className="text-2xl font-semibold mb-2">Insurance</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">Name</label>
                <input
                  type="text"
                  name="insuranceName"
                  value={form.insuranceName}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Insurance Number
                </label>
                <input
                  type="text"
                  name="insuranceNumber"
                  value={form.insuranceNumber}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Contact person
                </label>
                <input
                  type="text"
                  name="insuranceContact"
                  value={form.insuranceContact}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  name="insuranceEmail"
                  value={form.insuranceEmail}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Phone
                </label>
                <input
                  type="tel"
                  name="insurancePhone"
                  value={form.insurancePhone}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Address
                </label>
                <input
                  type="text"
                  name="insuranceAddress"
                  value={form.insuranceAddress}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">
                  Postcode
                </label>
                <input
                  type="text"
                  name="insurancePostcode"
                  value={form.insurancePostcode}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">
                  City
                </label>
                <input
                  type="text"
                  name="insuranceCity"
                  value={form.insuranceCity}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
            </div>
          </section>

          {/* Lawyer */}
          <section className="bg-blue-900/30 backdrop-blur-sm border border-blue-500/20 rounded-xl p-6 space-y-4">
            <h2 className="text-2xl font-semibold mb-2">Lawyer</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-300 mb-1">
                  First name
                </label>
                <input
                  type="text"
                  name="lawyerFirstName"
                  value={form.lawyerFirstName}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">
                  Last name
                </label>
                <input
                  type="text"
                  name="lawyerLastName"
                  value={form.lawyerLastName}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Company
                </label>
                <input
                  type="text"
                  name="lawyerCompany"
                  value={form.lawyerCompany}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  name="lawyerEmail"
                  value={form.lawyerEmail}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Phone
                </label>
                <input
                  type="tel"
                  name="lawyerPhone"
                  value={form.lawyerPhone}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Address
                </label>
                <input
                  type="text"
                  name="lawyerAddress"
                  value={form.lawyerAddress}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">
                  Postcode
                </label>
                <input
                  type="text"
                  name="lawyerPostcode"
                  value={form.lawyerPostcode}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">
                  City
                </label>
                <input
                  type="text"
                  name="lawyerCity"
                  value={form.lawyerCity}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
            </div>
          </section>

          {/* Workshop */}
          <section className="bg-blue-900/30 backdrop-blur-sm border border-blue-500/20 rounded-xl p-6 space-y-4">
            <h2 className="text-2xl font-semibold mb-2">Workshop</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">Name</label>
                <input
                  type="text"
                  name="workshopName"
                  value={form.workshopName}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  name="workshopEmail"
                  value={form.workshopEmail}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Phone
                </label>
                <input
                  type="tel"
                  name="workshopPhone"
                  value={form.workshopPhone}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Address
                </label>
                <input
                  type="text"
                  name="workshopAddress"
                  value={form.workshopAddress}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">
                  Postcode
                </label>
                <input
                  type="text"
                  name="workshopPostcode"
                  value={form.workshopPostcode}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">
                  City
                </label>
                <input
                  type="text"
                  name="workshopCity"
                  value={form.workshopCity}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
            </div>
          </section>

          {/* Vehicle */}
          <section className="bg-blue-900/30 backdrop-blur-sm border border-blue-500/20 rounded-xl p-6 space-y-4">
            <h2 className="text-2xl font-semibold mb-2">Vehicle</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">Brand</label>
                <input
                  type="text"
                  name="vehicleBrand"
                  value={form.vehicleBrand}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">Model</label>
                <input
                  type="text"
                  name="vehicleModel"
                  value={form.vehicleModel}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">Year</label>
                <input
                  type="text"
                  name="vehicleYear"
                  value={form.vehicleYear}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Number plate
                </label>
                <input
                  type="text"
                  name="vehicleNumberplate"
                  value={form.vehicleNumberplate}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
            </div>
          </section>

          {/* Save button */}
          <div className="flex justify-end">
            <button
              type="submit"
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold shadow-lg transition transform hover:scale-105"
            >
              Save changes
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
