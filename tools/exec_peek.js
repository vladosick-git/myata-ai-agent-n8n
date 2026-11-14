// Показывает последние запуски сценария и текст ошибок. Запуск внутри контейнера:
// NODE_PATH=/usr/local/lib/node_modules/n8n/node_modules node /tmp/exec_peek.js [workflowId] [сколько] [искать_строку]
const sqlite3 = require("sqlite3");
const { parse } = require("flatted");
const wf = process.argv[2] || "MyataAgent000001";
const limit = Number(process.argv[3] || 3);
const grep = process.argv[4] || "";
const db = new sqlite3.Database("/home/node/.n8n/database.sqlite", sqlite3.OPEN_READONLY);
db.all(
  `SELECT e.id, e.status, e.startedAt, e.stoppedAt, d.data FROM execution_entity e LEFT JOIN execution_data d ON d.executionId = e.id WHERE e.workflowId = ? ORDER BY e.id DESC LIMIT ?`,
  [wf, limit],
  (err, rows) => {
    if (err) { console.log("ошибка", err.message); return; }
    for (const r of rows) {
      console.log("=== запуск", r.id, r.status, r.startedAt, "→", r.stoppedAt);
      if (!r.data) continue;
      let data;
      try { data = parse(r.data); } catch (e) { console.log("не разобрал данные"); continue; }
      const run = (data.resultData && data.resultData.runData) || {};
      for (const [name, runs] of Object.entries(run)) {
        for (const x of runs) {
          const ms = x.executionTime;
          const errMsg = x.error ? " ОШИБКА: " + (x.error.message || "") + " | " + String(x.error.description || "").slice(0, 300) : "";
          let out = "";
          const main = x.data && (x.data.main || x.data.ai_languageModel || x.data.ai_outputParser);
          if (main && main[0] && main[0][0]) out = JSON.stringify(main[0][0].json);
          if (grep && !(name.includes(grep))) { console.log(" ", name, ms + "мс" + errMsg); continue; }
          console.log(" ", name, ms + "мс" + errMsg, grep ? "\n    " + out.slice(0, 3000) : out.slice(0, 160));
        }
      }
    }
    db.close();
  }
);
