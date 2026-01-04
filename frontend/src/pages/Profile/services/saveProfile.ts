import { api } from "../../../services/api";
import type { ProfileFormState } from "../types";

type Updater = (updater: (prev: ProfileFormState) => ProfileFormState) => void;

async function saveCustomer(form: ProfileFormState, setForm: Updater) {
  const payload = {
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
    await api.customers.update(customerId, payload);
  } else {
    const res = await api.customers.create(payload);
    customerId = res.data.id!;
    setForm(prev => ({ ...prev, customerId }));
  }
}

function hasVehicleData(form: ProfileFormState) {
  return (
    form.vehicleBrand ||
    form.vehicleModel ||
    form.vehicleYear ||
    form.vehicleNumberplate
  );
}

async function saveVehicle(form: ProfileFormState, setForm: Updater) {
  if (!hasVehicleData(form)) return;

  const payload = {
    brand: form.vehicleBrand,
    model: form.vehicleModel,
    year: Number(form.vehicleYear) || 0,
    numberplate: form.vehicleNumberplate,
  };

  if (form.vehicleId) {
    await api.vehicles.update(form.vehicleId, payload);
  } else {
    const res = await api.vehicles.create(payload);
    setForm(prev => ({ ...prev, vehicleId: res.data.id }));
  }
}

function hasWorkshopData(form: ProfileFormState) {
  return (
    form.workshopName ||
    form.workshopEmail ||
    form.workshopPhone ||
    form.workshopPostcode ||
    form.workshopCity ||
    form.workshopAddress
  );
}

async function saveWorkshop(form: ProfileFormState, setForm: Updater) {
  if (!hasWorkshopData(form)) return;

  const payload = {
    name: form.workshopName,
    email: form.workshopEmail,
    phone: form.workshopPhone,
    postcode: form.workshopPostcode,
    city: form.workshopCity,
    address: form.workshopAddress,
  };

  if (form.workshopId) {
    await api.workshops.update(form.workshopId, payload);
  } else {
    const res = await api.workshops.create(payload);
    setForm(prev => ({ ...prev, workshopId: res.data.id }));
  }
}

function hasLawyerData(form: ProfileFormState) {
  return (
    form.lawyerFirstName ||
    form.lawyerLastName ||
    form.lawyerCompany ||
    form.lawyerEmail ||
    form.lawyerPhone ||
    form.lawyerPostcode ||
    form.lawyerCity ||
    form.lawyerAddress
  );
}

async function saveLawyer(form: ProfileFormState, setForm: Updater) {
  if (!hasLawyerData(form)) return;

  const payload = {
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
    await api.lawyers.update(form.lawyerId, payload);
  } else {
    const res = await api.lawyers.create(payload);
    setForm(prev => ({ ...prev, lawyerId: res.data.id }));
  }
}

function hasInsuranceData(form: ProfileFormState) {
  return (
    form.insuranceName ||
    form.insuranceNumber ||
    form.insuranceEmail ||
    form.insurancePhone ||
    form.insurancePostcode ||
    form.insuranceCity ||
    form.insuranceContact ||
    form.insuranceAddress
  );
}

async function saveInsurance(form: ProfileFormState, setForm: Updater) {
  if (!hasInsuranceData(form)) return;

  const payload = {
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
    await api.insurances.update(form.insuranceId, payload);
  } else {
    const res = await api.insurances.create(payload);
    setForm(prev => ({ ...prev, insuranceId: res.data.id }));
  }
}

export async function saveProfileData(
  form: ProfileFormState,
  setForm: Updater,
) {
  await saveCustomer(form, setForm);
  await Promise.all([
    saveVehicle(form, setForm),
    saveWorkshop(form, setForm),
    saveLawyer(form, setForm),
    saveInsurance(form, setForm),
  ]);
}
