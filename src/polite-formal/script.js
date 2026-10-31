// Polite & formal – afterReply: a reply starts with a capital letter, and a one-line reply that ends in a word gets a
// full stop ("thank you, see you on monday" -> "Thank you, see you on monday."). A link, address or tag at the end and
// scripts without capital letters are left as they are.
function isLetter(c) {
  return c.toUpperCase() !== c.toLowerCase();
}

function afterReply(reply) {
  var text = reply.text || "";
  var out = text;
  var first = out.charAt(0);
  if (isLetter(first) && first === first.toLowerCase()) {
    out = first.toUpperCase() + out.slice(1);
  }
  var words = out.split(/\s+/);
  var last = words[words.length - 1];
  if (out.indexOf("\n") === -1 && isLetter(out.charAt(out.length - 1)) && !/[\/@.:#]/.test(last)) {
    out = out + ".";
  }
  return out === text ? undefined : out; // undefined keeps the reply as it is
}
