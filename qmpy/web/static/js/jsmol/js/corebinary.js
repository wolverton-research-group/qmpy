Clazz.declarePackage ("J.api");
Clazz.declareInterface (J.api, "JmolDocument");
Clazz.load (["java.io.DataInput", "$.FilterInputStream"], "java.io.DataInputStream", ["java.io.EOFException", "$.PushbackInputStream", "$.UTFDataFormatException", "java.lang.Double", "$.Float", "$.IndexOutOfBoundsException"], function () {
c$ = Clazz.decorateAsClass (function () {
this.bytearr = null;
this.chararr = null;
this.readBuffer = null;
this.lineBuffer = null;
Clazz.instantialize (this, arguments);
}, java.io, "DataInputStream", java.io.FilterInputStream, java.io.DataInput);
Clazz.prepareFields (c$, function () {
this.bytearr =  Clazz.newByteArray (80, 0);
this.chararr =  Clazz.newCharArray (80, '\0');
this.readBuffer =  Clazz.newByteArray (8, 0);
});
Clazz.overrideMethod (c$, "read", 
function (b, off, len) {
return this.$in.read (b, off, len);
}, "~A,~N,~N");
$_M(c$, "readFully", 
function (b, off, len) {
if (len < 0) throw  new IndexOutOfBoundsException ();
var n = 0;
while (n < len) {
var count = this.$in.read (b, off + n, len - n);
if (count < 0) throw  new java.io.EOFException ();
n += count;
}
}, "~A,~N,~N");
Clazz.overrideMethod (c$, "skipBytes", 
function (n) {
var total = 0;
var cur = 0;
while ((total < n) && ((cur = this.$in.skip (n - total)) > 0)) {
total += cur;
}
return total;
}, "~N");
Clazz.overrideMethod (c$, "readBoolean", 
function () {
var ch = this.$in.readByteAsInt ();
if (ch < 0) throw  new java.io.EOFException ();
return (ch != 0);
});
Clazz.overrideMethod (c$, "readByte", 
function () {
var ch = this.$in.readByteAsInt ();
if (ch < 0) throw  new java.io.EOFException ();
return (ch);
});
Clazz.overrideMethod (c$, "readUnsignedByte", 
function () {
var ch = this.$in.readByteAsInt ();
if (ch < 0) throw  new java.io.EOFException ();
return ch;
});
Clazz.overrideMethod (c$, "readShort", 
function () {
var ch1 = this.$in.readByteAsInt ();
var ch2 = this.$in.readByteAsInt ();
if ((ch1 | ch2) < 0) throw  new java.io.EOFException ();
return ((ch1 << 8) + (ch2 << 0));
});
$_M(c$, "readUnsignedShort", 
function () {
var ch1 = this.$in.readByteAsInt ();
var ch2 = this.$in.readByteAsInt ();
if ((ch1 | ch2) < 0) throw  new java.io.EOFException ();
return (ch1 << 8) + (ch2 << 0);
});
Clazz.overrideMethod (c$, "readChar", 
function () {
var ch1 = this.$in.readByteAsInt ();
var ch2 = this.$in.readByteAsInt ();
if ((ch1 | ch2) < 0) throw  new java.io.EOFException ();
return String.fromCharCode ((ch1 << 8) + (ch2 << 0));
});
Clazz.overrideMethod (c$, "readInt", 
function () {
var ch1 = this.$in.readByteAsInt ();
var ch2 = this.$in.readByteAsInt ();
var ch3 = this.$in.readByteAsInt ();
var ch4 = this.$in.readByteAsInt ();
if ((ch1 | ch2 | ch3 | ch4) < 0) throw  new java.io.EOFException ();
return ((ch1 << 24) + (ch2 << 16) + (ch3 << 8) + (ch4 << 0));
});
Clazz.overrideMethod (c$, "readLong", 
function () {
this.readFully (this.readBuffer, 0, 8);
return ((this.readBuffer[0] << 56) + ((this.readBuffer[1] & 255) << 48) + ((this.readBuffer[2] & 255) << 40) + ((this.readBuffer[3] & 255) << 32) + ((this.readBuffer[4] & 255) << 24) + ((this.readBuffer[5] & 255) << 16) + ((this.readBuffer[6] & 255) << 8) + ((this.readBuffer[7] & 255) << 0));
});
Clazz.overrideMethod (c$, "readFloat", 
function () {
return Float.intBitsToFloat (this.readInt ());
});
Clazz.overrideMethod (c$, "readDouble", 
function () {
return Double.longBitsToDouble (this.readLong ());
});
Clazz.overrideMethod (c$, "readLine", 
function () {
var buf = this.lineBuffer;
if (buf == null) {
buf = this.lineBuffer =  Clazz.newCharArray (128, '\0');
}var room = buf.length;
var offset = 0;
var c;
loop : while (true) {
switch (c = this.$in.readByteAsInt ()) {
case -1:
case '\n':
break loop;
case '\r':
var c2 = this.$in.readByteAsInt ();
if ((c2 != 10) && (c2 != -1)) {
if (!(Clazz.instanceOf (this.$in, java.io.PushbackInputStream))) {
this.$in =  new java.io.PushbackInputStream (this.$in, 1);
}(this.$in).unreadByte (c2);
}break loop;
default:
if (--room < 0) {
buf =  Clazz.newCharArray (offset + 128, '\0');
room = buf.length - offset - 1;
System.arraycopy (this.lineBuffer, 0, buf, 0, offset);
this.lineBuffer = buf;
}buf[offset++] = String.fromCharCode (c);
break;
}
}
if ((c == -1) && (offset == 0)) {
return null;
}return String.copyValueOf (buf, 0, offset);
});
Clazz.overrideMethod (c$, "readUTF", 
function () {
return java.io.DataInputStream.readUTFBytes (this, -1);
});
c$.readUTFBytes = $_M(c$, "readUTFBytes", 
function ($in, utflen) {
var isByteArray = (utflen >= 0);
if (!isByteArray) utflen = $in.readUnsignedShort ();
var bytearr = null;
var chararr = null;
if (Clazz.instanceOf ($in, java.io.DataInputStream)) {
var dis = $in;
if (dis.bytearr.length < utflen) {
dis.bytearr =  Clazz.newByteArray (isByteArray ? utflen : utflen * 2, 0);
dis.chararr =  Clazz.newCharArray (dis.bytearr.length, '\0');
}chararr = dis.chararr;
bytearr = dis.bytearr;
} else {
bytearr =  Clazz.newByteArray (utflen, 0);
chararr =  Clazz.newCharArray (utflen, '\0');
}var c;
var char2;
var char3;
var count = 0;
var chararr_count = 0;
$in.readFully (bytearr, 0, utflen);
while (count < utflen) {
c = bytearr[count] & 0xff;
if (c > 127) break;
count++;
chararr[chararr_count++] = String.fromCharCode (c);
}
while (count < utflen) {
c = bytearr[count] & 0xff;
switch (c >> 4) {
case 0:
case 1:
case 2:
case 3:
case 4:
case 5:
case 6:
case 7:
count++;
chararr[chararr_count++] = String.fromCharCode (c);
break;
case 12:
case 13:
count += 2;
if (count > utflen) throw  new java.io.UTFDataFormatException ("malformed input: partial character at end");
char2 = bytearr[count - 1];
if ((char2 & 0xC0) != 0x80) throw  new java.io.UTFDataFormatException ("malformed input around byte " + count);
chararr[chararr_count++] = String.fromCharCode (((c & 0x1F) << 6) | (char2 & 0x3F));
break;
case 14:
count += 3;
if (count > utflen) throw  new java.io.UTFDataFormatException ("malformed input: partial character at end");
char2 = bytearr[count - 2];
char3 = bytearr[count - 1];
if (((char2 & 0xC0) != 0x80) || ((char3 & 0xC0) != 0x80)) throw  new java.io.UTFDataFormatException ("malformed input around byte " + (count - 1));
chararr[chararr_count++] = String.fromCharCode (((c & 0x0F) << 12) | ((char2 & 0x3F) << 6) | ((char3 & 0x3F) << 0));
break;
default:
throw  new java.io.UTFDataFormatException ("malformed input around byte " + count);
}
}
return  String.instantialize (chararr, 0, chararr_count);
}, "java.io.DataInput,~N");
});
Clazz.declarePackage ("J.io2");
Clazz.load (["J.api.JmolDocument"], "J.io2.BinaryDocument", ["java.io.DataInputStream", "java.lang.Double", "J.util.Logger"], function () {
c$ = Clazz.decorateAsClass (function () {
this.stream = null;
this.isRandom = false;
this.isBigEndian = true;
this.t8 = null;
this.nBytes = 0;
this.out = null;
Clazz.instantialize (this, arguments);
}, J.io2, "BinaryDocument", null, J.api.JmolDocument);
Clazz.prepareFields (c$, function () {
this.t8 =  Clazz.newByteArray (8, 0);
});
Clazz.makeConstructor (c$, 
function () {
});
Clazz.overrideMethod (c$, "close", 
function () {
if (this.stream != null) try {
this.stream.close ();
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
} else {
throw e;
}
}
if (this.out != null) this.out.closeChannel ();
});
Clazz.overrideMethod (c$, "setStream", 
function (bis, isBigEndian) {
if (bis != null) this.stream =  new java.io.DataInputStream (bis);
this.isBigEndian = isBigEndian;
}, "java.io.BufferedInputStream,~B");
Clazz.overrideMethod (c$, "setStreamData", 
function (stream, isBigEndian) {
if (stream != null) this.stream = stream;
this.isBigEndian = isBigEndian;
}, "java.io.DataInputStream,~B");
$_M(c$, "setRandom", 
function (TF) {
this.isRandom = TF;
}, "~B");
Clazz.overrideMethod (c$, "readByte", 
function () {
this.nBytes++;
return this.ioReadByte ();
});
$_M(c$, "ioReadByte", 
($fz = function () {
var b = this.stream.readByte ();
if (this.out != null) this.out.writeByteAsInt (b);
return b;
}, $fz.isPrivate = true, $fz));
Clazz.overrideMethod (c$, "readByteArray", 
function (b, off, len) {
var n = this.ioRead (b, off, len);
if (n > 0) this.nBytes += n;
var nBytesRead = n;
if (n > 0 && n < len) {
while (nBytesRead < len && n > 0) {
n = this.ioRead (b, nBytesRead, len - nBytesRead);
if (n > 0) {
this.nBytes += n;
nBytesRead += n;
}}
}return nBytesRead;
}, "~A,~N,~N");
$_M(c$, "ioRead", 
($fz = function (b, off, len) {
var n = this.stream.read (b, off, len);
if (n > 0 && this.out != null) this.writeBytes (b, off, n);
return n;
}, $fz.isPrivate = true, $fz), "~A,~N,~N");
$_M(c$, "writeBytes", 
function (b, off, n) {
this.out.write (b, off, n);
}, "~A,~N,~N");
Clazz.overrideMethod (c$, "readString", 
function (nChar) {
var temp =  Clazz.newByteArray (nChar, 0);
var n = this.readByteArray (temp, 0, nChar);
return  String.instantialize (temp, 0, n, "UTF-8");
}, "~N");
Clazz.overrideMethod (c$, "readShort", 
function () {
this.nBytes += 2;
return (this.isBigEndian ? this.ioReadShort () : ((this.ioReadByte () & 0xff) | (this.ioReadByte () & 0xff) << 8));
});
$_M(c$, "ioReadShort", 
($fz = function () {
var b = this.stream.readShort ();
if (this.out != null) this.writeShort (b);
return b;
}, $fz.isPrivate = true, $fz));
$_M(c$, "writeShort", 
function (i) {
this.out.writeByteAsInt (i >> 8);
this.out.writeByteAsInt (i);
}, "~N");
Clazz.overrideMethod (c$, "readIntLE", 
function () {
this.nBytes += 4;
return this.readLEInt ();
});
Clazz.overrideMethod (c$, "readInt", 
function () {
this.nBytes += 4;
return (this.isBigEndian ? this.ioReadInt () : this.readLEInt ());
});
$_M(c$, "ioReadInt", 
($fz = function () {
var i = this.stream.readInt ();
if (this.out != null) this.writeInt (i);
return i;
}, $fz.isPrivate = true, $fz));
$_M(c$, "writeInt", 
function (i) {
this.out.writeByteAsInt (i >> 24);
this.out.writeByteAsInt (i >> 16);
this.out.writeByteAsInt (i >> 8);
this.out.writeByteAsInt (i);
}, "~N");
Clazz.overrideMethod (c$, "swapBytesI", 
function (n) {
return (((n >> 24) & 0xff) | ((n >> 16) & 0xff) << 8 | ((n >> 8) & 0xff) << 16 | (n & 0xff) << 24);
}, "~N");
Clazz.overrideMethod (c$, "swapBytesS", 
function (n) {
return ((((n >> 8) & 0xff) | (n & 0xff) << 8));
}, "~N");
Clazz.overrideMethod (c$, "readUnsignedShort", 
function () {
this.nBytes += 2;
var a = (this.ioReadByte () & 0xff);
var b = (this.ioReadByte () & 0xff);
return (this.isBigEndian ? (a << 8) + b : (b << 8) + a);
});
Clazz.overrideMethod (c$, "readLong", 
function () {
this.nBytes += 8;
return (this.isBigEndian ? this.ioReadLong () : (((this.ioReadByte ()) & 0xff) | ((this.ioReadByte ()) & 0xff) << 8 | ((this.ioReadByte ()) & 0xff) << 16 | ((this.ioReadByte ()) & 0xff) << 24 | ((this.ioReadByte ()) & 0xff) << 32 | ((this.ioReadByte ()) & 0xff) << 40 | ((this.ioReadByte ()) & 0xff) << 48 | ((this.ioReadByte ()) & 0xff) << 54));
});
$_M(c$, "ioReadLong", 
($fz = function () {
var b = this.stream.readLong ();
if (this.out != null) this.writeLong (b);
return b;
}, $fz.isPrivate = true, $fz));
$_M(c$, "writeLong", 
function (b) {
this.writeInt (((b >> 32) & 0xFFFFFFFF));
this.writeInt ((b & 0xFFFFFFFF));
}, "~N");
Clazz.overrideMethod (c$, "readFloat", 
function () {
var x = this.readInt ();
{
if (x == 0) return 0;
var o = J.io2.BinaryDocument;
if (o.fracIEEE == null);
o.setFracIEEE();
var m = ((x & 0x7F800000) >> 23);
return ((x & 0x80000000) == 0 ? 1 : -1) * o.shiftIEEE((x & 0x7FFFFF) | 0x800000, m - 149);
}});
$_M(c$, "readLEInt", 
($fz = function () {
return ((this.ioReadByte () & 0xff) | (this.ioReadByte () & 0xff) << 8 | (this.ioReadByte () & 0xff) << 16 | (this.ioReadByte () & 0xff) << 24);
}, $fz.isPrivate = true, $fz));
Clazz.overrideMethod (c$, "readDouble", 
function () {
{
this.readByteArray(this.t8, 0, 8);
return J.io2.BinaryDocument.bytesToDoubleToFloat(this.t8, 0, this.isBigEndian);
}});
c$.bytesToDoubleToFloat = $_M(c$, "bytesToDoubleToFloat", 
function (bytes, j, isBigEndian) {
{
if (J.io2.BinaryDocument.fracIEEE == null) J.io2.BinaryDocument.setFracIEEE ();
{
var o = J.io2.BinaryDocument;
var b1, b2, b3, b4, b5;
if (isBigEndian) {
b1 = bytes[j] & 0xFF;
b2 = bytes[j + 1] & 0xFF;
b3 = bytes[j + 2] & 0xFF;
b4 = bytes[j + 3] & 0xFF;
b5 = bytes[j + 4] & 0xFF;
} else {
b1 = bytes[j + 7] & 0xFF;
b2 = bytes[j + 6] & 0xFF;
b3 = bytes[j + 5] & 0xFF;
b4 = bytes[j + 4] & 0xFF;
b5 = bytes[j + 3] & 0xFF;
}
var s = ((b1 & 0x80) == 0 ? 1 : -1);
var e = (((b1 & 0x7F) << 4) | (b2 >> 4)) - 1026;
b2 = (b2 & 0xF) | 0x10;
return s * (o.shiftIEEE(b2, e) + o.shiftIEEE(b3, e - 8) + o.shiftIEEE(b4, e - 16)
+ o.shiftIEEE(b5, e - 24));
}}}, "~A,~N,~B");
c$.setFracIEEE = $_M(c$, "setFracIEEE", 
function () {
($t$ = J.io2.BinaryDocument.fracIEEE =  Clazz.newFloatArray (270, 0), J.io2.BinaryDocument.prototype.fracIEEE = J.io2.BinaryDocument.fracIEEE, $t$);
for (var i = 0; i < 270; i++) J.io2.BinaryDocument.fracIEEE[i] = Math.pow (2, i - 141);

});
c$.shiftIEEE = $_M(c$, "shiftIEEE", 
function (f, i) {
if (f == 0 || i < -140) return 0;
if (i > 128) return 3.4028235E38;
return f * J.io2.BinaryDocument.fracIEEE[i + 140];
}, "~N,~N");
$_M(c$, "ioReadDouble", 
($fz = function () {
var d = this.stream.readDouble ();
if (this.out != null) this.writeLong (Double.doubleToRawLongBits (d));
return d;
}, $fz.isPrivate = true, $fz));
$_M(c$, "readLELong", 
($fz = function () {
return (((this.ioReadByte ()) & 0xff) | ((this.ioReadByte ()) & 0xff) << 8 | ((this.ioReadByte ()) & 0xff) << 16 | ((this.ioReadByte ()) & 0xff) << 24 | ((this.ioReadByte ()) & 0xff) << 32 | ((this.ioReadByte ()) & 0xff) << 40 | ((this.ioReadByte ()) & 0xff) << 48 | ((this.ioReadByte ()) & 0xff) << 56);
}, $fz.isPrivate = true, $fz));
Clazz.overrideMethod (c$, "seek", 
function (offset) {
try {
if (offset == this.nBytes) return;
if (offset < this.nBytes) {
this.stream.reset ();
this.nBytes = 0;
} else {
offset -= this.nBytes;
}this.stream.skipBytes (offset);
this.nBytes += offset;
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
J.util.Logger.errorEx (null, e);
} else {
throw e;
}
}
}, "~N");
Clazz.overrideMethod (c$, "getPosition", 
function () {
return this.nBytes;
});
Clazz.overrideMethod (c$, "setOutputChannel", 
function (out) {
this.out = out;
}, "J.io.JmolOutputChannel");
Clazz.overrideMethod (c$, "getAllDataFiles", 
function (binaryFileList, firstFile) {
return null;
}, "~S,~S");
Clazz.overrideMethod (c$, "getAllDataMapped", 
function (replace, string, fileData) {
}, "~S,~S,java.util.Map");
Clazz.defineStatics (c$,
"fracIEEE", null);
});
