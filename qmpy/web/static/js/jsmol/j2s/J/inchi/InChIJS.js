Clazz.declarePackage ("J.inchi");
Clazz.load (["J.api.JmolInChI"], "J.inchi.InChIJS", ["JU.PT"], function () {
c$ = Clazz.declareType (J.inchi, "InChIJS", null, J.api.JmolInChI);
Clazz.makeConstructor (c$, 
function () {
});
Clazz.overrideMethod (c$, "getInchi", 
function (vwr, atoms, molData, options) {
if (atoms == null ? molData == null : atoms.cardinality () == 0) return "";
var ret = "";
try {
if (options == null) options = "";
options = JU.PT.rep (JU.PT.rep (options.$replace ('-', ' '), "  ", " ").trim (), " ", " -").toLowerCase ();
if (options.length > 0) options = "-" + options;
if (molData == null) molData = vwr.getModelExtract (atoms, false, false, "MOL");
if (molData.startsWith ("InChI=")) {
{
ret = (Jmol.inchiToInchiKey ? Jmol.inchiToInchiKey(molData) : "");
}} else {
var haveKey = (options.indexOf ("key") >= 0);
if (haveKey) {
options = options.$replace ("inchikey", "key");
}{
ret = (Jmol.molfileToInChI ? Jmol.molfileToInChI(molData, options) : "");
}}} catch (e) {
{
e = (e.getMessage$ ? e.getMessage$() : e);
}System.err.println ("InChIJS exception: " + e);
}
return ret;
}, "JV.Viewer,JU.BS,~S,~S");
{
var wasmPath = "/_WASM";
var es6Path = "/_ES6";
try {
{
var j2sPath = Jmol._applets.master._j2sFullPath;
//
Jmol.inchiPath = j2sPath + wasmPath;
//
var importPath = j2sPath + es6Path;
//
import(importPath + "/molfile-to-inchi.js");
}} catch (t) {
}
}});
