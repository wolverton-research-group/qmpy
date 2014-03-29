
depth=0
depthmax=5
nmax=300
nlines=0
function showall(objName,snot,Output){
 if(nlines>nmax || depth==depthmax)return ""
 nlines++
 depth++
 var obj=eval(objName)
 for(var i in obj){
   var st = null
   try {
	st =obj[i] + ""
   } catch (e) {
   }
   if(st==null){
	Output.push(objName+(isNaN(i)?"."+i:"["+i+"]")+" = null")
   }else{
	if(snot==null || st.indexOf(snot)<0)
		Output.push(objName+(isNaN(i)?"."+i:"["+i+"]")+" = "+st.replace(/</g,"&lt;"))
	if(st.indexOf("[")>=0){
		if(isNaN(i)){
		  if(i!="all" 
			&& i!="document"
			&& i.indexOf("top")<0
			&& i.indexOf("arent")<0
			&& i.indexOf("self")<0
			&& i.indexOf("Sibling")<0
			&& i.indexOf("window")<0
			&& i.indexOf("frame")<0
			&& i.indexOf("next")<0
			&& i.indexOf("previous")<0) {
				showall(objName+"."+i,snot,Output)
		  }
		} else if(objName.indexOf(".all")<0){
			showall(objName+"["+i+"]",snot,Output)
		}
	}
   }
 }
 depth--
}

function GRgetnewwindow(s,opt){
	var sm=""+Math.random()
	sm=sm.substring(3,10)
	return open(s,"GR_"+sm,opt)
}

slast=""
function showObject(s){
 if (!s)s=prompt("What do you want to see?",slast)
 if(!s)return
 slast=s
 var w=GRgetnewwindow("",wopt)
 var d=w.document
 d.open()
 d.write("<title>"+s+"</title>")
 var A=s.split(",")
 for(var j=0;j<A.length;j++){
  var Output = []
  showall(A[j],"function", Output)
  Output = Output.sort()
  d.write("<pre>")
  d.write(Output.join("\n"))
  d.write("</pre>")
 }
 d.close()
}

function showHtml(id) {
 var w=GRgetnewwindow("",wopt)
 var d=w.document
 d.open()
 d.write("<title>"+id+"</title>")
 d.write(document.getElementById(id).innerHTML.replace(/\</g,"&lt;").replace(/\&lt\;div/ig,"<br>&lt;div"))
 d.close()
}

function showJSON(x) {
	popupWindow("<pre>"+JSON.stringify(x,null," ")+"</pre>")
}

function showTabbed(data, field) {
	var s = ""
	for (var i = 0; i < data.length; i++) {
		var A = data[i]
		if (field)A = A[field]
		if (!A)continue
		s += "<pre>"
		for (var j = 0; j < A.length; j++) 
			if (A[j])
				s += A[j].join("\t") + "\n"
		s += "</pre>"
	}
	popupWindow(s)
}

woptions="menubar,scrollbars,resizable,alwaysRaised,width=450,height=600,left=50,top=50"

function popupWindow(swhat, options) {
	var s="<html>"+swhat+"</html>"
 	var sm=""+Math.random()
 	sm=sm.substring(3,10)
 	var newwin=open('','SIS_'+sm, options ? options : woptions)
 	newwin.document.write(s)
 	newwin.document.close()
}

//generic roundoff function

function roundoff(x,ndec){
	//round x to ndec decimal places (+) fixed; (-) floating
	if(x==0)return 0
	if(ndec==0)return Math.round(x)
	var neg=(x<0?"-":"")
	var xs=Math.abs(x)+""
	var i=(xs.indexOf("E") & xs.indexOf("e"))
	if(ndec<0 && i<0){
		var xs=roundoff(Math.abs(x)*1e-100,-ndec)
		var i=(xs.indexOf("E") & xs.indexOf("e"))
		var e=(eval(xs.substring(i+1,xs.length))+100)
		return neg+xs.substring(0,i)+(e!=0?"E"+e:"")
	}
	if (i>0) {
		var s=roundoff(xs.substring(0,i),Math.abs(ndec)-1)+"E"+xs.substring(i+1,xs.length)
		return neg+s
	}
	i=xs.indexOf(".")
	if (i<0) {
		xs=xs+"."
		i=xs.indexOf(".")
	}
	xs=xs+"000000000"
	var s="."+xs.substring(i+1+ndec,xs.length)
	xs=xs.substring(0,i)+xs.substring(i+1,i+1+ndec)
	var add1=(xs.charAt(0)=="0")
	if(add1)xs="1"+xs
	xs=eval(xs)+Math.round(eval(s))+""
	if(add1)xs=xs.substring(1,xs.length)
	xs=xs.substring(0,xs.length-ndec)+"."+xs.substring(xs.length-ndec,xs.length)
	if(xs.substring(0,1)==".")xs="0"+xs
	return neg+xs
}



