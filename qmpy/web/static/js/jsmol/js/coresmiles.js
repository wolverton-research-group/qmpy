Clazz.declarePackage ("J.api");
Clazz.declareInterface (J.api, "SmilesMatcherInterface");
Clazz.declarePackage ("J.smiles");
Clazz.load (["J.api.SmilesMatcherInterface"], "J.smiles.SmilesMatcher", ["J.smiles.InvalidSmilesException", "$.SmilesGenerator", "$.SmilesParser", "J.util.ArrayUtil", "$.BS", "$.BSUtil", "$.TextFormat"], function () {
c$ = Clazz.declareType (J.smiles, "SmilesMatcher", null, J.api.SmilesMatcherInterface);
Clazz.overrideMethod (c$, "getLastException", 
function () {
return J.smiles.InvalidSmilesException.getLastError ();
});
Clazz.overrideMethod (c$, "getMolecularFormula", 
function (pattern, isSmarts) {
J.smiles.InvalidSmilesException.setLastError (null);
try {
var search = J.smiles.SmilesParser.getMolecule (pattern, isSmarts);
search.createTopoMap (null);
search.nodes = search.jmolAtoms;
return search.getMolecularFormula (!isSmarts);
} catch (e) {
if (Clazz.exceptionOf (e, J.smiles.InvalidSmilesException)) {
if (J.smiles.InvalidSmilesException.getLastError () == null) J.smiles.InvalidSmilesException.setLastError (e.toString ());
return null;
} else {
throw e;
}
}
}, "~S,~B");
Clazz.overrideMethod (c$, "getSmiles", 
function (atoms, atomCount, bsSelected, asBioSmiles, allowUnmatchedRings, addCrossLinks, comment) {
J.smiles.InvalidSmilesException.setLastError (null);
try {
if (asBioSmiles) return ( new J.smiles.SmilesGenerator ()).getBioSmiles (atoms, atomCount, bsSelected, allowUnmatchedRings, addCrossLinks, comment);
return ( new J.smiles.SmilesGenerator ()).getSmiles (atoms, atomCount, bsSelected);
} catch (e) {
if (Clazz.exceptionOf (e, J.smiles.InvalidSmilesException)) {
if (J.smiles.InvalidSmilesException.getLastError () == null) J.smiles.InvalidSmilesException.setLastError (e.toString ());
return null;
} else {
throw e;
}
}
}, "~A,~N,J.util.BS,~B,~B,~B,~S");
$_M(c$, "areEqual", 
function (smiles1, smiles2) {
var result = this.find (smiles1, smiles2, false, false);
return (result == null ? -1 : result.length);
}, "~S,~S");
$_M(c$, "areEqual", 
function (smiles, molecule) {
var ret = this.find (smiles, molecule, false, true, true);
return (ret != null && ret.length == 1);
}, "~S,J.smiles.SmilesSearch");
$_M(c$, "find", 
function (pattern, smiles, isSmarts, firstMatchOnly) {
J.smiles.InvalidSmilesException.setLastError (null);
try {
var search = J.smiles.SmilesParser.getMolecule (smiles, false);
return this.find (pattern, search, isSmarts, !isSmarts, firstMatchOnly);
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
if (J.smiles.InvalidSmilesException.getLastError () == null) J.smiles.InvalidSmilesException.setLastError (e.toString ());
System.out.println (e.toString ());
return null;
} else {
throw e;
}
}
}, "~S,~S,~B,~B");
Clazz.overrideMethod (c$, "getRelationship", 
function (smiles1, smiles2) {
if (smiles1 == null || smiles2 == null || smiles1.length == 0 || smiles2.length == 0) return "";
var mf1 = this.getMolecularFormula (smiles1, false);
var mf2 = this.getMolecularFormula (smiles2, false);
if (!mf1.equals (mf2)) return "none";
var check;
var n1 = this.countStereo (smiles1);
var n2 = this.countStereo (smiles2);
check = (n1 == n2 && this.areEqual (smiles2, smiles1) > 0);
if (!check) {
var s = smiles1 + smiles2;
if (s.indexOf ("/") >= 0 || s.indexOf ("\\") >= 0 || s.indexOf ("@") >= 0) {
if (n1 == n2 && n1 > 0) {
smiles1 = this.reverseChirality (smiles1);
check = (this.areEqual (smiles1, smiles2) > 0);
if (check) return "enantiomers";
}check = (this.areEqual ("/nostereo/" + smiles2, smiles1) > 0);
if (check) return (n1 == n2 ? "diastereomers" : "ambiguous stereochemistry!");
}return "constitutional isomers";
}return "identical";
}, "~S,~S");
Clazz.overrideMethod (c$, "reverseChirality", 
function (smiles) {
smiles = J.util.TextFormat.simpleReplace (smiles, "@@", "!@");
smiles = J.util.TextFormat.simpleReplace (smiles, "@", "@@");
smiles = J.util.TextFormat.simpleReplace (smiles, "!@@", "@");
smiles = J.util.TextFormat.simpleReplace (smiles, "@@SP", "@SP");
smiles = J.util.TextFormat.simpleReplace (smiles, "@@OH", "@OH");
smiles = J.util.TextFormat.simpleReplace (smiles, "@@TB", "@TB");
return smiles;
}, "~S");
Clazz.overrideMethod (c$, "getSubstructureSet", 
function (pattern, atoms, atomCount, bsSelected, isSmarts, firstMatchOnly) {
return this.match (pattern, atoms, atomCount, bsSelected, null, isSmarts, false, firstMatchOnly, 1);
}, "~S,~A,~N,J.util.BS,~B,~B");
Clazz.overrideMethod (c$, "getSubstructureSets", 
function (smarts, atoms, atomCount, flags, bsSelected, ret, vRings) {
J.smiles.InvalidSmilesException.setLastError (null);
var sp =  new J.smiles.SmilesParser (true);
var search = null;
try {
search = sp.parse ("");
search.firstMatchOnly = false;
search.matchAllAtoms = false;
search.jmolAtoms = atoms;
search.jmolAtomCount = Math.abs (atomCount);
search.setSelected (bsSelected);
search.getRingData (true, flags, vRings);
search.asVector = false;
search.subSearches =  new Array (1);
search.getSelections ();
} catch (e) {
if (Clazz.exceptionOf (e, J.smiles.InvalidSmilesException)) {
} else {
throw e;
}
}
var bsDone =  new J.util.BS ();
for (var i = 0; i < smarts.length; i++) {
if (smarts[i] == null || smarts[i].length == 0 || smarts[i].startsWith ("#")) {
ret.addLast (null);
continue;
}try {
search.clear ();
var ss = sp.getSearch (search, J.smiles.SmilesParser.cleanPattern (smarts[i]), flags);
search.subSearches[0] = ss;
var bs = J.util.BSUtil.copy (search.search (false));
ret.addLast (bs);
bsDone.or (bs);
if (bsDone.cardinality () == atomCount) return;
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
if (J.smiles.InvalidSmilesException.getLastError () == null) J.smiles.InvalidSmilesException.setLastError (e.toString ());
System.out.println (e.toString ());
} else {
throw e;
}
}
}
}, "~A,~A,~N,~N,J.util.BS,J.util.JmolList,~A");
Clazz.overrideMethod (c$, "getSubstructureSetArray", 
function (pattern, atoms, atomCount, bsSelected, bsAromatic, isSmarts, firstMatchOnly) {
return this.match (pattern, atoms, atomCount, bsSelected, bsAromatic, isSmarts, false, firstMatchOnly, 2);
}, "~S,~A,~N,J.util.BS,J.util.BS,~B,~B");
Clazz.overrideMethod (c$, "getCorrelationMaps", 
function (pattern, atoms, atomCount, bsSelected, isSmarts, firstMatchOnly) {
return this.match (pattern, atoms, atomCount, bsSelected, null, isSmarts, false, firstMatchOnly, 3);
}, "~S,~A,~N,J.util.BS,~B,~B");
$_M(c$, "find", 
($fz = function (pattern, search, isSmarts, matchAllAtoms, firstMatchOnly) {
var bsAromatic =  new J.util.BS ();
search.createTopoMap (bsAromatic);
return this.match (pattern, search.jmolAtoms, -search.jmolAtoms.length, null, bsAromatic, isSmarts, matchAllAtoms, firstMatchOnly, 2);
}, $fz.isPrivate = true, $fz), "~S,J.smiles.SmilesSearch,~B,~B,~B");
$_M(c$, "match", 
($fz = function (pattern, atoms, atomCount, bsSelected, bsAromatic, isSmarts, matchAllAtoms, firstMatchOnly, mode) {
J.smiles.InvalidSmilesException.setLastError (null);
try {
var search = J.smiles.SmilesParser.getMolecule (pattern, isSmarts);
search.jmolAtoms = atoms;
search.jmolAtomCount = Math.abs (atomCount);
if (atomCount < 0) search.isSmilesFind = true;
search.setSelected (bsSelected);
search.getSelections ();
search.bsRequired = null;
search.setRingData (bsAromatic);
search.firstMatchOnly = firstMatchOnly;
search.matchAllAtoms = matchAllAtoms;
switch (mode) {
case 1:
search.asVector = false;
return search.search (false);
case 2:
search.asVector = true;
var vb = search.search (false);
return vb.toArray ( new Array (vb.size ()));
case 3:
search.getMaps = true;
var vl = search.search (false);
return vl.toArray (J.util.ArrayUtil.newInt2 (vl.size ()));
}
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
if (J.smiles.InvalidSmilesException.getLastError () == null) J.smiles.InvalidSmilesException.setLastError (e.toString ());
System.out.println (e.toString ());
} else {
throw e;
}
}
return null;
}, $fz.isPrivate = true, $fz), "~S,~A,~N,J.util.BS,J.util.BS,~B,~B,~B,~N");
$_M(c$, "countStereo", 
($fz = function (s) {
s = J.util.TextFormat.simpleReplace (s, "@@", "@");
var i = s.lastIndexOf ('@') + 1;
var n = 0;
for (; --i >= 0; ) if (s.charAt (i) == '@') n++;

return n;
}, $fz.isPrivate = true, $fz), "~S");
Clazz.defineStatics (c$,
"MODE_BITSET", 1,
"MODE_ARRAY", 2,
"MODE_MAP", 3);
});
Clazz.declarePackage ("J.smiles");
Clazz.load (["java.lang.Exception"], "J.smiles.InvalidSmilesException", null, function () {
c$ = Clazz.declareType (J.smiles, "InvalidSmilesException", Exception);
c$.getLastError = $_M(c$, "getLastError", 
function () {
return J.smiles.InvalidSmilesException.lastError;
});
c$.setLastError = $_M(c$, "setLastError", 
function (message) {
($t$ = J.smiles.InvalidSmilesException.lastError = message, J.smiles.InvalidSmilesException.prototype.lastError = J.smiles.InvalidSmilesException.lastError, $t$);
}, "~S");
Clazz.makeConstructor (c$, 
function (message) {
Clazz.superConstructor (this, J.smiles.InvalidSmilesException, [message]);
($t$ = J.smiles.InvalidSmilesException.lastError = message, J.smiles.InvalidSmilesException.prototype.lastError = J.smiles.InvalidSmilesException.lastError, $t$);
}, "~S");
Clazz.makeConstructor (c$, 
function (cause) {
Clazz.superConstructor (this, J.smiles.InvalidSmilesException, [cause]);
($t$ = J.smiles.InvalidSmilesException.lastError = cause.toString (), J.smiles.InvalidSmilesException.prototype.lastError = J.smiles.InvalidSmilesException.lastError, $t$);
}, "Throwable");
Clazz.makeConstructor (c$, 
function (message, cause) {
Clazz.superConstructor (this, J.smiles.InvalidSmilesException, [message, cause]);
($t$ = J.smiles.InvalidSmilesException.lastError = message + "\n" + cause.getCause (), J.smiles.InvalidSmilesException.prototype.lastError = J.smiles.InvalidSmilesException.lastError, $t$);
}, "~S,Throwable");
Clazz.defineStatics (c$,
"lastError", null);
});
Clazz.declarePackage ("J.smiles");
Clazz.load (["J.util.JmolMolecule", "$.BS", "$.JmolList", "$.V3"], "J.smiles.SmilesSearch", ["java.util.Arrays", "$.Hashtable", "J.smiles.SmilesAromatic", "$.SmilesAtom", "$.SmilesBond", "$.SmilesMeasure", "$.SmilesParser", "J.util.ArrayUtil", "$.BSUtil", "$.Logger", "$.SB"], function () {
c$ = Clazz.decorateAsClass (function () {
this.patternAtoms = null;
this.pattern = null;
this.jmolAtoms = null;
this.jmolAtomCount = 0;
this.bsSelected = null;
this.bsRequired = null;
this.firstMatchOnly = false;
this.matchAllAtoms = false;
this.isSmarts = false;
this.isSmilesFind = false;
this.subSearches = null;
this.haveSelected = false;
this.haveBondStereochemistry = false;
this.haveAtomStereochemistry = false;
this.needRingData = false;
this.needAromatic = true;
this.needRingMemberships = false;
this.ringDataMax = -2147483648;
this.measures = null;
this.flags = 0;
this.ringSets = null;
this.bsAromatic = null;
this.bsAromatic5 = null;
this.bsAromatic6 = null;
this.lastChainAtom = null;
this.asVector = false;
this.getMaps = false;
this.top = null;
this.isSilent = false;
this.isRingCheck = false;
this.selectedAtomCount = 0;
this.ringData = null;
this.ringCounts = null;
this.ringConnections = null;
this.bsFound = null;
this.htNested = null;
this.nNested = 0;
this.nestedBond = null;
this.vReturn = null;
this.bsReturn = null;
this.ignoreStereochemistry = false;
this.noAromatic = false;
this.aromaticDouble = false;
this.bsCheck = null;
this.v = null;
Clazz.instantialize (this, arguments);
}, J.smiles, "SmilesSearch", J.util.JmolMolecule);
Clazz.prepareFields (c$, function () {
this.patternAtoms =  new Array (16);
this.measures =  new J.util.JmolList ();
this.bsAromatic =  new J.util.BS ();
this.bsAromatic5 =  new J.util.BS ();
this.bsAromatic6 =  new J.util.BS ();
this.top = this;
this.bsFound =  new J.util.BS ();
this.bsReturn =  new J.util.BS ();
this.v =  new J.smiles.SmilesSearch.VTemp ();
});
$_M(c$, "toString", 
function () {
var sb =  new J.util.SB ().append (this.pattern);
sb.append ("\nmolecular formula: " + this.getMolecularFormula (true));
return sb.toString ();
});
$_M(c$, "setSelected", 
function (bs) {
if (bs == null) {
bs = J.util.BSUtil.newBitSet (this.jmolAtomCount);
bs.setBits (0, this.jmolAtomCount);
}this.bsSelected = bs;
}, "J.util.BS");
$_M(c$, "setAtomArray", 
function () {
if (this.patternAtoms.length > this.atomCount) this.patternAtoms = J.util.ArrayUtil.arrayCopyObject (this.patternAtoms, this.atomCount);
this.nodes = this.patternAtoms;
});
$_M(c$, "addAtom", 
function () {
if (this.atomCount >= this.patternAtoms.length) this.patternAtoms = J.util.ArrayUtil.doubleLength (this.patternAtoms);
var sAtom =  new J.smiles.SmilesAtom ().setIndex (this.atomCount);
this.patternAtoms[this.atomCount] = sAtom;
this.atomCount++;
return sAtom;
});
$_M(c$, "addNested", 
function (pattern) {
if (this.top.htNested == null) this.top.htNested =  new java.util.Hashtable ();
this.setNested (++this.top.nNested, pattern);
return this.top.nNested;
}, "~S");
$_M(c$, "clear", 
function () {
this.bsReturn.clearAll ();
this.nNested = 0;
this.htNested = null;
this.nestedBond = null;
this.clearBsFound (-1);
});
$_M(c$, "setNested", 
function (iNested, o) {
this.top.htNested.put ("_" + iNested, o);
}, "~N,~O");
$_M(c$, "getNested", 
function (iNested) {
return this.top.htNested.get ("_" + iNested);
}, "~N");
$_M(c$, "getMissingHydrogenCount", 
function () {
var n = 0;
var nH;
for (var i = 0; i < this.atomCount; i++) if ((nH = this.patternAtoms[i].missingHydrogenCount) >= 0) n += nH;

return n;
});
$_M(c$, "setRingData", 
function (bsA) {
if (this.needAromatic) this.needRingData = true;
var noAromatic = ((this.flags & 1) != 0);
this.needAromatic = new Boolean (this.needAromatic & ( new Boolean ((bsA == null) & !noAromatic).valueOf ())).valueOf ();
if (!this.needAromatic) {
this.bsAromatic.clearAll ();
if (bsA != null) this.bsAromatic.or (bsA);
if (!this.needRingMemberships && !this.needRingData) return;
}this.getRingData (this.needRingData, this.flags, null);
}, "J.util.BS");
$_M(c$, "getRingData", 
function (needRingData, flags, vRings) {
var aromaticStrict = ((flags & 4) != 0);
var aromaticDefined = ((flags & 8) != 0);
if (aromaticStrict && vRings == null) vRings = J.util.ArrayUtil.createArrayOfArrayList (4);
if (aromaticDefined && this.needAromatic) {
this.bsAromatic = J.smiles.SmilesAromatic.checkAromaticDefined (this.jmolAtoms, this.bsSelected);
aromaticStrict = false;
}if (this.ringDataMax < 0) this.ringDataMax = 8;
if (aromaticStrict && this.ringDataMax < 6) this.ringDataMax = 6;
if (needRingData) {
this.ringCounts =  Clazz.newIntArray (this.jmolAtomCount, 0);
this.ringConnections =  Clazz.newIntArray (this.jmolAtomCount, 0);
this.ringData =  new Array (this.ringDataMax + 1);
}this.ringSets =  new J.util.SB ();
var s = "****";
while (s.length < this.ringDataMax) s += s;

var v5 = null;
for (var i = 3; i <= this.ringDataMax; i++) {
if (i > this.jmolAtomCount) continue;
var smarts = "*1" + s.substring (0, i - 2) + "*1";
var search = J.smiles.SmilesParser.getMolecule (smarts, true);
var vR = this.subsearch (search, false, true);
if (vRings != null && i <= 5) {
var v =  new J.util.JmolList ();
for (var j = vR.size (); --j >= 0; ) v.addLast (vR.get (j));

vRings[i - 3] = v;
}if (this.needAromatic) {
if (!aromaticDefined && (!aromaticStrict || i == 5 || i == 6)) for (var r = vR.size (); --r >= 0; ) {
var bs = vR.get (r);
if (aromaticDefined || J.smiles.SmilesAromatic.isFlatSp2Ring (this.jmolAtoms, this.bsSelected, bs, (aromaticStrict ? 0.1 : 0.01))) this.bsAromatic.or (bs);
}
if (aromaticStrict) {
switch (i) {
case 5:
v5 = vR;
break;
case 6:
if (aromaticDefined) this.bsAromatic = J.smiles.SmilesAromatic.checkAromaticDefined (this.jmolAtoms, this.bsAromatic);
 else J.smiles.SmilesAromatic.checkAromaticStrict (this.jmolAtoms, this.bsAromatic, v5, vR);
vRings[3] =  new J.util.JmolList ();
this.setAromatic56 (v5, this.bsAromatic5, 5, vRings[3]);
this.setAromatic56 (vR, this.bsAromatic6, 6, vRings[3]);
break;
}
}}if (needRingData) {
this.ringData[i] =  new J.util.BS ();
for (var k = 0; k < vR.size (); k++) {
var r = vR.get (k);
this.ringData[i].or (r);
for (var j = r.nextSetBit (0); j >= 0; j = r.nextSetBit (j + 1)) this.ringCounts[j]++;

}
}}
if (needRingData) {
for (var i = this.bsSelected.nextSetBit (0); i >= 0; i = this.bsSelected.nextSetBit (i + 1)) {
var atom = this.jmolAtoms[i];
var bonds = atom.getEdges ();
if (bonds != null) for (var k = bonds.length; --k >= 0; ) if (this.ringCounts[atom.getBondedAtomIndex (k)] > 0) this.ringConnections[i]++;

}
}}, "~B,~N,~A");
$_M(c$, "setAromatic56", 
($fz = function (vRings, bs56, n56, vAromatic56) {
for (var k = 0; k < vRings.size (); k++) {
var r = vRings.get (k);
this.v.bsTemp.clearAll ();
this.v.bsTemp.or (r);
this.v.bsTemp.and (this.bsAromatic);
if (this.v.bsTemp.cardinality () == n56) {
bs56.or (r);
if (vAromatic56 != null) vAromatic56.addLast (r);
}}
}, $fz.isPrivate = true, $fz), "J.util.JmolList,J.util.BS,~N,J.util.JmolList");
$_M(c$, "subsearch", 
function (search, firstAtomOnly, isRingCheck) {
search.ringSets = this.ringSets;
search.jmolAtoms = this.jmolAtoms;
search.jmolAtomCount = this.jmolAtomCount;
search.bsSelected = this.bsSelected;
search.htNested = this.htNested;
search.isSmilesFind = this.isSmilesFind;
search.bsCheck = this.bsCheck;
search.isSmarts = true;
search.bsAromatic = this.bsAromatic;
search.bsAromatic5 = this.bsAromatic5;
search.bsAromatic6 = this.bsAromatic6;
search.ringData = this.ringData;
search.ringCounts = this.ringCounts;
search.ringConnections = this.ringConnections;
if (firstAtomOnly) {
search.bsRequired = null;
search.firstMatchOnly = false;
search.matchAllAtoms = false;
} else if (isRingCheck) {
search.bsRequired = null;
search.isSilent = true;
search.isRingCheck = true;
search.asVector = true;
search.matchAllAtoms = false;
} else {
search.haveSelected = this.haveSelected;
search.bsRequired = this.bsRequired;
search.firstMatchOnly = this.firstMatchOnly;
search.matchAllAtoms = this.matchAllAtoms;
search.getMaps = this.getMaps;
search.asVector = this.asVector;
search.vReturn = this.vReturn;
search.bsReturn = this.bsReturn;
}return search.search (firstAtomOnly);
}, "J.smiles.SmilesSearch,~B,~B");
$_M(c$, "search", 
function (firstAtomOnly) {
this.ignoreStereochemistry = ((this.flags & 2) != 0);
this.noAromatic = ((this.flags & 1) != 0);
this.aromaticDouble = ((this.flags & 16) != 0);
if (J.util.Logger.debugging && !this.isSilent) J.util.Logger.debug ("SmilesSearch processing " + this.pattern);
if (this.vReturn == null && (this.asVector || this.getMaps)) this.vReturn =  new J.util.JmolList ();
if (this.bsSelected == null) {
this.bsSelected = J.util.BSUtil.newBitSet (this.jmolAtomCount);
this.bsSelected.setBits (0, this.jmolAtomCount);
}this.selectedAtomCount = this.bsSelected.cardinality ();
if (this.subSearches != null) {
for (var i = 0; i < this.subSearches.length; i++) {
if (this.subSearches[i] == null) continue;
this.subsearch (this.subSearches[i], false, false);
if (this.firstMatchOnly) {
if (this.vReturn == null ? this.bsReturn.nextSetBit (0) >= 0 : this.vReturn.size () > 0) break;
}}
} else if (this.atomCount > 0) {
this.checkMatch (null, -1, -1, firstAtomOnly);
}return (this.asVector || this.getMaps ? this.vReturn : this.bsReturn);
}, "~B");
$_M(c$, "checkMatch", 
($fz = function (patternAtom, atomNum, iAtom, firstAtomOnly) {
var jmolAtom;
var jmolBonds;
if (patternAtom == null) {
if (this.nestedBond == null) {
this.clearBsFound (-1);
} else {
this.bsReturn.clearAll ();
}} else {
if (this.bsFound.get (iAtom) || !this.bsSelected.get (iAtom)) return true;
jmolAtom = this.jmolAtoms[iAtom];
if (!this.isRingCheck) {
if (patternAtom.atomsOr != null) {
for (var ii = 0; ii < patternAtom.nAtomsOr; ii++) if (!this.checkMatch (patternAtom.atomsOr[ii], atomNum, iAtom, firstAtomOnly)) return false;

return true;
}if (patternAtom.primitives == null) {
if (!this.checkPrimitiveAtom (patternAtom, iAtom)) return true;
} else {
for (var i = 0; i < patternAtom.nPrimitives; i++) if (!this.checkPrimitiveAtom (patternAtom.primitives[i], iAtom)) return true;

}}jmolBonds = jmolAtom.getEdges ();
for (var i = patternAtom.getBondCount (); --i >= 0; ) {
var patternBond = patternAtom.getBond (i);
if (patternBond.getAtomIndex2 () != patternAtom.index) continue;
var atom1 = patternBond.getAtom1 ();
var matchingAtom = atom1.getMatchingAtom ();
switch (patternBond.order) {
case 96:
case 112:
if (!this.checkMatchBond (patternAtom, atom1, patternBond, iAtom, matchingAtom, null)) return true;
break;
default:
var k = 0;
for (; k < jmolBonds.length; k++) if ((jmolBonds[k].getAtomIndex1 () == matchingAtom || jmolBonds[k].getAtomIndex2 () == matchingAtom) && jmolBonds[k].isCovalent ()) break;

if (k == jmolBonds.length) return true;
if (!this.checkMatchBond (patternAtom, atom1, patternBond, iAtom, matchingAtom, jmolBonds[k])) return true;
}
}
this.patternAtoms[patternAtom.index].setMatchingAtom (iAtom);
if (J.util.Logger.debugging && !this.isSilent) J.util.Logger.debug ("pattern atom " + atomNum + " " + patternAtom);
this.bsFound.set (iAtom);
}if (!this.continueMatch (atomNum, iAtom, firstAtomOnly)) return false;
if (iAtom >= 0) this.clearBsFound (iAtom);
return true;
}, $fz.isPrivate = true, $fz), "J.smiles.SmilesAtom,~N,~N,~B");
$_M(c$, "continueMatch", 
($fz = function (atomNum, iAtom, firstAtomOnly) {
var jmolAtom;
var jmolBonds;
if (++atomNum < this.atomCount) {
var newPatternAtom = this.patternAtoms[atomNum];
var newPatternBond = (iAtom >= 0 ? newPatternAtom.getBondTo (null) : atomNum == 0 ? this.nestedBond : null);
if (newPatternBond == null) {
var bs = J.util.BSUtil.copy (this.bsFound);
if (newPatternAtom.notBondedIndex >= 0) {
var pa = this.patternAtoms[newPatternAtom.notBondedIndex];
var a = this.jmolAtoms[pa.getMatchingAtom ()];
if (pa.bioType == '\0') {
jmolBonds = a.getEdges ();
for (var k = 0; k < jmolBonds.length; k++) bs.set (jmolBonds[k].getOtherAtomNode (a).getIndex ());

} else {
var ii = a.getOffsetResidueAtom ("0", 1);
if (ii >= 0) bs.set (ii);
ii = a.getOffsetResidueAtom ("0", -1);
if (ii >= 0) bs.set (ii);
}}var skipGroup = (iAtom >= 0 && newPatternAtom.isBioAtom && (newPatternAtom.atomName == null || newPatternAtom.residueChar != null));
for (var j = this.bsSelected.nextSetBit (0); j >= 0; j = this.bsSelected.nextSetBit (j + 1)) {
if (!bs.get (j) && !this.checkMatch (newPatternAtom, atomNum, j, firstAtomOnly)) return false;
if (skipGroup) {
var j1 = this.jmolAtoms[j].getOffsetResidueAtom (newPatternAtom.atomName, 1);
if (j1 >= 0) j = j1 - 1;
}}
this.bsFound = bs;
return true;
}jmolAtom = this.jmolAtoms[newPatternBond.getAtom1 ().getMatchingAtom ()];
switch (newPatternBond.order) {
case 96:
var nextGroupAtom = jmolAtom.getOffsetResidueAtom (newPatternAtom.atomName, 1);
if (nextGroupAtom >= 0) {
var bs = J.util.BSUtil.copy (this.bsFound);
jmolAtom.getGroupBits (this.bsFound);
if (!this.checkMatch (newPatternAtom, atomNum, nextGroupAtom, firstAtomOnly)) return false;
this.bsFound = bs;
}return true;
case 112:
var vLinks =  new J.util.JmolList ();
jmolAtom.getCrossLinkLeadAtomIndexes (vLinks);
var bs = J.util.BSUtil.copy (this.bsFound);
jmolAtom.getGroupBits (this.bsFound);
for (var j = 0; j < vLinks.size (); j++) if (!this.checkMatch (newPatternAtom, atomNum, vLinks.get (j).intValue (), firstAtomOnly)) return false;

this.bsFound = bs;
return true;
}
jmolBonds = jmolAtom.getEdges ();
if (jmolBonds != null) for (var j = 0; j < jmolBonds.length; j++) if (!this.checkMatch (newPatternAtom, atomNum, jmolAtom.getBondedAtomIndex (j), firstAtomOnly)) return false;

this.clearBsFound (iAtom);
return true;
}if (!this.ignoreStereochemistry && !this.checkStereochemistry ()) return true;
var bs =  new J.util.BS ();
var nMatch = 0;
for (var j = 0; j < this.atomCount; j++) {
var i = this.patternAtoms[j].getMatchingAtom ();
if (!firstAtomOnly && this.top.haveSelected && !this.patternAtoms[j].selected) continue;
nMatch++;
bs.set (i);
if (this.patternAtoms[j].isBioAtom && this.patternAtoms[j].atomName == null) this.jmolAtoms[i].getGroupBits (bs);
if (firstAtomOnly) break;
if (!this.isSmarts && this.patternAtoms[j].missingHydrogenCount > 0) this.getHydrogens (this.jmolAtoms[i], bs);
}
if (this.bsRequired != null && !this.bsRequired.intersects (bs)) return true;
if (this.matchAllAtoms && bs.cardinality () != this.selectedAtomCount) return true;
if (this.bsCheck != null) {
if (firstAtomOnly) {
this.bsCheck.clearAll ();
for (var j = 0; j < this.atomCount; j++) {
this.bsCheck.set (this.patternAtoms[j].getMatchingAtom ());
}
if (this.bsCheck.cardinality () != this.atomCount) return true;
} else {
if (bs.cardinality () != this.atomCount) return true;
}}this.bsReturn.or (bs);
if (this.getMaps) {
var map =  Clazz.newIntArray (nMatch, 0);
for (var j = 0, nn = 0; j < this.atomCount; j++) {
if (!firstAtomOnly && this.top.haveSelected && !this.patternAtoms[j].selected) continue;
map[nn++] = this.patternAtoms[j].getMatchingAtom ();
}
this.vReturn.addLast (map);
return !this.firstMatchOnly;
}if (this.asVector) {
var isOK = true;
for (var j = this.vReturn.size (); --j >= 0 && isOK; ) isOK = !((this.vReturn.get (j)).equals (bs));

if (!isOK) return true;
this.vReturn.addLast (bs);
}if (this.isRingCheck) {
this.ringSets.append (" ");
for (var k = atomNum * 3 + 2; --k > atomNum; ) this.ringSets.append ("-").appendI (this.patternAtoms[(k <= atomNum * 2 ? atomNum * 2 - k + 1 : k - 1) % atomNum].getMatchingAtom ());

this.ringSets.append ("- ");
return true;
}if (this.firstMatchOnly) return false;
return (bs.cardinality () != this.selectedAtomCount);
}, $fz.isPrivate = true, $fz), "~N,~N,~B");
$_M(c$, "clearBsFound", 
($fz = function (iAtom) {
if (iAtom < 0) {
if (this.bsCheck == null) {
this.bsFound.clearAll ();
}} else this.bsFound.clear (iAtom);
}, $fz.isPrivate = true, $fz), "~N");
$_M(c$, "getHydrogens", 
($fz = function (atom, bsHydrogens) {
var b = atom.getEdges ();
var k = -1;
for (var i = 0; i < b.length; i++) if (this.jmolAtoms[atom.getBondedAtomIndex (i)].getElementNumber () == 1) {
k = atom.getBondedAtomIndex (i);
if (bsHydrogens == null) break;
bsHydrogens.set (k);
}
return (k >= 0 ? this.jmolAtoms[k] : null);
}, $fz.isPrivate = true, $fz), "J.util.JmolNode,J.util.BS");
$_M(c$, "checkPrimitiveAtom", 
($fz = function (patternAtom, iAtom) {
var atom = this.jmolAtoms[iAtom];
var foundAtom = patternAtom.not;
while (true) {
var n;
if (patternAtom.iNested > 0) {
var o = this.getNested (patternAtom.iNested);
if (Clazz.instanceOf (o, J.smiles.SmilesSearch)) {
var search = o;
if (patternAtom.isBioAtom) search.nestedBond = patternAtom.getBondTo (null);
o = this.subsearch (search, true, false);
if (o == null) o =  new J.util.BS ();
if (!patternAtom.isBioAtom) this.setNested (patternAtom.iNested, o);
}foundAtom = (patternAtom.not != ((o).get (iAtom)));
break;
}if (patternAtom.isBioAtom) {
if (patternAtom.atomName != null && (patternAtom.isLeadAtom () ? !atom.isLeadAtom () : !patternAtom.atomName.equals (atom.getAtomName ().toUpperCase ()))) break;
if (patternAtom.residueName != null && !patternAtom.residueName.equals (atom.getGroup3 (false).toUpperCase ())) break;
if (patternAtom.residueChar != null) {
if (patternAtom.isDna () && !atom.isDna () || patternAtom.isRna () && !atom.isRna () || patternAtom.isProtein () && !atom.isProtein () || patternAtom.isNucleic () && !atom.isNucleic ()) break;
var s = atom.getGroup1 ('\0').toUpperCase ();
var isOK = patternAtom.residueChar.equals (s);
switch (patternAtom.residueChar.charAt (0)) {
case 'N':
isOK = patternAtom.isNucleic () ? atom.isNucleic () : isOK;
break;
case 'R':
isOK = patternAtom.isNucleic () ? atom.isPurine () : isOK;
break;
case 'Y':
isOK = patternAtom.isNucleic () ? atom.isPyrimidine () : isOK;
break;
}
if (!isOK) break;
}if (patternAtom.elementNumber >= 0 && patternAtom.elementNumber != atom.getElementNumber ()) break;
if (patternAtom.notCrossLinked && atom.getCrossLinkLeadAtomIndexes (null)) break;
} else {
if (patternAtom.jmolIndex >= 0 && atom.getIndex () != patternAtom.jmolIndex) break;
if (patternAtom.atomType != null && !patternAtom.atomType.equals (atom.getAtomType ())) break;
if (patternAtom.elementNumber >= 0 && patternAtom.elementNumber != atom.getElementNumber ()) break;
var isAromatic = patternAtom.isAromatic ();
if (!this.noAromatic && !patternAtom.aromaticAmbiguous && isAromatic != this.bsAromatic.get (iAtom)) break;
if ((n = patternAtom.getAtomicMass ()) != -2147483648) {
var isotope = atom.getIsotopeNumber ();
if (n >= 0 && n != isotope || n < 0 && isotope != 0 && -n != isotope) {
break;
}}if ((n = patternAtom.getCharge ()) != -2147483648 && n != atom.getFormalCharge ()) break;
n = patternAtom.getCovalentHydrogenCount () + patternAtom.missingHydrogenCount;
if (n >= 0 && n != atom.getCovalentHydrogenCount ()) break;
n = patternAtom.implicitHydrogenCount;
if (n != -2147483648) {
var nH = atom.getImplicitHydrogenCount ();
if (n == -1 ? nH == 0 : n != nH) break;
}if (patternAtom.degree > 0 && patternAtom.degree != atom.getCovalentBondCount ()) break;
if (patternAtom.nonhydrogenDegree > 0 && patternAtom.nonhydrogenDegree != atom.getCovalentBondCount () - atom.getCovalentHydrogenCount ()) break;
if (patternAtom.valence > 0 && patternAtom.valence != atom.getValence ()) break;
if (patternAtom.connectivity > 0 && patternAtom.connectivity != atom.getCovalentBondCount () + atom.getImplicitHydrogenCount ()) break;
if (this.ringData != null && patternAtom.ringSize >= -1) {
if (patternAtom.ringSize <= 0) {
if ((this.ringCounts[iAtom] == 0) != (patternAtom.ringSize == 0)) break;
} else {
var rd = this.ringData[patternAtom.ringSize == 500 ? 5 : patternAtom.ringSize == 600 ? 6 : patternAtom.ringSize];
if (rd == null || !rd.get (iAtom)) break;
if (!this.noAromatic) if (patternAtom.ringSize == 500) {
if (!this.bsAromatic5.get (iAtom)) break;
} else if (patternAtom.ringSize == 600) {
if (!this.bsAromatic6.get (iAtom)) break;
}}}if (this.ringData != null && patternAtom.ringMembership >= -1) {
if (patternAtom.ringMembership == -1 ? this.ringCounts[iAtom] == 0 : this.ringCounts[iAtom] != patternAtom.ringMembership) break;
}if (patternAtom.ringConnectivity >= 0) {
n = this.ringConnections[iAtom];
if (patternAtom.ringConnectivity == -1 && n == 0 || patternAtom.ringConnectivity != -1 && n != patternAtom.ringConnectivity) break;
}}foundAtom = !foundAtom;
break;
}
return foundAtom;
}, $fz.isPrivate = true, $fz), "J.smiles.SmilesAtom,~N");
$_M(c$, "checkMatchBond", 
($fz = function (patternAtom, atom1, patternBond, iAtom, matchingAtom, bond) {
if (patternBond.bondsOr != null) {
for (var ii = 0; ii < patternBond.nBondsOr; ii++) if (this.checkMatchBond (patternAtom, atom1, patternBond.bondsOr[ii], iAtom, matchingAtom, bond)) return true;

return false;
}if (patternBond.primitives == null) {
if (!this.checkPrimitiveBond (patternBond, iAtom, matchingAtom, bond)) return false;
} else {
for (var i = 0; i < patternBond.nPrimitives; i++) if (!this.checkPrimitiveBond (patternBond.primitives[i], iAtom, matchingAtom, bond)) return false;

}patternBond.matchingBond = bond;
return true;
}, $fz.isPrivate = true, $fz), "J.smiles.SmilesAtom,J.smiles.SmilesAtom,J.smiles.SmilesBond,~N,~N,J.util.JmolEdge");
$_M(c$, "checkPrimitiveBond", 
($fz = function (patternBond, iAtom1, iAtom2, bond) {
var bondFound = false;
switch (patternBond.order) {
case 96:
return (patternBond.isNot != (this.jmolAtoms[iAtom2].getOffsetResidueAtom ("0", 1) == this.jmolAtoms[iAtom1].getOffsetResidueAtom ("0", 0)));
case 112:
return (patternBond.isNot != this.jmolAtoms[iAtom1].isCrossLinked (this.jmolAtoms[iAtom2]));
}
var isAromatic1 = (!this.noAromatic && this.bsAromatic.get (iAtom1));
var isAromatic2 = (!this.noAromatic && this.bsAromatic.get (iAtom2));
var order = bond.getCovalentOrder ();
if (isAromatic1 && isAromatic2) {
switch (patternBond.order) {
case 17:
case 65:
bondFound = J.smiles.SmilesSearch.isRingBond (this.ringSets, iAtom1, iAtom2);
break;
case 1:
bondFound = !this.isSmarts || !J.smiles.SmilesSearch.isRingBond (this.ringSets, iAtom1, iAtom2);
break;
case 2:
bondFound = !this.isSmarts || this.aromaticDouble && (order == 2 || order == 514);
break;
case 769:
case 1025:
case 81:
case -1:
bondFound = true;
break;
}
} else {
switch (patternBond.order) {
case 81:
case -1:
bondFound = true;
break;
case 1:
case 257:
case 513:
bondFound = (order == 1 || order == 1041 || order == 1025);
break;
case 769:
bondFound = (order == (this.isSmilesFind ? 33 : 1));
break;
case 1025:
bondFound = (order == (this.isSmilesFind ? 97 : 1));
break;
case 2:
bondFound = (order == 2);
break;
case 3:
bondFound = (order == 3);
break;
case 65:
bondFound = J.smiles.SmilesSearch.isRingBond (this.ringSets, iAtom1, iAtom2);
break;
}
}return bondFound != patternBond.isNot;
}, $fz.isPrivate = true, $fz), "J.smiles.SmilesBond,~N,~N,J.util.JmolEdge");
c$.isRingBond = $_M(c$, "isRingBond", 
function (ringSets, i, j) {
return (ringSets != null && ringSets.indexOf ("-" + i + "-" + j + "-") >= 0);
}, "J.util.SB,~N,~N");
$_M(c$, "checkStereochemistry", 
($fz = function () {
for (var i = 0; i < this.measures.size (); i++) if (!this.measures.get (i).check ()) return false;

if (this.haveAtomStereochemistry) {
if (J.util.Logger.debugging) J.util.Logger.debug ("checking stereochemistry...");
var atom1 = null;
var atom2 = null;
var atom3 = null;
var atom4 = null;
var atom5 = null;
var atom6 = null;
var sAtom1 = null;
var sAtom2 = null;
var jn;
for (var i = 0; i < this.atomCount; i++) {
var sAtom = this.patternAtoms[i];
var atom0 = this.jmolAtoms[sAtom.getMatchingAtom ()];
var nH = sAtom.missingHydrogenCount;
if (nH < 0) nH = 0;
var chiralClass = sAtom.getChiralClass ();
if (chiralClass == -2147483648) continue;
var order = sAtom.getChiralOrder ();
if (this.isSmilesFind && (atom0.getAtomSite () >> 8) != chiralClass) return false;
atom4 = null;
if (J.util.Logger.debugging) J.util.Logger.debug ("...type " + chiralClass + " for pattern atom " + sAtom + " " + atom0);
switch (chiralClass) {
case 2:
var isAllene = true;
if (isAllene) {
sAtom1 = sAtom.getBond (0).getOtherAtom (sAtom);
sAtom2 = sAtom.getBond (1).getOtherAtom (sAtom);
if (sAtom1 == null || sAtom2 == null) continue;
var sAtom1a = sAtom;
var sAtom2a = sAtom;
while (sAtom1.getBondCount () == 2 && sAtom2.getBondCount () == 2 && sAtom1.getValence () == 4 && sAtom2.getValence () == 4) {
var b = sAtom1.getBondNotTo (sAtom1a, true);
sAtom1a = sAtom1;
sAtom1 = b.getOtherAtom (sAtom1);
b = sAtom2.getBondNotTo (sAtom2a, true);
sAtom2a = sAtom2;
sAtom2 = b.getOtherAtom (sAtom2);
}
sAtom = sAtom1;
}jn =  new Array (6);
jn[4] =  new J.smiles.SmilesAtom ().setIndex (604);
var nBonds = sAtom.getBondCount ();
for (var k = 0; k < nBonds; k++) {
sAtom1 = sAtom.bonds[k].getOtherAtom (sAtom);
if (sAtom.bonds[k].matchingBond.getCovalentOrder () == 2) {
if (sAtom2 == null) sAtom2 = sAtom1;
} else if (jn[0] == null) {
jn[0] = this.getJmolAtom (sAtom1.getMatchingAtom ());
} else {
jn[1] = this.getJmolAtom (sAtom1.getMatchingAtom ());
}}
if (sAtom2 == null) continue;
nBonds = sAtom2.getBondCount ();
if (nBonds < 2 || nBonds > 3) continue;
for (var k = 0; k < nBonds; k++) {
sAtom1 = sAtom2.bonds[k].getOtherAtom (sAtom2);
if (sAtom2.bonds[k].matchingBond.getCovalentOrder () == 2) {
} else if (jn[2] == null) {
jn[2] = this.getJmolAtom (sAtom1.getMatchingAtom ());
} else {
jn[3] = this.getJmolAtom (sAtom1.getMatchingAtom ());
}}
if (this.isSmilesFind) {
if (jn[1] == null) this.getX (sAtom, jn, 1, false, isAllene);
if (jn[3] == null) this.getX (sAtom2, jn, 3, false, false);
if (!this.setSmilesCoordinates (atom0, sAtom, sAtom2, jn)) return false;
}if (jn[1] == null) this.getX (sAtom, jn, 1, true, false);
if (jn[3] == null) this.getX (sAtom2, jn, 3, true, false);
if (!J.smiles.SmilesSearch.checkStereochemistryAll (sAtom.not, atom0, chiralClass, order, jn[0], jn[1], jn[2], jn[3], null, null, this.v)) return false;
continue;
case 4:
case 8:
case 5:
case 6:
atom1 = this.getJmolAtom (sAtom.getMatchingBondedAtom (0));
switch (nH) {
case 0:
atom2 = this.getJmolAtom (sAtom.getMatchingBondedAtom (1));
break;
case 1:
atom2 = this.getHydrogens (this.getJmolAtom (sAtom.getMatchingAtom ()), null);
if (sAtom.isFirst) {
var a = atom2;
atom2 = atom1;
atom1 = a;
}break;
default:
continue;
}
atom3 = this.getJmolAtom (sAtom.getMatchingBondedAtom (2 - nH));
atom4 = this.getJmolAtom (sAtom.getMatchingBondedAtom (3 - nH));
atom5 = this.getJmolAtom (sAtom.getMatchingBondedAtom (4 - nH));
atom6 = this.getJmolAtom (sAtom.getMatchingBondedAtom (5 - nH));
if (this.isSmilesFind && !this.setSmilesCoordinates (atom0, sAtom, sAtom2, [atom1, atom2, atom3, atom4, atom5, atom6])) return false;
if (!J.smiles.SmilesSearch.checkStereochemistryAll (sAtom.not, atom0, chiralClass, order, atom1, atom2, atom3, atom4, atom5, atom6, this.v)) return false;
continue;
}
}
}if (this.haveBondStereochemistry) {
for (var k = 0; k < this.atomCount; k++) {
var sAtom1 = this.patternAtoms[k];
var sAtom2 = null;
var sAtomDirected1 = null;
var sAtomDirected2 = null;
var dir1 = 0;
var dir2 = 0;
var bondType = 0;
var b;
var nBonds = sAtom1.getBondCount ();
var isAtropisomer = false;
for (var j = 0; j < nBonds; j++) {
b = sAtom1.getBond (j);
var isAtom2 = (b.getAtom2 () === sAtom1);
var type = b.order;
switch (type) {
case 769:
case 1025:
case 2:
if (isAtom2) continue;
sAtom2 = b.getAtom2 ();
bondType = type;
isAtropisomer = (type != 2);
if (isAtropisomer) dir1 = (b.isNot ? -1 : 1);
break;
case 257:
case 513:
sAtomDirected1 = (isAtom2 ? b.getAtom1 () : b.getAtom2 ());
dir1 = (isAtom2 != (type == 257) ? 1 : -1);
break;
}
}
if (isAtropisomer) {
b = sAtom1.getBondNotTo (sAtom2, false);
if (b == null) return false;
sAtomDirected1 = b.getOtherAtom (sAtom1);
b = sAtom2.getBondNotTo (sAtom1, false);
if (b == null) return false;
sAtomDirected2 = b.getOtherAtom (sAtom2);
} else {
if (sAtom2 == null || dir1 == 0) continue;
nBonds = sAtom2.getBondCount ();
for (var j = 0; j < nBonds && dir2 == 0; j++) {
b = sAtom2.getBond (j);
var isAtom2 = (b.getAtom2 () === sAtom2);
var type = b.order;
switch (type) {
case 257:
case 513:
sAtomDirected2 = (isAtom2 ? b.getAtom1 () : b.getAtom2 ());
dir2 = (isAtom2 != (type == 257) ? 1 : -1);
break;
}
}
if (dir2 == 0) continue;
}if (this.isSmilesFind) this.setSmilesBondCoordinates (sAtom1, sAtom2, bondType);
var dbAtom1 = this.getJmolAtom (sAtom1.getMatchingAtom ());
var dbAtom2 = this.getJmolAtom (sAtom2.getMatchingAtom ());
var dbAtom1a = this.getJmolAtom (sAtomDirected1.getMatchingAtom ());
var dbAtom2a = this.getJmolAtom (sAtomDirected2.getMatchingAtom ());
if (dbAtom1a == null || dbAtom2a == null) return false;
J.smiles.SmilesMeasure.setTorsionData (dbAtom1a, dbAtom1, dbAtom2, dbAtom2a, this.v, isAtropisomer);
if (isAtropisomer) {
dir2 = (bondType == 769 ? 1 : -1);
var f = this.v.vTemp1.dot (this.v.vTemp2);
if (f < 0.05 || f > 0.95 || this.v.vNorm1.dot (this.v.vNorm2) * dir1 * dir2 > 0) return false;
} else {
if (this.v.vTemp1.dot (this.v.vTemp2) * dir1 * dir2 < 0) return false;
}}
}return true;
}, $fz.isPrivate = true, $fz));
$_M(c$, "getX", 
($fz = function (sAtom, jn, pt, haveCoordinates, needHSwitch) {
var atom = this.getJmolAtom (sAtom.getMatchingAtom ());
var doSwitch = sAtom.isFirst || pt == 3;
if (haveCoordinates) {
if (this.isSmarts) {
var b = atom.getEdges ();
for (var i = 0; i < b.length; i++) {
if (b[i].getCovalentOrder () == 2) continue;
var a = this.jmolAtoms[atom.getBondedAtomIndex (i)];
if (a === jn[pt - 1]) continue;
jn[pt] = a;
break;
}
}if (jn[pt] == null) {
var v =  new J.util.V3 ();
var n = 0;
for (var i = 0; i < 4; i++) {
if (jn[i] == null) continue;
n++;
v.sub (jn[i]);
}
if (v.length () == 0) {
v.setT ((jn[4]));
doSwitch = false;
} else {
v.scaleAdd2 (n + 1, this.getJmolAtom (sAtom.getMatchingAtom ()), v);
doSwitch = this.isSmilesFind || doSwitch;
}jn[pt] =  new J.smiles.SmilesAtom ().setIndex (-1);
(jn[pt]).setT (v);
}}if (jn[pt] == null) {
jn[pt] = this.getHydrogens (atom, null);
if (needHSwitch) doSwitch = true;
}if (jn[pt] != null && doSwitch) {
var a = jn[pt];
jn[pt] = jn[pt - 1];
jn[pt - 1] = a;
}}, $fz.isPrivate = true, $fz), "J.smiles.SmilesAtom,~A,~N,~B,~B");
c$.checkStereochemistryAll = $_M(c$, "checkStereochemistryAll", 
function (isNot, atom0, chiralClass, order, atom1, atom2, atom3, atom4, atom5, atom6, v) {
switch (chiralClass) {
default:
case 2:
case 4:
return (isNot == (J.smiles.SmilesSearch.getHandedness (atom2, atom3, atom4, atom1, v) != order));
case 5:
return (isNot == (!J.smiles.SmilesSearch.isDiaxial (atom0, atom0, atom5, atom1, v, -0.95) || J.smiles.SmilesSearch.getHandedness (atom2, atom3, atom4, atom1, v) != order));
case 6:
if (isNot != (!J.smiles.SmilesSearch.isDiaxial (atom0, atom0, atom6, atom1, v, -0.95))) return false;
J.smiles.SmilesSearch.getPlaneNormals (atom2, atom3, atom4, atom5, v);
if (isNot != (v.vNorm1.dot (v.vNorm2) < 0 || v.vNorm2.dot (v.vNorm3) < 0)) return false;
v.vNorm2.setT (atom0);
v.vNorm2.sub (atom1);
return (isNot == ((v.vNorm1.dot (v.vNorm2) < 0 ? 2 : 1) == order));
case 8:
J.smiles.SmilesSearch.getPlaneNormals (atom1, atom2, atom3, atom4, v);
return (v.vNorm1.dot (v.vNorm2) < 0 ? isNot == (order != 3) : v.vNorm2.dot (v.vNorm3) < 0 ? isNot == (order != 2) : isNot == (order != 1));
}
}, "~B,J.util.JmolNode,~N,~N,J.util.JmolNode,J.util.JmolNode,J.util.JmolNode,J.util.JmolNode,J.util.JmolNode,J.util.JmolNode,J.smiles.SmilesSearch.VTemp");
$_M(c$, "getJmolAtom", 
($fz = function (i) {
return (i < 0 || i >= this.jmolAtoms.length ? null : this.jmolAtoms[i]);
}, $fz.isPrivate = true, $fz), "~N");
$_M(c$, "setSmilesBondCoordinates", 
($fz = function (sAtom1, sAtom2, bondType) {
var dbAtom1 = this.jmolAtoms[sAtom1.getMatchingAtom ()];
var dbAtom2 = this.jmolAtoms[sAtom2.getMatchingAtom ()];
dbAtom1.set (-1, 0, 0);
dbAtom2.set (1, 0, 0);
if (bondType == 2) {
var nBonds = 0;
var dir1 = 0;
var bonds = dbAtom1.getEdges ();
for (var k = bonds.length; --k >= 0; ) {
var bond = bonds[k];
var atom = bond.getOtherAtomNode (dbAtom1);
if (atom === dbAtom2) continue;
atom.set (-1, (nBonds++ == 0) ? -1 : 1, 0);
var mode = (bond.getAtomIndex2 () == dbAtom1.getIndex () ? nBonds : -nBonds);
switch (bond.order) {
case 1025:
dir1 = mode;
break;
case 1041:
dir1 = -mode;
}
}
var dir2 = 0;
nBonds = 0;
var atoms =  new Array (2);
bonds = dbAtom2.getEdges ();
for (var k = bonds.length; --k >= 0; ) {
var bond = bonds[k];
var atom = bond.getOtherAtomNode (dbAtom2);
if (atom === dbAtom1) continue;
atoms[nBonds] = atom;
atom.set (1, (nBonds++ == 0) ? 1 : -1, 0);
var mode = (bond.getAtomIndex2 () == dbAtom2.getIndex () ? nBonds : -nBonds);
switch (bond.order) {
case 1025:
dir2 = mode;
break;
case 1041:
dir2 = -mode;
}
}
if ((dir1 * dir2 > 0) == (Math.abs (dir1) % 2 == Math.abs (dir2) % 2)) {
var y = (atoms[0]).y;
(atoms[0]).y = (atoms[1]).y;
(atoms[1]).y = y;
}} else {
var bonds = dbAtom1.getEdges ();
var dir = 0;
for (var k = bonds.length; --k >= 0; ) {
var bond = bonds[k];
if (bond.getOtherAtomNode (dbAtom1) === dbAtom2) {
dir = (bond.order == 33 ? 1 : -1);
break;
}}
for (var k = bonds.length; --k >= 0; ) {
var bond = bonds[k];
var atom = bond.getOtherAtomNode (dbAtom1);
if (atom !== dbAtom2) atom.set (-1, 1, 0);
}
bonds = dbAtom2.getEdges ();
for (var k = bonds.length; --k >= 0; ) {
var bond = bonds[k];
var atom = bond.getOtherAtomNode (dbAtom2);
if (atom !== dbAtom1) atom.set (1, 1, -dir / 2.0);
}
}}, $fz.isPrivate = true, $fz), "J.smiles.SmilesAtom,J.smiles.SmilesAtom,~N");
$_M(c$, "setSmilesCoordinates", 
($fz = function (atom, sAtom, sAtom2, cAtoms) {
var atomSite = atom.getAtomSite ();
if (atomSite == -2147483648) return false;
var chiralClass = atomSite >> 8;
var chiralOrder = atomSite & 0xFF;
var a2 = (chiralClass == 2 || chiralClass == 3 ? a2 = this.jmolAtoms[sAtom2.getMatchingAtom ()] : null);
atom.set (0, 0, 0);
atom = this.jmolAtoms[sAtom.getMatchingAtom ()];
atom.set (0, 0, 0);
var map = this.getMappedAtoms (atom, a2, cAtoms);
switch (chiralClass) {
case 2:
case 4:
if (chiralOrder == 2) {
var i = map[0];
map[0] = map[1];
map[1] = i;
}cAtoms[map[0]].set (0, 0, 1);
cAtoms[map[1]].set (1, 0, -1);
cAtoms[map[2]].set (0, 1, -1);
cAtoms[map[3]].set (-1, -1, -1);
break;
case 8:
switch (chiralOrder) {
case 1:
cAtoms[map[0]].set (1, 0, 0);
cAtoms[map[1]].set (0, 1, 0);
cAtoms[map[2]].set (-1, 0, 0);
cAtoms[map[3]].set (0, -1, 0);
break;
case 2:
cAtoms[map[0]].set (1, 0, 0);
cAtoms[map[1]].set (-1, 0, 0);
cAtoms[map[2]].set (0, 1, 0);
cAtoms[map[3]].set (0, -1, 0);
break;
case 3:
cAtoms[map[0]].set (1, 0, 0);
cAtoms[map[1]].set (0, 1, 0);
cAtoms[map[2]].set (0, -1, 0);
cAtoms[map[3]].set (-1, 0, 0);
break;
}
break;
case 5:
case 6:
var n = map.length;
if (chiralOrder == 2) {
var i = map[0];
map[0] = map[n - 1];
map[n - 1] = i;
}cAtoms[map[0]].set (0, 0, 1);
cAtoms[map[n - 1]].set (0, 0, -1);
cAtoms[map[1]].set (1, 0, 0);
cAtoms[map[2]].set (0, 1, 0);
cAtoms[map[3]].set (-1, 0, 0);
if (n == 6) cAtoms[map[4]].set (0, -1, 0);
break;
}
return true;
}, $fz.isPrivate = true, $fz), "J.util.JmolNode,J.smiles.SmilesAtom,J.smiles.SmilesAtom,~A");
$_M(c$, "getMappedAtoms", 
function (atom, a2, cAtoms) {
var map =  Clazz.newIntArray (cAtoms[4] == null ? 4 : cAtoms[5] == null ? 5 : 6, 0);
for (var i = 0; i < map.length; i++) map[i] = (cAtoms[i] == null ? 104 + i * 100 : cAtoms[i].getIndex ());

var k;
var bonds = atom.getEdges ();
var b2 = (a2 == null ? null : a2.getEdges ());
for (var i = 0; i < map.length; i++) {
for (k = 0; k < bonds.length; k++) if (bonds[k].getOtherAtomNode (atom) === cAtoms[i]) break;

if (k < bonds.length) {
map[i] = (k * 10 + 100) + i;
} else if (a2 != null) {
for (k = 0; k < b2.length; k++) if (b2[k].getOtherAtomNode (a2) === cAtoms[i]) break;

if (k < b2.length) map[i] = (k * 10 + 300) + i;
}}
java.util.Arrays.sort (map);
for (var i = 0; i < map.length; i++) {
map[i] = map[i] % 10;
}
return map;
}, "J.util.JmolNode,J.util.JmolNode,~A");
c$.isDiaxial = $_M(c$, "isDiaxial", 
function (atomA, atomB, atom1, atom2, v, f) {
v.vA.setT (atomA);
v.vB.setT (atomB);
v.vA.sub (atom1);
v.vB.sub (atom2);
v.vA.normalize ();
v.vB.normalize ();
return (v.vA.dot (v.vB) < f);
}, "J.util.JmolNode,J.util.JmolNode,J.util.JmolNode,J.util.JmolNode,J.smiles.SmilesSearch.VTemp,~N");
c$.getHandedness = $_M(c$, "getHandedness", 
($fz = function (a, b, c, pt, v) {
var d = J.smiles.SmilesAromatic.getNormalThroughPoints (a, b, c, v.vTemp, v.vA, v.vB);
return (J.smiles.SmilesSearch.distanceToPlane (v.vTemp, d, pt) > 0 ? 1 : 2);
}, $fz.isPrivate = true, $fz), "J.util.JmolNode,J.util.JmolNode,J.util.JmolNode,J.util.JmolNode,J.smiles.SmilesSearch.VTemp");
c$.getPlaneNormals = $_M(c$, "getPlaneNormals", 
($fz = function (atom1, atom2, atom3, atom4, v) {
J.smiles.SmilesAromatic.getNormalThroughPoints (atom1, atom2, atom3, v.vNorm1, v.vTemp1, v.vTemp2);
J.smiles.SmilesAromatic.getNormalThroughPoints (atom2, atom3, atom4, v.vNorm2, v.vTemp1, v.vTemp2);
J.smiles.SmilesAromatic.getNormalThroughPoints (atom3, atom4, atom1, v.vNorm3, v.vTemp1, v.vTemp2);
}, $fz.isPrivate = true, $fz), "J.util.JmolNode,J.util.JmolNode,J.util.JmolNode,J.util.JmolNode,J.smiles.SmilesSearch.VTemp");
c$.distanceToPlane = $_M(c$, "distanceToPlane", 
function (norm, w, pt) {
return (norm == null ? NaN : (norm.x * pt.x + norm.y * pt.y + norm.z * pt.z + w) / Math.sqrt (norm.x * norm.x + norm.y * norm.y + norm.z * norm.z));
}, "J.util.V3,~N,J.util.P3");
$_M(c$, "createTopoMap", 
function (bsAromatic) {
if (bsAromatic == null) bsAromatic =  new J.util.BS ();
var nAtomsMissing = this.getMissingHydrogenCount ();
var atoms =  new Array (this.atomCount + nAtomsMissing);
this.jmolAtoms = atoms;
var ptAtom = 0;
var bsFixH =  new J.util.BS ();
for (var i = 0; i < this.atomCount; i++) {
var sAtom = this.patternAtoms[i];
var cclass = sAtom.getChiralClass ();
var n = sAtom.missingHydrogenCount;
if (n < 0) n = 0;
var atom = atoms[ptAtom] =  new J.smiles.SmilesAtom ().setAll (0, ptAtom, cclass == -2147483648 ? cclass : (cclass << 8) + sAtom.getChiralOrder (), sAtom.elementNumber, sAtom.getCharge ());
atom.atomName = sAtom.atomName;
atom.residueName = sAtom.residueName;
atom.residueChar = sAtom.residueChar;
atom.isBioAtom = sAtom.isBioAtom;
atom.$isLeadAtom = sAtom.$isLeadAtom;
atom.setAtomicMass (sAtom.getAtomicMass ());
if (sAtom.isAromatic ()) bsAromatic.set (ptAtom);
if (!sAtom.isFirst && n == 1 && cclass > 0) bsFixH.set (ptAtom);
sAtom.setMatchingAtom (ptAtom++);
var bonds =  new Array (sAtom.getBondCount () + n);
atom.setBonds (bonds);
while (--n >= 0) {
var atomH = atoms[ptAtom] =  new J.smiles.SmilesAtom ().setAll (0, ptAtom, 0, 1, 0);
ptAtom++;
atomH.setBonds ( new Array (1));
var b =  new J.smiles.SmilesBond (atom, atomH, 1, false);
J.util.Logger.info ("" + b);
}
}
for (var i = 0; i < this.atomCount; i++) {
var sAtom = this.patternAtoms[i];
var i1 = sAtom.getMatchingAtom ();
var atom1 = atoms[i1];
var n = sAtom.getBondCount ();
for (var j = 0; j < n; j++) {
var sBond = sAtom.getBond (j);
var firstAtom = (sBond.getAtom1 () === sAtom);
if (firstAtom) {
var order = 1;
switch (sBond.order) {
case 769:
order = 33;
break;
case 1025:
order = 97;
break;
case 257:
order = 1025;
break;
case 513:
order = 1041;
break;
case 112:
case 96:
order = sBond.order;
break;
case 1:
order = 1;
break;
case 17:
order = 514;
break;
case 2:
order = 2;
break;
case 3:
order = 3;
break;
}
var atom2 = atoms[sBond.getAtom2 ().getMatchingAtom ()];
var b =  new J.smiles.SmilesBond (atom1, atom2, order, false);
atom2.bondCount--;
J.util.Logger.info ("" + b);
} else {
var atom2 = atoms[sBond.getAtom1 ().getMatchingAtom ()];
var b = atom2.getBondTo (atom1);
atom1.addBond (b);
}}
}
for (var i = bsFixH.nextSetBit (0); i >= 0; i = bsFixH.nextSetBit (i + 1)) {
var bonds = atoms[i].getEdges ();
var b = bonds[0];
bonds[0] = bonds[1];
bonds[1] = b;
}
}, "J.util.BS");
$_M(c$, "setTop", 
function (parent) {
if (parent == null) this.top = this;
 else this.top = parent.getTop ();
}, "J.smiles.SmilesSearch");
$_M(c$, "getTop", 
function () {
return (this.top === this ? this : this.top.getTop ());
});
$_M(c$, "getSelections", 
function () {
var ht = this.top.htNested;
if (ht == null || this.jmolAtoms.length == 0) return;
var htNew =  new java.util.Hashtable ();
for (var entry, $entry = ht.entrySet ().iterator (); $entry.hasNext () && ((entry = $entry.next ()) || true);) {
var key = entry.getValue ().toString ();
if (key.startsWith ("select")) {
var bs = (htNew.containsKey (key) ? htNew.get (key) : this.jmolAtoms[0].findAtomsLike (key.substring (6)));
if (bs == null) bs =  new J.util.BS ();
htNew.put (key, bs);
entry.setValue (bs);
}}
});
Clazz.pu$h ();
c$ = Clazz.decorateAsClass (function () {
this.vTemp = null;
this.vA = null;
this.vB = null;
this.vTemp1 = null;
this.vTemp2 = null;
this.vNorm1 = null;
this.vNorm2 = null;
this.vNorm3 = null;
this.bsTemp = null;
Clazz.instantialize (this, arguments);
}, J.smiles.SmilesSearch, "VTemp");
Clazz.prepareFields (c$, function () {
this.vTemp =  new J.util.V3 ();
this.vA =  new J.util.V3 ();
this.vB =  new J.util.V3 ();
this.vTemp1 =  new J.util.V3 ();
this.vTemp2 =  new J.util.V3 ();
this.vNorm1 =  new J.util.V3 ();
this.vNorm2 =  new J.util.V3 ();
this.vNorm3 =  new J.util.V3 ();
this.bsTemp =  new J.util.BS ();
});
c$ = Clazz.p0p ();
Clazz.defineStatics (c$,
"INITIAL_ATOMS", 16);
});
Clazz.declarePackage ("J.smiles");
Clazz.load (["java.util.Hashtable", "J.smiles.SmilesSearch", "J.util.BS"], "J.smiles.SmilesGenerator", ["J.smiles.InvalidSmilesException", "$.SmilesAromatic", "$.SmilesAtom", "$.SmilesBond", "$.SmilesParser", "J.util.BSUtil", "$.Elements", "$.JmolList", "$.JmolMolecule", "$.Logger", "$.SB"], function () {
c$ = Clazz.decorateAsClass (function () {
this.atoms = null;
this.atomCount = 0;
this.bsSelected = null;
this.bsAromatic = null;
this.ringSets = null;
this.vTemp = null;
this.nPairs = 0;
this.bsBondsUp = null;
this.bsBondsDn = null;
this.bsToDo = null;
this.prevAtom = null;
this.prevSp2Atoms = null;
this.htRingsSequence = null;
this.htRings = null;
this.bsIncludingH = null;
Clazz.instantialize (this, arguments);
}, J.smiles, "SmilesGenerator");
Clazz.prepareFields (c$, function () {
this.vTemp =  new J.smiles.SmilesSearch.VTemp ();
this.bsBondsUp =  new J.util.BS ();
this.bsBondsDn =  new J.util.BS ();
this.htRingsSequence =  new java.util.Hashtable ();
this.htRings =  new java.util.Hashtable ();
});
$_M(c$, "getSmiles", 
function (atoms, atomCount, bsSelected) {
var i = bsSelected.nextSetBit (0);
if (i < 0) return "";
this.atoms = atoms;
this.atomCount = atomCount;
this.bsSelected = bsSelected = J.util.BSUtil.copy (bsSelected);
return this.getSmilesComponent (atoms[i], bsSelected, false);
}, "~A,~N,J.util.BS");
$_M(c$, "getBioSmiles", 
function (atoms, atomCount, bsSelected, allowUnmatchedRings, addCrossLinks, comment) {
this.atoms = atoms;
this.atomCount = atomCount;
var sb =  new J.util.SB ();
var bs = J.util.BSUtil.copy (bsSelected);
if (comment != null) sb.append ("//* Jmol bioSMILES ").append (comment.$replace ('*', '_')).append (" *//");
var end = "\n";
var bsIgnore =  new J.util.BS ();
var lastComponent = null;
var s;
var vLinks =  new J.util.JmolList ();
try {
var len = 0;
for (var i = bs.nextSetBit (0); i >= 0; i = bs.nextSetBit (i + 1)) {
var a = atoms[i];
var ch = a.getGroup1 ('?');
var bioStructureName = a.getBioStructureTypeName ();
var unknown = (ch.equals ("?"));
if (end != null) {
if (sb.length () > 0) sb.append (end);
end = null;
len = 0;
if (bioStructureName.length > 0) {
var id = a.getChainID ();
if (id != 0) {
s = "//* chain " + a.getChainIDStr () + " " + bioStructureName + " " + a.getResno () + " *// ";
len = s.length;
sb.append (s);
}sb.append ("~").appendC (bioStructureName.charAt (0)).append ("~");
len++;
} else {
s = this.getSmilesComponent (a, bs, true);
if (s.equals (lastComponent)) {
end = "";
} else {
lastComponent = s;
var groupName = a.getGroup3 (true);
if (groupName != null) sb.append ("//* ").append (groupName).append (" *//");
sb.append (s);
end = ".\n";
}continue;
}}if (len >= 75) {
sb.append ("\n  ");
len = 2;
}if (unknown) {
this.addBracketedBioName (sb, a, bioStructureName.length > 0 ? ".0" : null);
} else {
sb.append (ch);
}len++;
var i0 = a.getOffsetResidueAtom ("0", 0);
if (addCrossLinks) {
a.getCrossLinkLeadAtomIndexes (vLinks);
for (var j = 0; j < vLinks.size (); j++) {
sb.append (":");
s = this.getRingCache (i0, vLinks.get (j).intValue (), this.htRingsSequence);
sb.append (s);
len += 1 + s.length;
}
vLinks.clear ();
}a.getGroupBits (bsIgnore);
bs.andNot (bsIgnore);
var i2 = a.getOffsetResidueAtom ("0", 1);
if (i2 < 0 || !bs.get (i2)) {
sb.append (" //* ").appendI (a.getResno ()).append (" *//");
if (i2 < 0 && (i2 = bs.nextSetBit (i + 1)) < 0) break;
if (len > 0) end = ".\n";
}i = i2 - 1;
}
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
System.out.println (e.toString ());
return "";
} else {
throw e;
}
}
if (!allowUnmatchedRings && !this.htRingsSequence.isEmpty ()) {
this.dumpRingKeys (sb, this.htRingsSequence);
throw  new J.smiles.InvalidSmilesException ("//* ?ring error? *//");
}s = sb.toString ();
if (s.endsWith (".\n")) s = s.substring (0, s.length - 2);
return s;
}, "~A,~N,J.util.BS,~B,~B,~S");
$_M(c$, "addBracketedBioName", 
($fz = function (sb, a, atomName) {
sb.append ("[");
if (atomName != null) {
var chain = a.getChainIDStr ();
sb.append (a.getGroup3 (false));
if (!atomName.equals (".0")) sb.append (atomName).append ("#").appendI (a.getElementNumber ());
sb.append ("//* ").appendI (a.getResno ());
if (chain.length > 0) sb.append (":").append (chain);
sb.append (" *//");
} else {
sb.append (J.util.Elements.elementNameFromNumber (a.getElementNumber ()));
}sb.append ("]");
}, $fz.isPrivate = true, $fz), "J.util.SB,J.util.JmolNode,~S");
$_M(c$, "getSmilesComponent", 
($fz = function (atom, bs, allowConnectionsToOutsideWorld) {
if (atom.getElementNumber () == 1 && atom.getEdges ().length > 0) atom = this.atoms[atom.getBondedAtomIndex (0)];
this.bsSelected = J.util.JmolMolecule.getBranchBitSet (this.atoms, atom.getIndex (), J.util.BSUtil.copy (bs), null, -1, true, false);
bs.andNot (this.bsSelected);
this.bsIncludingH = J.util.BSUtil.copy (this.bsSelected);
for (var j = this.bsSelected.nextSetBit (0); j >= 0; j = this.bsSelected.nextSetBit (j + 1)) {
var a = this.atoms[j];
if (a.getElementNumber () == 1 && a.getIsotopeNumber () == 0) this.bsSelected.clear (j);
}
if (this.bsSelected.cardinality () > 2) {
var search = null;
search = J.smiles.SmilesParser.getMolecule ("A[=&@]A", true);
search.jmolAtoms = this.atoms;
search.setSelected (this.bsSelected);
search.jmolAtomCount = this.atomCount;
search.ringDataMax = 7;
search.setRingData (null);
this.bsAromatic = search.bsAromatic;
this.ringSets = search.ringSets;
this.setBondDirections ();
} else {
this.bsAromatic =  new J.util.BS ();
}this.bsToDo = J.util.BSUtil.copy (this.bsSelected);
var sb =  new J.util.SB ();
for (var i = this.bsToDo.nextSetBit (0); i >= 0; i = this.bsToDo.nextSetBit (i + 1)) if (this.atoms[i].getCovalentBondCount () > 4) {
this.getSmiles (sb, this.atoms[i], allowConnectionsToOutsideWorld, false);
atom = null;
}
if (atom != null) while ((atom = this.getSmiles (sb, atom, allowConnectionsToOutsideWorld, true)) != null) {
}
while (this.bsToDo.cardinality () > 0 || !this.htRings.isEmpty ()) {
var e = this.htRings.values ().iterator ();
if (e.hasNext ()) {
atom = this.atoms[(e.next ()[1]).intValue ()];
if (!this.bsToDo.get (atom.getIndex ())) break;
} else {
atom = this.atoms[this.bsToDo.nextSetBit (0)];
}sb.append (".");
this.prevSp2Atoms = null;
this.prevAtom = null;
while ((atom = this.getSmiles (sb, atom, allowConnectionsToOutsideWorld, true)) != null) {
}
}
if (!this.htRings.isEmpty ()) {
this.dumpRingKeys (sb, this.htRings);
throw  new J.smiles.InvalidSmilesException ("//* ?ring error? *//\n" + sb);
}return sb.toString ();
}, $fz.isPrivate = true, $fz), "J.util.JmolNode,J.util.BS,~B");
$_M(c$, "getBondStereochemistry", 
($fz = function (bond, atomFrom) {
if (bond == null) return '\0';
var i = bond.index;
var isFirst = (atomFrom == null || bond.getAtomIndex1 () == atomFrom.getIndex ());
return (this.bsBondsUp.get (i) ? (isFirst ? '/' : '\\') : this.bsBondsDn.get (i) ? (isFirst ? '\\' : '/') : '\0');
}, $fz.isPrivate = true, $fz), "J.util.JmolEdge,J.util.JmolNode");
$_M(c$, "setBondDirections", 
($fz = function () {
var bsDone =  new J.util.BS ();
var edges =  Clazz.newArray (2, 3, null);
for (var i = this.bsSelected.nextSetBit (0); i >= 0; i = this.bsSelected.nextSetBit (i + 1)) {
var atom1 = this.atoms[i];
var bonds = atom1.getEdges ();
for (var k = 0; k < bonds.length; k++) {
var bond = bonds[k];
var index = bond.index;
if (bsDone.get (index)) continue;
var atom2 = bond.getOtherAtomNode (atom1);
if (bond.getCovalentOrder () != 2 || J.smiles.SmilesSearch.isRingBond (this.ringSets, i, atom2.getIndex ())) continue;
bsDone.set (index);
var b0 = null;
var a0 = null;
var i0 = 0;
var atom12 = [atom1, atom2];
if (J.util.Logger.debugging) J.util.Logger.debug (atom1 + " == " + atom2);
var edgeCount = 1;
for (var j = 0; j < 2 && edgeCount > 0 && edgeCount < 3; j++) {
edgeCount = 0;
var atomA = atom12[j];
var bb = atomA.getEdges ();
for (var b = 0; b < bb.length; b++) {
if (bb[b].getCovalentOrder () != 1) continue;
edges[j][edgeCount++] = bb[b];
if (this.getBondStereochemistry (bb[b], atomA) != '\0') {
b0 = bb[b];
i0 = j;
}}
}
if (edgeCount == 3 || edgeCount == 0) continue;
if (b0 == null) {
i0 = 0;
b0 = edges[i0][0];
this.bsBondsUp.set (b0.index);
}var c0 = this.getBondStereochemistry (b0, atom12[i0]);
a0 = b0.getOtherAtomNode (atom12[i0]);
if (a0 == null) continue;
for (var j = 0; j < 2; j++) for (var jj = 0; jj < 2; jj++) {
var b1 = edges[j][jj];
if (b1 == null || b1 === b0) continue;
var bi = b1.index;
var a1 = b1.getOtherAtomNode (atom12[j]);
if (a1 == null) continue;
var c1 = this.getBondStereochemistry (b1, atom12[j]);
var isOpposite = J.smiles.SmilesSearch.isDiaxial (atom12[i0], atom12[j], a0, a1, this.vTemp, 0);
if (c1 == '\0' || (c1 != c0) == isOpposite) {
var isUp = (c0 == '\\' && isOpposite || c0 == '/' && !isOpposite);
if (isUp == (b1.getAtomIndex1 () != a1.getIndex ())) this.bsBondsUp.set (bi);
 else this.bsBondsDn.set (bi);
} else {
J.util.Logger.error ("BOND STEREOCHEMISTRY ERROR");
}if (J.util.Logger.debugging) J.util.Logger.debug (this.getBondStereochemistry (b0, atom12[0]) + " " + a0.getIndex () + " " + a1.getIndex () + " " + this.getBondStereochemistry (b1, atom12[j]));
}

}
}
}, $fz.isPrivate = true, $fz));
$_M(c$, "getSmiles", 
($fz = function (sb, atom, allowConnectionsToOutsideWorld, allowBranches) {
var atomIndex = atom.getIndex ();
if (!this.bsToDo.get (atomIndex)) return null;
this.bsToDo.clear (atomIndex);
var isExtension = (!this.bsSelected.get (atomIndex));
var prevIndex = (this.prevAtom == null ? -1 : this.prevAtom.getIndex ());
var isAromatic = this.bsAromatic.get (atomIndex);
var havePreviousSp2Atoms = (this.prevSp2Atoms != null);
var sp2Atoms = this.prevSp2Atoms;
var nSp2Atoms = 0;
var atomicNumber = atom.getElementNumber ();
var nH = 0;
var v =  new J.util.JmolList ();
var bond0 = null;
var bondPrev = null;
var bonds = atom.getEdges ();
var aH = null;
var stereoFlag = (isAromatic ? 10 : 0);
var stereo =  new Array (7);
if (J.util.Logger.debugging) J.util.Logger.debug (sb.toString ());
if (bonds != null) for (var i = bonds.length; --i >= 0; ) {
var bond = bonds[i];
if (!bond.isCovalent ()) continue;
var atom1 = bonds[i].getOtherAtomNode (atom);
var index1 = atom1.getIndex ();
if (index1 == prevIndex) {
bondPrev = bonds[i];
continue;
}var isH = (atom1.getElementNumber () == 1 && atom1.getIsotopeNumber () == 0);
if (!this.bsIncludingH.get (index1)) {
if (!isH && allowConnectionsToOutsideWorld && this.bsSelected.get (atomIndex)) this.bsToDo.set (index1);
 else continue;
}if (isH) {
aH = atom1;
nH++;
if (nH > 1) stereoFlag = 10;
} else {
v.addLast (bonds[i]);
}}
var strBond = null;
if (sp2Atoms == null) sp2Atoms =  new Array (5);
if (bondPrev != null) {
strBond = J.smiles.SmilesBond.getBondOrderString (bondPrev.getCovalentOrder ());
if (this.prevSp2Atoms == null) sp2Atoms[nSp2Atoms++] = this.prevAtom;
 else nSp2Atoms = 2;
}nSp2Atoms += nH;
var nMax = 0;
var bsBranches =  new J.util.BS ();
if (allowBranches) for (var i = 0; i < v.size (); i++) {
var bond = v.get (i);
var a = bond.getOtherAtomNode (atom);
var n = a.getCovalentBondCount () - a.getCovalentHydrogenCount ();
var order = bond.getCovalentOrder ();
if (order == 1 && n == 1 && i < v.size () - (bond0 == null ? 1 : 0)) {
bsBranches.set (bond.index);
} else if ((order > 1 || n > nMax) && !this.htRings.containsKey (J.smiles.SmilesGenerator.getRingKey (a.getIndex (), atomIndex))) {
nMax = (order > 1 ? 1000 + order : n);
bond0 = bond;
}}
var atomNext = (bond0 == null ? null : bond0.getOtherAtomNode (atom));
var orderNext = (bond0 == null ? 0 : bond0.getCovalentOrder ());
if (stereoFlag < 7 && bondPrev != null) {
if (bondPrev.getCovalentOrder () == 2 && orderNext == 2 && this.prevSp2Atoms != null && this.prevSp2Atoms[1] != null) {
stereo[stereoFlag++] = this.prevSp2Atoms[0];
stereo[stereoFlag++] = this.prevSp2Atoms[1];
} else {
stereo[stereoFlag++] = this.prevAtom;
}}if (stereoFlag < 7 && nH == 1) stereo[stereoFlag++] = aH;
var deferStereo = (orderNext == 1 && this.prevSp2Atoms == null);
var chBond = this.getBondStereochemistry (bondPrev, this.prevAtom);
var sMore =  new J.util.SB ();
for (var i = 0; i < v.size (); i++) {
var bond = v.get (i);
if (!bsBranches.get (bond.index)) continue;
var a = bond.getOtherAtomNode (atom);
var s2 =  new J.util.SB ();
s2.append ("(");
this.prevAtom = atom;
this.prevSp2Atoms = null;
var bond0t = bond0;
this.getSmiles (s2, a, allowConnectionsToOutsideWorld, allowBranches);
bond0 = bond0t;
s2.append (")");
if (sMore.indexOf (s2.toString ()) >= 0) stereoFlag = 10;
sMore.appendSB (s2);
v.remove (i--);
if (stereoFlag < 7) stereo[stereoFlag++] = a;
if (nSp2Atoms < 5) sp2Atoms[nSp2Atoms++] = a;
}
var index2 = (orderNext == 2 ? atomNext.getIndex () : -1);
if (nH > 1 || isAromatic || index2 < 0 || J.smiles.SmilesSearch.isRingBond (this.ringSets, atomIndex, index2)) {
nSp2Atoms = -1;
}if (nSp2Atoms < 0) sp2Atoms = null;
if (strBond != null || chBond != '\0') {
if (chBond != '\0') strBond = "" + chBond;
sb.append (strBond);
}var atat = null;
if (!allowBranches && (v.size () == 5 || v.size () == 6)) atat = this.sortInorganic (atom, v);
for (var i = 0; i < v.size (); i++) {
var bond = v.get (i);
if (bond === bond0) continue;
var a = bond.getOtherAtomNode (atom);
var s = this.getRingCache (atomIndex, a.getIndex (), this.htRings);
strBond = J.smiles.SmilesBond.getBondOrderString (bond.order);
if (!deferStereo) {
chBond = this.getBondStereochemistry (bond, atom);
if (chBond != '\0') strBond = "" + chBond;
}sMore.append (strBond);
sMore.append (s);
if (stereoFlag < 7) stereo[stereoFlag++] = a;
if (sp2Atoms != null && nSp2Atoms < 5) sp2Atoms[nSp2Atoms++] = a;
}
if (havePreviousSp2Atoms && stereoFlag == 2 && orderNext == 2 && atomNext.getCovalentBondCount () == 3) {
bonds = atomNext.getEdges ();
for (var k = 0; k < bonds.length; k++) {
if (bonds[k].isCovalent () && atomNext.getBondedAtomIndex (k) != atomIndex) stereo[stereoFlag++] = this.atoms[atomNext.getBondedAtomIndex (k)];
}
nSp2Atoms = 0;
} else if (atomNext != null && stereoFlag < 7) {
stereo[stereoFlag++] = atomNext;
}var valence = atom.getValence ();
var charge = atom.getFormalCharge ();
var isotope = atom.getIsotopeNumber ();
var atomName = atom.getAtomName ();
var groupType = atom.getBioStructureTypeName ();
if (J.util.Logger.debugging) sb.append ("\n//* " + atom + " *//\t");
if (isExtension && groupType.length != 0 && atomName.length != 0) this.addBracketedBioName (sb, atom, "." + atomName);
 else sb.append (J.smiles.SmilesAtom.getAtomLabel (atomicNumber, isotope, valence, charge, nH, isAromatic, atat != null ? atat : this.checkStereoPairs (atom, atomIndex, stereo, stereoFlag)));
sb.appendSB (sMore);
if (bond0 == null) return null;
if (orderNext == 2 && (nSp2Atoms == 1 || nSp2Atoms == 2)) {
if (sp2Atoms[0] == null) sp2Atoms[0] = atom;
if (sp2Atoms[1] == null) sp2Atoms[1] = atom;
} else {
sp2Atoms = null;
nSp2Atoms = 0;
}this.prevSp2Atoms = sp2Atoms;
this.prevAtom = atom;
return atomNext;
}, $fz.isPrivate = true, $fz), "J.util.SB,J.util.JmolNode,~B,~B");
$_M(c$, "sortInorganic", 
($fz = function (atom, v) {
var atomIndex = atom.getIndex ();
var n = v.size ();
var axialPairs =  new J.util.JmolList ();
var bonds =  new J.util.JmolList ();
var a1;
var a2;
var bond1;
var bond2;
var bsDone =  new J.util.BS ();
var pair0 = null;
var stereo =  new Array (6);
var isOK = true;
var s = "";
for (var i = 0; i < n; i++) {
bond1 = v.get (i);
stereo[0] = a1 = bond1.getOtherAtomNode (atom);
if (i == 0) s = this.addStereoCheck (atomIndex, stereo, 0, "");
 else if (isOK && this.addStereoCheck (atomIndex, stereo, 0, s) != null) isOK = false;
if (bsDone.get (i)) continue;
bsDone.set (i);
var isAxial = false;
for (var j = i + 1; j < n; j++) {
if (bsDone.get (j)) continue;
bond2 = v.get (j);
a2 = bond2.getOtherAtomNode (atom);
if (J.smiles.SmilesSearch.isDiaxial (atom, atom, a1, a2, this.vTemp, -0.95)) {
axialPairs.addLast ([bond1, bond2]);
isAxial = true;
bsDone.set (j);
break;
}}
if (!isAxial) bonds.addLast (bond1);
}
var nPairs = axialPairs.size ();
if (isOK || n == 6 && nPairs != 3 || n == 5 && nPairs == 0) return "";
pair0 = axialPairs.get (0);
bond1 = pair0[0];
stereo[0] = bond1.getOtherAtomNode (atom);
v.clear ();
v.addLast (bond1);
if (nPairs > 1) bonds.addLast (axialPairs.get (1)[0]);
if (nPairs == 3) bonds.addLast (axialPairs.get (2)[0]);
if (nPairs > 1) bonds.addLast (axialPairs.get (1)[1]);
if (nPairs == 3) bonds.addLast (axialPairs.get (2)[1]);
for (var i = 0; i < bonds.size (); i++) {
bond1 = bonds.get (i);
v.addLast (bond1);
stereo[i + 1] = bond1.getOtherAtomNode (atom);
}
v.addLast (pair0[1]);
return J.smiles.SmilesGenerator.getStereoFlag (atom, stereo, n, this.vTemp);
}, $fz.isPrivate = true, $fz), "J.util.JmolNode,J.util.JmolList");
$_M(c$, "checkStereoPairs", 
($fz = function (atom, atomIndex, stereo, stereoFlag) {
if (stereoFlag < 4) return "";
if (stereoFlag == 4 && (atom.getElementNumber ()) == 6) {
var s = "";
for (var i = 0; i < 4; i++) if ((s = this.addStereoCheck (atomIndex, stereo, i, s)) == null) {
stereoFlag = 10;
break;
}
}return (stereoFlag > 6 ? "" : J.smiles.SmilesGenerator.getStereoFlag (atom, stereo, stereoFlag, this.vTemp));
}, $fz.isPrivate = true, $fz), "J.util.JmolNode,~N,~A,~N");
c$.getStereoFlag = $_M(c$, "getStereoFlag", 
($fz = function (atom0, atoms, nAtoms, v) {
var atom1 = atoms[0];
var atom2 = atoms[1];
var atom3 = atoms[2];
var atom4 = atoms[3];
var atom5 = atoms[4];
var atom6 = atoms[5];
var chiralClass = 4;
switch (nAtoms) {
default:
case 5:
case 6:
return (J.smiles.SmilesSearch.checkStereochemistryAll (false, atom0, chiralClass, 1, atom1, atom2, atom3, atom4, atom5, atom6, v) ? "@" : "@@");
case 2:
case 4:
if (atom3 == null || atom4 == null) return "";
var d = J.smiles.SmilesAromatic.getNormalThroughPoints (atom1, atom2, atom3, v.vTemp, v.vA, v.vB);
if (Math.abs (J.smiles.SmilesSearch.distanceToPlane (v.vTemp, d, atom4)) < 0.2) {
chiralClass = 8;
if (J.smiles.SmilesSearch.checkStereochemistryAll (false, atom0, chiralClass, 1, atom1, atom2, atom3, atom4, atom5, atom6, v)) return "@SP1";
if (J.smiles.SmilesSearch.checkStereochemistryAll (false, atom0, chiralClass, 2, atom1, atom2, atom3, atom4, atom5, atom6, v)) return "@SP2";
if (J.smiles.SmilesSearch.checkStereochemistryAll (false, atom0, chiralClass, 3, atom1, atom2, atom3, atom4, atom5, atom6, v)) return "@SP3";
} else {
return (J.smiles.SmilesSearch.checkStereochemistryAll (false, atom0, chiralClass, 1, atom1, atom2, atom3, atom4, atom5, atom6, v) ? "@" : "@@");
}}
return "";
}, $fz.isPrivate = true, $fz), "J.util.JmolNode,~A,~N,J.smiles.SmilesSearch.VTemp");
$_M(c$, "addStereoCheck", 
($fz = function (atomIndex, stereo, i, s) {
var n = stereo[i].getAtomicAndIsotopeNumber ();
var nx = stereo[i].getCovalentBondCount ();
var nh = (n == 6 ? stereo[i].getCovalentHydrogenCount () : 0);
if (n == 6 ? nx != 4 || nh != 3 : nx > 1) return s;
var sa = ";" + n + "/" + nh + "/" + nx + ",";
if (s.indexOf (sa) >= 0) {
if (nh == 3) {
var ndt = 0;
for (var j = 0; j < nx && ndt < 3; j++) {
var ia = stereo[i].getBondedAtomIndex (j);
if (ia == atomIndex) continue;
ndt += this.atoms[ia].getAtomicAndIsotopeNumber ();
}
if (ndt > 3) return s;
}return null;
}return s + sa;
}, $fz.isPrivate = true, $fz), "~N,~A,~N,~S");
$_M(c$, "getRingCache", 
($fz = function (i0, i1, ht) {
var key = J.smiles.SmilesGenerator.getRingKey (i0, i1);
var o = ht.get (key);
var s = (o == null ? null : o[0]);
if (s == null) {
ht.put (key, [s = J.smiles.SmilesParser.getRingPointer (++this.nPairs), Integer.$valueOf (i1)]);
if (J.util.Logger.debugging) J.util.Logger.debug ("adding for " + i0 + " ring key " + this.nPairs + ": " + key);
} else {
ht.remove (key);
if (J.util.Logger.debugging) J.util.Logger.debug ("using ring key " + key);
}return s;
}, $fz.isPrivate = true, $fz), "~N,~N,java.util.Map");
$_M(c$, "dumpRingKeys", 
($fz = function (sb, ht) {
J.util.Logger.info (sb.toString () + "\n\n");
for (var key, $key = ht.keySet ().iterator (); $key.hasNext () && ((key = $key.next ()) || true);) J.util.Logger.info ("unmatched ring key: " + key);

}, $fz.isPrivate = true, $fz), "J.util.SB,java.util.Map");
c$.getRingKey = $_M(c$, "getRingKey", 
function (i0, i1) {
return Math.min (i0, i1) + "_" + Math.max (i0, i1);
}, "~N,~N");
});
Clazz.declarePackage ("J.smiles");
Clazz.load (null, "J.smiles.SmilesAromatic", ["J.util.BS", "$.V3"], function () {
c$ = Clazz.declareType (J.smiles, "SmilesAromatic");
c$.isFlatSp2Ring = $_M(c$, "isFlatSp2Ring", 
function (atoms, bsSelected, bs, cutoff) {
for (var i = bs.nextSetBit (0); i >= 0; i = bs.nextSetBit (i + 1)) {
var ringAtom = atoms[i];
var bonds = ringAtom.getEdges ();
if (bonds.length < 3) continue;
if (bonds.length > 3) return false;
}
if (cutoff == 3.4028235E38) return true;
if (cutoff <= 0) cutoff = 0.01;
var vTemp =  new J.util.V3 ();
var vA =  new J.util.V3 ();
var vB =  new J.util.V3 ();
var vMean = null;
var nPoints = bs.cardinality ();
var vNorms =  new Array (nPoints * 2);
var nNorms = 0;
var maxDev = (1 - cutoff * 5);
for (var i = bs.nextSetBit (0); i >= 0; i = bs.nextSetBit (i + 1)) {
var ringAtom = atoms[i];
var bonds = ringAtom.getEdges ();
var iSub = -1;
var r1 = -1;
var r2 = -1;
for (var k = bonds.length; --k >= 0; ) {
var iAtom = ringAtom.getBondedAtomIndex (k);
if (!bsSelected.get (iAtom)) continue;
if (!bs.get (iAtom)) iSub = iAtom;
 else if (r1 < 0) r1 = iAtom;
 else r2 = iAtom;
}
J.smiles.SmilesAromatic.getNormalThroughPoints (atoms[r1], atoms[i], atoms[r2], vTemp, vA, vB);
if (vMean == null) vMean =  new J.util.V3 ();
if (!J.smiles.SmilesAromatic.addNormal (vTemp, vMean, maxDev)) return false;
vNorms[nNorms++] = J.util.V3.newV (vTemp);
if (iSub >= 0) {
J.smiles.SmilesAromatic.getNormalThroughPoints (atoms[r1], atoms[iSub], atoms[r2], vTemp, vA, vB);
if (!J.smiles.SmilesAromatic.addNormal (vTemp, vMean, maxDev)) return false;
vNorms[nNorms++] = J.util.V3.newV (vTemp);
}}
var isFlat = J.smiles.SmilesAromatic.checkStandardDeviation (vNorms, vMean, nNorms, cutoff);
return isFlat;
}, "~A,J.util.BS,J.util.BS,~N");
c$.addNormal = $_M(c$, "addNormal", 
($fz = function (vTemp, vMean, maxDev) {
var similarity = vMean.dot (vTemp);
if (similarity != 0 && Math.abs (similarity) < maxDev) return false;
if (similarity < 0) vTemp.scale (-1);
vMean.add (vTemp);
vMean.normalize ();
return true;
}, $fz.isPrivate = true, $fz), "J.util.V3,J.util.V3,~N");
c$.checkStandardDeviation = $_M(c$, "checkStandardDeviation", 
($fz = function (vNorms, vMean, n, cutoff) {
var sum = 0;
var sum2 = 0;
for (var i = 0; i < n; i++) {
var v = vNorms[i].dot (vMean);
sum += v;
sum2 += (v) * v;
}
sum = Math.sqrt ((sum2 - sum * sum / n) / (n - 1));
return (sum < cutoff);
}, $fz.isPrivate = true, $fz), "~A,J.util.V3,~N,~N");
c$.getNormalThroughPoints = $_M(c$, "getNormalThroughPoints", 
function (pointA, pointB, pointC, vNorm, vAB, vAC) {
vAB.sub2 (pointB, pointA);
vAC.sub2 (pointC, pointA);
vNorm.cross (vAB, vAC);
vNorm.normalize ();
vAB.setT (pointA);
return -vAB.dot (vNorm);
}, "J.util.JmolNode,J.util.JmolNode,J.util.JmolNode,J.util.V3,J.util.V3,J.util.V3");
c$.checkAromaticDefined = $_M(c$, "checkAromaticDefined", 
function (jmolAtoms, bsAtoms) {
var bsDefined =  new J.util.BS ();
for (var i = bsAtoms.nextSetBit (0); i >= 0; i = bsAtoms.nextSetBit (i + 1)) {
var bonds = jmolAtoms[i].getEdges ();
for (var j = 0; j < bonds.length; j++) {
switch (bonds[j].order) {
case 515:
case 514:
case 513:
bsDefined.set (bonds[j].getAtomIndex1 ());
bsDefined.set (bonds[j].getAtomIndex2 ());
}
}
}
return bsDefined;
}, "~A,J.util.BS");
c$.checkAromaticStrict = $_M(c$, "checkAromaticStrict", 
function (jmolAtoms, bsAromatic, v5, v6) {
var bsStrict =  new J.util.BS ();
var bsTest =  new J.util.BS ();
for (var i = v5.size (); --i >= 0; ) {
var bs = v5.get (i);
if (J.smiles.SmilesAromatic.isAromaticRing (bsAromatic, bsTest, bs, 5)) J.smiles.SmilesAromatic.checkAromaticStrict2 (jmolAtoms, bsStrict, v5, v6, bs, true);
}
for (var i = v6.size (); --i >= 0; ) {
var bs = v6.get (i);
if (J.smiles.SmilesAromatic.isAromaticRing (bsAromatic, bsTest, bs, 6)) J.smiles.SmilesAromatic.checkAromaticStrict2 (jmolAtoms, bsStrict, v5, v6, bs, false);
}
bsAromatic.clearAll ();
bsAromatic.or (bsStrict);
}, "~A,J.util.BS,J.util.JmolList,J.util.JmolList");
c$.isAromaticRing = $_M(c$, "isAromaticRing", 
($fz = function (bsAromatic, bsTest, bs, n) {
bsTest.clearAll ();
bsTest.or (bs);
bsTest.and (bsAromatic);
return (bsTest.cardinality () == n);
}, $fz.isPrivate = true, $fz), "J.util.BS,J.util.BS,J.util.BS,~N");
c$.checkAromaticStrict2 = $_M(c$, "checkAromaticStrict2", 
($fz = function (jmolAtoms, bsStrict, v5, v6, bsRing, is5) {
var piElectronCount = J.smiles.SmilesAromatic.countInternalPairs (jmolAtoms, bsRing, is5) << 1;
switch (piElectronCount) {
case -3:
break;
default:
for (var i = bsRing.nextSetBit (0); i >= 0; i = bsRing.nextSetBit (i + 1)) {
var bonds = jmolAtoms[i].getEdges ();
for (var j = 0; j < bonds.length; j++) if (bonds[j].order == 2) {
var i2 = bonds[j].getOtherAtomNode (jmolAtoms[i]).getIndex ();
if (!bsRing.get (i2)) {
var piShared = false;
for (var k = v5.size (); --k >= 0 && !piShared; ) {
var bs = v5.get (k);
if (bs.get (i2) && (bsStrict.get (i2) || Math.abs (J.smiles.SmilesAromatic.countInternalPairs (jmolAtoms, bs, true)) == 3)) piShared = true;
}
for (var k = v6.size (); --k >= 0 && !piShared; ) {
var bs = v6.get (k);
if (bs.get (i2) && (bsStrict.get (i2) || Math.abs (J.smiles.SmilesAromatic.countInternalPairs (jmolAtoms, bs, false)) == 3)) piShared = true;
}
if (!piShared) return;
piElectronCount++;
}}
}
break;
}
if (piElectronCount == 6) bsStrict.or (bsRing);
}, $fz.isPrivate = true, $fz), "~A,J.util.BS,J.util.JmolList,J.util.JmolList,J.util.BS,~B");
c$.countInternalPairs = $_M(c$, "countInternalPairs", 
($fz = function (jmolAtoms, bsRing, is5) {
var nDouble = 0;
var nAromatic = 0;
var nLonePairs = 0;
for (var i = bsRing.nextSetBit (0); i >= 0; i = bsRing.nextSetBit (i + 1)) {
var atom = jmolAtoms[i];
var bonds = atom.getEdges ();
var haveDouble = false;
for (var k = 0; k < bonds.length; k++) {
var j = bonds[k].getOtherAtomNode (atom).getIndex ();
if (bsRing.get (j)) {
switch (bonds[k].order) {
case 514:
case 513:
case 515:
nAromatic++;
break;
case 2:
nDouble++;
haveDouble = true;
}
}}
if (is5 && nAromatic == 0) {
switch (atom.getElementNumber ()) {
case 7:
case 8:
case 16:
if (!haveDouble) nLonePairs++;
break;
}
}}
return (nAromatic == 0 ? Clazz.doubleToInt (nDouble / 2) + nLonePairs : nAromatic == (is5 ? 5 : 6) ? -3 : 0);
}, $fz.isPrivate = true, $fz), "~A,J.util.BS,~B");
});
Clazz.declarePackage ("J.smiles");
Clazz.load (["J.util.JmolNode", "$.P3"], "J.smiles.SmilesAtom", ["J.util.ArrayUtil", "$.Elements", "$.Logger"], function () {
c$ = Clazz.decorateAsClass (function () {
this.atomsOr = null;
this.nAtomsOr = 0;
this.primitives = null;
this.nPrimitives = 0;
this.index = 0;
this.atomName = null;
this.residueName = null;
this.residueChar = null;
this.isBioAtom = false;
this.bioType = '\0';
this.$isLeadAtom = false;
this.notBondedIndex = -1;
this.notCrossLinked = false;
this.aromaticAmbiguous = true;
this.atomType = null;
this.covalentHydrogenCount = -1;
this.not = false;
this.selected = false;
this.hasSymbol = false;
this.isFirst = true;
this.jmolIndex = -1;
this.elementNumber = -2;
this.missingHydrogenCount = -2147483648;
this.implicitHydrogenCount = -2147483648;
this.parent = null;
this.bonds = null;
this.bondCount = 0;
this.iNested = 0;
this.atomicMass = -2147483648;
this.charge = -2147483648;
this.matchingAtom = -1;
this.chiralClass = -2147483648;
this.chiralOrder = -2147483648;
this.$isAromatic = false;
this.component = 0;
this.atomSite = 0;
this.degree = -1;
this.nonhydrogenDegree = -1;
this.valence = 0;
this.connectivity = -1;
this.ringMembership = -2147483648;
this.ringSize = -2147483648;
this.ringConnectivity = -1;
Clazz.instantialize (this, arguments);
}, J.smiles, "SmilesAtom", J.util.P3, J.util.JmolNode);
Clazz.prepareFields (c$, function () {
this.bonds =  new Array (4);
});
c$.getChiralityClass = $_M(c$, "getChiralityClass", 
function (xx) {
return Clazz.doubleToInt (("0;11;AL;33;TH;TP;OH;77;SP;".indexOf (xx) + 1) / 3);
}, "~S");
c$.allowSmilesUnbracketed = $_M(c$, "allowSmilesUnbracketed", 
function (xx) {
return ("B, C, N, O, P, S, F, Cl, Br, I,".indexOf (xx + ",") >= 0);
}, "~S");
$_M(c$, "setBioAtom", 
function (bioType) {
this.isBioAtom = (bioType != '\0');
this.bioType = bioType;
if (this.parent != null) {
this.parent.bioType = bioType;
this.parent.isBioAtom = this.isBioAtom;
}}, "~S");
$_M(c$, "setAtomName", 
function (name) {
if (name == null) return;
if (name.length > 0) this.atomName = name;
if (name.equals ("0")) this.$isLeadAtom = true;
if (this.parent != null) {
this.parent.atomName = name;
}}, "~S");
$_M(c$, "setBonds", 
function (bonds) {
this.bonds = bonds;
}, "~A");
$_M(c$, "addAtomOr", 
function () {
if (this.atomsOr == null) this.atomsOr =  new Array (2);
if (this.nAtomsOr >= this.atomsOr.length) this.atomsOr = J.util.ArrayUtil.doubleLength (this.atomsOr);
var sAtom =  new J.smiles.SmilesAtom ().setIndex (this.index);
sAtom.parent = this;
this.atomsOr[this.nAtomsOr] = sAtom;
this.nAtomsOr++;
return sAtom;
});
$_M(c$, "addPrimitive", 
function () {
if (this.primitives == null) this.primitives =  new Array (2);
if (this.nPrimitives >= this.primitives.length) {
var tmp =  new Array (this.primitives.length * 2);
System.arraycopy (this.primitives, 0, tmp, 0, this.primitives.length);
this.primitives = tmp;
}var sAtom =  new J.smiles.SmilesAtom ().setIndex (this.index);
sAtom.parent = this;
this.primitives[this.nPrimitives] = sAtom;
this.setSymbol ("*");
this.hasSymbol = false;
this.nPrimitives++;
return sAtom;
});
Clazz.overrideMethod (c$, "toString", 
function () {
var s = (this.residueChar != null || this.residueName != null ? (this.residueChar == null ? this.residueName : this.residueChar) + "." + this.atomName : this.elementNumber == -1 ? "A" : this.elementNumber == -2 ? "*" : J.util.Elements.elementSymbolFromNumber (this.elementNumber));
if (this.$isAromatic) s = s.toLowerCase ();
return "[" + s + '.' + this.index + (this.matchingAtom >= 0 ? "(" + this.matchingAtom + ")" : "") + "]";
});
$_M(c$, "setIndex", 
function (index) {
this.index = index;
return this;
}, "~N");
$_M(c$, "setAll", 
function (iComponent, ptAtom, flags, atomicNumber, charge) {
this.component = iComponent;
this.index = ptAtom;
this.atomSite = flags;
this.elementNumber = atomicNumber;
this.charge = charge;
return this;
}, "~N,~N,~N,~N,~N");
$_M(c$, "setHydrogenCount", 
function (molecule) {
if (this.missingHydrogenCount != -2147483648) return true;
var count = J.smiles.SmilesAtom.getDefaultCount (this.elementNumber, this.$isAromatic);
if (count == -2) return false;
if (count == -1) return true;
if (this.elementNumber == 7 && this.$isAromatic && this.bondCount == 2) {
if (this.bonds[0].order == 1 && this.bonds[1].order == 1) count++;
}for (var i = 0; i < this.bondCount; i++) {
var bond = this.bonds[i];
switch (bond.order) {
case 81:
if (this.elementNumber == 7) {
J.util.Logger.info ("Ambiguous bonding to aromatic N found -- MF may be in error");
}count -= 1;
break;
case 1:
case 257:
case 513:
count -= 1;
break;
case 2:
count -= (this.$isAromatic && this.elementNumber == 6 ? 1 : 2);
break;
case 3:
count -= 3;
break;
}
}
if (count > 0) this.missingHydrogenCount = count;
return true;
}, "J.smiles.SmilesSearch");
c$.getDefaultCount = $_M(c$, "getDefaultCount", 
function (elementNumber, isAromatic) {
switch (elementNumber) {
case 0:
case -1:
return -1;
case 6:
return (isAromatic ? 3 : 4);
case 8:
case 16:
return 2;
case 7:
return (isAromatic ? 2 : 3);
case 5:
case 15:
return 3;
case 9:
case 17:
case 35:
case 53:
return 1;
}
return -2;
}, "~N,~B");
Clazz.overrideMethod (c$, "getIndex", 
function () {
return this.index;
});
$_M(c$, "isAromatic", 
function () {
return this.$isAromatic;
});
$_M(c$, "setSymbol", 
function (symbol) {
this.$isAromatic = symbol.equals (symbol.toLowerCase ());
this.hasSymbol = true;
if (symbol.equals ("*")) {
this.$isAromatic = false;
this.elementNumber = -2;
return true;
}if (symbol.equals ("Xx")) {
this.elementNumber = 0;
return true;
}this.aromaticAmbiguous = false;
if (symbol.equals ("a") || symbol.equals ("A")) {
if (this.elementNumber < 0) this.elementNumber = -1;
return true;
}if (this.$isAromatic) symbol = symbol.substring (0, 1).toUpperCase () + (symbol.length == 1 ? "" : symbol.substring (1));
this.elementNumber = J.util.Elements.elementNumberFromSymbol (symbol, true);
return (this.elementNumber != 0);
}, "~S");
Clazz.overrideMethod (c$, "getElementNumber", 
function () {
return this.elementNumber;
});
$_M(c$, "getAtomicMass", 
function () {
return this.atomicMass;
});
$_M(c$, "setAtomicMass", 
function (mass) {
this.atomicMass = mass;
}, "~N");
$_M(c$, "getCharge", 
function () {
return this.charge;
});
$_M(c$, "setCharge", 
function (charge) {
this.charge = charge;
}, "~N");
$_M(c$, "getMatchingAtom", 
function () {
return this.matchingAtom;
});
$_M(c$, "setMatchingAtom", 
function (atom) {
this.matchingAtom = atom;
}, "~N");
$_M(c$, "getChiralClass", 
function () {
return this.chiralClass;
});
$_M(c$, "setChiralClass", 
function (chiralClass) {
this.chiralClass = chiralClass;
}, "~N");
$_M(c$, "getChiralOrder", 
function () {
return this.chiralOrder;
});
$_M(c$, "setChiralOrder", 
function (chiralOrder) {
this.chiralOrder = chiralOrder;
}, "~N");
$_M(c$, "setExplicitHydrogenCount", 
function (count) {
this.missingHydrogenCount = count;
}, "~N");
$_M(c$, "setImplicitHydrogenCount", 
function (count) {
this.implicitHydrogenCount = count;
}, "~N");
$_M(c$, "setDegree", 
function (degree) {
this.degree = degree;
}, "~N");
$_M(c$, "setNonhydrogenDegree", 
function (degree) {
this.nonhydrogenDegree = degree;
}, "~N");
$_M(c$, "setValence", 
function (valence) {
this.valence = valence;
}, "~N");
$_M(c$, "setConnectivity", 
function (connectivity) {
this.connectivity = connectivity;
}, "~N");
$_M(c$, "setRingMembership", 
function (rm) {
this.ringMembership = rm;
}, "~N");
$_M(c$, "setRingSize", 
function (rs) {
this.ringSize = rs;
}, "~N");
$_M(c$, "setRingConnectivity", 
function (rc) {
this.ringConnectivity = rc;
}, "~N");
Clazz.overrideMethod (c$, "getModelIndex", 
function () {
return this.component;
});
Clazz.overrideMethod (c$, "getAtomSite", 
function () {
return this.atomSite;
});
Clazz.overrideMethod (c$, "getImplicitHydrogenCount", 
function () {
return 0;
});
$_M(c$, "getExplicitHydrogenCount", 
function () {
return this.missingHydrogenCount;
});
Clazz.overrideMethod (c$, "getFormalCharge", 
function () {
return this.charge;
});
Clazz.overrideMethod (c$, "getIsotopeNumber", 
function () {
return this.atomicMass;
});
Clazz.overrideMethod (c$, "getAtomicAndIsotopeNumber", 
function () {
return J.util.Elements.getAtomicAndIsotopeNumber (this.elementNumber, this.atomicMass);
});
Clazz.overrideMethod (c$, "getAtomName", 
function () {
return this.atomName == null ? "" : this.atomName;
});
Clazz.overrideMethod (c$, "getGroup3", 
function (allowNull) {
return this.residueName == null ? "" : this.residueName;
}, "~B");
Clazz.overrideMethod (c$, "getGroup1", 
function (c0) {
return this.residueChar == null ? "" : this.residueChar;
}, "~S");
$_M(c$, "addBond", 
function (bond) {
if (this.bondCount >= this.bonds.length) this.bonds = J.util.ArrayUtil.doubleLength (this.bonds);
this.bonds[this.bondCount] = bond;
this.bondCount++;
}, "J.smiles.SmilesBond");
$_M(c$, "setBondArray", 
function () {
if (this.bonds.length > this.bondCount) this.bonds = J.util.ArrayUtil.arrayCopyObject (this.bonds, this.bondCount);
if (this.atomsOr != null && this.atomsOr.length > this.nAtomsOr) this.atomsOr = J.util.ArrayUtil.arrayCopyObject (this.atomsOr, this.atomsOr.length);
if (this.primitives != null && this.primitives.length > this.nPrimitives) this.primitives = J.util.ArrayUtil.arrayCopyObject (this.primitives, this.primitives.length);
for (var i = 0; i < this.bonds.length; i++) {
if (this.isBioAtom && this.bonds[i].order == 17) this.bonds[i].order = 112;
if (this.bonds[i].getAtom1 ().index > this.bonds[i].getAtom2 ().index) {
this.bonds[i].switchAtoms ();
}}
});
Clazz.overrideMethod (c$, "getEdges", 
function () {
return (this.parent != null ? this.parent.getEdges () : this.bonds);
});
$_M(c$, "getBond", 
function (number) {
return (this.parent != null ? this.parent.getBond (number) : number >= 0 && number < this.bondCount ? this.bonds[number] : null);
}, "~N");
Clazz.overrideMethod (c$, "getCovalentBondCount", 
function () {
return this.getBondCount ();
});
$_M(c$, "getBondCount", 
function () {
return (this.parent != null ? this.parent.getCovalentBondCount () : this.bondCount);
});
$_M(c$, "getMatchingBondedAtom", 
function (i) {
if (this.parent != null) return this.parent.getMatchingBondedAtom (i);
if (i >= this.bondCount) return -1;
var b = this.bonds[i];
return (b.getAtom1 () === this ? b.getAtom2 () : b.getAtom1 ()).matchingAtom;
}, "~N");
Clazz.overrideMethod (c$, "getBondedAtomIndex", 
function (j) {
return (this.parent != null ? this.parent.getBondedAtomIndex (j) : this.bonds[j].getOtherAtom (this).index);
}, "~N");
Clazz.overrideMethod (c$, "getCovalentHydrogenCount", 
function () {
if (this.covalentHydrogenCount >= 0) return this.covalentHydrogenCount;
if (this.parent != null) return this.parent.getCovalentHydrogenCount ();
this.covalentHydrogenCount = 0;
for (var k = 0; k < this.bonds.length; k++) if (this.bonds[k].getOtherAtom (this).elementNumber == 1) this.covalentHydrogenCount++;

return this.covalentHydrogenCount;
});
Clazz.overrideMethod (c$, "getValence", 
function () {
if (this.parent != null) return this.parent.getValence ();
var n = this.valence;
if (n <= 0 && this.bonds != null) for (var i = this.bonds.length; --i >= 0; ) n += this.bonds[i].getValence ();

this.valence = n;
return n;
});
$_M(c$, "getBondTo", 
function (atom) {
if (this.parent != null) return this.parent.getBondTo (atom);
var bond;
for (var k = 0; k < this.bonds.length; k++) {
if ((bond = this.bonds[k]) == null) continue;
if (atom == null ? bond.getAtom2 () === this : bond.getOtherAtom (this) === atom) return bond;
}
return null;
}, "J.smiles.SmilesAtom");
$_M(c$, "getBondNotTo", 
function (atom, allowH) {
var bond;
for (var k = 0; k < this.bonds.length; k++) {
if ((bond = this.bonds[k]) == null) continue;
var atom2 = bond.getOtherAtom (this);
if (atom !== atom2 && (allowH || atom2.elementNumber != 1)) return bond;
}
return null;
}, "J.smiles.SmilesAtom,~B");
Clazz.overrideMethod (c$, "isLeadAtom", 
function () {
return this.$isLeadAtom;
});
Clazz.overrideMethod (c$, "getOffsetResidueAtom", 
function (name, offset) {
if (this.isBioAtom) for (var k = 0; k < this.bonds.length; k++) if (this.bonds[k].getAtomIndex1 () == this.index && this.bonds[k].order == 96) return this.bonds[k].getOtherAtom (this).index;

return -1;
}, "~S,~N");
Clazz.overrideMethod (c$, "getGroupBits", 
function (bs) {
bs.set (this.index);
return;
}, "J.util.BS");
Clazz.overrideMethod (c$, "isCrossLinked", 
function (node) {
var bond = this.getBondTo (node);
return bond.isHydrogen ();
}, "J.util.JmolNode");
Clazz.overrideMethod (c$, "getCrossLinkLeadAtomIndexes", 
function (vLinks) {
for (var k = 0; k < this.bonds.length; k++) if (this.bonds[k].order == 112) vLinks.addLast (Integer.$valueOf (this.bonds[k].getOtherAtom (this).index));

return true;
}, "J.util.JmolList");
Clazz.overrideMethod (c$, "getBioStructureTypeName", 
function () {
return null;
});
Clazz.overrideMethod (c$, "getResno", 
function () {
return 0;
});
Clazz.overrideMethod (c$, "getChainID", 
function () {
return 0;
});
Clazz.overrideMethod (c$, "getChainIDStr", 
function () {
return "";
});
c$.getAtomLabel = $_M(c$, "getAtomLabel", 
function (atomicNumber, isotopeNumber, valence, charge, nH, isAromatic, stereo) {
var sym = J.util.Elements.elementSymbolFromNumber (atomicNumber);
if (isAromatic) {
sym = sym.toLowerCase ();
if (atomicNumber != 6) valence = 2147483647;
}var count = (stereo.length > 0 || isotopeNumber != 0 || charge != 0 ? -1 : J.smiles.SmilesAtom.getDefaultCount (atomicNumber, false));
return (count == valence ? sym : "[" + (isotopeNumber <= 0 ? "" : "" + isotopeNumber) + sym + (charge < 0 ? "" + charge : charge > 0 ? "+" + charge : "") + stereo + (nH > 1 ? "H" + nH : nH == 1 ? "H" : "") + "]");
}, "~N,~N,~N,~N,~N,~B,~S");
Clazz.overrideMethod (c$, "isDna", 
function () {
return this.bioType == 'd';
});
Clazz.overrideMethod (c$, "isRna", 
function () {
return this.bioType == 'r';
});
Clazz.overrideMethod (c$, "isNucleic", 
function () {
return this.bioType == 'n' || this.bioType == 'r' || this.bioType == 'd';
});
Clazz.overrideMethod (c$, "isProtein", 
function () {
return this.bioType == 'p';
});
Clazz.overrideMethod (c$, "isPurine", 
function () {
return this.residueChar != null && this.isNucleic () && "AG".indexOf (this.residueChar) >= 0;
});
Clazz.overrideMethod (c$, "isPyrimidine", 
function () {
return this.residueChar != null && this.isNucleic () && "CTUI".indexOf (this.residueChar) >= 0;
});
Clazz.overrideMethod (c$, "isDeleted", 
function () {
return false;
});
$_M(c$, "setAtomType", 
function (type) {
this.atomType = type;
}, "~S");
Clazz.overrideMethod (c$, "getAtomType", 
function () {
return (this.atomType == null ? this.atomName : this.atomType);
});
Clazz.overrideMethod (c$, "findAtomsLike", 
function (substring) {
return null;
}, "~S");
Clazz.defineStatics (c$,
"STEREOCHEMISTRY_DEFAULT", 0,
"STEREOCHEMISTRY_ALLENE", 2,
"STEREOCHEMISTRY_TETRAHEDRAL", 4,
"STEREOCHEMISTRY_TRIGONAL_BIPYRAMIDAL", 5,
"STEREOCHEMISTRY_OCTAHEDRAL", 6,
"STEREOCHEMISTRY_SQUARE_PLANAR", 8,
"UNBRACKETED_SET", "B, C, N, O, P, S, F, Cl, Br, I,");
});
Clazz.declarePackage ("J.smiles");
Clazz.load (["J.util.JmolEdge"], "J.smiles.SmilesBond", ["J.smiles.InvalidSmilesException"], function () {
c$ = Clazz.decorateAsClass (function () {
this.atom1 = null;
this.atom2 = null;
this.isNot = false;
this.matchingBond = null;
this.primitives = null;
this.nPrimitives = 0;
this.bondsOr = null;
this.nBondsOr = 0;
Clazz.instantialize (this, arguments);
}, J.smiles, "SmilesBond", J.util.JmolEdge);
c$.getBondOrderString = $_M(c$, "getBondOrderString", 
function (order) {
switch (order) {
case 1:
return "";
case 2:
return "=";
case 3:
return "#";
default:
return "";
}
}, "~N");
$_M(c$, "set", 
function (bond) {
this.order = bond.order;
this.isNot = bond.isNot;
this.primitives = bond.primitives;
this.nPrimitives = bond.nPrimitives;
this.bondsOr = bond.bondsOr;
this.nBondsOr = bond.nBondsOr;
}, "J.smiles.SmilesBond");
$_M(c$, "addBondOr", 
function () {
if (this.bondsOr == null) this.bondsOr =  new Array (2);
if (this.nBondsOr >= this.bondsOr.length) {
var tmp =  new Array (this.bondsOr.length * 2);
System.arraycopy (this.bondsOr, 0, tmp, 0, this.bondsOr.length);
this.bondsOr = tmp;
}var sBond =  new J.smiles.SmilesBond (null, null, -1, false);
this.bondsOr[this.nBondsOr] = sBond;
this.nBondsOr++;
return sBond;
});
$_M(c$, "addPrimitive", 
function () {
if (this.primitives == null) this.primitives =  new Array (2);
if (this.nPrimitives >= this.primitives.length) {
var tmp =  new Array (this.primitives.length * 2);
System.arraycopy (this.primitives, 0, tmp, 0, this.primitives.length);
this.primitives = tmp;
}var sBond =  new J.smiles.SmilesBond (null, null, -1, false);
this.primitives[this.nPrimitives] = sBond;
this.nPrimitives++;
return sBond;
});
Clazz.overrideMethod (c$, "toString", 
function () {
return this.atom1 + " -" + (this.isNot ? "!" : "") + this.order + "- " + this.atom2;
});
Clazz.makeConstructor (c$, 
function (atom1, atom2, bondType, isNot) {
Clazz.superConstructor (this, J.smiles.SmilesBond, []);
this.set2 (bondType, isNot);
this.set2a (atom1, atom2);
}, "J.smiles.SmilesAtom,J.smiles.SmilesAtom,~N,~B");
$_M(c$, "set2", 
function (bondType, isNot) {
this.order = bondType;
this.isNot = isNot;
}, "~N,~B");
$_M(c$, "set2a", 
function (atom1, atom2) {
if (atom1 != null) {
this.atom1 = atom1;
atom1.addBond (this);
}if (atom2 != null) {
this.atom2 = atom2;
atom2.isFirst = false;
atom2.addBond (this);
}}, "J.smiles.SmilesAtom,J.smiles.SmilesAtom");
c$.isBondType = $_M(c$, "isBondType", 
function (ch, isSearch, isBioSequence) {
if ("-=#:/\\.+!,&;@~^'".indexOf (ch) < 0) return false;
if (!isSearch && "-=#:/\\.~^'".indexOf (ch) < 0) throw  new J.smiles.InvalidSmilesException ("SMARTS bond type " + ch + " not allowed in SMILES");
if (isBioSequence && ch == '~') return false;
return true;
}, "~S,~B,~B");
c$.getBondTypeFromCode = $_M(c$, "getBondTypeFromCode", 
function (code) {
switch (code) {
case '.':
return 0;
case '-':
return 1;
case '=':
return 2;
case '#':
return 3;
case ':':
return 17;
case '/':
return 257;
case '\\':
return 513;
case '^':
return 769;
case '\'':
return 1025;
case '@':
return 65;
case '~':
return 81;
case '+':
return 96;
}
return -1;
}, "~S");
$_M(c$, "getAtom1", 
function () {
return this.atom1;
});
$_M(c$, "getAtom2", 
function () {
return this.atom2;
});
$_M(c$, "setAtom2", 
function (atom) {
this.atom2 = atom;
if (this.atom2 != null) {
atom.addBond (this);
}}, "J.smiles.SmilesAtom");
$_M(c$, "getBondType", 
function () {
return this.order;
});
$_M(c$, "getOtherAtom", 
function (a) {
return (this.atom1 === a ? this.atom2 : this.atom1);
}, "J.smiles.SmilesAtom");
Clazz.overrideMethod (c$, "getAtomIndex1", 
function () {
return this.atom1.index;
});
Clazz.overrideMethod (c$, "getAtomIndex2", 
function () {
return this.atom2.index;
});
Clazz.overrideMethod (c$, "getCovalentOrder", 
function () {
return this.order;
});
Clazz.overrideMethod (c$, "getOtherAtomNode", 
function (atom) {
return (atom === this.atom1 ? this.atom2 : atom === this.atom2 ? this.atom1 : null);
}, "J.util.JmolNode");
Clazz.overrideMethod (c$, "isCovalent", 
function () {
return this.order != 112;
});
$_M(c$, "getValence", 
function () {
return (this.order & 7);
});
Clazz.overrideMethod (c$, "isHydrogen", 
function () {
return this.order == 112;
});
$_M(c$, "switchAtoms", 
function () {
var a = this.atom1;
this.atom1 = this.atom2;
this.atom2 = a;
switch (this.order) {
case 769:
this.order = 1025;
break;
case 1025:
this.order = 769;
break;
case 257:
this.order = 513;
break;
case 513:
this.order = 257;
break;
}
});
Clazz.defineStatics (c$,
"TYPE_UNKNOWN", -1,
"TYPE_NONE", 0,
"TYPE_SINGLE", 1,
"TYPE_DOUBLE", 2,
"TYPE_TRIPLE", 3,
"TYPE_AROMATIC", 0x11,
"TYPE_DIRECTIONAL_1", 0x101,
"TYPE_DIRECTIONAL_2", 0x201,
"TYPE_ATROPISOMER_1", 0x301,
"TYPE_ATROPISOMER_2", 0x401,
"TYPE_RING", 0x41,
"TYPE_ANY", 0x51,
"TYPE_BIO_SEQUENCE", 0x60,
"TYPE_BIO_PAIR", 0x70,
"TYPE_MULTIPLE", 999);
});
Clazz.declarePackage ("J.smiles");
c$ = Clazz.decorateAsClass (function () {
this.search = null;
this.nPoints = 0;
this.type = 0;
this.index = 0;
this.isNot = false;
this.indices = null;
this.min = 0;
this.max = 0;
this.points = null;
Clazz.instantialize (this, arguments);
}, J.smiles, "SmilesMeasure");
Clazz.prepareFields (c$, function () {
this.indices =  Clazz.newIntArray (4, 0);
this.points =  new Array (4);
});
Clazz.makeConstructor (c$, 
function (search, index, type, min, max, isNot) {
this.search = search;
this.type = Math.min (4, Math.max (type, 2));
this.index = index;
this.min = Math.min (min, max);
this.max = Math.max (min, max);
this.isNot = isNot;
}, "J.smiles.SmilesSearch,~N,~N,~N,~N,~B");
Clazz.overrideMethod (c$, "toString", 
function () {
var s = "(." + "__dat".charAt (this.type) + this.index + ":" + this.min + "," + this.max + ") for";
for (var i = 0; i < this.type; i++) s += " " + (i >= this.nPoints ? "?" : "" + this.indices[i]);

return s;
});
$_M(c$, "addPoint", 
function (index) {
if (this.nPoints == this.type) return false;
if (this.nPoints == 0) for (var i = 1; i < this.type; i++) this.indices[i] = index + i;

this.indices[this.nPoints++] = index;
return true;
}, "~N");
$_M(c$, "check", 
function () {
for (var i = 0; i < this.type; i++) {
var iAtom = this.search.patternAtoms[this.indices[i]].getMatchingAtom ();
this.points[i] = this.search.jmolAtoms[iAtom];
}
var d = 0;
switch (this.type) {
case 2:
d = this.points[0].distance (this.points[1]);
break;
case 3:
this.search.v.vA.sub2 (this.points[0], this.points[1]);
this.search.v.vB.sub2 (this.points[2], this.points[1]);
d = this.search.v.vA.angle (this.search.v.vB) / 0.017453292;
break;
case 4:
J.smiles.SmilesMeasure.setTorsionData (this.points[0], this.points[1], this.points[2], this.points[3], this.search.v, true);
d = this.search.v.vTemp1.angle (this.search.v.vTemp2) / 0.017453292 * (this.search.v.vNorm1.dot (this.search.v.vNorm2) < 0 ? 1 : -1);
break;
}
return ((d < this.min || d > this.max) == this.isNot);
});
c$.setTorsionData = $_M(c$, "setTorsionData", 
function (pt1a, pt1, pt2, pt2a, v, isAll) {
v.vTemp1.setT (pt1a);
v.vTemp1.sub (pt1);
v.vTemp2.setT (pt2a);
v.vTemp2.sub (pt2);
if (!isAll) return;
v.vNorm1.setT (pt1);
v.vNorm1.sub (pt2);
v.vNorm1.normalize ();
v.vTemp1.cross (v.vTemp1, v.vNorm1);
v.vTemp1.normalize ();
v.vTemp2.cross (v.vTemp2, v.vNorm1);
v.vTemp2.normalize ();
v.vNorm2.cross (v.vTemp1, v.vTemp2);
}, "J.util.P3,J.util.P3,J.util.P3,J.util.P3,J.smiles.SmilesSearch.VTemp,~B");
Clazz.defineStatics (c$,
"TYPES", "__dat",
"radiansPerDegree", (0.017453292519943295));
Clazz.declarePackage ("J.smiles");
Clazz.load (["java.util.Hashtable"], "J.smiles.SmilesParser", ["java.lang.Character", "J.smiles.InvalidSmilesException", "$.SmilesAtom", "$.SmilesBond", "$.SmilesMeasure", "$.SmilesSearch", "J.util.Elements", "$.JmolList", "$.Logger", "$.Parser", "$.SB", "$.TextFormat"], function () {
c$ = Clazz.decorateAsClass (function () {
this.isSmarts = false;
this.isBioSequence = false;
this.bioType = '\0';
this.ringBonds = null;
this.braceCount = 0;
this.branchLevel = 0;
this.flags = 0;
this.htMeasures = null;
Clazz.instantialize (this, arguments);
}, J.smiles, "SmilesParser");
Clazz.prepareFields (c$, function () {
this.ringBonds =  new java.util.Hashtable ();
this.htMeasures =  new java.util.Hashtable ();
});
c$.getMolecule = $_M(c$, "getMolecule", 
function (pattern, isSmarts) {
return ( new J.smiles.SmilesParser (isSmarts)).parse (pattern);
}, "~S,~B");
Clazz.makeConstructor (c$, 
function (isSmarts) {
this.isSmarts = isSmarts;
}, "~B");
$_M(c$, "reset", 
function () {
this.braceCount = 0;
this.branchLevel = 0;
});
$_M(c$, "parse", 
function (pattern) {
if (pattern == null) throw  new J.smiles.InvalidSmilesException ("SMILES expressions must not be null");
var search =  new J.smiles.SmilesSearch ();
if (pattern.indexOf ("$(select") >= 0) pattern = this.parseNested (search, pattern, "select");
pattern = J.smiles.SmilesParser.cleanPattern (pattern);
while (pattern.startsWith ("/")) {
var strFlags = J.smiles.SmilesParser.getSubPattern (pattern, 0, '/').toUpperCase ();
pattern = pattern.substring (strFlags.length);
this.flags = 0;
if (strFlags.indexOf ("NOAROMATIC") >= 0) this.flags |= 1;
if (strFlags.indexOf ("AROMATICSTRICT") >= 0) this.flags |= 4;
if (strFlags.indexOf ("AROMATICDEFINED") >= 0) this.flags |= 8;
if (strFlags.indexOf ("AROMATICDOUBLE") >= 0) this.flags |= 16;
if (strFlags.indexOf ("NOSTEREO") >= 0) this.flags |= 2;
}
if (pattern.indexOf ("$") >= 0) pattern = this.parseVariables (pattern);
if (this.isSmarts && pattern.indexOf ("[$") >= 0) pattern = this.parseVariableLength (pattern);
if (pattern.indexOf ("||") >= 0) {
var patterns = J.util.TextFormat.splitChars (pattern, "||");
var toDo = "";
search.subSearches =  new Array (patterns.length);
for (var i = 0; i < patterns.length; i++) {
var key = "|" + patterns[i] + "|";
if (toDo.indexOf (key) < 0) {
search.subSearches[i] = this.getSearch (search, patterns[i], this.flags);
toDo += key;
}}
J.util.Logger.info (toDo);
return search;
}return this.getSearch (search, pattern, this.flags);
}, "~S");
$_M(c$, "parseVariableLength", 
($fz = function (pattern) {
var sout =  new J.util.SB ();
var len = pattern.length - 1;
var nParen = 0;
var haveInternalOr = false;
for (var i = 0; i < len; i++) {
switch (pattern.charAt (i)) {
case '(':
nParen++;
break;
case ')':
nParen--;
break;
case '|':
if (nParen > 0) {
haveInternalOr = true;
if (pattern.charAt (i + 1) == '|') {
pattern = pattern.substring (0, i) + pattern.substring (i + 1);
len--;
}}break;
}
}
if (pattern.indexOf ("||") >= 0) {
var patterns = J.util.TextFormat.splitChars (pattern, "||");
for (var i = 0; i < patterns.length; i++) sout.append ("||").append (this.parseVariableLength (patterns[i]));

} else {
var pt = -1;
var ret =  Clazz.newIntArray (1, 0);
var isOK = true;
var bracketed = null;
while ((pt = pattern.indexOf ("[$", pt + 1)) >= 0) {
var pt0 = pt;
var min = -2147483648;
var max = -2147483648;
pt = J.smiles.SmilesParser.getDigits (pattern, pt + 2, ret);
min = ret[0];
if (min != -2147483648) {
if (J.smiles.SmilesParser.getChar (pattern, pt) == '-') {
pt = J.smiles.SmilesParser.getDigits (pattern, pt + 1, ret);
max = ret[0];
}}if (J.smiles.SmilesParser.getChar (pattern, pt) != '(') continue;
bracketed = J.smiles.SmilesParser.getSubPattern (pattern, pt0, '[');
if (!bracketed.endsWith (")")) continue;
var pt1 = pt0 + bracketed.length + 2;
var repeat = J.smiles.SmilesParser.getSubPattern (pattern, pt, '(');
var pt2 = pt;
bracketed = J.smiles.SmilesParser.getSubPattern (pattern, pt, '[');
pt += 1 + repeat.length;
if (repeat.indexOf (':') >= 0 && repeat.indexOf ('|') < 0) {
var parenCount = 0;
var n = repeat.length;
var ptColon = -1;
for (var i = 0; i < n; i++) {
switch (repeat.charAt (i)) {
case '[':
case '(':
parenCount++;
break;
case ')':
case ']':
parenCount--;
break;
case '.':
if (ptColon >= 0 && parenCount == 0) n = i;
break;
case ':':
if (ptColon < 0 && parenCount == 0) ptColon = i;
break;
}
}
if (ptColon > 0) repeat = repeat.substring (0, ptColon) + "(" + repeat.substring (ptColon, n) + ")" + repeat.substring (n);
}if (min == -2147483648) {
var ptOr = repeat.indexOf ("|");
if (ptOr >= 0) return this.parseVariableLength (pattern.substring (0, pt0) + "[$1" + pattern.substring (pt2, pt2 + ptOr + 1) + ")]" + pattern.substring (pt1) + "||" + pattern.substring (0, pt0) + "[$1(" + pattern.substring (pt2 + ptOr + 2) + pattern.substring (pt1));
continue;
}if (max == -2147483648) max = min;
if (repeat.indexOf ("|") >= 0) repeat = "[$(" + repeat + ")]";
for (var i = min; i <= max; i++) {
var sb =  new J.util.SB ();
sb.append ("||").append (pattern.substring (0, pt0));
for (var j = 0; j < i; j++) sb.append (repeat);

sb.append (pattern.substring (pt1));
sout.appendSB (sb);
}
}
if (!isOK) throw  new J.smiles.InvalidSmilesException ("bad variable expression: " + bracketed);
}return (haveInternalOr ? this.parseVariableLength (sout.substring (2)) : sout.length () < 2 ? pattern : sout.substring (2));
}, $fz.isPrivate = true, $fz), "~S");
$_M(c$, "getSearch", 
function (parent, pattern, flags) {
this.htMeasures =  new java.util.Hashtable ();
var molecule =  new J.smiles.SmilesSearch ();
molecule.setTop (parent);
molecule.isSmarts = this.isSmarts;
molecule.pattern = pattern;
molecule.flags = flags;
if (pattern.indexOf ("$(") >= 0) pattern = this.parseNested (molecule, pattern, "");
this.parseSmiles (molecule, pattern, null, false);
if (this.braceCount != 0) throw  new J.smiles.InvalidSmilesException ("unmatched '{'");
if (!this.ringBonds.isEmpty ()) throw  new J.smiles.InvalidSmilesException ("Open ring");
molecule.setAtomArray ();
for (var i = molecule.atomCount; --i >= 0; ) {
var atom = molecule.patternAtoms[i];
atom.setBondArray ();
if (!this.isSmarts && atom.bioType == '\0' && !atom.setHydrogenCount (molecule)) throw  new J.smiles.InvalidSmilesException ("unbracketed atoms must be one of: B, C, N, O, P, S, F, Cl, Br, I,");
}
if (this.isSmarts) for (var i = molecule.atomCount; --i >= 0; ) {
var atom = molecule.patternAtoms[i];
this.checkNested (molecule, atom, flags);
for (var k = 0; k < atom.nAtomsOr; k++) this.checkNested (molecule, atom.atomsOr[k], flags);

for (var k = 0; k < atom.nPrimitives; k++) this.checkNested (molecule, atom.primitives[k], flags);

}
if (!this.isSmarts && !this.isBioSequence) molecule.elementCounts[1] = molecule.getMissingHydrogenCount ();
this.fixChirality (molecule);
return molecule;
}, "J.smiles.SmilesSearch,~S,~N");
$_M(c$, "checkNested", 
($fz = function (molecule, atom, flags) {
if (atom.iNested > 0) {
var o = molecule.getNested (atom.iNested);
if (Clazz.instanceOf (o, String)) {
var s = o;
if (s.startsWith ("select")) return;
if (s.charAt (0) != '~' && atom.bioType != '\0') s = "~" + atom.bioType + "~" + s;
var search = this.getSearch (molecule, s, flags);
if (search.atomCount > 0 && search.patternAtoms[0].selected) atom.selected = true;
molecule.setNested (atom.iNested, search);
}}}, $fz.isPrivate = true, $fz), "J.smiles.SmilesSearch,J.smiles.SmilesAtom,~N");
$_M(c$, "fixChirality", 
($fz = function (molecule) {
for (var i = molecule.atomCount; --i >= 0; ) {
var sAtom = molecule.patternAtoms[i];
var stereoClass = sAtom.getChiralClass ();
if (stereoClass == -2147483648) continue;
var nBonds = sAtom.missingHydrogenCount;
if (nBonds < 0) nBonds = 0;
nBonds += sAtom.getBondCount ();
switch (stereoClass) {
case 0:
switch (nBonds) {
case 2:
stereoClass = (sAtom.getValence () == 3 ? 3 : 2);
break;
case 3:
case 4:
case 5:
case 6:
stereoClass = nBonds;
break;
}
break;
case 8:
if (nBonds != 4) stereoClass = 0;
break;
case 2:
case 6:
case 4:
case 5:
if (nBonds != stereoClass) stereoClass = 0;
break;
}
if (stereoClass == 0) throw  new J.smiles.InvalidSmilesException ("Incorrect number of bonds for stereochemistry descriptor");
sAtom.setChiralClass (stereoClass);
}
}, $fz.isPrivate = true, $fz), "J.smiles.SmilesSearch");
$_M(c$, "parseSmiles", 
($fz = function (molecule, pattern, currentAtom, isBranchAtom) {
var ret =  Clazz.newIntArray (1, 0);
var pt = 0;
var ch;
var bond = null;
while (pattern != null && pattern.length != 0) {
var index = 0;
if (currentAtom == null || bond != null && bond.order == 0) {
if (this.isBioSequence) molecule.top.needAromatic = false;
index = this.checkBioType (pattern, 0);
}ch = J.smiles.SmilesParser.getChar (pattern, index);
var haveOpen = this.checkBrace (molecule, ch, '{');
if (haveOpen) ch = J.smiles.SmilesParser.getChar (pattern, ++index);
if (ch == '(') {
var isMeasure = (J.smiles.SmilesParser.getChar (pattern, index + 1) == '.');
if (currentAtom == null) throw  new J.smiles.InvalidSmilesException ("No previous atom for " + (isMeasure ? "measure" : "branch"));
var subString = J.smiles.SmilesParser.getSubPattern (pattern, index, '(');
if (subString.startsWith (".")) {
this.parseMeasure (molecule, subString.substring (1), currentAtom);
} else if (subString.length == 0 && this.isBioSequence) {
currentAtom.notCrossLinked = true;
} else {
this.branchLevel++;
this.parseSmiles (molecule, subString, currentAtom, true);
this.branchLevel--;
}index = subString.length + 2;
ch = J.smiles.SmilesParser.getChar (pattern, index);
if (ch == '}' && this.checkBrace (molecule, ch, '}')) index++;
} else {
pt = index;
while (J.smiles.SmilesBond.isBondType (ch, this.isSmarts, this.isBioSequence)) ch = J.smiles.SmilesParser.getChar (pattern, ++index);

bond = this.parseBond (molecule, null, pattern.substring (pt, index), null, currentAtom, false, isBranchAtom);
if (haveOpen && bond.order != -1) index = pt;
ch = J.smiles.SmilesParser.getChar (pattern, index);
if (this.checkBrace (molecule, ch, '{')) ch = J.smiles.SmilesParser.getChar (pattern, ++index);
if (ch == '~' && bond.order == 0) {
index = this.checkBioType (pattern, index);
ch = J.smiles.SmilesParser.getChar (pattern, index);
}if (ch == '\0' && bond.order == 0) return;
var isRing = (Character.isDigit (ch) || ch == '%');
var isAtom = (!isRing && (ch == '_' || ch == '[' || ch == '*' || Character.isLetter (ch)));
if (isRing) {
var ringNumber;
switch (ch) {
case '%':
if (J.smiles.SmilesParser.getChar (pattern, index + 1) == '(') {
var subPattern = J.smiles.SmilesParser.getSubPattern (pattern, index + 1, '(');
J.smiles.SmilesParser.getDigits (subPattern, 0, ret);
index += subPattern.length + 3;
if (ret[0] < 0) throw  new J.smiles.InvalidSmilesException ("Invalid ring designation: " + subPattern);
} else {
if (index + 3 <= pattern.length) index = J.smiles.SmilesParser.getDigits (pattern.substring (0, index + 3), index + 1, ret);
if (ret[0] < 10) throw  new J.smiles.InvalidSmilesException ("Two digits must follow the % sign");
}ringNumber = ret[0];
break;
default:
ringNumber = ch.charCodeAt (0) - 48;
index++;
}
this.parseRing (molecule, ringNumber, currentAtom, bond);
} else if (isAtom) {
switch (ch) {
case '[':
case '_':
var subPattern = J.smiles.SmilesParser.getSubPattern (pattern, index, ch);
index += subPattern.length + (ch == '[' ? 2 : 0);
if (this.isBioSequence && ch == '[' && subPattern.indexOf (".") < 0 && subPattern.indexOf ("_") < 0) subPattern += ".0";
currentAtom = this.parseAtom (molecule, null, subPattern, currentAtom, bond, ch == '[', false, isBranchAtom);
if (bond.order != -1 && bond.order != 0) bond.set2a (null, currentAtom);
break;
default:
var ch2 = (!this.isBioSequence && Character.isUpperCase (ch) ? J.smiles.SmilesParser.getChar (pattern, index + 1) : '\0');
if (ch != 'X' || ch2 != 'x') if (!Character.isLowerCase (ch2) || J.util.Elements.elementNumberFromSymbol (pattern.substring (index, index + 2), true) == 0) ch2 = '\0';
if (ch2 != '\0' && "NA CA BA PA SC AC".indexOf (pattern.substring (index, index + 2)) >= 0) {
ch2 = '\0';
}var size = (Character.isUpperCase (ch) && Character.isLowerCase (ch2) ? 2 : 1);
currentAtom = this.parseAtom (molecule, null, pattern.substring (index, index + size), currentAtom, bond, false, false, isBranchAtom);
index += size;
}
} else {
throw  new J.smiles.InvalidSmilesException ("Unexpected character: " + J.smiles.SmilesParser.getChar (pattern, index));
}ch = J.smiles.SmilesParser.getChar (pattern, index);
if (ch == '}' && this.checkBrace (molecule, ch, '}')) index++;
}pattern = pattern.substring (index);
isBranchAtom = false;
}
}, $fz.isPrivate = true, $fz), "J.smiles.SmilesSearch,~S,J.smiles.SmilesAtom,~B");
$_M(c$, "checkBioType", 
($fz = function (pattern, index) {
this.isBioSequence = (pattern.charAt (index) == '~');
if (this.isBioSequence) {
index++;
this.bioType = '*';
var ch = J.smiles.SmilesParser.getChar (pattern, 2);
if (ch == '~' && ((ch = pattern.charAt (1)) == '*' || Character.isLowerCase (ch))) {
this.bioType = ch;
index = 3;
}}return index;
}, $fz.isPrivate = true, $fz), "~S,~N");
$_M(c$, "parseMeasure", 
($fz = function (molecule, strMeasure, currentAtom) {
var pt = strMeasure.indexOf (":");
var isNot = false;
var id = (pt < 0 ? strMeasure : strMeasure.substring (0, pt));
while (pt != 0) {
var len = id.length;
if (len == 1) id += "0";
var m = this.htMeasures.get (id);
if ((m == null) == (pt < 0)) break;
try {
if (pt > 0) {
var type = ("__dat".indexOf (id.charAt (0)));
if (type < 2) break;
var ret =  Clazz.newIntArray (1, 0);
var index = J.smiles.SmilesParser.getDigits (id, 1, ret);
var pt2 = strMeasure.indexOf (",", pt);
if (pt2 < 0) pt2 = strMeasure.indexOf ("-", pt + 1);
if (pt2 < 0) break;
var s = strMeasure.substring (pt + 1, pt2);
if (s.startsWith ("!")) {
isNot = true;
s = s.substring (1);
}var min = (pt + 1 == pt2 ? 0 : J.util.Parser.fVal (s));
s = strMeasure.substring (pt2 + 1);
var max = (s.length == 0 ? 3.4028235E38 : J.util.Parser.fVal (s));
m =  new J.smiles.SmilesMeasure (molecule, index, type, min, max, isNot);
molecule.measures.addLast (m);
if (index > 0) this.htMeasures.put (id, m);
 else if (index == 0 && J.util.Logger.debugging) J.util.Logger.debug ("measure created: " + m);
} else {
if (!m.addPoint (currentAtom.index)) break;
if (m.nPoints == m.type) {
this.htMeasures.remove (id);
if (J.util.Logger.debugging) J.util.Logger.debug ("measure created: " + m);
}return;
}if (!m.addPoint (currentAtom.index)) break;
} catch (e) {
if (Clazz.exceptionOf (e, NumberFormatException)) {
break;
} else {
throw e;
}
}
return;
}
throw  new J.smiles.InvalidSmilesException ("invalid measure: " + strMeasure);
}, $fz.isPrivate = true, $fz), "J.smiles.SmilesSearch,~S,J.smiles.SmilesAtom");
$_M(c$, "checkBrace", 
($fz = function (molecule, ch, type) {
switch (ch) {
case '{':
if (ch != type) break;
this.braceCount++;
molecule.top.haveSelected = true;
return true;
case '}':
if (ch != type) break;
if (this.braceCount > 0) {
this.braceCount--;
return true;
}break;
default:
return false;
}
throw  new J.smiles.InvalidSmilesException ("Unmatched '}'");
}, $fz.isPrivate = true, $fz), "J.smiles.SmilesSearch,~S,~S");
$_M(c$, "parseNested", 
($fz = function (molecule, pattern, prefix) {
var index;
prefix = "$(" + prefix;
while ((index = pattern.lastIndexOf (prefix)) >= 0) {
var s = J.smiles.SmilesParser.getSubPattern (pattern, index + 1, '(');
var pt = index + s.length + 3;
pattern = pattern.substring (0, index) + "_" + molecule.addNested (s) + "_" + pattern.substring (pt);
}
return pattern;
}, $fz.isPrivate = true, $fz), "J.smiles.SmilesSearch,~S,~S");
$_M(c$, "parseVariables", 
($fz = function (pattern) {
var keys =  new J.util.JmolList ();
var values =  new J.util.JmolList ();
var index;
var ipt = 0;
var iptLast = -1;
while ((index = pattern.indexOf ("$", ipt)) >= 0) {
if (J.smiles.SmilesParser.getChar (pattern, ipt + 1) == '(') break;
ipt = J.smiles.SmilesParser.skipTo (pattern, index, '=');
if (ipt <= index + 1 || J.smiles.SmilesParser.getChar (pattern, ipt + 1) != '\"') break;
var key = pattern.substring (index, ipt);
if (key.lastIndexOf ('$') > 0 || key.indexOf (']') > 0) throw  new J.smiles.InvalidSmilesException ("Invalid variable name: " + key);
var s = J.smiles.SmilesParser.getSubPattern (pattern, ipt + 1, '\"');
keys.addLast ("[" + key + "]");
values.addLast (s);
ipt += s.length + 2;
ipt = J.smiles.SmilesParser.skipTo (pattern, ipt, ';');
iptLast = ++ipt;
}
if (iptLast < 0) return pattern;
return J.util.TextFormat.replaceStrings (pattern.substring (iptLast), keys, values);
}, $fz.isPrivate = true, $fz), "~S");
$_M(c$, "parseAtom", 
($fz = function (molecule, atomSet, pattern, currentAtom, bond, isBracketed, isPrimitive, isBranchAtom) {
if (pattern == null || pattern.length == 0) throw  new J.smiles.InvalidSmilesException ("Empty atom definition");
var newAtom = (atomSet == null ? molecule.addAtom () : isPrimitive ? atomSet.addPrimitive () : atomSet.addAtomOr ());
if (this.braceCount > 0) newAtom.selected = true;
if (!this.checkLogic (molecule, pattern, newAtom, null, currentAtom, isPrimitive, isBranchAtom)) {
var ret =  Clazz.newIntArray (1, 0);
if (this.isBioSequence && pattern.length == 1) pattern += ".0";
var ch = pattern.charAt (0);
var index = 0;
var isNot = false;
if (this.isSmarts && ch == '!') {
ch = J.smiles.SmilesParser.getChar (pattern, ++index);
if (ch == '\0') throw  new J.smiles.InvalidSmilesException ("invalid '!'");
newAtom.not = isNot = true;
}var hydrogenCount = -2147483648;
var biopt = pattern.indexOf ('.');
if (biopt >= 0) {
var name = pattern.substring (index, biopt);
if (name.length == 0) name = "*";
if (name.length > 1) newAtom.residueName = name.toUpperCase ();
 else if (!name.equals ("*")) newAtom.residueChar = name;
name = pattern.substring (biopt + 1).toUpperCase ();
if ((biopt = name.indexOf ("#")) >= 0) {
J.smiles.SmilesParser.getDigits (name, biopt + 1, ret);
newAtom.elementNumber = ret[0];
name = name.substring (0, biopt);
}if (name.length == 0) name = "*";
if (!name.equals ("*")) newAtom.setAtomName (name);
ch = '\0';
}newAtom.setBioAtom (this.bioType);
while (ch != '\0') {
newAtom.setAtomName (this.isBioSequence ? "0" : "");
if (Character.isDigit (ch)) {
index = J.smiles.SmilesParser.getDigits (pattern, index, ret);
var mass = ret[0];
if (mass == -2147483648) throw  new J.smiles.InvalidSmilesException ("Non numeric atomic mass");
if (J.smiles.SmilesParser.getChar (pattern, index) == '?') {
index++;
mass = -mass;
}newAtom.setAtomicMass (mass);
} else {
switch (ch) {
case '"':
var type = J.util.Parser.getQuotedStringAt (pattern, index);
index += type.length + 2;
newAtom.setAtomType (type);
break;
case '_':
index = J.smiles.SmilesParser.getDigits (pattern, index + 1, ret) + 1;
if (ret[0] == -2147483648) throw  new J.smiles.InvalidSmilesException ("Invalid SEARCH primitive: " + pattern.substring (index));
newAtom.iNested = ret[0];
if (this.isBioSequence && isBracketed) {
if (index != pattern.length) throw  new J.smiles.InvalidSmilesException ("invalid characters: " + pattern.substring (index));
}break;
case '=':
index = J.smiles.SmilesParser.getDigits (pattern, index + 1, ret);
newAtom.jmolIndex = ret[0];
break;
case '#':
index = J.smiles.SmilesParser.getDigits (pattern, index + 1, ret);
newAtom.elementNumber = ret[0];
break;
case '-':
case '+':
index = this.checkCharge (pattern, index, newAtom);
break;
case '@':
molecule.haveAtomStereochemistry = true;
index = this.checkChirality (pattern, index, molecule.patternAtoms[newAtom.index]);
break;
default:
var nextChar = J.smiles.SmilesParser.getChar (pattern, index + 1);
var sym2 = pattern.substring (index + 1, index + (Character.isLowerCase (nextChar) && (!isBracketed || !Character.isDigit (J.smiles.SmilesParser.getChar (pattern, index + 2))) ? 2 : 1));
var symbol = Character.toUpperCase (ch) + sym2;
var mustBeSymbol = true;
var checkForPrimitive = (isBracketed && Character.isLetter (ch));
if (checkForPrimitive) {
if (!isNot && (isPrimitive ? atomSet : newAtom).hasSymbol) {
mustBeSymbol = false;
} else if (ch == 'H') {
mustBeSymbol = !Character.isDigit (nextChar) || J.smiles.SmilesParser.getChar (pattern, index + 2) == '?';
} else if ("DdhRrvXx".indexOf (ch) >= 0 && Character.isDigit (nextChar)) {
mustBeSymbol = false;
} else if (!symbol.equals ("A") && !symbol.equals ("Xx")) {
mustBeSymbol = (J.util.Elements.elementNumberFromSymbol (symbol, true) > 0);
if (!mustBeSymbol && sym2 !== "") {
sym2 = "";
symbol = symbol.substring (0, 1);
mustBeSymbol = (J.util.Elements.elementNumberFromSymbol (symbol, true) > 0);
}}}if (mustBeSymbol) {
if (!isBracketed && !this.isSmarts && !this.isBioSequence && !J.smiles.SmilesAtom.allowSmilesUnbracketed (symbol) || !newAtom.setSymbol (symbol = ch + sym2)) throw  new J.smiles.InvalidSmilesException ("Invalid atom symbol: " + symbol);
if (isPrimitive) atomSet.hasSymbol = true;
index += symbol.length;
} else {
index = J.smiles.SmilesParser.getDigits (pattern, index + 1, ret);
var val = ret[0];
switch (ch) {
default:
throw  new J.smiles.InvalidSmilesException ("Invalid SEARCH primitive: " + pattern.substring (index));
case 'D':
newAtom.setDegree (val == -2147483648 ? 1 : val);
break;
case 'd':
newAtom.setNonhydrogenDegree (val == -2147483648 ? 1 : val);
break;
case 'H':
hydrogenCount = (val == -2147483648 ? 1 : val);
break;
case 'h':
newAtom.setImplicitHydrogenCount (val == -2147483648 ? -1 : val);
break;
case 'R':
if (val == -2147483648) val = -1;
newAtom.setRingMembership (val);
molecule.top.needRingData = true;
break;
case 'r':
if (val == -2147483648) {
val = -1;
newAtom.setRingMembership (val);
} else {
newAtom.setRingSize (val);
switch (val) {
case 500:
val = 5;
break;
case 600:
val = 6;
break;
}
if (val > molecule.ringDataMax) molecule.ringDataMax = val;
}molecule.top.needRingData = true;
break;
case 'v':
newAtom.setValence (val == -2147483648 ? 1 : val);
break;
case 'X':
newAtom.setConnectivity (val == -2147483648 ? 1 : val);
break;
case 'x':
newAtom.setRingConnectivity (val == -2147483648 ? -1 : val);
molecule.top.needRingData = true;
break;
}
}}
}ch = J.smiles.SmilesParser.getChar (pattern, index);
if (isNot && ch != '\0') throw  new J.smiles.InvalidSmilesException ("'!' may only involve one primitive.");
}
if (hydrogenCount == -2147483648 && isBracketed) hydrogenCount = -2147483647;
newAtom.setExplicitHydrogenCount (hydrogenCount);
molecule.patternAtoms[newAtom.index].setExplicitHydrogenCount (hydrogenCount);
}if (currentAtom != null && bond.order == 0) {
newAtom.notBondedIndex = currentAtom.index;
}if (currentAtom != null && bond.order != 0) {
if (bond.order == -1) bond.order = (this.isBioSequence && isBranchAtom ? 112 : this.isSmarts || currentAtom.isAromatic () && newAtom.isAromatic () ? 81 : 1);
if (!isBracketed) bond.set2a (null, newAtom);
if (this.branchLevel == 0 && (bond.order == 17 || bond.order == 112)) this.branchLevel++;
}if (this.branchLevel == 0) molecule.lastChainAtom = newAtom;
return newAtom;
}, $fz.isPrivate = true, $fz), "J.smiles.SmilesSearch,J.smiles.SmilesAtom,~S,J.smiles.SmilesAtom,J.smiles.SmilesBond,~B,~B,~B");
$_M(c$, "parseRing", 
($fz = function (molecule, ringNum, currentAtom, bond) {
var r = Integer.$valueOf (ringNum);
var bond0 = this.ringBonds.get (r);
if (bond0 == null) {
this.ringBonds.put (r, bond);
return;
}this.ringBonds.remove (r);
switch (bond.order) {
case -1:
bond.order = (bond0.order != -1 ? bond0.order : this.isSmarts || currentAtom.isAromatic () && bond0.getAtom1 ().isAromatic () ? 81 : 1);
break;
case 257:
bond.order = 513;
break;
case 513:
bond.order = 257;
break;
}
if (bond0.order != -1 && bond0.order != bond.order) throw  new J.smiles.InvalidSmilesException ("Incoherent bond type for ring");
bond0.set (bond);
currentAtom.bondCount--;
bond0.setAtom2 (currentAtom);
}, $fz.isPrivate = true, $fz), "J.smiles.SmilesSearch,~N,J.smiles.SmilesAtom,J.smiles.SmilesBond");
$_M(c$, "checkCharge", 
($fz = function (pattern, index, newAtom) {
var len = pattern.length;
var ch = pattern.charAt (index);
var count = 1;
++index;
if (index < len) {
var nextChar = pattern.charAt (index);
if (Character.isDigit (nextChar)) {
var ret =  Clazz.newIntArray (1, 0);
index = J.smiles.SmilesParser.getDigits (pattern, index, ret);
count = ret[0];
if (count == -2147483648) throw  new J.smiles.InvalidSmilesException ("Non numeric charge");
} else {
while (index < len && pattern.charAt (index) == ch) {
index++;
count++;
}
}}newAtom.setCharge (ch == '+' ? count : -count);
return index;
}, $fz.isPrivate = true, $fz), "~S,~N,J.smiles.SmilesAtom");
$_M(c$, "checkChirality", 
($fz = function (pattern, index, newAtom) {
var stereoClass = 0;
var order = -2147483648;
var len = pattern.length;
var ch;
stereoClass = 0;
order = 1;
if (++index < len) {
switch (ch = pattern.charAt (index)) {
case '@':
order = 2;
index++;
break;
case 'H':
break;
case 'A':
case 'D':
case 'E':
case 'O':
case 'S':
case 'T':
stereoClass = (index + 1 < len ? J.smiles.SmilesAtom.getChiralityClass (pattern.substring (index, index + 2)) : -1);
index += 2;
break;
default:
order = (Character.isDigit (ch) ? 1 : -1);
}
var pt = index;
if (order == 1) {
while (pt < len && Character.isDigit (pattern.charAt (pt))) pt++;

if (pt > index) {
try {
order = Integer.parseInt (pattern.substring (index, pt));
} catch (e) {
if (Clazz.exceptionOf (e, NumberFormatException)) {
order = -1;
} else {
throw e;
}
}
index = pt;
}}if (order < 1 || stereoClass < 0) throw  new J.smiles.InvalidSmilesException ("Invalid stereochemistry descriptor");
}newAtom.setChiralClass (stereoClass);
newAtom.setChiralOrder (order);
if (J.smiles.SmilesParser.getChar (pattern, index) == '?') {
J.util.Logger.info ("Ignoring '?' in stereochemistry");
index++;
}return index;
}, $fz.isPrivate = true, $fz), "~S,~N,J.smiles.SmilesAtom");
$_M(c$, "parseBond", 
($fz = function (molecule, bondSet, pattern, bond, currentAtom, isPrimitive, isBranchAtom) {
var ch = J.smiles.SmilesParser.getChar (pattern, 0);
if (ch == '.') {
if (bond != null || bondSet != null) throw  new J.smiles.InvalidSmilesException ("invalid '.'");
this.isBioSequence = (J.smiles.SmilesParser.getChar (pattern, 1) == '~');
return  new J.smiles.SmilesBond (null, null, 0, false);
}if (ch == '+' && bondSet != null) throw  new J.smiles.InvalidSmilesException ("invalid '+'");
var newBond = (bondSet == null ? (bond == null ?  new J.smiles.SmilesBond (currentAtom, null, (this.isBioSequence && currentAtom != null ? (isBranchAtom ? 112 : 96) : -1), false) : bond) : isPrimitive ? bondSet.addPrimitive () : bondSet.addBondOr ());
if (ch != '\0' && !this.checkLogic (molecule, pattern, null, newBond, currentAtom, isPrimitive, false)) {
var isBondNot = (ch == '!');
if (isBondNot) {
ch = J.smiles.SmilesParser.getChar (pattern, 1);
if (ch == '\0' || ch == '!') throw  new J.smiles.InvalidSmilesException ("invalid '!'");
}var bondType = J.smiles.SmilesBond.getBondTypeFromCode (ch);
if (bondType == 65) molecule.top.needRingMemberships = true;
if (currentAtom == null && bondType != 0) throw  new J.smiles.InvalidSmilesException ("Bond without a previous atom");
switch (bondType) {
case 769:
case 1025:
if (isBondNot) {
isBondNot = false;
bondType = (bondType == 769 ? 1025 : 769);
}molecule.haveBondStereochemistry = true;
break;
case 257:
case 513:
molecule.haveBondStereochemistry = true;
break;
case 17:
break;
case 2:
case 1:
if (currentAtom.isAromatic ()) molecule.top.needRingData = true;
break;
}
newBond.set2 (bondType, isBondNot);
if (this.isBioSequence && bondSet != null) bondSet.set2 (bondType, isBondNot);
}return newBond;
}, $fz.isPrivate = true, $fz), "J.smiles.SmilesSearch,J.smiles.SmilesBond,~S,J.smiles.SmilesBond,J.smiles.SmilesAtom,~B,~B");
$_M(c$, "checkLogic", 
($fz = function (molecule, pattern, atom, bond, currentAtom, isPrimitive, isBranchAtom) {
var pt = pattern.indexOf (',');
var len = pattern.length;
while (true) {
var haveOr = (pt > 0);
if (haveOr && !this.isSmarts || pt == 0) break;
var props = "";
pt = pattern.indexOf (';');
if (pt >= 0) {
if (!this.isSmarts || pt == 0) break;
props = "&" + pattern.substring (pt + 1);
pattern = pattern.substring (0, pt);
if (!haveOr) {
pattern += props;
props = "";
}}var index = 0;
if (haveOr) {
pattern += ",";
while ((pt = pattern.indexOf (',', index)) > 0 && pt <= len) {
var s = pattern.substring (index, pt) + props;
if (s.length == 0) throw  new J.smiles.InvalidSmilesException ("missing " + (bond == null ? "atom" : "bond") + " token");
if (bond == null) this.parseAtom (molecule, atom, s, null, null, true, false, isBranchAtom);
 else this.parseBond (molecule, bond, s, null, currentAtom, false, false);
index = pt + 1;
}
} else if ((pt = pattern.indexOf ('&')) >= 0 || bond != null && len > 1 && !isPrimitive) {
if (!this.isSmarts || pt == 0) break;
if (bond != null && pt < 0) {
if (len > 1) {
var sNew =  new J.util.SB ();
for (var i = 0; i < len; ) {
var ch = pattern.charAt (i++);
sNew.appendC (ch);
if (ch != '!' && i < len) sNew.appendC ('&');
}
pattern = sNew.toString ();
len = pattern.length;
}}pattern += "&";
while ((pt = pattern.indexOf ('&', index)) > 0 && pt <= len) {
var s = pattern.substring (index, pt) + props;
if (bond == null) this.parseAtom (molecule, atom, s, null, null, true, true, isBranchAtom);
 else this.parseBond (molecule, bond, s, null, currentAtom, true, false);
index = pt + 1;
}
} else {
return false;
}return true;
}
var ch = pattern.charAt (pt);
throw  new J.smiles.InvalidSmilesException ((this.isSmarts ? "invalid placement for '" + ch + "'" : "[" + ch + "] notation only valid with SMARTS, not SMILES,") + " in " + pattern);
}, $fz.isPrivate = true, $fz), "J.smiles.SmilesSearch,~S,J.smiles.SmilesAtom,J.smiles.SmilesBond,J.smiles.SmilesAtom,~B,~B");
c$.getSubPattern = $_M(c$, "getSubPattern", 
($fz = function (pattern, index, ch) {
var ch2;
var margin = 1;
switch (ch) {
case '[':
ch2 = ']';
break;
case '"':
case '%':
ch2 = ch;
break;
case '(':
ch2 = ')';
break;
default:
ch2 = ch;
margin = 0;
}
var len = pattern.length;
var pCount = 1;
for (var pt = index + 1; pt < len; pt++) {
var ch1 = pattern.charAt (pt);
if (ch1 == ch2) {
pCount--;
if (pCount == 0) return pattern.substring (index + margin, pt + 1 - margin);
} else if (ch1 == ch) {
pCount++;
}}
throw  new J.smiles.InvalidSmilesException ("Unmatched " + ch);
}, $fz.isPrivate = true, $fz), "~S,~N,~S");
c$.getChar = $_M(c$, "getChar", 
($fz = function (pattern, i) {
return (i < pattern.length ? pattern.charAt (i) : '\0');
}, $fz.isPrivate = true, $fz), "~S,~N");
c$.getDigits = $_M(c$, "getDigits", 
($fz = function (pattern, index, ret) {
var pt = index;
var len = pattern.length;
while (pt < len && Character.isDigit (pattern.charAt (pt))) pt++;

try {
ret[0] = Integer.parseInt (pattern.substring (index, pt));
} catch (e) {
if (Clazz.exceptionOf (e, NumberFormatException)) {
ret[0] = -2147483648;
} else {
throw e;
}
}
return pt;
}, $fz.isPrivate = true, $fz), "~S,~N,~A");
c$.skipTo = $_M(c$, "skipTo", 
($fz = function (pattern, index, ch0) {
var pt = index;
var ch;
while ((ch = J.smiles.SmilesParser.getChar (pattern, ++pt)) != ch0 && ch != '\0') {
}
return (ch == '\0' ? -1 : pt);
}, $fz.isPrivate = true, $fz), "~S,~N,~S");
c$.getRingPointer = $_M(c$, "getRingPointer", 
function (i) {
return (i < 10 ? "" + i : i < 100 ? "%" + i : "%(" + i + ")");
}, "~N");
c$.cleanPattern = $_M(c$, "cleanPattern", 
function (pattern) {
pattern = J.util.TextFormat.replaceAllCharacters (pattern, " \t\n\r", "");
pattern = J.util.TextFormat.simpleReplace (pattern, "^^", "'");
var i = 0;
var i2 = 0;
while ((i = pattern.indexOf ("//*")) >= 0 && (i2 = pattern.indexOf ("*//")) >= i) pattern = pattern.substring (0, i) + pattern.substring (i2 + 3);

pattern = J.util.TextFormat.simpleReplace (pattern, "//", "");
return pattern;
}, "~S");
});
