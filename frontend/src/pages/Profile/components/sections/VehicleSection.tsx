import type { ProfileFormState } from "../../types";

type Props = {
  form: ProfileFormState;
  onChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => void;
};

export function VehicleSection({ form, onChange }: Props) {
  return (
    <section className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-950 space-y-4">
            <h2 className="text-2xl font-semibold mb-2">Vehicle</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">Brand</label>
                <input
                  type="text"
                  name="vehicleBrand"
                  value={form.vehicleBrand}
                  onChange={onChange}
                  className="w-full px-3 py-2 rounded-lg bg-white border border-gray-200 text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-indigo-500 dark:bg-gray-900 dark:border-gray-800 dark:text-gray-100"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">Model</label>
                <input
                  type="text"
                  name="vehicleModel"
                  value={form.vehicleModel}
                  onChange={onChange}
                  className="w-full px-3 py-2 rounded-lg bg-white border border-gray-200 text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-indigo-500 dark:bg-gray-900 dark:border-gray-800 dark:text-gray-100"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">Year</label>
                <input
                  type="text"
                  name="vehicleYear"
                  value={form.vehicleYear}
                  onChange={onChange}
                  className="w-full px-3 py-2 rounded-lg bg-white border border-gray-200 text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-indigo-500 dark:bg-gray-900 dark:border-gray-800 dark:text-gray-100"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  Number plate
                </label>
                <input
                  type="text"
                  name="vehicleNumberplate"
                  value={form.vehicleNumberplate}
                  onChange={onChange}
                  className="w-full px-3 py-2 rounded-lg bg-white border border-gray-200 text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-indigo-500 dark:bg-gray-900 dark:border-gray-800 dark:text-gray-100"
                />
              </div>
            </div>
          </section>
  );
}
