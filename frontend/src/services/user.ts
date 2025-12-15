import { api } from "./api";

export async function userNeedsOnboarding(): Promise<boolean> {
  const res = await api.customers.getAll();
  return res.data.length === 0;
}
