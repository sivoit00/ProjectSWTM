import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { userNeedsOnboarding } from "../../services/user";

export default function Start() {
  const navigate = useNavigate();

  useEffect(() => {
    const run = async () => {
      try {
        const needs = await userNeedsOnboarding();
        console.log("needsOnboarding:", needs);
        if (needs) {
          navigate("/onboarding", { replace: true });
        } else {
          navigate("/home", { replace: true });
        }
      } catch (e) {
        console.error("Onboarding check failed", e);
        navigate("/home", { replace: true });
      }
    };
    run();
  }, [navigate]);

  return null;
}
