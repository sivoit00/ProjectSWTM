export interface ProfileFormState {
  // My Profile
  customerId: number | undefined;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  postcode: string;
  city: string;
  phone: string;
  address: string;

  // Lawyer
  lawyerId: number | undefined;
  lawyerFirstName: string;
  lawyerLastName: string;
  lawyerCompany: string;
  lawyerEmail: string;
  lawyerPostcode: string;
  lawyerCity: string;
  lawyerPhone: string;
  lawyerAddress: string;

  // Workshop
  workshopId: number | undefined;
  workshopName: string;
  workshopEmail: string;
  workshopPostcode: string;
  workshopCity: string;
  workshopPhone: string;
  workshopAddress: string;

  // Vehicle
  vehicleId: number | undefined;
  vehicleBrand: string;
  vehicleModel: string;
  vehicleYear: string;
  vehicleNumberplate: string;

  // Insurance
  insuranceId: number | undefined;
  insuranceName: string;
  insuranceNumber: string;
  insuranceEmail: string;
  insurancePhone: string;
  insurancePostcode: string;
  insuranceCity: string;
  insuranceContact: string;
  insuranceAddress: string;
}

export interface UseProfileFormReturn {
  form: ProfileFormState;
  handleChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => void;
  handleSubmit: (e: React.FormEvent) => Promise<void>;
  success: string | null;
  error: string | null;
}
