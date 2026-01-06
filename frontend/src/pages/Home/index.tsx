import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FileUp, ListChecks, MessageSquare, Wand2 } from "lucide-react";
import { OnboardingWizard } from "../Profile/components/onboarding/OnboardingWizard";
import { useProfileForm } from "../Profile/hooks/useProfileForm";
import keycloak from "../../keycloak";

export default function Home() {
  const navigate = useNavigate();

  const { form, handleChange, handleSubmit } = useProfileForm();
  const [showOnboarding, setShowOnboarding] = useState(false);

  const benefits = [
    {
      title: "One place for the whole case",
      text: "Workshop, insurance and lawyer support — routed automatically.",
    },
    {
      title: "Clear next steps",
      text: "You always know what to do now and what information is needed.",
    },
    {
      title: "Less back-and-forth",
      text: "Draft messages and structured info so you can move faster.",
    },
  ] as const;

  const [benefitIndex, setBenefitIndex] = useState(0);
  const [phase, setPhase] = useState<"pre" | "in" | "out">("pre");

  useEffect(() => {
  const initOnboarding = async () => {
    try {
      const userId =
        keycloak.tokenParsed?.sub || keycloak.tokenParsed?.preferred_username;

      if (!userId) {
        console.warn("No user id in token, skipping onboarding check");
        return;
      }

      const storageKey = `onboardingCompleted:${userId}`;
      const alreadyCompleted = localStorage.getItem(storageKey) === "true";

      if (!alreadyCompleted) {
        setShowOnboarding(true);
      }
    } catch (err) {
      console.error("Error in initOnboarding", err);
    }
  };

  initOnboarding();
}, []);


  const handleFinishOnboarding = async (e: React.FormEvent) => {
  await handleSubmit(e);

  const userId =
    keycloak.tokenParsed?.sub || keycloak.tokenParsed?.preferred_username;

  if (userId) {
    const storageKey = `onboardingCompleted:${userId}`;
    localStorage.setItem(storageKey, "true");
  }

  setShowOnboarding(false);
};


  useEffect(() => {
    let showTimer: number | undefined;
    let hideTimer: number | undefined;
    let enterTimer: number | undefined;
    let isCancelled = false;

    const enter = () => {
      // Start hidden on the left, then slide/fade in.
      setPhase("pre");
      enterTimer = window.setTimeout(() => {
        if (isCancelled) return;
        setPhase("in");
      }, 30);
    };

    const cycle = () => {
      if (isCancelled) return;

      // Enter + visible phase
      enter();
      showTimer = window.setTimeout(() => {
        // Slide/fade out to the right
        setPhase("out");

        hideTimer = window.setTimeout(() => {
          // Swap content while hidden, then fade in
          setBenefitIndex((prev) => (prev + 1) % benefits.length);
          cycle();
        }, 500);
      }, 8000);
    };

    cycle();

    return () => {
      isCancelled = true;
      if (showTimer) window.clearTimeout(showTimer);
      if (hideTimer) window.clearTimeout(hideTimer);
      if (enterTimer) window.clearTimeout(enterTimer);
    };
  }, [benefits.length]);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 dark:bg-gray-950 dark:text-gray-100">
      <div className="mx-auto max-w-6xl px-6 py-7">
        <div className="flex flex-row items-start justify-between gap-4">
          <div className="min-w-0">
            <h1 className="mt-3 text-3xl sm:text-4xl font-bold">
              Welcome to <span className="text-indigo-600 dark:text-indigo-400">MyClone</span>
            </h1>
            <p className="mt-2 text-base sm:text-lg text-gray-700 dark:text-gray-300">
              One agent for workshop, insurance advice, lawyer support and basic treatment — you describe your case once, MyClone routes it and handles the workflow.
            </p>
          </div>

          <button
            onClick={() => navigate("/chat")}
            className="inline-flex shrink-0 items-center justify-center gap-2 whitespace-nowrap px-5 py-3 bg-indigo-600 hover:bg-indigo-700 rounded-lg font-semibold text-white shadow-sm transition"
          >
            <MessageSquare size={18} />
            Start now
          </button>
        </div>

        <div className="mt-6 rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-950">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-800 dark:bg-gray-900">
              <div className="flex items-start gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600 text-white">
                  <MessageSquare size={18} />
                </div>
                <div>
                  <div className="text-xs font-semibold text-indigo-700 dark:text-indigo-400">Step 1</div>
                  <div className="mt-1 text-base font-semibold">Start chat</div>
                  <div className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                    Tell your case in one sentence — any topic.
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-800 dark:bg-gray-900">
              <div className="flex items-start gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600 text-white">
                  <FileUp size={18} />
                </div>
                <div>
                  <div className="text-xs font-semibold text-indigo-700 dark:text-indigo-400">Step 2</div>
                  <div className="mt-1 text-base font-semibold">Add files</div>
                  <div className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                    Photos, invoices, policy docs, letters (optional).
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-800 dark:bg-gray-900">
              <div className="flex items-start gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600 text-white">
                  <Wand2 size={18} />
                </div>
                <div>
                  <div className="text-xs font-semibold text-indigo-700 dark:text-indigo-400">Step 3</div>
                  <div className="mt-1 text-base font-semibold">Get next steps</div>
                  <div className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                    MyClone guides you and takes over the busywork.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-5 grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-950">
            <div className="text-sm font-semibold">Example request</div>
            <div className="mt-3 space-y-2">
              <div className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-900 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-100">
                “I had an accident — do I need a lawyer, and what should I do next?”
              </div>
              <div className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-900 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-100">
                “I can upload photos, my insurance policy, and the other party’s details.”
              </div>
            </div>
            <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
              Tip: Mention dates, location, and what documents you already have.
            </div>
          </div>

          <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-950">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <ListChecks size={16} className="text-indigo-600 dark:text-indigo-400" />
              What you get
            </div>
            <div className="mt-3 space-y-2 text-sm text-gray-700 dark:text-gray-300">
              <div className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-900">
                Automatic routing (workshop / insurance / lawyer)
              </div>
              <div className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-900">
                Clear next steps (what to do now)
              </div>
              <div className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-900">
                Draft messages + the exact info/files needed
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-950">
          <div className="text-sm font-semibold">
            Why{" "}
            <span className="text-indigo-600 dark:text-indigo-400">MyClone</span>
          </div>
          <div
            className={`mt-2 transition-[opacity,transform] duration-500 ease-out motion-reduce:transition-none motion-reduce:transform-none ${
              phase === "in"
                ? "opacity-100 translate-x-0"
                : phase === "out"
                  ? "opacity-0 translate-x-8"
                  : "opacity-0 -translate-x-8"
            }`}
            aria-live="polite"
          >
            <div className="text-base font-semibold">
              {benefits[benefitIndex].title}
            </div>
            <div className="mt-1 text-sm text-gray-700 dark:text-gray-300">
              {benefits[benefitIndex].text}
            </div>
          </div>
        </div>
      </div>
      <OnboardingWizard
        open={showOnboarding}
        onClose={() => setShowOnboarding(false)}
        form={form}
        onChange={handleChange}
        onSubmit={handleFinishOnboarding}
      />
    </div>
  );
}
