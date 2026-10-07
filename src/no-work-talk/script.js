// No work talk – onIncoming: a message about work goes to you instead of getting an automatic reply.
function onIncoming(event) {
  var m = (event.message || "").toLowerCase();
  if (/\b(meeting|deadline|invoice|client|sestanek|rok oddaje)\b/.test(m)) {
    return { handoff: "CUSTOM" };
  }
  return "reply";
}
