var menubarreq = new XMLHttpRequest;
menubarreq.open("GET", "/static/menubar.html")
menubarreq.onreadystatechange = function() {
	if (this.readyState == 4 && this.status == 200) {
		var el = document.createElement('div')
		el.innerHTML = this.responseText
		document.body.appendChild(el)
	}
}
menubarreq.send()