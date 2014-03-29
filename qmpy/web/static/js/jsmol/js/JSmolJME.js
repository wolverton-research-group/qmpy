/*
  JSmolJME.js   Bob Hanson hansonr@stolaf.edu  6/14/2012 and 3/20/2013

  JME 2D option -- use Jmol.getJMEApplet(id, Info, linkedApplet) to access
  
  linkedApplet puts JME into INFO block for that applet; 
	use Jmol.showInfo(jmol,true/false) to show/hide JME
	
	see http://chemapps.stolaf.edu/jmol/jme for files and demo
	
	There is a bug in JME that the first time it loads a model, it centers it, 
	but after that, it fails to center it. Could get around that, perhaps, by
	creating a new JME applet each time.
	
	JME licensing: http://www.molinspiration.com/jme/doc/index.html
	note that required boilerplate: "JME Editor courtesy of Peter Ertl, Novartis"
	
  
  these methods are private to JSmolJME.js
  
*/

(function (Jmol, document) {

	Jmol._JMEApplet = function(id, Info, linkedApplet, checkOnly) {
    this._isJME = true;
    this._isJava = (Info.use && Info.use.toUpperCase() == "JAVA")
		this._jmolType = "Jmol._JME" + (this._isJava ? "(JAVA)" : "(HTML5)");
    if (checkOnly)
      return this;
    window[id] = this;
    Jmol._setObject(this, id, Info);
    this._options = Info.options;
		this._linkedApplet = linkedApplet;
		this._readyFunction = Info.readyFunction;
		this._ready = false; 
 		this._jarPath = Info.jarPath;
		this._jarFile = Info.jarFile;
    if (linkedApplet)
      this._console = linkedApplet._console;
		Jmol._setConsoleDiv(this._console);
    this._divId = this._id + "_jmeappletdiv";
    this._isEmbedded = true;
    if (Info.divId) {
      this._isEmbedded = false;
      this._divId = Info.divId;
    }
 		if (Jmol._document) {
			if (this._linkedApplet) {
				this._linkedApplet._infoObject = this;
				this._linkedApplet._info = null;
				var d = Jmol._getElement(this._linkedApplet, "infotablediv");
				d.style.display = "block";
				var d = Jmol._getElement(this._linkedApplet, "infodiv");
        if (this._isEmbedded)
          this._divid = d.id;
			  Jmol._document = null;
			  d.innerHTML = this.create();
			  Jmol._document = document;
				this._showContainer(false, false);
			} else {
				this.create();
			}
		}
		return this;
  }

  Jmol._JMEApplet._getApplet = function(id, Info, linkedApplet, checkOnly) {
	
	// requires JmolJME.js and JME.jar
	// note that the variable name the return is assigned to MUST match the first parameter in quotes
	// jme = Jmol.getJMEApplet("jme", Info)

		Info || (Info = {});
		var DefaultInfo = {
			width: 300,
			height: 300,
			jarPath: "jme",
			jarFile: "JME.jar",
			options: "autoez"
			// see http://www2.chemie.uni-erlangen.de/services/fragment/editor/jme_functions.html
			// rbutton, norbutton - show / hide R button
			// hydrogens, nohydrogens - display / hide hydrogens
			// query, noquery - enable / disable query features
			// autoez, noautoez - automatic generation of SMILES with E,Z stereochemistry
			// nocanonize - SMILES canonicalization and detection of aromaticity supressed
			// nostereo - stereochemistry not considered when creating SMILES
			// reaction, noreaction - enable / disable reaction input
			// multipart - possibility to enter multipart structures
			// number - possibility to number (mark) atoms
			// depict - the applet will appear without editing butons,this is used for structure display only
		};		
		Jmol._addDefaultInfo(Info, DefaultInfo);
    if (!Jmol.featureDetection.allowHTML5)Info.use = "JAVA";
    var applet = new Jmol._JMEApplet(id, Info, linkedApplet, checkOnly);
    return (checkOnly ? applet : Jmol._registerApplet(id, applet));  
  }
  
  Jmol._JMEApplet.onload = function() {
    for (var i in Jmol._applets) {
      var app = Jmol._applets[i]
   	  if (app._isJME && !app._isJava && !app._ready) {
       app._applet = new JSApplet.JSME(app._divId, app.__Info);
       app._ready = true;
       if (app._readyFunction)
         app._readyFunction();
      }
    }
  }   

  jsmeOnLoad = Jmol._JMEApplet.onload;
        
;(function(proto){

  proto.create = function() {
    var s;
    if (this._isJava) {
  		var w = (this._linkedApplet ? "2px" : this._containerWidth);
  		var h = (this._linkedApplet ? "2px" : this._containerHeight);
  		s = '<applet code="JME.class" id="' + this._id + '_object" name="' + this._id 
  			+ '_object" archive="' + this._jarFile + '" codebase="' + this._jarPath + '" width="'+w+'" height="'+h+'">'
  			+ '<param name="options" value="' + this._options + '" />'	
  			+ '</applet>';
    } else if (this._isEmbedded) {
      s = "<div id=\"" + this._divId + "\" style=\"width:100%;height:100%;position:absolute;top:0px;left:0px;\"></div>" 
    }
  	return this._code = Jmol._documentWrite(s);
	}

  proto._checkDeferred = function(script) {
    return false;
  }	
  
	proto._searchDatabase = function(query, database){
		this._showInfo(false);
		if (database == "$")
			query = "$" + query; // 2D variant
		var dm = database + query;
		if (Jmol.db._DirectDatabaseCalls[database]) {
			this._loadFile(dm, script);
			return;
		}
		var self=this;
		Jmol._getRawDataFromServer(
			database,
			query,
			function(data){self._loadModel(data)}
		);
	}
	
	proto._loadFile = function(fileName){
		this._showInfo(false);
		this._thisJmolModel = "" + Math.random();
		var self = this;
		Jmol._loadFileData(this, fileName, function(data){self._loadModel(data)});
	}
	
	proto._loadModel = function(jmeOrMolData) {
		Jmol.jmeReadMolecule(this, jmeOrMolData);
	}
	
	proto._showInfo = function(tf) {
	  // from applet, so here is where we do the SMILES transfer
	  var jmol = this._linkedApplet;
	  if (jmol) {
		  var jme = this._applet;
      if (jme == null && this._isJava)
        jme = this._applet = Jmol._getElement(this, "object");
      var isOK = true;
      if (jme != null) {
  		  var jmeSMILES = jme.smiles();
  		  var jmolAtoms = jmeSMILES ? Jmol.evaluate(jmol, "{*}.find('SMILES', '" + jmeSMILES + "')") : "({})";
		    var isOK = (jmolAtoms != "({})");
      }
		  if (!isOK) {
			  if (tf) {
			    // toJME
          this._molData = Jmol.evaluate(jmol, "write('mol')")//Jmol.evaluate(jmol, "script('show chemical sdf')");//
          var cmd  = this._id + "._readMolData()";
			    setTimeout(cmd,100);
			  } else {
			    // toJmol
			    if (jmeSMILES)
				    Jmol.script(jmol, "load \"$" + jmeSMILES + "\"");
			  }
			}
 		  this._showContainer(tf, true);
		}
	}

  proto._readMolData = function() {
    if (!this._applet)return;
    this._applet.readMolFile(this._molData);
  }
  
  proto._showContainer = function(tf, andShow) {
		Jmol._getElement(this._linkedApplet, "infoheaderdiv").style.display = "none";
  	var d = Jmol._getElement(this._linkedApplet, "infotablediv");
    if (this._isJava) {
    	var w = (!tf ? "2px" : "100%");
  		var h = (!tf ? "2px" : "100%");
  		d.style.width = w;
  		d.style.height = h;
  		d = Jmol._getElement(this._linkedApplet, "infodiv");
  		d.style.overflow = "hidden";
  		if (andShow) {
  			d = Jmol._getElement(this, "object");
  			d.style.width = w; 
  			d.style.height = h; 
  			Jmol._getElement(this._linkedApplet, "infoheaderspan").innerHTML = (tf ? this : this._linkedApplet)._infoHeader;	
  		}
    } else {
      d.style.display = (tf ? "block" : "none");
  		d = Jmol._getElement(this._linkedApplet, "infodiv");
  		d.style.overflow = "hidden";
  		if (andShow) {
  			Jmol._getElement(this._linkedApplet, "infoheaderspan").innerHTML = (tf ? this : this._linkedApplet)._infoHeader;	
  		}
    }
		if (tf)
			Jmol._getElement(this._linkedApplet, "infoheaderdiv").style.display = "block";		
	}
})(Jmol._JMEApplet.prototype);

  //////  additional API for JME /////////

  // see also http://www2.chemie.uni-erlangen.de/services/fragment/editor/jme_functions.html
	  
  Jmol.jmeSmiles = function(jme, withStereoChemistry) {
  	return (arguments.length == 1 || withStereoChemistry ? jme._applet.smiles() : jme._applet.nonisomericSmiles())
  }
  
  Jmol.jmeReadMolecule = function(jme, jmeOrMolData) {
    // JME data is a single line with no line ending
  	if (jmeOrMolData.indexOf("\n") < 0 && jmeOrMolData.indexOf("\r") < 0)
	  	return  jme._applet.readMolecule(jmeOrMolData);
  	return  jme._applet.readMolFile(jmeOrMolData);
	}
	
  Jmol.jmeGetFile = function(jme, asJME) {
  	return  (asJME ? jme._applet.jmeFile() : jme._applet.molFile());
  }
  
  Jmol.jmeReset = function(jme) {
  	jme._applet.reset();
  }
  
  Jmol.jmeOptions = function(jme, options) {
  	jme._applet.options(options);
  }
	
})(Jmol, document);
