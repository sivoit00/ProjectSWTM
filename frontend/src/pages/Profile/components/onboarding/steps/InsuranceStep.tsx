import type { ProfileFormState } from "../../../types";

type Props = {
  form: ProfileFormState;
  onChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => void;
};

export function InsuranceStep({ form, onChange }: Props) {
  return (
    <section className="space-y-4">
      <h3 className="text-xl font-semibold">Insurance</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="md:col-span-2">
          <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
            Name
          </label>
          <input
            type="text"
            name="insuranceName"
            value={form.insuranceName}
            onChange={onChange}
            className="w-full px-3 py-2 rounded-lg bg-white border border-gray-200 text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-indigo-500 dark:bg-gray-900 dark:border-gray-800 dark:text-gray-100"
          />
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
            Number
          </label>
          <input
            type="text"
            name="insuranceNumber"
            value={form.insuranceNumber}
            onChange={onChange}
            className="w-full px-3 py-2 rounded-lg bg-white border border-gray-200 text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-indigo-500 dark:bg-gray-900 dark:border-gray-800 dark:text-gray-100"
          />
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
            Contact
          </label>
          <input
            type="text"
            name="insuranceContact"
            value={form.insuranceContact}
            onChange={onChange}
            className="w-full px-3 py-2 rounded-lg bg-white border border-gray-200 text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-indigo-500 dark:bg-gray-900 dark:border-gray-800 dark:text-gray-100"
          />
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
            Email
          </label>
          <input
            type="email"
            name="insuranceEmail"
            value={form.insuranceEmail}
            onChange={onChange}
            className="w-full px-3 py-2 rounded-lg bg-white border border-gray-200 text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-indigo-500 dark:bg-gray-900 dark:border-gray-800 dark:text-gray-100"
          />
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
            Phone
          </label>
          <input
            type="tel"
            name="insurancePhone"
            value={form.insurancePhone}
            onChange={onChange}
            className="w-full px-3 py-2 rounded-lg bg-white border border-gray-200 text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-indigo-500 dark:bg-gray-900 dark:border-gray-800 dark:text-gray-100"
          />
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
            Address
          </label>
          <input
            type="text"
            name="insuranceAddress"
            value={form.insuranceAddress}
            onChange={onChange}
            className="w-full px-3 py-2 rounded-lg bg-white border border-gray-200 text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-indigo-500 dark:bg-gray-900 dark:border-gray-800 dark:text-gray-100"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
            Postcode
          </label>
          <input
            type="text"
            name="insurancePostcode"
            value={form.insurancePostcode}
            onChange={onChange}
            className="w-full px-3 py-2 rounded-lg bg-white border border-gray-200 text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-indigo-500 dark:bg-gray-900 dark:border-gray-800 dark:text-gray-100"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
            City
          </label>
          <input
            type="text"
            name="insuranceCity"
            value={form.insuranceCity}
            onChange={onChange}
            className="w-full px-3 py-2 rounded-lg bg-white border border-gray-200 text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-indigo-500 dark:bg-gray-900 dark:border-gray-800 dark:text-gray-100"
          />
        </div>
      </div>
    </section>
  );
}
