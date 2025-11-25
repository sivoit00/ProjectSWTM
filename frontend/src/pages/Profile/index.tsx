import { useState } from "react";
import { api } from "../../services/api";

export default function Profile() {
  const [form, setForm] = useState({
    // My Profile
    username: "",
    email: "",
    firstName: "",
    lastName: "",
    postcode: "",
    city: "",
    phone: "",
    // Lawyer
    lawyerFirstName: "",
    lawyerLastName: "",
    lawyerCompany: "",
    lawyerEmail: "",
    lawyerPostcode: "",
    lawyerCity: "",
    lawyerPhone: "",
    // Workshop
    workshopName: "",
    workshopEmail: "",
    workshopPostcode: "",
    workshopCity: "",
    workshopPhone: "",
    // Vehicle
    vehicleBrand: "",
    vehicleModel: "",
    vehicleYear: "",
    vehicleNumberPlate: "",
    // Insurance
    insuranceName: "",
    insuranceNumber: "",
    insuranceEmail: "",
    insurancePhone: "",
    insurancePostcode: "",
    insuranceCity: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

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
      };

      const customerRes = await api.customers.create(customerPayload);
      const customerId = customerRes.data.id!;

      // 2) Vehicle
      if (
        form.vehicleBrand ||
        form.vehicleModel ||
        form.vehicleYear ||
        form.vehicleNumberPlate
      ) {
        const vehiclePayload = {
          brand: form.vehicleBrand,
          model: form.vehicleModel,
          year: Number(form.vehicleYear) || 0,
          numberPlate: form.vehicleNumberPlate,
          customerId,
        };
        await api.vehicles.create(vehiclePayload);
      }

      // 3) Workshop
      if (
        form.workshopName ||
        form.workshopEmail ||
        form.workshopPhone ||
        form.workshopPostcode ||
        form.workshopCity
      ) {
        const workshopPayload = {
          name: form.workshopName,
          email: form.workshopEmail,
          phone: form.workshopPhone,
          postcode: form.workshopPostcode,
          city: form.workshopCity,
        };
        await api.workshops.create(workshopPayload);
      }

      // 4) Lawyer
      if (
        form.lawyerFirstName ||
        form.lawyerLastName ||
        form.lawyerCompany ||
        form.lawyerEmail ||
        form.lawyerPhone ||
        form.lawyerPostcode ||
        form.lawyerCity
      ) {
        const lawyerPayload = {
          firstName: form.lawyerFirstName,
          lastName: form.lawyerLastName,
          company: form.lawyerCompany,
          email: form.lawyerEmail,
          phone: form.lawyerPhone,
          postcode: form.lawyerPostcode,
          city: form.lawyerCity,
        };
        await api.lawyers.create(lawyerPayload);
      }

      // 5) Insurance
      if (
        form.insuranceName ||
        form.insuranceEmail ||
        form.insurancePhone ||
        form.insurancePostcode ||
        form.insuranceCity
      ) {
        const insurancePayload = {
          name: form.insuranceName,
          email: form.insuranceEmail,
          phone: form.insurancePhone,
          postcode: form.insurancePostcode,
          city: form.insuranceCity,
        };
        await api.insurances.create(insurancePayload);
      }

      console.log("Profile saved");
    } catch (error) {
      console.error("Error saving profile", error);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen p-8 text-white overflow-y-auto">
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

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* My Profile */}
          <section className="bg-blue-900/30 backdrop-blur-sm border border-blue-500/20 rounded-xl p-6 space-y-4">
            <h2 className="text-2xl font-semibold mb-2">My Profile</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
                <label className="block text-sm text-gray-300 mb-1">First name</label>
                <input
                  type="text"
                  name="firstName"
                  value={form.firstName}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">Last name</label>
                <input
                  type="text"
                  name="lastName"
                  value={form.lastName}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">Username</label>
                <input
                  type="text"
                  name="username"
                  value={form.username}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">Email</label>
                <input
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">Phone</label>
                <input
                  type="tel"
                  name="phone"
                  value={form.phone}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">Postcode</label>
                <input
                  type="text"
                  name="postcode"
                  value={form.postcode}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">City</label>
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
                <label className="block text-sm text-gray-300 mb-1">Insurance Number</label>
                <input
                  type="text"
                  name="insuranceNumber"
                  value={form.insuranceNumber}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">Email</label>
                <input
                  type="email"
                  name="insuranceEmail"
                  value={form.insuranceEmail}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">Phone</label>
                <input
                  type="tel"
                  name="insurancePhone"
                  value={form.insurancePhone}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">Postcode</label>
                <input
                  type="text"
                  name="insurancePostcode"
                  value={form.insurancePostcode}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">City</label>
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
                <label className="block text-sm text-gray-300 mb-1">First name</label>
                <input
                  type="text"
                  name="lawyerFirstName"
                  value={form.lawyerFirstName}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">Last name</label>
                <input
                  type="text"
                  name="lawyerLastName"
                  value={form.lawyerLastName}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">Company</label>
                <input
                  type="text"
                  name="lawyerCompany"
                  value={form.lawyerCompany}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">Email</label>
                <input
                  type="email"
                  name="lawyerEmail"
                  value={form.lawyerEmail}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">Phone</label>
                <input
                  type="tel"
                  name="lawyerPhone"
                  value={form.lawyerPhone}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">Postcode</label>
                <input
                  type="text"
                  name="lawyerPostcode"
                  value={form.lawyerPostcode}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">City</label>
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
                <label className="block text-sm text-gray-300 mb-1">Email</label>
                <input
                  type="email"
                  name="workshopEmail"
                  value={form.workshopEmail}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">Phone</label>
                <input
                  type="tel"
                  name="workshopPhone"
                  value={form.workshopPhone}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">Postcode</label>
                <input
                  type="text"
                  name="workshopPostcode"
                  value={form.workshopPostcode}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">City</label>
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
                <label className="block text-sm text-gray-300 mb-1">Number plate</label>
                <input
                  type="text"
                  name="vehicleNumberPlate"
                  value={form.vehicleNumberPlate}
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
