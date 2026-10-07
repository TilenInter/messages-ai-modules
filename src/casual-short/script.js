// Casual & short – afterReply: a one-line reply doesn't need a full stop at the end ("see you soon." -> "see you soon").
function afterReply(reply) {
  var t = reply.text;
  var oneLine = t.indexOf("\n") === -1;
  var oneSentence = t.split(/[.!?]+/).filter(function (s) { return s.trim().length > 0; }).length === 1;
  if (oneLine && oneSentence && /[^.]\.$/.test(t)) {
    return t.slice(0, -1);
  }
  return undefined; // keep the reply as it is
}
