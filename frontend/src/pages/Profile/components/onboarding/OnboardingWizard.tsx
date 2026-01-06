import { useState } from "react";
import type { ProfileFormState } from "../../types";
import { OnboardingStepIndicator } from "./OnboardingStepIndicator";
import { ProfileStep } from "./steps/ProfileStep";
import { VehicleStep } from "./steps/VehicleStep";
import { WorkshopStep } from "./steps/WorkshopStep";
import { LawyerStep } from "./steps/LawyerStep";
import { InsuranceStep } from "./steps/InsuranceStep";

type Props = {
  open: boolean;
  onClose: () => void;
  form: ProfileFormState;
  onChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => void;
  onSubmit: (e: React.FormEvent) => Promise<void>;
};

const stepLabels = ["My Profile", "Insurance", "Lawyer", "Workshop", "Vehicle"];

export function OnboardingWizard({
  open,
  onClose,
  form,
  onChange,
  onSubmit,
}: Props) {
  const [step, setStep] = useState(0);

  if (!open) return null;

  const isLastStep = step === stepLabels.length - 1;

  const next = () => {
    if (!isLastStep) setStep(s => s + 1);
  };

  const prev = () => {
    if (step > 0) setStep(s => s - 1);
  };

  const handleFinish = async (e?: React.FormEvent) => {
  if (e) e.preventDefault();
  await onSubmit(new Event("submit") as any);
  onClose();
};


  const renderStep = () => {
    switch (step) {
      case 0:
        return <ProfileStep form={form} onChange={onChange} />;
      case 1:
        return <InsuranceStep form={form} onChange={onChange} />;
      case 2:
        return <LawyerStep form={form} onChange={onChange} />;
      case 3:
        return <WorkshopStep form={form} onChange={onChange} />;
      case 4:
        return <VehicleStep form={form} onChange={onChange} />;
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50">
      <div className="relative bg-white dark:bg-gray-950 rounded-2xl shadow-xl w-full max-w-3xl p-6 space-y-6">
        <button
          type="button"
          onClick={onClose}
          className="absolute right-4 top-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
        >
          ✕
        </button>

        <div className="space-y-2">
          <h2 className="text-2xl font-semibold">Welcome!</h2>
          <p className="text-gray-700 dark:text-gray-300">
            Let’s set up your account in a few quick steps. This can also be done later in your profile!
          </p>
        </div>

        <OnboardingStepIndicator
          currentStep={step}
          labels={stepLabels}
        />

        <form
          onSubmit={isLastStep ? handleFinish : e => e.preventDefault()}
          className="space-y-6"
        >
          {renderStep()}

          <div className="flex justify-between pt-4 border-t border-gray-200 dark:border-gray-800">
            <button
              type="button"
              onClick={step === 0 ? onClose : prev}
              className="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-100 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-800"
            >
              {step === 0 ? "Skip for now" : "Back"}
            </button>

            {!isLastStep ? (
              <button
                type="button"
                onClick={next}
                className="px-6 py-2 rounded-lg bg-indigo-600 text-white font-semibold hover:bg-indigo-700"
              >
                Next
              </button>
            ) : (
              <button
                type="button"
                onClick={handleFinish}
                className="px-6 py-2 rounded-lg bg-indigo-600 text-white font-semibold hover:bg-indigo-700"
              >
                Finish setup
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
