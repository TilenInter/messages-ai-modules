// No work talk – onIncoming: a message about work goes to you instead of getting an automatic reply.
// Words in the six app languages (en, sl, de, hr, it, es); whole words only, so "client" doesn't match "clientele".
var WORDS = [
  "meeting", "meetings", "deadline", "deadlines", "invoice", "invoices", "client", "clients",
  "sestanek", "sestanka", "sestanku", "sestanki", "rok oddaje", "faktura", "fakturo",
  "besprechung", "frist", "rechnung", "kunde", "kunden",
  "sastanak", "sastanka", "sastanku", "rok predaje", "klijent", "klijenta", "klijenti",
  "riunione", "riunioni", "scadenza", "fattura", "fatture", "cliente", "clienti",
  "reunión", "reunion", "reuniones", "plazo de entrega", "factura", "facturas", "clientes"
];

function onIncoming(event) {
  var text = " " + (event.message || "").toLowerCase().replace(/[\s.,!?;:"'()\[\]¿¡«»„“”…-]+/g, " ") + " ";
  for (var i = 0; i < WORDS.length; i++) {
    if (text.indexOf(" " + WORDS[i] + " ") !== -1) {
      return { handoff: "CUSTOM" };
    }
  }
  return "reply";
}
