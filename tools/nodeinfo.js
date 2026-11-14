// Справка по узлам n8n: node nodeinfo.js [имя_узла] — без аргумента печатает версии нужных узлов.
const a = JSON.parse(require("fs").readFileSync("/tmp/nodes.json", "utf8"));
const by = {};
for (const n of a) (by[n.name] = by[n.name] || []).push(n);
const arg = process.env.NODE_NAME;
if (!arg) {
  const want = ["@n8n/n8n-nodes-langchain.agent", "@n8n/n8n-nodes-langchain.lmChatAnthropic", "@n8n/n8n-nodes-langchain.outputParserStructured", "@n8n/n8n-nodes-langchain.memoryBufferWindow", "@n8n/n8n-nodes-langchain.chainLlm", "n8n-nodes-base.googleSheets", "n8n-nodes-base.telegram", "n8n-nodes-base.httpRequest", "n8n-nodes-base.scheduleTrigger", "n8n-nodes-base.executeWorkflow", "n8n-nodes-base.executeWorkflowTrigger", "n8n-nodes-base.switch", "n8n-nodes-base.code", "n8n-nodes-base.set", "n8n-nodes-base.if", "n8n-nodes-base.splitOut", "n8n-nodes-base.aggregate", "n8n-nodes-base.merge", "n8n-nodes-base.dataTable"];
  for (const w of want) {
    const l = by[w] || [];
    console.log(w, "->", l.map((n) => JSON.stringify(n.version) + " def=" + n.defaultVersion).join(" | ") || "НЕТ");
  }
} else {
  const l = by[arg] || [];
  const n = l[l.length - 1];
  if (!n) { console.log("нет узла", arg); process.exit(0); }
  console.log("version", JSON.stringify(n.version), "default", n.defaultVersion);
  console.log("credentials", JSON.stringify((n.credentials || []).map((c) => [c.name, c.displayOptions])));
  const show = (p, ind) => {
    const dv = typeof p.default === "object" ? JSON.stringify(p.default) : p.default;
    console.log(ind + p.name + " [" + p.type + "] def=" + String(dv).slice(0, 80) + (p.displayOptions ? " show=" + JSON.stringify(p.displayOptions).slice(0, 160) : ""));
    if (p.options && process.env.DEEP) for (const o of p.options) {
      if (o.values) { console.log(ind + "  <" + o.name + ">"); for (const v of o.values) show(v, ind + "    "); }
      else if (o.type) show(o, ind + "  ");
      else console.log(ind + "  = " + o.value);
    }
  };
  for (const p of n.properties) show(p, "");
}
