Clazz.declarePackage ("JS");
Clazz.load (["JU.M4"], "JS.SymmetryOperation", ["java.lang.Boolean", "$.Character", "$.Float", "java.util.Hashtable", "JU.Matrix", "$.P3", "$.PT", "$.SB", "$.V3", "JU.Logger", "$.Parser"], function () {
c$ = Clazz.decorateAsClass (function () {
this.xyzOriginal = null;
this.xyzCanonical = null;
this.xyz = null;
this.doNormalize = true;
this.isFinalized = false;
this.opId = 0;
this.centering = null;
this.myLabels = null;
this.modDim = 0;
this.linearRotTrans = null;
this.rsvs = null;
this.isBio = false;
this.sigma = null;
this.number = 0;
this.subsystemCode = null;
this.timeReversal = 0;
this.unCentered = false;
this.isCenteringOp = false;
this.magOp = 3.4028235E38;
this.divisor = 12;
this.info = null;
Clazz.instantialize (this, arguments);
}, JS, "SymmetryOperation", JU.M4);
Clazz.defineMethod (c$, "setSigma", 
function (subsystemCode, sigma) {
this.subsystemCode = subsystemCode;
this.sigma = sigma;
}, "~S,JU.Matrix");
Clazz.makeConstructor (c$, 
function (op, atoms, atomIndex, countOrId, doNormalize) {
Clazz.superConstructor (this, JS.SymmetryOperation, []);
this.doNormalize = doNormalize;
if (op == null) {
this.opId = countOrId;
return;
}this.xyzOriginal = op.xyzOriginal;
this.xyz = op.xyz;
this.divisor = op.divisor;
this.opId = op.opId;
this.modDim = op.modDim;
this.myLabels = op.myLabels;
this.number = op.number;
this.linearRotTrans = op.linearRotTrans;
this.sigma = op.sigma;
this.subsystemCode = op.subsystemCode;
this.timeReversal = op.timeReversal;
this.setMatrix (false);
if (!op.isFinalized) this.doFinalize ();
if (doNormalize && this.sigma == null) JS.SymmetryOperation.setOffset (this, atoms, atomIndex, countOrId);
}, "JS.SymmetryOperation,~A,~N,~N,~B");
Clazz.defineMethod (c$, "setGamma", 
 function (isReverse) {
var n = 3 + this.modDim;
var a = (this.rsvs =  new JU.Matrix (null, n + 1, n + 1)).getArray ();
var t =  Clazz.newDoubleArray (n, 0);
var pt = 0;
for (var i = 0; i < n; i++) {
for (var j = 0; j < n; j++) a[i][j] = this.linearRotTrans[pt++];

t[i] = (isReverse ? -1 : 1) * this.linearRotTrans[pt++];
}
a[n][n] = 1;
if (isReverse) this.rsvs = this.rsvs.inverse ();
for (var i = 0; i < n; i++) a[i][n] = t[i];

a = this.rsvs.getSubmatrix (0, 0, 3, 3).getArray ();
for (var i = 0; i < 3; i++) for (var j = 0; j < 4; j++) this.setElement (i, j, (j < 3 ? a[i][j] : t[i]));


this.setElement (3, 3, 1);
}, "~B");
Clazz.defineMethod (c$, "doFinalize", 
function () {
JS.SymmetryOperation.div12 (this, this.divisor);
if (this.modDim > 0) {
var a = this.rsvs.getArray ();
for (var i = a.length - 1; --i >= 0; ) a[i][3 + this.modDim] = JS.SymmetryOperation.finalizeD (a[i][3 + this.modDim], this.divisor);

}this.isFinalized = true;
});
c$.div12 = Clazz.defineMethod (c$, "div12", 
 function (op, divisor) {
op.m03 = JS.SymmetryOperation.finalizeF (op.m03, divisor);
op.m13 = JS.SymmetryOperation.finalizeF (op.m13, divisor);
op.m23 = JS.SymmetryOperation.finalizeF (op.m23, divisor);
return op;
}, "JU.M4,~N");
c$.finalizeF = Clazz.defineMethod (c$, "finalizeF", 
 function (m, divisor) {
if (divisor == 0) {
if (m == 0) return 0;
var n = Clazz.floatToInt (m);
return ((n >> 8) * 1 / (n & 255));
}return m / divisor;
}, "~N,~N");
c$.finalizeD = Clazz.defineMethod (c$, "finalizeD", 
 function (m, divisor) {
if (divisor == 0) {
if (m == 0) return 0;
var n = Clazz.doubleToInt (m);
return ((n >> 8) * 1 / (n & 255));
}return m / divisor;
}, "~N,~N");
Clazz.defineMethod (c$, "getXyz", 
function (normalized) {
return (normalized && this.modDim == 0 || this.xyzOriginal == null ? this.xyz : this.xyzOriginal);
}, "~B");
Clazz.defineMethod (c$, "getxyzTrans", 
function (t) {
var m = JU.M4.newM4 (this);
m.add (t);
return JS.SymmetryOperation.getXYZFromMatrix (m, false, false, false);
}, "JU.P3");
c$.newPoint = Clazz.defineMethod (c$, "newPoint", 
function (m, atom1, atom2, x, y, z) {
m.rotTrans2 (atom1, atom2);
atom2.add3 (x, y, z);
}, "JU.M4,JU.P3,JU.P3,~N,~N,~N");
Clazz.defineMethod (c$, "dumpInfo", 
function () {
return "\n" + this.xyz + "\ninternal matrix representation:\n" + this.toString ();
});
c$.dumpSeitz = Clazz.defineMethod (c$, "dumpSeitz", 
function (s, isCanonical) {
var sb =  new JU.SB ();
var r =  Clazz.newFloatArray (4, 0);
for (var i = 0; i < 3; i++) {
s.getRow (i, r);
sb.append ("[\t");
for (var j = 0; j < 3; j++) sb.appendI (Clazz.floatToInt (r[j])).append ("\t");

var trans = r[3];
if (trans != Clazz.floatToInt (trans)) trans = 12 * trans;
sb.append (JS.SymmetryOperation.twelfthsOf (isCanonical ? JS.SymmetryOperation.normalizeTwelfths (trans / 12, 12, true) : Clazz.floatToInt (trans))).append ("\t]\n");
}
return sb.toString ();
}, "JU.M4,~B");
Clazz.defineMethod (c$, "setMatrixFromXYZ", 
function (xyz, modDim, allowScaling) {
if (xyz == null) return false;
this.xyzOriginal = xyz;
this.divisor = JS.SymmetryOperation.setDivisor (xyz);
xyz = xyz.toLowerCase ();
this.setModDim (modDim);
var isReverse = (xyz.startsWith ("!"));
if (isReverse) xyz = xyz.substring (1);
if (xyz.indexOf ("xyz matrix:") == 0) {
this.xyz = xyz;
JU.Parser.parseStringInfestedFloatArray (xyz, null, this.linearRotTrans);
return this.setFromMatrix (null, isReverse);
}if (xyz.indexOf ("[[") == 0) {
xyz = xyz.$replace ('[', ' ').$replace (']', ' ').$replace (',', ' ');
JU.Parser.parseStringInfestedFloatArray (xyz, null, this.linearRotTrans);
for (var i = this.linearRotTrans.length; --i >= 0; ) if (Float.isNaN (this.linearRotTrans[i])) return false;

this.setMatrix (isReverse);
this.isFinalized = true;
this.isBio = (xyz.indexOf ("bio") >= 0);
this.xyz = (this.isBio ? this.toString () : JS.SymmetryOperation.getXYZFromMatrix (this, false, false, false));
return true;
}if (modDim == 0 && xyz.indexOf ("x4") >= 0) {
for (var i = 14; --i >= 4; ) {
if (xyz.indexOf ("x" + i) >= 0) {
this.setModDim (i - 3);
break;
}}
}var mxyz = null;
if (xyz.endsWith ("m")) {
this.timeReversal = (xyz.indexOf ("-m") >= 0 ? -1 : 1);
allowScaling = true;
} else if (xyz.indexOf ("mz)") >= 0) {
var pt = xyz.indexOf ("(");
mxyz = xyz.substring (pt + 1, xyz.length - 1);
xyz = xyz.substring (0, pt);
allowScaling = false;
}var strOut = JS.SymmetryOperation.getMatrixFromString (this, xyz, this.linearRotTrans, allowScaling);
if (strOut == null) return false;
this.xyzCanonical = strOut;
if (mxyz != null) {
var isProper = (JU.M4.newA16 (this.linearRotTrans).determinant3 () == 1);
this.timeReversal = (((xyz.indexOf ("-x") < 0) == (mxyz.indexOf ("-mx") < 0)) == isProper ? 1 : -1);
}this.setMatrix (isReverse);
this.xyz = (isReverse ? JS.SymmetryOperation.getXYZFromMatrix (this, true, false, false) : this.doNormalize ? strOut : xyz);
if (this.timeReversal != 0) this.xyz += (this.timeReversal == 1 ? ",m" : ",-m");
if (JU.Logger.debugging) JU.Logger.debug ("" + this);
return true;
}, "~S,~N,~B");
c$.setDivisor = Clazz.defineMethod (c$, "setDivisor", 
 function (xyz) {
var pt = xyz.indexOf ('/');
var len = xyz.length;
while (pt > 0 && pt < len - 1) {
var c = xyz.charAt (pt + 1);
if ("2346".indexOf (c) < 0 || pt < len - 2 && Character.isDigit (xyz.charAt (pt + 2))) {
return 0;
}pt = xyz.indexOf ('/', pt + 1);
}
return 12;
}, "~S");
Clazz.defineMethod (c$, "setModDim", 
 function (dim) {
var n = (dim + 4) * (dim + 4);
this.modDim = dim;
if (dim > 0) this.myLabels = JS.SymmetryOperation.labelsXn;
this.linearRotTrans =  Clazz.newFloatArray (n, 0);
}, "~N");
Clazz.defineMethod (c$, "setMatrix", 
 function (isReverse) {
if (this.linearRotTrans.length > 16) {
this.setGamma (isReverse);
} else {
this.setA (this.linearRotTrans);
if (isReverse) {
var p3 = JU.P3.new3 (this.m03, this.m13, this.m23);
this.invert ();
this.rotate (p3);
p3.scale (-1);
this.setTranslation (p3);
}}}, "~B");
Clazz.defineMethod (c$, "setFromMatrix", 
function (offset, isReverse) {
var v = 0;
var pt = 0;
this.myLabels = (this.modDim == 0 ? JS.SymmetryOperation.labelsXYZ : JS.SymmetryOperation.labelsXn);
var rowPt = 0;
var n = 3 + this.modDim;
for (var i = 0; rowPt < n; i++) {
if (Float.isNaN (this.linearRotTrans[i])) return false;
v = this.linearRotTrans[i];
if (Math.abs (v) < 0.00001) v = 0;
var isTrans = ((i + 1) % (n + 1) == 0);
if (isTrans) {
var denom = (this.divisor == 0 ? (Clazz.floatToInt (v)) & 255 : this.divisor);
if (denom == 0) denom = 12;
v = JS.SymmetryOperation.finalizeF (v, this.divisor);
if (offset != null) {
if (pt < offset.length) v += offset[pt++];
}v = JS.SymmetryOperation.normalizeTwelfths ((v < 0 ? -1 : 1) * Math.abs (v * denom) / denom, denom, this.doNormalize);
if (this.divisor == 0) v = JS.SymmetryOperation.toDivisor (v, denom);
rowPt++;
}this.linearRotTrans[i] = v;
}
this.linearRotTrans[this.linearRotTrans.length - 1] = this.divisor;
this.setMatrix (isReverse);
this.isFinalized = (offset == null);
this.xyz = JS.SymmetryOperation.getXYZFromMatrix (this, true, false, false);
return true;
}, "~A,~B");
c$.getMatrixFromXYZ = Clazz.defineMethod (c$, "getMatrixFromXYZ", 
function (xyz) {
var linearRotTrans =  Clazz.newFloatArray (16, 0);
xyz = JS.SymmetryOperation.getMatrixFromString (null, "!" + xyz, linearRotTrans, false);
return (xyz == null ? null : JS.SymmetryOperation.div12 (JU.M4.newA16 (linearRotTrans), JS.SymmetryOperation.setDivisor (xyz)));
}, "~S");
c$.getMatrixFromString = Clazz.defineMethod (c$, "getMatrixFromString", 
function (op, xyz, linearRotTrans, allowScaling) {
var isDenominator = false;
var isDecimal = false;
var isNegative = false;
var modDim = (op == null ? 0 : op.modDim);
var nRows = 4 + modDim;
var divisor = (op == null ? JS.SymmetryOperation.setDivisor (xyz) : op.divisor);
var doNormalize = (op == null ? !xyz.startsWith ("!") : op.doNormalize);
var dimOffset = (modDim > 0 ? 3 : 0);
linearRotTrans[linearRotTrans.length - 1] = 1;
var transPt = xyz.indexOf (';') + 1;
if (transPt != 0) {
allowScaling = true;
if (transPt == xyz.length) xyz += "0,0,0";
}var rotPt = -1;
var myLabels = (op == null || modDim == 0 ? null : op.myLabels);
if (myLabels == null) myLabels = JS.SymmetryOperation.labelsXYZ;
xyz = xyz.toLowerCase () + ",";
xyz = xyz.$replace ('(', ',');
if (modDim > 0) xyz = JS.SymmetryOperation.replaceXn (xyz, modDim + 3);
var xpt = 0;
var tpt0 = 0;
var rowPt = 0;
var ch;
var iValue = 0;
var denom = 0;
var numer = 0;
var decimalMultiplier = 1;
var strT = "";
var strOut = "";
var ret =  Clazz.newIntArray (1, 0);
var len = xyz.length;
for (var i = 0; i < len; i++) {
switch (ch = xyz.charAt (i)) {
case ';':
break;
case '\'':
case ' ':
case '{':
case '}':
case '!':
continue;
case '-':
isNegative = true;
continue;
case '+':
isNegative = false;
continue;
case '/':
denom = 0;
isDenominator = true;
continue;
case 'x':
case 'y':
case 'z':
case 'a':
case 'b':
case 'c':
case 'd':
case 'e':
case 'f':
case 'g':
case 'h':
tpt0 = rowPt * nRows;
var ipt = (ch >= 'x' ? ch.charCodeAt (0) - 120 : ch.charCodeAt (0) - 97 + dimOffset);
xpt = tpt0 + ipt;
var val = (isNegative ? -1 : 1);
if (allowScaling && iValue != 0) {
linearRotTrans[xpt] = iValue;
val = Clazz.floatToInt (iValue);
iValue = 0;
} else {
linearRotTrans[xpt] = val;
}strT += JS.SymmetryOperation.plusMinus (strT, val, myLabels[ipt]);
break;
case ',':
if (transPt != 0) {
if (transPt > 0) {
rotPt = i;
i = transPt - 1;
transPt = -i;
iValue = 0;
denom = 0;
continue;
}transPt = i + 1;
i = rotPt;
}iValue = JS.SymmetryOperation.normalizeTwelfths (iValue, denom == 0 ? 12 : divisor == 0 ? denom : divisor, doNormalize);
linearRotTrans[tpt0 + nRows - 1] = (divisor == 0 && denom > 0 ? iValue = JS.SymmetryOperation.toDivisor (numer, denom) : iValue);
strT += JS.SymmetryOperation.xyzFraction12 (iValue, (divisor == 0 ? denom : divisor), false, true);
strOut += (strOut === "" ? "" : ",") + strT;
if (rowPt == nRows - 2) return strOut;
iValue = 0;
numer = 0;
denom = 0;
strT = "";
if (rowPt++ > 2 && modDim == 0) {
JU.Logger.warn ("Symmetry Operation? " + xyz);
return null;
}break;
case '.':
isDecimal = true;
decimalMultiplier = 1;
continue;
case '0':
if (!isDecimal && divisor == 12 && (isDenominator || !allowScaling)) continue;
default:
var ich = ch.charCodeAt (0) - 48;
if (ich >= 0 && ich <= 9) {
if (isDecimal) {
decimalMultiplier /= 10;
if (iValue < 0) isNegative = true;
iValue += decimalMultiplier * ich * (isNegative ? -1 : 1);
continue;
}if (isDenominator) {
ret[0] = i;
denom = JU.PT.parseIntNext (xyz, ret);
if (denom < 0) return null;
i = ret[0] - 1;
if (iValue == 0) {
linearRotTrans[xpt] /= denom;
} else {
numer = Clazz.floatToInt (iValue);
iValue /= denom;
}} else {
iValue = iValue * 10 + (isNegative ? -1 : 1) * ich;
isNegative = false;
}} else {
JU.Logger.warn ("symmetry character?" + ch);
}}
isDecimal = isDenominator = isNegative = false;
}
return null;
}, "JS.SymmetryOperation,~S,~A,~B");
c$.replaceXn = Clazz.defineMethod (c$, "replaceXn", 
function (xyz, n) {
for (var i = n; --i >= 0; ) xyz = JU.PT.rep (xyz, JS.SymmetryOperation.labelsXn[i], JS.SymmetryOperation.labelsXnSub[i]);

return xyz;
}, "~S,~N");
c$.toDivisor = Clazz.defineMethod (c$, "toDivisor", 
 function (numer, denom) {
var n = Clazz.floatToInt (numer);
if (n != numer) {
var f = numer - n;
denom = Clazz.floatToInt (Math.abs (denom / f));
n = Clazz.floatToInt (Math.abs (numer) / f);
}return ((n << 8) + denom);
}, "~N,~N");
c$.xyzFraction12 = Clazz.defineMethod (c$, "xyzFraction12", 
 function (n12ths, denom, allPositive, halfOrLess) {
var n = n12ths;
if (denom != 12) {
var $in = Clazz.floatToInt (n);
denom = ($in & 255);
n = $in >> 8;
}var half = (Clazz.doubleToInt (denom / 2));
if (allPositive) {
while (n < 0) n += denom;

} else if (halfOrLess) {
while (n > half) n -= denom;

while (n < -half) n += denom;

}var s = (denom == 12 ? JS.SymmetryOperation.twelfthsOf (n) : n == 0 ? "0" : n + "/" + denom);
return (s.charAt (0) == '0' ? "" : n > 0 ? "+" + s : s);
}, "~N,~N,~B,~B");
c$.twelfthsOf = Clazz.defineMethod (c$, "twelfthsOf", 
function (n12ths) {
var str = "";
if (n12ths < 0) {
n12ths = -n12ths;
str = "-";
}var m = 12;
var n = Math.round (n12ths);
if (Math.abs (n - n12ths) > 0.01) {
var f = n12ths / 12;
var max = 20;
for (m = 3; m < max; m++) {
var fm = f * m;
n = Math.round (fm);
if (Math.abs (n - fm) < 0.01) break;
}
if (m == max) return str + f;
} else {
if (n == 12) return str + "1";
if (n < 12) return str + JS.SymmetryOperation.twelfths[n % 12];
switch (n % 12) {
case 0:
return "" + Clazz.doubleToInt (n / 12);
case 2:
case 10:
m = 6;
break;
case 3:
case 9:
m = 4;
break;
case 4:
case 8:
m = 3;
break;
case 6:
m = 2;
break;
default:
break;
}
n = (Clazz.doubleToInt (n * m / 12));
}return str + n + "/" + m;
}, "~N");
c$.plusMinus = Clazz.defineMethod (c$, "plusMinus", 
 function (strT, x, sx) {
return (x == 0 ? "" : (x < 0 ? "-" : strT.length == 0 ? "" : "+") + (x == 1 || x == -1 ? "" : "" + Clazz.floatToInt (Math.abs (x))) + sx);
}, "~S,~N,~S");
c$.normalizeTwelfths = Clazz.defineMethod (c$, "normalizeTwelfths", 
 function (iValue, divisor, doNormalize) {
iValue *= divisor;
var half = Clazz.doubleToInt (divisor / 2);
if (doNormalize) {
while (iValue > half) iValue -= divisor;

while (iValue <= -half) iValue += divisor;

}return iValue;
}, "~N,~N,~B");
c$.getXYZFromMatrix = Clazz.defineMethod (c$, "getXYZFromMatrix", 
function (mat, is12ths, allPositive, halfOrLess) {
var str = "";
var op = (Clazz.instanceOf (mat, JS.SymmetryOperation) ? mat : null);
if (op != null && op.modDim > 0) return JS.SymmetryOperation.getXYZFromRsVs (op.rsvs.getRotation (), op.rsvs.getTranslation (), is12ths);
var row =  Clazz.newFloatArray (4, 0);
var denom = Clazz.floatToInt (mat.getElement (3, 3));
if (denom == 1) denom = 12;
 else mat.setElement (3, 3, 1);
for (var i = 0; i < 3; i++) {
var lpt = (i < 3 ? 0 : 3);
mat.getRow (i, row);
var term = "";
for (var j = 0; j < 3; j++) if (row[j] != 0) term += JS.SymmetryOperation.plusMinus (term, row[j], JS.SymmetryOperation.labelsXYZ[j + lpt]);

term += JS.SymmetryOperation.xyzFraction12 ((is12ths ? row[3] : row[3] * denom), denom, allPositive, halfOrLess);
str += "," + term;
}
return str.substring (1);
}, "JU.M4,~B,~B,~B");
c$.setOffset = Clazz.defineMethod (c$, "setOffset", 
function (m, atoms, atomIndex, count) {
if (count == 0) return;
var x = 0;
var y = 0;
var z = 0;
if (JS.SymmetryOperation.atomTest == null) JS.SymmetryOperation.atomTest =  new JU.P3 ();
for (var i = atomIndex, i2 = i + count; i < i2; i++) {
JS.SymmetryOperation.newPoint (m, atoms[i], JS.SymmetryOperation.atomTest, 0, 0, 0);
x += JS.SymmetryOperation.atomTest.x;
y += JS.SymmetryOperation.atomTest.y;
z += JS.SymmetryOperation.atomTest.z;
}
x /= count;
y /= count;
z /= count;
while (x < -0.001 || x >= 1.001) {
m.m03 += (x < 0 ? 1 : -1);
x += (x < 0 ? 1 : -1);
}
while (y < -0.001 || y >= 1.001) {
m.m13 += (y < 0 ? 1 : -1);
y += (y < 0 ? 1 : -1);
}
while (z < -0.001 || z >= 1.001) {
m.m23 += (z < 0 ? 1 : -1);
z += (z < 0 ? 1 : -1);
}
}, "JU.M4,~A,~N,~N");
Clazz.defineMethod (c$, "rotateAxes", 
function (vectors, unitcell, ptTemp, mTemp) {
var vRot =  new Array (3);
this.getRotationScale (mTemp);
for (var i = vectors.length; --i >= 0; ) {
ptTemp.setT (vectors[i]);
unitcell.toFractional (ptTemp, true);
mTemp.rotate (ptTemp);
unitcell.toCartesian (ptTemp, true);
vRot[i] = JU.V3.newV (ptTemp);
}
return vRot;
}, "~A,JS.UnitCell,JU.P3,JU.M3");
Clazz.defineMethod (c$, "fcoord2", 
function (p) {
if (this.divisor == 12) return JS.SymmetryOperation.fcoord (p);
return this.fc2 (this.linearRotTrans[3]) + " " + this.fc2 (this.linearRotTrans[7]) + " " + this.fc2 (this.linearRotTrans[11]);
}, "JU.T3");
Clazz.defineMethod (c$, "fc2", 
 function (f) {
var num = Clazz.floatToInt (f);
var denom = (num & 255);
num = num >> 8;
return (num == 0 ? "0" : num + "/" + denom);
}, "~N");
c$.fcoord = Clazz.defineMethod (c$, "fcoord", 
function (p) {
return JS.SymmetryOperation.fc (p.x) + " " + JS.SymmetryOperation.fc (p.y) + " " + JS.SymmetryOperation.fc (p.z);
}, "JU.T3");
c$.fc = Clazz.defineMethod (c$, "fc", 
 function (x) {
var xabs = Math.abs (x);
var m = (x < 0 ? "-" : "");
var x24 = Clazz.floatToInt (JS.SymmetryOperation.approxF (xabs * 24));
if (x24 / 24 == Clazz.floatToInt (x24 / 24)) return m + (Clazz.doubleToInt (x24 / 24));
if (x24 % 8 != 0) {
return m + JS.SymmetryOperation.twelfthsOf (x24 >> 1);
}return (x24 == 0 ? "0" : x24 == 24 ? m + "1" : m + (Clazz.doubleToInt (x24 / 8)) + "/3");
}, "~N");
c$.approxF = Clazz.defineMethod (c$, "approxF", 
function (f) {
return JU.PT.approx (f, 100);
}, "~N");
c$.getXYZFromRsVs = Clazz.defineMethod (c$, "getXYZFromRsVs", 
function (rs, vs, is12ths) {
var ra = rs.getArray ();
var va = vs.getArray ();
var d = ra.length;
var s = "";
for (var i = 0; i < d; i++) {
s += ",";
for (var j = 0; j < d; j++) {
var r = ra[i][j];
if (r != 0) {
s += (r < 0 ? "-" : s.endsWith (",") ? "" : "+") + (Math.abs (r) == 1 ? "" : "" + Clazz.doubleToInt (Math.abs (r))) + "x" + (j + 1);
}}
s += JS.SymmetryOperation.xyzFraction12 (Clazz.doubleToInt (va[i][0] * (is12ths ? 1 : 12)), 12, false, true);
}
return JU.PT.rep (s.substring (1), ",+", ",");
}, "JU.Matrix,JU.Matrix,~B");
Clazz.defineMethod (c$, "toString", 
function () {
return (this.rsvs == null ? Clazz.superCall (this, JS.SymmetryOperation, "toString", []) : Clazz.superCall (this, JS.SymmetryOperation, "toString", []) + " " + this.rsvs.toString ());
});
Clazz.defineMethod (c$, "getMagneticOp", 
function () {
return (this.magOp == 3.4028235E38 ? this.magOp = this.determinant3 () * this.timeReversal : this.magOp);
});
Clazz.defineMethod (c$, "setTimeReversal", 
function (magRev) {
this.timeReversal = magRev;
if (this.xyz.indexOf ("m") >= 0) this.xyz = this.xyz.substring (0, this.xyz.indexOf ("m"));
if (magRev != 0) {
this.xyz += (magRev == 1 ? ",m" : ",-m");
}}, "~N");
Clazz.defineMethod (c$, "getCentering", 
function () {
if (!this.isFinalized) this.doFinalize ();
if (this.centering == null && !this.unCentered) {
if (this.modDim == 0 && this.m00 == 1 && this.m11 == 1 && this.m22 == 1 && this.m01 == 0 && this.m02 == 0 && this.m10 == 0 && this.m12 == 0 && this.m20 == 0 && this.m21 == 0 && (this.m03 != 0 || this.m13 != 0 || this.m23 != 0)) {
this.isCenteringOp = true;
this.centering = JU.V3.new3 (this.m03, this.m13, this.m23);
} else {
this.unCentered = true;
this.centering = null;
}}return this.centering;
});
Clazz.defineMethod (c$, "fixMagneticXYZ", 
function (m, xyz, addMag) {
if (this.timeReversal == 0) return xyz;
var pt = xyz.indexOf ("m");
pt -= Clazz.doubleToInt ((3 - this.timeReversal) / 2);
xyz = (pt < 0 ? xyz : xyz.substring (0, pt));
if (!addMag) return xyz + (this.timeReversal > 0 ? " +1" : " -1");
var m2 = JU.M4.newM4 (m);
m2.m03 = m2.m13 = m2.m23 = 0;
if (this.getMagneticOp () < 0) m2.scale (-1);
xyz += "(" + JU.PT.rep (JU.PT.rep (JU.PT.rep (JS.SymmetryOperation.getXYZFromMatrix (m2, false, false, false), "x", "mx"), "y", "my"), "z", "mz") + ")";
return xyz;
}, "JU.M4,~S,~B");
Clazz.defineMethod (c$, "getInfo", 
function () {
if (this.info == null) {
this.info =  new java.util.Hashtable ();
this.info.put ("xyz", this.xyz);
if (this.centering != null) this.info.put ("centering", this.centering);
this.info.put ("index", Integer.$valueOf (this.number - 1));
this.info.put ("isCenteringOp", Boolean.$valueOf (this.isCenteringOp));
if (this.linearRotTrans != null) this.info.put ("linearRotTrans", this.linearRotTrans);
this.info.put ("modulationDimension", Integer.$valueOf (this.modDim));
this.info.put ("matrix", JU.M4.newM4 (this));
if (this.magOp != 3.4028235E38) this.info.put ("magOp", Float.$valueOf (this.magOp));
this.info.put ("id", Integer.$valueOf (this.opId));
this.info.put ("timeReversal", Integer.$valueOf (this.timeReversal));
if (this.xyzOriginal != null) this.info.put ("xyzOriginal", this.xyzOriginal);
}return this.info;
});
Clazz.defineStatics (c$,
"atomTest", null,
"DIVISOR_MASK", 0xFF,
"DIVISOR_OFFSET", 8,
"twelfths",  Clazz.newArray (-1, ["0", "1/12", "1/6", "1/4", "1/3", "5/12", "1/2", "7/12", "2/3", "3/4", "5/6", "11/12"]));
c$.labelsXYZ = c$.prototype.labelsXYZ =  Clazz.newArray (-1, ["x", "y", "z"]);
c$.labelsXn = c$.prototype.labelsXn =  Clazz.newArray (-1, ["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9", "x10", "x11", "x12", "x13"]);
c$.labelsXnSub = c$.prototype.labelsXnSub =  Clazz.newArray (-1, ["x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]);
});
