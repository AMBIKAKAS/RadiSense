export async function runAnalysis(payload: unknown) {
  const res = await fetch("https://radisense.onrender.com/api/v1/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Analysis failed");
  }

  return res.json();
}
