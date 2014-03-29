/*
*  JSpecView Utility functions
*  Version 2.0, Copyright(c) 2006-2012, Dept of Chemistry, University of the West Indies, Mona
*  Robert J Lancashire  robert.lancashire@uwimona.edu.jm
*
*
*  12:19 PM 3/8/2012 added support for JSpecViewAppletPro  -- BH
*  5/21/2012 -- incorporated as JmolJSV.js into Jmol
* 
*/

/*
	Inserts the JSpecView applet in any compatible User Agent using the <object> tag
	uses IE conditional comments to distinguish between IE and Mozilla
	see http://msdn.microsoft.com/workshop/author/dhtml/overview/ccomment_ovw.asp
*/

(function (Jmol, document) {
	
	Jmol._JSVVersion="2.0";

	Jmol._JSVApplet = function(id, Info, caption, checkOnly){
		this._jmolType = "Jmol._JSVApplet" + (Info.isSigned ? " (signed)" : "");
		this._id = id;
    if (checkOnly)
      return this;
		this._width = Info.width;
		this._height = Info.height;
		this._isSigned = Info.isSigned;
		this._dataMultiplier=1;
		this._hasOptions = Info.addSelectionOptions;
		this._info = "";
		this._infoHeader = this._jmolType + ' "' + this._id + '"'
		this._defaultModel = Info.defaultModel;
		this._readyFunction = Info.readyFunction;
		this._ready = false; 
		this._applet = null;
		this._jarFile = Info.jarFile || (Info.isSigned ? "JSpecViewAppletSigned.jar" : "JSpecViewApplet.jar"); 
		this._jarPath =	Info.jarPath || "."; 
		this._memoryLimit = Info.memoryLimit || 512;
		this._canScript = function(script) {return true;};
		this._containerWidth = this._width + ((this._width==parseFloat(this._width))? "px":"");
		this._containerHeight = this._height + ((this._height==parseFloat(this._height))? "px":"");
		this._syncKeyword = "JSpecView:"

		this._initialize = function(codebaseDirectory, fileNameOrUseSignedApplet) {
			Jmol.controls == undefined || Jmol.controls._onloadResetForms();		
		}
				
		this._create(id, Info, caption);
		return this;
	}

  Jmol._JSVApplet._getApplet = function(id, Info) {
	// note that the variable name the return is assigned to MUST match the first parameter in quotes
	// applet = Jmol.getJSVApplet("applet", Info)

		Info || (Info = {});
		var DefaultInfo = {
			width: 500,
			height: 300,
			debug: false,
			jarPath: ".",
			jarFile: "JSpecViewApplet.jar",
			isSigned: false,
			initParams: null,
			readyFunction: null,
			script: null
		};
		Jmol._addDefaultInfo(Info, DefaultInfo);
		return Jmol._registerApplet(id, new Jmol._JSVApplet(id, Info, null));
	}
  
	Jmol._JSVApplet.prototype._create = function(id, Info, caption){

		Jmol._setObject(this, id, Info);

		var params = {
			syncId: ("" + Math.random()).substring(3),
			progressbar: "true",
			progresscolor: "blue",
			boxbgcolor: Info.color || "black",
			boxfgcolor: "white",
			boxmessage: "Downloading JSpecViewApplet ..."
		};
		
		var myClass = "jspecview.applet.JSVApplet" + (this._isSigned ? "Pro" : "");
		var script = (Info.initParams ? Info.initParams : "") + ';appletID ' + this._id + ';syncID '+ params.syncId
		+ ';appletReadyCallbackFunctionName ' + this._id + '._readyCallback'
		+ ';syncCallbackFunctionName Jmol._mySyncCallback;';
		
    Jmol._Applet._createApplet(this, Info, params, myClass, script);
	}
	
	Jmol._JSVApplet.prototype._readyCallback = function(id, fullid, isReady, applet) {
		if (!isReady)
			return; // ignore -- page is closing
		this._ready = true;
		this._applet = applet;
		this._readyScript && setTimeout(this._id + "._script(" + this._id  + "._readyScript)",50);
		this._readyFunction && this._readyFunction(this);
    Jmol._setReady(this);
	}
	
  Jmol._JSVApplet.prototype._checkDeferred = function(script) {
    return false;
  }	
  
	Jmol._JSVApplet.prototype._showInfo = function(){"showinfo"};//Jmol._Applet.prototype._showInfo;
	
	Jmol._JSVApplet.prototype._show = Jmol._Applet.prototype._show;
	
	Jmol._JSVApplet.prototype._script = function(script) {
		if (!this._ready) {
			this._readyScript || (this._readyScript = ";");
			this._readyScript += ";" + script;
			return; 
		}
		this._applet.runScript(script);
	}
	
	Jmol._JSVApplet.prototype._syncScript = function(script) {
		this._applet.syncScript(script);
	}
	
	Jmol._JSVApplet.prototype._getPropertyAsJSON = function(sKey) {
		return this._applet.getPropertyAsJSON(sKey) + "";
	}

	Jmol._JSVApplet.prototype._getPropertyAsJavaObject = function(sKey) {		
		return this._applet.getPropertyAsJavaObject(sKey);
	}

	Jmol._JSVApplet.prototype._getPropertyAsArray = function(sKey,sValue) {
		return Jmol._evalJSON(this._getPropertyAsJSON(sKey,sValue),sKey);
	}

	Jmol._JSVApplet.prototype._resizeApplet = Jmol._Applet.prototype._resizeApplet;

	Jmol._JSVApplet.prototype._loadFile = function(fileName, params){
		this._showInfo(false);
		params || (params = "");
		this._thisJSVModel = "" + Math.random();
		// TODO
//		this._script("zap;set echo middle center;echo Retrieving data...");
		if (this._jvsIsSigned) {
			this._script("load \"" + fileName + "\"" + params);
			return;
		}
		var self = this;
		Jmol._loadFileData(this, fileName, function(data){Jmol.jsvLoadInline(self, data, params)});
	}

////// additional API for JSpecView ////////////

  /**
   * returns a Java Map<String, Object>
   * -- use key = "" for full set	    
   * -- key can drill down into spectra selecting specific subsets of data   
   */   

  Jmol.jsvGetPropertyAsJavaObject = function(jsvApplet, key) {
    return jsvApplet._applet.getPropertyAsJavaObject(key)    
  }

  /**
   * returns a JSON equivalent of jsvGetPropertyAsJavaObject
   * -- use key = "" for full set	    
   * -- key can drill down into spectra selecting specific subsets of data   
   */   

  Jmol.jsvGetPropertyAsJSON = function(jsvApplet, key) {
    return "" + jsvApplet._applet.getPropertyAsJSON(key)    
  }

  Jmol.jsvIsPro = function(jsvApplet) {
    return (jsvApplet._applet.isPro() ? true : false);    
  }

  Jmol.jsvIsSigned = function(jsvApplet) {
    return (jsvApplet._applet.isSigned() ? true : false);    
  }

  /**
   * Returns the calculated colour of a visible spectrum (Transmittance)
   * 
   * @return Color as a string
   */
	Jmol.jsvGetSolnColour = function(jsvApplet) {
		return "" + jsvApplet._applet.getSolnColour();
  }
  
  /**
   * Method that can be called from another applet or from javascript to return
   * the coordinate of clicked point in the plot area of the <code>
   * JSVPanel</code>
   * 
   * @return A String representation of the coordinate
   */

  Jmol.jsvGetCoordinate = function(jsvApplet) {
    return "" + jsvApplet._applet.getCoordinate();
  }

  /**
   * Delivers spectrum coded as desired: XY, SQZ, PAC, DIF, DIFDUP, FIX, AML, CML
   * 
   * @param type
   * @param n  -- nth spectrum in set: -1 for current; 0->[nSpec-1] for a specific one
   * @return data or "only <nSpec> spectra available"
   * 
   */

  Jmol.jsvExport = function(jsvApplet, exportType, n) {
    return "" + jsvApplet._applet.exportSpectrum(exportType, n);
  }

  /**
   * runs a script right now, without queuing it, and returns 
   * only after completion   
   * returns TRUE if succesful (ureliably; under development)
   */	   
  Jmol.jsvRunScriptNow = function(jsvApplet, script) {
    return (jsvApplet._applet.runScriptNow(script) ? true : false);    
  }

  /**
   * runs a script using a queue, possibly waiting until an applet is ready
   * same as Jmol.script(jsvApplet, script)   
   *   
   * @param script
   */
  Jmol.jsvRunScript = function(jsvApplet, script) {
    jsvApplet.runScript(script);   
  }

  /**
   * Loads in-line JCAMP-DX data into the existing applet window
   * 
   * @param data
   *        String
   */

  Jmol.jsvLoadInline = function(jsvApplet, data, params) {
    jsvApplet._applet.loadInline(data);
    // currently params are ignored
  }

  Jmol.jsvSetFilePath = function(jsvApplet, tmpFilePath) {
    jsvApplet._applet.setFilePath(tmpFilePath);    
  }

  /**
   * Sets the spectrum to the specified block number
   * same as SPECTRUMNUMBER n
   * @param n -- starting with 1
   */
  Jmol.jsvSetSpectrumNumber = function(jsvApplet, n) {
    jsvApplet._applet.setSpectrumNumber(n)    
  }

  /**
   * toggles the grid on/off
   */

  Jmol.jsvToggleGrid = function(jsvApplet) {
    jsvApplet._applet.toggleGrid();
  }

  /**
   * toggles the coordinate display
   */
  Jmol.jsvToggleCoordinate = function(jsvApplet) {
    jsvApplet._applet.toggleCoordinate();    
  }

  /**
   * toggles the integration graph on/off
   */
  Jmol.jsvToggleIntegration = function(jsvApplet) {
    jsvApplet._applet.toggleIntegration();    
  }

  /**
   * adds a highlight to a portion of the plot area
   * 
   * @param x1
   *        the starting x value
   * @param x2
   *        the ending x value
   * @param r
   *        the red portion of the highlight color
   * @param g
   *        the green portion of the highlight color
   * @param b
   *        the blue portion of the highlight color
   * @param a
   *        the alpha portion of the highlight color
   */
  Jmol.jsvAddHightlight = function(jsvApplet, x1, x2, r, g, b, a) {
    jsvApplet._applet.addHightlight(x1, x2, r, g, b, a);    
  }

  /**
   * removes all highlights from the plot area
   */
  Jmol.jsvRemoveAllHighlights = function(jsvApplet) {
    jsvApplet._applet.removeAllHighlights();    
  }

  /**
   * removes a highlight from the plot area
   * 
   * @param x1
   *        the starting x value
   * @param x2
   *        the ending x value
   */
  Jmol.jsvRemoveHighlight = function(jsvApplet, x1, x2) {
    jsvApplet._applet.removeHighlight(x1, x2);
  }

  /**
   * Method that can be called from another applet or from javascript that
   * toggles reversing the plot on a <code>JSVPanel</code>
   */
  Jmol.jsvReversePlot = function(jsvApplet) {
    jsvApplet._applet.reversePlot();    
  }

  /**
   * special command linking Jmol and JSpecView
   * -- currently in development (5/2012, BH)   
   * 
   */
  Jmol.jsvSyncScript = function(jsvApplet, peakScript) {
    jsvApplet.syncScript(peakScript);    
  }

  /**
   * Writes a message to the status label
   * 
   * @param msg
   *        the message
   */
  Jmol.jsvWriteStatus = function(jsvApplet, msg) {
    jsvApplet._applet.writeStatus(msg);    
  }

  Jmol.jsvSetVisible = function(jsvApplet, TF) {
    jsvApplet._applet.setVisible(TF);    
  }


})(Jmol, document);

