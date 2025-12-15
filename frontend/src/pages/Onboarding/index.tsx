import React, { useState } from "react";
import { useNavigate } from "react-router-dom"
import { api } from "../../services/api";

type Step = 1 | 2 | 3 | 4 | 5;

export default function Onboarding() {
  const [step, setStep] = useState<Step>(1);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const [form, setForm] = useState({
    // My Profile
    username: "",
    email: "",
    firstName: "",
    lastName: "",
    postcode: "",
    city: "",
    phone: "",
    address: "",
    // Insurance
    insuranceName: "",
    insuranceNumber: "",
    insuranceEmail: "",
    insurancePhone: "",
    insurancePostcode: "",
    insuranceCity: "",
    insuranceContact: "",
    insuranceAddress: "",
    // Lawyer
    lawyerFirstName: "",
    lawyerLastName: "",
    lawyerCompany: "",
    lawyerEmail: "",
    lawyerPostcode: "",
    lawyerCity: "",
    lawyerPhone: "",
    lawyerAddress: "",
    // Workshop
    workshopName: "",
    workshopEmail: "",
    workshopPostcode: "",
    workshopCity: "",
    workshopPhone: "",
    workshopAddress: "",
    // Vehicle
    vehicleBrand: "",
    vehicleModel: "",
    vehicleYear: "",
    vehicleNumberplate: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const next = () => setStep(s => (s < 5 ? ((s + 1) as Step) : s));
  const back = () => setStep(s => (s > 1 ? ((s - 1) as Step) : s));

  const handleFinish = async () => {
    setIsSaving(true);
    setError(null);
    try {
      // 1) Customer (My Profile)
      const customerRes = await api.customers.create({
        firstName: form.firstName,
        lastName: form.lastName,
        username: form.username,
        email: form.email,
        phone: form.phone,
        postcode: form.postcode,
        city: form.city,
        address: form.address,
      });
      const customerId = customerRes.data.id as number;

      // 2) Vehicle
      if (
        form.vehicleBrand ||
        form.vehicleModel ||
        form.vehicleYear ||
        form.vehicleNumberplate
      ) {
        await api.vehicles.create({
          brand: form.vehicleBrand,
          model: form.vehicleModel,
          year: Number(form.vehicleYear) || 0,
          numberplate: form.vehicleNumberplate,
        });

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
        await api.workshops.create({
          name: form.workshopName,
          email: form.workshopEmail,
          phone: form.workshopPhone,
          postcode: form.workshopPostcode,
          city: form.workshopCity,
          address: form.workshopAddress,
        });
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
        await api.lawyers.create({
          firstName: form.lawyerFirstName,
          lastName: form.lawyerLastName,
          company: form.lawyerCompany,
          email: form.lawyerEmail,
          phone: form.lawyerPhone,
          postcode: form.lawyerPostcode,
          city: form.lawyerCity,
          address: form.lawyerAddress,
        });
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
        await api.insurances.create({
          name: form.insuranceName,
          number: form.insuranceNumber,
          email: form.insuranceEmail,
          phone: form.insurancePhone,
          postcode: form.insurancePostcode,
          city: form.insuranceCity,
          contact: form.insuranceContact,
          address: form.insuranceAddress,
        });
      }

      navigate("/");
    } catch (e) {
      console.error(e);
      setError("Could not save your data. Please try again.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="flex flex-col items-center p-8 text-white min-h-screen">
      <div className="max-w-3xl w-full space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold">Welcome to MyClone</h1>
          <p className="text-gray-300">
            Let’s set up your account in a few quick steps. This can also be done later in your profile!
          </p>
        </div>

        {/* Step indicators */}
        <div className="flex justify-center gap-4">
          {[1, 2, 3, 4, 5].map(s => (
            <div
              key={s}
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                step === s
                  ? "bg-blue-600"
                  : "bg-blue-900 border border-blue-500/40"
              }`}
            >
              {s}
            </div>
          ))}
        </div>

        {error && (
          <div className="bg-red-900/40 border border-red-500/60 text-red-200 px-4 py-2 rounded">
            {error}
          </div>
        )}

        {/* Step 1: My Profile */}
        {step === 1 && (
          <section className="bg-blue-900/30 border border-blue-500/20 rounded-xl p-6 space-y-4">
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
        )}

        {/* Step 2: Insurance */}
        {step === 2 && (
          <section className="bg-blue-900/30 border border-blue-500/20 rounded-xl p-6 space-y-4">
            <h2 className="text-2xl font-semibold mb-2">Insurance</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Name
                </label>
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
        )}

        {/* Step 3: Lawyer */}
        {step === 3 && (
          <section className="bg-blue-900/30 border border-blue-500/20 rounded-xl p-6 space-y-4">
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
        )}

        {/* Step 4: Workshop */}
        {step === 4 && (
          <section className="bg-blue-900/30 border border-blue-500/20 rounded-xl p-6 space-y-4">
            <h2 className="text-2xl font-semibold mb-2">Workshop</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Name
                </label>
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
        )}

        {/* Step 5: Vehicle */}
        {step === 5 && (
          <section className="bg-blue-900/30 border border-blue-500/20 rounded-xl p-6 space-y-4">
            <h2 className="text-2xl font-semibold mb-2">Vehicle</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Brand
                </label>
                <input
                  type="text"
                  name="vehicleBrand"
                  value={form.vehicleBrand}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Model
                </label>
                <input
                  type="text"
                  name="vehicleModel"
                  value={form.vehicleModel}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">
                  Year
                </label>
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
        )}

        {/* Navigation buttons */}
        <div className="flex justify-between mt-4">
          <button
            type="button"
            disabled={step === 1}
            onClick={back}
            className="px-4 py-2 rounded-lg border border-blue-500/50 disabled:opacity-50"
          >
            Back
          </button>
          {step < 5 ? (
            <button
              type="button"
              onClick={next}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold"
            >
              Next
            </button>
          ) : (
            <button
              type="button"
              onClick={handleFinish}
              disabled={isSaving}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold disabled:opacity-50"
            >
              {isSaving ? "Saving..." : "Finish setup"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
