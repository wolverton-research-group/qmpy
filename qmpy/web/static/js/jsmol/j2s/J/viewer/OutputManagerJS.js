Clazz.declarePackage ("J.viewer");
Clazz.load (["J.viewer.OutputManagerAll"], "J.viewer.OutputManagerJS", null, function () {
c$ = Clazz.declareType (J.viewer, "OutputManagerJS", J.viewer.OutputManagerAll);
Clazz.makeConstructor (c$, 
function () {
Clazz.superConstructor (this, J.viewer.OutputManagerJS, []);
});
Clazz.overrideMethod (c$, "clipImageOrPasteText", 
function (text) {
return "Clipboard not available";
}, "~S");
Clazz.overrideMethod (c$, "getClipboardText", 
function () {
return "Clipboard not available";
});
});
