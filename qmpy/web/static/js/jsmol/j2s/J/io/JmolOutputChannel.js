Clazz.declarePackage ("J.io");
Clazz.load (["java.io.OutputStream"], "J.io.JmolOutputChannel", ["java.io.BufferedWriter", "$.ByteArrayOutputStream", "$.OutputStreamWriter", "J.util.SB"], function () {
c$ = Clazz.decorateAsClass (function () {
this.fm = null;
this.fileName = null;
this.bw = null;
this.isLocalFile = false;
this.byteCount = 0;
this.isCanceled = false;
this.closed = false;
this.os = null;
this.sb = null;
this.type = null;
Clazz.instantialize (this, arguments);
}, J.io, "JmolOutputChannel", java.io.OutputStream);
$_M(c$, "setParams", 
function (fm, fileName, asWriter, os) {
this.fm = fm;
this.fileName = fileName;
this.os = os;
this.isLocalFile = (fileName != null && !(fileName.startsWith ("http://") || fileName.startsWith ("https://")));
if (asWriter && os != null) this.bw =  new java.io.BufferedWriter ( new java.io.OutputStreamWriter (os));
return this;
}, "J.viewer.FileManager,~S,~B,java.io.OutputStream");
$_M(c$, "getFileName", 
function () {
return this.fileName;
});
$_M(c$, "getByteCount", 
function () {
return this.byteCount;
});
$_M(c$, "setType", 
function (type) {
this.type = type;
}, "~S");
$_M(c$, "getType", 
function () {
return this.type;
});
$_M(c$, "append", 
function (s) {
try {
if (this.bw != null) {
this.bw.write (s);
} else if (this.os == null) {
if (this.sb == null) this.sb =  new J.util.SB ();
this.sb.append (s);
} else {
var b = s.getBytes ();
this.os.write (b, 0, b.length);
this.byteCount += b.length;
return this;
}} catch (e) {
if (Clazz.exceptionOf (e, java.io.IOException)) {
} else {
throw e;
}
}
this.byteCount += s.length;
return this;
}, "~S");
Clazz.overrideMethod (c$, "write", 
function (buf, i, len) {
if (this.os == null) this.os =  new java.io.ByteArrayOutputStream ();
{
this.os.write(buf, i, len);
}this.byteCount += len;
}, "~A,~N,~N");
Clazz.overrideMethod (c$, "writeByteAsInt", 
function (b) {
if (this.os == null) this.os =  new java.io.ByteArrayOutputStream ();
{
this.os.writeByteAsInt(b);
}this.byteCount++;
}, "~N");
$_M(c$, "cancel", 
function () {
this.isCanceled = true;
this.closeChannel ();
});
$_M(c$, "closeChannel", 
function () {
if (this.closed) return null;
try {
if (this.bw != null) {
this.bw.flush ();
this.bw.close ();
} else if (this.os != null) {
this.os.flush ();
this.os.close ();
}} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
} else {
throw e;
}
}
this.closed = true;
if (this.isCanceled) return null;
if (this.fileName == null) return (this.sb == null ? null : this.sb.toString ());
{
var data = (this.sb == null ? this.toByteArray() :
this.sb.toString()); if (typeof this.fileName == "function") {
this.fileName(data); } else { Jmol._doAjax(this.fileName,
null, data); }
}return null;
});
$_M(c$, "toByteArray", 
function () {
return (Clazz.instanceOf (this.os, java.io.ByteArrayOutputStream) ? (this.os).toByteArray () : null);
});
$_M(c$, "close", 
function () {
this.closeChannel ();
});
Clazz.overrideMethod (c$, "toString", 
function () {
if (this.bw != null) try {
this.bw.flush ();
} catch (e) {
if (Clazz.exceptionOf (e, java.io.IOException)) {
} else {
throw e;
}
}
if (this.sb != null) return this.closeChannel ();
return this.byteCount + " bytes";
});
});
