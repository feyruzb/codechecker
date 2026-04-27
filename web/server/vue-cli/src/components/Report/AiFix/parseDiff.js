import parseDiff from "parse-diff";

export function parseAiDiff(text) {
  if (!text) return { lines: [], chunks: [], explanation: "", raw: text };

  try {
    // Extract diff block — try ```diff fences first, then DIFF_START/DIFF_END
    const diffMatch = text.match(/```diff\n([\s\S]*?)```/)
      || text.match(/DIFF_START\n([\s\S]*?)DIFF_END/);
    // Extract explanation after EXPLANATION:
    const explMatch = text.match(/EXPLANATION:\s*([\s\S]*?)$/);

    const explanation = explMatch ? explMatch[1].trim() : "";

    if (!diffMatch) return { lines: [], chunks: [], explanation, raw: text };

    const diffText = diffMatch[1];
    const files = parseDiff(diffText);

    if (!files.length || !files[0].chunks.length) {
      return { lines: [], chunks: [], explanation, raw: text };
    }

    const lines = [];
    for (const chunk of files[0].chunks) {
      for (const change of chunk.changes) {
        const content = change.content.substring(1); // strip +/-/space prefix
        if (change.type === "add") {
          lines.push({
            type: "add", oldNum: null,
            newNum: change.ln, text: content
          });
        } else if (change.type === "del") {
          lines.push({
            type: "remove", oldNum: change.ln,
            newNum: null, text: content
          });
        } else {
          lines.push({
            type: "context", oldNum: change.ln1,
            newNum: change.ln2, text: content
          });
        }
      }
    }

    return { lines, chunks: files[0].chunks, explanation, raw: "" };
  } catch {
    return { lines: [], chunks: [], explanation: "", raw: text };
  }
}

export function mergeWithSource(fileContent, parsed) {
  if (!parsed.chunks || !parsed.chunks.length || !fileContent) {
    return parsed.lines;
  }

  const srcLines = fileContent.split("\n");
  const result = [];
  let oldLine = 1;
  let newLine = 1;

  for (const chunk of parsed.chunks) {
    const chunkOldStart = chunk.oldStart;

    // Unchanged lines before this chunk
    while (oldLine < chunkOldStart && oldLine <= srcLines.length) {
      result.push({
        type: "context", oldNum: oldLine,
        newNum: newLine, text: srcLines[oldLine - 1] || ""
      });
      oldLine++;
      newLine++;
    }

    // Chunk changes
    for (const change of chunk.changes) {
      const content = change.content.substring(1);
      if (change.type === "del") {
        result.push({
          type: "remove", oldNum: oldLine,
          newNum: null, text: content
        });
        oldLine++;
      } else if (change.type === "add") {
        result.push({
          type: "add", oldNum: null,
          newNum: newLine, text: content
        });
        newLine++;
      } else {
        result.push({
          type: "context", oldNum: oldLine,
          newNum: newLine, text: content
        });
        oldLine++;
        newLine++;
      }
    }
  }

  // Remaining lines after last chunk
  while (oldLine <= srcLines.length) {
    result.push({
      type: "context", oldNum: oldLine,
      newNum: newLine, text: srcLines[oldLine - 1] || ""
    });
    oldLine++;
    newLine++;
  }

  // Sanity check: if result is unreasonably large, return just the diff hunks
  if (result.length > srcLines.length * 3) {
    return parsed.lines;
  }

  return result;
}
