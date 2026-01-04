import { redirect } from "next/navigation";

export default function FlameMapPage() {
  // Consolidated: redirect Flame Map to the main Flame view
  redirect("/flame");
}
