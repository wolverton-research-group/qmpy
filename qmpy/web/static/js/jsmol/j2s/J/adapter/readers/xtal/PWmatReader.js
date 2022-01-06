Clazz.declarePackage ("J.adapter.readers.xtal");
Clazz.load (["J.adapter.smarter.AtomSetCollectionReader"], "J.adapter.readers.xtal.PWmatReader", ["JU.PT"], function () {
c$ = Clazz.decorateAsClass (function () {
this.nAtoms = 0;
Clazz.instantialize (this, arguments);
}, J.adapter.readers.xtal, "PWmatReader", J.adapter.smarter.AtomSetCollectionReader);
Clazz.overrideMethod (c$, "initializeReader", 
function () {
this.doApplySymmetry = true;
});
Clazz.overrideMethod (c$, "checkLine", 
function () {
if (this.nAtoms == 0) {
this.setSpaceGroupName ("P1");
this.nAtoms = JU.PT.parseInt (this.line);
this.setFractionalCoordinates (true);
return true;
}var lc = this.line.toLowerCase ();
if (lc.startsWith ("lattice")) {
this.readUnitCell ();
} else if (lc.startsWith ("position")) {
this.readCoordinates ();
} else {
this.continuing = false;
}return true;
});
Clazz.defineMethod (c$, "readUnitCell", 
 function () {
var unitCellData =  Clazz.newFloatArray (9, 0);
this.fillFloatArray (null, 0, unitCellData);
this.addExplicitLatticeVector (0, unitCellData, 0);
this.addExplicitLatticeVector (1, unitCellData, 3);
this.addExplicitLatticeVector (2, unitCellData, 6);
});
Clazz.defineMethod (c$, "readCoordinates", 
 function () {
var i = 0;
while (this.rd () != null && i++ < this.nAtoms) {
var tokens = this.getTokens ();
this.addAtomXYZSymName (tokens, 1, null, J.adapter.smarter.AtomSetCollectionReader.getElementSymbol (Integer.parseInt (tokens[0])));
}
});
});
