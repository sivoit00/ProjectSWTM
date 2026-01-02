import { useEffect, useState } from "react";
import type { ProfileFormState, UseProfileFormReturn } from "../types";
import { loadProfileData } from "../services/loadProfile";
import { saveProfileData } from "../services/saveProfile";

const initialState: ProfileFormState = {
  customerId: undefined,
  username: "",
  email: "",
  firstName: "",
  lastName: "",
  postcode: "",
  city: "",
  phone: "",
  address: "",
  lawyerId: undefined,
  lawyerFirstName: "",
  lawyerLastName: "",
  lawyerCompany: "",
  lawyerEmail: "",
  lawyerPostcode: "",
  lawyerCity: "",
  lawyerPhone: "",
  lawyerAddress: "",
  workshopId: undefined,
  workshopName: "",
  workshopEmail: "",
  workshopPostcode: "",
  workshopCity: "",
  workshopPhone: "",
  workshopAddress: "",
  vehicleId: undefined,
  vehicleBrand: "",
  vehicleModel: "",
  vehicleYear: "",
  vehicleNumberplate: "",
  insuranceId: undefined,
  insuranceName: "",
  insuranceNumber: "",
  insuranceEmail: "",
  insurancePhone: "",
  insurancePostcode: "",
  insuranceCity: "",
  insuranceContact: "",
  insuranceAddress: "",
};

export function useProfileForm(): UseProfileFormReturn {
  const [form, setForm] = useState<ProfileFormState>(initialState);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProfileData(setForm).catch(err => {
      console.error("Error loading profile data", err);
      setError("Could not load your data. Please try again.");
    });
  }, []);

  const handleChange: UseProfileFormReturn["handleChange"] = e => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit: UseProfileFormReturn["handleSubmit"] = async e => {
    e.preventDefault();
    setSuccess(null);
    setError(null);

    try {
      await saveProfileData(form, setForm);
      setSuccess("Changes saved successfully!");
    } catch (err) {
      console.error("Error saving profile", err);
      setError("Could not save your data. Please try again.");
    }
  };

  return { form, handleChange, handleSubmit, success, error };
}
