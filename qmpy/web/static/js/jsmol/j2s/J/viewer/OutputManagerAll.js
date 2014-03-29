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
