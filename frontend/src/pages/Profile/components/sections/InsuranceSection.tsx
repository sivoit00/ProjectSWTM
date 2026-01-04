import type { ProfileFormState } from "../../types";

type Props = {
  form: ProfileFormState;
  onChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => void;
};

export function InsuranceSection({ form, onChange }: Props) {
  return (
    <section className="bg-blue-900/30 backdrop-blur-sm border border-blue-500/20 rounded-xl p-6 space-y-4">
            <h2 className="text-2xl font-semibold mb-2">Insurance</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-300 mb-1">Name</label>
                <input
                  type="text"
                  name="insuranceName"
                  value={form.insuranceName}
                  onChange={onChange}
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
                  onChange={onChange}
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
                  onChange={onChange}
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
                  onChange={onChange}
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
                  onChange={onChange}
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
                  onChange={onChange}
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
                  onChange={onChange}
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
                  onChange={onChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
            </div>
          </section>
  );
}
