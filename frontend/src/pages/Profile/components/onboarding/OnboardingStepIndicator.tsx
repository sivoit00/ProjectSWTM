type Props = {
  currentStep: number;
  labels: string[];
};

export function OnboardingStepIndicator({ currentStep, labels }: Props) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex-1 flex items-center gap-2">
        {labels.map((label, index) => {
          const active = index === currentStep;
          const completed = index < currentStep;
          return (
            <div key={label} className="flex-1 flex items-center">
              <div
                className={[
                  "flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold",
                  completed
                    ? "bg-indigo-600 text-white"
                    : active
                    ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/60 dark:text-indigo-100"
                    : "bg-gray-200 text-gray-600 dark:bg-gray-800 dark:text-gray-300",
                ].join(" ")}
              >
                {index + 1}
              </div>
              {index < labels.length - 1 && (
                <div className="flex-1 h-0.5 mx-2 bg-gray-200 dark:bg-gray-800" />
              )}
            </div>
          );
        })}
      </div>
      <span className="ml-4 text-sm text-gray-600 dark:text-gray-300">
        Step {currentStep + 1} of {labels.length}:{" "}
        <span className="font-medium">{labels[currentStep]}</span>
      </span>
    </div>
  );
}
