// BH 9/17/2013 10:18:40 AM  file transfer functions moved to JSmolCore 
// BH 3/5/2013 9:54:16 PM added support for a cover image: Info.coverImage, coverScript, coverTitle, deferApplet, deferUncover
 
// BH 1/3/2013 4:54:01 AM mouse binding should return false -- see d.bind(...), and d.bind("contextmenu") is not necessary

// JSmol.js -- Jmol pure JavaScript version
// author: Bob Hanson, hansonr@stolaf.edu	4/16/2012
// author: Takanori Nakane biochem_fan 6/12/2012

// This library requires jQuery and 
//
//	JSmoljQueryExt.js
//	JSmolCore.js
//  JSmolApplet.js
//  JSmolApi.js
//  j2sjmol.js    (Clazz and associated classes)
// prior to JSmol.js

// these two:
//
//  JSmolThree.js
//  JSmolGLmol.js
//  
//  are optional 

;(function (Jmol) {

	Jmol._getCanvas = function(id, Info, checkOnly, checkWebGL, checkHTML5) {
		// overrides the function in JmolCore.js
		var canvas = null;
		if (checkWebGL && Jmol.featureDetection.supportsWebGL()) {
			Jmol._Canvas3D.prototype = Jmol._jsSetPrototype(new Jmol._Applet(id,Info, "", true));
			GLmol.setRefresh(Jmol._Canvas3D.prototype);
			canvas = new Jmol._Canvas3D(id, Info, null, checkOnly);
		}
		if (checkHTML5 && canvas == null) {
			Jmol._Canvas2D.prototype = Jmol._jsSetPrototype(new Jmol._Applet(id,Info, "", true));
			canvas = new Jmol._Canvas2D(id, Info, null, checkOnly);
		}
		return canvas;
	};

	Jmol._Canvas2D = function(id, Info, caption, checkOnly){
		this._syncId = ("" + Math.random()).substring(3);
		this._id = id;
		this._is2D = true;
    this._isJava = false;
		this._aaScale = 1; // antialias scaling
		this._jmolType = "Jmol._Canvas2D (JSmol)";
		this._platform = "J.awtjs2d.Platform";
		if (checkOnly)
			return this;
    window[id] = this;
		this._createCanvas(id, Info, caption, null);
    if (!Jmol._document || this._deferApplet)
      return this;
    this._init();
		return this;
	};


	Jmol._jsSetPrototype = function(proto) {
    proto._init = function() {
   		this._setupJS();
		  this._showInfo(true); 
		  if (this._disableInitialConsole)
			  this._showInfo(false);
    };
    
    proto._createCanvas = function(id, Info, caption, glmol) {
			Jmol._setObject(this, id, Info);
      if (glmol) {
  			this._GLmol = glmol;
	   		this._GLmol.applet = this;
        this._GLmol.id = this._id;
      }      
      var t = Jmol._getWrapper(this, true);
      if (this._deferApplet) {
      } else if (Jmol._document) {
				Jmol._documentWrite(t);
        this._getCanvas(false);				        
				t = "";
			} else {
        this._deferApplet = true;
				t += '<script type="text/javascript">' + id + '._cover(false)</script>';
			}
			t += Jmol._getWrapper(this, false);
      if (Info.addSelectionOptions)
				t += Jmol._getGrabberOptions(this, caption);
			if (Jmol._debugAlert && !Jmol._document)
				alert(t);
			this._code = Jmol._documentWrite(t);
		};
		                      
    proto._cover = function (doCover) {
      if (doCover || !this._deferApplet) {
        this._displayCoverImage(doCover);
        return;
      }
      // uncovering UNMADE applet upon clicking image
      var s = (this._coverScript ? this._coverScript : "");
      this._coverScript = "";
      if (this._deferUncover)
        s += ";refresh;javascript " + this._id + "._displayCoverImage(false)";
      this._script(s, true);
      if (this._deferUncover && this._coverTitle == "activate 3D model")
        Jmol._getElement(this, "coverimage").title = "3D model is loading...";
      this._start();
      if (!this._deferUncover)
        this._displayCoverImage(doCover);
      if (this._init)
        this._init();
    };
  
    proto._displayCoverImage = function(TF) {
      if (!this._coverImage || this._isCovered == TF) return;
      this._isCovered = TF;
      Jmol._getElement(this, "coverdiv").style.display = (TF ? "block" : "none");
    };

    proto._start = function() {
      if (this._deferApplet)
        this._getCanvas(false);      
      if (this._defaultModel)
        Jmol._search(this, this._defaultModel);
      // if (this._readyScript) {
        // this._script(this._readyScript);
      // }
      this._showInfo(false);
    };                      

    proto._getCanvas = function(doReplace) {
      if (this._is2D)
        this._createCanvas2d(doReplace);
      else
        this._GLmol.create();
    };
                      
		proto._createCanvas2d = function(doReplace) {
		  var canvas = document.createElement( 'canvas' );
      var container = Jmol.$(this, "appletdiv");
      if (doReplace) {
        container[0].removeChild(this._canvas);
        Jmol._jsUnsetMouse(this._canvas);
      }
      var w = Math.round(container.width());
	  	var h = Math.round(container.height());
  		canvas.applet = this;
      this._canvas = canvas;
  		canvas.style.width = "100%";
  		canvas.style.height = "100%";
  		canvas.width = w;
  		canvas.height = h; // w and h used in setScreenDimension
  		canvas.id = this._id + "_canvas2d";
  		container.append(canvas);
      Jmol._jsSetMouse(canvas);
		}
		
		proto._setupJS = function() {
			window["j2s.lib"] = {
				base : this._j2sPath + "/",
				alias : ".",
				console : this._console
			};
			
			var es = Jmol._execStack;
			var doStart = (es.length == 0);
			es.push([this, Jmol.__loadClazz, null, "loadClazz"])
			if (!this._is2D) {
	   		es.push([this, Jmol.__loadClass, "J.exportjs.JSExporter","load JSExporter"])
				es.push([this, this.__addExportHook, null, "addExportHook"])
			}			 			
			if (Jmol.debugCode) {
        // es.push([this.__checkLoadStatus, null,"checkLoadStatus"])
        es.push([this, Jmol.__loadClass, "J.appletjs.Jmol", "load Jmol"])
      }
			es.push([this, this.__createApplet, null,"createApplet"])

			this._isSigned = true; // access all files via URL hook
			this._ready = false; 
			this._applet = null;
			this._canScript = function(script) {return true;};
			this._savedOrientations = [];
			this._syncKeyword = "Select:";
			Jmol._execLog += ("execStack loaded by " + this._id + " len=" + Jmol._execStack.length + "\n")
			if (!doStart)return;
			Jmol.__nextExecution();
		};

// proto.__checkLoadStatus = function(applet) {
// return;
// if (J.appletjs && J.appletjs.Jmol) {
// Jmol.__nextExecution();
// return;
// }
// // spin wheels until core.z.js is processed
// setTimeout(applet._id + ".__checkLoadStatus(" + applet._id + ")",100);
// }


		proto.__addExportHook = function(applet) {
		  GLmol.addExportHook(applet);
			Jmol.__nextExecution();
		};

		proto.__createApplet = function(applet) {
			var viewerOptions =  new java.util.Hashtable ();
      Jmol._setJmolParams(viewerOptions, applet.__Info, true);
			viewerOptions.put("appletReadyCallback","Jmol._readyCallback");
			viewerOptions.put("applet", true);
			viewerOptions.put("name", applet._id + "_object");
			viewerOptions.put("syncId", applet._syncId);      
      if (applet._color) 
        viewerOptions.put("bgcolor", applet._color);
      if (!applet._is2D)  
			  viewerOptions.put("script", "set multipleBondSpacing 0.35;");
			
			viewerOptions.put("signedApplet", "true");
			viewerOptions.put("platform", applet._platform);
			if (applet._is2D)
				viewerOptions.put("display",applet._id + "_canvas2d");
  			
			// viewerOptions.put("repaintManager", "J.render");
			viewerOptions.put("documentBase", document.location.href);
			var base = document.location.href.split("?")[0].split("#")[0].split("/")
			base[base.length - 1] = window["j2s.lib"].base
			viewerOptions.put ("codeBase", base.join("/"));
      
			Jmol._registerApplet(applet._id, applet);
      applet._applet = new J.appletjs.Jmol(viewerOptions);
      
      if (!applet._is2D)
				applet._GLmol.applet = applet;
			applet._jsSetScreenDimensions();
      
      
			if(applet.aaScale && applet.aaScale != 1)
				applet._applet.viewer.actionManager.setMouseDragFactor(applet.aaScale)
			Jmol.__nextExecution();
		};
		
		proto._jsSetScreenDimensions = function() {
				if (!this._applet)return
				// strangely, if CTRL+/CTRL- are used repeatedly, then the
        // applet div can be not the same size as the canvas if there
        // is a border in place.
				var d = Jmol._getElement(this, (this._is2D ? "canvas2d" : "canvas"));
				this._applet.viewer.setScreenDimension(
				d.width, d.height);
// Math.floor(Jmol.$(this, "appletdiv").height()));

		};

		proto._loadModel = function(mol, params) {
			var script = 'load DATA "model"\n' + mol + '\nEND "model" ' + params;
			this._script(script);
			this._showInfo(false);
		};
	
/*
 * proto._showInfo = function(tf) { Jmol._getElement(this,
 * "infoheaderspan").innerHTML = this._infoHeader; if (this._info)
 * Jmol._getElement(this, "infodiv").innerHTML = this._info; if
 * ((!this._isInfoVisible) == (!tf)) return; this._isInfoVisible = tf; if
 * (this._infoObject) { this._infoObject._showInfo(tf); } else {
 * Jmol._getElement(this, "infotablediv").style.display = (tf ? "block" :
 * "none"); Jmol._getElement(this, "infoheaderdiv").style.display = (tf ?
 * "block" : "none"); } this._show(!tf); }
 */		
		proto._show = function(tf) {
			Jmol._getElement(this,"appletdiv").style.display = (tf ? "block" : "none");
			if (tf)
				Jmol._repaint(this, true);
		};
		
		proto._canScript = function(script) {return true};
		
		proto._delay = function(eval, sc, millis) {
		// does not take into account that scripts may be added after this and
		// need to be cached.
			this._delayID = setTimeout(function(){eval.resumeEval(sc,false)}, millis);		
		}
		
		proto._loadFile = function(fileName, params){
			this._showInfo(false);
			params || (params = "");
			this._thisJmolModel = "" + Math.random();
			this._fileName = fileName;
      Jmol._scriptLoad(this, fileName, params, true);
		};
		
		proto._createDomNode = function(id, data) {
			id = this._id + "_" + id;
			var d = document.getElementById(id);
			if (d)
				document.body.removeChild(d);
			if (!data)
				return;
			if (data.indexOf("<?") == 0)
				data = data.substring(data.indexOf("<", 1));
			if (data.indexOf("/>") >= 0) {
				// no doubt there is a more efficient way to do this.
				// Firefox, at least, does not recognize "/>" in HTML blocks
				// that are added this way.
				var D = data.split("/>");
				for (var i = D.length - 1; --i >= 0;) {
					var s = D[i];
					var pt = s.lastIndexOf("<") + 1;
					var pt2 = pt;
					var len = s.length;
					var name = "";
					while (++pt2 < len) {
					  if (" \t\n\r".indexOf(s.charAt(pt2))>= 0) {
							var name = s.substring(pt, pt2);
							D[i] = s + "></"+name+">";
							break;
						}	  	
					}
				}
				data = D.join('');
			}
			d = document.createElement("_xml")
			d.id = id;
			d.innerHTML = data;
			d.style.display = "none";
			document.body.appendChild(d);
			return d;
		}		
	
		proto.equals = function(a) { return this == a };
		proto.clone = function() { return this };
		proto.hashCode = function() { return parseInt(this._syncId) };  
	
  
    proto._processGesture = function(touches) {
      return this._applet.viewer.mouse.processTwoPointGesture(touches);
    }
    
    proto._processEvent = function(type, xym) {
			this._applet.viewer.handleOldJvm10Event(type,xym[0],xym[1],xym[2],System.currentTimeMillis());
    }
    
    proto._resize = function() {
      var s = "__resizeTimeout_" + this._id;
      // only at end
      if (Jmol[s])
        clearTimeout(Jmol[s]);
      var self = this;
      Jmol[s] = setTimeout(function() {Jmol._repaint(self, true);Jmol[s]=null}, 100);
    }
    
    
    return proto;
	};
	
	
	
  Jmol._repaint = function(applet, asNewThread) {
    // asNewThread: true is from RepaintManager.repaintNow()
    // false is from Repaintmanager.requestRepaintAndWait()
    //
		
    // alert("_repaint " + arguments.callee.caller.caller.exName)
		if (!applet._applet)return;

		// asNewThread = false;
		var container = Jmol.$(applet, "appletdiv");
		var w = Math.round(container.width());
		var h = Math.round(container.height());
    if (applet._is2D && (applet._canvas.width != w || applet._canvas.height != h)) {
      applet._getCanvas(true);
      applet._applet.viewer.setDisplay(applet._canvas);
    }
		applet._applet.viewer.setScreenDimension(w, h);

		if (asNewThread) {
      setTimeout(function(){ applet._applet.viewer.updateJS(0,0)});
  	} else {
  		applet._applet.viewer.updateJS(0,0);
  	}
  	// System.out.println(applet._applet.fullName)
	}

	Jmol._getHiddenCanvas = function(applet, id, width, height, forceNew) {
  	id = applet._id + "_" + id;
		var d = document.getElementById(id);
    if (d && forceNew) {
      d = null;
    }
		if (!d)
	    d = document.createElement( 'canvas' );
	    // for some reason both these need to be set, or maybe just d.width?
		d.width = d.style.width = width;
		d.height = d.style.height = height;
		// d.style.display = "none";
		if (d.id != id) {
			d.id = id;
	  }
	  return d;
	}

	Jmol.__loadClass = function(applet, javaClass) {
	  ClazzLoader.loadClass(javaClass, function() {Jmol.__nextExecution()});
	};

	Jmol.__nextExecution = function(trigger) {
		var es = Jmol._execStack;
	  if (es.length == 0)
	  	return;
	  if (!trigger) {
			Jmol._execLog += ("settimeout for " + es[0][0]._id + " " + es[0][3] + " len=" + es.length + "\n")
		  setTimeout("Jmol.__nextExecution(true)",10)
	  	return;
	  }
	  var e = es.shift();
	  Jmol._execLog += "executing " + e[0]._id + " " + e[3] + "\n"
		e[1](e[0],e[2]);	
	};

	Jmol.__loadClazz = function(applet) {
		// problems with multiple applets?
	  if (!Jmol.__clazzLoaded) {
  		Jmol.__clazzLoaded = true;
			LoadClazz();
			if (applet._noMonitor)
				ClassLoaderProgressMonitor.showStatus = function() {}
			LoadClazz = null;

			ClazzLoader.globalLoaded = function (file) {
       // not really.... just nothing more yet to do yet
      	ClassLoaderProgressMonitor.showStatus ("Application loaded.", true);
  			if (!Jmol.debugCode || !Jmol.haveCore) {
  				Jmol.haveCore = true;
    			Jmol.__nextExecution();
    		}
      };
			ClazzLoader.packageClasspath ("java", null, true);
			ClazzLoader.setPrimaryFolder (applet._j2sPath); // where
															// org.jsmol.test.Test
															// is to be found
			ClazzLoader.packageClasspath (applet._j2sPath); // where the other
															// files are to be
															// found
  		// if (!Jmol.debugCode)
			  return;
		}
		Jmol.__nextExecution();
	};

  Jmol._loadImage = function(platform, echoNameAndPath, bytes, fOnload, image) {
  // bytes would be from a ZIP file -- will have to reflect those back from
	// server as an image after conversion to base64
  // ah, but that's a problem, because that image would be needed to be
	// posted, but you can't post an image call.
  // so we would have to go with <image data:> which does not work in all
	// browsers. Hmm.
  
    var path = echoNameAndPath[1];
    
    if (image == null) {
      var image = new Image();
      image.onload = function() {Jmol._loadImage(platform, echoNameAndPath, null, fOnload, image)};

      if (bytes != null) {      
        bytes = J.io.Base64.getBase64(bytes).toString();      
        var filename = path.substring(url.lastIndexOf("/") + 1);                                                           
        var mimetype = (filename.indexOf(".png") >= 0 ? "image/png" : filename.indexOf(".jpg") >= 0 ? "image/jpg" : "");
    	   // now what?
      }
      image.src = path;
      return true; // as far as we can tell!
    }
    var width = image.width;
    var height = image.height; 
    var id = "echo_" + echoNameAndPath[0];
    var canvas = Jmol._getHiddenCanvas(platform.viewer.applet, id, width, height, true);
    canvas.imageWidth = width;
    canvas.imageHeight = height;
    canvas.id = id;
    canvas.image=image;
    Jmol._setCanvasImage(canvas, width, height);
    // return a null canvas and the error in path if there is a problem
    fOnload(canvas,path);
  };

  Jmol._setCanvasImage = function(canvas, width, height) {
    canvas.buf32 = null;
    canvas.width = width;
    canvas.height = height;
    canvas.getContext("2d").drawImage(canvas.image, 0, 0, width, height);
  };

		
})(Jmol);
