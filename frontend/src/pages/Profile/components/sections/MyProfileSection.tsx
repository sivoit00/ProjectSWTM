import type { ProfileFormState } from "../../types";

type Props = {
  form: ProfileFormState;
  onChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => void;
};

export function MyProfileSection({ form, onChange }: Props) {
  return (
    <section className="bg-blue-900/30 backdrop-blur-sm border border-blue-500/20 rounded-xl p-6 space-y-4">
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
                  name="lastName"
                  value={form.lastName}
                  onChange={onChange}
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
                  name="email"
                  value={form.email}
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
                  name="phone"
                  value={form.phone}
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
                  name="address"
                  value={form.address}
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
                  name="postcode"
                  value={form.postcode}
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
                  name="city"
                  value={form.city}
                  onChange={onChange}
                  className="w-full px-3 py-2 rounded-lg bg-blue-950/60 border border-blue-500/30 focus:outline-none focus:border-blue-400"
                />
              </div>
            </div>
          </section>
  );
}
