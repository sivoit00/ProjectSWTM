import { MyProfileSection } from "./components/sections/MyProfileSection";
import { InsuranceSection } from "./components/sections/InsuranceSection";
import { LawyerSection } from "./components/sections/LawyerSection";
import { VehicleSection } from "./components/sections/VehicleSection";
import { WorkshopSection } from "./components/sections/WorkshopSection";
import { FeedbackAlert } from "./components/FeedbackAlert";
import { useProfileForm } from "./hooks/useProfileForm";

export default function Profile() {
  const { form, handleChange, handleSubmit, success, error } = useProfileForm();

  return (
    <div className="flex flex-col items-center h-screen p-8 text-white overflow-y-auto">
      <div className="max-w-4xl w-full space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold pt-2">
            My <span className="text-blue-400">Profile</span>
          </h1>
          <p className="text-gray-300">
            Manage your personal, vehicle and service information in one place.
          </p>
        </div>

        <FeedbackAlert success={success} error={error} />

        <form onSubmit={handleSubmit} className="space-y-8">
          <MyProfileSection form={form} onChange={handleChange} />
          <InsuranceSection form={form} onChange={handleChange} />
          <LawyerSection form={form} onChange={handleChange} />
          <WorkshopSection form={form} onChange={handleChange} />
          <VehicleSection form={form} onChange={handleChange} />

          <div className="flex justify-end">
            <button
              type="submit"
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold shadow-lg transition transform hover:scale-105"
            >
              Save changes
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
