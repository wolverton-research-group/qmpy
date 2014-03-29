Clazz.declarePackage ("J.api");
Clazz.declareInterface (J.api, "JmolZipUtility");
Clazz.declarePackage ("J.io2");
Clazz.load (["J.api.JmolZipUtility"], "J.io2.ZipUtil", ["java.io.BufferedInputStream", "$.BufferedReader", "$.ByteArrayInputStream", "$.StringReader", "java.lang.Character", "$.Long", "java.util.Date", "$.Hashtable", "$.StringTokenizer", "java.util.zip.CRC32", "$.GZIPInputStream", "$.ZipEntry", "$.ZipInputStream", "$.ZipOutputStream", "J.adapter.smarter.AtomSetCollection", "J.api.Interface", "J.io.JmolBinary", "J.io2.JmolZipInputStream", "J.util.Escape", "$.JmolList", "$.Logger", "$.Parser", "$.SB", "$.TextFormat", "J.viewer.FileManager", "$.JC", "$.Viewer"], function () {
c$ = Clazz.declareType (J.io2, "ZipUtil", null, J.api.JmolZipUtility);
Clazz.makeConstructor (c$, 
function () {
});
Clazz.overrideMethod (c$, "newZipInputStream", 
function (is) {
return J.io2.ZipUtil.newZIS (is);
}, "java.io.InputStream");
c$.newZIS = $_M(c$, "newZIS", 
($fz = function (is) {
return (Clazz.instanceOf (is, J.api.ZInputStream) ? is : Clazz.instanceOf (is, java.io.BufferedInputStream) ?  new J.io2.JmolZipInputStream (is) :  new J.io2.JmolZipInputStream ( new java.io.BufferedInputStream (is)));
}, $fz.isPrivate = true, $fz), "java.io.InputStream");
Clazz.overrideMethod (c$, "getAllZipData", 
function (is, subfileList, name0, binaryFileList, fileData) {
J.io2.ZipUtil.getAllZipDataStatic (is, subfileList, name0, binaryFileList, fileData);
}, "java.io.InputStream,~A,~S,~S,java.util.Map");
c$.getAllZipDataStatic = $_M(c$, "getAllZipDataStatic", 
($fz = function (is, subfileList, name0, binaryFileList, fileData) {
var zis = J.io2.ZipUtil.newZIS (is);
var ze;
var listing =  new J.util.SB ();
binaryFileList = "|" + binaryFileList + "|";
var prefix = J.util.TextFormat.join (subfileList, '/', 1);
var prefixd = null;
if (prefix != null) {
prefixd = prefix.substring (0, prefix.indexOf ("/") + 1);
if (prefixd.length == 0) prefixd = null;
}try {
while ((ze = zis.getNextEntry ()) != null) {
var name = ze.getName ();
if (prefix != null && prefixd != null && !(name.equals (prefix) || name.startsWith (prefixd))) continue;
listing.append (name).appendC ('\n');
var sname = "|" + name.substring (name.lastIndexOf ("/") + 1) + "|";
var asBinaryString = (binaryFileList.indexOf (sname) >= 0);
var bytes = J.io.JmolBinary.getStreamBytes (zis, ze.getSize ());
var str;
if (asBinaryString) {
str = J.io2.ZipUtil.getBinaryStringForBytes (bytes);
name += ":asBinaryString";
} else {
str = J.io.JmolBinary.fixUTF (bytes);
}str = "BEGIN Directory Entry " + name + "\n" + str + "\nEND Directory Entry " + name + "\n";
fileData.put (name0 + "|" + name, str);
}
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
} else {
throw e;
}
}
fileData.put ("#Directory_Listing", listing.toString ());
}, $fz.isPrivate = true, $fz), "java.io.InputStream,~A,~S,~S,java.util.Map");
c$.getBinaryStringForBytes = $_M(c$, "getBinaryStringForBytes", 
($fz = function (bytes) {
var ret =  new J.util.SB ();
for (var i = 0; i < bytes.length; i++) ret.append (Integer.toHexString (bytes[i] & 0xFF)).appendC (' ');

return ret.toString ();
}, $fz.isPrivate = true, $fz), "~A");
Clazz.overrideMethod (c$, "getZipFileContents", 
function (bis, list, listPtr, asBufferedInputStream) {
var ret;
if (list == null || listPtr >= list.length) return this.getZipDirectoryAsStringAndClose (bis);
var fileName = list[listPtr];
var zis =  new java.util.zip.ZipInputStream (bis);
var ze;
try {
var isAll = (fileName.equals ("."));
if (isAll || fileName.lastIndexOf ("/") == fileName.length - 1) {
ret =  new J.util.SB ();
while ((ze = zis.getNextEntry ()) != null) {
var name = ze.getName ();
if (isAll || name.startsWith (fileName)) ret.append (name).appendC ('\n');
}
var str = ret.toString ();
if (asBufferedInputStream) return  new java.io.BufferedInputStream ( new java.io.ByteArrayInputStream (str.getBytes ()));
return str;
}var asBinaryString = false;
if (fileName.indexOf (":asBinaryString") > 0) {
fileName = fileName.substring (0, fileName.indexOf (":asBinaryString"));
asBinaryString = true;
}while ((ze = zis.getNextEntry ()) != null) {
if (!fileName.equals (ze.getName ())) continue;
var bytes = J.io.JmolBinary.getStreamBytes (zis, ze.getSize ());
if (J.io.JmolBinary.isZipB (bytes)) return this.getZipFileContents ( new java.io.BufferedInputStream ( new java.io.ByteArrayInputStream (bytes)), list, ++listPtr, asBufferedInputStream);
if (asBufferedInputStream) return  new java.io.BufferedInputStream ( new java.io.ByteArrayInputStream (bytes));
if (asBinaryString) {
ret =  new J.util.SB ();
for (var i = 0; i < bytes.length; i++) ret.append (Integer.toHexString (bytes[i] & 0xFF)).appendC (' ');

return ret.toString ();
}return J.io.JmolBinary.fixUTF (bytes);
}
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
} else {
throw e;
}
}
return "";
}, "java.io.BufferedInputStream,~A,~N,~B");
Clazz.overrideMethod (c$, "getZipFileContentsAsBytes", 
function (bis, list, listPtr) {
var ret =  Clazz.newByteArray (0, 0);
var fileName = list[listPtr];
if (fileName.lastIndexOf ("/") == fileName.length - 1) return ret;
try {
bis = J.io.JmolBinary.checkPngZipStream (bis);
var zis =  new java.util.zip.ZipInputStream (bis);
var ze;
while ((ze = zis.getNextEntry ()) != null) {
if (!fileName.equals (ze.getName ())) continue;
var bytes = J.io.JmolBinary.getStreamBytes (zis, ze.getSize ());
if (J.io.JmolBinary.isZipB (bytes) && ++listPtr < list.length) return this.getZipFileContentsAsBytes ( new java.io.BufferedInputStream ( new java.io.ByteArrayInputStream (bytes)), list, listPtr);
return bytes;
}
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
} else {
throw e;
}
}
return ret;
}, "java.io.BufferedInputStream,~A,~N");
Clazz.overrideMethod (c$, "getZipDirectoryAsStringAndClose", 
function (bis) {
var sb =  new J.util.SB ();
var s =  new Array (0);
try {
s = this.getZipDirectoryOrErrorAndClose (bis, false);
bis.close ();
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
J.util.Logger.error (e.toString ());
} else {
throw e;
}
}
for (var i = 0; i < s.length; i++) sb.append (s[i]).appendC ('\n');

return sb.toString ();
}, "java.io.BufferedInputStream");
Clazz.overrideMethod (c$, "getZipDirectoryAndClose", 
function (bis, addManifest) {
var s =  new Array (0);
try {
s = this.getZipDirectoryOrErrorAndClose (bis, addManifest);
bis.close ();
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
J.util.Logger.error (e.toString ());
} else {
throw e;
}
}
return s;
}, "java.io.BufferedInputStream,~B");
$_M(c$, "getZipDirectoryOrErrorAndClose", 
($fz = function (bis, addManifest) {
bis = J.io.JmolBinary.checkPngZipStream (bis);
var v =  new J.util.JmolList ();
var zis =  new java.util.zip.ZipInputStream (bis);
var ze;
var manifest = null;
while ((ze = zis.getNextEntry ()) != null) {
var fileName = ze.getName ();
if (addManifest && J.io2.ZipUtil.isJmolManifest (fileName)) manifest = J.io2.ZipUtil.getZipEntryAsString (zis);
 else if (!fileName.startsWith ("__MACOS")) v.addLast (fileName);
}
zis.close ();
if (addManifest) v.add (0, manifest == null ? "" : manifest + "\n############\n");
return v.toArray ( new Array (v.size ()));
}, $fz.isPrivate = true, $fz), "java.io.BufferedInputStream,~B");
c$.getZipEntryAsString = $_M(c$, "getZipEntryAsString", 
($fz = function (is) {
return J.io.JmolBinary.fixUTF (J.io.JmolBinary.getStreamBytes (is, -1));
}, $fz.isPrivate = true, $fz), "java.io.InputStream");
c$.isJmolManifest = $_M(c$, "isJmolManifest", 
($fz = function (thisEntry) {
return thisEntry.startsWith ("JmolManifest");
}, $fz.isPrivate = true, $fz), "~S");
Clazz.overrideMethod (c$, "cacheZipContents", 
function (bis, fileName, cache) {
var zis = this.newZipInputStream (bis);
var ze;
var listing =  new J.util.SB ();
var n = 0;
try {
while ((ze = zis.getNextEntry ()) != null) {
var name = ze.getName ();
listing.append (name).appendC ('\n');
var nBytes = ze.getSize ();
var bytes = J.io.JmolBinary.getStreamBytes (zis, nBytes);
n += bytes.length;
cache.put (fileName + "|" + name, bytes);
}
zis.close ();
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
try {
zis.close ();
} catch (e1) {
if (Clazz.exceptionOf (e1, java.io.IOException)) {
} else {
throw e1;
}
}
return null;
} else {
throw e;
}
}
if (n == 0) return null;
J.util.Logger.info ("ZipUtil cached " + n + " bytes from " + fileName);
return listing.toString ();
}, "java.io.BufferedInputStream,~S,java.util.Map");
Clazz.overrideMethod (c$, "getGzippedBytesAsString", 
function (bytes) {
return J.io2.ZipUtil.staticGetGzippedBytesAsString (bytes);
}, "~A");
c$.staticGetGzippedBytesAsString = $_M(c$, "staticGetGzippedBytesAsString", 
function (bytes) {
try {
var is =  new java.io.ByteArrayInputStream (bytes);
do {
is =  new java.io.BufferedInputStream ( new java.util.zip.GZIPInputStream (is, 512));
} while (J.io.JmolBinary.isGzipS (is));
var s = J.io2.ZipUtil.getZipEntryAsString (is);
is.close ();
return s;
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
return "";
} else {
throw e;
}
}
}, "~A");
$_M(c$, "getUnGzippedInputStream", 
function (bytes) {
try {
var is =  new java.io.ByteArrayInputStream (bytes);
do {
is =  new java.io.BufferedInputStream ( new java.util.zip.GZIPInputStream (is, 512));
} while (J.io.JmolBinary.isGzipS (is));
return is;
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
return null;
} else {
throw e;
}
}
}, "~A");
Clazz.overrideMethod (c$, "newGZIPInputStream", 
function (bis) {
return  new java.util.zip.GZIPInputStream (bis, 512);
}, "java.io.BufferedInputStream");
$_M(c$, "addPngFileBytes", 
($fz = function (name, ret, iFile, crcMap, isSparDir, newName, ptSlash, v) {
var crc =  new java.util.zip.CRC32 ();
crc.update (ret, 0, ret.length);
var crcValue = Long.$valueOf (crc.getValue ());
if (crcMap.containsKey (crcValue)) {
newName = crcMap.get (crcValue);
} else {
if (isSparDir) newName = newName.$replace ('.', '_');
if (crcMap.containsKey (newName)) {
var pt = newName.lastIndexOf (".");
if (pt > ptSlash) newName = newName.substring (0, pt) + "[" + iFile + "]" + newName.substring (pt);
 else newName = newName + "[" + iFile + "]";
}v.addLast (name);
v.addLast (newName);
v.addLast (ret);
crcMap.put (crcValue, newName);
}return newName;
}, $fz.isPrivate = true, $fz), "~S,~A,~N,java.util.Hashtable,~B,~S,~N,J.util.JmolList");
$_M(c$, "writeZipFile", 
($fz = function (privateKey, fm, viewer, outFileName, fileNamesAndByteArrays, msg) {
var buf =  Clazz.newByteArray (1024, 0);
var nBytesOut = 0;
var nBytes = 0;
J.util.Logger.info ("creating zip file " + (outFileName == null ? "" : outFileName) + "...");
var fullFilePath = null;
var fileList = "";
try {
var out = viewer.openOutputChannel (privateKey, outFileName, false);
var bos;
{
bos = out;
}var zos =  new java.util.zip.ZipOutputStream (bos);
for (var i = 0; i < fileNamesAndByteArrays.size (); i += 3) {
var fname = fileNamesAndByteArrays.get (i);
var bytes = null;
var data = fm.cacheGet (fname, false);
if (Clazz.instanceOf (data, java.util.Map)) continue;
if (fname.indexOf ("file:/") == 0) {
fname = fname.substring (5);
if (fname.length > 2 && fname.charAt (2) == ':') fname = fname.substring (1);
} else if (fname.indexOf ("cache://") == 0) {
fname = fname.substring (8);
}var fnameShort = fileNamesAndByteArrays.get (i + 1);
if (fnameShort == null) fnameShort = fname;
if (data != null) bytes = (J.util.Escape.isAB (data) ? data : (data).getBytes ());
if (bytes == null) bytes = fileNamesAndByteArrays.get (i + 2);
var key = ";" + fnameShort + ";";
if (fileList.indexOf (key) >= 0) {
J.util.Logger.info ("duplicate entry");
continue;
}fileList += key;
zos.putNextEntry ( new java.util.zip.ZipEntry (fnameShort));
var nOut = 0;
if (bytes == null) {
var $in = viewer.openFileInputStream (privateKey, fname);
var len;
while ((len = $in.read (buf, 0, 1024)) > 0) {
zos.write (buf, 0, len);
nOut += len;
}
$in.close ();
} else {
zos.write (bytes, 0, bytes.length);
nOut += bytes.length;
}nBytesOut += nOut;
zos.closeEntry ();
J.util.Logger.info ("...added " + fname + " (" + nOut + " bytes)");
}
zos.flush ();
zos.close ();
var ret = out.closeChannel ();
J.util.Logger.info (nBytesOut + " bytes prior to compression");
nBytes = out.getByteCount ();
if (ret != null) {
if (ret.indexOf ("Exception") >= 0) return ret;
msg += " " + ret;
}fullFilePath = out.getFileName ();
if (fullFilePath == null) return out.toByteArray ();
} catch (e) {
if (Clazz.exceptionOf (e, java.io.IOException)) {
J.util.Logger.info (e.toString ());
return e.toString ();
} else {
throw e;
}
}
return msg + " " + nBytes + " " + fullFilePath;
}, $fz.isPrivate = true, $fz), "~N,J.viewer.FileManager,J.viewer.Viewer,~S,J.util.JmolList,~S");
Clazz.overrideMethod (c$, "getSceneScript", 
function (scenes, htScenes, list) {
var iSceneLast = 0;
var iScene = 0;
var sceneScript =  new J.util.SB ().append ("###scene.spt###").append (" Jmol ").append (J.viewer.Viewer.getJmolVersion ()).append ("\n{\nsceneScripts={");
for (var i = 1; i < scenes.length; i++) {
scenes[i - 1] = J.util.TextFormat.trim (scenes[i - 1], "\t\n\r ");
var pt =  Clazz.newIntArray (1, 0);
iScene = J.util.Parser.parseIntNext (scenes[i], pt);
if (iScene == -2147483648) return "bad scene ID: " + iScene;
scenes[i] = scenes[i].substring (pt[0]);
list.addLast (Integer.$valueOf (iScene));
var key = iSceneLast + "-" + iScene;
htScenes.put (key, scenes[i - 1]);
if (i > 1) sceneScript.append (",");
sceneScript.appendC ('\n').append (J.util.Escape.eS (key)).append (": ").append (J.util.Escape.eS (scenes[i - 1]));
iSceneLast = iScene;
}
sceneScript.append ("\n}\n");
if (list.size () == 0) return "no lines 'pause scene n'";
sceneScript.append ("\nthisSceneRoot = '$SCRIPT_PATH$'.split('_scene_')[1];\n").append ("thisSceneID = 0 + ('$SCRIPT_PATH$'.split('_scene_')[2]).split('.')[1];\n").append ("var thisSceneState = '$SCRIPT_PATH$'.replace('.min.png','.all.png') + 'state.spt';\n").append ("var spath = ''+currentSceneID+'-'+thisSceneID;\n").append ("print thisSceneRoot + ' ' + spath;\n").append ("var sscript = sceneScripts[spath];\n").append ("var isOK = true;\n").append ("try{\n").append ("if (thisSceneRoot != currentSceneRoot){\n").append (" isOK = false;\n").append ("} else if (sscript != '') {\n").append (" isOK = true;\n").append ("} else if (thisSceneID <= currentSceneID){\n").append (" isOK = false;\n").append ("} else {\n").append (" sscript = '';\n").append (" for (var i = currentSceneID; i < thisSceneID; i++){\n").append ("  var key = ''+i+'-'+(i + 1); var script = sceneScripts[key];\n").append ("  if (script = '') {isOK = false;break;}\n").append ("  sscript += ';'+script;\n").append (" }\n").append ("}\n}catch(e){print e;isOK = false}\n").append ("if (isOK) {" + J.io2.ZipUtil.wrapPathForAllFiles ("script inline @sscript", "print e;isOK = false") + "}\n").append ("if (!isOK){script @thisSceneState}\n").append ("currentSceneRoot = thisSceneRoot; currentSceneID = thisSceneID;\n}\n");
return sceneScript.toString ();
}, "~A,java.util.Map,J.util.JmolList");
c$.wrapPathForAllFiles = $_M(c$, "wrapPathForAllFiles", 
($fz = function (cmd, strCatch) {
var vname = "v__" + ("" + Math.random ()).substring (3);
return "# Jmol script\n{\n\tVar " + vname + " = pathForAllFiles\n\tpathForAllFiles=\"$SCRIPT_PATH$\"\n\ttry{\n\t\t" + cmd + "\n\t}catch(e){" + strCatch + "}\n\tpathForAllFiles = " + vname + "\n}\n";
}, $fz.isPrivate = true, $fz), "~S,~S");
Clazz.overrideMethod (c$, "createZipSet", 
function (privateKey, fm, viewer, fileName, script, scripts, includeRemoteFiles) {
var v =  new J.util.JmolList ();
var fileNames =  new J.util.JmolList ();
var crcMap =  new java.util.Hashtable ();
var haveSceneScript = (scripts != null && scripts.length == 3 && scripts[1].startsWith ("###scene.spt###"));
var sceneScriptOnly = (haveSceneScript && scripts[2].equals ("min"));
if (!sceneScriptOnly) {
J.io.JmolBinary.getFileReferences (script, fileNames);
if (haveSceneScript) J.io.JmolBinary.getFileReferences (scripts[1], fileNames);
}var haveScripts = (!haveSceneScript && scripts != null && scripts.length > 0);
if (haveScripts) {
script = J.io2.ZipUtil.wrapPathForAllFiles ("script " + J.util.Escape.eS (scripts[0]), "");
for (var i = 0; i < scripts.length; i++) fileNames.addLast (scripts[i]);

}var nFiles = fileNames.size ();
if (fileName != null) fileName = fileName.$replace ('\\', '/');
var fileRoot = fileName;
if (fileRoot != null) {
fileRoot = fileName.substring (fileName.lastIndexOf ("/") + 1);
if (fileRoot.indexOf (".") >= 0) fileRoot = fileRoot.substring (0, fileRoot.indexOf ("."));
}var newFileNames =  new J.util.JmolList ();
for (var iFile = 0; iFile < nFiles; iFile++) {
var name = fileNames.get (iFile);
var isLocal = !viewer.isJS && J.viewer.FileManager.isLocal (name);
var newName = name;
if (isLocal || includeRemoteFiles) {
var ptSlash = name.lastIndexOf ("/");
newName = (name.indexOf ("?") > 0 && name.indexOf ("|") < 0 ? J.util.TextFormat.replaceAllCharacters (name, "/:?\"'=&", "_") : J.viewer.FileManager.stripPath (name));
newName = J.util.TextFormat.replaceAllCharacters (newName, "[]", "_");
var isSparDir = (fm.spardirCache != null && fm.spardirCache.containsKey (name));
if (isLocal && name.indexOf ("|") < 0 && !isSparDir) {
v.addLast (name);
v.addLast (newName);
v.addLast (null);
} else {
var ret = (isSparDir ? fm.spardirCache.get (name) : fm.getFileAsBytes (name, null, true));
if (!J.util.Escape.isAB (ret)) return ret;
newName = this.addPngFileBytes (name, ret, iFile, crcMap, isSparDir, newName, ptSlash, v);
}name = "$SCRIPT_PATH$" + newName;
}crcMap.put (newName, newName);
newFileNames.addLast (name);
}
if (!sceneScriptOnly) {
script = J.util.TextFormat.replaceQuotedStrings (script, fileNames, newFileNames);
v.addLast ("state.spt");
v.addLast (null);
v.addLast (script.getBytes ());
}if (haveSceneScript) {
if (scripts[0] != null) {
v.addLast ("animate.spt");
v.addLast (null);
v.addLast (scripts[0].getBytes ());
}v.addLast ("scene.spt");
v.addLast (null);
script = J.util.TextFormat.replaceQuotedStrings (scripts[1], fileNames, newFileNames);
v.addLast (script.getBytes ());
}var sname = (haveSceneScript ? "scene.spt" : "state.spt");
v.addLast ("JmolManifest.txt");
v.addLast (null);
var sinfo = "# Jmol Manifest Zip Format 1.1\n# Created " + ( new java.util.Date ()) + "\n" + "# JmolVersion " + J.viewer.Viewer.getJmolVersion () + "\n" + sname;
v.addLast (sinfo.getBytes ());
v.addLast ("Jmol_version_" + J.viewer.Viewer.getJmolVersion ().$replace (' ', '_').$replace (':', '.'));
v.addLast (null);
v.addLast ( Clazz.newByteArray (0, 0));
if (fileRoot != null) {
var imageParams =  new java.util.Hashtable ();
imageParams.put ("type", "PNG");
imageParams.put ("comment", J.viewer.JC.embedScript (script));
var bytes = viewer.getImageAsBytes (imageParams);
if (J.util.Escape.isAB (bytes)) {
v.addLast ("preview.png");
v.addLast (null);
v.addLast (bytes);
}}return this.writeZipFile (privateKey, fm, viewer, fileName, v, "OK JMOL");
}, "~N,J.viewer.FileManager,J.viewer.Viewer,~S,~S,~A,~B");
Clazz.overrideMethod (c$, "getAtomSetCollectionOrBufferedReaderFromZip", 
function (adapter, is, fileName, zipDirectory, htParams, subFilePtr, asBufferedReader) {
var doCombine = (subFilePtr == 1);
htParams.put ("zipSet", fileName);
var subFileList = htParams.get ("subFileList");
if (subFileList == null) subFileList = J.io2.ZipUtil.checkSpecialInZip (zipDirectory);
var subFileName = (subFileList == null || subFilePtr >= subFileList.length ? null : subFileList[subFilePtr]);
if (subFileName != null && (subFileName.startsWith ("/") || subFileName.startsWith ("\\"))) subFileName = subFileName.substring (1);
var selectedFile = 0;
if (subFileName == null && htParams.containsKey ("modelNumber")) {
selectedFile = (htParams.get ("modelNumber")).intValue ();
if (selectedFile > 0 && doCombine) htParams.remove ("modelNumber");
}var manifest = htParams.get ("manifest");
var useFileManifest = (manifest == null);
if (useFileManifest) manifest = (zipDirectory.length > 0 ? zipDirectory[0] : "");
var haveManifest = (manifest.length > 0);
if (haveManifest) {
if (J.util.Logger.debugging) J.util.Logger.debug ("manifest for  " + fileName + ":\n" + manifest);
}var ignoreErrors = (manifest.indexOf ("IGNORE_ERRORS") >= 0);
var selectAll = (manifest.indexOf ("IGNORE_MANIFEST") >= 0);
var exceptFiles = (manifest.indexOf ("EXCEPT_FILES") >= 0);
if (selectAll || subFileName != null) haveManifest = false;
if (useFileManifest && haveManifest) {
var path = J.io.JmolBinary.getManifestScriptPath (manifest);
if (path != null) return "NOTE: file recognized as a script file: " + fileName + path + "\n";
}var vCollections =  new J.util.JmolList ();
var htCollections = (haveManifest ?  new java.util.Hashtable () : null);
var nFiles = 0;
var ret = J.io2.ZipUtil.checkSpecialData (is, zipDirectory);
if (Clazz.instanceOf (ret, String)) return ret;
var data = ret;
try {
if (data != null) {
var reader =  new java.io.BufferedReader ( new java.io.StringReader (data.toString ()));
if (asBufferedReader) {
return reader;
}ret = adapter.getAtomSetCollectionFromReader (fileName, reader, htParams);
if (Clazz.instanceOf (ret, String)) return ret;
if (Clazz.instanceOf (ret, J.adapter.smarter.AtomSetCollection)) {
var atomSetCollection = ret;
if (atomSetCollection.errorMessage != null) {
if (ignoreErrors) return null;
return atomSetCollection.errorMessage;
}return atomSetCollection;
}if (ignoreErrors) return null;
return "unknown reader error";
}if (Clazz.instanceOf (is, java.io.BufferedInputStream)) is = J.io.JmolBinary.checkPngZipStream (is);
var zis = J.io.JmolBinary.newZipInputStream (is);
var ze;
if (haveManifest) manifest = '|' + manifest.$replace ('\r', '|').$replace ('\n', '|') + '|';
while ((ze = zis.getNextEntry ()) != null && (selectedFile <= 0 || vCollections.size () < selectedFile)) {
if (ze.isDirectory ()) continue;
var thisEntry = ze.getName ();
if (subFileName != null && !thisEntry.equals (subFileName)) continue;
if (subFileName != null) htParams.put ("subFileName", subFileName);
if (J.io2.ZipUtil.isJmolManifest (thisEntry) || haveManifest && exceptFiles == manifest.indexOf ("|" + thisEntry + "|") >= 0) continue;
var bytes = J.io.JmolBinary.getStreamBytes (zis, ze.getSize ());
if (J.io.JmolBinary.isZipB (bytes)) {
var bis =  new java.io.BufferedInputStream ( new java.io.ByteArrayInputStream (bytes));
var zipDir2 = J.io.JmolBinary.getZipDirectoryAndClose (bis, true);
bis =  new java.io.BufferedInputStream ( new java.io.ByteArrayInputStream (bytes));
var atomSetCollections = this.getAtomSetCollectionOrBufferedReaderFromZip (adapter, bis, fileName + "|" + thisEntry, zipDir2, htParams, ++subFilePtr, asBufferedReader);
if (Clazz.instanceOf (atomSetCollections, String)) {
if (ignoreErrors) continue;
return atomSetCollections;
} else if (Clazz.instanceOf (atomSetCollections, J.adapter.smarter.AtomSetCollection) || Clazz.instanceOf (atomSetCollections, J.util.JmolList)) {
if (haveManifest && !exceptFiles) htCollections.put (thisEntry, atomSetCollections);
 else vCollections.addLast (atomSetCollections);
} else if (Clazz.instanceOf (atomSetCollections, java.io.BufferedReader)) {
if (doCombine) zis.close ();
return atomSetCollections;
} else {
if (ignoreErrors) continue;
zis.close ();
return "unknown zip reader error";
}} else if (J.io.JmolBinary.isGzipB (bytes)) {
return this.getUnGzippedInputStream (bytes);
} else if (J.io.JmolBinary.isPickleB (bytes)) {
var bis =  new java.io.BufferedInputStream ( new java.io.ByteArrayInputStream (bytes));
if (doCombine) zis.close ();
return bis;
} else {
var sData;
if (J.io.JmolBinary.isCompoundDocumentB (bytes)) {
var jd = J.api.Interface.getInterface ("jmol.util.CompoundDocument");
jd.setStream ( new java.io.BufferedInputStream ( new java.io.ByteArrayInputStream (bytes)), true);
sData = jd.getAllDataFiles ("Molecule", "Input").toString ();
} else if (J.io.JmolBinary.isGzipB (bytes)) {
sData = J.io.JmolBinary.getGzippedBytesAsString (bytes);
} else {
sData = J.io.JmolBinary.fixUTF (bytes);
}var reader =  new java.io.BufferedReader ( new java.io.StringReader (sData));
if (asBufferedReader) {
if (doCombine) zis.close ();
return reader;
}var fname = fileName + "|" + ze.getName ();
ret = adapter.getAtomSetCollectionFromReader (fname, reader, htParams);
if (!(Clazz.instanceOf (ret, J.adapter.smarter.AtomSetCollection))) {
if (ignoreErrors) continue;
zis.close ();
return "" + ret;
}if (haveManifest && !exceptFiles) htCollections.put (thisEntry, ret);
 else vCollections.addLast (ret);
var a = ret;
if (a.errorMessage != null) {
if (ignoreErrors) continue;
zis.close ();
return a.errorMessage;
}}}
if (doCombine) zis.close ();
if (haveManifest && !exceptFiles) {
var list = J.util.TextFormat.split (manifest, '|');
for (var i = 0; i < list.length; i++) {
var file = list[i];
if (file.length == 0 || file.indexOf ("#") == 0) continue;
if (htCollections.containsKey (file)) vCollections.addLast (htCollections.get (file));
 else if (J.util.Logger.debugging) J.util.Logger.debug ("manifested file " + file + " was not found in " + fileName);
}
}if (!doCombine) return vCollections;
var result =  new J.adapter.smarter.AtomSetCollection ("Array", null, null, vCollections);
if (result.errorMessage != null) {
if (ignoreErrors) return null;
return result.errorMessage;
}if (nFiles == 1) selectedFile = 1;
if (selectedFile > 0 && selectedFile <= vCollections.size ()) return vCollections.get (selectedFile - 1);
return result;
} catch (e$$) {
if (Clazz.exceptionOf (e$$, Exception)) {
var e = e$$;
{
if (ignoreErrors) return null;
J.util.Logger.error ("" + e);
return "" + e;
}
} else if (Clazz.exceptionOf (e$$, Error)) {
var er = e$$;
{
J.util.Logger.errorEx (null, er);
return "" + er;
}
} else {
throw e$$;
}
}
}, "J.api.JmolAdapter,java.io.InputStream,~S,~A,java.util.Map,~N,~B");
c$.checkSpecialData = $_M(c$, "checkSpecialData", 
($fz = function (is, zipDirectory) {
var isSpartan = false;
for (var i = 1; i < zipDirectory.length; i++) {
if (zipDirectory[i].endsWith (".spardir/") || zipDirectory[i].indexOf ("_spartandir") >= 0) {
isSpartan = true;
break;
}}
if (!isSpartan) return null;
var data =  new J.util.SB ();
data.append ("Zip File Directory: ").append ("\n").append (J.util.Escape.eAS (zipDirectory, true)).append ("\n");
var fileData =  new java.util.Hashtable ();
J.io2.ZipUtil.getAllZipDataStatic (is, [], "", "Molecule", fileData);
var prefix = "|";
var outputData = fileData.get (prefix + "output");
if (outputData == null) outputData = fileData.get ((prefix = "|" + zipDirectory[1]) + "output");
data.append (outputData);
var files = J.io2.ZipUtil.getSpartanFileList (prefix, J.io2.ZipUtil.getSpartanDirs (outputData));
for (var i = 2; i < files.length; i++) {
var name = files[i];
if (fileData.containsKey (name)) data.append (fileData.get (name));
 else data.append (name + "\n");
}
return data;
}, $fz.isPrivate = true, $fz), "java.io.InputStream,~A");
Clazz.overrideMethod (c$, "spartanFileList", 
function (name, type) {
var dirNums = J.io2.ZipUtil.getSpartanDirs (type);
if (dirNums.length == 0 && name.endsWith (".spardir.zip") && type.indexOf (".zip|output") >= 0) {
var sname = name.$replace ('\\', '/');
var pt = name.lastIndexOf (".spardir");
pt = sname.lastIndexOf ("/");
sname = name + "|" + name.substring (pt + 1, name.length - 4);
return ["SpartanSmol", sname, sname + "/output"];
}return J.io2.ZipUtil.getSpartanFileList (name, dirNums);
}, "~S,~S");
c$.getSpartanDirs = $_M(c$, "getSpartanDirs", 
($fz = function (outputFileData) {
if (outputFileData == null) return [];
if (outputFileData.startsWith ("java.io.FileNotFoundException") || outputFileData.startsWith ("FILE NOT FOUND") || outputFileData.indexOf ("<html") >= 0) return ["M0001"];
var v =  new J.util.JmolList ();
var token;
var lasttoken = "";
try {
var tokens =  new java.util.StringTokenizer (outputFileData, " \t\r\n");
while (tokens.hasMoreTokens ()) {
if ((token = tokens.nextToken ()).equals (")")) v.addLast (lasttoken);
 else if (token.equals ("Start-") && tokens.nextToken ().equals ("Molecule")) v.addLast (J.util.TextFormat.split (tokens.nextToken (), '"')[1]);
lasttoken = token;
}
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
} else {
throw e;
}
}
return v.toArray ( new Array (v.size ()));
}, $fz.isPrivate = true, $fz), "~S");
c$.getSpartanFileList = $_M(c$, "getSpartanFileList", 
($fz = function (name, dirNums) {
var files =  new Array (2 + dirNums.length * 5);
files[0] = "SpartanSmol";
files[1] = "Directory Entry ";
var pt = 2;
name = name.$replace ('\\', '/');
if (name.endsWith ("/")) name = name.substring (0, name.length - 1);
for (var i = 0; i < dirNums.length; i++) {
var path = name + (Character.isDigit (dirNums[i].charAt (0)) ? "/Profile." + dirNums[i] : "/" + dirNums[i]);
files[pt++] = path + "/#JMOL_MODEL " + dirNums[i];
files[pt++] = path + "/input";
files[pt++] = path + "/archive";
files[pt++] = path + "/Molecule:asBinaryString";
files[pt++] = path + "/proparc";
}
return files;
}, $fz.isPrivate = true, $fz), "~S,~A");
c$.checkSpecialInZip = $_M(c$, "checkSpecialInZip", 
function (zipDirectory) {
var name;
return (zipDirectory.length < 2 ? null : (name = zipDirectory[1]).endsWith (".spardir/") || zipDirectory.length == 2 ? ["", (name.endsWith ("/") ? name.substring (0, name.length - 1) : name)] : null);
}, "~A");
Clazz.overrideMethod (c$, "getCachedPngjBytes", 
function (fm, pathName) {
if (pathName.indexOf (".png") < 0) return null;
J.util.Logger.info ("FileManager checking PNGJ cache for " + pathName);
var shortName = J.io2.ZipUtil.shortSceneFilename (pathName);
if (fm.pngjCache == null && !this.cachePngjFile (fm, [pathName, null])) return null;
var pngjCache = fm.pngjCache;
var isMin = (pathName.indexOf (".min.") >= 0);
if (!isMin) {
var cName = fm.getCanonicalName (J.io.JmolBinary.getZipRoot (pathName));
if (!pngjCache.containsKey (cName) && !this.cachePngjFile (fm, [pathName, null])) return null;
if (pathName.indexOf ("|") < 0) shortName = cName;
}if (pngjCache.containsKey (shortName)) {
J.util.Logger.info ("FileManager using memory cache " + shortName);
return pngjCache.get (shortName);
}if (!isMin || !this.cachePngjFile (fm, [pathName, null])) return null;
J.util.Logger.info ("FileManager using memory cache " + shortName);
return pngjCache.get (shortName);
}, "J.viewer.FileManager,~S");
Clazz.overrideMethod (c$, "cachePngjFile", 
function (fm, data) {
var pngjCache = fm.pngjCache =  new java.util.Hashtable ();
if (data == null) return false;
data[1] = null;
if (data[0] == null) return false;
data[0] = J.io.JmolBinary.getZipRoot (data[0]);
var shortName = J.io2.ZipUtil.shortSceneFilename (data[0]);
try {
data[1] = this.cacheZipContents (J.io.JmolBinary.checkPngZipStream (fm.getBufferedInputStreamOrErrorMessageFromName (data[0], null, false, false, null, false)), shortName, fm.pngjCache);
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
return false;
} else {
throw e;
}
}
if (data[1] == null) return false;
var bytes = data[1].getBytes ();
pngjCache.put (fm.getCanonicalName (data[0]), bytes);
if (shortName.indexOf ("_scene_") >= 0) {
pngjCache.put (J.io2.ZipUtil.shortSceneFilename (data[0]), bytes);
bytes = pngjCache.remove (shortName + "|state.spt");
if (bytes != null) pngjCache.put (J.io2.ZipUtil.shortSceneFilename (data[0] + "|state.spt"), bytes);
}for (var key, $key = pngjCache.keySet ().iterator (); $key.hasNext () && ((key = $key.next ()) || true);) System.out.println (key);

return true;
}, "J.viewer.FileManager,~A");
c$.shortSceneFilename = $_M(c$, "shortSceneFilename", 
($fz = function (pathName) {
var pt = pathName.indexOf ("_scene_") + 7;
if (pt < 7) return pathName;
var s = "";
if (pathName.endsWith ("|state.spt")) {
var pt1 = pathName.indexOf ('.', pt);
if (pt1 < 0) return pathName;
s = pathName.substring (pt, pt1);
}var pt2 = pathName.lastIndexOf ("|");
return pathName.substring (0, pt) + s + (pt2 > 0 ? pathName.substring (pt2) : "");
}, $fz.isPrivate = true, $fz), "~S");
Clazz.defineStatics (c$,
"SCENE_TAG", "###scene.spt###");
});
$_L(["java.io.Closeable","$.InputStream"],"java.io.FileInputStream",["java.lang.IndexOutOfBoundsException","$.NullPointerException"],function(){
c$=$_C(function(){
this.fd=null;
this.innerFD=false;
$_Z(this,arguments);
},java.io,"FileInputStream",java.io.InputStream,java.io.Closeable);
$_K(c$,
function(file){
$_R(this,java.io.FileInputStream);
},"java.io.File");
$_K(c$,
function(fd){
$_R(this,java.io.FileInputStream);
if(fd==null){
throw new NullPointerException();
}},"java.io.FileDescriptor");
$_K(c$,
function(fileName){
this.construct(null==fileName?null:null);
},"~S");
$_V(c$,"available",
function(){
return 0;
});
$_V(c$,"close",
function(){
if(this.fd==null){
return;
}});
$_V(c$,"finalize",
function(){
this.close();
});
$_M(c$,"getFD",
function(){
return this.fd;
});
$_M(c$,"read",
function(){
var readed=$_A(1,0);
var result=this.read(readed,0,1);
return result==-1?-1:readed[0]&0xff;
});
$_M(c$,"read",
function(buffer){
return this.read(buffer,0,buffer.length);
},"~A");
$_M(c$,"read",
function(buffer,offset,count){
if(count>buffer.length-offset||count<0||offset<0){
throw new IndexOutOfBoundsException();
}if(0==count){
return 0;
}return 0;
},"~A,~N,~N");
$_V(c$,"skip",
function(count){
return 0;
},"~N");
});
Clazz.declarePackage ("JZ");
Clazz.declareInterface (JZ, "Checksum");
Clazz.declarePackage ("JZ");
Clazz.load (["JZ.Checksum"], "JZ.CRC32", null, function () {
c$ = Clazz.decorateAsClass (function () {
this.crc = 0;
this.b1 = null;
Clazz.instantialize (this, arguments);
}, JZ, "CRC32", null, JZ.Checksum);
Clazz.prepareFields (c$, function () {
this.b1 =  Clazz.newByteArray (1, 0);
});
Clazz.overrideMethod (c$, "update", 
function (buf, index, len) {
var c = ~this.crc;
while (--len >= 0) c = JZ.CRC32.crc_table[(c ^ buf[index++]) & 0xff] ^ (c >>> 8);

this.crc = ~c;
}, "~A,~N,~N");
Clazz.overrideMethod (c$, "reset", 
function () {
this.crc = 0;
});
Clazz.overrideMethod (c$, "resetLong", 
function (vv) {
this.crc = (vv & 0xffffffff);
}, "~N");
Clazz.overrideMethod (c$, "getValue", 
function () {
return this.crc & 0xffffffff;
});
Clazz.overrideMethod (c$, "updateByteAsInt", 
function (b) {
this.b1[0] = b;
this.update (this.b1, 0, 1);
}, "~N");
Clazz.defineStatics (c$,
"crc_table", [0, 1996959894, -301047508, -1727442502, 124634137, 1886057615, -379345611, -1637575261, 249268274, 2044508324, -522852066, -1747789432, 162941995, 2125561021, -407360249, -1866523247, 498536548, 1789927666, -205950648, -2067906082, 450548861, 1843258603, -187386543, -2083289657, 325883990, 1684777152, -43845254, -1973040660, 335633487, 1661365465, -99664541, -1928851979, 997073096, 1281953886, -715111964, -1570279054, 1006888145, 1258607687, -770865667, -1526024853, 901097722, 1119000684, -608450090, -1396901568, 853044451, 1172266101, -589951537, -1412350631, 651767980, 1373503546, -925412992, -1076862698, 565507253, 1454621731, -809855591, -1195530993, 671266974, 1594198024, -972236366, -1324619484, 795835527, 1483230225, -1050600021, -1234817731, 1994146192, 31158534, -1731059524, -271249366, 1907459465, 112637215, -1614814043, -390540237, 2013776290, 251722036, -1777751922, -519137256, 2137656763, 141376813, -1855689577, -429695999, 1802195444, 476864866, -2056965928, -228458418, 1812370925, 453092731, -2113342271, -183516073, 1706088902, 314042704, -1950435094, -54949764, 1658658271, 366619977, -1932296973, -69972891, 1303535960, 984961486, -1547960204, -725929758, 1256170817, 1037604311, -1529756563, -740887301, 1131014506, 879679996, -1385723834, -631195440, 1141124467, 855842277, -1442165665, -586318647, 1342533948, 654459306, -1106571248, -921952122, 1466479909, 544179635, -1184443383, -832445281, 1591671054, 702138776, -1328506846, -942167884, 1504918807, 783551873, -1212326853, -1061524307, -306674912, -1698712650, 62317068, 1957810842, -355121351, -1647151185, 81470997, 1943803523, -480048366, -1805370492, 225274430, 2053790376, -468791541, -1828061283, 167816743, 2097651377, -267414716, -2029476910, 503444072, 1762050814, -144550051, -2140837941, 426522225, 1852507879, -19653770, -1982649376, 282753626, 1742555852, -105259153, -1900089351, 397917763, 1622183637, -690576408, -1580100738, 953729732, 1340076626, -776247311, -1497606297, 1068828381, 1219638859, -670225446, -1358292148, 906185462, 1090812512, -547295293, -1469587627, 829329135, 1181335161, -882789492, -1134132454, 628085408, 1382605366, -871598187, -1156888829, 570562233, 1426400815, -977650754, -1296233688, 733239954, 1555261956, -1026031705, -1244606671, 752459403, 1541320221, -1687895376, -328994266, 1969922972, 40735498, -1677130071, -351390145, 1913087877, 83908371, -1782625662, -491226604, 2075208622, 213261112, -1831694693, -438977011, 2094854071, 198958881, -2032938284, -237706686, 1759359992, 534414190, -2118248755, -155638181, 1873836001, 414664567, -2012718362, -15766928, 1711684554, 285281116, -1889165569, -127750551, 1634467795, 376229701, -1609899400, -686959890, 1308918612, 956543938, -1486412191, -799009033, 1231636301, 1047427035, -1362007478, -640263460, 1088359270, 936918000, -1447252397, -558129467, 1202900863, 817233897, -1111625188, -893730166, 1404277552, 615818150, -1160759803, -841546093, 1423857449, 601450431, -1285129682, -1000256840, 1567103746, 711928724, -1274298825, -1022587231, 1510334235, 755167117]);
});
Clazz.declarePackage ("java.util.zip");
Clazz.load (["JZ.CRC32"], "java.util.zip.CRC32", null, function () {
c$ = Clazz.declareType (java.util.zip, "CRC32", JZ.CRC32);
});
Clazz.declarePackage ("JZ");
Clazz.load (["java.io.FilterInputStream"], "JZ.InflaterInputStream", ["java.io.EOFException", "$.IOException", "java.lang.IllegalArgumentException", "$.IndexOutOfBoundsException", "$.NullPointerException"], function () {
c$ = Clazz.decorateAsClass (function () {
this.inflater = null;
this.buf = null;
this.len = 0;
this.closed = false;
this.eof = false;
this.close_in = true;
this.myinflater = false;
this.byte1 = null;
this.b = null;
Clazz.instantialize (this, arguments);
}, JZ, "InflaterInputStream", java.io.FilterInputStream);
Clazz.prepareFields (c$, function () {
this.byte1 =  Clazz.newByteArray (1, 0);
this.b =  Clazz.newByteArray (512, 0);
});
Clazz.makeConstructor (c$, 
function ($in, inflater, size, close_in) {
Clazz.superConstructor (this, JZ.InflaterInputStream, [$in]);
this.inflater = inflater;
this.buf =  Clazz.newByteArray (size, 0);
this.close_in = close_in;
}, "java.io.InputStream,JZ.Inflater,~N,~B");
Clazz.overrideMethod (c$, "readByteAsInt", 
function () {
if (this.closed) {
throw  new java.io.IOException ("Stream closed");
}return this.read (this.byte1, 0, 1) == -1 ? -1 : this.byte1[0] & 0xff;
});
Clazz.overrideMethod (c$, "read", 
function (b, off, len) {
return this.readInf (b, off, len);
}, "~A,~N,~N");
$_M(c$, "readInf", 
function (b, off, len) {
if (this.closed) {
throw  new java.io.IOException ("Stream closed");
}if (b == null) {
throw  new NullPointerException ();
} else if (off < 0 || len < 0 || len > b.length - off) {
throw  new IndexOutOfBoundsException ();
} else if (len == 0) {
return 0;
} else if (this.eof) {
return -1;
}var n = 0;
this.inflater.setOutput (b, off, len);
while (!this.eof) {
if (this.inflater.avail_in == 0) this.fill ();
var err = this.inflater.inflate (0);
n += this.inflater.next_out_index - off;
off = this.inflater.next_out_index;
switch (err) {
case -3:
throw  new java.io.IOException (this.inflater.msg);
case 1:
case 2:
this.eof = true;
if (err == 2) return -1;
break;
default:
}
if (this.inflater.avail_out == 0) break;
}
return n;
}, "~A,~N,~N");
Clazz.overrideMethod (c$, "available", 
function () {
if (this.closed) {
throw  new java.io.IOException ("Stream closed");
}return (this.eof ? 0 : 1);
});
Clazz.overrideMethod (c$, "skip", 
function (n) {
if (n < 0) {
throw  new IllegalArgumentException ("negative skip length");
}if (this.closed) {
throw  new java.io.IOException ("Stream closed");
}var max = Math.min (n, 2147483647);
var total = 0;
while (total < max) {
var len = max - total;
if (len > this.b.length) {
len = this.b.length;
}len = this.read (this.b, 0, len);
if (len == -1) {
this.eof = true;
break;
}total += len;
}
return total;
}, "~N");
Clazz.overrideMethod (c$, "close", 
function () {
if (!this.closed) {
if (this.myinflater) this.inflater.end ();
if (this.close_in) this.$in.close ();
this.closed = true;
}});
$_M(c$, "fill", 
function () {
if (this.closed) {
throw  new java.io.IOException ("Stream closed");
}this.len = this.$in.read (this.buf, 0, this.buf.length);
if (this.len == -1) {
if (this.inflater.istate.wrap == 0 && !this.inflater.finished ()) {
this.buf[0] = 0;
this.len = 1;
} else if (this.inflater.istate.was != -1) {
throw  new java.io.IOException ("footer is not found");
} else {
throw  new java.io.EOFException ("Unexpected end of ZLIB input stream");
}}this.inflater.setInput (this.buf, 0, this.len, true);
});
Clazz.overrideMethod (c$, "markSupported", 
function () {
return false;
});
Clazz.overrideMethod (c$, "mark", 
function (readlimit) {
}, "~N");
Clazz.overrideMethod (c$, "reset", 
function () {
throw  new java.io.IOException ("mark/reset not supported");
});
$_M(c$, "getTotalIn", 
function () {
return this.inflater.getTotalIn ();
});
$_M(c$, "getTotalOut", 
function () {
return this.inflater.getTotalOut ();
});
$_M(c$, "getAvailIn", 
function () {
if (this.inflater.avail_in <= 0) return null;
var tmp =  Clazz.newByteArray (this.inflater.avail_in, 0);
System.arraycopy (this.inflater.next_in, this.inflater.next_in_index, tmp, 0, this.inflater.avail_in);
return tmp;
});
$_M(c$, "readHeader", 
function () {
var empty = "".getBytes ();
this.inflater.setInput (empty, 0, 0, false);
this.inflater.setOutput (empty, 0, 0);
var err = this.inflater.inflate (0);
if (!this.inflater.istate.inParsingHeader ()) {
return;
}var b1 =  Clazz.newByteArray (1, 0);
do {
var i = this.$in.read (b1, 0, 1);
if (i <= 0) throw  new java.io.IOException ("no input");
this.inflater.setInput (b1, 0, b1.length, false);
err = this.inflater.inflate (0);
if (err != 0) throw  new java.io.IOException (this.inflater.msg);
} while (this.inflater.istate.inParsingHeader ());
});
$_M(c$, "getInflater", 
function () {
return this.inflater;
});
Clazz.defineStatics (c$,
"DEFAULT_BUFSIZE", 512);
});
Clazz.declarePackage ("java.util.zip");
Clazz.load (["JZ.InflaterInputStream"], "java.util.zip.InflaterInputStream", null, function () {
c$ = Clazz.decorateAsClass (function () {
this.inf = null;
Clazz.instantialize (this, arguments);
}, java.util.zip, "InflaterInputStream", JZ.InflaterInputStream);
Clazz.makeConstructor (c$, 
function ($in, inflater, size) {
Clazz.superConstructor (this, java.util.zip.InflaterInputStream, [$in, inflater, size, true]);
this.inf = inflater;
}, "java.io.InputStream,java.util.zip.Inflater,~N");
});
Clazz.declarePackage ("java.util.zip");
Clazz.load (["java.util.zip.InflaterInputStream", "$.CRC32"], "java.util.zip.GZIPInputStream", ["java.io.EOFException", "$.IOException", "java.util.zip.CheckedInputStream", "$.Inflater", "$.ZipException"], function () {
c$ = Clazz.decorateAsClass (function () {
this.crc = null;
this.eos = false;
this.$closed = false;
this.tmpbuf = null;
Clazz.instantialize (this, arguments);
}, java.util.zip, "GZIPInputStream", java.util.zip.InflaterInputStream);
Clazz.prepareFields (c$, function () {
this.crc =  new java.util.zip.CRC32 ();
this.tmpbuf =  Clazz.newByteArray (128, 0);
});
$_M(c$, "ensureOpen", 
($fz = function () {
if (this.$closed) {
throw  new java.io.IOException ("Stream closed");
}}, $fz.isPrivate = true, $fz));
Clazz.makeConstructor (c$, 
function ($in, size) {
Clazz.superConstructor (this, java.util.zip.GZIPInputStream, [$in,  new java.util.zip.Inflater ().init (0, true), size]);
this.readHeader ($in);
}, "java.io.InputStream,~N");
Clazz.overrideMethod (c$, "read", 
function (buf, off, len) {
this.ensureOpen ();
if (this.eos) {
return -1;
}var n = this.readInf (buf, off, len);
if (n == -1) {
if (this.readTrailer ()) this.eos = true;
 else return this.read (buf, off, len);
} else {
this.crc.update (buf, off, n);
}return n;
}, "~A,~N,~N");
$_M(c$, "close", 
function () {
if (!this.$closed) {
Clazz.superCall (this, java.util.zip.GZIPInputStream, "close", []);
this.eos = true;
this.$closed = true;
}});
$_M(c$, "readHeader", 
($fz = function (this_in) {
var $in =  new java.util.zip.CheckedInputStream (this_in, this.crc);
this.crc.reset ();
if (this.readUShort ($in) != 35615) {
throw  new java.util.zip.ZipException ("Not in GZIP format");
}if (this.readUByte ($in) != 8) {
throw  new java.util.zip.ZipException ("Unsupported compression method");
}var flg = this.readUByte ($in);
this.skipBytes ($in, 6);
var n = 10;
if ((flg & 4) == 4) {
var m = this.readUShort ($in);
this.skipBytes ($in, m);
n += m + 2;
}if ((flg & 8) == 8) {
do {
n++;
} while (this.readUByte ($in) != 0);
}if ((flg & 16) == 16) {
do {
n++;
} while (this.readUByte ($in) != 0);
}if ((flg & 2) == 2) {
var v = this.crc.getValue () & 0xffff;
if (this.readUShort ($in) != v) {
throw  new java.util.zip.ZipException ("Corrupt GZIP header");
}n += 2;
}this.crc.reset ();
return n;
}, $fz.isPrivate = true, $fz), "java.io.InputStream");
$_M(c$, "readTrailer", 
($fz = function () {
return true;
}, $fz.isPrivate = true, $fz));
$_M(c$, "readUShort", 
($fz = function ($in) {
var b = this.readUByte ($in);
return (this.readUByte ($in) << 8) | b;
}, $fz.isPrivate = true, $fz), "java.io.InputStream");
$_M(c$, "readUByte", 
($fz = function ($in) {
var b = $in.readByteAsInt ();
if (b == -1) {
throw  new java.io.EOFException ();
}if (b < -1 || b > 255) {
throw  new java.io.IOException (this.$in.getClass ().getName () + ".read() returned value out of range -1..255: " + b);
}return b;
}, $fz.isPrivate = true, $fz), "java.io.InputStream");
$_M(c$, "skipBytes", 
($fz = function ($in, n) {
while (n > 0) {
var len = $in.read (this.tmpbuf, 0, n < this.tmpbuf.length ? n : this.tmpbuf.length);
if (len == -1) {
throw  new java.io.EOFException ();
}n -= len;
}
}, $fz.isPrivate = true, $fz), "java.io.InputStream,~N");
Clazz.defineStatics (c$,
"GZIP_MAGIC", 0x8b1f,
"FHCRC", 2,
"FEXTRA", 4,
"FNAME", 8,
"FCOMMENT", 16);
});
Clazz.declarePackage ("JZ");
Clazz.load (null, "JZ.ZStream", ["JZ.Adler32"], function () {
c$ = Clazz.decorateAsClass (function () {
this.next_in = null;
this.next_in_index = 0;
this.avail_in = 0;
this.total_in = 0;
this.next_out = null;
this.next_out_index = 0;
this.avail_out = 0;
this.total_out = 0;
this.msg = null;
this.dstate = null;
this.istate = null;
this.data_type = 0;
this.checksum = null;
Clazz.instantialize (this, arguments);
}, JZ, "ZStream");
$_M(c$, "setAdler32", 
function () {
this.checksum =  new JZ.Adler32 ();
});
$_M(c$, "inflate", 
function (f) {
if (this.istate == null) return -2;
return this.istate.inflate (f);
}, "~N");
$_M(c$, "deflate", 
function (flush) {
if (this.dstate == null) {
return -2;
}return this.dstate.deflate (flush);
}, "~N");
$_M(c$, "flush_pending", 
function () {
var len = this.dstate.pending;
if (len > this.avail_out) len = this.avail_out;
if (len == 0) return;
if (this.dstate.pending_buf.length <= this.dstate.pending_out || this.next_out.length <= this.next_out_index || this.dstate.pending_buf.length < (this.dstate.pending_out + len) || this.next_out.length < (this.next_out_index + len)) {
}System.arraycopy (this.dstate.pending_buf, this.dstate.pending_out, this.next_out, this.next_out_index, len);
this.next_out_index += len;
this.dstate.pending_out += len;
this.total_out += len;
this.avail_out -= len;
this.dstate.pending -= len;
if (this.dstate.pending == 0) {
this.dstate.pending_out = 0;
}});
$_M(c$, "read_buf", 
function (buf, start, size) {
var len = this.avail_in;
if (len > size) len = size;
if (len == 0) return 0;
this.avail_in -= len;
if (this.dstate.wrap != 0) {
this.checksum.update (this.next_in, this.next_in_index, len);
}System.arraycopy (this.next_in, this.next_in_index, buf, start, len);
this.next_in_index += len;
this.total_in += len;
return len;
}, "~A,~N,~N");
$_M(c$, "getAdler", 
function () {
return this.checksum.getValue ();
});
$_M(c$, "free", 
function () {
this.next_in = null;
this.next_out = null;
this.msg = null;
});
$_M(c$, "setOutput", 
function (buf, off, len) {
this.next_out = buf;
this.next_out_index = off;
this.avail_out = len;
}, "~A,~N,~N");
$_M(c$, "setInput", 
function (buf, off, len, append) {
if (len <= 0 && append && this.next_in != null) return;
if (this.avail_in > 0 && append) {
var tmp =  Clazz.newByteArray (this.avail_in + len, 0);
System.arraycopy (this.next_in, this.next_in_index, tmp, 0, this.avail_in);
System.arraycopy (buf, off, tmp, this.avail_in, len);
this.next_in = tmp;
this.next_in_index = 0;
this.avail_in += len;
} else {
this.next_in = buf;
this.next_in_index = off;
this.avail_in = len;
}}, "~A,~N,~N,~B");
$_M(c$, "getAvailIn", 
function () {
return this.avail_in;
});
$_M(c$, "getTotalOut", 
function () {
return this.total_out;
});
$_M(c$, "getTotalIn", 
function () {
return this.total_in;
});
c$.getBytes = $_M(c$, "getBytes", 
function (s) {
{
var x = [];
for (var i = 0; i < s.length;i++) {
var pt = s.charCodeAt(i);
if (pt <= 0x7F) {
x.push(pt);
} else if (pt <= 0x7FF) {
x.push(0xC0|((pt>>6)&0x1F));
x.push(0x80|(pt&0x3F));
} else if (pt <= 0xFFFF) {
x.push(0xE0|((pt>>12)&0xF));
x.push(0x80|((pt>>6)&0x3F));
x.push(0x80|(pt&0x3F));
} else {
x.push(0x3F); // '?'
}
}
return (Int32Array != Array ? new Int32Array(x) : x);
}}, "~S");
Clazz.defineStatics (c$,
"Z_STREAM_ERROR", -2);
});
Clazz.declarePackage ("JZ");
Clazz.load (["JZ.ZStream"], "JZ.Inflater", ["JZ.Inflate"], function () {
c$ = Clazz.declareType (JZ, "Inflater", JZ.ZStream);
$_M(c$, "init", 
function (w, nowrap) {
this.setAdler32 ();
if (w == 0) w = 15;
this.istate =  new JZ.Inflate (this);
this.istate.inflateInit (nowrap ? -w : w);
return this;
}, "~N,~B");
Clazz.overrideMethod (c$, "inflate", 
function (f) {
if (this.istate == null) return -2;
var ret = this.istate.inflate (f);
return ret;
}, "~N");
Clazz.overrideMethod (c$, "end", 
function () {
if (this.istate == null) return -2;
var ret = this.istate.inflateEnd ();
return ret;
});
$_M(c$, "sync", 
function () {
if (this.istate == null) return -2;
return this.istate.inflateSync ();
});
$_M(c$, "syncPoint", 
function () {
if (this.istate == null) return -2;
return this.istate.inflateSyncPoint ();
});
$_M(c$, "setDictionary", 
function (dictionary, dictLength) {
if (this.istate == null) return -2;
return this.istate.inflateSetDictionary (dictionary, dictLength);
}, "~A,~N");
Clazz.overrideMethod (c$, "finished", 
function () {
return this.istate.mode == 12;
});
$_M(c$, "reset", 
function () {
this.avail_in = 0;
if (this.istate != null) this.istate.reset ();
});
Clazz.defineStatics (c$,
"MAX_WBITS", 15,
"DEF_WBITS", 15,
"$Z_STREAM_ERROR", -2);
});
Clazz.declarePackage ("JZ");
Clazz.load (["JZ.Checksum"], "JZ.Adler32", null, function () {
c$ = Clazz.decorateAsClass (function () {
this.s1 = 1;
this.s2 = 0;
this.b1 = null;
Clazz.instantialize (this, arguments);
}, JZ, "Adler32", null, JZ.Checksum);
Clazz.prepareFields (c$, function () {
this.b1 =  Clazz.newByteArray (1, 0);
});
Clazz.overrideMethod (c$, "resetLong", 
function (init) {
this.s1 = init & 0xffff;
this.s2 = (init >> 16) & 0xffff;
}, "~N");
Clazz.overrideMethod (c$, "reset", 
function () {
this.s1 = 1;
this.s2 = 0;
});
Clazz.overrideMethod (c$, "getValue", 
function () {
return ((this.s2 << 16) | this.s1);
});
Clazz.overrideMethod (c$, "update", 
function (buf, index, len) {
if (len == 1) {
this.s1 += buf[index++] & 0xff;
this.s2 += this.s1;
this.s1 %= 65521;
this.s2 %= 65521;
return;
}var len1 = Clazz.doubleToInt (len / 5552);
var len2 = len % 5552;
while (len1-- > 0) {
var k = 5552;
len -= k;
while (k-- > 0) {
this.s1 += buf[index++] & 0xff;
this.s2 += this.s1;
}
this.s1 %= 65521;
this.s2 %= 65521;
}
var k = len2;
len -= k;
while (k-- > 0) {
this.s1 += buf[index++] & 0xff;
this.s2 += this.s1;
}
this.s1 %= 65521;
this.s2 %= 65521;
}, "~A,~N,~N");
Clazz.overrideMethod (c$, "updateByteAsInt", 
function (b) {
this.b1[0] = b;
this.update (this.b1, 0, 1);
}, "~N");
Clazz.defineStatics (c$,
"BASE", 65521,
"NMAX", 5552);
});
Clazz.declarePackage ("JZ");
c$ = Clazz.decorateAsClass (function () {
this.dyn_tree = null;
this.max_code = 0;
this.stat_desc = null;
Clazz.instantialize (this, arguments);
}, JZ, "Tree");
c$.d_code = $_M(c$, "d_code", 
function (dist) {
return ((dist) < 256 ? JZ.Tree._dist_code[dist] : JZ.Tree._dist_code[256 + ((dist) >>> 7)]);
}, "~N");
$_M(c$, "gen_bitlen", 
function (s) {
var tree = this.dyn_tree;
var stree = this.stat_desc.static_tree;
var extra = this.stat_desc.extra_bits;
var base = this.stat_desc.extra_base;
var max_length = this.stat_desc.max_length;
var h;
var n;
var m;
var bits;
var xbits;
var f;
var overflow = 0;
for (bits = 0; bits <= 15; bits++) s.bl_count[bits] = 0;

tree[s.heap[s.heap_max] * 2 + 1] = 0;
for (h = s.heap_max + 1; h < 573; h++) {
n = s.heap[h];
bits = tree[tree[n * 2 + 1] * 2 + 1] + 1;
if (bits > max_length) {
bits = max_length;
overflow++;
}tree[n * 2 + 1] = bits;
if (n > this.max_code) continue;
s.bl_count[bits]++;
xbits = 0;
if (n >= base) xbits = extra[n - base];
f = tree[n * 2];
s.opt_len += f * (bits + xbits);
if (stree != null) s.static_len += f * (stree[n * 2 + 1] + xbits);
}
if (overflow == 0) return;
do {
bits = max_length - 1;
while (s.bl_count[bits] == 0) bits--;

s.bl_count[bits]--;
s.bl_count[bits + 1] += 2;
s.bl_count[max_length]--;
overflow -= 2;
} while (overflow > 0);
for (bits = max_length; bits != 0; bits--) {
n = s.bl_count[bits];
while (n != 0) {
m = s.heap[--h];
if (m > this.max_code) continue;
if (tree[m * 2 + 1] != bits) {
s.opt_len += (bits - tree[m * 2 + 1]) * tree[m * 2];
tree[m * 2 + 1] = bits;
}n--;
}
}
}, "JZ.Deflate");
$_M(c$, "build_tree", 
function (s) {
var tree = this.dyn_tree;
var stree = this.stat_desc.static_tree;
var elems = this.stat_desc.elems;
var n;
var m;
var max_code = -1;
var node;
s.heap_len = 0;
s.heap_max = 573;
for (n = 0; n < elems; n++) {
if (tree[n * 2] != 0) {
s.heap[++s.heap_len] = max_code = n;
s.depth[n] = 0;
} else {
tree[n * 2 + 1] = 0;
}}
while (s.heap_len < 2) {
node = s.heap[++s.heap_len] = (max_code < 2 ? ++max_code : 0);
tree[node * 2] = 1;
s.depth[node] = 0;
s.opt_len--;
if (stree != null) s.static_len -= stree[node * 2 + 1];
}
this.max_code = max_code;
for (n = Clazz.doubleToInt (s.heap_len / 2); n >= 1; n--) s.pqdownheap (tree, n);

node = elems;
do {
n = s.heap[1];
s.heap[1] = s.heap[s.heap_len--];
s.pqdownheap (tree, 1);
m = s.heap[1];
s.heap[--s.heap_max] = n;
s.heap[--s.heap_max] = m;
tree[node * 2] = (tree[n * 2] + tree[m * 2]);
s.depth[node] = (Math.max (s.depth[n], s.depth[m]) + 1);
tree[n * 2 + 1] = tree[m * 2 + 1] = node;
s.heap[1] = node++;
s.pqdownheap (tree, 1);
} while (s.heap_len >= 2);
s.heap[--s.heap_max] = s.heap[1];
this.gen_bitlen (s);
JZ.Tree.gen_codes (tree, max_code, s.bl_count);
}, "JZ.Deflate");
c$.gen_codes = $_M(c$, "gen_codes", 
function (tree, max_code, bl_count) {
var code = 0;
var bits;
var n;
JZ.Tree.next_code[0] = 0;
for (bits = 1; bits <= 15; bits++) {
JZ.Tree.next_code[bits] = code = ((code + bl_count[bits - 1]) << 1);
}
for (n = 0; n <= max_code; n++) {
var len = tree[n * 2 + 1];
if (len == 0) continue;
tree[n * 2] = (JZ.Tree.bi_reverse (JZ.Tree.next_code[len]++, len));
}
}, "~A,~N,~A");
c$.bi_reverse = $_M(c$, "bi_reverse", 
function (code, len) {
var res = 0;
do {
res |= code & 1;
code >>>= 1;
res <<= 1;
} while (--len > 0);
return res >>> 1;
}, "~N,~N");
Clazz.defineStatics (c$,
"MAX_BITS", 15,
"LITERALS", 256,
"LENGTH_CODES", 29,
"L_CODES", (286),
"HEAP_SIZE", (573),
"MAX_BL_BITS", 7,
"END_BLOCK", 256,
"REP_3_6", 16,
"REPZ_3_10", 17,
"REPZ_11_138", 18,
"extra_lbits", [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0],
"extra_dbits", [0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13],
"extra_blbits", [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 3, 7],
"bl_order", [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15],
"Buf_size", 16,
"DIST_CODE_LEN", 512,
"_dist_code", [0, 1, 2, 3, 4, 4, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 0, 0, 16, 17, 18, 18, 19, 19, 20, 20, 20, 20, 21, 21, 21, 21, 22, 22, 22, 22, 22, 22, 22, 22, 23, 23, 23, 23, 23, 23, 23, 23, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29],
"_length_code", [0, 1, 2, 3, 4, 5, 6, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 12, 12, 13, 13, 13, 13, 14, 14, 14, 14, 15, 15, 15, 15, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17, 17, 17, 17, 17, 17, 18, 18, 18, 18, 18, 18, 18, 18, 19, 19, 19, 19, 19, 19, 19, 19, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 27, 28],
"base_length", [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 0],
"base_dist", [0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384, 512, 768, 1024, 1536, 2048, 3072, 4096, 6144, 8192, 12288, 16384, 24576],
"next_code",  Clazz.newShortArray (16, 0));
Clazz.declarePackage ("JZ");
Clazz.load (["JZ.Tree"], "JZ.StaticTree", null, function () {
c$ = Clazz.decorateAsClass (function () {
this.static_tree = null;
this.extra_bits = null;
this.extra_base = 0;
this.elems = 0;
this.max_length = 0;
Clazz.instantialize (this, arguments);
}, JZ, "StaticTree");
Clazz.makeConstructor (c$, 
($fz = function (static_tree, extra_bits, extra_base, elems, max_length) {
this.static_tree = static_tree;
this.extra_bits = extra_bits;
this.extra_base = extra_base;
this.elems = elems;
this.max_length = max_length;
}, $fz.isPrivate = true, $fz), "~A,~A,~N,~N,~N");
Clazz.defineStatics (c$,
"MAX_BITS", 15,
"BL_CODES", 19,
"D_CODES", 30,
"LITERALS", 256,
"LENGTH_CODES", 29,
"L_CODES", (286),
"MAX_BL_BITS", 7,
"static_ltree", [12, 8, 140, 8, 76, 8, 204, 8, 44, 8, 172, 8, 108, 8, 236, 8, 28, 8, 156, 8, 92, 8, 220, 8, 60, 8, 188, 8, 124, 8, 252, 8, 2, 8, 130, 8, 66, 8, 194, 8, 34, 8, 162, 8, 98, 8, 226, 8, 18, 8, 146, 8, 82, 8, 210, 8, 50, 8, 178, 8, 114, 8, 242, 8, 10, 8, 138, 8, 74, 8, 202, 8, 42, 8, 170, 8, 106, 8, 234, 8, 26, 8, 154, 8, 90, 8, 218, 8, 58, 8, 186, 8, 122, 8, 250, 8, 6, 8, 134, 8, 70, 8, 198, 8, 38, 8, 166, 8, 102, 8, 230, 8, 22, 8, 150, 8, 86, 8, 214, 8, 54, 8, 182, 8, 118, 8, 246, 8, 14, 8, 142, 8, 78, 8, 206, 8, 46, 8, 174, 8, 110, 8, 238, 8, 30, 8, 158, 8, 94, 8, 222, 8, 62, 8, 190, 8, 126, 8, 254, 8, 1, 8, 129, 8, 65, 8, 193, 8, 33, 8, 161, 8, 97, 8, 225, 8, 17, 8, 145, 8, 81, 8, 209, 8, 49, 8, 177, 8, 113, 8, 241, 8, 9, 8, 137, 8, 73, 8, 201, 8, 41, 8, 169, 8, 105, 8, 233, 8, 25, 8, 153, 8, 89, 8, 217, 8, 57, 8, 185, 8, 121, 8, 249, 8, 5, 8, 133, 8, 69, 8, 197, 8, 37, 8, 165, 8, 101, 8, 229, 8, 21, 8, 149, 8, 85, 8, 213, 8, 53, 8, 181, 8, 117, 8, 245, 8, 13, 8, 141, 8, 77, 8, 205, 8, 45, 8, 173, 8, 109, 8, 237, 8, 29, 8, 157, 8, 93, 8, 221, 8, 61, 8, 189, 8, 125, 8, 253, 8, 19, 9, 275, 9, 147, 9, 403, 9, 83, 9, 339, 9, 211, 9, 467, 9, 51, 9, 307, 9, 179, 9, 435, 9, 115, 9, 371, 9, 243, 9, 499, 9, 11, 9, 267, 9, 139, 9, 395, 9, 75, 9, 331, 9, 203, 9, 459, 9, 43, 9, 299, 9, 171, 9, 427, 9, 107, 9, 363, 9, 235, 9, 491, 9, 27, 9, 283, 9, 155, 9, 411, 9, 91, 9, 347, 9, 219, 9, 475, 9, 59, 9, 315, 9, 187, 9, 443, 9, 123, 9, 379, 9, 251, 9, 507, 9, 7, 9, 263, 9, 135, 9, 391, 9, 71, 9, 327, 9, 199, 9, 455, 9, 39, 9, 295, 9, 167, 9, 423, 9, 103, 9, 359, 9, 231, 9, 487, 9, 23, 9, 279, 9, 151, 9, 407, 9, 87, 9, 343, 9, 215, 9, 471, 9, 55, 9, 311, 9, 183, 9, 439, 9, 119, 9, 375, 9, 247, 9, 503, 9, 15, 9, 271, 9, 143, 9, 399, 9, 79, 9, 335, 9, 207, 9, 463, 9, 47, 9, 303, 9, 175, 9, 431, 9, 111, 9, 367, 9, 239, 9, 495, 9, 31, 9, 287, 9, 159, 9, 415, 9, 95, 9, 351, 9, 223, 9, 479, 9, 63, 9, 319, 9, 191, 9, 447, 9, 127, 9, 383, 9, 255, 9, 511, 9, 0, 7, 64, 7, 32, 7, 96, 7, 16, 7, 80, 7, 48, 7, 112, 7, 8, 7, 72, 7, 40, 7, 104, 7, 24, 7, 88, 7, 56, 7, 120, 7, 4, 7, 68, 7, 36, 7, 100, 7, 20, 7, 84, 7, 52, 7, 116, 7, 3, 8, 131, 8, 67, 8, 195, 8, 35, 8, 163, 8, 99, 8, 227, 8],
"static_dtree", [0, 5, 16, 5, 8, 5, 24, 5, 4, 5, 20, 5, 12, 5, 28, 5, 2, 5, 18, 5, 10, 5, 26, 5, 6, 5, 22, 5, 14, 5, 30, 5, 1, 5, 17, 5, 9, 5, 25, 5, 5, 5, 21, 5, 13, 5, 29, 5, 3, 5, 19, 5, 11, 5, 27, 5, 7, 5, 23, 5]);
c$.static_l_desc = c$.prototype.static_l_desc =  new JZ.StaticTree (JZ.StaticTree.static_ltree, JZ.Tree.extra_lbits, 257, 286, 15);
c$.static_d_desc = c$.prototype.static_d_desc =  new JZ.StaticTree (JZ.StaticTree.static_dtree, JZ.Tree.extra_dbits, 0, 30, 15);
c$.static_bl_desc = c$.prototype.static_bl_desc =  new JZ.StaticTree (null, JZ.Tree.extra_blbits, 0, 19, 7);
});
Clazz.declarePackage ("JZ");
Clazz.load (["JZ.Tree"], "JZ.Deflate", ["JZ.CRC32", "$.GZIPHeader", "$.StaticTree"], function () {
c$ = Clazz.decorateAsClass (function () {
this.strm = null;
this.status = 0;
this.pending_buf = null;
this.pending_buf_size = 0;
this.pending_out = 0;
this.pending = 0;
this.wrap = 1;
this.data_type = 0;
this.method = 0;
this.last_flush = 0;
this.w_size = 0;
this.w_bits = 0;
this.w_mask = 0;
this.window = null;
this.window_size = 0;
this.prev = null;
this.head = null;
this.ins_h = 0;
this.hash_size = 0;
this.hash_bits = 0;
this.hash_mask = 0;
this.hash_shift = 0;
this.block_start = 0;
this.match_length = 0;
this.prev_match = 0;
this.match_available = 0;
this.strstart = 0;
this.match_start = 0;
this.lookahead = 0;
this.prev_length = 0;
this.max_chain_length = 0;
this.max_lazy_match = 0;
this.level = 0;
this.strategy = 0;
this.good_match = 0;
this.nice_match = 0;
this.dyn_ltree = null;
this.dyn_dtree = null;
this.bl_tree = null;
this.l_desc = null;
this.d_desc = null;
this.bl_desc = null;
this.bl_count = null;
this.heap = null;
this.heap_len = 0;
this.heap_max = 0;
this.depth = null;
this.l_buf = 0;
this.lit_bufsize = 0;
this.last_lit = 0;
this.d_buf = 0;
this.opt_len = 0;
this.static_len = 0;
this.matches = 0;
this.last_eob_len = 0;
this.bi_buf = 0;
this.bi_valid = 0;
this.gheader = null;
Clazz.instantialize (this, arguments);
}, JZ, "Deflate");
Clazz.prepareFields (c$, function () {
this.l_desc =  new JZ.Tree ();
this.d_desc =  new JZ.Tree ();
this.bl_desc =  new JZ.Tree ();
this.bl_count =  Clazz.newShortArray (16, 0);
this.heap =  Clazz.newIntArray (573, 0);
this.depth =  Clazz.newByteArray (573, 0);
});
Clazz.makeConstructor (c$, 
function (strm) {
this.strm = strm;
this.dyn_ltree =  Clazz.newShortArray (1146, 0);
this.dyn_dtree =  Clazz.newShortArray (122, 0);
this.bl_tree =  Clazz.newShortArray (78, 0);
}, "JZ.ZStream");
$_M(c$, "deflateInit", 
function (level) {
return this.deflateInit2 (level, 15);
}, "~N");
$_M(c$, "deflateInit2", 
function (level, bits) {
return this.deflateInit5 (level, 8, bits, 8, 0);
}, "~N,~N");
$_M(c$, "deflateInit3", 
function (level, bits, memlevel) {
return this.deflateInit5 (level, 8, bits, memlevel, 0);
}, "~N,~N,~N");
$_M(c$, "lm_init", 
function () {
this.window_size = 2 * this.w_size;
this.head[this.hash_size - 1] = 0;
for (var i = 0; i < this.hash_size - 1; i++) {
this.head[i] = 0;
}
this.max_lazy_match = JZ.Deflate.config_table[this.level].max_lazy;
this.good_match = JZ.Deflate.config_table[this.level].good_length;
this.nice_match = JZ.Deflate.config_table[this.level].nice_length;
this.max_chain_length = JZ.Deflate.config_table[this.level].max_chain;
this.strstart = 0;
this.block_start = 0;
this.lookahead = 0;
this.match_length = this.prev_length = 2;
this.match_available = 0;
this.ins_h = 0;
});
$_M(c$, "tr_init", 
function () {
this.l_desc.dyn_tree = this.dyn_ltree;
this.l_desc.stat_desc = JZ.StaticTree.static_l_desc;
this.d_desc.dyn_tree = this.dyn_dtree;
this.d_desc.stat_desc = JZ.StaticTree.static_d_desc;
this.bl_desc.dyn_tree = this.bl_tree;
this.bl_desc.stat_desc = JZ.StaticTree.static_bl_desc;
this.bi_buf = 0;
this.bi_valid = 0;
this.last_eob_len = 8;
this.init_block ();
});
$_M(c$, "init_block", 
function () {
for (var i = 0; i < 286; i++) this.dyn_ltree[i * 2] = 0;

for (var i = 0; i < 30; i++) this.dyn_dtree[i * 2] = 0;

for (var i = 0; i < 19; i++) this.bl_tree[i * 2] = 0;

this.dyn_ltree[512] = 1;
this.opt_len = this.static_len = 0;
this.last_lit = this.matches = 0;
});
$_M(c$, "pqdownheap", 
function (tree, k) {
var v = this.heap[k];
var j = k << 1;
while (j <= this.heap_len) {
if (j < this.heap_len && JZ.Deflate.smaller (tree, this.heap[j + 1], this.heap[j], this.depth)) {
j++;
}if (JZ.Deflate.smaller (tree, v, this.heap[j], this.depth)) break;
this.heap[k] = this.heap[j];
k = j;
j <<= 1;
}
this.heap[k] = v;
}, "~A,~N");
c$.smaller = $_M(c$, "smaller", 
function (tree, n, m, depth) {
var tn2 = tree[n * 2];
var tm2 = tree[m * 2];
return (tn2 < tm2 || (tn2 == tm2 && depth[n] <= depth[m]));
}, "~A,~N,~N,~A");
$_M(c$, "scan_tree", 
function (tree, max_code) {
var n;
var prevlen = -1;
var curlen;
var nextlen = tree[1];
var count = 0;
var max_count = 7;
var min_count = 4;
if (nextlen == 0) {
max_count = 138;
min_count = 3;
}tree[(max_code + 1) * 2 + 1] = 0xffff;
for (n = 0; n <= max_code; n++) {
curlen = nextlen;
nextlen = tree[(n + 1) * 2 + 1];
if (++count < max_count && curlen == nextlen) {
continue;
} else if (count < min_count) {
this.bl_tree[curlen * 2] += count;
} else if (curlen != 0) {
if (curlen != prevlen) this.bl_tree[curlen * 2]++;
this.bl_tree[32]++;
} else if (count <= 10) {
this.bl_tree[34]++;
} else {
this.bl_tree[36]++;
}count = 0;
prevlen = curlen;
if (nextlen == 0) {
max_count = 138;
min_count = 3;
} else if (curlen == nextlen) {
max_count = 6;
min_count = 3;
} else {
max_count = 7;
min_count = 4;
}}
}, "~A,~N");
$_M(c$, "build_bl_tree", 
function () {
var max_blindex;
this.scan_tree (this.dyn_ltree, this.l_desc.max_code);
this.scan_tree (this.dyn_dtree, this.d_desc.max_code);
this.bl_desc.build_tree (this);
for (max_blindex = 18; max_blindex >= 3; max_blindex--) {
if (this.bl_tree[JZ.Tree.bl_order[max_blindex] * 2 + 1] != 0) break;
}
this.opt_len += 3 * (max_blindex + 1) + 5 + 5 + 4;
return max_blindex;
});
$_M(c$, "send_all_trees", 
function (lcodes, dcodes, blcodes) {
var rank;
this.send_bits (lcodes - 257, 5);
this.send_bits (dcodes - 1, 5);
this.send_bits (blcodes - 4, 4);
for (rank = 0; rank < blcodes; rank++) {
this.send_bits (this.bl_tree[JZ.Tree.bl_order[rank] * 2 + 1], 3);
}
this.send_tree (this.dyn_ltree, lcodes - 1);
this.send_tree (this.dyn_dtree, dcodes - 1);
}, "~N,~N,~N");
$_M(c$, "send_tree", 
function (tree, max_code) {
var n;
var prevlen = -1;
var curlen;
var nextlen = tree[1];
var count = 0;
var max_count = 7;
var min_count = 4;
if (nextlen == 0) {
max_count = 138;
min_count = 3;
}for (n = 0; n <= max_code; n++) {
curlen = nextlen;
nextlen = tree[(n + 1) * 2 + 1];
if (++count < max_count && curlen == nextlen) {
continue;
} else if (count < min_count) {
do {
this.send_code (curlen, this.bl_tree);
} while (--count != 0);
} else if (curlen != 0) {
if (curlen != prevlen) {
this.send_code (curlen, this.bl_tree);
count--;
}this.send_code (16, this.bl_tree);
this.send_bits (count - 3, 2);
} else if (count <= 10) {
this.send_code (17, this.bl_tree);
this.send_bits (count - 3, 3);
} else {
this.send_code (18, this.bl_tree);
this.send_bits (count - 11, 7);
}count = 0;
prevlen = curlen;
if (nextlen == 0) {
max_count = 138;
min_count = 3;
} else if (curlen == nextlen) {
max_count = 6;
min_count = 3;
} else {
max_count = 7;
min_count = 4;
}}
}, "~A,~N");
$_M(c$, "put_byte", 
function (p, start, len) {
System.arraycopy (p, start, this.pending_buf, this.pending, len);
this.pending += len;
}, "~A,~N,~N");
$_M(c$, "put_byteB", 
function (c) {
{
this.pending_buf[this.pending++] = c&0xff;
}}, "~N");
$_M(c$, "put_short", 
function (w) {
this.put_byteB ((w));
this.put_byteB ((w >>> 8));
}, "~N");
$_M(c$, "putShortMSB", 
function (b) {
this.put_byteB ((b >> 8));
this.put_byteB ((b));
}, "~N");
$_M(c$, "send_code", 
function (c, tree) {
var c2 = c * 2;
this.send_bits ((tree[c2] & 0xffff), (tree[c2 + 1] & 0xffff));
}, "~N,~A");
$_M(c$, "send_bits", 
function (value, length) {
var len = length;
if (this.bi_valid > 16 - len) {
var val = value;
this.bi_buf |= ((val << this.bi_valid) & 0xffff);
this.put_short (this.bi_buf);
this.bi_buf = ((val >>> (16 - this.bi_valid)) & 0xffff);
this.bi_valid += len - 16;
} else {
this.bi_buf |= (((value) << this.bi_valid) & 0xffff);
this.bi_valid += len;
}}, "~N,~N");
$_M(c$, "_tr_align", 
function () {
this.send_bits (2, 3);
this.send_code (256, JZ.StaticTree.static_ltree);
this.bi_flush ();
if (1 + this.last_eob_len + 10 - this.bi_valid < 9) {
this.send_bits (2, 3);
this.send_code (256, JZ.StaticTree.static_ltree);
this.bi_flush ();
}this.last_eob_len = 7;
});
$_M(c$, "_tr_tally", 
function (dist, lc) {
this.pending_buf[this.d_buf + this.last_lit * 2] = (dist >>> 8);
this.pending_buf[this.d_buf + this.last_lit * 2 + 1] = dist;
this.pending_buf[this.l_buf + this.last_lit] = lc;
this.last_lit++;
if (dist == 0) {
this.dyn_ltree[lc * 2]++;
} else {
this.matches++;
dist--;
this.dyn_ltree[(JZ.Tree._length_code[lc] + 256 + 1) * 2]++;
this.dyn_dtree[JZ.Tree.d_code (dist) * 2]++;
}if ((this.last_lit & 0x1fff) == 0 && this.level > 2) {
var out_length = this.last_lit * 8;
var in_length = this.strstart - this.block_start;
var dcode;
for (dcode = 0; dcode < 30; dcode++) {
out_length += this.dyn_dtree[dcode * 2] * (5 + JZ.Tree.extra_dbits[dcode]);
}
out_length >>>= 3;
if ((this.matches < (Clazz.doubleToInt (this.last_lit / 2))) && out_length < Clazz.doubleToInt (in_length / 2)) return true;
}return (this.last_lit == this.lit_bufsize - 1);
}, "~N,~N");
$_M(c$, "compress_block", 
function (ltree, dtree) {
var dist;
var lc;
var lx = 0;
var code;
var extra;
if (this.last_lit != 0) {
do {
dist = ((this.pending_buf[this.d_buf + lx * 2] << 8) & 0xff00) | (this.pending_buf[this.d_buf + lx * 2 + 1] & 0xff);
lc = (this.pending_buf[this.l_buf + lx]) & 0xff;
lx++;
if (dist == 0) {
this.send_code (lc, ltree);
} else {
code = JZ.Tree._length_code[lc];
this.send_code (code + 256 + 1, ltree);
extra = JZ.Tree.extra_lbits[code];
if (extra != 0) {
lc -= JZ.Tree.base_length[code];
this.send_bits (lc, extra);
}dist--;
code = JZ.Tree.d_code (dist);
this.send_code (code, dtree);
extra = JZ.Tree.extra_dbits[code];
if (extra != 0) {
dist -= JZ.Tree.base_dist[code];
this.send_bits (dist, extra);
}}} while (lx < this.last_lit);
}this.send_code (256, ltree);
this.last_eob_len = ltree[513];
}, "~A,~A");
$_M(c$, "set_data_type", 
function () {
var n = 0;
var ascii_freq = 0;
var bin_freq = 0;
while (n < 7) {
bin_freq += this.dyn_ltree[n * 2];
n++;
}
while (n < 128) {
ascii_freq += this.dyn_ltree[n * 2];
n++;
}
while (n < 256) {
bin_freq += this.dyn_ltree[n * 2];
n++;
}
this.data_type = (bin_freq > (ascii_freq >>> 2) ? 0 : 1);
});
$_M(c$, "bi_flush", 
function () {
if (this.bi_valid == 16) {
this.put_short (this.bi_buf);
this.bi_buf = 0;
this.bi_valid = 0;
} else if (this.bi_valid >= 8) {
this.put_byteB (this.bi_buf);
this.bi_buf >>>= 8;
this.bi_valid -= 8;
}});
$_M(c$, "bi_windup", 
function () {
if (this.bi_valid > 8) {
this.put_short (this.bi_buf);
} else if (this.bi_valid > 0) {
this.put_byteB (this.bi_buf);
}this.bi_buf = 0;
this.bi_valid = 0;
});
$_M(c$, "copy_block", 
function (buf, len, header) {
this.bi_windup ();
this.last_eob_len = 8;
if (header) {
this.put_short (len);
this.put_short (~len);
}this.put_byte (this.window, buf, len);
}, "~N,~N,~B");
$_M(c$, "flush_block_only", 
function (eof) {
this._tr_flush_block (this.block_start >= 0 ? this.block_start : -1, this.strstart - this.block_start, eof);
this.block_start = this.strstart;
this.strm.flush_pending ();
}, "~B");
$_M(c$, "deflate_stored", 
function (flush) {
var max_block_size = 0xffff;
var max_start;
if (max_block_size > this.pending_buf_size - 5) {
max_block_size = this.pending_buf_size - 5;
}while (true) {
if (this.lookahead <= 1) {
this.fill_window ();
if (this.lookahead == 0 && flush == 0) return 0;
if (this.lookahead == 0) break;
}this.strstart += this.lookahead;
this.lookahead = 0;
max_start = this.block_start + max_block_size;
if (this.strstart == 0 || this.strstart >= max_start) {
this.lookahead = (this.strstart - max_start);
this.strstart = max_start;
this.flush_block_only (false);
if (this.strm.avail_out == 0) return 0;
}if (this.strstart - this.block_start >= this.w_size - 262) {
this.flush_block_only (false);
if (this.strm.avail_out == 0) return 0;
}}
this.flush_block_only (flush == 4);
if (this.strm.avail_out == 0) return (flush == 4) ? 2 : 0;
return flush == 4 ? 3 : 1;
}, "~N");
$_M(c$, "_tr_stored_block", 
function (buf, stored_len, eof) {
this.send_bits ((0) + (eof ? 1 : 0), 3);
this.copy_block (buf, stored_len, true);
}, "~N,~N,~B");
$_M(c$, "_tr_flush_block", 
function (buf, stored_len, eof) {
var opt_lenb;
var static_lenb;
var max_blindex = 0;
if (this.level > 0) {
if (this.data_type == 2) this.set_data_type ();
this.l_desc.build_tree (this);
this.d_desc.build_tree (this);
max_blindex = this.build_bl_tree ();
opt_lenb = (this.opt_len + 3 + 7) >>> 3;
static_lenb = (this.static_len + 3 + 7) >>> 3;
if (static_lenb <= opt_lenb) opt_lenb = static_lenb;
} else {
opt_lenb = static_lenb = stored_len + 5;
}if (stored_len + 4 <= opt_lenb && buf != -1) {
this._tr_stored_block (buf, stored_len, eof);
} else if (static_lenb == opt_lenb) {
this.send_bits ((2) + (eof ? 1 : 0), 3);
this.compress_block (JZ.StaticTree.static_ltree, JZ.StaticTree.static_dtree);
} else {
this.send_bits ((4) + (eof ? 1 : 0), 3);
this.send_all_trees (this.l_desc.max_code + 1, this.d_desc.max_code + 1, max_blindex + 1);
this.compress_block (this.dyn_ltree, this.dyn_dtree);
}this.init_block ();
if (eof) {
this.bi_windup ();
}}, "~N,~N,~B");
$_M(c$, "fill_window", 
function () {
var n;
var m;
var p;
var more;
do {
more = (this.window_size - this.lookahead - this.strstart);
if (more == 0 && this.strstart == 0 && this.lookahead == 0) {
more = this.w_size;
} else if (more == -1) {
more--;
} else if (this.strstart >= this.w_size + this.w_size - 262) {
System.arraycopy (this.window, this.w_size, this.window, 0, this.w_size);
this.match_start -= this.w_size;
this.strstart -= this.w_size;
this.block_start -= this.w_size;
n = this.hash_size;
p = n;
do {
m = (this.head[--p] & 0xffff);
this.head[p] = (m >= this.w_size ? (m - this.w_size) : 0);
} while (--n != 0);
n = this.w_size;
p = n;
do {
m = (this.prev[--p] & 0xffff);
this.prev[p] = (m >= this.w_size ? (m - this.w_size) : 0);
} while (--n != 0);
more += this.w_size;
}if (this.strm.avail_in == 0) return;
n = this.strm.read_buf (this.window, this.strstart + this.lookahead, more);
this.lookahead += n;
if (this.lookahead >= 3) {
this.ins_h = this.window[this.strstart] & 0xff;
this.ins_h = (((this.ins_h) << this.hash_shift) ^ (this.window[this.strstart + 1] & 0xff)) & this.hash_mask;
}} while (this.lookahead < 262 && this.strm.avail_in != 0);
});
$_M(c$, "deflate_fast", 
function (flush) {
var hash_head = 0;
var bflush;
while (true) {
if (this.lookahead < 262) {
this.fill_window ();
if (this.lookahead < 262 && flush == 0) {
return 0;
}if (this.lookahead == 0) break;
}if (this.lookahead >= 3) {
this.ins_h = (((this.ins_h) << this.hash_shift) ^ (this.window[(this.strstart) + (2)] & 0xff)) & this.hash_mask;
hash_head = (this.head[this.ins_h] & 0xffff);
this.prev[this.strstart & this.w_mask] = this.head[this.ins_h];
this.head[this.ins_h] = this.strstart;
}if (hash_head != 0 && ((this.strstart - hash_head) & 0xffff) <= this.w_size - 262) {
if (this.strategy != 2) {
this.match_length = this.longest_match (hash_head);
}}if (this.match_length >= 3) {
bflush = this._tr_tally (this.strstart - this.match_start, this.match_length - 3);
this.lookahead -= this.match_length;
if (this.match_length <= this.max_lazy_match && this.lookahead >= 3) {
this.match_length--;
do {
this.strstart++;
this.ins_h = ((this.ins_h << this.hash_shift) ^ (this.window[(this.strstart) + (2)] & 0xff)) & this.hash_mask;
hash_head = (this.head[this.ins_h] & 0xffff);
this.prev[this.strstart & this.w_mask] = this.head[this.ins_h];
this.head[this.ins_h] = this.strstart;
} while (--this.match_length != 0);
this.strstart++;
} else {
this.strstart += this.match_length;
this.match_length = 0;
this.ins_h = this.window[this.strstart] & 0xff;
this.ins_h = (((this.ins_h) << this.hash_shift) ^ (this.window[this.strstart + 1] & 0xff)) & this.hash_mask;
}} else {
bflush = this._tr_tally (0, this.window[this.strstart] & 0xff);
this.lookahead--;
this.strstart++;
}if (bflush) {
this.flush_block_only (false);
if (this.strm.avail_out == 0) return 0;
}}
this.flush_block_only (flush == 4);
if (this.strm.avail_out == 0) {
if (flush == 4) return 2;
return 0;
}return flush == 4 ? 3 : 1;
}, "~N");
$_M(c$, "deflate_slow", 
function (flush) {
var hash_head = 0;
var bflush;
while (true) {
if (this.lookahead < 262) {
this.fill_window ();
if (this.lookahead < 262 && flush == 0) {
return 0;
}if (this.lookahead == 0) break;
}if (this.lookahead >= 3) {
this.ins_h = (((this.ins_h) << this.hash_shift) ^ (this.window[(this.strstart) + (2)] & 0xff)) & this.hash_mask;
hash_head = (this.head[this.ins_h] & 0xffff);
this.prev[this.strstart & this.w_mask] = this.head[this.ins_h];
this.head[this.ins_h] = this.strstart;
}this.prev_length = this.match_length;
this.prev_match = this.match_start;
this.match_length = 2;
if (hash_head != 0 && this.prev_length < this.max_lazy_match && ((this.strstart - hash_head) & 0xffff) <= this.w_size - 262) {
if (this.strategy != 2) {
this.match_length = this.longest_match (hash_head);
}if (this.match_length <= 5 && (this.strategy == 1 || (this.match_length == 3 && this.strstart - this.match_start > 4096))) {
this.match_length = 2;
}}if (this.prev_length >= 3 && this.match_length <= this.prev_length) {
var max_insert = this.strstart + this.lookahead - 3;
bflush = this._tr_tally (this.strstart - 1 - this.prev_match, this.prev_length - 3);
this.lookahead -= this.prev_length - 1;
this.prev_length -= 2;
do {
if (++this.strstart <= max_insert) {
this.ins_h = (((this.ins_h) << this.hash_shift) ^ (this.window[(this.strstart) + (2)] & 0xff)) & this.hash_mask;
hash_head = (this.head[this.ins_h] & 0xffff);
this.prev[this.strstart & this.w_mask] = this.head[this.ins_h];
this.head[this.ins_h] = this.strstart;
}} while (--this.prev_length != 0);
this.match_available = 0;
this.match_length = 2;
this.strstart++;
if (bflush) {
this.flush_block_only (false);
if (this.strm.avail_out == 0) return 0;
}} else if (this.match_available != 0) {
bflush = this._tr_tally (0, this.window[this.strstart - 1] & 0xff);
if (bflush) {
this.flush_block_only (false);
}this.strstart++;
this.lookahead--;
if (this.strm.avail_out == 0) return 0;
} else {
this.match_available = 1;
this.strstart++;
this.lookahead--;
}}
if (this.match_available != 0) {
bflush = this._tr_tally (0, this.window[this.strstart - 1] & 0xff);
this.match_available = 0;
}this.flush_block_only (flush == 4);
if (this.strm.avail_out == 0) {
if (flush == 4) return 2;
return 0;
}return flush == 4 ? 3 : 1;
}, "~N");
$_M(c$, "longest_match", 
function (cur_match) {
var chain_length = this.max_chain_length;
var scan = this.strstart;
var match;
var len;
var best_len = this.prev_length;
var limit = this.strstart > (this.w_size - 262) ? this.strstart - (this.w_size - 262) : 0;
var nice_match = this.nice_match;
var wmask = this.w_mask;
var strend = this.strstart + 258;
var scan_end1 = this.window[scan + best_len - 1];
var scan_end = this.window[scan + best_len];
if (this.prev_length >= this.good_match) {
chain_length >>= 2;
}if (nice_match > this.lookahead) nice_match = this.lookahead;
do {
match = cur_match;
if (this.window[match + best_len] != scan_end || this.window[match + best_len - 1] != scan_end1 || this.window[match] != this.window[scan] || this.window[++match] != this.window[scan + 1]) continue;
scan += 2;
match++;
do {
} while (this.window[++scan] == this.window[++match] && this.window[++scan] == this.window[++match] && this.window[++scan] == this.window[++match] && this.window[++scan] == this.window[++match] && this.window[++scan] == this.window[++match] && this.window[++scan] == this.window[++match] && this.window[++scan] == this.window[++match] && this.window[++scan] == this.window[++match] && scan < strend);
len = 258 - (strend - scan);
scan = strend - 258;
if (len > best_len) {
this.match_start = cur_match;
best_len = len;
if (len >= nice_match) break;
scan_end1 = this.window[scan + best_len - 1];
scan_end = this.window[scan + best_len];
}} while ((cur_match = (this.prev[cur_match & wmask] & 0xffff)) > limit && --chain_length != 0);
if (best_len <= this.lookahead) return best_len;
return this.lookahead;
}, "~N");
$_M(c$, "deflateInit5", 
($fz = function (level, method, windowBits, memLevel, strategy) {
var wrap = 1;
this.strm.msg = null;
if (level == -1) level = 6;
if (windowBits < 0) {
wrap = 0;
windowBits = -windowBits;
} else if (windowBits > 15) {
wrap = 2;
windowBits -= 16;
this.strm.checksum =  new JZ.CRC32 ();
}if (memLevel < 1 || memLevel > 9 || method != 8 || windowBits < 9 || windowBits > 15 || level < 0 || level > 9 || strategy < 0 || strategy > 2) {
return -2;
}this.strm.dstate = this;
this.wrap = wrap;
this.w_bits = windowBits;
this.w_size = 1 << this.w_bits;
this.w_mask = this.w_size - 1;
this.hash_bits = memLevel + 7;
this.hash_size = 1 << this.hash_bits;
this.hash_mask = this.hash_size - 1;
this.hash_shift = (Clazz.doubleToInt ((this.hash_bits + 3 - 1) / 3));
this.window =  Clazz.newByteArray (this.w_size * 2, 0);
this.prev =  Clazz.newShortArray (this.w_size, 0);
this.head =  Clazz.newShortArray (this.hash_size, 0);
this.lit_bufsize = 1 << (memLevel + 6);
this.pending_buf =  Clazz.newByteArray (this.lit_bufsize * 4, 0);
this.pending_buf_size = this.lit_bufsize * 4;
this.d_buf = Clazz.doubleToInt (this.lit_bufsize / 2);
this.l_buf = (3) * this.lit_bufsize;
this.level = level;
this.strategy = strategy;
this.method = method;
return this.deflateReset ();
}, $fz.isPrivate = true, $fz), "~N,~N,~N,~N,~N");
$_M(c$, "deflateReset", 
function () {
this.strm.total_in = this.strm.total_out = 0;
this.strm.msg = null;
this.strm.data_type = 2;
this.pending = 0;
this.pending_out = 0;
if (this.wrap < 0) {
this.wrap = -this.wrap;
}this.status = (this.wrap == 0) ? 113 : 42;
this.strm.checksum.reset ();
this.last_flush = 0;
this.tr_init ();
this.lm_init ();
return 0;
});
$_M(c$, "deflateEnd", 
function () {
if (this.status != 42 && this.status != 113 && this.status != 666) {
return -2;
}this.pending_buf = null;
this.head = null;
this.prev = null;
this.window = null;
return this.status == 113 ? -3 : 0;
});
$_M(c$, "deflateParams", 
function (_level, _strategy) {
var err = 0;
if (_level == -1) {
_level = 6;
}if (_level < 0 || _level > 9 || _strategy < 0 || _strategy > 2) {
return -2;
}if (JZ.Deflate.config_table[this.level].func != JZ.Deflate.config_table[_level].func && this.strm.total_in != 0) {
err = this.strm.deflate (1);
}if (this.level != _level) {
this.level = _level;
this.max_lazy_match = JZ.Deflate.config_table[this.level].max_lazy;
this.good_match = JZ.Deflate.config_table[this.level].good_length;
this.nice_match = JZ.Deflate.config_table[this.level].nice_length;
this.max_chain_length = JZ.Deflate.config_table[this.level].max_chain;
}this.strategy = _strategy;
return err;
}, "~N,~N");
$_M(c$, "deflateSetDictionary", 
function (dictionary, dictLength) {
var length = dictLength;
var index = 0;
if (dictionary == null || this.status != 42) return -2;
this.strm.checksum.update (dictionary, 0, dictLength);
if (length < 3) return 0;
if (length > this.w_size - 262) {
length = this.w_size - 262;
index = dictLength - length;
}System.arraycopy (dictionary, index, this.window, 0, length);
this.strstart = length;
this.block_start = length;
this.ins_h = this.window[0] & 0xff;
this.ins_h = (((this.ins_h) << this.hash_shift) ^ (this.window[1] & 0xff)) & this.hash_mask;
for (var n = 0; n <= length - 3; n++) {
this.ins_h = (((this.ins_h) << this.hash_shift) ^ (this.window[(n) + (2)] & 0xff)) & this.hash_mask;
this.prev[n & this.w_mask] = this.head[this.ins_h];
this.head[this.ins_h] = n;
}
return 0;
}, "~A,~N");
$_M(c$, "deflate", 
function (flush) {
var old_flush;
if (flush > 4 || flush < 0) {
return -2;
}if (this.strm.next_out == null || (this.strm.next_in == null && this.strm.avail_in != 0) || (this.status == 666 && flush != 4)) {
this.strm.msg = JZ.Deflate.z_errmsg[4];
return -2;
}if (this.strm.avail_out == 0) {
this.strm.msg = JZ.Deflate.z_errmsg[7];
return -5;
}old_flush = this.last_flush;
this.last_flush = flush;
if (this.status == 42) {
if (this.wrap == 2) {
this.getGZIPHeader ().put (this);
this.status = 113;
this.strm.checksum.reset ();
} else {
var header = (8 + ((this.w_bits - 8) << 4)) << 8;
var level_flags = ((this.level - 1) & 0xff) >> 1;
if (level_flags > 3) level_flags = 3;
header |= (level_flags << 6);
if (this.strstart != 0) header |= 32;
header += 31 - (header % 31);
this.status = 113;
this.putShortMSB (header);
if (this.strstart != 0) {
var adler = this.strm.checksum.getValue ();
this.putShortMSB ((adler >>> 16));
this.putShortMSB ((adler & 0xffff));
}this.strm.checksum.reset ();
}}if (this.pending != 0) {
this.strm.flush_pending ();
if (this.strm.avail_out == 0) {
this.last_flush = -1;
return 0;
}} else if (this.strm.avail_in == 0 && flush <= old_flush && flush != 4) {
this.strm.msg = JZ.Deflate.z_errmsg[7];
return -5;
}if (this.status == 666 && this.strm.avail_in != 0) {
this.strm.msg = JZ.Deflate.z_errmsg[7];
return -5;
}if (this.strm.avail_in != 0 || this.lookahead != 0 || (flush != 0 && this.status != 666)) {
var bstate = -1;
switch (JZ.Deflate.config_table[this.level].func) {
case 0:
bstate = this.deflate_stored (flush);
break;
case 1:
bstate = this.deflate_fast (flush);
break;
case 2:
bstate = this.deflate_slow (flush);
break;
default:
}
if (bstate == 2 || bstate == 3) {
this.status = 666;
}if (bstate == 0 || bstate == 2) {
if (this.strm.avail_out == 0) {
this.last_flush = -1;
}return 0;
}if (bstate == 1) {
if (flush == 1) {
this._tr_align ();
} else {
this._tr_stored_block (0, 0, false);
if (flush == 3) {
for (var i = 0; i < this.hash_size; i++) this.head[i] = 0;

}}this.strm.flush_pending ();
if (this.strm.avail_out == 0) {
this.last_flush = -1;
return 0;
}}}if (flush != 4) return 0;
if (this.wrap <= 0) return 1;
if (this.wrap == 2) {
var adler = this.strm.checksum.getValue ();
this.put_byteB ((adler & 0xff));
this.put_byteB (((adler >> 8) & 0xff));
this.put_byteB (((adler >> 16) & 0xff));
this.put_byteB (((adler >> 24) & 0xff));
this.put_byteB ((this.strm.total_in & 0xff));
this.put_byteB (((this.strm.total_in >> 8) & 0xff));
this.put_byteB (((this.strm.total_in >> 16) & 0xff));
this.put_byteB (((this.strm.total_in >> 24) & 0xff));
this.getGZIPHeader ().setCRC (adler);
} else {
var adler = this.strm.checksum.getValue ();
this.putShortMSB ((adler >>> 16));
this.putShortMSB ((adler & 0xffff));
}this.strm.flush_pending ();
if (this.wrap > 0) this.wrap = -this.wrap;
return this.pending != 0 ? 0 : 1;
}, "~N");
$_M(c$, "getGZIPHeader", 
function () {
if (this.gheader == null) {
this.gheader =  new JZ.GZIPHeader ();
}return this.gheader;
});
$_M(c$, "getBytesRead", 
function () {
return this.strm.total_in;
});
$_M(c$, "getBytesWritten", 
function () {
return this.strm.total_out;
});
Clazz.pu$h ();
c$ = Clazz.decorateAsClass (function () {
this.good_length = 0;
this.max_lazy = 0;
this.nice_length = 0;
this.max_chain = 0;
this.func = 0;
Clazz.instantialize (this, arguments);
}, JZ.Deflate, "Config");
Clazz.makeConstructor (c$, 
function (a, b, c, d, e) {
this.good_length = a;
this.max_lazy = b;
this.nice_length = c;
this.max_chain = d;
this.func = e;
}, "~N,~N,~N,~N,~N");
c$ = Clazz.p0p ();
Clazz.defineStatics (c$,
"MAX_MEM_LEVEL", 9,
"Z_DEFAULT_COMPRESSION", -1,
"MAX_WBITS", 15,
"DEF_MEM_LEVEL", 8,
"STORED", 0,
"FAST", 1,
"SLOW", 2,
"config_table", null);
{
($t$ = JZ.Deflate.config_table =  new Array (10), JZ.Deflate.prototype.config_table = JZ.Deflate.config_table, $t$);
JZ.Deflate.config_table[0] =  new JZ.Deflate.Config (0, 0, 0, 0, 0);
JZ.Deflate.config_table[1] =  new JZ.Deflate.Config (4, 4, 8, 4, 1);
JZ.Deflate.config_table[2] =  new JZ.Deflate.Config (4, 5, 16, 8, 1);
JZ.Deflate.config_table[3] =  new JZ.Deflate.Config (4, 6, 32, 32, 1);
JZ.Deflate.config_table[4] =  new JZ.Deflate.Config (4, 4, 16, 16, 2);
JZ.Deflate.config_table[5] =  new JZ.Deflate.Config (8, 16, 32, 32, 2);
JZ.Deflate.config_table[6] =  new JZ.Deflate.Config (8, 16, 128, 128, 2);
JZ.Deflate.config_table[7] =  new JZ.Deflate.Config (8, 32, 128, 256, 2);
JZ.Deflate.config_table[8] =  new JZ.Deflate.Config (32, 128, 258, 1024, 2);
JZ.Deflate.config_table[9] =  new JZ.Deflate.Config (32, 258, 258, 4096, 2);
}Clazz.defineStatics (c$,
"z_errmsg", ["need dictionary", "stream end", "", "file error", "stream error", "data error", "insufficient memory", "buffer error", "incompatible version", ""],
"NeedMore", 0,
"BlockDone", 1,
"FinishStarted", 2,
"FinishDone", 3,
"PRESET_DICT", 0x20,
"Z_FILTERED", 1,
"Z_HUFFMAN_ONLY", 2,
"Z_DEFAULT_STRATEGY", 0,
"Z_NO_FLUSH", 0,
"Z_PARTIAL_FLUSH", 1,
"Z_FULL_FLUSH", 3,
"Z_FINISH", 4,
"Z_OK", 0,
"Z_STREAM_END", 1,
"Z_NEED_DICT", 2,
"Z_STREAM_ERROR", -2,
"Z_DATA_ERROR", -3,
"Z_BUF_ERROR", -5,
"INIT_STATE", 42,
"BUSY_STATE", 113,
"FINISH_STATE", 666,
"Z_DEFLATED", 8,
"STORED_BLOCK", 0,
"STATIC_TREES", 1,
"DYN_TREES", 2,
"Z_BINARY", 0,
"Z_ASCII", 1,
"Z_UNKNOWN", 2,
"Buf_size", 16,
"REP_3_6", 16,
"REPZ_3_10", 17,
"REPZ_11_138", 18,
"MIN_MATCH", 3,
"MAX_MATCH", 258,
"MIN_LOOKAHEAD", (262),
"MAX_BITS", 15,
"D_CODES", 30,
"BL_CODES", 19,
"LENGTH_CODES", 29,
"LITERALS", 256,
"L_CODES", (286),
"HEAP_SIZE", (573),
"END_BLOCK", 256);
});
Clazz.declarePackage ("JZ");
Clazz.load (["JZ.ZStream"], "JZ.Deflater", ["JZ.Deflate"], function () {
c$ = Clazz.decorateAsClass (function () {
this.$finished = false;
Clazz.instantialize (this, arguments);
}, JZ, "Deflater", JZ.ZStream);
$_M(c$, "init", 
function (level, bits, nowrap) {
if (bits == 0) bits = 15;
this.$finished = false;
this.setAdler32 ();
this.dstate =  new JZ.Deflate (this);
this.dstate.deflateInit2 (level, nowrap ? -bits : bits);
return this;
}, "~N,~N,~B");
Clazz.overrideMethod (c$, "deflate", 
function (flush) {
if (this.dstate == null) {
return -2;
}var ret = this.dstate.deflate (flush);
if (ret == 1) this.$finished = true;
return ret;
}, "~N");
Clazz.overrideMethod (c$, "end", 
function () {
this.$finished = true;
if (this.dstate == null) return -2;
var ret = this.dstate.deflateEnd ();
this.dstate = null;
this.free ();
return ret;
});
$_M(c$, "params", 
function (level, strategy) {
if (this.dstate == null) return -2;
return this.dstate.deflateParams (level, strategy);
}, "~N,~N");
$_M(c$, "setDictionary", 
function (dictionary, dictLength) {
if (this.dstate == null) return -2;
return this.dstate.deflateSetDictionary (dictionary, dictLength);
}, "~A,~N");
Clazz.overrideMethod (c$, "finished", 
function () {
return this.$finished;
});
$_M(c$, "finish", 
function () {
});
$_M(c$, "getBytesRead", 
function () {
return this.dstate.getBytesRead ();
});
$_M(c$, "getBytesWritten", 
function () {
return this.dstate.getBytesWritten ();
});
Clazz.defineStatics (c$,
"MAX_WBITS", 15,
"Z_STREAM_END", 1,
"$Z_STREAM_ERROR", -2);
});
Clazz.declarePackage ("JZ");
Clazz.load (null, "JZ.GZIPHeader", ["JZ.ZStream", "java.lang.IllegalArgumentException", "$.InternalError"], function () {
c$ = Clazz.decorateAsClass (function () {
this.text = false;
this.fhcrc = false;
this.time = 0;
this.xflags = 0;
this.os = 255;
this.extra = null;
this.name = null;
this.comment = null;
this.hcrc = 0;
this.crc = 0;
this.done = false;
this.mtime = 0;
Clazz.instantialize (this, arguments);
}, JZ, "GZIPHeader", null, Cloneable);
$_M(c$, "setModifiedTime", 
function (mtime) {
this.mtime = mtime;
}, "~N");
$_M(c$, "getModifiedTime", 
function () {
return this.mtime;
});
$_M(c$, "setOS", 
function (os) {
if ((0 <= os && os <= 13) || os == 255) this.os = os;
 else throw  new IllegalArgumentException ("os: " + os);
}, "~N");
$_M(c$, "getOS", 
function () {
return this.os;
});
$_M(c$, "setName", 
function (name) {
this.name = JZ.ZStream.getBytes (name);
}, "~S");
$_M(c$, "getName", 
function () {
if (this.name == null) return "";
try {
return  String.instantialize (this.name, "ISO-8859-1");
} catch (e) {
if (Clazz.exceptionOf (e, java.io.UnsupportedEncodingException)) {
throw  new InternalError (e.toString ());
} else {
throw e;
}
}
});
$_M(c$, "setComment", 
function (comment) {
this.comment = JZ.ZStream.getBytes (comment);
}, "~S");
$_M(c$, "getComment", 
function () {
if (this.comment == null) return "";
try {
return  String.instantialize (this.comment, "ISO-8859-1");
} catch (e) {
if (Clazz.exceptionOf (e, java.io.UnsupportedEncodingException)) {
throw  new InternalError (e.toString ());
} else {
throw e;
}
}
});
$_M(c$, "setCRC", 
function (crc) {
this.crc = crc;
}, "~N");
$_M(c$, "getCRC", 
function () {
return this.crc;
});
$_M(c$, "put", 
function (d) {
var flag = 0;
if (this.text) {
flag |= 1;
}if (this.fhcrc) {
flag |= 2;
}if (this.extra != null) {
flag |= 4;
}if (this.name != null) {
flag |= 8;
}if (this.comment != null) {
flag |= 16;
}var xfl = 0;
if (d.level == 1) {
xfl |= 4;
} else if (d.level == 9) {
xfl |= 2;
}d.put_short (0x8b1f);
d.put_byteB (8);
d.put_byteB (flag);
d.put_byteB (this.mtime);
d.put_byteB ((this.mtime >> 8));
d.put_byteB ((this.mtime >> 16));
d.put_byteB ((this.mtime >> 24));
d.put_byteB (xfl);
d.put_byteB (this.os);
if (this.extra != null) {
d.put_byteB (this.extra.length);
d.put_byteB ((this.extra.length >> 8));
d.put_byte (this.extra, 0, this.extra.length);
}if (this.name != null) {
d.put_byte (this.name, 0, this.name.length);
d.put_byteB (0);
}if (this.comment != null) {
d.put_byte (this.comment, 0, this.comment.length);
d.put_byteB (0);
}}, "JZ.Deflate");
$_M(c$, "clone", 
function () {
var gheader = Clazz.superCall (this, JZ.GZIPHeader, "clone", []);
var tmp;
if (gheader.extra != null) {
tmp =  Clazz.newByteArray (gheader.extra.length, 0);
System.arraycopy (gheader.extra, 0, tmp, 0, tmp.length);
gheader.extra = tmp;
}if (gheader.name != null) {
tmp =  Clazz.newByteArray (gheader.name.length, 0);
System.arraycopy (gheader.name, 0, tmp, 0, tmp.length);
gheader.name = tmp;
}if (gheader.comment != null) {
tmp =  Clazz.newByteArray (gheader.comment.length, 0);
System.arraycopy (gheader.comment, 0, tmp, 0, tmp.length);
gheader.comment = tmp;
}return gheader;
});
Clazz.defineStatics (c$,
"OS_MSDOS", 0x00,
"OS_AMIGA", 0x01,
"OS_VMS", 0x02,
"OS_UNIX", 0x03,
"OS_ATARI", 0x05,
"OS_OS2", 0x06,
"OS_MACOS", 0x07,
"OS_TOPS20", 0x0a,
"OS_WIN32", 0x0b,
"OS_VMCMS", 0x04,
"OS_ZSYSTEM", 0x08,
"OS_CPM", 0x09,
"OS_QDOS", 0x0c,
"OS_RISCOS", 0x0d,
"OS_UNKNOWN", 0xff);
});
Clazz.declarePackage ("JZ");
Clazz.load (["java.lang.Exception"], "JZ.Inflate", ["JZ.Adler32", "$.CRC32", "$.GZIPHeader", "$.InfBlocks", "java.io.ByteArrayOutputStream"], function () {
c$ = Clazz.decorateAsClass (function () {
this.mode = 0;
this.method = 0;
this.was = -1;
this.need = 0;
this.marker = 0;
this.wrap = 0;
this.wbits = 0;
this.blocks = null;
this.z = null;
this.flags = 0;
this.need_bytes = -1;
this.crcbuf = null;
this.gheader = null;
if (!Clazz.isClassDefined ("JZ.Inflate.Return")) {
JZ.Inflate.$Inflate$Return$ ();
}
this.tmp_string = null;
Clazz.instantialize (this, arguments);
}, JZ, "Inflate");
Clazz.prepareFields (c$, function () {
this.crcbuf =  Clazz.newByteArray (4, 0);
});
$_M(c$, "reset", 
function () {
this.inflateReset ();
});
$_M(c$, "inflateReset", 
function () {
if (this.z == null) return -2;
this.z.total_in = this.z.total_out = 0;
this.z.msg = null;
this.mode = 14;
this.need_bytes = -1;
this.blocks.reset ();
return 0;
});
$_M(c$, "inflateEnd", 
function () {
if (this.blocks != null) {
this.blocks.free ();
}return 0;
});
Clazz.makeConstructor (c$, 
function (z) {
this.z = z;
}, "JZ.ZStream");
$_M(c$, "inflateInit", 
function (w) {
this.z.msg = null;
this.blocks = null;
this.wrap = 0;
if (w < 0) {
w = -w;
} else {
this.wrap = (w >> 4) + 1;
if (w < 48) w &= 15;
}if (w < 8 || w > 15) {
this.inflateEnd ();
return -2;
}if (this.blocks != null && this.wbits != w) {
this.blocks.free ();
this.blocks = null;
}this.wbits = w;
this.blocks =  new JZ.InfBlocks (this.z, 1 << w);
this.inflateReset ();
return 0;
}, "~N");
$_M(c$, "inflate", 
function (f) {
var r;
var b;
if (this.z == null || this.z.next_in == null) {
if (f == 4 && this.mode == 14) return 0;
return -2;
}f = f == 4 ? -5 : 0;
r = -5;
while (true) {
switch (this.mode) {
case 14:
if (this.wrap == 0) {
this.mode = 7;
break;
}try {
r = this.readBytes (2, r, f);
} catch (e) {
if (Clazz.exceptionOf (e, JZ.Inflate.Return)) {
return e.r;
} else {
throw e;
}
}
if ((this.wrap & 2) != 0 && this.need == 0x8b1f) {
this.z.checksum =  new JZ.CRC32 ();
this.checksum (2, this.need);
if (this.gheader == null) this.gheader =  new JZ.GZIPHeader ();
this.mode = 23;
break;
}this.flags = 0;
this.method = (this.need) & 0xff;
b = ((this.need >> 8)) & 0xff;
if ((this.wrap & 1) == 0 || (((this.method << 8) + b) % 31) != 0) {
this.mode = 13;
this.z.msg = "incorrect header check";
break;
}if ((this.method & 0xf) != 8) {
this.mode = 13;
this.z.msg = "unknown compression method";
break;
}if ((this.method >> 4) + 8 > this.wbits) {
this.mode = 13;
this.z.msg = "invalid window size";
break;
}this.z.checksum =  new JZ.Adler32 ();
if ((b & 32) == 0) {
this.mode = 7;
break;
}this.mode = 2;
case 2:
if (this.z.avail_in == 0) return r;
r = f;
this.z.avail_in--;
this.z.total_in++;
this.need = ((this.z.next_in[this.z.next_in_index++] & 0xff) << 24) & 0xff000000;
this.mode = 3;
case 3:
if (this.z.avail_in == 0) return r;
r = f;
this.z.avail_in--;
this.z.total_in++;
this.need += ((this.z.next_in[this.z.next_in_index++] & 0xff) << 16) & 0xff0000;
this.mode = 4;
case 4:
if (this.z.avail_in == 0) return r;
r = f;
this.z.avail_in--;
this.z.total_in++;
this.need += ((this.z.next_in[this.z.next_in_index++] & 0xff) << 8) & 0xff00;
this.mode = 5;
case 5:
if (this.z.avail_in == 0) return r;
r = f;
this.z.avail_in--;
this.z.total_in++;
this.need += (this.z.next_in[this.z.next_in_index++] & 0xff);
this.z.checksum.resetLong (this.need);
this.mode = 6;
return 2;
case 6:
this.mode = 13;
this.z.msg = "need dictionary";
this.marker = 0;
return -2;
case 7:
r = this.blocks.proc (r);
if (r == -3) {
this.mode = 13;
this.marker = 0;
break;
}if (r == 0) {
r = f;
}if (r != 1) {
return r;
}r = f;
this.was = this.z.checksum.getValue ();
this.blocks.reset ();
if (this.wrap == 0) {
this.mode = 12;
break;
}this.mode = 8;
case 8:
if (this.z.avail_in == 0) return r;
r = f;
this.z.avail_in--;
this.z.total_in++;
this.need = ((this.z.next_in[this.z.next_in_index++] & 0xff) << 24) & 0xff000000;
this.mode = 9;
case 9:
if (this.z.avail_in == 0) return r;
r = f;
this.z.avail_in--;
this.z.total_in++;
this.need += ((this.z.next_in[this.z.next_in_index++] & 0xff) << 16) & 0xff0000;
this.mode = 10;
case 10:
if (this.z.avail_in == 0) return r;
r = f;
this.z.avail_in--;
this.z.total_in++;
this.need += ((this.z.next_in[this.z.next_in_index++] & 0xff) << 8) & 0xff00;
this.mode = 11;
case 11:
if (this.z.avail_in == 0) return r;
r = f;
this.z.avail_in--;
this.z.total_in++;
this.need += (this.z.next_in[this.z.next_in_index++] & 0xff);
if (this.flags != 0) {
this.need = ((this.need & 0xff000000) >> 24 | (this.need & 0x00ff0000) >> 8 | (this.need & 0x0000ff00) << 8 | (this.need & 0x0000ffff) << 24) & 0xffffffff;
}if (((this.was)) != ((this.need))) {
this.z.msg = "incorrect data check";
} else if (this.flags != 0 && this.gheader != null) {
this.gheader.crc = this.need;
}this.mode = 15;
case 15:
if (this.wrap != 0 && this.flags != 0) {
try {
r = this.readBytes (4, r, f);
} catch (e) {
if (Clazz.exceptionOf (e, JZ.Inflate.Return)) {
return e.r;
} else {
throw e;
}
}
if (this.z.msg != null && this.z.msg.equals ("incorrect data check")) {
this.mode = 13;
this.marker = 5;
break;
}if (this.need != (this.z.total_out & 0xffffffff)) {
this.z.msg = "incorrect length check";
this.mode = 13;
break;
}this.z.msg = null;
} else {
if (this.z.msg != null && this.z.msg.equals ("incorrect data check")) {
this.mode = 13;
this.marker = 5;
break;
}}this.mode = 12;
case 12:
return 1;
case 13:
return -3;
case 23:
try {
r = this.readBytes (2, r, f);
} catch (e) {
if (Clazz.exceptionOf (e, JZ.Inflate.Return)) {
return e.r;
} else {
throw e;
}
}
this.flags = (this.need) & 0xffff;
if ((this.flags & 0xff) != 8) {
this.z.msg = "unknown compression method";
this.mode = 13;
break;
}if ((this.flags & 0xe000) != 0) {
this.z.msg = "unknown header flags set";
this.mode = 13;
break;
}if ((this.flags & 0x0200) != 0) {
this.checksum (2, this.need);
}this.mode = 16;
case 16:
try {
r = this.readBytes (4, r, f);
} catch (e) {
if (Clazz.exceptionOf (e, JZ.Inflate.Return)) {
return e.r;
} else {
throw e;
}
}
if (this.gheader != null) this.gheader.time = this.need;
if ((this.flags & 0x0200) != 0) {
this.checksum (4, this.need);
}this.mode = 17;
case 17:
try {
r = this.readBytes (2, r, f);
} catch (e) {
if (Clazz.exceptionOf (e, JZ.Inflate.Return)) {
return e.r;
} else {
throw e;
}
}
if (this.gheader != null) {
this.gheader.xflags = (this.need) & 0xff;
this.gheader.os = ((this.need) >> 8) & 0xff;
}if ((this.flags & 0x0200) != 0) {
this.checksum (2, this.need);
}this.mode = 18;
case 18:
if ((this.flags & 0x0400) != 0) {
try {
r = this.readBytes (2, r, f);
} catch (e) {
if (Clazz.exceptionOf (e, JZ.Inflate.Return)) {
return e.r;
} else {
throw e;
}
}
if (this.gheader != null) {
this.gheader.extra =  Clazz.newByteArray ((this.need) & 0xffff, 0);
}if ((this.flags & 0x0200) != 0) {
this.checksum (2, this.need);
}} else if (this.gheader != null) {
this.gheader.extra = null;
}this.mode = 19;
case 19:
if ((this.flags & 0x0400) != 0) {
try {
r = this.readBytes (r, f);
if (this.gheader != null) {
var foo = this.tmp_string.toByteArray ();
this.tmp_string = null;
if (foo.length == this.gheader.extra.length) {
System.arraycopy (foo, 0, this.gheader.extra, 0, foo.length);
} else {
this.z.msg = "bad extra field length";
this.mode = 13;
break;
}}} catch (e) {
if (Clazz.exceptionOf (e, JZ.Inflate.Return)) {
return e.r;
} else {
throw e;
}
}
} else if (this.gheader != null) {
this.gheader.extra = null;
}this.mode = 20;
case 20:
if ((this.flags & 0x0800) != 0) {
try {
r = this.readString (r, f);
if (this.gheader != null) {
this.gheader.name = this.tmp_string.toByteArray ();
}this.tmp_string = null;
} catch (e) {
if (Clazz.exceptionOf (e, JZ.Inflate.Return)) {
return e.r;
} else {
throw e;
}
}
} else if (this.gheader != null) {
this.gheader.name = null;
}this.mode = 21;
case 21:
if ((this.flags & 0x1000) != 0) {
try {
r = this.readString (r, f);
if (this.gheader != null) {
this.gheader.comment = this.tmp_string.toByteArray ();
}this.tmp_string = null;
} catch (e) {
if (Clazz.exceptionOf (e, JZ.Inflate.Return)) {
return e.r;
} else {
throw e;
}
}
} else if (this.gheader != null) {
this.gheader.comment = null;
}this.mode = 22;
case 22:
if ((this.flags & 0x0200) != 0) {
try {
r = this.readBytes (2, r, f);
} catch (e) {
if (Clazz.exceptionOf (e, JZ.Inflate.Return)) {
return e.r;
} else {
throw e;
}
}
if (this.gheader != null) {
this.gheader.hcrc = (this.need & 0xffff);
}if (this.need != (this.z.checksum.getValue () & 0xffff)) {
this.mode = 13;
this.z.msg = "header crc mismatch";
this.marker = 5;
break;
}}this.z.checksum =  new JZ.CRC32 ();
this.mode = 7;
break;
default:
return -2;
}
}
}, "~N");
$_M(c$, "inflateSetDictionary", 
function (dictionary, dictLength) {
if (this.z == null || (this.mode != 6 && this.wrap != 0)) {
return -2;
}var index = 0;
var length = dictLength;
if (this.mode == 6) {
var adler_need = this.z.checksum.getValue ();
this.z.checksum.reset ();
this.z.checksum.update (dictionary, 0, dictLength);
if (this.z.checksum.getValue () != adler_need) {
return -3;
}}this.z.checksum.reset ();
if (length >= (1 << this.wbits)) {
length = (1 << this.wbits) - 1;
index = dictLength - length;
}this.blocks.set_dictionary (dictionary, index, length);
this.mode = 7;
return 0;
}, "~A,~N");
$_M(c$, "inflateSync", 
function () {
var n;
var p;
var m;
var r;
var w;
if (this.z == null) return -2;
if (this.mode != 13) {
this.mode = 13;
this.marker = 0;
}if ((n = this.z.avail_in) == 0) return -5;
p = this.z.next_in_index;
m = this.marker;
while (n != 0 && m < 4) {
if (this.z.next_in[p] == JZ.Inflate.mark[m]) {
m++;
} else if (this.z.next_in[p] != 0) {
m = 0;
} else {
m = 4 - m;
}p++;
n--;
}
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.z.avail_in = n;
this.marker = m;
if (m != 4) {
return -3;
}r = this.z.total_in;
w = this.z.total_out;
this.inflateReset ();
this.z.total_in = r;
this.z.total_out = w;
this.mode = 7;
return 0;
});
$_M(c$, "inflateSyncPoint", 
function () {
if (this.z == null || this.blocks == null) return -2;
return this.blocks.sync_point ();
});
$_M(c$, "readBytes", 
($fz = function (n, r, f) {
if (this.need_bytes == -1) {
this.need_bytes = n;
this.need = 0;
}while (this.need_bytes > 0) {
if (this.z.avail_in == 0) {
throw Clazz.innerTypeInstance (JZ.Inflate.Return, this, null, r);
}r = f;
this.z.avail_in--;
this.z.total_in++;
this.need = this.need | ((this.z.next_in[this.z.next_in_index++] & 0xff) << ((n - this.need_bytes) * 8));
this.need_bytes--;
}
if (n == 2) {
this.need &= 0xffff;
} else if (n == 4) {
this.need &= 0xffffffff;
}this.need_bytes = -1;
return r;
}, $fz.isPrivate = true, $fz), "~N,~N,~N");
$_M(c$, "readString", 
($fz = function (r, f) {
if (this.tmp_string == null) {
this.tmp_string =  new java.io.ByteArrayOutputStream ();
}var b = 0;
do {
if (this.z.avail_in == 0) {
throw Clazz.innerTypeInstance (JZ.Inflate.Return, this, null, r);
}r = f;
this.z.avail_in--;
this.z.total_in++;
b = this.z.next_in[this.z.next_in_index];
if (b != 0) this.tmp_string.write (this.z.next_in, this.z.next_in_index, 1);
this.z.checksum.update (this.z.next_in, this.z.next_in_index, 1);
this.z.next_in_index++;
} while (b != 0);
return r;
}, $fz.isPrivate = true, $fz), "~N,~N");
$_M(c$, "readBytes", 
($fz = function (r, f) {
if (this.tmp_string == null) {
this.tmp_string =  new java.io.ByteArrayOutputStream ();
}while (this.need > 0) {
if (this.z.avail_in == 0) {
throw Clazz.innerTypeInstance (JZ.Inflate.Return, this, null, r);
}r = f;
this.z.avail_in--;
this.z.total_in++;
this.tmp_string.write (this.z.next_in, this.z.next_in_index, 1);
this.z.checksum.update (this.z.next_in, this.z.next_in_index, 1);
this.z.next_in_index++;
this.need--;
}
return r;
}, $fz.isPrivate = true, $fz), "~N,~N");
$_M(c$, "checksum", 
($fz = function (n, v) {
for (var i = 0; i < n; i++) {
this.crcbuf[i] = (v & 0xff);
v >>= 8;
}
this.z.checksum.update (this.crcbuf, 0, n);
}, $fz.isPrivate = true, $fz), "~N,~N");
$_M(c$, "getGZIPHeader", 
function () {
return this.gheader;
});
$_M(c$, "inParsingHeader", 
function () {
switch (this.mode) {
case 14:
case 2:
case 3:
case 4:
case 5:
case 23:
case 16:
case 17:
case 18:
case 19:
case 20:
case 21:
case 22:
return true;
default:
return false;
}
});
c$.$Inflate$Return$ = function () {
Clazz.pu$h ();
c$ = Clazz.decorateAsClass (function () {
Clazz.prepareCallback (this, arguments);
this.r = 0;
Clazz.instantialize (this, arguments);
}, JZ.Inflate, "Return", Exception);
Clazz.makeConstructor (c$, 
function (a) {
Clazz.superConstructor (this, JZ.Inflate.Return, []);
this.r = a;
}, "~N");
c$ = Clazz.p0p ();
};
Clazz.defineStatics (c$,
"PRESET_DICT", 0x20,
"Z_NO_FLUSH", 0,
"Z_PARTIAL_FLUSH", 1,
"Z_SYNC_FLUSH", 2,
"Z_FULL_FLUSH", 3,
"Z_FINISH", 4,
"Z_DEFLATED", 8,
"Z_OK", 0,
"Z_STREAM_END", 1,
"Z_NEED_DICT", 2,
"Z_STREAM_ERROR", -2,
"Z_DATA_ERROR", -3,
"Z_BUF_ERROR", -5,
"DICT4", 2,
"DICT3", 3,
"DICT2", 4,
"DICT1", 5,
"DICT0", 6,
"BLOCKS", 7,
"CHECK4", 8,
"CHECK3", 9,
"CHECK2", 10,
"CHECK1", 11,
"DONE", 12,
"BAD", 13,
"HEAD", 14,
"LENGTH", 15,
"TIME", 16,
"OS", 17,
"EXLEN", 18,
"EXTRA", 19,
"NAME", 20,
"COMMENT", 21,
"HCRC", 22,
"FLAGS", 23,
"mark", [0, 0, 0xff, 0xff]);
});
Clazz.declarePackage ("JZ");
c$ = Clazz.decorateAsClass (function () {
this.hn = null;
this.v = null;
this.c = null;
this.r = null;
this.u = null;
this.x = null;
Clazz.instantialize (this, arguments);
}, JZ, "InfTree");
$_M(c$, "huft_build", 
($fz = function (b, bindex, n, s, d, e, t, m, hp, hn, v) {
var a;
var f;
var g;
var h;
var i;
var j;
var k;
var l;
var mask;
var p;
var q;
var w;
var xp;
var y;
var z;
p = 0;
i = n;
do {
this.c[b[bindex + p]]++;
p++;
i--;
} while (i != 0);
if (this.c[0] == n) {
t[0] = -1;
m[0] = 0;
return 0;
}l = m[0];
for (j = 1; j <= 15; j++) if (this.c[j] != 0) break;

k = j;
if (l < j) {
l = j;
}for (i = 15; i != 0; i--) {
if (this.c[i] != 0) break;
}
g = i;
if (l > i) {
l = i;
}m[0] = l;
for (y = 1 << j; j < i; j++, y <<= 1) {
if ((y -= this.c[j]) < 0) {
return -3;
}}
if ((y -= this.c[i]) < 0) {
return -3;
}this.c[i] += y;
this.x[1] = j = 0;
p = 1;
xp = 2;
while (--i != 0) {
this.x[xp] = (j += this.c[p]);
xp++;
p++;
}
i = 0;
p = 0;
do {
if ((j = b[bindex + p]) != 0) {
v[this.x[j]++] = i;
}p++;
} while (++i < n);
n = this.x[g];
this.x[0] = i = 0;
p = 0;
h = -1;
w = -l;
this.u[0] = 0;
q = 0;
z = 0;
for (; k <= g; k++) {
a = this.c[k];
while (a-- != 0) {
while (k > w + l) {
h++;
w += l;
z = g - w;
z = (z > l) ? l : z;
if ((f = 1 << (j = k - w)) > a + 1) {
f -= a + 1;
xp = k;
if (j < z) {
while (++j < z) {
if ((f <<= 1) <= this.c[++xp]) break;
f -= this.c[xp];
}
}}z = 1 << j;
if (hn[0] + z > 1440) {
return -3;
}this.u[h] = q = hn[0];
hn[0] += z;
if (h != 0) {
this.x[h] = i;
this.r[0] = j;
this.r[1] = l;
j = i >>> (w - l);
this.r[2] = (q - this.u[h - 1] - j);
System.arraycopy (this.r, 0, hp, (this.u[h - 1] + j) * 3, 3);
} else {
t[0] = q;
}}
this.r[1] = (k - w);
if (p >= n) {
this.r[0] = 192;
} else if (v[p] < s) {
this.r[0] = (v[p] < 256 ? 0 : 96);
this.r[2] = v[p++];
} else {
this.r[0] = (e[v[p] - s] + 16 + 64);
this.r[2] = d[v[p++] - s];
}f = 1 << (k - w);
for (j = i >>> w; j < z; j += f) {
System.arraycopy (this.r, 0, hp, (q + j) * 3, 3);
}
for (j = 1 << (k - 1); (i & j) != 0; j >>>= 1) {
i ^= j;
}
i ^= j;
mask = (1 << w) - 1;
while ((i & mask) != this.x[h]) {
h--;
w -= l;
mask = (1 << w) - 1;
}
}
}
return y != 0 && g != 1 ? -5 : 0;
}, $fz.isPrivate = true, $fz), "~A,~N,~N,~N,~A,~A,~A,~A,~A,~A,~A");
$_M(c$, "inflate_trees_bits", 
function (c, bb, tb, hp, z) {
var result;
this.initWorkArea (19);
this.hn[0] = 0;
result = this.huft_build (c, 0, 19, 19, null, null, tb, bb, hp, this.hn, this.v);
if (result == -3) {
z.msg = "oversubscribed dynamic bit lengths tree";
} else if (result == -5 || bb[0] == 0) {
z.msg = "incomplete dynamic bit lengths tree";
result = -3;
}return result;
}, "~A,~A,~A,~A,JZ.ZStream");
$_M(c$, "inflate_trees_dynamic", 
function (nl, nd, c, bl, bd, tl, td, hp, z) {
var result;
this.initWorkArea (288);
this.hn[0] = 0;
result = this.huft_build (c, 0, nl, 257, JZ.InfTree.cplens, JZ.InfTree.cplext, tl, bl, hp, this.hn, this.v);
if (result != 0 || bl[0] == 0) {
if (result == -3) {
z.msg = "oversubscribed literal/length tree";
} else if (result != -4) {
z.msg = "incomplete literal/length tree";
result = -3;
}return result;
}this.initWorkArea (288);
result = this.huft_build (c, nl, nd, 0, JZ.InfTree.cpdist, JZ.InfTree.cpdext, td, bd, hp, this.hn, this.v);
if (result != 0 || (bd[0] == 0 && nl > 257)) {
if (result == -3) {
z.msg = "oversubscribed distance tree";
} else if (result == -5) {
z.msg = "incomplete distance tree";
result = -3;
} else if (result != -4) {
z.msg = "empty distance tree with lengths";
result = -3;
}return result;
}return 0;
}, "~N,~N,~A,~A,~A,~A,~A,~A,JZ.ZStream");
c$.inflate_trees_fixed = $_M(c$, "inflate_trees_fixed", 
function (bl, bd, tl, td, z) {
bl[0] = 9;
bd[0] = 5;
tl[0] = JZ.InfTree.fixed_tl;
td[0] = JZ.InfTree.fixed_td;
return 0;
}, "~A,~A,~A,~A,JZ.ZStream");
$_M(c$, "initWorkArea", 
($fz = function (vsize) {
if (this.hn == null) {
this.hn =  Clazz.newIntArray (1, 0);
this.v =  Clazz.newIntArray (vsize, 0);
this.c =  Clazz.newIntArray (16, 0);
this.r =  Clazz.newIntArray (3, 0);
this.u =  Clazz.newIntArray (15, 0);
this.x =  Clazz.newIntArray (16, 0);
}if (this.v.length < vsize) {
this.v =  Clazz.newIntArray (vsize, 0);
}for (var i = 0; i < vsize; i++) {
this.v[i] = 0;
}
for (var i = 0; i < 16; i++) {
this.c[i] = 0;
}
for (var i = 0; i < 3; i++) {
this.r[i] = 0;
}
System.arraycopy (this.c, 0, this.u, 0, 15);
System.arraycopy (this.c, 0, this.x, 0, 16);
}, $fz.isPrivate = true, $fz), "~N");
Clazz.defineStatics (c$,
"MANY", 1440,
"Z_OK", 0,
"Z_DATA_ERROR", -3,
"Z_MEM_ERROR", -4,
"Z_BUF_ERROR", -5,
"fixed_bl", 9,
"fixed_bd", 5,
"fixed_tl", [96, 7, 256, 0, 8, 80, 0, 8, 16, 84, 8, 115, 82, 7, 31, 0, 8, 112, 0, 8, 48, 0, 9, 192, 80, 7, 10, 0, 8, 96, 0, 8, 32, 0, 9, 160, 0, 8, 0, 0, 8, 128, 0, 8, 64, 0, 9, 224, 80, 7, 6, 0, 8, 88, 0, 8, 24, 0, 9, 144, 83, 7, 59, 0, 8, 120, 0, 8, 56, 0, 9, 208, 81, 7, 17, 0, 8, 104, 0, 8, 40, 0, 9, 176, 0, 8, 8, 0, 8, 136, 0, 8, 72, 0, 9, 240, 80, 7, 4, 0, 8, 84, 0, 8, 20, 85, 8, 227, 83, 7, 43, 0, 8, 116, 0, 8, 52, 0, 9, 200, 81, 7, 13, 0, 8, 100, 0, 8, 36, 0, 9, 168, 0, 8, 4, 0, 8, 132, 0, 8, 68, 0, 9, 232, 80, 7, 8, 0, 8, 92, 0, 8, 28, 0, 9, 152, 84, 7, 83, 0, 8, 124, 0, 8, 60, 0, 9, 216, 82, 7, 23, 0, 8, 108, 0, 8, 44, 0, 9, 184, 0, 8, 12, 0, 8, 140, 0, 8, 76, 0, 9, 248, 80, 7, 3, 0, 8, 82, 0, 8, 18, 85, 8, 163, 83, 7, 35, 0, 8, 114, 0, 8, 50, 0, 9, 196, 81, 7, 11, 0, 8, 98, 0, 8, 34, 0, 9, 164, 0, 8, 2, 0, 8, 130, 0, 8, 66, 0, 9, 228, 80, 7, 7, 0, 8, 90, 0, 8, 26, 0, 9, 148, 84, 7, 67, 0, 8, 122, 0, 8, 58, 0, 9, 212, 82, 7, 19, 0, 8, 106, 0, 8, 42, 0, 9, 180, 0, 8, 10, 0, 8, 138, 0, 8, 74, 0, 9, 244, 80, 7, 5, 0, 8, 86, 0, 8, 22, 192, 8, 0, 83, 7, 51, 0, 8, 118, 0, 8, 54, 0, 9, 204, 81, 7, 15, 0, 8, 102, 0, 8, 38, 0, 9, 172, 0, 8, 6, 0, 8, 134, 0, 8, 70, 0, 9, 236, 80, 7, 9, 0, 8, 94, 0, 8, 30, 0, 9, 156, 84, 7, 99, 0, 8, 126, 0, 8, 62, 0, 9, 220, 82, 7, 27, 0, 8, 110, 0, 8, 46, 0, 9, 188, 0, 8, 14, 0, 8, 142, 0, 8, 78, 0, 9, 252, 96, 7, 256, 0, 8, 81, 0, 8, 17, 85, 8, 131, 82, 7, 31, 0, 8, 113, 0, 8, 49, 0, 9, 194, 80, 7, 10, 0, 8, 97, 0, 8, 33, 0, 9, 162, 0, 8, 1, 0, 8, 129, 0, 8, 65, 0, 9, 226, 80, 7, 6, 0, 8, 89, 0, 8, 25, 0, 9, 146, 83, 7, 59, 0, 8, 121, 0, 8, 57, 0, 9, 210, 81, 7, 17, 0, 8, 105, 0, 8, 41, 0, 9, 178, 0, 8, 9, 0, 8, 137, 0, 8, 73, 0, 9, 242, 80, 7, 4, 0, 8, 85, 0, 8, 21, 80, 8, 258, 83, 7, 43, 0, 8, 117, 0, 8, 53, 0, 9, 202, 81, 7, 13, 0, 8, 101, 0, 8, 37, 0, 9, 170, 0, 8, 5, 0, 8, 133, 0, 8, 69, 0, 9, 234, 80, 7, 8, 0, 8, 93, 0, 8, 29, 0, 9, 154, 84, 7, 83, 0, 8, 125, 0, 8, 61, 0, 9, 218, 82, 7, 23, 0, 8, 109, 0, 8, 45, 0, 9, 186, 0, 8, 13, 0, 8, 141, 0, 8, 77, 0, 9, 250, 80, 7, 3, 0, 8, 83, 0, 8, 19, 85, 8, 195, 83, 7, 35, 0, 8, 115, 0, 8, 51, 0, 9, 198, 81, 7, 11, 0, 8, 99, 0, 8, 35, 0, 9, 166, 0, 8, 3, 0, 8, 131, 0, 8, 67, 0, 9, 230, 80, 7, 7, 0, 8, 91, 0, 8, 27, 0, 9, 150, 84, 7, 67, 0, 8, 123, 0, 8, 59, 0, 9, 214, 82, 7, 19, 0, 8, 107, 0, 8, 43, 0, 9, 182, 0, 8, 11, 0, 8, 139, 0, 8, 75, 0, 9, 246, 80, 7, 5, 0, 8, 87, 0, 8, 23, 192, 8, 0, 83, 7, 51, 0, 8, 119, 0, 8, 55, 0, 9, 206, 81, 7, 15, 0, 8, 103, 0, 8, 39, 0, 9, 174, 0, 8, 7, 0, 8, 135, 0, 8, 71, 0, 9, 238, 80, 7, 9, 0, 8, 95, 0, 8, 31, 0, 9, 158, 84, 7, 99, 0, 8, 127, 0, 8, 63, 0, 9, 222, 82, 7, 27, 0, 8, 111, 0, 8, 47, 0, 9, 190, 0, 8, 15, 0, 8, 143, 0, 8, 79, 0, 9, 254, 96, 7, 256, 0, 8, 80, 0, 8, 16, 84, 8, 115, 82, 7, 31, 0, 8, 112, 0, 8, 48, 0, 9, 193, 80, 7, 10, 0, 8, 96, 0, 8, 32, 0, 9, 161, 0, 8, 0, 0, 8, 128, 0, 8, 64, 0, 9, 225, 80, 7, 6, 0, 8, 88, 0, 8, 24, 0, 9, 145, 83, 7, 59, 0, 8, 120, 0, 8, 56, 0, 9, 209, 81, 7, 17, 0, 8, 104, 0, 8, 40, 0, 9, 177, 0, 8, 8, 0, 8, 136, 0, 8, 72, 0, 9, 241, 80, 7, 4, 0, 8, 84, 0, 8, 20, 85, 8, 227, 83, 7, 43, 0, 8, 116, 0, 8, 52, 0, 9, 201, 81, 7, 13, 0, 8, 100, 0, 8, 36, 0, 9, 169, 0, 8, 4, 0, 8, 132, 0, 8, 68, 0, 9, 233, 80, 7, 8, 0, 8, 92, 0, 8, 28, 0, 9, 153, 84, 7, 83, 0, 8, 124, 0, 8, 60, 0, 9, 217, 82, 7, 23, 0, 8, 108, 0, 8, 44, 0, 9, 185, 0, 8, 12, 0, 8, 140, 0, 8, 76, 0, 9, 249, 80, 7, 3, 0, 8, 82, 0, 8, 18, 85, 8, 163, 83, 7, 35, 0, 8, 114, 0, 8, 50, 0, 9, 197, 81, 7, 11, 0, 8, 98, 0, 8, 34, 0, 9, 165, 0, 8, 2, 0, 8, 130, 0, 8, 66, 0, 9, 229, 80, 7, 7, 0, 8, 90, 0, 8, 26, 0, 9, 149, 84, 7, 67, 0, 8, 122, 0, 8, 58, 0, 9, 213, 82, 7, 19, 0, 8, 106, 0, 8, 42, 0, 9, 181, 0, 8, 10, 0, 8, 138, 0, 8, 74, 0, 9, 245, 80, 7, 5, 0, 8, 86, 0, 8, 22, 192, 8, 0, 83, 7, 51, 0, 8, 118, 0, 8, 54, 0, 9, 205, 81, 7, 15, 0, 8, 102, 0, 8, 38, 0, 9, 173, 0, 8, 6, 0, 8, 134, 0, 8, 70, 0, 9, 237, 80, 7, 9, 0, 8, 94, 0, 8, 30, 0, 9, 157, 84, 7, 99, 0, 8, 126, 0, 8, 62, 0, 9, 221, 82, 7, 27, 0, 8, 110, 0, 8, 46, 0, 9, 189, 0, 8, 14, 0, 8, 142, 0, 8, 78, 0, 9, 253, 96, 7, 256, 0, 8, 81, 0, 8, 17, 85, 8, 131, 82, 7, 31, 0, 8, 113, 0, 8, 49, 0, 9, 195, 80, 7, 10, 0, 8, 97, 0, 8, 33, 0, 9, 163, 0, 8, 1, 0, 8, 129, 0, 8, 65, 0, 9, 227, 80, 7, 6, 0, 8, 89, 0, 8, 25, 0, 9, 147, 83, 7, 59, 0, 8, 121, 0, 8, 57, 0, 9, 211, 81, 7, 17, 0, 8, 105, 0, 8, 41, 0, 9, 179, 0, 8, 9, 0, 8, 137, 0, 8, 73, 0, 9, 243, 80, 7, 4, 0, 8, 85, 0, 8, 21, 80, 8, 258, 83, 7, 43, 0, 8, 117, 0, 8, 53, 0, 9, 203, 81, 7, 13, 0, 8, 101, 0, 8, 37, 0, 9, 171, 0, 8, 5, 0, 8, 133, 0, 8, 69, 0, 9, 235, 80, 7, 8, 0, 8, 93, 0, 8, 29, 0, 9, 155, 84, 7, 83, 0, 8, 125, 0, 8, 61, 0, 9, 219, 82, 7, 23, 0, 8, 109, 0, 8, 45, 0, 9, 187, 0, 8, 13, 0, 8, 141, 0, 8, 77, 0, 9, 251, 80, 7, 3, 0, 8, 83, 0, 8, 19, 85, 8, 195, 83, 7, 35, 0, 8, 115, 0, 8, 51, 0, 9, 199, 81, 7, 11, 0, 8, 99, 0, 8, 35, 0, 9, 167, 0, 8, 3, 0, 8, 131, 0, 8, 67, 0, 9, 231, 80, 7, 7, 0, 8, 91, 0, 8, 27, 0, 9, 151, 84, 7, 67, 0, 8, 123, 0, 8, 59, 0, 9, 215, 82, 7, 19, 0, 8, 107, 0, 8, 43, 0, 9, 183, 0, 8, 11, 0, 8, 139, 0, 8, 75, 0, 9, 247, 80, 7, 5, 0, 8, 87, 0, 8, 23, 192, 8, 0, 83, 7, 51, 0, 8, 119, 0, 8, 55, 0, 9, 207, 81, 7, 15, 0, 8, 103, 0, 8, 39, 0, 9, 175, 0, 8, 7, 0, 8, 135, 0, 8, 71, 0, 9, 239, 80, 7, 9, 0, 8, 95, 0, 8, 31, 0, 9, 159, 84, 7, 99, 0, 8, 127, 0, 8, 63, 0, 9, 223, 82, 7, 27, 0, 8, 111, 0, 8, 47, 0, 9, 191, 0, 8, 15, 0, 8, 143, 0, 8, 79, 0, 9, 255],
"fixed_td", [80, 5, 1, 87, 5, 257, 83, 5, 17, 91, 5, 4097, 81, 5, 5, 89, 5, 1025, 85, 5, 65, 93, 5, 16385, 80, 5, 3, 88, 5, 513, 84, 5, 33, 92, 5, 8193, 82, 5, 9, 90, 5, 2049, 86, 5, 129, 192, 5, 24577, 80, 5, 2, 87, 5, 385, 83, 5, 25, 91, 5, 6145, 81, 5, 7, 89, 5, 1537, 85, 5, 97, 93, 5, 24577, 80, 5, 4, 88, 5, 769, 84, 5, 49, 92, 5, 12289, 82, 5, 13, 90, 5, 3073, 86, 5, 193, 192, 5, 24577],
"cplens", [3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31, 35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258, 0, 0],
"cplext", [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0, 112, 112],
"cpdist", [1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193, 257, 385, 513, 769, 1025, 1537, 2049, 3073, 4097, 6145, 8193, 12289, 16385, 24577],
"cpdext", [0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13],
"BMAX", 15);
Clazz.declarePackage ("JZ");
Clazz.load (["JZ.InfTree"], "JZ.InfBlocks", ["JZ.InfCodes"], function () {
c$ = Clazz.decorateAsClass (function () {
this.mode = 0;
this.left = 0;
this.table = 0;
this.index = 0;
this.blens = null;
this.bb = null;
this.tb = null;
this.bl = null;
this.bd = null;
this.tl = null;
this.td = null;
this.tli = null;
this.tdi = null;
this.codes = null;
this.last = 0;
this.bitk = 0;
this.bitb = 0;
this.hufts = null;
this.window = null;
this.end = 0;
this.read = 0;
this.write = 0;
this.check = false;
this.inftree = null;
this.z = null;
Clazz.instantialize (this, arguments);
}, JZ, "InfBlocks");
Clazz.prepareFields (c$, function () {
this.bb =  Clazz.newIntArray (1, 0);
this.tb =  Clazz.newIntArray (1, 0);
this.bl =  Clazz.newIntArray (1, 0);
this.bd =  Clazz.newIntArray (1, 0);
this.tli =  Clazz.newIntArray (1, 0);
this.tdi =  Clazz.newIntArray (1, 0);
this.inftree =  new JZ.InfTree ();
});
Clazz.makeConstructor (c$, 
function (z, w) {
this.z = z;
this.codes =  new JZ.InfCodes (this.z, this);
this.hufts =  Clazz.newIntArray (4320, 0);
this.window =  Clazz.newByteArray (w, 0);
this.end = w;
this.check = (z.istate.wrap == 0) ? false : true;
this.mode = 0;
{
this.tl = Clazz.newArray(1, null);
this.td = Clazz.newArray(1, null);
}this.reset ();
}, "JZ.ZStream,~N");
$_M(c$, "reset", 
function () {
if (this.mode == 4 || this.mode == 5) {
}if (this.mode == 6) {
this.codes.free (this.z);
}this.mode = 0;
this.bitk = 0;
this.bitb = 0;
this.read = this.write = 0;
if (this.check) {
this.z.checksum.reset ();
}});
$_M(c$, "proc", 
function (r) {
var t;
var b;
var k;
var p;
var n;
var q;
var m;
{
p = this.z.next_in_index;
n = this.z.avail_in;
b = this.bitb;
k = this.bitk;
}{
q = this.write;
m = (q < this.read ? this.read - q - 1 : this.end - q);
}while (true) {
switch (this.mode) {
case 0:
while (k < (3)) {
if (n != 0) {
r = 0;
} else {
this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
return this.inflate_flush (r);
}n--;
b |= (this.z.next_in[p++] & 0xff) << k;
k += 8;
}
t = (b & 7);
this.last = t & 1;
switch (t >>> 1) {
case 0:
{
b >>>= (3);
k -= (3);
}t = k & 7;
{
b >>>= (t);
k -= (t);
}this.mode = 1;
break;
case 1:
JZ.InfTree.inflate_trees_fixed (this.bl, this.bd, this.tl, this.td, this.z);
this.codes.init (this.bl[0], this.bd[0], this.tl[0], 0, this.td[0], 0);
{
b >>>= (3);
k -= (3);
}this.mode = 6;
break;
case 2:
{
b >>>= (3);
k -= (3);
}this.mode = 3;
break;
case 3:
{
b >>>= (3);
k -= (3);
}this.mode = 9;
this.z.msg = "invalid block type";
r = -3;
this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
return this.inflate_flush (r);
}
break;
case 1:
while (k < (32)) {
if (n != 0) {
r = 0;
} else {
this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
return this.inflate_flush (r);
}n--;
b |= (this.z.next_in[p++] & 0xff) << k;
k += 8;
}
if ((((~b) >>> 16) & 0xffff) != (b & 0xffff)) {
this.mode = 9;
this.z.msg = "invalid stored block lengths";
r = -3;
this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
return this.inflate_flush (r);
}this.left = (b & 0xffff);
b = k = 0;
this.mode = this.left != 0 ? 2 : (this.last != 0 ? 7 : 0);
break;
case 2:
if (n == 0) {
this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
return this.inflate_flush (r);
}if (m == 0) {
if (q == this.end && this.read != 0) {
q = 0;
m = (q < this.read ? this.read - q - 1 : this.end - q);
}if (m == 0) {
this.write = q;
r = this.inflate_flush (r);
q = this.write;
m = (q < this.read ? this.read - q - 1 : this.end - q);
if (q == this.end && this.read != 0) {
q = 0;
m = (q < this.read ? this.read - q - 1 : this.end - q);
}if (m == 0) {
this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
return this.inflate_flush (r);
}}}r = 0;
t = this.left;
if (t > n) t = n;
if (t > m) t = m;
System.arraycopy (this.z.next_in, p, this.window, q, t);
p += t;
n -= t;
q += t;
m -= t;
if ((this.left -= t) != 0) break;
this.mode = this.last != 0 ? 7 : 0;
break;
case 3:
while (k < (14)) {
if (n != 0) {
r = 0;
} else {
this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
return this.inflate_flush (r);
}n--;
b |= (this.z.next_in[p++] & 0xff) << k;
k += 8;
}
this.table = t = (b & 0x3fff);
if ((t & 0x1f) > 29 || ((t >> 5) & 0x1f) > 29) {
this.mode = 9;
this.z.msg = "too many length or distance symbols";
r = -3;
this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
return this.inflate_flush (r);
}t = 258 + (t & 0x1f) + ((t >> 5) & 0x1f);
if (this.blens == null || this.blens.length < t) {
this.blens =  Clazz.newIntArray (t, 0);
} else {
for (var i = 0; i < t; i++) {
this.blens[i] = 0;
}
}{
b >>>= (14);
k -= (14);
}this.index = 0;
this.mode = 4;
case 4:
while (this.index < 4 + (this.table >>> 10)) {
while (k < (3)) {
if (n != 0) {
r = 0;
} else {
this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
return this.inflate_flush (r);
}n--;
b |= (this.z.next_in[p++] & 0xff) << k;
k += 8;
}
this.blens[JZ.InfBlocks.border[this.index++]] = b & 7;
{
b >>>= (3);
k -= (3);
}}
while (this.index < 19) {
this.blens[JZ.InfBlocks.border[this.index++]] = 0;
}
this.bb[0] = 7;
t = this.inftree.inflate_trees_bits (this.blens, this.bb, this.tb, this.hufts, this.z);
if (t != 0) {
r = t;
if (r == -3) {
this.blens = null;
this.mode = 9;
}this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
return this.inflate_flush (r);
}this.index = 0;
this.mode = 5;
case 5:
while (true) {
t = this.table;
if (!(this.index < 258 + (t & 0x1f) + ((t >> 5) & 0x1f))) {
break;
}var i;
var j;
var c;
t = this.bb[0];
while (k < (t)) {
if (n != 0) {
r = 0;
} else {
this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
return this.inflate_flush (r);
}n--;
b |= (this.z.next_in[p++] & 0xff) << k;
k += 8;
}
if (this.tb[0] == -1) {
}t = this.hufts[(this.tb[0] + (b & JZ.InfBlocks.inflate_mask[t])) * 3 + 1];
c = this.hufts[(this.tb[0] + (b & JZ.InfBlocks.inflate_mask[t])) * 3 + 2];
if (c < 16) {
b >>>= (t);
k -= (t);
this.blens[this.index++] = c;
} else {
i = c == 18 ? 7 : c - 14;
j = c == 18 ? 11 : 3;
while (k < (t + i)) {
if (n != 0) {
r = 0;
} else {
this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
return this.inflate_flush (r);
}n--;
b |= (this.z.next_in[p++] & 0xff) << k;
k += 8;
}
b >>>= (t);
k -= (t);
j += (b & JZ.InfBlocks.inflate_mask[i]);
b >>>= (i);
k -= (i);
i = this.index;
t = this.table;
if (i + j > 258 + (t & 0x1f) + ((t >> 5) & 0x1f) || (c == 16 && i < 1)) {
this.blens = null;
this.mode = 9;
this.z.msg = "invalid bit length repeat";
r = -3;
this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
return this.inflate_flush (r);
}c = c == 16 ? this.blens[i - 1] : 0;
do {
this.blens[i++] = c;
} while (--j != 0);
this.index = i;
}}
this.tb[0] = -1;
{
this.bl[0] = 9;
this.bd[0] = 6;
t = this.table;
t = this.inftree.inflate_trees_dynamic (257 + (t & 0x1f), 1 + ((t >> 5) & 0x1f), this.blens, this.bl, this.bd, this.tli, this.tdi, this.hufts, this.z);
if (t != 0) {
if (t == -3) {
this.blens = null;
this.mode = 9;
}r = t;
this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
return this.inflate_flush (r);
}this.codes.init (this.bl[0], this.bd[0], this.hufts, this.tli[0], this.hufts, this.tdi[0]);
}this.mode = 6;
case 6:
this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
if ((r = this.codes.proc (r)) != 1) {
return this.inflate_flush (r);
}r = 0;
this.codes.free (this.z);
p = this.z.next_in_index;
n = this.z.avail_in;
b = this.bitb;
k = this.bitk;
q = this.write;
m = (q < this.read ? this.read - q - 1 : this.end - q);
if (this.last == 0) {
this.mode = 0;
break;
}this.mode = 7;
case 7:
this.write = q;
r = this.inflate_flush (r);
q = this.write;
m = (q < this.read ? this.read - q - 1 : this.end - q);
if (this.read != this.write) {
this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
return this.inflate_flush (r);
}this.mode = 8;
case 8:
r = 1;
this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
return this.inflate_flush (r);
case 9:
r = -3;
this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
return this.inflate_flush (r);
default:
r = -2;
this.bitb = b;
this.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.write = q;
return this.inflate_flush (r);
}
}
}, "~N");
$_M(c$, "free", 
function () {
this.reset ();
this.window = null;
this.hufts = null;
});
$_M(c$, "set_dictionary", 
function (d, start, n) {
System.arraycopy (d, start, this.window, 0, n);
this.read = this.write = n;
}, "~A,~N,~N");
$_M(c$, "sync_point", 
function () {
return this.mode == 1 ? 1 : 0;
});
$_M(c$, "inflate_flush", 
function (r) {
var n;
var p;
var q;
p = this.z.next_out_index;
q = this.read;
n = ((q <= this.write ? this.write : this.end) - q);
if (n > this.z.avail_out) n = this.z.avail_out;
if (n != 0 && r == -5) r = 0;
this.z.avail_out -= n;
this.z.total_out += n;
if (this.check && n > 0) {
this.z.checksum.update (this.window, q, n);
}System.arraycopy (this.window, q, this.z.next_out, p, n);
p += n;
q += n;
if (q == this.end) {
q = 0;
if (this.write == this.end) this.write = 0;
n = this.write - q;
if (n > this.z.avail_out) n = this.z.avail_out;
if (n != 0 && r == -5) r = 0;
this.z.avail_out -= n;
this.z.total_out += n;
if (this.check && n > 0) {
this.z.checksum.update (this.window, q, n);
}System.arraycopy (this.window, q, this.z.next_out, p, n);
p += n;
q += n;
}this.z.next_out_index = p;
this.read = q;
return r;
}, "~N");
Clazz.defineStatics (c$,
"MANY", 1440,
"inflate_mask", [0x00000000, 0x00000001, 0x00000003, 0x00000007, 0x0000000f, 0x0000001f, 0x0000003f, 0x0000007f, 0x000000ff, 0x000001ff, 0x000003ff, 0x000007ff, 0x00000fff, 0x00001fff, 0x00003fff, 0x00007fff, 0x0000ffff],
"border", [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15],
"Z_OK", 0,
"Z_STREAM_END", 1,
"Z_STREAM_ERROR", -2,
"Z_DATA_ERROR", -3,
"Z_BUF_ERROR", -5,
"TYPE", 0,
"LENS", 1,
"STORED", 2,
"TABLE", 3,
"BTREE", 4,
"DTREE", 5,
"CODES", 6,
"DRY", 7,
"DONE", 8,
"BAD", 9);
});
Clazz.declarePackage ("JZ");
c$ = Clazz.decorateAsClass (function () {
this.mode = 0;
this.len = 0;
this.tree = null;
this.tree_index = 0;
this.need = 0;
this.lit = 0;
this.get = 0;
this.dist = 0;
this.lbits = 0;
this.dbits = 0;
this.ltree = null;
this.ltree_index = 0;
this.dtree = null;
this.dtree_index = 0;
this.z = null;
this.s = null;
Clazz.instantialize (this, arguments);
}, JZ, "InfCodes");
Clazz.makeConstructor (c$, 
function (z, s) {
this.z = z;
this.s = s;
}, "JZ.ZStream,JZ.InfBlocks");
$_M(c$, "init", 
function (bl, bd, tl, tl_index, td, td_index) {
this.mode = 0;
this.lbits = bl;
this.dbits = bd;
this.ltree = tl;
this.ltree_index = tl_index;
this.dtree = td;
this.dtree_index = td_index;
this.tree = null;
}, "~N,~N,~A,~N,~A,~N");
$_M(c$, "proc", 
function (r) {
var j;
var tindex;
var e;
var b = 0;
var k = 0;
var p = 0;
var n;
var q;
var m;
var f;
p = this.z.next_in_index;
n = this.z.avail_in;
b = this.s.bitb;
k = this.s.bitk;
q = this.s.write;
m = q < this.s.read ? this.s.read - q - 1 : this.s.end - q;
while (true) {
switch (this.mode) {
case 0:
if (m >= 258 && n >= 10) {
this.s.bitb = b;
this.s.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.s.write = q;
r = this.inflate_fast (this.lbits, this.dbits, this.ltree, this.ltree_index, this.dtree, this.dtree_index, this.s, this.z);
p = this.z.next_in_index;
n = this.z.avail_in;
b = this.s.bitb;
k = this.s.bitk;
q = this.s.write;
m = q < this.s.read ? this.s.read - q - 1 : this.s.end - q;
if (r != 0) {
this.mode = r == 1 ? 7 : 9;
break;
}}this.need = this.lbits;
this.tree = this.ltree;
this.tree_index = this.ltree_index;
this.mode = 1;
case 1:
j = this.need;
while (k < (j)) {
if (n != 0) r = 0;
 else {
this.s.bitb = b;
this.s.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.s.write = q;
return this.s.inflate_flush (r);
}n--;
b |= (this.z.next_in[p++] & 0xff) << k;
k += 8;
}
tindex = (this.tree_index + (b & JZ.InfCodes.inflate_mask[j])) * 3;
b >>>= (this.tree[tindex + 1]);
k -= (this.tree[tindex + 1]);
e = this.tree[tindex];
if (e == 0) {
this.lit = this.tree[tindex + 2];
this.mode = 6;
break;
}if ((e & 16) != 0) {
this.get = e & 15;
this.len = this.tree[tindex + 2];
this.mode = 2;
break;
}if ((e & 64) == 0) {
this.need = e;
this.tree_index = Clazz.doubleToInt (tindex / 3) + this.tree[tindex + 2];
break;
}if ((e & 32) != 0) {
this.mode = 7;
break;
}this.mode = 9;
this.z.msg = "invalid literal/length code";
r = -3;
this.s.bitb = b;
this.s.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.s.write = q;
return this.s.inflate_flush (r);
case 2:
j = this.get;
while (k < (j)) {
if (n != 0) r = 0;
 else {
this.s.bitb = b;
this.s.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.s.write = q;
return this.s.inflate_flush (r);
}n--;
b |= (this.z.next_in[p++] & 0xff) << k;
k += 8;
}
this.len += (b & JZ.InfCodes.inflate_mask[j]);
b >>= j;
k -= j;
this.need = this.dbits;
this.tree = this.dtree;
this.tree_index = this.dtree_index;
this.mode = 3;
case 3:
j = this.need;
while (k < (j)) {
if (n != 0) r = 0;
 else {
this.s.bitb = b;
this.s.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.s.write = q;
return this.s.inflate_flush (r);
}n--;
b |= (this.z.next_in[p++] & 0xff) << k;
k += 8;
}
tindex = (this.tree_index + (b & JZ.InfCodes.inflate_mask[j])) * 3;
b >>= this.tree[tindex + 1];
k -= this.tree[tindex + 1];
e = (this.tree[tindex]);
if ((e & 16) != 0) {
this.get = e & 15;
this.dist = this.tree[tindex + 2];
this.mode = 4;
break;
}if ((e & 64) == 0) {
this.need = e;
this.tree_index = Clazz.doubleToInt (tindex / 3) + this.tree[tindex + 2];
break;
}this.mode = 9;
this.z.msg = "invalid distance code";
r = -3;
this.s.bitb = b;
this.s.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.s.write = q;
return this.s.inflate_flush (r);
case 4:
j = this.get;
while (k < (j)) {
if (n != 0) r = 0;
 else {
this.s.bitb = b;
this.s.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.s.write = q;
return this.s.inflate_flush (r);
}n--;
b |= (this.z.next_in[p++] & 0xff) << k;
k += 8;
}
this.dist += (b & JZ.InfCodes.inflate_mask[j]);
b >>= j;
k -= j;
this.mode = 5;
case 5:
f = q - this.dist;
while (f < 0) {
f += this.s.end;
}
while (this.len != 0) {
if (m == 0) {
if (q == this.s.end && this.s.read != 0) {
q = 0;
m = q < this.s.read ? this.s.read - q - 1 : this.s.end - q;
}if (m == 0) {
this.s.write = q;
r = this.s.inflate_flush (r);
q = this.s.write;
m = q < this.s.read ? this.s.read - q - 1 : this.s.end - q;
if (q == this.s.end && this.s.read != 0) {
q = 0;
m = q < this.s.read ? this.s.read - q - 1 : this.s.end - q;
}if (m == 0) {
this.s.bitb = b;
this.s.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.s.write = q;
return this.s.inflate_flush (r);
}}}this.s.window[q++] = this.s.window[f++];
m--;
if (f == this.s.end) f = 0;
this.len--;
}
this.mode = 0;
break;
case 6:
if (m == 0) {
if (q == this.s.end && this.s.read != 0) {
q = 0;
m = q < this.s.read ? this.s.read - q - 1 : this.s.end - q;
}if (m == 0) {
this.s.write = q;
r = this.s.inflate_flush (r);
q = this.s.write;
m = q < this.s.read ? this.s.read - q - 1 : this.s.end - q;
if (q == this.s.end && this.s.read != 0) {
q = 0;
m = q < this.s.read ? this.s.read - q - 1 : this.s.end - q;
}if (m == 0) {
this.s.bitb = b;
this.s.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.s.write = q;
return this.s.inflate_flush (r);
}}}r = 0;
this.s.window[q++] = this.lit;
m--;
this.mode = 0;
break;
case 7:
if (k > 7) {
k -= 8;
n++;
p--;
}this.s.write = q;
r = this.s.inflate_flush (r);
q = this.s.write;
m = q < this.s.read ? this.s.read - q - 1 : this.s.end - q;
if (this.s.read != this.s.write) {
this.s.bitb = b;
this.s.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.s.write = q;
return this.s.inflate_flush (r);
}this.mode = 8;
case 8:
r = 1;
this.s.bitb = b;
this.s.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.s.write = q;
return this.s.inflate_flush (r);
case 9:
r = -3;
this.s.bitb = b;
this.s.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.s.write = q;
return this.s.inflate_flush (r);
default:
r = -2;
this.s.bitb = b;
this.s.bitk = k;
this.z.avail_in = n;
this.z.total_in += p - this.z.next_in_index;
this.z.next_in_index = p;
this.s.write = q;
return this.s.inflate_flush (r);
}
}
}, "~N");
$_M(c$, "free", 
function (z) {
}, "JZ.ZStream");
$_M(c$, "inflate_fast", 
function (bl, bd, tl, tl_index, td, td_index, s, z) {
var t;
var tp;
var tp_index;
var e;
var b;
var k;
var p;
var n;
var q;
var m;
var ml;
var md;
var c;
var d;
var r;
var tp_index_t_3;
p = z.next_in_index;
n = z.avail_in;
b = s.bitb;
k = s.bitk;
q = s.write;
m = q < s.read ? s.read - q - 1 : s.end - q;
ml = JZ.InfCodes.inflate_mask[bl];
md = JZ.InfCodes.inflate_mask[bd];
do {
while (k < (20)) {
n--;
b |= (z.next_in[p++] & 0xff) << k;
k += 8;
}
t = b & ml;
tp = tl;
tp_index = tl_index;
tp_index_t_3 = (tp_index + t) * 3;
if ((e = tp[tp_index_t_3]) == 0) {
b >>= (tp[tp_index_t_3 + 1]);
k -= (tp[tp_index_t_3 + 1]);
s.window[q++] = tp[tp_index_t_3 + 2];
m--;
continue;
}do {
b >>= (tp[tp_index_t_3 + 1]);
k -= (tp[tp_index_t_3 + 1]);
if ((e & 16) != 0) {
e &= 15;
c = tp[tp_index_t_3 + 2] + (b & JZ.InfCodes.inflate_mask[e]);
b >>= e;
k -= e;
while (k < (15)) {
n--;
b |= (z.next_in[p++] & 0xff) << k;
k += 8;
}
t = b & md;
tp = td;
tp_index = td_index;
tp_index_t_3 = (tp_index + t) * 3;
e = tp[tp_index_t_3];
do {
b >>= (tp[tp_index_t_3 + 1]);
k -= (tp[tp_index_t_3 + 1]);
if ((e & 16) != 0) {
e &= 15;
while (k < (e)) {
n--;
b |= (z.next_in[p++] & 0xff) << k;
k += 8;
}
d = tp[tp_index_t_3 + 2] + (b & JZ.InfCodes.inflate_mask[e]);
b >>= (e);
k -= (e);
m -= c;
if (q >= d) {
r = q - d;
if (q - r > 0 && 2 > (q - r)) {
s.window[q++] = s.window[r++];
s.window[q++] = s.window[r++];
c -= 2;
} else {
System.arraycopy (s.window, r, s.window, q, 2);
q += 2;
r += 2;
c -= 2;
}} else {
r = q - d;
do {
r += s.end;
} while (r < 0);
e = s.end - r;
if (c > e) {
c -= e;
if (q - r > 0 && e > (q - r)) {
do {
s.window[q++] = s.window[r++];
} while (--e != 0);
} else {
System.arraycopy (s.window, r, s.window, q, e);
q += e;
r += e;
e = 0;
}r = 0;
}}if (q - r > 0 && c > (q - r)) {
do {
s.window[q++] = s.window[r++];
} while (--c != 0);
} else {
System.arraycopy (s.window, r, s.window, q, c);
q += c;
r += c;
c = 0;
}break;
} else if ((e & 64) == 0) {
t += tp[tp_index_t_3 + 2];
t += (b & JZ.InfCodes.inflate_mask[e]);
tp_index_t_3 = (tp_index + t) * 3;
e = tp[tp_index_t_3];
} else {
z.msg = "invalid distance code";
c = z.avail_in - n;
c = (k >> 3) < c ? k >> 3 : c;
n += c;
p -= c;
k -= c << 3;
s.bitb = b;
s.bitk = k;
z.avail_in = n;
z.total_in += p - z.next_in_index;
z.next_in_index = p;
s.write = q;
return -3;
}} while (true);
break;
}if ((e & 64) == 0) {
t += tp[tp_index_t_3 + 2];
t += (b & JZ.InfCodes.inflate_mask[e]);
tp_index_t_3 = (tp_index + t) * 3;
if ((e = tp[tp_index_t_3]) == 0) {
b >>= (tp[tp_index_t_3 + 1]);
k -= (tp[tp_index_t_3 + 1]);
s.window[q++] = tp[tp_index_t_3 + 2];
m--;
break;
}} else if ((e & 32) != 0) {
c = z.avail_in - n;
c = (k >> 3) < c ? k >> 3 : c;
n += c;
p -= c;
k -= c << 3;
s.bitb = b;
s.bitk = k;
z.avail_in = n;
z.total_in += p - z.next_in_index;
z.next_in_index = p;
s.write = q;
return 1;
} else {
z.msg = "invalid literal/length code";
c = z.avail_in - n;
c = (k >> 3) < c ? k >> 3 : c;
n += c;
p -= c;
k -= c << 3;
s.bitb = b;
s.bitk = k;
z.avail_in = n;
z.total_in += p - z.next_in_index;
z.next_in_index = p;
s.write = q;
return -3;
}} while (true);
} while (m >= 258 && n >= 10);
c = z.avail_in - n;
c = (k >> 3) < c ? k >> 3 : c;
n += c;
p -= c;
k -= c << 3;
s.bitb = b;
s.bitk = k;
z.avail_in = n;
z.total_in += p - z.next_in_index;
z.next_in_index = p;
s.write = q;
return 0;
}, "~N,~N,~A,~N,~A,~N,JZ.InfBlocks,JZ.ZStream");
Clazz.defineStatics (c$,
"inflate_mask", [0x00000000, 0x00000001, 0x00000003, 0x00000007, 0x0000000f, 0x0000001f, 0x0000003f, 0x0000007f, 0x000000ff, 0x000001ff, 0x000003ff, 0x000007ff, 0x00000fff, 0x00001fff, 0x00003fff, 0x00007fff, 0x0000ffff],
"Z_OK", 0,
"Z_STREAM_END", 1,
"Z_STREAM_ERROR", -2,
"Z_DATA_ERROR", -3,
"START", 0,
"LEN", 1,
"LENEXT", 2,
"DIST", 3,
"DISTEXT", 4,
"COPY", 5,
"LIT", 6,
"WASH", 7,
"END", 8,
"BADCODE", 9);
Clazz.declarePackage ("java.util.zip");
Clazz.load (["java.io.FilterInputStream"], "java.util.zip.CheckedInputStream", null, function () {
c$ = Clazz.decorateAsClass (function () {
this.cksum = null;
Clazz.instantialize (this, arguments);
}, java.util.zip, "CheckedInputStream", java.io.FilterInputStream);
Clazz.makeConstructor (c$, 
function ($in, cksum) {
Clazz.superConstructor (this, java.util.zip.CheckedInputStream, [$in]);
this.cksum = cksum;
}, "java.io.InputStream,JZ.Checksum");
Clazz.overrideMethod (c$, "readByteAsInt", 
function () {
var b = this.$in.readByteAsInt ();
if (b != -1) {
this.cksum.updateByteAsInt (b);
}return b;
});
Clazz.overrideMethod (c$, "read", 
function (buf, off, len) {
len = this.$in.read (buf, off, len);
if (len != -1) {
this.cksum.update (buf, off, len);
}return len;
}, "~A,~N,~N");
Clazz.overrideMethod (c$, "skip", 
function (n) {
var buf =  Clazz.newByteArray (512, 0);
var total = 0;
while (total < n) {
var len = n - total;
len = this.read (buf, 0, len < buf.length ? len : buf.length);
if (len == -1) {
return total;
}total += len;
}
return total;
}, "~N");
$_M(c$, "getChecksum", 
function () {
return this.cksum;
});
});
Clazz.declarePackage ("java.util.zip");
Clazz.load (["JZ.Inflater"], "java.util.zip.Inflater", null, function () {
c$ = Clazz.declareType (java.util.zip, "Inflater", JZ.Inflater);
$_M(c$, "initialize", 
function (nowrap) {
return this.init (0, nowrap);
}, "~B");
});
Clazz.declarePackage ("java.util.zip");
Clazz.load (["java.io.IOException"], "java.util.zip.ZipException", null, function () {
c$ = Clazz.declareType (java.util.zip, "ZipException", java.io.IOException);
});
Clazz.declarePackage ("java.util.zip");
c$ = Clazz.declareInterface (java.util.zip, "ZipConstants");
Clazz.defineStatics (c$,
"LOCSIG", 0x04034b50,
"EXTSIG", 0x08074b50,
"CENSIG", 0x02014b50,
"ENDSIG", 0x06054b50,
"LOCHDR", 30,
"EXTHDR", 16,
"CENHDR", 46,
"ENDHDR", 22,
"LOCVER", 4,
"LOCFLG", 6,
"LOCHOW", 8,
"LOCTIM", 10,
"LOCCRC", 14,
"LOCSIZ", 18,
"LOCLEN", 22,
"LOCNAM", 26,
"LOCEXT", 28,
"EXTCRC", 4,
"EXTSIZ", 8,
"EXTLEN", 12,
"CENVEM", 4,
"CENVER", 6,
"CENFLG", 8,
"CENHOW", 10,
"CENTIM", 12,
"CENCRC", 16,
"CENSIZ", 20,
"CENLEN", 24,
"CENNAM", 28,
"CENEXT", 30,
"CENCOM", 32,
"CENDSK", 34,
"CENATT", 36,
"CENATX", 38,
"CENOFF", 42,
"ENDSUB", 8,
"ENDTOT", 10,
"ENDSIZ", 12,
"ENDOFF", 16,
"ENDCOM", 20);
Clazz.declarePackage ("java.util.zip");
Clazz.load (["java.util.zip.ZipConstants"], "java.util.zip.ZipEntry", ["java.lang.IllegalArgumentException", "$.InternalError", "$.NullPointerException", "java.util.Date"], function () {
c$ = Clazz.decorateAsClass (function () {
this.offset = 0;
this.name = null;
this.time = -1;
this.crc = -1;
this.size = -1;
this.csize = -1;
this.method = -1;
this.flag = 0;
this.extra = null;
this.comment = null;
Clazz.instantialize (this, arguments);
}, java.util.zip, "ZipEntry", null, [java.util.zip.ZipConstants, Cloneable]);
Clazz.makeConstructor (c$, 
function (name) {
if (name == null) {
throw  new NullPointerException ();
}if (name.length > 0xFFFF) {
throw  new IllegalArgumentException ("entry name too long");
}this.name = name;
}, "~S");
$_M(c$, "getName", 
function () {
return this.name;
});
$_M(c$, "setTime", 
function (time) {
this.time = java.util.zip.ZipEntry.javaToDosTime (time);
}, "~N");
$_M(c$, "getTime", 
function () {
return this.time != -1 ? java.util.zip.ZipEntry.dosToJavaTime (this.time) : -1;
});
$_M(c$, "setSize", 
function (size) {
if (size < 0) {
throw  new IllegalArgumentException ("invalid entry size");
}this.size = size;
}, "~N");
$_M(c$, "getSize", 
function () {
return this.size;
});
$_M(c$, "getCompressedSize", 
function () {
return this.csize;
});
$_M(c$, "setCompressedSize", 
function (csize) {
this.csize = csize;
}, "~N");
$_M(c$, "setCrc", 
function (crc) {
if (crc < 0 || crc > 0xFFFFFFFF) {
throw  new IllegalArgumentException ("invalid entry crc-32");
}this.crc = crc;
}, "~N");
$_M(c$, "getCrc", 
function () {
return this.crc;
});
$_M(c$, "setMethod", 
function (method) {
if (method != 0 && method != 8) {
throw  new IllegalArgumentException ("invalid compression method");
}this.method = method;
}, "~N");
$_M(c$, "getMethod", 
function () {
return this.method;
});
$_M(c$, "setExtra", 
function (extra) {
if (extra != null && extra.length > 0xFFFF) {
throw  new IllegalArgumentException ("invalid extra field length");
}this.extra = extra;
}, "~A");
$_M(c$, "getExtra", 
function () {
return this.extra;
});
$_M(c$, "setComment", 
function (comment) {
this.comment = comment;
}, "~S");
$_M(c$, "getComment", 
function () {
return this.comment;
});
$_M(c$, "isDirectory", 
function () {
return this.name.endsWith ("/");
});
Clazz.overrideMethod (c$, "toString", 
function () {
return this.getName ();
});
c$.dosToJavaTime = $_M(c$, "dosToJavaTime", 
($fz = function (dtime) {
var d =  new java.util.Date ((((dtime >> 25) & 0x7f) + 80), (((dtime >> 21) & 0x0f) - 1), ((dtime >> 16) & 0x1f), ((dtime >> 11) & 0x1f), ((dtime >> 5) & 0x3f), ((dtime << 1) & 0x3e));
return d.getTime ();
}, $fz.isPrivate = true, $fz), "~N");
c$.javaToDosTime = $_M(c$, "javaToDosTime", 
($fz = function (time) {
var d =  new java.util.Date (time);
var year = d.getYear () + 1900;
if (year < 1980) {
return 2162688;
}return (year - 1980) << 25 | (d.getMonth () + 1) << 21 | d.getDate () << 16 | d.getHours () << 11 | d.getMinutes () << 5 | d.getSeconds () >> 1;
}, $fz.isPrivate = true, $fz), "~N");
Clazz.overrideMethod (c$, "hashCode", 
function () {
return this.name.hashCode ();
});
$_M(c$, "clone", 
function () {
try {
var e = Clazz.superCall (this, java.util.zip.ZipEntry, "clone", []);
if (this.extra != null) {
e.extra =  Clazz.newByteArray (this.extra.length, 0);
System.arraycopy (this.extra, 0, e.extra, 0, this.extra.length);
}return e;
} catch (e) {
if (Clazz.exceptionOf (e, CloneNotSupportedException)) {
throw  new InternalError ();
} else {
throw e;
}
}
});
Clazz.defineStatics (c$,
"STORED", 0,
"DEFLATED", 8);
});
Clazz.declarePackage ("java.util.zip");
c$ = Clazz.declareType (java.util.zip, "ZipConstants64");
Clazz.defineStatics (c$,
"ZIP64_ENDSIG", 0x06064b50,
"ZIP64_LOCSIG", 0x07064b50,
"ZIP64_ENDHDR", 56,
"ZIP64_LOCHDR", 20,
"ZIP64_EXTHDR", 24,
"ZIP64_EXTID", 0x0001,
"ZIP64_MAGICCOUNT", 0xFFFF,
"ZIP64_MAGICVAL", 0xFFFFFFFF,
"ZIP64_ENDLEN", 4,
"ZIP64_ENDVEM", 12,
"ZIP64_ENDVER", 14,
"ZIP64_ENDNMD", 16,
"ZIP64_ENDDSK", 20,
"ZIP64_ENDTOD", 24,
"ZIP64_ENDTOT", 32,
"ZIP64_ENDSIZ", 40,
"ZIP64_ENDOFF", 48,
"ZIP64_ENDEXT", 56,
"ZIP64_LOCDSK", 4,
"ZIP64_LOCOFF", 8,
"ZIP64_LOCTOT", 16,
"ZIP64_EXTCRC", 4,
"ZIP64_EXTSIZ", 8,
"ZIP64_EXTLEN", 16,
"EFS", 0x800);
Clazz.declarePackage ("java.util.zip");
Clazz.load (["java.util.zip.InflaterInputStream", "$.ZipConstants", "$.CRC32"], "java.util.zip.ZipInputStream", ["java.io.EOFException", "$.IOException", "$.PushbackInputStream", "java.lang.IllegalArgumentException", "$.IndexOutOfBoundsException", "$.Long", "$.NullPointerException", "java.util.zip.Inflater", "$.ZipEntry", "$.ZipException"], function () {
c$ = Clazz.decorateAsClass (function () {
this.entry = null;
this.flag = 0;
this.crc = null;
this.remaining = 0;
this.tmpbuf = null;
this.$closed = false;
this.entryEOF = false;
this.zc = null;
this.byteTest = null;
this.$b = null;
Clazz.instantialize (this, arguments);
}, java.util.zip, "ZipInputStream", java.util.zip.InflaterInputStream, java.util.zip.ZipConstants);
Clazz.prepareFields (c$, function () {
this.crc =  new java.util.zip.CRC32 ();
this.tmpbuf =  Clazz.newByteArray (512, 0);
this.byteTest = [0x20];
this.$b =  Clazz.newByteArray (256, 0);
});
$_M(c$, "ensureOpen", 
($fz = function () {
if (this.$closed) {
throw  new java.io.IOException ("Stream closed");
}}, $fz.isPrivate = true, $fz));
Clazz.makeConstructor (c$, 
function ($in) {
Clazz.superConstructor (this, java.util.zip.ZipInputStream, [ new java.io.PushbackInputStream ($in, 1024), java.util.zip.ZipInputStream.newInflater (), 512]);
var charset = "UTF-8";
try {
 String.instantialize (this.byteTest, charset);
} catch (e) {
if (Clazz.exceptionOf (e, java.io.UnsupportedEncodingException)) {
throw  new NullPointerException ("charset is invalid");
} else {
throw e;
}
}
this.zc = charset;
}, "java.io.InputStream");
c$.newInflater = $_M(c$, "newInflater", 
($fz = function () {
return  new java.util.zip.Inflater ().init (0, true);
}, $fz.isPrivate = true, $fz));
$_M(c$, "getNextEntry", 
function () {
this.ensureOpen ();
if (this.entry != null) {
this.closeEntry ();
}this.crc.reset ();
this.inflater = this.inf = java.util.zip.ZipInputStream.newInflater ();
if ((this.entry = this.readLOC ()) == null) {
return null;
}if (this.entry.method == 0) {
this.remaining = this.entry.size;
}this.entryEOF = false;
return this.entry;
});
$_M(c$, "closeEntry", 
function () {
this.ensureOpen ();
while (this.read (this.tmpbuf, 0, this.tmpbuf.length) != -1) {
}
this.entryEOF = true;
});
Clazz.overrideMethod (c$, "available", 
function () {
this.ensureOpen ();
return (this.entryEOF ? 0 : 1);
});
Clazz.overrideMethod (c$, "read", 
function (b, off, len) {
this.ensureOpen ();
if (off < 0 || len < 0 || off > b.length - len) {
throw  new IndexOutOfBoundsException ();
} else if (len == 0) {
return 0;
}if (this.entry == null) {
return -1;
}switch (this.entry.method) {
case 8:
len = this.readInf (b, off, len);
if (len == -1) {
this.readEnd (this.entry);
this.entryEOF = true;
this.entry = null;
} else {
this.crc.update (b, off, len);
}return len;
case 0:
if (this.remaining <= 0) {
this.entryEOF = true;
this.entry = null;
return -1;
}if (len > this.remaining) {
len = this.remaining;
}len = this.$in.read (b, off, len);
if (len == -1) {
throw  new java.util.zip.ZipException ("unexpected EOF");
}this.crc.update (b, off, len);
this.remaining -= len;
if (this.remaining == 0 && this.entry.crc != this.crc.getValue ()) {
throw  new java.util.zip.ZipException ("invalid entry CRC (expected 0x" + Long.toHexString (this.entry.crc) + " but got 0x" + Long.toHexString (this.crc.getValue ()) + ")");
}return len;
default:
throw  new java.util.zip.ZipException ("invalid compression method");
}
}, "~A,~N,~N");
Clazz.overrideMethod (c$, "skip", 
function (n) {
if (n < 0) {
throw  new IllegalArgumentException ("negative skip length");
}this.ensureOpen ();
var max = Math.min (n, 2147483647);
var total = 0;
while (total < max) {
var len = max - total;
if (len > this.tmpbuf.length) {
len = this.tmpbuf.length;
}len = this.read (this.tmpbuf, 0, len);
if (len == -1) {
this.entryEOF = true;
break;
}total += len;
}
return total;
}, "~N");
$_M(c$, "close", 
function () {
if (!this.$closed) {
Clazz.superCall (this, java.util.zip.ZipInputStream, "close", []);
this.$closed = true;
}});
$_M(c$, "readLOC", 
($fz = function () {
try {
this.readFully (this.tmpbuf, 0, 30);
} catch (e) {
if (Clazz.exceptionOf (e, java.io.EOFException)) {
return null;
} else {
throw e;
}
}
if (java.util.zip.ZipInputStream.get32 (this.tmpbuf, 0) != 67324752) {
return null;
}this.flag = java.util.zip.ZipInputStream.get16 (this.tmpbuf, 6);
var len = java.util.zip.ZipInputStream.get16 (this.tmpbuf, 26);
var blen = this.$b.length;
if (len > blen) {
do blen = blen * 2;
 while (len > blen);
this.$b =  Clazz.newByteArray (blen, 0);
}this.readFully (this.$b, 0, len);
var e = this.createZipEntry (((this.flag & 2048) != 0) ? this.toStringUTF8 (this.$b, len) : this.toStringb2 (this.$b, len));
if ((this.flag & 1) == 1) {
throw  new java.util.zip.ZipException ("encrypted ZIP entry not supported");
}e.method = java.util.zip.ZipInputStream.get16 (this.tmpbuf, 8);
e.time = java.util.zip.ZipInputStream.get32 (this.tmpbuf, 10);
if ((this.flag & 8) == 8) {
if (e.method != 8) {
throw  new java.util.zip.ZipException ("only DEFLATED entries can have EXT descriptor");
}} else {
e.crc = java.util.zip.ZipInputStream.get32 (this.tmpbuf, 14);
e.csize = java.util.zip.ZipInputStream.get32 (this.tmpbuf, 18);
e.size = java.util.zip.ZipInputStream.get32 (this.tmpbuf, 22);
}len = java.util.zip.ZipInputStream.get16 (this.tmpbuf, 28);
if (len > 0) {
var bb =  Clazz.newByteArray (len, 0);
this.readFully (bb, 0, len);
e.setExtra (bb);
if (e.csize == 4294967295 || e.size == 4294967295) {
var off = 0;
while (off + 4 < len) {
var sz = java.util.zip.ZipInputStream.get16 (bb, off + 2);
if (java.util.zip.ZipInputStream.get16 (bb, off) == 1) {
off += 4;
if (sz < 16 || (off + sz) > len) {
return e;
}e.size = java.util.zip.ZipInputStream.get64 (bb, off);
e.csize = java.util.zip.ZipInputStream.get64 (bb, off + 8);
break;
}off += (sz + 4);
}
}}return e;
}, $fz.isPrivate = true, $fz));
$_M(c$, "toStringUTF8", 
($fz = function (b2, len) {
try {
return  String.instantialize (b2, 0, len, this.zc);
} catch (e) {
if (Clazz.exceptionOf (e, java.io.UnsupportedEncodingException)) {
return this.toStringb2 (b2, len);
} else {
throw e;
}
}
}, $fz.isPrivate = true, $fz), "~A,~N");
$_M(c$, "toStringb2", 
($fz = function (b2, len) {
return  String.instantialize (b2, 0, len);
}, $fz.isPrivate = true, $fz), "~A,~N");
$_M(c$, "createZipEntry", 
function (name) {
return  new java.util.zip.ZipEntry (name);
}, "~S");
$_M(c$, "readEnd", 
($fz = function (e) {
var n = this.inf.getAvailIn ();
if (n > 0) {
(this.$in).unread (this.buf, this.len - n, n);
this.eof = false;
}if ((this.flag & 8) == 8) {
if (this.inf.getTotalOut () > 4294967295 || this.inf.getTotalIn () > 4294967295) {
this.readFully (this.tmpbuf, 0, 24);
var sig = java.util.zip.ZipInputStream.get32 (this.tmpbuf, 0);
if (sig != 134695760) {
e.crc = sig;
e.csize = java.util.zip.ZipInputStream.get64 (this.tmpbuf, 4);
e.size = java.util.zip.ZipInputStream.get64 (this.tmpbuf, 12);
(this.$in).unread (this.tmpbuf, 19, 4);
} else {
e.crc = java.util.zip.ZipInputStream.get32 (this.tmpbuf, 4);
e.csize = java.util.zip.ZipInputStream.get64 (this.tmpbuf, 8);
e.size = java.util.zip.ZipInputStream.get64 (this.tmpbuf, 16);
}} else {
this.readFully (this.tmpbuf, 0, 16);
var sig = java.util.zip.ZipInputStream.get32 (this.tmpbuf, 0);
if (sig != 134695760) {
e.crc = sig;
e.csize = java.util.zip.ZipInputStream.get32 (this.tmpbuf, 4);
e.size = java.util.zip.ZipInputStream.get32 (this.tmpbuf, 8);
(this.$in).unread (this.tmpbuf, 11, 4);
} else {
e.crc = java.util.zip.ZipInputStream.get32 (this.tmpbuf, 4);
e.csize = java.util.zip.ZipInputStream.get32 (this.tmpbuf, 8);
e.size = java.util.zip.ZipInputStream.get32 (this.tmpbuf, 12);
}}}if (e.size != this.inf.getTotalOut ()) {
throw  new java.util.zip.ZipException ("invalid entry size (expected " + e.size + " but got " + this.inf.getTotalOut () + " bytes)");
}if (e.csize != this.inf.getTotalIn ()) {
throw  new java.util.zip.ZipException ("invalid entry compressed size (expected " + e.csize + " but got " + this.inf.getTotalIn () + " bytes)");
}if (e.crc != this.crc.getValue ()) {
throw  new java.util.zip.ZipException ("invalid entry CRC (expected 0x" + Long.toHexString (e.crc) + " but got 0x" + Long.toHexString (this.crc.getValue ()) + ")");
}}, $fz.isPrivate = true, $fz), "java.util.zip.ZipEntry");
$_M(c$, "readFully", 
($fz = function (b, off, len) {
while (len > 0) {
var n = this.$in.read (b, off, len);
if (n == -1) {
throw  new java.io.EOFException ();
}off += n;
len -= n;
}
}, $fz.isPrivate = true, $fz), "~A,~N,~N");
c$.get16 = $_M(c$, "get16", 
($fz = function (b, off) {
return (b[off] & 0xff) | ((b[off + 1] & 0xff) << 8);
}, $fz.isPrivate = true, $fz), "~A,~N");
c$.get32 = $_M(c$, "get32", 
($fz = function (b, off) {
return (java.util.zip.ZipInputStream.get16 (b, off) | (java.util.zip.ZipInputStream.get16 (b, off + 2) << 16)) & 0xffffffff;
}, $fz.isPrivate = true, $fz), "~A,~N");
c$.get64 = $_M(c$, "get64", 
($fz = function (b, off) {
return java.util.zip.ZipInputStream.get32 (b, off) | (java.util.zip.ZipInputStream.get32 (b, off + 4) << 32);
}, $fz.isPrivate = true, $fz), "~A,~N");
Clazz.defineStatics (c$,
"STORED", 0,
"DEFLATED", 8);
});
Clazz.load (["java.io.FilterInputStream"], "java.io.PushbackInputStream", ["java.io.IOException", "java.lang.IllegalArgumentException", "$.IndexOutOfBoundsException", "$.NullPointerException"], function () {
c$ = Clazz.decorateAsClass (function () {
this.buf = null;
this.pos = 0;
Clazz.instantialize (this, arguments);
}, java.io, "PushbackInputStream", java.io.FilterInputStream);
$_M(c$, "ensureOpen", 
($fz = function () {
if (this.$in == null) throw  new java.io.IOException ("Stream closed");
}, $fz.isPrivate = true, $fz));
Clazz.makeConstructor (c$, 
function ($in, size) {
Clazz.superConstructor (this, java.io.PushbackInputStream, [$in]);
if (size <= 0) {
throw  new IllegalArgumentException ("size <= 0");
}this.buf =  Clazz.newByteArray (size, 0);
this.pos = size;
}, "java.io.InputStream,~N");
Clazz.overrideMethod (c$, "readByteAsInt", 
function () {
this.ensureOpen ();
if (this.pos < this.buf.length) {
return this.buf[this.pos++] & 0xff;
}return this.$in.readByteAsInt ();
});
Clazz.overrideMethod (c$, "read", 
function (b, off, len) {
this.ensureOpen ();
if (b == null) {
throw  new NullPointerException ();
} else if (off < 0 || len < 0 || len > b.length - off) {
throw  new IndexOutOfBoundsException ();
} else if (len == 0) {
return 0;
}var avail = this.buf.length - this.pos;
if (avail > 0) {
if (len < avail) {
avail = len;
}System.arraycopy (this.buf, this.pos, b, off, avail);
this.pos += avail;
off += avail;
len -= avail;
}if (len > 0) {
len = this.$in.read (b, off, len);
if (len == -1) {
return avail == 0 ? -1 : avail;
}return avail + len;
}return avail;
}, "~A,~N,~N");
$_M(c$, "unreadByte", 
function (b) {
this.ensureOpen ();
if (this.pos == 0) {
throw  new java.io.IOException ("Push back buffer is full");
}this.buf[--this.pos] = b;
}, "~N");
$_M(c$, "unread", 
function (b, off, len) {
this.ensureOpen ();
if (len > this.pos) {
throw  new java.io.IOException ("Push back buffer is full");
}this.pos -= len;
System.arraycopy (b, off, this.buf, this.pos, len);
}, "~A,~N,~N");
Clazz.overrideMethod (c$, "available", 
function () {
this.ensureOpen ();
var n = this.buf.length - this.pos;
var avail = this.$in.available ();
return n > (2147483647 - avail) ? 2147483647 : n + avail;
});
Clazz.overrideMethod (c$, "skip", 
function (n) {
this.ensureOpen ();
if (n <= 0) {
return 0;
}var pskip = this.buf.length - this.pos;
if (pskip > 0) {
if (n < pskip) {
pskip = n;
}this.pos += pskip;
n -= pskip;
}if (n > 0) {
pskip += this.$in.skip (n);
}return pskip;
}, "~N");
Clazz.overrideMethod (c$, "markSupported", 
function () {
return false;
});
Clazz.overrideMethod (c$, "mark", 
function (readlimit) {
}, "~N");
Clazz.overrideMethod (c$, "reset", 
function () {
throw  new java.io.IOException ("mark/reset not supported");
});
Clazz.overrideMethod (c$, "close", 
function () {
if (this.$in == null) return;
this.$in.close ();
this.$in = null;
this.buf = null;
});
});
Clazz.declarePackage ("J.api");
Clazz.declareInterface (J.api, "ZInputStream");
Clazz.declarePackage ("J.io2");
Clazz.load (["java.util.zip.ZipInputStream", "J.api.ZInputStream"], "J.io2.JmolZipInputStream", null, function () {
c$ = Clazz.declareType (J.io2, "JmolZipInputStream", java.util.zip.ZipInputStream, J.api.ZInputStream);
});
Clazz.declarePackage ("JZ");
Clazz.load (["java.io.FilterOutputStream"], "JZ.DeflaterOutputStream", ["java.io.IOException", "java.lang.IndexOutOfBoundsException"], function () {
c$ = Clazz.decorateAsClass (function () {
this.deflater = null;
this.buffer = null;
this.closed = false;
this.syncFlush = false;
this.buf1 = null;
this.mydeflater = false;
this.close_out = true;
Clazz.instantialize (this, arguments);
}, JZ, "DeflaterOutputStream", java.io.FilterOutputStream);
Clazz.prepareFields (c$, function () {
this.buf1 =  Clazz.newByteArray (1, 0);
});
Clazz.makeConstructor (c$, 
function (out, deflater, size, close_out) {
Clazz.superConstructor (this, JZ.DeflaterOutputStream, [out]);
if (size == 0) size = 512;
this.deflater = deflater;
this.buffer =  Clazz.newByteArray (size, 0);
this.close_out = close_out;
}, "java.io.OutputStream,JZ.Deflater,~N,~B");
Clazz.overrideMethod (c$, "writeByteAsInt", 
function (b) {
this.buf1[0] = (b & 0xff);
this.write (this.buf1, 0, 1);
}, "~N");
$_M(c$, "write", 
function (b, off, len) {
if (this.deflater.finished ()) throw  new java.io.IOException ("finished");
if ( new Boolean ( new Boolean (off < 0 | len < 0).valueOf () | off + len > b.length).valueOf ()) throw  new IndexOutOfBoundsException ();
if (len == 0) return;
var flush = this.syncFlush ? 2 : 0;
this.deflater.setInput (b, off, len, true);
while (this.deflater.avail_in > 0) {
var err = this.deflate (flush);
if (err == 1) break;
}
}, "~A,~N,~N");
$_M(c$, "finish", 
function () {
while (!this.deflater.finished ()) {
this.deflate (4);
}
});
Clazz.overrideMethod (c$, "close", 
function () {
if (!this.closed) {
this.finish ();
if (this.mydeflater) {
this.deflater.end ();
}if (this.close_out) this.out.close ();
this.closed = true;
}});
$_M(c$, "deflate", 
function (flush) {
this.deflater.setOutput (this.buffer, 0, this.buffer.length);
var err = this.deflater.deflate (flush);
switch (err) {
case 0:
case 1:
break;
case -5:
if (this.deflater.avail_in <= 0 && flush != 4) {
break;
}default:
throw  new java.io.IOException ("failed to deflate");
}
var len = this.deflater.next_out_index;
if (len > 0) {
this.out.write (this.buffer, 0, len);
}return err;
}, "~N");
Clazz.overrideMethod (c$, "flush", 
function () {
if (this.syncFlush && !this.deflater.finished ()) {
while (true) {
var err = this.deflate (2);
if (this.deflater.next_out_index < this.buffer.length) break;
if (err == 1) break;
}
}this.out.flush ();
});
$_M(c$, "getTotalIn", 
function () {
return this.deflater.getTotalIn ();
});
$_M(c$, "getTotalOut", 
function () {
return this.deflater.getTotalOut ();
});
$_M(c$, "setSyncFlush", 
function (syncFlush) {
this.syncFlush = syncFlush;
}, "~B");
$_M(c$, "getSyncFlush", 
function () {
return this.syncFlush;
});
$_M(c$, "getDeflater", 
function () {
return this.deflater;
});
Clazz.defineStatics (c$,
"DEFAULT_BUFSIZE", 512);
});
Clazz.declarePackage ("java.util.zip");
Clazz.load (["JZ.Deflater"], "java.util.zip.Deflater", null, function () {
c$ = Clazz.declareType (java.util.zip, "Deflater", JZ.Deflater);
Clazz.makeConstructor (c$, 
function (compressionLevel) {
if (compressionLevel != 2147483647) this.init (compressionLevel, 0, false);
}, "~N");
Clazz.defineStatics (c$,
"DEFAULT_COMPRESSION", -1);
});
Clazz.declarePackage ("java.util.zip");
Clazz.load (["JZ.DeflaterOutputStream"], "java.util.zip.DeflaterOutputStream", null, function () {
c$ = Clazz.declareType (java.util.zip, "DeflaterOutputStream", JZ.DeflaterOutputStream);
Clazz.makeConstructor (c$, 
function (out, deflater) {
Clazz.superConstructor (this, java.util.zip.DeflaterOutputStream, [out, deflater, 0, true]);
}, "java.io.OutputStream,java.util.zip.Deflater");
});
Clazz.declarePackage ("java.util.zip");
Clazz.load (["java.util.zip.DeflaterOutputStream", "$.ZipConstants", "java.util.Hashtable", "java.util.zip.CRC32", "J.util.JmolList"], "java.util.zip.ZipOutputStream", ["JZ.ZStream", "java.io.IOException", "java.lang.Boolean", "$.IllegalArgumentException", "$.IndexOutOfBoundsException", "$.Long", "java.util.zip.Deflater", "$.ZipException"], function () {
c$ = Clazz.decorateAsClass (function () {
this.current = null;
this.xentries = null;
this.names = null;
this.crc = null;
this.written = 0;
this.locoff = 0;
this.comment = null;
this.method = 8;
this.finished = false;
this.$closed = false;
Clazz.instantialize (this, arguments);
}, java.util.zip, "ZipOutputStream", java.util.zip.DeflaterOutputStream, java.util.zip.ZipConstants);
Clazz.prepareFields (c$, function () {
this.xentries =  new J.util.JmolList ();
this.names =  new java.util.Hashtable ();
this.crc =  new java.util.zip.CRC32 ();
});
c$.version = $_M(c$, "version", 
($fz = function (e) {
switch (e.method) {
case 8:
return 20;
case 0:
return 10;
default:
throw  new java.util.zip.ZipException ("unsupported compression method");
}
}, $fz.isPrivate = true, $fz), "java.util.zip.ZipEntry");
$_M(c$, "ensureOpen", 
($fz = function () {
if (this.$closed) {
throw  new java.io.IOException ("Stream closed");
}}, $fz.isPrivate = true, $fz));
Clazz.makeConstructor (c$, 
function (out) {
Clazz.superConstructor (this, java.util.zip.ZipOutputStream, [out, java.util.zip.ZipOutputStream.newDeflater ()]);
}, "java.io.OutputStream");
c$.newDeflater = $_M(c$, "newDeflater", 
($fz = function () {
return ( new java.util.zip.Deflater (2147483647)).init (-1, 0, true);
}, $fz.isPrivate = true, $fz));
$_M(c$, "setComment", 
function (comment) {
if (comment != null) {
this.comment = JZ.ZStream.getBytes (comment);
if (this.comment.length > 0xffff) throw  new IllegalArgumentException ("ZIP file comment too long.");
}}, "~S");
$_M(c$, "putNextEntry", 
function (e) {
this.ensureOpen ();
if (this.current != null) {
this.closeEntry ();
}if (e.time == -1) {
e.setTime (System.currentTimeMillis ());
}if (e.method == -1) {
e.method = this.method;
}e.flag = 0;
switch (e.method) {
case 8:
if (e.size == -1 || e.csize == -1 || e.crc == -1) e.flag = 8;
break;
case 0:
if (e.size == -1) {
e.size = e.csize;
} else if (e.csize == -1) {
e.csize = e.size;
} else if (e.size != e.csize) {
throw  new java.util.zip.ZipException ("STORED entry where compressed != uncompressed size");
}if (e.size == -1 || e.crc == -1) {
throw  new java.util.zip.ZipException ("STORED entry missing size, compressed size, or crc-32");
}break;
default:
throw  new java.util.zip.ZipException ("unsupported compression method");
}
if (this.names.containsKey (e.name)) {
throw  new java.util.zip.ZipException ("duplicate entry: " + e.name);
}this.names.put (e.name, Boolean.TRUE);
e.flag |= 2048;
this.current = e;
this.current.offset = this.written;
this.xentries.addLast (this.current);
this.writeLOC (this.current);
}, "java.util.zip.ZipEntry");
$_M(c$, "closeEntry", 
function () {
this.ensureOpen ();
if (this.current != null) {
var e = this.current;
switch (e.method) {
case 8:
this.deflater.finish ();
Clazz.superCall (this, java.util.zip.ZipOutputStream, "finish", []);
if ((e.flag & 8) == 0) {
if (e.size != this.deflater.getBytesRead ()) {
throw  new java.util.zip.ZipException ("invalid entry size (expected " + e.size + " but got " + this.deflater.getBytesRead () + " bytes)");
}if (e.csize != this.deflater.getBytesWritten ()) {
throw  new java.util.zip.ZipException ("invalid entry compressed size (expected " + e.csize + " but got " + this.deflater.getBytesWritten () + " bytes)");
}if (e.crc != this.crc.getValue ()) {
throw  new java.util.zip.ZipException ("invalid entry CRC-32 (expected 0x" + Long.toHexString (e.crc) + " but got 0x" + Long.toHexString (this.crc.getValue ()) + ")");
}} else {
e.size = this.deflater.getBytesRead ();
e.csize = this.deflater.getBytesWritten ();
e.crc = this.crc.getValue ();
this.writeEXT (e);
}this.deflater = java.util.zip.ZipOutputStream.newDeflater ();
this.written += e.csize;
break;
case 0:
if (e.size != this.written - this.locoff) {
throw  new java.util.zip.ZipException ("invalid entry size (expected " + e.size + " but got " + (this.written - this.locoff) + " bytes)");
}if (e.crc != this.crc.getValue ()) {
throw  new java.util.zip.ZipException ("invalid entry crc-32 (expected 0x" + Long.toHexString (e.crc) + " but got 0x" + Long.toHexString (this.crc.getValue ()) + ")");
}break;
default:
throw  new java.util.zip.ZipException ("invalid compression method");
}
this.crc.reset ();
this.current = null;
}});
$_M(c$, "write", 
function (b, off, len) {
this.ensureOpen ();
if (off < 0 || len < 0 || off > b.length - len) {
throw  new IndexOutOfBoundsException ();
} else if (len == 0) {
return;
}if (this.current == null) {
throw  new java.util.zip.ZipException ("no current ZIP entry");
}var entry = this.current;
switch (entry.method) {
case 8:
Clazz.superCall (this, java.util.zip.ZipOutputStream, "write", [b, off, len]);
break;
case 0:
this.written += len;
if (this.written - this.locoff > entry.size) {
throw  new java.util.zip.ZipException ("attempt to write past end of STORED entry");
}this.out.write (this.buffer, 0, len);
break;
default:
throw  new java.util.zip.ZipException ("invalid compression method");
}
this.crc.update (b, off, len);
}, "~A,~N,~N");
$_M(c$, "finish", 
function () {
this.ensureOpen ();
if (this.finished) {
return;
}if (this.current != null) {
this.closeEntry ();
}var off = this.written;
for (var xentry, $xentry = this.xentries.iterator (); $xentry.hasNext () && ((xentry = $xentry.next ()) || true);) this.writeCEN (xentry);

this.writeEND (off, this.written - off);
this.finished = true;
});
$_M(c$, "close", 
function () {
if (!this.$closed) {
Clazz.superCall (this, java.util.zip.ZipOutputStream, "close", []);
this.$closed = true;
}});
$_M(c$, "writeLOC", 
($fz = function (entry) {
var e = entry;
var flag = e.flag;
var elen = (e.extra != null) ? e.extra.length : 0;
var hasZip64 = false;
this.writeInt (67324752);
if ((flag & 8) == 8) {
this.writeShort (java.util.zip.ZipOutputStream.version (e));
this.writeShort (flag);
this.writeShort (e.method);
this.writeInt (e.time);
this.writeInt (0);
this.writeInt (0);
this.writeInt (0);
} else {
if (e.csize >= 4294967295 || e.size >= 4294967295) {
hasZip64 = true;
this.writeShort (45);
} else {
this.writeShort (java.util.zip.ZipOutputStream.version (e));
}this.writeShort (flag);
this.writeShort (e.method);
this.writeInt (e.time);
this.writeInt (e.crc);
if (hasZip64) {
this.writeInt (4294967295);
this.writeInt (4294967295);
elen += 20;
} else {
this.writeInt (e.csize);
this.writeInt (e.size);
}}var nameBytes = JZ.ZStream.getBytes (e.name);
this.writeShort (nameBytes.length);
this.writeShort (elen);
this.writeBytes (nameBytes, 0, nameBytes.length);
if (hasZip64) {
this.writeShort (1);
this.writeShort (16);
this.writeLong (e.size);
this.writeLong (e.csize);
}if (e.extra != null) {
this.writeBytes (e.extra, 0, e.extra.length);
}this.locoff = this.written;
}, $fz.isPrivate = true, $fz), "java.util.zip.ZipEntry");
$_M(c$, "writeEXT", 
($fz = function (e) {
this.writeInt (134695760);
this.writeInt (e.crc);
if (e.csize >= 4294967295 || e.size >= 4294967295) {
this.writeLong (e.csize);
this.writeLong (e.size);
} else {
this.writeInt (e.csize);
this.writeInt (e.size);
}}, $fz.isPrivate = true, $fz), "java.util.zip.ZipEntry");
$_M(c$, "writeCEN", 
($fz = function (entry) {
var e = entry;
var flag = e.flag;
var version = java.util.zip.ZipOutputStream.version (e);
var csize = e.csize;
var size = e.size;
var offset = entry.offset;
var e64len = 0;
var hasZip64 = false;
if (e.csize >= 4294967295) {
csize = 4294967295;
e64len += 8;
hasZip64 = true;
}if (e.size >= 4294967295) {
size = 4294967295;
e64len += 8;
hasZip64 = true;
}if (entry.offset >= 4294967295) {
offset = 4294967295;
e64len += 8;
hasZip64 = true;
}this.writeInt (33639248);
if (hasZip64) {
this.writeShort (45);
this.writeShort (45);
} else {
this.writeShort (version);
this.writeShort (version);
}this.writeShort (flag);
this.writeShort (e.method);
this.writeInt (e.time);
this.writeInt (e.crc);
this.writeInt (csize);
this.writeInt (size);
var nameBytes = JZ.ZStream.getBytes (e.name);
this.writeShort (nameBytes.length);
if (hasZip64) {
this.writeShort (e64len + 4 + (e.extra != null ? e.extra.length : 0));
} else {
this.writeShort (e.extra != null ? e.extra.length : 0);
}var commentBytes;
if (e.comment != null) {
commentBytes = JZ.ZStream.getBytes (e.comment);
this.writeShort (Math.min (commentBytes.length, 0xffff));
} else {
commentBytes = null;
this.writeShort (0);
}this.writeShort (0);
this.writeShort (0);
this.writeInt (0);
this.writeInt (offset);
this.writeBytes (nameBytes, 0, nameBytes.length);
if (hasZip64) {
this.writeShort (1);
this.writeShort (e64len);
if (size == 4294967295) this.writeLong (e.size);
if (csize == 4294967295) this.writeLong (e.csize);
if (offset == 4294967295) this.writeLong (entry.offset);
}if (e.extra != null) {
this.writeBytes (e.extra, 0, e.extra.length);
}if (commentBytes != null) {
this.writeBytes (commentBytes, 0, Math.min (commentBytes.length, 0xffff));
}}, $fz.isPrivate = true, $fz), "java.util.zip.ZipEntry");
$_M(c$, "writeEND", 
($fz = function (off, len) {
var hasZip64 = false;
var xlen = len;
var xoff = off;
if (xlen >= 4294967295) {
xlen = 4294967295;
hasZip64 = true;
}if (xoff >= 4294967295) {
xoff = 4294967295;
hasZip64 = true;
}var count = this.xentries.size ();
if (count >= 65535) {
count = 65535;
hasZip64 = true;
}if (hasZip64) {
var off64 = this.written;
this.writeInt (101075792);
this.writeLong (44);
this.writeShort (45);
this.writeShort (45);
this.writeInt (0);
this.writeInt (0);
this.writeLong (this.xentries.size ());
this.writeLong (this.xentries.size ());
this.writeLong (len);
this.writeLong (off);
this.writeInt (117853008);
this.writeInt (0);
this.writeLong (off64);
this.writeInt (1);
}this.writeInt (101010256);
this.writeShort (0);
this.writeShort (0);
this.writeShort (count);
this.writeShort (count);
this.writeInt (xlen);
this.writeInt (xoff);
if (this.comment != null) {
this.writeShort (this.comment.length);
this.writeBytes (this.comment, 0, this.comment.length);
} else {
this.writeShort (0);
}}, $fz.isPrivate = true, $fz), "~N,~N");
$_M(c$, "writeShort", 
($fz = function (v) {
var out = this.out;
{
out.writeByteAsInt((v >>> 0) & 0xff);
out.writeByteAsInt((v >>> 8) & 0xff);
}this.written += 2;
}, $fz.isPrivate = true, $fz), "~N");
$_M(c$, "writeInt", 
($fz = function (v) {
var out = this.out;
{
out.writeByteAsInt((v >>> 0) & 0xff);
out.writeByteAsInt((v >>> 8) & 0xff);
out.writeByteAsInt((v >>> 16) & 0xff);
out.writeByteAsInt((v >>> 24) & 0xff);
}this.written += 4;
}, $fz.isPrivate = true, $fz), "~N");
$_M(c$, "writeLong", 
($fz = function (v) {
var out = this.out;
{
out.writeByteAsInt((v >>> 0) & 0xff);
out.writeByteAsInt((v >>> 8) & 0xff);
out.writeByteAsInt((v >>> 16) & 0xff);
out.writeByteAsInt((v >>> 24) & 0xff);
out.writeByteAsInt(0);
out.writeByteAsInt(0);
out.writeByteAsInt(0);
out.writeByteAsInt(0);
}this.written += 8;
}, $fz.isPrivate = true, $fz), "~N");
$_M(c$, "writeBytes", 
($fz = function (b, off, len) {
this.out.write (b, off, len);
this.written += len;
}, $fz.isPrivate = true, $fz), "~A,~N,~N");
Clazz.defineStatics (c$,
"STORED", 0,
"DEFLATED", 8);
});
Clazz.declarePackage ("J.image");
Clazz.load (["J.api.JmolImageEncoder"], "J.image.ImageEncoder", null, function () {
c$ = Clazz.decorateAsClass (function () {
this.out = null;
this.width = -1;
this.height = -1;
this.quality = -1;
this.date = null;
this.errRet = null;
this.pixels = null;
Clazz.instantialize (this, arguments);
}, J.image, "ImageEncoder", null, J.api.JmolImageEncoder);
Clazz.overrideMethod (c$, "createImage", 
function (apiPlatform, type, objImage, out, params, errRet) {
this.out = out;
this.errRet = errRet;
try {
this.width = apiPlatform.getImageWidth (objImage);
this.height = apiPlatform.getImageHeight (objImage);
this.date = params.get ("date");
var q = params.get ("quality");
this.quality = (q == null ? -1 : q.intValue ());
this.setParams (params);
this.encodeImage (apiPlatform, objImage);
this.generate ();
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
errRet[0] = e.toString ();
out.cancel ();
} else {
throw e;
}
} finally {
this.close ();
}
return (errRet[0] == null);
}, "J.api.ApiPlatform,~S,~O,J.io.JmolOutputChannel,java.util.Map,~A");
$_M(c$, "encodeImage", 
function (apiPlatform, objImage) {
{
pixels = null;
}this.pixels = apiPlatform.grabPixels (objImage, this.width, this.height, this.pixels, 0, this.height);
}, "J.api.ApiPlatform,~O");
$_M(c$, "putString", 
function (str) {
this.out.append (str);
}, "~S");
$_M(c$, "putByte", 
function (b) {
this.out.writeByteAsInt (b);
}, "~N");
$_M(c$, "close", 
function () {
this.out.closeChannel ();
});
});
Clazz.declarePackage ("J.image");
Clazz.load (["J.image.ImageEncoder"], "J.image.CRCEncoder", ["java.util.zip.CRC32", "J.util.ArrayUtil"], function () {
c$ = Clazz.decorateAsClass (function () {
this.startPos = 0;
this.bytePos = 0;
this.crc = null;
this.pngBytes = null;
this.dataLen = 0;
this.int2 = null;
this.int4 = null;
Clazz.instantialize (this, arguments);
}, J.image, "CRCEncoder", J.image.ImageEncoder);
Clazz.prepareFields (c$, function () {
this.int2 =  Clazz.newByteArray (2, 0);
this.int4 =  Clazz.newByteArray (4, 0);
});
Clazz.makeConstructor (c$, 
function () {
Clazz.superConstructor (this, J.image.CRCEncoder, []);
this.pngBytes =  Clazz.newByteArray (250, 0);
this.crc =  new java.util.zip.CRC32 ();
});
$_M(c$, "setData", 
function (b, pt) {
this.pngBytes = b;
this.dataLen = b.length;
this.startPos = this.bytePos = pt;
}, "~A,~N");
$_M(c$, "getBytes", 
function () {
return (this.dataLen == this.pngBytes.length ? this.pngBytes : J.util.ArrayUtil.arrayCopyByte (this.pngBytes, this.dataLen));
});
$_M(c$, "writeCRC", 
function () {
this.crc.reset ();
this.crc.update (this.pngBytes, this.startPos, this.bytePos - this.startPos);
this.writeInt4 (this.crc.getValue ());
});
$_M(c$, "writeInt2", 
function (n) {
this.int2[0] = ((n >> 8) & 0xff);
this.int2[1] = (n & 0xff);
this.writeBytes (this.int2);
}, "~N");
$_M(c$, "writeInt4", 
function (n) {
J.image.CRCEncoder.getInt4 (n, this.int4);
this.writeBytes (this.int4);
}, "~N");
c$.getInt4 = $_M(c$, "getInt4", 
function (n, int4) {
int4[0] = ((n >> 24) & 0xff);
int4[1] = ((n >> 16) & 0xff);
int4[2] = ((n >> 8) & 0xff);
int4[3] = (n & 0xff);
}, "~N,~A");
$_M(c$, "writeByte", 
function (b) {
var temp = [b];
this.writeBytes (temp);
}, "~N");
$_M(c$, "writeString", 
function (s) {
this.writeBytes (s.getBytes ());
}, "~S");
$_M(c$, "writeBytes", 
function (data) {
var newPos = this.bytePos + data.length;
this.dataLen = Math.max (this.dataLen, newPos);
if (newPos > this.pngBytes.length) this.pngBytes = J.util.ArrayUtil.arrayCopyByte (this.pngBytes, newPos + 16);
System.arraycopy (data, 0, this.pngBytes, this.bytePos, data.length);
this.bytePos = newPos;
}, "~A");
});
Clazz.declarePackage ("J.image");
Clazz.load (["J.image.CRCEncoder"], "J.image.PngEncoder", ["java.io.ByteArrayOutputStream", "java.util.zip.Deflater", "$.DeflaterOutputStream"], function () {
c$ = Clazz.decorateAsClass (function () {
this.encodeAlpha = false;
this.filter = 0;
this.bytesPerPixel = 0;
this.compressionLevel = 0;
this.type = null;
this.transparentColor = null;
this.applicationData = null;
this.applicationPrefix = null;
this.version = null;
this.scanLines = null;
this.byteWidth = 0;
Clazz.instantialize (this, arguments);
}, J.image, "PngEncoder", J.image.CRCEncoder);
Clazz.overrideMethod (c$, "setParams", 
function (params) {
if (this.quality < 0) this.quality = 2;
 else if (this.quality > 9) this.quality = 9;
this.encodeAlpha = false;
this.filter = 0;
this.compressionLevel = this.quality;
this.transparentColor = params.get ("transparentColor");
this.type = (params.get ("type") + "0000").substring (0, 4);
this.version = params.get ("comment");
this.applicationData = params.get ("applicationData");
this.applicationPrefix = params.get ("applicationPrefix");
}, "java.util.Map");
Clazz.overrideMethod (c$, "generate", 
function () {
var ptJmol =  Clazz.newIntArray (1, 0);
if (!this.pngEncode (ptJmol)) {
this.out.cancel ();
return;
}var bytes = this.getBytes ();
var len = this.dataLen;
if (this.applicationData != null) {
J.image.PngEncoder.setJmolTypeText (this.applicationPrefix, ptJmol[0], bytes, len, this.applicationData.length, this.type);
this.out.write (bytes, 0, len);
len = (bytes = this.applicationData).length;
}this.out.write (bytes, 0, len);
});
$_M(c$, "pngEncode", 
($fz = function (ptAppTag) {
var pngIdBytes = [-119, 80, 78, 71, 13, 10, 26, 10];
this.writeBytes (pngIdBytes);
this.writeHeader ();
ptAppTag[0] = this.bytePos + 4;
this.writeText (J.image.PngEncoder.getApplicationText (this.applicationPrefix, this.type, 0, 0));
this.writeText ("Software\0Jmol " + this.version);
this.writeText ("Creation Time\0" + this.date);
if (!this.encodeAlpha && this.transparentColor != null) this.writeTransparentColor (this.transparentColor.intValue ());
return this.writeImageData ();
}, $fz.isPrivate = true, $fz), "~A");
c$.setJmolTypeText = $_M(c$, "setJmolTypeText", 
($fz = function (prefix, ptJmolByteText, b, nPNG, nState, type) {
var s = "iTXt" + J.image.PngEncoder.getApplicationText (prefix, type, nPNG, nState);
var encoder =  new J.image.PngEncoder ();
encoder.setData (b, ptJmolByteText);
encoder.writeString (s);
encoder.writeCRC ();
}, $fz.isPrivate = true, $fz), "~S,~N,~A,~N,~N,~S");
c$.getApplicationText = $_M(c$, "getApplicationText", 
($fz = function (prefix, type, nPNG, nState) {
var sPNG = "000000000" + nPNG;
sPNG = sPNG.substring (sPNG.length - 9);
var sState = "000000000" + nState;
sState = sState.substring (sState.length - 9);
return prefix + "\0" + type + (type.equals ("PNG") ? "0" : "") + sPNG + "+" + sState;
}, $fz.isPrivate = true, $fz), "~S,~S,~N,~N");
$_M(c$, "writeHeader", 
($fz = function () {
this.writeInt4 (13);
this.startPos = this.bytePos;
this.writeString ("IHDR");
this.writeInt4 (this.width);
this.writeInt4 (this.height);
this.writeByte (8);
this.writeByte (this.encodeAlpha ? 6 : 2);
this.writeByte (0);
this.writeByte (0);
this.writeByte (0);
this.writeCRC ();
}, $fz.isPrivate = true, $fz));
$_M(c$, "writeText", 
($fz = function (msg) {
this.writeInt4 (msg.length);
this.startPos = this.bytePos;
this.writeString ("iTXt" + msg);
this.writeCRC ();
}, $fz.isPrivate = true, $fz), "~S");
$_M(c$, "writeTransparentColor", 
($fz = function (icolor) {
this.writeInt4 (6);
this.startPos = this.bytePos;
this.writeString ("tRNS");
this.writeInt2 ((icolor >> 16) & 0xFF);
this.writeInt2 ((icolor >> 8) & 0xFF);
this.writeInt2 (icolor & 0xFF);
this.writeCRC ();
}, $fz.isPrivate = true, $fz), "~N");
$_M(c$, "writeImageData", 
($fz = function () {
this.bytesPerPixel = (this.encodeAlpha ? 4 : 3);
this.byteWidth = this.width * this.bytesPerPixel;
var scanWidth = this.byteWidth + 1;
var rowsLeft = this.height;
var startRow = 0;
var nRows;
var scanPos;
var deflater =  new java.util.zip.Deflater (this.compressionLevel);
var outBytes =  new java.io.ByteArrayOutputStream (1024);
var compBytes =  new java.util.zip.DeflaterOutputStream (outBytes, deflater);
var pt = 0;
try {
while (rowsLeft > 0) {
nRows = Math.max (1, Math.min (Clazz.doubleToInt (32767 / scanWidth), rowsLeft));
this.scanLines =  Clazz.newByteArray (scanWidth * nRows, 0);
var nPixels = this.width * nRows;
scanPos = 0;
for (var i = 0; i < nPixels; i++, pt++) {
if (i % this.width == 0) {
this.scanLines[scanPos++] = this.filter;
}this.scanLines[scanPos++] = ((this.pixels[pt] >> 16) & 0xff);
this.scanLines[scanPos++] = ((this.pixels[pt] >> 8) & 0xff);
this.scanLines[scanPos++] = ((this.pixels[pt]) & 0xff);
if (this.encodeAlpha) {
this.scanLines[scanPos++] = ((this.pixels[pt] >> 24) & 0xff);
}}
compBytes.write (this.scanLines, 0, scanPos);
startRow += nRows;
rowsLeft -= nRows;
}
compBytes.close ();
var compressedLines = outBytes.toByteArray ();
this.writeInt4 (compressedLines.length);
this.startPos = this.bytePos;
this.writeString ("IDAT");
this.writeBytes (compressedLines);
this.writeCRC ();
this.writeEnd ();
deflater.finish ();
return true;
} catch (e) {
if (Clazz.exceptionOf (e, java.io.IOException)) {
System.err.println (e.toString ());
return false;
} else {
throw e;
}
}
}, $fz.isPrivate = true, $fz));
$_M(c$, "writeEnd", 
($fz = function () {
this.writeInt4 (0);
this.startPos = this.bytePos;
this.writeString ("IEND");
this.writeCRC ();
}, $fz.isPrivate = true, $fz));
Clazz.defineStatics (c$,
"FILTER_NONE", 0,
"FILTER_SUB", 1,
"FILTER_UP", 2,
"FILTER_LAST", 2);
});
Clazz.declarePackage ("J.image");
Clazz.load (["J.image.ImageEncoder", "J.util.ArrayUtil"], ["J.image.Huffman", "$.JpgEncoder", "$.DCT", "$.JpegObj"], null, function () {
c$ = Clazz.decorateAsClass (function () {
this.jpegObj = null;
this.huf = null;
this.dct = null;
this.defaultQuality = 100;
Clazz.instantialize (this, arguments);
}, J.image, "JpgEncoder", J.image.ImageEncoder);
Clazz.makeConstructor (c$, 
function () {
Clazz.superConstructor (this, J.image.JpgEncoder, []);
});
Clazz.overrideMethod (c$, "setParams", 
function (params) {
if (this.quality <= 0) this.quality = this.defaultQuality;
this.jpegObj =  new J.image.JpegObj ();
this.jpegObj.comment = params.get ("comment");
}, "java.util.Map");
Clazz.overrideMethod (c$, "generate", 
function () {
this.jpegObj.imageWidth = this.width;
this.jpegObj.imageHeight = this.height;
this.dct =  new J.image.DCT (this.quality);
this.huf =  new J.image.Huffman (this.width, this.height);
if (this.jpegObj == null) return;
this.jpegObj.getYCCArray (this.pixels);
var longState = this.writeHeaders (this.jpegObj, this.dct);
this.writeCompressedData (this.jpegObj, this.dct, this.huf);
this.writeMarker (J.image.JpgEncoder.eoi);
if (longState != null) {
var b = longState.getBytes ();
this.out.write (b, 0, b.length);
}});
$_M(c$, "writeCompressedData", 
($fz = function (jpegObj, dct, huf) {
var i;
var j;
var r;
var c;
var a;
var b;
var comp;
var xpos;
var ypos;
var xblockoffset;
var yblockoffset;
var inputArray;
var dctArray1 =  Clazz.newFloatArray (8, 8, 0);
var dctArray2 =  Clazz.newDoubleArray (8, 8, 0);
var dctArray3 =  Clazz.newIntArray (64, 0);
var lastDCvalue =  Clazz.newIntArray (jpegObj.numberOfComponents, 0);
var minBlockWidth;
var minBlockHeight;
minBlockWidth = ((huf.imageWidth % 8 != 0) ? Clazz.doubleToInt (Math.floor (huf.imageWidth / 8.0) + 1) * 8 : huf.imageWidth);
minBlockHeight = ((huf.imageHeight % 8 != 0) ? Clazz.doubleToInt (Math.floor (huf.imageHeight / 8.0) + 1) * 8 : huf.imageHeight);
for (comp = 0; comp < jpegObj.numberOfComponents; comp++) {
minBlockWidth = Math.min (minBlockWidth, jpegObj.blockWidth[comp]);
minBlockHeight = Math.min (minBlockHeight, jpegObj.blockHeight[comp]);
}
xpos = 0;
for (r = 0; r < minBlockHeight; r++) {
for (c = 0; c < minBlockWidth; c++) {
xpos = c * 8;
ypos = r * 8;
for (comp = 0; comp < jpegObj.numberOfComponents; comp++) {
inputArray = jpegObj.components[comp];
var vsampF = jpegObj.vsampFactor[comp];
var hsampF = jpegObj.hsampFactor[comp];
var qNumber = jpegObj.qtableNumber[comp];
var dcNumber = jpegObj.dctableNumber[comp];
var acNumber = jpegObj.actableNumber[comp];
for (i = 0; i < vsampF; i++) {
for (j = 0; j < hsampF; j++) {
xblockoffset = j * 8;
yblockoffset = i * 8;
for (a = 0; a < 8; a++) {
for (b = 0; b < 8; b++) {
dctArray1[a][b] = inputArray[ypos + yblockoffset + a][xpos + xblockoffset + b];
}
}
dctArray2 = J.image.DCT.forwardDCT (dctArray1);
dctArray3 = J.image.DCT.quantizeBlock (dctArray2, dct.divisors[qNumber]);
huf.HuffmanBlockEncoder (this.out, dctArray3, lastDCvalue[comp], dcNumber, acNumber);
lastDCvalue[comp] = dctArray3[0];
}
}
}
}
}
huf.flushBuffer (this.out);
}, $fz.isPrivate = true, $fz), "J.image.JpegObj,J.image.DCT,J.image.Huffman");
$_M(c$, "writeHeaders", 
($fz = function (jpegObj, dct) {
var i;
var j;
var index;
var offset;
var tempArray;
this.writeMarker (J.image.JpgEncoder.soi);
this.writeArray (J.image.JpgEncoder.jfif);
var comment = null;
if (jpegObj.comment.length > 0) this.writeString (jpegObj.comment, 0xE1);
this.writeString ("JPEG Encoder Copyright 1998, James R. Weeks and BioElectroMech.\n\n", 0xFE);
var dqt =  Clazz.newByteArray (134, 0);
dqt[0] = 0xFF;
dqt[1] = 0xDB;
dqt[2] = 0;
dqt[3] = 132;
offset = 4;
for (i = 0; i < 2; i++) {
dqt[offset++] = ((0) + i);
tempArray = dct.quantum[i];
for (j = 0; j < 64; j++) {
dqt[offset++] = tempArray[J.image.Huffman.jpegNaturalOrder[j]];
}
}
this.writeArray (dqt);
var sof =  Clazz.newByteArray (19, 0);
sof[0] = 0xFF;
sof[1] = 0xC0;
sof[2] = 0;
sof[3] = 17;
sof[4] = jpegObj.precision;
sof[5] = ((jpegObj.imageHeight >> 8) & 0xFF);
sof[6] = ((jpegObj.imageHeight) & 0xFF);
sof[7] = ((jpegObj.imageWidth >> 8) & 0xFF);
sof[8] = ((jpegObj.imageWidth) & 0xFF);
sof[9] = jpegObj.numberOfComponents;
index = 10;
for (i = 0; i < sof[9]; i++) {
sof[index++] = jpegObj.compID[i];
sof[index++] = ((jpegObj.hsampFactor[i] << 4) + jpegObj.vsampFactor[i]);
sof[index++] = jpegObj.qtableNumber[i];
}
this.writeArray (sof);
this.WriteDHTHeader (J.image.Huffman.bitsDCluminance, J.image.Huffman.valDCluminance);
this.WriteDHTHeader (J.image.Huffman.bitsACluminance, J.image.Huffman.valACluminance);
this.WriteDHTHeader (J.image.Huffman.bitsDCchrominance, J.image.Huffman.valDCchrominance);
this.WriteDHTHeader (J.image.Huffman.bitsACchrominance, J.image.Huffman.valACchrominance);
var sos =  Clazz.newByteArray (14, 0);
sos[0] = 0xFF;
sos[1] = 0xDA;
sos[2] = 0;
sos[3] = 12;
sos[4] = jpegObj.numberOfComponents;
index = 5;
for (i = 0; i < sos[4]; i++) {
sos[index++] = jpegObj.compID[i];
sos[index++] = ((jpegObj.dctableNumber[i] << 4) + jpegObj.actableNumber[i]);
}
sos[index++] = jpegObj.ss;
sos[index++] = jpegObj.se;
sos[index++] = ((jpegObj.ah << 4) + jpegObj.al);
this.writeArray (sos);
return comment;
}, $fz.isPrivate = true, $fz), "J.image.JpegObj,J.image.DCT");
$_M(c$, "writeString", 
($fz = function (s, id) {
var len = s.length;
var i0 = 0;
var suffix = " #Jmol...\u0000";
while (i0 < len) {
var nBytes = len - i0;
if (nBytes > 65510) {
nBytes = 65500;
var pt = s.lastIndexOf ('\n', i0 + nBytes);
if (pt > i0 + 1) nBytes = pt - i0;
}if (i0 + nBytes == len) suffix = "";
this.writeTag (nBytes + suffix.length, id);
this.writeArray (s.substring (i0, i0 + nBytes).getBytes ());
if (suffix.length > 0) this.writeArray (suffix.getBytes ());
i0 += nBytes;
}
}, $fz.isPrivate = true, $fz), "~S,~N");
$_M(c$, "writeTag", 
($fz = function (length, id) {
length += 2;
var com =  Clazz.newByteArray (4, 0);
com[0] = 0xFF;
com[1] = id;
com[2] = ((length >> 8) & 0xFF);
com[3] = (length & 0xFF);
this.writeArray (com);
}, $fz.isPrivate = true, $fz), "~N,~N");
$_M(c$, "WriteDHTHeader", 
function (bits, val) {
var dht;
var bytes = 0;
for (var j = 1; j < 17; j++) bytes += bits[j];

dht =  Clazz.newByteArray (21 + bytes, 0);
dht[0] = 0xFF;
dht[1] = 0xC4;
var index = 4;
for (var j = 0; j < 17; j++) dht[index++] = bits[j];

for (var j = 0; j < bytes; j++) dht[index++] = val[j];

dht[2] = (((index - 2) >> 8) & 0xFF);
dht[3] = ((index - 2) & 0xFF);
this.writeArray (dht);
}, "~A,~A");
$_M(c$, "writeMarker", 
function (data) {
this.out.write (data, 0, 2);
}, "~A");
$_M(c$, "writeArray", 
function (data) {
this.out.write (data, 0, data.length);
}, "~A");
Clazz.defineStatics (c$,
"CONTINUE_MAX", 65500,
"CONTINUE_MAX_BUFFER", 65510,
"eoi", [0xFF, 0xD9],
"jfif", [0xff, 0xe0, 0, 16, 0x4a, 0x46, 0x49, 0x46, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0],
"soi", [0xFF, 0xD8]);
c$ = Clazz.decorateAsClass (function () {
this.quantum = null;
this.divisors = null;
this.quantum_luminance = null;
this.DivisorsLuminance = null;
this.quantum_chrominance = null;
this.DivisorsChrominance = null;
Clazz.instantialize (this, arguments);
}, J.image, "DCT");
Clazz.prepareFields (c$, function () {
this.quantum = J.util.ArrayUtil.newInt2 (2);
this.divisors = J.util.ArrayUtil.newDouble2 (2);
this.quantum_luminance =  Clazz.newIntArray (64, 0);
this.DivisorsLuminance =  Clazz.newDoubleArray (64, 0);
this.quantum_chrominance =  Clazz.newIntArray (64, 0);
this.DivisorsChrominance =  Clazz.newDoubleArray (64, 0);
});
Clazz.makeConstructor (c$, 
function (quality) {
this.initMatrix (quality);
}, "~N");
$_M(c$, "initMatrix", 
($fz = function (quality) {
quality = (quality < 1 ? 1 : quality > 100 ? 100 : quality);
quality = (quality < 50 ? Clazz.doubleToInt (5000 / quality) : 200 - quality * 2);
this.quantum_luminance[0] = 16;
this.quantum_luminance[1] = 11;
this.quantum_luminance[2] = 10;
this.quantum_luminance[3] = 16;
this.quantum_luminance[4] = 24;
this.quantum_luminance[5] = 40;
this.quantum_luminance[6] = 51;
this.quantum_luminance[7] = 61;
this.quantum_luminance[8] = 12;
this.quantum_luminance[9] = 12;
this.quantum_luminance[10] = 14;
this.quantum_luminance[11] = 19;
this.quantum_luminance[12] = 26;
this.quantum_luminance[13] = 58;
this.quantum_luminance[14] = 60;
this.quantum_luminance[15] = 55;
this.quantum_luminance[16] = 14;
this.quantum_luminance[17] = 13;
this.quantum_luminance[18] = 16;
this.quantum_luminance[19] = 24;
this.quantum_luminance[20] = 40;
this.quantum_luminance[21] = 57;
this.quantum_luminance[22] = 69;
this.quantum_luminance[23] = 56;
this.quantum_luminance[24] = 14;
this.quantum_luminance[25] = 17;
this.quantum_luminance[26] = 22;
this.quantum_luminance[27] = 29;
this.quantum_luminance[28] = 51;
this.quantum_luminance[29] = 87;
this.quantum_luminance[30] = 80;
this.quantum_luminance[31] = 62;
this.quantum_luminance[32] = 18;
this.quantum_luminance[33] = 22;
this.quantum_luminance[34] = 37;
this.quantum_luminance[35] = 56;
this.quantum_luminance[36] = 68;
this.quantum_luminance[37] = 109;
this.quantum_luminance[38] = 103;
this.quantum_luminance[39] = 77;
this.quantum_luminance[40] = 24;
this.quantum_luminance[41] = 35;
this.quantum_luminance[42] = 55;
this.quantum_luminance[43] = 64;
this.quantum_luminance[44] = 81;
this.quantum_luminance[45] = 104;
this.quantum_luminance[46] = 113;
this.quantum_luminance[47] = 92;
this.quantum_luminance[48] = 49;
this.quantum_luminance[49] = 64;
this.quantum_luminance[50] = 78;
this.quantum_luminance[51] = 87;
this.quantum_luminance[52] = 103;
this.quantum_luminance[53] = 121;
this.quantum_luminance[54] = 120;
this.quantum_luminance[55] = 101;
this.quantum_luminance[56] = 72;
this.quantum_luminance[57] = 92;
this.quantum_luminance[58] = 95;
this.quantum_luminance[59] = 98;
this.quantum_luminance[60] = 112;
this.quantum_luminance[61] = 100;
this.quantum_luminance[62] = 103;
this.quantum_luminance[63] = 99;
J.image.DCT.AANscale (this.DivisorsLuminance, this.quantum_luminance, quality);
for (var i = 4; i < 64; i++) this.quantum_chrominance[i] = 99;

this.quantum_chrominance[0] = 17;
this.quantum_chrominance[1] = 18;
this.quantum_chrominance[2] = 24;
this.quantum_chrominance[3] = 47;
this.quantum_chrominance[8] = 18;
this.quantum_chrominance[9] = 21;
this.quantum_chrominance[10] = 26;
this.quantum_chrominance[11] = 66;
this.quantum_chrominance[16] = 24;
this.quantum_chrominance[17] = 26;
this.quantum_chrominance[18] = 56;
this.quantum_chrominance[24] = 47;
this.quantum_chrominance[25] = 66;
J.image.DCT.AANscale (this.DivisorsChrominance, this.quantum_chrominance, quality);
this.quantum[0] = this.quantum_luminance;
this.quantum[1] = this.quantum_chrominance;
this.divisors[0] = this.DivisorsLuminance;
this.divisors[1] = this.DivisorsChrominance;
}, $fz.isPrivate = true, $fz), "~N");
c$.AANscale = $_M(c$, "AANscale", 
($fz = function (divisors, values, quality) {
for (var j = 0; j < 64; j++) {
var temp = Clazz.doubleToInt ((values[j] * quality + 50) / 100);
values[j] = (temp < 1 ? 1 : temp > 255 ? 255 : temp);
}
for (var i = 0, index = 0; i < 8; i++) for (var j = 0; j < 8; j++, index++) divisors[index] = (0.125 / (values[index] * J.image.DCT.AANscaleFactor[i] * J.image.DCT.AANscaleFactor[j]));


}, $fz.isPrivate = true, $fz), "~A,~A,~N");
c$.forwardDCT = $_M(c$, "forwardDCT", 
function (input) {
var output =  Clazz.newDoubleArray (8, 8, 0);
var tmp0;
var tmp1;
var tmp2;
var tmp3;
var tmp4;
var tmp5;
var tmp6;
var tmp7;
var tmp10;
var tmp11;
var tmp12;
var tmp13;
var z1;
var z2;
var z3;
var z4;
var z5;
var z11;
var z13;
for (var i = 0; i < 8; i++) for (var j = 0; j < 8; j++) output[i][j] = (input[i][j] - 128.0);


for (var i = 0; i < 8; i++) {
tmp0 = output[i][0] + output[i][7];
tmp7 = output[i][0] - output[i][7];
tmp1 = output[i][1] + output[i][6];
tmp6 = output[i][1] - output[i][6];
tmp2 = output[i][2] + output[i][5];
tmp5 = output[i][2] - output[i][5];
tmp3 = output[i][3] + output[i][4];
tmp4 = output[i][3] - output[i][4];
tmp10 = tmp0 + tmp3;
tmp13 = tmp0 - tmp3;
tmp11 = tmp1 + tmp2;
tmp12 = tmp1 - tmp2;
output[i][0] = tmp10 + tmp11;
output[i][4] = tmp10 - tmp11;
z1 = (tmp12 + tmp13) * 0.707106781;
output[i][2] = tmp13 + z1;
output[i][6] = tmp13 - z1;
tmp10 = tmp4 + tmp5;
tmp11 = tmp5 + tmp6;
tmp12 = tmp6 + tmp7;
z5 = (tmp10 - tmp12) * 0.382683433;
z2 = 0.541196100 * tmp10 + z5;
z4 = 1.306562965 * tmp12 + z5;
z3 = tmp11 * 0.707106781;
z11 = tmp7 + z3;
z13 = tmp7 - z3;
output[i][5] = z13 + z2;
output[i][3] = z13 - z2;
output[i][1] = z11 + z4;
output[i][7] = z11 - z4;
}
for (var i = 0; i < 8; i++) {
tmp0 = output[0][i] + output[7][i];
tmp7 = output[0][i] - output[7][i];
tmp1 = output[1][i] + output[6][i];
tmp6 = output[1][i] - output[6][i];
tmp2 = output[2][i] + output[5][i];
tmp5 = output[2][i] - output[5][i];
tmp3 = output[3][i] + output[4][i];
tmp4 = output[3][i] - output[4][i];
tmp10 = tmp0 + tmp3;
tmp13 = tmp0 - tmp3;
tmp11 = tmp1 + tmp2;
tmp12 = tmp1 - tmp2;
output[0][i] = tmp10 + tmp11;
output[4][i] = tmp10 - tmp11;
z1 = (tmp12 + tmp13) * 0.707106781;
output[2][i] = tmp13 + z1;
output[6][i] = tmp13 - z1;
tmp10 = tmp4 + tmp5;
tmp11 = tmp5 + tmp6;
tmp12 = tmp6 + tmp7;
z5 = (tmp10 - tmp12) * 0.382683433;
z2 = 0.541196100 * tmp10 + z5;
z4 = 1.306562965 * tmp12 + z5;
z3 = tmp11 * 0.707106781;
z11 = tmp7 + z3;
z13 = tmp7 - z3;
output[5][i] = z13 + z2;
output[3][i] = z13 - z2;
output[1][i] = z11 + z4;
output[7][i] = z11 - z4;
}
return output;
}, "~A");
c$.quantizeBlock = $_M(c$, "quantizeBlock", 
function (inputData, divisorsCode) {
var outputData =  Clazz.newIntArray (64, 0);
for (var i = 0, index = 0; i < 8; i++) for (var j = 0; j < 8; j++, index++) outputData[index] = (Math.round (inputData[i][j] * divisorsCode[index]));


return outputData;
}, "~A,~A");
Clazz.defineStatics (c$,
"N", 8,
"NN", 64,
"AANscaleFactor", [1.0, 1.387039845, 1.306562965, 1.175875602, 1.0, 0.785694958, 0.541196100, 0.275899379]);
c$ = Clazz.decorateAsClass (function () {
this.bufferPutBits = 0;
this.bufferPutBuffer = 0;
this.imageHeight = 0;
this.imageWidth = 0;
this.dc_matrix0 = null;
this.ac_matrix0 = null;
this.dc_matrix1 = null;
this.ac_matrix1 = null;
this.dc_matrix = null;
this.ac_matrix = null;
this.numOfDCTables = 0;
this.numOfACTables = 0;
Clazz.instantialize (this, arguments);
}, J.image, "Huffman");
Clazz.makeConstructor (c$, 
function (width, height) {
this.initHuf ();
this.imageWidth = width;
this.imageHeight = height;
}, "~N,~N");
$_M(c$, "HuffmanBlockEncoder", 
function (out, zigzag, prec, dcCode, acCode) {
var temp;
var temp2;
var nbits;
var k;
var r;
var i;
this.numOfDCTables = 2;
this.numOfACTables = 2;
var matrixDC = this.dc_matrix[dcCode];
var matrixAC = this.ac_matrix[acCode];
temp = temp2 = zigzag[0] - prec;
if (temp < 0) {
temp = -temp;
temp2--;
}nbits = 0;
while (temp != 0) {
nbits++;
temp >>= 1;
}
this.bufferIt (out, matrixDC[nbits][0], matrixDC[nbits][1]);
if (nbits != 0) {
this.bufferIt (out, temp2, nbits);
}r = 0;
for (k = 1; k < 64; k++) {
if ((temp = zigzag[J.image.Huffman.jpegNaturalOrder[k]]) == 0) {
r++;
} else {
while (r > 15) {
this.bufferIt (out, matrixAC[0xF0][0], matrixAC[0xF0][1]);
r -= 16;
}
temp2 = temp;
if (temp < 0) {
temp = -temp;
temp2--;
}nbits = 1;
while ((temp >>= 1) != 0) {
nbits++;
}
i = (r << 4) + nbits;
this.bufferIt (out, matrixAC[i][0], matrixAC[i][1]);
this.bufferIt (out, temp2, nbits);
r = 0;
}}
if (r > 0) {
this.bufferIt (out, matrixAC[0][0], matrixAC[0][1]);
}}, "J.io.JmolOutputChannel,~A,~N,~N,~N");
$_M(c$, "bufferIt", 
function (out, code, size) {
var putBuffer = code;
var putBits = this.bufferPutBits;
putBuffer &= (1 << size) - 1;
putBits += size;
putBuffer <<= 24 - putBits;
putBuffer |= this.bufferPutBuffer;
while (putBits >= 8) {
var c = ((putBuffer >> 16) & 0xFF);
out.writeByteAsInt (c);
if (c == 0xFF) {
out.writeByteAsInt (0);
}putBuffer <<= 8;
putBits -= 8;
}
this.bufferPutBuffer = putBuffer;
this.bufferPutBits = putBits;
}, "J.io.JmolOutputChannel,~N,~N");
$_M(c$, "flushBuffer", 
function (out) {
var putBuffer = this.bufferPutBuffer;
var putBits = this.bufferPutBits;
while (putBits >= 8) {
var c = ((putBuffer >> 16) & 0xFF);
out.writeByteAsInt (c);
if (c == 0xFF) {
out.writeByteAsInt (0);
}putBuffer <<= 8;
putBits -= 8;
}
if (putBits > 0) {
var c = ((putBuffer >> 16) & 0xFF);
out.writeByteAsInt (c);
}}, "J.io.JmolOutputChannel");
$_M(c$, "initHuf", 
($fz = function () {
this.dc_matrix0 =  Clazz.newIntArray (12, 2, 0);
this.dc_matrix1 =  Clazz.newIntArray (12, 2, 0);
this.ac_matrix0 =  Clazz.newIntArray (255, 2, 0);
this.ac_matrix1 =  Clazz.newIntArray (255, 2, 0);
this.dc_matrix = J.util.ArrayUtil.newInt3 (2, -1);
this.ac_matrix = J.util.ArrayUtil.newInt3 (2, -1);
var p;
var l;
var i;
var lastp;
var si;
var code;
var huffsize =  Clazz.newIntArray (257, 0);
var huffcode =  Clazz.newIntArray (257, 0);
p = 0;
for (l = 1; l <= 16; l++) {
for (i = J.image.Huffman.bitsDCchrominance[l]; --i >= 0; ) {
huffsize[p++] = l;
}
}
huffsize[p] = 0;
lastp = p;
code = 0;
si = huffsize[0];
p = 0;
while (huffsize[p] != 0) {
while (huffsize[p] == si) {
huffcode[p++] = code;
code++;
}
code <<= 1;
si++;
}
for (p = 0; p < lastp; p++) {
this.dc_matrix1[J.image.Huffman.valDCchrominance[p]][0] = huffcode[p];
this.dc_matrix1[J.image.Huffman.valDCchrominance[p]][1] = huffsize[p];
}
p = 0;
for (l = 1; l <= 16; l++) {
for (i = J.image.Huffman.bitsACchrominance[l]; --i >= 0; ) {
huffsize[p++] = l;
}
}
huffsize[p] = 0;
lastp = p;
code = 0;
si = huffsize[0];
p = 0;
while (huffsize[p] != 0) {
while (huffsize[p] == si) {
huffcode[p++] = code;
code++;
}
code <<= 1;
si++;
}
for (p = 0; p < lastp; p++) {
this.ac_matrix1[J.image.Huffman.valACchrominance[p]][0] = huffcode[p];
this.ac_matrix1[J.image.Huffman.valACchrominance[p]][1] = huffsize[p];
}
p = 0;
for (l = 1; l <= 16; l++) {
for (i = J.image.Huffman.bitsDCluminance[l]; --i >= 0; ) {
huffsize[p++] = l;
}
}
huffsize[p] = 0;
lastp = p;
code = 0;
si = huffsize[0];
p = 0;
while (huffsize[p] != 0) {
while (huffsize[p] == si) {
huffcode[p++] = code;
code++;
}
code <<= 1;
si++;
}
for (p = 0; p < lastp; p++) {
this.dc_matrix0[J.image.Huffman.valDCluminance[p]][0] = huffcode[p];
this.dc_matrix0[J.image.Huffman.valDCluminance[p]][1] = huffsize[p];
}
p = 0;
for (l = 1; l <= 16; l++) {
for (i = J.image.Huffman.bitsACluminance[l]; --i >= 0; ) {
huffsize[p++] = l;
}
}
huffsize[p] = 0;
lastp = p;
code = 0;
si = huffsize[0];
p = 0;
while (huffsize[p] != 0) {
while (huffsize[p] == si) {
huffcode[p++] = code;
code++;
}
code <<= 1;
si++;
}
for (var q = 0; q < lastp; q++) {
this.ac_matrix0[J.image.Huffman.valACluminance[q]][0] = huffcode[q];
this.ac_matrix0[J.image.Huffman.valACluminance[q]][1] = huffsize[q];
}
this.dc_matrix[0] = this.dc_matrix0;
this.dc_matrix[1] = this.dc_matrix1;
this.ac_matrix[0] = this.ac_matrix0;
this.ac_matrix[1] = this.ac_matrix1;
}, $fz.isPrivate = true, $fz));
Clazz.defineStatics (c$,
"bitsDCluminance", [0x00, 0, 1, 5, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
"valDCluminance", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
"bitsDCchrominance", [0x01, 0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
"valDCchrominance", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
"bitsACluminance", [0x10, 0, 2, 1, 3, 3, 2, 4, 3, 5, 5, 4, 4, 0, 0, 1, 0x7d],
"valACluminance", [0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41, 0x06, 0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xa1, 0x08, 0x23, 0x42, 0xb1, 0xc1, 0x15, 0x52, 0xd1, 0xf0, 0x24, 0x33, 0x62, 0x72, 0x82, 0x09, 0x0a, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5a, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6a, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7a, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8a, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9a, 0xa2, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xc2, 0xc3, 0xc4, 0xc5, 0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8, 0xd9, 0xda, 0xe1, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea, 0xf1, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7, 0xf8, 0xf9, 0xfa],
"bitsACchrominance", [0x11, 0, 2, 1, 2, 4, 4, 3, 4, 7, 5, 4, 4, 0, 1, 2, 0x77],
"valACchrominance", [0x00, 0x01, 0x02, 0x03, 0x11, 0x04, 0x05, 0x21, 0x31, 0x06, 0x12, 0x41, 0x51, 0x07, 0x61, 0x71, 0x13, 0x22, 0x32, 0x81, 0x08, 0x14, 0x42, 0x91, 0xa1, 0xb1, 0xc1, 0x09, 0x23, 0x33, 0x52, 0xf0, 0x15, 0x62, 0x72, 0xd1, 0x0a, 0x16, 0x24, 0x34, 0xe1, 0x25, 0xf1, 0x17, 0x18, 0x19, 0x1a, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5a, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6a, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7a, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8a, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9a, 0xa2, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xc2, 0xc3, 0xc4, 0xc5, 0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8, 0xd9, 0xda, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7, 0xf8, 0xf9, 0xfa],
"jpegNaturalOrder", [0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5, 12, 19, 26, 33, 40, 48, 41, 34, 27, 20, 13, 6, 7, 14, 21, 28, 35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23, 30, 37, 44, 51, 58, 59, 52, 45, 38, 31, 39, 46, 53, 60, 61, 54, 47, 55, 62, 63]);
c$ = Clazz.decorateAsClass (function () {
this.comment = null;
this.imageHeight = 0;
this.imageWidth = 0;
this.blockWidth = null;
this.blockHeight = null;
this.precision = 8;
this.numberOfComponents = 3;
this.components = null;
this.compID = null;
this.hsampFactor = null;
this.vsampFactor = null;
this.qtableNumber = null;
this.dctableNumber = null;
this.actableNumber = null;
this.lastColumnIsDummy = null;
this.lastRowIsDummy = null;
this.ss = 0;
this.se = 63;
this.ah = 0;
this.al = 0;
this.compWidth = null;
this.compHeight = null;
this.maxHsampFactor = 0;
this.maxVsampFactor = 0;
Clazz.instantialize (this, arguments);
}, J.image, "JpegObj");
Clazz.prepareFields (c$, function () {
this.compID = [1, 2, 3];
this.hsampFactor = [1, 1, 1];
this.vsampFactor = [1, 1, 1];
this.qtableNumber = [0, 1, 1];
this.dctableNumber = [0, 1, 1];
this.actableNumber = [0, 1, 1];
this.lastColumnIsDummy = [false, false, false];
this.lastRowIsDummy = [false, false, false];
});
Clazz.makeConstructor (c$, 
function () {
this.components = J.util.ArrayUtil.newFloat3 (this.numberOfComponents, -1);
this.compWidth =  Clazz.newIntArray (this.numberOfComponents, 0);
this.compHeight =  Clazz.newIntArray (this.numberOfComponents, 0);
this.blockWidth =  Clazz.newIntArray (this.numberOfComponents, 0);
this.blockHeight =  Clazz.newIntArray (this.numberOfComponents, 0);
});
$_M(c$, "getYCCArray", 
function (pixels) {
this.maxHsampFactor = 1;
this.maxVsampFactor = 1;
for (var y = 0; y < this.numberOfComponents; y++) {
this.maxHsampFactor = Math.max (this.maxHsampFactor, this.hsampFactor[y]);
this.maxVsampFactor = Math.max (this.maxVsampFactor, this.vsampFactor[y]);
}
for (var y = 0; y < this.numberOfComponents; y++) {
this.compWidth[y] = (Clazz.doubleToInt (((this.imageWidth % 8 != 0) ? (Clazz.doubleToInt (Math.ceil (this.imageWidth / 8.0))) * 8 : this.imageWidth) / this.maxHsampFactor)) * this.hsampFactor[y];
if (this.compWidth[y] != ((Clazz.doubleToInt (this.imageWidth / this.maxHsampFactor)) * this.hsampFactor[y])) {
this.lastColumnIsDummy[y] = true;
}this.blockWidth[y] = Clazz.doubleToInt (Math.ceil (this.compWidth[y] / 8.0));
this.compHeight[y] = (Clazz.doubleToInt (((this.imageHeight % 8 != 0) ? (Clazz.doubleToInt (Math.ceil (this.imageHeight / 8.0))) * 8 : this.imageHeight) / this.maxVsampFactor)) * this.vsampFactor[y];
if (this.compHeight[y] != ((Clazz.doubleToInt (this.imageHeight / this.maxVsampFactor)) * this.vsampFactor[y])) {
this.lastRowIsDummy[y] = true;
}this.blockHeight[y] = Clazz.doubleToInt (Math.ceil (this.compHeight[y] / 8.0));
}
var Y =  Clazz.newFloatArray (this.compHeight[0], this.compWidth[0], 0);
var Cr1 =  Clazz.newFloatArray (this.compHeight[0], this.compWidth[0], 0);
var Cb1 =  Clazz.newFloatArray (this.compHeight[0], this.compWidth[0], 0);
for (var pt = 0, y = 0; y < this.imageHeight; ++y) {
for (var x = 0; x < this.imageWidth; ++x, pt++) {
var p = pixels[pt];
var r = ((p >> 16) & 0xff);
var g = ((p >> 8) & 0xff);
var b = (p & 0xff);
Y[y][x] = ((0.299 * r + 0.587 * g + 0.114 * b));
Cb1[y][x] = 128 + ((-0.16874 * r - 0.33126 * g + 0.5 * b));
Cr1[y][x] = 128 + ((0.5 * r - 0.41869 * g - 0.08131 * b));
}
}
this.components[0] = Y;
this.components[1] = Cb1;
this.components[2] = Cr1;
}, "~A");
});
Clazz.declarePackage ("J.viewer");
c$ = Clazz.declareType (J.viewer, "OutputManager");
Clazz.declarePackage ("J.viewer");
Clazz.load (["J.viewer.OutputManager"], "J.viewer.OutputManagerAll", ["java.lang.Boolean", "java.util.Hashtable", "J.api.Interface", "J.i18n.GT", "J.io.JmolBinary", "J.util.JmolList", "$.Logger", "$.SB", "$.TextFormat", "J.viewer.FileManager", "$.JC", "$.Viewer"], function () {
c$ = Clazz.decorateAsClass (function () {
this.viewer = null;
this.privateKey = 0;
Clazz.instantialize (this, arguments);
}, J.viewer, "OutputManagerAll", J.viewer.OutputManager);
Clazz.overrideMethod (c$, "setViewer", 
function (viewer, privateKey) {
this.viewer = viewer;
this.privateKey = privateKey;
return this;
}, "J.viewer.Viewer,~N");
Clazz.overrideMethod (c$, "createImage", 
function (params) {
var type = params.get ("type");
var fileName = params.get ("fileName");
var text = params.get ("text");
var bytes = params.get ("bytes");
var quality = J.viewer.OutputManagerAll.getInt (params, "quality", -2147483648);
var out = params.get ("outputChannel");
var closeStream = (out == null);
var len = -1;
try {
if (!this.viewer.checkPrivateKey (this.privateKey)) return "ERROR: SECURITY";
if (params.get ("image") != null) {
this.getOrSaveImage (params);
return fileName;
}if (bytes != null) {
if (out == null) out = this.viewer.openOutputChannel (this.privateKey, fileName, false);
out.write (bytes, 0, bytes.length);
} else if (text != null) {
if (out == null) out = this.viewer.openOutputChannel (this.privateKey, fileName, true);
out.append (text);
} else {
len = 1;
var bytesOrError = this.getOrSaveImage (params);
if (Clazz.instanceOf (bytesOrError, String)) return bytesOrError;
bytes = bytesOrError;
if (bytes != null) return (fileName == null ? bytes :  String.instantialize (bytes));
len = (params.get ("byteCount")).intValue ();
}} catch (exc) {
if (Clazz.exceptionOf (exc, java.io.IOException)) {
J.util.Logger.errorEx ("IO Exception", exc);
return exc.toString ();
} else {
throw exc;
}
} finally {
if (out != null) {
if (closeStream) out.closeChannel ();
len = out.getByteCount ();
}}
return (len < 0 ? "Creation of " + fileName + " failed: " + this.viewer.getErrorMessageUn () : "OK " + type + " " + (len > 0 ? len + " " : "") + fileName + (quality == -2147483648 ? "" : "; quality=" + quality));
}, "java.util.Map");
Clazz.overrideMethod (c$, "getOrSaveImage", 
function (params) {
var bytes = null;
var errMsg = null;
var type = (params.get ("type")).toUpperCase ();
var fileName = params.get ("fileName");
var scripts = params.get ("scripts");
var objImage = params.get ("image");
var channel = params.get ("outputChannel");
var asBytes = (channel == null && fileName == null);
var closeChannel = (channel == null && fileName != null);
var releaseImage = (objImage == null);
var image = (objImage == null ? this.viewer.getScreenImageBuffer (null, true) : objImage);
var isOK = false;
try {
if (image == null) return errMsg = this.viewer.getErrorMessage ();
if (channel == null) channel = this.viewer.openOutputChannel (this.privateKey, fileName, false);
if (channel == null) return errMsg = "ERROR: canceled";
var comment = null;
var stateData = null;
params.put ("date", this.viewer.apiPlatform.getDateFormat ());
if (type.startsWith ("JP")) {
type = J.util.TextFormat.simpleReplace (type, "E", "");
if (type.equals ("JPG64")) {
params.put ("outputChannelTemp", this.getOutputChannel (null, null));
comment = "";
} else {
comment = (!asBytes ? this.getWrappedState (null, null, image, false) : "");
}} else if (type.startsWith ("PNG")) {
comment = "";
var isPngj = type.equals ("PNGJ");
if (isPngj) {
stateData = this.getWrappedState (fileName, scripts, image, true);
if (Clazz.instanceOf (stateData, String)) stateData = J.viewer.Viewer.getJmolVersion ().getBytes ();
} else if (!asBytes) {
stateData = (this.getWrappedState (null, scripts, image, false)).getBytes ();
}if (stateData != null) {
params.put ("applicationData", stateData);
params.put ("applicationPrefix", "Jmol Type");
}if (type.equals ("PNGT")) params.put ("transparentColor", Integer.$valueOf (this.viewer.getBackgroundArgb ()));
type = "PNG";
}if (comment != null) params.put ("comment", comment.length == 0 ? J.viewer.Viewer.getJmolVersion () : comment);
var errRet =  new Array (1);
isOK = this.createTheImage (image, type, channel, params, errRet);
if (closeChannel) channel.closeChannel ();
if (isOK) {
if (asBytes) bytes = channel.toByteArray ();
 else if (params.containsKey ("captureByteCount")) errMsg = "OK: " + params.get ("captureByteCount").toString () + " bytes";
} else {
errMsg = errRet[0];
}} finally {
if (releaseImage) this.viewer.releaseScreenImage ();
params.put ("byteCount", Integer.$valueOf (bytes != null ? bytes.length : isOK ? channel.getByteCount () : -1));
}
return (errMsg == null ? bytes : errMsg);
}, "java.util.Map");
Clazz.overrideMethod (c$, "getWrappedState", 
function (fileName, scripts, objImage, asJmolZip) {
var width = this.viewer.apiPlatform.getImageWidth (objImage);
var height = this.viewer.apiPlatform.getImageHeight (objImage);
if (width > 0 && !this.viewer.global.imageState && !asJmolZip || !this.viewer.global.preserveState) return "";
var s = this.viewer.getStateInfo3 (null, width, height);
if (asJmolZip) {
if (fileName != null) this.viewer.fileManager.clearPngjCache (fileName);
return J.io.JmolBinary.createZipSet (this.privateKey, this.viewer.fileManager, this.viewer, null, s, scripts, true);
}try {
s = J.viewer.JC.embedScript (J.viewer.FileManager.setScriptFileReferences (s, ".", null, null));
} catch (e) {
J.util.Logger.error ("state could not be saved: " + e.toString ());
s = "Jmol " + J.viewer.Viewer.getJmolVersion ();
}
return s;
}, "~S,~A,~O,~B");
$_M(c$, "createTheImage", 
($fz = function (objImage, type, out, params, errRet) {
type = type.substring (0, 1) + type.substring (1).toLowerCase ();
{
if (type == "Pdf")
type += ":";
}var ie = J.api.Interface.getInterface ("J.image." + type + "Encoder");
if (ie == null) {
errRet[0] = "Image encoder type " + type + " not available";
return false;
}return ie.createImage (this.viewer.apiPlatform, type, objImage, out, params, errRet);
}, $fz.isPrivate = true, $fz), "~O,~S,J.io.JmolOutputChannel,java.util.Map,~A");
Clazz.overrideMethod (c$, "outputToFile", 
function (params) {
return this.handleOutputToFile (params, true);
}, "java.util.Map");
Clazz.overrideMethod (c$, "getOutputChannel", 
function (fileName, fullPath) {
if (!this.viewer.haveAccess (J.viewer.Viewer.ACCESS.ALL)) return null;
if (fileName != null) {
fileName = this.getOutputFileNameFromDialog (fileName, -2147483648);
if (fileName == null) return null;
}if (fullPath != null) fullPath[0] = fileName;
var localName = (J.viewer.FileManager.isLocal (fileName) ? fileName : null);
try {
return this.viewer.openOutputChannel (this.privateKey, localName, false);
} catch (e) {
if (Clazz.exceptionOf (e, java.io.IOException)) {
J.util.Logger.info (e.toString ());
return null;
} else {
throw e;
}
}
}, "~S,~A");
Clazz.overrideMethod (c$, "processWriteOrCapture", 
function (params) {
var fileName = params.get ("fileName");
if (fileName == null) return this.viewer.clipImageOrPasteText (params.get ("text"));
var bsFrames = params.get ("bsFrames");
var nVibes = J.viewer.OutputManagerAll.getInt (params, "nVibes", 0);
return (bsFrames != null || nVibes != 0 ? this.processMultiFrameOutput (fileName, bsFrames, nVibes, params) : this.handleOutputToFile (params, true));
}, "java.util.Map");
c$.getInt = $_M(c$, "getInt", 
($fz = function (params, key, def) {
var p = params.get (key);
return (p == null ? def : p.intValue ());
}, $fz.isPrivate = true, $fz), "java.util.Map,~S,~N");
$_M(c$, "processMultiFrameOutput", 
($fz = function (fileName, bsFrames, nVibes, params) {
var info = "";
var n = 0;
var quality = J.viewer.OutputManagerAll.getInt (params, "quality", -1);
fileName = this.setFullPath (params, this.getOutputFileNameFromDialog (fileName, quality));
if (fileName == null) return null;
var ptDot = fileName.indexOf (".");
if (ptDot < 0) ptDot = fileName.length;
var froot = fileName.substring (0, ptDot);
var fext = fileName.substring (ptDot);
var sb =  new J.util.SB ();
if (bsFrames == null) {
this.viewer.transformManager.vibrationOn = true;
sb =  new J.util.SB ();
for (var i = 0; i < nVibes; i++) {
for (var j = 0; j < 20; j++) {
this.viewer.transformManager.setVibrationT (j / 20 + 0.2501);
if (!this.writeFrame (++n, froot, fext, params, sb)) return "ERROR WRITING FILE SET: \n" + info;
}
}
this.viewer.setVibrationOff ();
} else {
for (var i = bsFrames.nextSetBit (0); i >= 0; i = bsFrames.nextSetBit (i + 1)) {
this.viewer.setCurrentModelIndex (i);
if (!this.writeFrame (++n, froot, fext, params, sb)) return "ERROR WRITING FILE SET: \n" + info;
}
}if (info.length == 0) info = "OK\n";
return info + "\n" + n + " files created";
}, $fz.isPrivate = true, $fz), "~S,J.util.BS,~N,java.util.Map");
$_M(c$, "setFullPath", 
($fz = function (params, fileName) {
var fullPath = params.get ("fullPath");
if (fullPath != null) fullPath[0] = fileName;
if (fileName == null) return null;
params.put ("fileName", fileName);
return fileName;
}, $fz.isPrivate = true, $fz), "java.util.Map,~S");
Clazz.overrideMethod (c$, "getOutputFromExport", 
function (params) {
var width = J.viewer.OutputManagerAll.getInt (params, "width", 0);
var height = J.viewer.OutputManagerAll.getInt (params, "height", 0);
var fileName = params.get ("fileName");
if (fileName != null) {
fileName = this.setFullPath (params, this.getOutputFileNameFromDialog (fileName, -2147483648));
if (fileName == null) return null;
}this.viewer.mustRender = true;
var saveWidth = this.viewer.dimScreen.width;
var saveHeight = this.viewer.dimScreen.height;
this.viewer.resizeImage (width, height, true, true, false);
this.viewer.setModelVisibility ();
var data = this.viewer.repaintManager.renderExport (this.viewer.gdata, this.viewer.modelSet, params);
this.viewer.resizeImage (saveWidth, saveHeight, true, true, true);
return data;
}, "java.util.Map");
Clazz.overrideMethod (c$, "getImageAsBytes", 
function (params) {
var width = J.viewer.OutputManagerAll.getInt (params, "width", 0);
var height = J.viewer.OutputManagerAll.getInt (params, "height", 0);
var saveWidth = this.viewer.dimScreen.width;
var saveHeight = this.viewer.dimScreen.height;
this.viewer.mustRender = true;
this.viewer.resizeImage (width, height, true, false, false);
this.viewer.setModelVisibility ();
this.viewer.creatingImage = true;
var bytesOrStr = null;
try {
bytesOrStr = this.getOrSaveImage (params);
} catch (e$$) {
if (Clazz.exceptionOf (e$$, java.io.IOException)) {
var e = e$$;
{
bytesOrStr = e;
this.viewer.setErrorMessage ("Error creating image: " + e, null);
}
} else if (Clazz.exceptionOf (e$$, Error)) {
var er = e$$;
{
this.viewer.handleError (er, false);
this.viewer.setErrorMessage ("Error creating image: " + er, null);
bytesOrStr = this.viewer.getErrorMessage ();
}
} else {
throw e$$;
}
}
this.viewer.creatingImage = false;
this.viewer.resizeImage (saveWidth, saveHeight, true, false, true);
return bytesOrStr;
}, "java.util.Map");
Clazz.overrideMethod (c$, "writeFileData", 
function (fileName, type, modelIndex, parameters) {
var fullPath =  new Array (1);
var out = this.getOutputChannel (fileName, fullPath);
if (out == null) return "";
fileName = fullPath[0];
var pathName = (type.equals ("FILE") ? this.viewer.getFullPathName () : null);
var getCurrentFile = (pathName != null && (pathName.equals ("string") || pathName.indexOf ("[]") >= 0 || pathName.equals ("JSNode")));
var asBytes = (pathName != null && !getCurrentFile);
if (asBytes) {
pathName = this.viewer.getModelSetPathName ();
if (pathName == null) return null;
}out.setType (type);
var msg = (type.equals ("PDB") || type.equals ("PQR") ? this.viewer.getPdbAtomData (null, out) : type.startsWith ("PLOT") ? this.viewer.modelSet.getPdbData (modelIndex, type.substring (5), this.viewer.getSelectionSet (false), parameters, out) : getCurrentFile ? out.append (this.viewer.getCurrentFileAsString ()).toString () : this.viewer.getFileAsBytes (pathName, out));
out.closeChannel ();
if (msg != null) msg = "OK " + msg + " " + fileName;
return msg;
}, "~S,~S,~N,~A");
$_M(c$, "writeFrame", 
($fz = function (n, froot, fext, params, sb) {
var fileName = "0000" + n;
fileName = this.setFullPath (params, froot + fileName.substring (fileName.length - 4) + fext);
var msg = this.handleOutputToFile (params, false);
this.viewer.scriptEcho (msg);
sb.append (msg).append ("\n");
return msg.startsWith ("OK");
}, $fz.isPrivate = true, $fz), "~N,~S,~S,java.util.Map,J.util.SB");
$_M(c$, "getOutputFileNameFromDialog", 
($fz = function (fileName, quality) {
if (fileName == null || this.viewer.$isKiosk) return null;
var useDialog = (fileName.indexOf ("?") == 0);
if (useDialog) fileName = fileName.substring (1);
useDialog = new Boolean (useDialog | (this.viewer.isApplet () && (fileName.indexOf ("http:") < 0))).valueOf ();
fileName = J.viewer.FileManager.getLocalPathForWritingFile (this.viewer, fileName);
if (useDialog) fileName = this.viewer.dialogAsk (quality == -2147483648 ? "Save" : "Save Image", fileName);
return fileName;
}, $fz.isPrivate = true, $fz), "~S,~N");
$_M(c$, "handleOutputToFile", 
($fz = function (params, doCheck) {
var ret = null;
var fileName = params.get ("fileName");
var type = params.get ("type");
var text = params.get ("text");
var width = J.viewer.OutputManagerAll.getInt (params, "width", 0);
var height = J.viewer.OutputManagerAll.getInt (params, "height", 0);
var quality = J.viewer.OutputManagerAll.getInt (params, "quality", -2147483648);
var captureMode = J.viewer.OutputManagerAll.getInt (params, "captureMode", -2147483648);
if (captureMode != -2147483648 && !this.viewer.allowCapture ()) return "ERROR: Cannot capture on this platform.";
var mustRender = (quality != -2147483648);
var localName = null;
if (captureMode != -2147483648) {
doCheck = false;
mustRender = false;
type = "GIF";
}if (doCheck) fileName = this.getOutputFileNameFromDialog (fileName, quality);
fileName = this.setFullPath (params, fileName);
if (fileName == null) return null;
if (J.viewer.FileManager.isLocal (fileName)) localName = fileName;
var saveWidth = this.viewer.dimScreen.width;
var saveHeight = this.viewer.dimScreen.height;
this.viewer.creatingImage = true;
if (mustRender) {
this.viewer.mustRender = true;
this.viewer.resizeImage (width, height, true, false, false);
this.viewer.setModelVisibility ();
}try {
if (type.equals ("JMOL")) type = "ZIPALL";
if (type.equals ("ZIP") || type.equals ("ZIPALL")) {
var scripts = params.get ("scripts");
if (scripts != null && type.equals ("ZIP")) type = "ZIPALL";
ret = J.io.JmolBinary.createZipSet (this.privateKey, this.viewer.fileManager, this.viewer, localName, text, scripts, type.equals ("ZIPALL"));
} else if (type.equals ("SCENE")) {
ret = (this.viewer.isJS ? "ERROR: Not Available" : this.createSceneSet (fileName, text, width, height));
} else {
var bytes = params.get ("bytes");
ret = this.viewer.statusManager.createImage (fileName, type, text, bytes, quality);
if (ret == null) {
var msg = null;
if (captureMode != -2147483648) {
var out = null;
var cparams = this.viewer.captureParams;
switch (captureMode) {
case 1073742032:
if (cparams != null) (cparams.get ("outputChannel")).closeChannel ();
out = this.getOutputChannel (localName, null);
if (out == null) {
ret = msg = "ERROR: capture canceled";
this.viewer.captureParams = null;
} else {
localName = out.getFileName ();
msg = type + "_STREAM_OPEN " + localName;
this.viewer.captureParams = params;
params.put ("captureFileName", localName);
params.put ("captureCount", Integer.$valueOf (1));
params.put ("captureMode", Integer.$valueOf (1073742032));
}break;
default:
if (cparams == null) {
ret = msg = "ERROR: capture not active";
} else {
params = cparams;
switch (captureMode) {
default:
ret = msg = "ERROR: CAPTURE MODE=" + captureMode + "?";
break;
case 1276118017:
if (Boolean.FALSE === params.get ("captureEnabled")) {
ret = msg = "capturing OFF; use CAPTURE ON/END/CANCEL to continue";
} else {
var count = J.viewer.OutputManagerAll.getInt (params, "captureCount", 1);
params.put ("captureCount", Integer.$valueOf (++count));
msg = type + "_STREAM_ADD " + count;
}break;
case 1048589:
case 1048588:
params = cparams;
params.put ("captureEnabled", (captureMode == 1048589 ? Boolean.TRUE : Boolean.FALSE));
ret = type + "_STREAM_" + (captureMode == 1048589 ? "ON" : "OFF");
params.put ("captureMode", Integer.$valueOf (1276118017));
break;
case 1150985:
case 1073741874:
params = cparams;
params.put ("captureMode", Integer.$valueOf (captureMode));
fileName = params.get ("captureFileName");
msg = type + "_STREAM_" + (captureMode == 1150985 ? "CLOSE " : "CANCEL ") + params.get ("captureFileName");
this.viewer.captureParams = null;
this.viewer.prompt (J.i18n.GT._ ("Capture") + ": " + (captureMode == 1073741874 ? J.i18n.GT._ ("canceled") : J.i18n.GT._ ("{0} saved", [fileName])), "OK", null, true);
}
break;
}break;
}
if (out != null) params.put ("outputChannel", out);
}params.put ("fileName", localName);
if (ret == null) ret = this.createImage (params);
if (Clazz.instanceOf (ret, String)) this.viewer.statusManager.createImage (ret, type, null, null, quality);
if (msg != null) this.viewer.showString (msg + " (" + params.get ("captureByteCount") + " bytes)", false);
}}if (Clazz.instanceOf (ret, Array)) ret = "OK " + J.io.JmolBinary.postByteArray (this.viewer.fileManager, fileName, ret);
} catch (er) {
J.util.Logger.error (this.viewer.setErrorMessage ((ret = "ERROR creating image??: " + er), null));
}
this.viewer.creatingImage = false;
if (quality != -2147483648) {
this.viewer.resizeImage (saveWidth, saveHeight, true, false, true);
}return ret;
}, $fz.isPrivate = true, $fz), "java.util.Map,~B");
$_M(c$, "createSceneSet", 
($fz = function (sceneFile, type, width, height) {
var script0 = this.viewer.getFileAsString (sceneFile);
if (script0 == null) return "no such file: " + sceneFile;
sceneFile = J.util.TextFormat.simpleReplace (sceneFile, ".spt", "");
var fileRoot = sceneFile;
var fileExt = type.toLowerCase ();
var scenes = J.util.TextFormat.splitChars (script0, "pause scene ");
var htScenes =  new java.util.Hashtable ();
var list =  new J.util.JmolList ();
var script = J.io.JmolBinary.getSceneScript (scenes, htScenes, list);
if (J.util.Logger.debugging) J.util.Logger.debug (script);
script0 = J.util.TextFormat.simpleReplace (script0, "pause scene", "delay " + this.viewer.animationManager.lastFrameDelay + " # scene");
var str = [script0, script, null];
this.viewer.saveState ("_scene0");
var nFiles = 0;
if (scenes[0] !== "") this.viewer.zap (true, true, false);
var iSceneLast = -1;
for (var i = 0; i < scenes.length - 1; i++) {
try {
var iScene = list.get (i).intValue ();
if (iScene > iSceneLast) this.viewer.showString ("Creating Scene " + iScene, false);
this.viewer.eval.runScript (scenes[i]);
if (iScene <= iSceneLast) continue;
iSceneLast = iScene;
str[2] = "all";
var fileName = fileRoot + "_scene_" + iScene + ".all." + fileExt;
var params =  new java.util.Hashtable ();
params.put ("fileName", fileName);
params.put ("type", "PNGJ");
params.put ("scripts", str);
params.put ("width", Integer.$valueOf (width));
params.put ("height", Integer.$valueOf (height));
var msg = this.handleOutputToFile (params, false);
str[0] = null;
str[2] = "min";
fileName = fileRoot + "_scene_" + iScene + ".min." + fileExt;
params.put ("fileName", fileName);
params.put ("width", Integer.$valueOf (Math.min (width, 200)));
params.put ("height", Integer.$valueOf (Math.min (height, 200)));
msg += "\n" + this.handleOutputToFile (params, false);
this.viewer.showString (msg, false);
nFiles += 2;
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
return "script error " + e.toString ();
} else {
throw e;
}
}
}
try {
this.viewer.eval.runScript (this.viewer.getSavedState ("_scene0"));
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
} else {
throw e;
}
}
return "OK " + nFiles + " files created";
}, $fz.isPrivate = true, $fz), "~S,~S,~N,~N");
Clazz.overrideMethod (c$, "setLogFile", 
function (value) {
var path = null;
var logFilePath = this.viewer.getLogFilePath ();
if (logFilePath == null || value.indexOf ("\\") >= 0) {
value = null;
} else if (value.startsWith ("http://") || value.startsWith ("https://")) {
path = value;
} else if (value.indexOf ("/") >= 0) {
value = null;
} else if (value.length > 0) {
if (!value.startsWith ("JmolLog_")) value = "JmolLog_" + value;
path = this.viewer.getAbsolutePath (this.privateKey, logFilePath + value);
}if (path == null) value = null;
 else J.util.Logger.info (J.i18n.GT._ ("Setting log file to {0}", path));
if (value == null || !this.viewer.haveAccess (J.viewer.Viewer.ACCESS.ALL)) {
J.util.Logger.info (J.i18n.GT._ ("Cannot set log file path."));
value = null;
} else {
this.viewer.logFileName = path;
this.viewer.global.setS ("_logFile", this.viewer.isApplet () ? value : path);
}return value;
}, "~S");
Clazz.overrideMethod (c$, "logToFile", 
function (data) {
try {
var doClear = (data.equals ("$CLEAR$"));
if (data.indexOf ("$NOW$") >= 0) data = J.util.TextFormat.simpleReplace (data, "$NOW$", this.viewer.apiPlatform.getDateFormat ());
if (this.viewer.logFileName == null) {
J.util.Logger.info (data);
return;
}var out = this.viewer.openLogFile (this.privateKey, !doClear);
if (!doClear) {
var ptEnd = data.indexOf ('\0');
if (ptEnd >= 0) data = data.substring (0, ptEnd);
out.append (data);
if (ptEnd < 0) out.append ("\n");
}J.util.Logger.info (out.closeChannel ());
} catch (e) {
if (Clazz.exceptionOf (e, Exception)) {
if (J.util.Logger.debugging) J.util.Logger.debug ("cannot log " + data);
} else {
throw e;
}
}
}, "~S");
});
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
