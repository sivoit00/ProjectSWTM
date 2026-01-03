import type { ProfileFormState } from "../../types";

type Props = {
  form: ProfileFormState;
  onChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => void;
};

export function LawyerSection({ form, onChange }: Props) {
  return (
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
                  onChange={onChange}
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
                  onChange={onChange}
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
                  name="lawyerEmail"
                  value={form.lawyerEmail}
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
                  name="lawyerPhone"
                  value={form.lawyerPhone}
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
                  name="lawyerAddress"
                  value={form.lawyerAddress}
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
                  name="lawyerPostcode"
                  value={form.lawyerPostcode}
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
                  name="lawyerCity"
                  value={form.lawyerCity}
                  onChange={onChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
            </div>
          </section>
  );
}
