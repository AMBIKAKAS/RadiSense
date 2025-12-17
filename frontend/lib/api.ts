export async function runAnalysis(payload: unknown) {
  const res = await fetch("http://127.0.0.1:8000/api/v1/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Analysis failed");
  }

  return res.json();
}
