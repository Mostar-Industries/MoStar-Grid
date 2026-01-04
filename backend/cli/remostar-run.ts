import { MostarAI } from "../models/MostarAI";

function main(): void {
  const ai = new MostarAI();

  console.log("🧠 DCX0 (mind)");
  console.log(ai.inferFromMind("Evaluate justice vs. efficiency."));

  console.log("🕊️ DCX1 (soul)");
  console.log(ai.inferFromSoul("What does Ubuntu say about this conflict?"));

  console.log("⚙️ DCX2 (body)");
  console.log(ai.inferFromBody("Trigger audit + log run."));
}

main();
