const { execFileSync } = require("child_process");

const stripAnsi = s =>
  s.replace(/(\x1B|\u241B)\[[0-9;]*[A-Za-z]/g, "");

const cleanResult = raw => {
  let text = stripAnsi(raw);
  // kiro-cli outputs "> " prompt markers; take content after the last one
  const parts = text.split(/^> /m);
  if (parts.length > 1) text = parts[parts.length - 1];
  // Remove tool-use chatter lines
  text = text.replace(/^(Searching for:|Reading file:|Let me ).*\n?/gm, "");
  text = text.replace(/\(using tool:.*?\)/g, "");
  return text.replace(/\n{3,}/g, "\n\n").trim();
};

module.exports = function aiFix(app) {
  const express = require("express");
  app.use(express.json({ limit: "2mb" }));

  app.post("/api/ai-fix", (req, res) => {
    const {
      fileContent, filePath,
      message, checkerName, line
    } = req.body;

    const prompt = [
      "You are a code review assistant. You MUST respond with ONLY a unified diff and an explanation. No markdown headers, no prose, no extra commentary.",
      "",
      "Checker: " + (checkerName || "unknown"),
      "File: " + (filePath || "unknown"),
      "Line: " + (line || "unknown"),
      "Message: " + (message || "unknown"),
      "",
      "Source code (first 4000 chars):",
      (fileContent || "").substring(0, 4000),
      "",
      "Respond in EXACTLY this format:",
      "",
      "DIFF_START",
      "--- a/" + (filePath || "file"),
      "+++ b/" + (filePath || "file"),
      "@@ -LINE,COUNT +LINE,COUNT @@",
      " context line",
      "-removed line",
      "+added line",
      "DIFF_END",
      "",
      "EXPLANATION:",
      "Your brief explanation here."
    ].join("\n");

    const cmd =
      "kiro-cli";
    const args = ["chat", "--no-interactive", prompt];

    try {
      const result = execFileSync(cmd, args, {
        timeout: 120000,
        encoding: "utf-8",
        maxBuffer: 1024 * 1024,
        env: { ...process.env, NO_COLOR: "1" }
      });
      res.json({ result: cleanResult(result) });
    } catch (err) {
      const out = err.stdout
        || err.stderr || err.message;
      res.json({
        result: "Error: "
          + cleanResult(out).substring(0, 2000)
      });
    }
  });
};
