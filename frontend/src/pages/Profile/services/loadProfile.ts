import { api } from "../../../services/api";
import type { ProfileFormState } from "../types";

type Updater = (updater: (prev: ProfileFormState) => ProfileFormState) => void;

async function loadCustomer(setForm: Updater) {
  const kundenRes = await api.customers.getAll();
  const firstCustomer = kundenRes.data[0];
  if (!firstCustomer) return;

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

async function loadVehicle(setForm: Updater) {
  const fahrzeugeRes = await api.vehicles.getAll();
  const firstVehicle = fahrzeugeRes.data[0];
  if (!firstVehicle) return;

  setForm(prev => ({
    ...prev,
    vehicleId: firstVehicle.id,
    vehicleBrand: firstVehicle.brand ?? "",
    vehicleModel: firstVehicle.model ?? "",
    vehicleYear: String(firstVehicle.year ?? ""),
    vehicleNumberplate: firstVehicle.numberplate ?? "",
  }));
}

async function loadWorkshop(setForm: Updater) {
  const werkstattRes = await api.workshops.getAll();
  const firstWorkshop = werkstattRes.data[0];
  if (!firstWorkshop) return;

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

async function loadLawyer(setForm: Updater) {
  const anwaltRes = await api.lawyers.getAll();
  const firstLawyer = anwaltRes.data[0];
  if (!firstLawyer) return;

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

async function loadInsurance(setForm: Updater) {
  const versRes = await api.insurances.getAll();
  const firstInsurance = versRes.data[0];
  if (!firstInsurance) return;

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

export async function loadProfileData(setForm: Updater) {
  // parallele Requests -> weniger Wartezeit, einfachere Kontrolle
  await Promise.all([
    loadCustomer(setForm),
    loadVehicle(setForm),
    loadWorkshop(setForm),
    loadLawyer(setForm),
    loadInsurance(setForm),
  ]);
}
